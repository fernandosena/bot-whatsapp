"""
Rotas de Perfil do Usuário
Permite ao usuário visualizar e editar seus próprios dados
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.middleware.auth import get_current_user
from app.core.database import get_users_collection
from app.core.security import get_password_hash, verify_password
from app.utils.audit import log_audit

router = APIRouter(tags=["User Profile"])


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UpdateEmailRequest(BaseModel):
    new_email: EmailStr
    password: str


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Retorna o perfil completo do usuário atual
    """
    users_collection = get_users_collection()

    user = await users_collection.find_one({"_id": ObjectId(current_user["user_id"])})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Remover senha do retorno
    user.pop("password_hash", None)
    user["id"] = str(user.pop("_id"))

    return user


@router.put("/me")
async def update_my_profile(
    data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza dados do perfil do usuário
    Permite atualizar: nome, telefone, empresa, bio
    """
    users_collection = get_users_collection()

    # Preparar dados para atualização
    update_data = {}
    if data.full_name is not None:
        update_data["full_name"] = data.full_name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.company is not None:
        update_data["company"] = data.company
    if data.bio is not None:
        update_data["bio"] = data.bio

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar"
        )

    update_data["updated_at"] = datetime.utcnow()

    # Atualizar usuário
    result = await users_collection.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma alteração foi feita"
        )

    # Log de auditoria
    await log_audit(
        user_id=current_user["user_id"],
        action="update_profile",
        description=f"Usuário atualizou seu perfil",
        metadata={"fields_updated": list(update_data.keys())}
    )

    return {
        "success": True,
        "message": "Perfil atualizado com sucesso"
    }


@router.post("/me/change-password")
async def change_my_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Altera a senha do usuário
    Requer senha atual para confirmação
    """
    users_collection = get_users_collection()

    # Buscar usuário
    user = await users_collection.find_one({"_id": ObjectId(current_user["user_id"])})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar senha atual
    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )

    # Validar nova senha (mínimo 6 caracteres)
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ter no mínimo 6 caracteres"
        )

    # Hash da nova senha
    new_password_hash = get_password_hash(data.new_password)

    # Atualizar senha
    await users_collection.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {"$set": {
            "password_hash": new_password_hash,
            "updated_at": datetime.utcnow()
        }}
    )

    # Log de auditoria
    await log_audit(
        user_id=current_user["user_id"],
        action="change_password",
        description="Usuário alterou sua senha"
    )

    return {
        "success": True,
        "message": "Senha alterada com sucesso"
    }


@router.post("/me/change-email")
async def change_my_email(
    data: UpdateEmailRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Altera o email do usuário
    Requer senha para confirmação
    """
    users_collection = get_users_collection()

    # Buscar usuário
    user = await users_collection.find_one({"_id": ObjectId(current_user["user_id"])})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar senha
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )

    # Verificar se o novo email já está em uso
    existing_user = await users_collection.find_one({
        "email": data.new_email,
        "flag_del": False
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email já está em uso"
        )

    # Atualizar email
    await users_collection.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {"$set": {
            "email": data.new_email,
            "email_verified": False,  # Precisa verificar novo email
            "updated_at": datetime.utcnow()
        }}
    )

    # Log de auditoria
    await log_audit(
        user_id=current_user["user_id"],
        action="change_email",
        description=f"Usuário alterou email de {user['email']} para {data.new_email}"
    )

    return {
        "success": True,
        "message": "Email alterado com sucesso. Por favor, verifique seu novo email."
    }


@router.delete("/me")
async def delete_my_account(
    password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta a conta do usuário (soft delete)
    Requer senha para confirmação
    """
    users_collection = get_users_collection()

    # Buscar usuário
    user = await users_collection.find_one({"_id": ObjectId(current_user["user_id"])})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar senha
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )

    # Soft delete
    await users_collection.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {"$set": {
            "flag_del": True,
            "deleted_at": datetime.utcnow(),
            "deleted_by": ObjectId(current_user["user_id"]),
            "deleted_reason": "Usuário solicitou exclusão da conta"
        }}
    )

    # Log de auditoria
    await log_audit(
        user_id=current_user["user_id"],
        action="delete_account",
        description="Usuário deletou sua própria conta"
    )

    return {
        "success": True,
        "message": "Conta deletada com sucesso. Seus dados foram preservados por 30 dias."
    }


@router.get("/me/stats")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """
    Retorna estatísticas do usuário
    - Tempo de conta
    - Plano atual
    - Uso de recursos
    """
    from app.core.database import get_subscriptions_collection, get_plans_collection

    users_collection = get_users_collection()
    subscriptions_collection = get_subscriptions_collection()
    plans_collection = get_plans_collection()

    # Buscar usuário
    user = await users_collection.find_one({"_id": ObjectId(current_user["user_id"])})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Buscar assinatura ativa
    subscription = await subscriptions_collection.find_one({
        "user_id": ObjectId(current_user["user_id"]),
        "status": "active",
        "flag_del": False
    })

    plan = None
    if subscription:
        plan = await plans_collection.find_one({"_id": subscription["plan_id"]})

    # Calcular tempo de conta
    account_age_days = (datetime.utcnow() - user["created_at"]).days

    return {
        "account_created": user["created_at"],
        "account_age_days": account_age_days,
        "email_verified": user.get("email_verified", False),
        "current_plan": plan["name"] if plan else "Sem plano",
        "subscription_status": subscription["status"] if subscription else "inactive",
        "total_logins": user.get("login_count", 0),
        "last_login": user.get("last_login_at")
    }
