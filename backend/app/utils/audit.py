"""
Sistema de Auditoria - Registra TODAS as ações críticas do sistema
"""
from datetime import datetime
from typing import Dict, Optional, Any
from bson import ObjectId
from app.core.database import get_audit_logs_collection


async def log_audit(
    user_id: Optional[str],
    action: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success"
) -> Dict:
    """
    Registra ação de auditoria

    Args:
        user_id: ID do usuário que executou a ação
        action: Tipo de ação (ex: "user_login", "plan_created", "soft_delete")
        details: Detalhes adicionais da ação
        ip_address: IP do usuário
        user_agent: User agent do navegador
        status: Status da ação ("success", "failure", "warning")

    Returns:
        Registro de auditoria criado
    """
    audit_collection = get_audit_logs_collection()

    audit_log = {
        "user_id": ObjectId(user_id) if user_id else None,
        "action": action,
        "details": details,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "status": status,
        "timestamp": datetime.utcnow(),
        "flag_del": False,
        "deleted_at": None,
        "deleted_by": None,
        "deleted_reason": None
    }

    result = await audit_collection.insert_one(audit_log)
    audit_log["_id"] = result.inserted_id

    return audit_log


async def log_permanent_delete(collection_name: str, record_id: str):
    """
    Log OBRIGATÓRIO para deleções permanentes

    Args:
        collection_name: Nome da collection
        record_id: ID do registro deletado
    """
    await log_audit(
        user_id=None,  # Sistema
        action="PERMANENT_DELETE",
        details={
            "collection": collection_name,
            "record_id": record_id,
            "warning": "DELEÇÃO PERMANENTE - AÇÃO IRREVERSÍVEL"
        },
        status="warning"
    )


async def log_login(user_id: str, ip_address: str, user_agent: str, success: bool):
    """Log de tentativa de login"""
    await log_audit(
        user_id=user_id if success else None,
        action="user_login",
        details={"user_id": user_id},
        ip_address=ip_address,
        user_agent=user_agent,
        status="success" if success else "failure"
    )


async def log_logout(user_id: str, ip_address: str):
    """Log de logout"""
    await log_audit(
        user_id=user_id,
        action="user_logout",
        details={},
        ip_address=ip_address,
        status="success"
    )


async def log_plan_created(admin_id: str, plan_id: str, plan_name: str):
    """Log de criação de plano"""
    await log_audit(
        user_id=admin_id,
        action="plan_created",
        details={"plan_id": plan_id, "plan_name": plan_name},
        status="success"
    )


async def log_plan_updated(admin_id: str, plan_id: str, changes: Dict):
    """Log de atualização de plano"""
    await log_audit(
        user_id=admin_id,
        action="plan_updated",
        details={"plan_id": plan_id, "changes": changes},
        status="success"
    )


async def log_plan_deleted(admin_id: str, plan_id: str, reason: str):
    """Log de soft delete de plano"""
    await log_audit(
        user_id=admin_id,
        action="plan_soft_deleted",
        details={"plan_id": plan_id, "reason": reason},
        status="success"
    )


async def log_subscription_created(user_id: str, plan_id: str, payment_method: str):
    """Log de criação de assinatura"""
    await log_audit(
        user_id=user_id,
        action="subscription_created",
        details={"plan_id": plan_id, "payment_method": payment_method},
        status="success"
    )


async def log_payment(user_id: str, amount: float, payment_method: str, status: str):
    """Log de pagamento"""
    await log_audit(
        user_id=user_id,
        action="payment",
        details={
            "amount": amount,
            "payment_method": payment_method,
            "payment_status": status
        },
        status="success" if status == "approved" else "failure"
    )


async def log_data_restored(admin_id: str, collection: str, record_id: str):
    """Log de restauração de dados"""
    await log_audit(
        user_id=admin_id,
        action="data_restored",
        details={"collection": collection, "record_id": record_id},
        status="success"
    )


async def log_suspicious_activity(user_id: str, activity_type: str, details: Dict):
    """Log de atividade suspeita"""
    await log_audit(
        user_id=user_id,
        action="suspicious_activity",
        details={"activity_type": activity_type, **details},
        status="warning"
    )


async def log_ip_blocked(ip_address: str, reason: str):
    """Log de bloqueio de IP"""
    await log_audit(
        user_id=None,
        action="ip_blocked",
        details={"ip_address": ip_address, "reason": reason},
        status="warning"
    )


async def get_user_audit_history(user_id: str, limit: int = 100) -> list:
    """
    Busca histórico de auditoria de um usuário

    Args:
        user_id: ID do usuário
        limit: Quantidade máxima de registros

    Returns:
        Lista de logs de auditoria
    """
    audit_collection = get_audit_logs_collection()

    cursor = audit_collection.find(
        {"user_id": ObjectId(user_id), "flag_del": False}
    ).sort("timestamp", -1).limit(limit)

    return await cursor.to_list(length=limit)


async def get_recent_audits(limit: int = 100) -> list:
    """
    Busca logs de auditoria recentes

    Args:
        limit: Quantidade máxima de registros

    Returns:
        Lista de logs de auditoria
    """
    audit_collection = get_audit_logs_collection()

    cursor = audit_collection.find(
        {"flag_del": False}
    ).sort("timestamp", -1).limit(limit)

    return await cursor.to_list(length=limit)
