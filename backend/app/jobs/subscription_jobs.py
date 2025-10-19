"""
Subscription Jobs - Tarefas de Renovação de Assinaturas

Jobs para:
- Verificar assinaturas expirando
- Processar assinaturas expiradas
- Renovar assinaturas automaticamente
"""

import logging
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId
import stripe
import os

from app.core.database import (
    get_subscriptions_collection,
    get_users_collection,
    get_payments_collection,
    get_plans_collection
)
from app.utils.audit import log_audit
from app.core.email import (
    send_expiring_notification,
    send_expired_notification,
    send_renewed_notification
)

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def check_expiring_subscriptions():
    """
    Verifica assinaturas que vão expirar em 3 dias
    Envia notificação para o usuário

    Executa: Diariamente às 9h
    """
    logger.info("🔍 Verificando assinaturas expirando...")

    try:
        subscriptions_collection = get_subscriptions_collection()
        users_collection = get_users_collection()

        # Data de 3 dias a partir de agora
        three_days_from_now = datetime.utcnow() + timedelta(days=3)

        # Buscar assinaturas que expiram em ~3 dias
        # e que ainda não foram notificadas
        expiring_subscriptions = await subscriptions_collection.find({
            "status": "active",
            "flag_del": False,
            "current_period_end": {
                "$gte": datetime.utcnow(),
                "$lte": three_days_from_now
            },
            "expiration_warning_sent": {"$ne": True}
        }).to_list(length=None)

        logger.info(f"📊 Encontradas {len(expiring_subscriptions)} assinaturas expirando")

        notifications_sent = 0

        for subscription in expiring_subscriptions:
            try:
                # Buscar usuário
                user = await users_collection.find_one({
                    "_id": ObjectId(subscription["user_id"]),
                    "flag_del": False
                })

                if not user:
                    logger.warning(f"⚠️ Usuário não encontrado: {subscription['user_id']}")
                    continue

                # Buscar plano
                plan = await plans_collection.find_one({
                    "_id": ObjectId(subscription["plan_id"]),
                    "flag_del": False
                })

                # Enviar email de notificação
                if plan:
                    await send_expiring_notification(
                        user_email=user.get("email"),
                        user_name=user.get("name", "Usuário"),
                        plan_name=plan.get("name", "Plano"),
                        expires_at=subscription["current_period_end"],
                        days=3
                    )
                    logger.info(
                        f"📧 Email de expiração enviado para {user.get('email')}: "
                        f"Assinatura expira em {subscription['current_period_end']}"
                    )
                else:
                    logger.warning(f"⚠️ Plano não encontrado: {subscription['plan_id']}")

                # Marcar como notificado
                await subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "expiration_warning_sent": True,
                            "expiration_warning_sent_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

                # Log de auditoria
                await log_audit(
                    collection_name="subscriptions",
                    document_id=str(subscription["_id"]),
                    action="expiration_warning_sent",
                    user_id=str(subscription["user_id"]),
                    details={
                        "expires_at": subscription["current_period_end"].isoformat(),
                        "days_remaining": 3
                    }
                )

                notifications_sent += 1

            except Exception as e:
                logger.error(
                    f"❌ Erro ao processar assinatura {subscription['_id']}: {str(e)}"
                )
                continue

        logger.info(
            f"✅ Job concluído: {notifications_sent} notificações enviadas de "
            f"{len(expiring_subscriptions)} assinaturas"
        )

        return {
            "success": True,
            "total_found": len(expiring_subscriptions),
            "notifications_sent": notifications_sent
        }

    except Exception as e:
        logger.error(f"❌ Erro no job check_expiring_subscriptions: {str(e)}")
        return {"success": False, "error": str(e)}


async def process_expired_subscriptions():
    """
    Processa assinaturas que expiraram
    Marca como inactive e remove acesso

    Executa: Diariamente às 00:30
    """
    logger.info("🔍 Processando assinaturas expiradas...")

    try:
        subscriptions_collection = get_subscriptions_collection()
        users_collection = get_users_collection()

        # Buscar assinaturas expiradas que ainda estão ativas
        now = datetime.utcnow()

        expired_subscriptions = await subscriptions_collection.find({
            "status": "active",
            "flag_del": False,
            "current_period_end": {"$lt": now},
            "cancel_at_period_end": {"$ne": True}  # Não processar cancelamentos agendados
        }).to_list(length=None)

        logger.info(f"📊 Encontradas {len(expired_subscriptions)} assinaturas expiradas")

        processed = 0

        for subscription in expired_subscriptions:
            try:
                # Atualizar status da assinatura
                await subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "status": "inactive",
                            "expired_at": now,
                            "updated_at": now
                        }
                    }
                )

                # Atualizar usuário (remover plano ativo)
                await users_collection.update_one(
                    {"_id": ObjectId(subscription["user_id"])},
                    {
                        "$set": {
                            "current_plan_id": None,
                            "subscription_status": "expired",
                            "updated_at": now
                        }
                    }
                )

                # Buscar usuário e plano para enviar email
                user = await users_collection.find_one({
                    "_id": ObjectId(subscription["user_id"]),
                    "flag_del": False
                })

                plan = await plans_collection.find_one({
                    "_id": ObjectId(subscription["plan_id"]),
                    "flag_del": False
                })

                # Enviar email de expiração
                if user and plan:
                    await send_expired_notification(
                        user_email=user.get("email"),
                        user_name=user.get("name", "Usuário"),
                        plan_name=plan.get("name", "Plano"),
                        expired_at=now
                    )
                    logger.info(
                        f"📧 Email de expiração enviado: user_id={subscription['user_id']}, "
                        f"plan_id={subscription['plan_id']}"
                    )
                else:
                    logger.warning(f"⚠️ Usuário ou plano não encontrado para envio de email")

                # Log de auditoria
                await log_audit(
                    collection_name="subscriptions",
                    document_id=str(subscription["_id"]),
                    action="subscription_expired",
                    user_id=str(subscription["user_id"]),
                    details={
                        "plan_id": subscription["plan_id"],
                        "expired_at": now.isoformat()
                    }
                )

                processed += 1

            except Exception as e:
                logger.error(
                    f"❌ Erro ao processar assinatura expirada {subscription['_id']}: {str(e)}"
                )
                continue

        logger.info(
            f"✅ Job concluído: {processed} assinaturas expiradas processadas"
        )

        return {
            "success": True,
            "total_found": len(expired_subscriptions),
            "processed": processed
        }

    except Exception as e:
        logger.error(f"❌ Erro no job process_expired_subscriptions: {str(e)}")
        return {"success": False, "error": str(e)}


async def renew_subscriptions():
    """
    Renova assinaturas automaticamente (Stripe)
    Para assinaturas com renovação automática habilitada

    Executa: Diariamente às 2h
    """
    logger.info("🔄 Processando renovações automáticas...")

    try:
        subscriptions_collection = get_subscriptions_collection()
        payments_collection = get_payments_collection()
        users_collection = get_users_collection()
        plans_collection = get_plans_collection()

        # Buscar assinaturas Stripe que precisam renovar
        # (expiram hoje e têm auto-renovação)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        subscriptions_to_renew = await subscriptions_collection.find({
            "gateway": "stripe",
            "status": "active",
            "flag_del": False,
            "cancel_at_period_end": {"$ne": True},
            "current_period_end": {
                "$gte": today_start,
                "$lt": today_end
            }
        }).to_list(length=None)

        logger.info(f"📊 Encontradas {len(subscriptions_to_renew)} assinaturas para renovar")

        renewed = 0
        failed = 0

        for subscription in subscriptions_to_renew:
            try:
                # Buscar plano
                plan = await plans_collection.find_one({
                    "_id": ObjectId(subscription["plan_id"]),
                    "flag_del": False
                })

                if not plan:
                    logger.warning(f"⚠️ Plano não encontrado: {subscription['plan_id']}")
                    failed += 1
                    continue

                # Buscar usuário
                user = await users_collection.find_one({
                    "_id": ObjectId(subscription["user_id"]),
                    "flag_del": False
                })

                if not user:
                    logger.warning(f"⚠️ Usuário não encontrado: {subscription['user_id']}")
                    failed += 1
                    continue

                # Tentar renovar via Stripe
                if subscription.get("gateway_subscription_id"):
                    try:
                        # Buscar subscription no Stripe
                        stripe_sub = stripe.Subscription.retrieve(
                            subscription["gateway_subscription_id"]
                        )

                        # Verificar se está ativa
                        if stripe_sub.status == "active":
                            # Stripe renova automaticamente
                            # Apenas atualizar datas no nosso banco
                            new_period_end = datetime.fromtimestamp(
                                stripe_sub.current_period_end
                            )

                            await subscriptions_collection.update_one(
                                {"_id": subscription["_id"]},
                                {
                                    "$set": {
                                        "current_period_start": datetime.fromtimestamp(
                                            stripe_sub.current_period_start
                                        ),
                                        "current_period_end": new_period_end,
                                        "updated_at": datetime.utcnow(),
                                        "last_renewed_at": datetime.utcnow()
                                    }
                                }
                            )

                            # Enviar email de renovação
                            await send_renewed_notification(
                                user_email=user.get("email"),
                                user_name=user.get("name", "Usuário"),
                                plan_name=plan.get("name", "Plano"),
                                new_period_end=new_period_end,
                                amount=plan.get("price_monthly", 0)
                            )

                            logger.info(
                                f"✅ Assinatura renovada via Stripe: "
                                f"user={user.get('email')}, novo período até {new_period_end}"
                            )

                            # Log de auditoria
                            await log_audit(
                                collection_name="subscriptions",
                                document_id=str(subscription["_id"]),
                                action="subscription_renewed",
                                user_id=str(subscription["user_id"]),
                                details={
                                    "gateway": "stripe",
                                    "new_period_end": new_period_end.isoformat(),
                                    "amount": plan["price_monthly"]
                                }
                            )

                            renewed += 1

                        else:
                            logger.warning(
                                f"⚠️ Subscription Stripe não está ativa: {stripe_sub.status}"
                            )
                            failed += 1

                    except stripe.error.StripeError as e:
                        logger.error(f"❌ Erro Stripe ao renovar: {str(e)}")
                        failed += 1
                        continue

                else:
                    logger.warning(
                        f"⚠️ Assinatura sem gateway_subscription_id: {subscription['_id']}"
                    )
                    failed += 1

            except Exception as e:
                logger.error(
                    f"❌ Erro ao renovar assinatura {subscription['_id']}: {str(e)}"
                )
                failed += 1
                continue

        logger.info(
            f"✅ Job concluído: {renewed} renovadas, {failed} falharam de "
            f"{len(subscriptions_to_renew)} total"
        )

        return {
            "success": True,
            "total_found": len(subscriptions_to_renew),
            "renewed": renewed,
            "failed": failed
        }

    except Exception as e:
        logger.error(f"❌ Erro no job renew_subscriptions: {str(e)}")
        return {"success": False, "error": str(e)}
