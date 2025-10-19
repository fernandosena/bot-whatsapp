"""
Payment Processor - Processamento de Pagamentos

Lógica centralizada para processar pagamentos aprovados
e criar/atualizar assinaturas
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId

from app.core.database import (
    get_payments_collection,
    get_subscriptions_collection,
    get_users_collection,
    get_plans_collection
)
from app.core.email import send_payment_notification
from app.utils.audit import log_audit

logger = logging.getLogger(__name__)


async def process_approved_payment(
    payment_id: str,
    gateway_payment_id: str,
    gateway_subscription_id: Optional[str] = None
) -> Dict:
    """
    Processa um pagamento aprovado

    - Atualiza status do pagamento
    - Cria ou renova assinatura
    - Atualiza usuário
    - Envia email de confirmação

    Args:
        payment_id: ID do pagamento no banco
        gateway_payment_id: ID do pagamento no gateway
        gateway_subscription_id: ID da subscription no gateway (Stripe)

    Returns:
        Dict com resultado do processamento
    """
    try:
        payments_collection = get_payments_collection()
        subscriptions_collection = get_subscriptions_collection()
        users_collection = get_users_collection()
        plans_collection = get_plans_collection()

        # Buscar pagamento
        payment = await payments_collection.find_one({
            "_id": ObjectId(payment_id),
            "flag_del": False
        })

        if not payment:
            logger.error(f"❌ Pagamento não encontrado: {payment_id}")
            return {"success": False, "error": "Pagamento não encontrado"}

        # Verificar se já foi processado
        if payment.get("status") == "approved":
            logger.warning(f"⚠️ Pagamento já processado: {payment_id}")
            return {"success": True, "message": "Pagamento já processado"}

        # Buscar plano
        plan = await plans_collection.find_one({
            "_id": ObjectId(payment["plan_id"]),
            "flag_del": False
        })

        if not plan:
            logger.error(f"❌ Plano não encontrado: {payment['plan_id']}")
            return {"success": False, "error": "Plano não encontrado"}

        # Buscar usuário
        user = await users_collection.find_one({
            "_id": ObjectId(payment["user_id"]),
            "flag_del": False
        })

        if not user:
            logger.error(f"❌ Usuário não encontrado: {payment['user_id']}")
            return {"success": False, "error": "Usuário não encontrado"}

        now = datetime.utcnow()

        # Calcular período da assinatura
        billing_cycle = payment.get("billing_cycle", "monthly")

        if billing_cycle == "monthly":
            period_days = 30
        elif billing_cycle == "quarterly":
            period_days = 90
        elif billing_cycle == "yearly":
            period_days = 365
        else:
            period_days = 30

        current_period_start = now
        current_period_end = now + timedelta(days=period_days)

        # Verificar se usuário já tem assinatura ativa
        existing_subscription = await subscriptions_collection.find_one({
            "user_id": str(payment["user_id"]),
            "status": "active",
            "flag_del": False
        })

        if existing_subscription:
            # Renovar assinatura existente
            await subscriptions_collection.update_one(
                {"_id": existing_subscription["_id"]},
                {
                    "$set": {
                        "current_period_start": current_period_start,
                        "current_period_end": current_period_end,
                        "last_payment_id": str(payment["_id"]),
                        "updated_at": now,
                        "last_renewed_at": now
                    }
                }
            )

            subscription_id = str(existing_subscription["_id"])
            action = "subscription_renewed"

            logger.info(f"✅ Assinatura renovada: {subscription_id}")

        else:
            # Criar nova assinatura
            subscription_data = {
                "user_id": str(payment["user_id"]),
                "plan_id": str(payment["plan_id"]),
                "status": "active",
                "billing_cycle": billing_cycle,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end,
                "gateway": payment["gateway"],
                "gateway_payment_id": gateway_payment_id,
                "gateway_subscription_id": gateway_subscription_id,
                "last_payment_id": str(payment["_id"]),
                "cancel_at_period_end": False,
                "created_at": now,
                "updated_at": now,
                "flag_del": False
            }

            result = await subscriptions_collection.insert_one(subscription_data)
            subscription_id = str(result.inserted_id)
            action = "subscription_created"

            logger.info(f"✅ Nova assinatura criada: {subscription_id}")

        # Atualizar pagamento
        await payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": "approved",
                    "gateway_payment_id": gateway_payment_id,
                    "subscription_id": subscription_id,
                    "approved_at": now,
                    "updated_at": now
                }
            }
        )

        # Atualizar usuário
        await users_collection.update_one(
            {"_id": ObjectId(payment["user_id"])},
            {
                "$set": {
                    "current_plan_id": str(payment["plan_id"]),
                    "subscription_status": "active",
                    "updated_at": now
                }
            }
        )

        # Enviar email de confirmação
        payment_method_map = {
            "credit_card": "Cartão de Crédito",
            "pix": "PIX",
            "boleto": "Boleto Bancário",
            "paypal": "PayPal"
        }

        await send_payment_notification(
            user_email=user.get("email"),
            user_name=user.get("name", "Usuário"),
            plan_name=plan.get("name", "Plano"),
            amount=payment.get("amount", 0),
            payment_method=payment_method_map.get(
                payment.get("payment_method"),
                payment.get("payment_method", "Desconhecido")
            ),
            transaction_id=gateway_payment_id
        )

        # Log de auditoria
        await log_audit(
            collection_name="payments",
            document_id=payment_id,
            action="payment_approved",
            user_id=str(payment["user_id"]),
            details={
                "gateway": payment["gateway"],
                "amount": payment["amount"],
                "gateway_payment_id": gateway_payment_id,
                "subscription_id": subscription_id
            }
        )

        await log_audit(
            collection_name="subscriptions",
            document_id=subscription_id,
            action=action,
            user_id=str(payment["user_id"]),
            details={
                "plan_id": str(payment["plan_id"]),
                "billing_cycle": billing_cycle,
                "period_end": current_period_end.isoformat()
            }
        )

        logger.info(
            f"✅ Pagamento processado com sucesso: "
            f"payment_id={payment_id}, subscription_id={subscription_id}"
        )

        return {
            "success": True,
            "payment_id": payment_id,
            "subscription_id": subscription_id,
            "message": "Pagamento processado e assinatura ativada"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao processar pagamento {payment_id}: {str(e)}")
        return {"success": False, "error": str(e)}


async def process_failed_payment(payment_id: str, reason: str) -> Dict:
    """
    Processa um pagamento que falhou

    Args:
        payment_id: ID do pagamento
        reason: Motivo da falha

    Returns:
        Dict com resultado
    """
    try:
        payments_collection = get_payments_collection()

        payment = await payments_collection.find_one({
            "_id": ObjectId(payment_id),
            "flag_del": False
        })

        if not payment:
            return {"success": False, "error": "Pagamento não encontrado"}

        now = datetime.utcnow()

        # Atualizar pagamento
        await payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": "failed",
                    "failure_reason": reason,
                    "failed_at": now,
                    "updated_at": now
                }
            }
        )

        # Log de auditoria
        await log_audit(
            collection_name="payments",
            document_id=payment_id,
            action="payment_failed",
            user_id=str(payment["user_id"]),
            details={
                "gateway": payment["gateway"],
                "amount": payment["amount"],
                "reason": reason
            }
        )

        # TODO: Enviar email de falha no pagamento

        logger.info(f"✅ Pagamento marcado como falho: {payment_id}")

        return {"success": True, "message": "Pagamento marcado como falho"}

    except Exception as e:
        logger.error(f"❌ Erro ao processar falha: {str(e)}")
        return {"success": False, "error": str(e)}


async def process_cancelled_payment(payment_id: str, reason: str) -> Dict:
    """
    Processa um pagamento cancelado

    Args:
        payment_id: ID do pagamento
        reason: Motivo do cancelamento

    Returns:
        Dict com resultado
    """
    try:
        payments_collection = get_payments_collection()

        payment = await payments_collection.find_one({
            "_id": ObjectId(payment_id),
            "flag_del": False
        })

        if not payment:
            return {"success": False, "error": "Pagamento não encontrado"}

        now = datetime.utcnow()

        # Atualizar pagamento
        await payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_reason": reason,
                    "cancelled_at": now,
                    "updated_at": now
                }
            }
        )

        # Log de auditoria
        await log_audit(
            collection_name="payments",
            document_id=payment_id,
            action="payment_cancelled",
            user_id=str(payment["user_id"]),
            details={
                "gateway": payment["gateway"],
                "reason": reason
            }
        )

        logger.info(f"✅ Pagamento cancelado: {payment_id}")

        return {"success": True, "message": "Pagamento cancelado"}

    except Exception as e:
        logger.error(f"❌ Erro ao cancelar pagamento: {str(e)}")
        return {"success": False, "error": str(e)}
