"""
Rotas de Autenticação
Register, Login, Logout, Refresh Token
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.models.user import UserCreate, UserResponse
from app.models.session import SessionCreate
from app.core.database import get_users_collection, get_sessions_collection
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_device_fingerprint
)
from app.utils.soft_delete import find_one_active, soft_delete
from app.utils.audit import log_login, log_logout
from app.middleware.auth import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, request: Request):
    """
    Registra novo usuário

    - **email**: Email único
    - **password**: Senha (mínimo 8 caracteres)
    - **name**: Nome completo
    - **phone**: Telefone (opcional)
    """
    users_collection = get_users_collection()

    # Verifica se email já existe
    existing_user = await find_one_active(users_collection, {"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Validação de senha
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter no mínimo 8 caracteres"
        )

    # Cria usuário
    user_dict = user.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user.password)
    user_dict["role"] = "user"
    user_dict["is_active"] = True
    user_dict["email_verified"] = False
    user_dict["phone_verified"] = False
    user_dict["oauth_provider"] = None
    user_dict["oauth_id"] = None
    user_dict["current_plan_id"] = None
    user_dict["subscription_status"] = "free"
    user_dict["active_devices"] = []

    # Soft delete fields
    user_dict["flag_del"] = False
    user_dict["deleted_at"] = None
    user_dict["deleted_by"] = None
    user_dict["deleted_reason"] = None

    # Timestamps
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["last_login"] = None

    result = await users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)

    # Remove senha do response
    if "hashed_password" in user_dict:
        del user_dict["hashed_password"]

    return user_dict


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, request: Request):
    """
    Autentica usuário e cria sessão

    - **email**: Email do usuário
    - **password**: Senha do usuário

    Returns:
        Access token e refresh token
    """
    users_collection = get_users_collection()
    sessions_collection = get_sessions_collection()

    # Busca usuário
    user = await find_one_active(users_collection, {"email": login_data.email})

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        # Log de tentativa de login falha
        await log_login(
            user_id=login_data.email,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    # Verifica se usuário está ativo
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado. Entre em contato com o suporte."
        )

    # Gera tokens
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    # Gera device fingerprint
    device_fingerprint = generate_device_fingerprint(
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host
    )

    # Cria sessão
    session_dict = {
        "user_id": user["_id"],
        "device_fingerprint": device_fingerprint,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "is_active": True,
        "last_activity": datetime.utcnow(),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "login_at": datetime.utcnow(),
        "logout_at": None,
        "is_desktop": False,
        "desktop_version": None,
        "flag_del": False,
        "deleted_at": None,
        "deleted_by": None,
        "deleted_reason": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await sessions_collection.insert_one(session_dict)

    # Atualiza último login do usuário
    await users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"last_login": datetime.utcnow()},
            "$addToSet": {"active_devices": device_fingerprint}
        }
    )

    # Log de login bem-sucedido
    await log_login(
        user_id=user_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        success=True
    )

    # Prepara response
    user_response = {
        "_id": user_id,
        "email": user["email"],
        "name": user["name"],
        "phone": user.get("phone"),
        "avatar": user.get("avatar"),
        "role": user["role"],
        "is_active": user["is_active"],
        "email_verified": user["email_verified"],
        "current_plan_id": str(user["current_plan_id"]) if user.get("current_plan_id") else None,
        "subscription_status": user["subscription_status"],
        "created_at": user["created_at"],
        "last_login": user.get("last_login")
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/logout")
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Encerra sessão do usuário
    """
    sessions_collection = get_sessions_collection()

    # Busca token do header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )

    token = auth_header.replace("Bearer ", "")

    # Marca sessão como inativa (soft delete)
    await sessions_collection.update_one(
        {
            "user_id": current_user["_id"],
            "access_token": token,
            "is_active": True
        },
        {
            "$set": {
                "is_active": False,
                "logout_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Log de logout
    await log_logout(
        user_id=str(current_user["_id"]),
        ip_address=request.client.host
    )

    return {"message": "Logout realizado com sucesso"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh_access_token(token_data: RefreshTokenRequest, request: Request):
    """
    Renova access token usando refresh token

    - **refresh_token**: Refresh token válido

    Returns:
        Novo access token e refresh token
    """
    users_collection = get_users_collection()
    sessions_collection = get_sessions_collection()

    # Verifica refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )

    # Busca usuário
    user = await find_one_active(users_collection, {"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    # Busca sessão com refresh token
    session = await find_one_active(
        sessions_collection,
        {
            "user_id": user["_id"],
            "refresh_token": token_data.refresh_token,
            "is_active": True
        }
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida"
        )

    # Gera novos tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    # Atualiza sessão com novos tokens
    await sessions_collection.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "last_activity": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Prepara response
    user_response = {
        "_id": user_id,
        "email": user["email"],
        "name": user["name"],
        "phone": user.get("phone"),
        "avatar": user.get("avatar"),
        "role": user["role"],
        "is_active": user["is_active"],
        "email_verified": user["email_verified"],
        "current_plan_id": str(user["current_plan_id"]) if user.get("current_plan_id") else None,
        "subscription_status": user["subscription_status"],
        "created_at": user["created_at"],
        "last_login": user.get("last_login")
    }

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    user_response = {
        "_id": str(current_user["_id"]),
        "email": current_user["email"],
        "name": current_user["name"],
        "phone": current_user.get("phone"),
        "avatar": current_user.get("avatar"),
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "email_verified": current_user["email_verified"],
        "current_plan_id": str(current_user["current_plan_id"]) if current_user.get("current_plan_id") else None,
        "subscription_status": current_user["subscription_status"],
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login")
    }

    return user_response


@router.get("/sessions")
async def list_user_sessions(current_user: dict = Depends(get_current_user)):
    """
    Lista sessões ativas do usuário
    """
    sessions_collection = get_sessions_collection()

    sessions = await sessions_collection.find({
        "user_id": current_user["_id"],
        "is_active": True,
        "flag_del": False
    }).to_list(length=None)

    # Remove tokens sensíveis
    for session in sessions:
        session["_id"] = str(session["_id"])
        session["user_id"] = str(session["user_id"])
        if "access_token" in session:
            del session["access_token"]
        if "refresh_token" in session:
            del session["refresh_token"]

    return {"sessions": sessions, "count": len(sessions)}


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Encerra uma sessão específica
    """
    sessions_collection = get_sessions_collection()

    if not ObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de sessão inválido"
        )

    # Marca sessão como inativa
    result = await sessions_collection.update_one(
        {
            "_id": ObjectId(session_id),
            "user_id": current_user["_id"]
        },
        {
            "$set": {
                "is_active": False,
                "logout_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )

    return {"message": "Sessão encerrada com sucesso"}
