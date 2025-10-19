"""
Password Reset Routes

Endpoints para recuperação de senha
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
import hashlib

from app.core.database import get_users_collection
from app.core.security import hash_password
from app.core.email import email_service
from app.utils.audit import log_audit

router = APIRouter()


class PasswordResetRequestSchema(BaseModel):
    """Schema para solicitar reset de senha"""
    email: EmailStr


class PasswordResetConfirmSchema(BaseModel):
    """Schema para confirmar reset de senha"""
    token: str
    new_password: str


def generate_reset_token() -> str:
    """
    Gera token seguro para reset de senha

    Returns:
        Token hexadecimal de 32 bytes
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    Hash do token para armazenamento seguro

    Args:
        token: Token em texto plano

    Returns:
        Hash SHA256 do token
    """
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(data: PasswordResetRequestSchema):
    """
    Solicita reset de senha

    Envia email com link de reset se o email existir.
    Sempre retorna sucesso (segurança - não vazar se email existe)

    Args:
        data: Email do usuário

    Returns:
        Mensagem de confirmação
    """
    try:
        users_collection = get_users_collection()

        # Buscar usuário
        user = await users_collection.find_one({
            "email": data.email,
            "flag_del": False
        })

        # Sempre retornar sucesso (não vazar se email existe)
        if not user:
            return {
                "success": True,
                "message": "Se o email existir, você receberá instruções para redefinir sua senha."
            }

        # Verificar se usuário está ativo
        if not user.get("is_active"):
            return {
                "success": True,
                "message": "Se o email existir, você receberá instruções para redefinir sua senha."
            }

        # Gerar token
        reset_token = generate_reset_token()
        token_hash = hash_token(reset_token)

        # Definir expiração (1 hora)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Salvar token no usuário
        await users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password_reset_token": token_hash,
                    "password_reset_expires": expires_at,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Enviar email
        frontend_url = email_service.frontend_url
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        await email_service.send_password_reset_email(
            user_email=user["email"],
            user_name=user.get("name", "Usuário"),
            reset_link=reset_link,
            expires_minutes=60
        )

        # Log de auditoria
        await log_audit(
            collection_name="users",
            document_id=str(user["_id"]),
            action="password_reset_requested",
            user_id=str(user["_id"]),
            details={
                "email": user["email"],
                "expires_at": expires_at.isoformat()
            }
        )

        return {
            "success": True,
            "message": "Se o email existir, você receberá instruções para redefinir sua senha."
        }

    except Exception as e:
        # Log erro mas não expor detalhes
        print(f"❌ Erro em password reset request: {str(e)}")
        return {
            "success": True,
            "message": "Se o email existir, você receberá instruções para redefinir sua senha."
        }


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(data: PasswordResetConfirmSchema):
    """
    Confirma reset de senha com token

    Args:
        data: Token e nova senha

    Returns:
        Confirmação

    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        users_collection = get_users_collection()

        # Hash do token recebido
        token_hash = hash_token(data.token)

        # Buscar usuário com token válido
        now = datetime.utcnow()

        user = await users_collection.find_one({
            "password_reset_token": token_hash,
            "password_reset_expires": {"$gt": now},
            "flag_del": False
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado. Solicite um novo reset de senha."
            )

        # Validar senha (mínimo 8 caracteres)
        if len(data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A senha deve ter no mínimo 8 caracteres."
            )

        # Hash da nova senha
        password_hash = hash_password(data.new_password)

        # Atualizar senha e limpar token
        await users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": now
                },
                "$unset": {
                    "password_reset_token": "",
                    "password_reset_expires": ""
                }
            }
        )

        # Invalidar todas as sessões ativas (forçar novo login)
        from app.core.database import get_sessions_collection
        sessions_collection = get_sessions_collection()

        await sessions_collection.update_many(
            {
                "user_id": user["_id"],
                "is_active": True,
                "flag_del": False
            },
            {
                "$set": {
                    "is_active": False,
                    "updated_at": now,
                    "logout_reason": "password_reset"
                }
            }
        )

        # Enviar email de confirmação
        await email_service.send_password_changed_email(
            user_email=user["email"],
            user_name=user.get("name", "Usuário")
        )

        # Log de auditoria
        await log_audit(
            collection_name="users",
            document_id=str(user["_id"]),
            action="password_reset_confirmed",
            user_id=str(user["_id"]),
            details={
                "email": user["email"],
                "sessions_invalidated": True
            }
        )

        return {
            "success": True,
            "message": "Senha alterada com sucesso. Faça login com sua nova senha."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro em password reset confirm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar reset de senha. Tente novamente."
        )


@router.post("/password-reset/validate-token", status_code=status.HTTP_200_OK)
async def validate_reset_token(token: str):
    """
    Valida se token de reset é válido

    Usado pelo frontend para verificar token antes de mostrar formulário

    Args:
        token: Token de reset

    Returns:
        Informações sobre validade do token
    """
    try:
        users_collection = get_users_collection()

        # Hash do token
        token_hash = hash_token(token)

        # Buscar usuário
        now = datetime.utcnow()

        user = await users_collection.find_one({
            "password_reset_token": token_hash,
            "password_reset_expires": {"$gt": now},
            "flag_del": False
        })

        if not user:
            return {
                "valid": False,
                "message": "Token inválido ou expirado."
            }

        # Calcular tempo restante
        expires_at = user["password_reset_expires"]
        time_remaining = (expires_at - now).total_seconds() / 60  # minutos

        return {
            "valid": True,
            "email": user["email"],
            "expires_in_minutes": int(time_remaining),
            "message": "Token válido."
        }

    except Exception as e:
        print(f"❌ Erro ao validar token: {str(e)}")
        return {
            "valid": False,
            "message": "Erro ao validar token."
        }
