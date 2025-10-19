"""
Cleanup Jobs - Tarefas de Limpeza

Jobs para:
- Limpar sessões antigas
- Limpar pagamentos pendentes antigos
"""

import logging
from datetime import datetime, timedelta
from bson import ObjectId

from app.core.database import (
    get_sessions_collection,
    get_payments_collection
)
from app.utils.audit import log_audit

logger = logging.getLogger(__name__)


async def cleanup_old_sessions():
    """
    Remove sessões expiradas há mais de 30 dias

    Executa: Semanalmente (domingo às 3h)
    """
    logger.info("🧹 Limpando sessões antigas...")

    try:
        sessions_collection = get_sessions_collection()

        # Data de corte: 30 dias atrás
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Buscar sessões expiradas antigas que não foram deletadas
        old_sessions = await sessions_collection.find({
            "flag_del": False,
            "expires_at": {"$lt": cutoff_date}
        }).to_list(length=None)

        logger.info(f"📊 Encontradas {len(old_sessions)} sessões antigas para limpar")

        cleaned = 0

        for session in old_sessions:
            try:
                # Soft delete
                await sessions_collection.update_one(
                    {"_id": session["_id"]},
                    {
                        "$set": {
                            "flag_del": True,
                            "deleted_at": datetime.utcnow(),
                            "deleted_by": "system",
                            "deleted_reason": "Sessão expirada há mais de 30 dias (limpeza automática)"
                        }
                    }
                )

                # Log de auditoria
                await log_audit(
                    collection_name="sessions",
                    document_id=str(session["_id"]),
                    action="session_cleaned",
                    user_id=str(session.get("user_id", "system")),
                    details={
                        "expired_at": session.get("expires_at").isoformat() if session.get("expires_at") else None,
                        "days_old": (datetime.utcnow() - session.get("expires_at")).days if session.get("expires_at") else None
                    }
                )

                cleaned += 1

            except Exception as e:
                logger.error(f"❌ Erro ao limpar sessão {session['_id']}: {str(e)}")
                continue

        logger.info(f"✅ Job concluído: {cleaned} sessões limpas")

        return {
            "success": True,
            "total_found": len(old_sessions),
            "cleaned": cleaned
        }

    except Exception as e:
        logger.error(f"❌ Erro no job cleanup_old_sessions: {str(e)}")
        return {"success": False, "error": str(e)}


async def cleanup_pending_payments():
    """
    Remove pagamentos pendentes antigos (>7 dias)
    Pagamentos pendentes que não foram aprovados/rejeitados após 7 dias

    Executa: Mensalmente (dia 1 às 4h)
    """
    logger.info("🧹 Limpando pagamentos pendentes antigos...")

    try:
        payments_collection = get_payments_collection()

        # Data de corte: 7 dias atrás
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        # Buscar pagamentos pendentes antigos
        old_payments = await payments_collection.find({
            "flag_del": False,
            "status": "pending",
            "created_at": {"$lt": cutoff_date}
        }).to_list(length=None)

        logger.info(f"📊 Encontrados {len(old_payments)} pagamentos pendentes antigos")

        cleaned = 0

        for payment in old_payments:
            try:
                # Atualizar status para cancelled
                await payments_collection.update_one(
                    {"_id": payment["_id"]},
                    {
                        "$set": {
                            "status": "cancelled",
                            "cancelled_at": datetime.utcnow(),
                            "cancelled_reason": "Pagamento pendente expirado (>7 dias)",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

                # Log de auditoria
                await log_audit(
                    collection_name="payments",
                    document_id=str(payment["_id"]),
                    action="payment_auto_cancelled",
                    user_id=str(payment.get("user_id", "system")),
                    details={
                        "gateway": payment.get("gateway"),
                        "amount": payment.get("amount"),
                        "created_at": payment.get("created_at").isoformat() if payment.get("created_at") else None,
                        "days_pending": (datetime.utcnow() - payment.get("created_at")).days if payment.get("created_at") else None
                    }
                )

                cleaned += 1

            except Exception as e:
                logger.error(f"❌ Erro ao limpar pagamento {payment['_id']}: {str(e)}")
                continue

        logger.info(f"✅ Job concluído: {cleaned} pagamentos cancelados")

        return {
            "success": True,
            "total_found": len(old_payments),
            "cleaned": cleaned
        }

    except Exception as e:
        logger.error(f"❌ Erro no job cleanup_pending_payments: {str(e)}")
        return {"success": False, "error": str(e)}
