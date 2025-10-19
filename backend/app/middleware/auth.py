"""
Middleware de Autenticação e Autorização
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from bson import ObjectId

from backend.app.core.security import verify_token
from backend.app.core.database import get_users_collection, get_sessions_collection
from backend.app.utils.soft_delete import find_one_active


security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Dependency para obter usuário autenticado atual

    Verifica:
    1. Token JWT válido
    2. Usuário existe e está ativo
    3. Sessão está ativa

    Returns:
        Dados do usuário autenticado

    Raises:
        HTTPException: Se autenticação falhar
    """
    token = credentials.credentials

    # Verifica token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Busca usuário
    users_collection = get_users_collection()
    user = await find_one_active(users_collection, {"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado",
        )

    # Verifica sessão ativa
    sessions_collection = get_sessions_collection()
    session = await find_one_active(
        sessions_collection,
        {
            "user_id": ObjectId(user_id),
            "access_token": token,
            "is_active": True
        }
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Atualiza última atividade da sessão
    from datetime import datetime
    await sessions_collection.update_one(
        {"_id": session["_id"]},
        {"$set": {"last_activity": datetime.utcnow()}}
    )

    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency para garantir que usuário está ativo

    Returns:
        Dados do usuário ativo

    Raises:
        HTTPException: Se usuário não estiver ativo
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return current_user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency para garantir que usuário é admin

    Returns:
        Dados do usuário admin

    Raises:
        HTTPException: Se usuário não for admin
    """
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )

    return current_user


async def get_current_super_admin(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency para garantir que usuário é super admin

    Returns:
        Dados do super admin

    Raises:
        HTTPException: Se usuário não for super admin
    """
    if current_user.get("role") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas super administradores."
        )

    return current_user


def check_plan_feature(feature: str):
    """
    Decorator para verificar se plano do usuário tem determinada feature

    Args:
        feature: Nome da feature (ex: "has_api_access", "has_variables")

    Returns:
        Dependency function
    """
    async def verify_feature(current_user: dict = Depends(get_current_user)):
        from backend.app.core.database import get_subscriptions_collection, get_plans_collection

        # Busca assinatura ativa do usuário
        subscriptions_collection = get_subscriptions_collection()
        subscription = await find_one_active(
            subscriptions_collection,
            {
                "user_id": current_user["_id"],
                "status": "active"
            }
        )

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nenhuma assinatura ativa"
            )

        # Busca plano
        plans_collection = get_plans_collection()
        plan = await find_one_active(
            plans_collection,
            {"_id": subscription["plan_id"]}
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano não encontrado"
            )

        # Verifica feature
        if not plan.get("features", {}).get(feature, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu plano não possui acesso a esta funcionalidade. Upgrade necessário."
            )

        return current_user

    return verify_feature


async def verify_device_limit(current_user: dict = Depends(get_current_user)):
    """
    Verifica se usuário atingiu limite de dispositivos do plano

    Returns:
        Dados do usuário

    Raises:
        HTTPException: Se limite de dispositivos foi atingido
    """
    from backend.app.core.database import get_subscriptions_collection, get_plans_collection

    # Busca assinatura ativa
    subscriptions_collection = get_subscriptions_collection()
    subscription = await find_one_active(
        subscriptions_collection,
        {
            "user_id": current_user["_id"],
            "status": "active"
        }
    )

    if not subscription:
        # Plano free - limite 1 dispositivo
        max_devices = 1
    else:
        # Busca plano
        plans_collection = get_plans_collection()
        plan = await find_one_active(
            plans_collection,
            {"_id": subscription["plan_id"]}
        )

        if not plan:
            max_devices = 1
        else:
            max_devices = plan.get("features", {}).get("max_devices", 1)

    # Conta dispositivos ativos
    active_devices = len(current_user.get("active_devices", []))

    if active_devices >= max_devices:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite de dispositivos atingido ({max_devices}). Faça upgrade do plano ou desconecte um dispositivo."
        )

    return current_user


# Alias para compatibilidade com rotas admin
require_admin = Depends(get_current_admin_user)
