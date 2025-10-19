"""
Payment History Routes

Endpoints para histórico de pagamentos e gerenciamento de assinatura
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.models.payment import PaymentListItem, PaymentHistoryResponse
from app.core.database import get_payments_collection, get_subscriptions_collection, get_plans_collection
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/my-payments", response_model=PaymentHistoryResponse)
async def get_my_payments(
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    gateway: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista pagamentos do usuário atual

    Args:
        limit: Quantidade máxima de resultados (1-100)
        status: Filtrar por status (approved, pending, rejected, etc)
        gateway: Filtrar por gateway (mercadopago, stripe, paypal)

    Returns:
        Lista de pagamentos com informações resumidas
    """
    try:
        payments_collection = get_payments_collection()
        plans_collection = get_plans_collection()

        # Construir query
        query = {
            "user_id": current_user["user_id"],
            "flag_del": False
        }

        if status:
            query["status"] = status

        if gateway:
            query["gateway"] = gateway

        # Buscar pagamentos
        cursor = payments_collection.find(query).sort("created_at", -1).limit(limit)
        payments = await cursor.to_list(length=limit)

        # Buscar nomes dos planos
        plan_ids = list(set([p["plan_id"] for p in payments if p.get("plan_id")]))
        plans_cursor = plans_collection.find({"_id": {"$in": [ObjectId(pid) for pid in plan_ids]}})
        plans_list = await plans_cursor.to_list(length=len(plan_ids))
        plans_map = {str(p["_id"]): p["name"] for p in plans_list}

        # Formatar resultado
        result = []
        for payment in payments:
            result.append(PaymentListItem(
                id=str(payment["_id"]),
                amount=payment["amount"],
                currency=payment.get("currency", "BRL"),
                status=payment["status"],
                payment_method=payment["payment_method"],
                gateway=payment["gateway"],
                created_at=payment["created_at"],
                paid_at=payment.get("paid_at"),
                plan_name=plans_map.get(payment.get("plan_id"))
            ))

        return PaymentHistoryResponse(
            total=len(result),
            payments=result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico de pagamentos: {str(e)}"
        )


@router.get("/my-subscription")
async def get_my_subscription(
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna detalhes da assinatura ativa do usuário

    Returns:
        Informações completas da assinatura
    """
    try:
        subscriptions_collection = get_subscriptions_collection()
        plans_collection = get_plans_collection()

        # Buscar assinatura ativa
        subscription = await subscriptions_collection.find_one({
            "user_id": current_user["user_id"],
            "flag_del": False,
            "status": "active"
        })

        if not subscription:
            return {
                "has_subscription": False,
                "message": "Nenhuma assinatura ativa encontrada"
            }

        # Buscar plano
        plan = await plans_collection.find_one({
            "_id": ObjectId(subscription["plan_id"]),
            "flag_del": False
        })

        if not plan:
            raise HTTPException(status_code=404, detail="Plano não encontrado")

        # Buscar último pagamento
        payments_collection = get_payments_collection()
        last_payment = await payments_collection.find_one(
            {
                "user_id": current_user["user_id"],
                "plan_id": subscription["plan_id"],
                "status": "approved",
                "flag_del": False
            },
            sort=[("paid_at", -1)]
        )

        return {
            "has_subscription": True,
            "subscription": {
                "id": str(subscription["_id"]),
                "status": subscription["status"],
                "current_period_start": subscription.get("current_period_start"),
                "current_period_end": subscription.get("current_period_end"),
                "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
                "cancelled_at": subscription.get("cancelled_at"),
                "gateway": subscription.get("gateway"),
                "gateway_subscription_id": subscription.get("gateway_subscription_id"),
                "created_at": subscription.get("created_at"),
            },
            "plan": {
                "id": str(plan["_id"]),
                "name": plan["name"],
                "description": plan["description"],
                "price_monthly": plan["price_monthly"],
                "price_yearly": plan["price_yearly"],
                "features": plan.get("features", {}),
            },
            "last_payment": {
                "id": str(last_payment["_id"]) if last_payment else None,
                "amount": last_payment["amount"] if last_payment else None,
                "paid_at": last_payment.get("paid_at") if last_payment else None,
                "payment_method": last_payment["payment_method"] if last_payment else None,
            } if last_payment else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar assinatura: {str(e)}"
        )


@router.get("/payment/{payment_id}")
async def get_payment_details(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna detalhes completos de um pagamento específico

    Args:
        payment_id: ID do pagamento

    Returns:
        Detalhes completos do pagamento
    """
    try:
        payments_collection = get_payments_collection()
        plans_collection = get_plans_collection()

        # Buscar pagamento
        payment = await payments_collection.find_one({
            "_id": ObjectId(payment_id),
            "user_id": current_user["user_id"],
            "flag_del": False
        })

        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        # Buscar plano
        plan = None
        if payment.get("plan_id"):
            plan = await plans_collection.find_one({
                "_id": ObjectId(payment["plan_id"]),
                "flag_del": False
            })

        return {
            "payment": {
                "id": str(payment["_id"]),
                "amount": payment["amount"],
                "currency": payment.get("currency", "BRL"),
                "status": payment["status"],
                "payment_method": payment["payment_method"],
                "gateway": payment["gateway"],
                "gateway_payment_id": payment["gateway_payment_id"],
                "created_at": payment["created_at"],
                "paid_at": payment.get("paid_at"),
                "expires_at": payment.get("expires_at"),
                "pix_qr_code": payment.get("pix_qr_code"),
                "pix_qr_code_base64": payment.get("pix_qr_code_base64"),
                "boleto_url": payment.get("boleto_url"),
                "boleto_barcode": payment.get("boleto_barcode"),
                "card_last_4_digits": payment.get("card_last_4_digits"),
                "card_brand": payment.get("card_brand"),
            },
            "plan": {
                "id": str(plan["_id"]),
                "name": plan["name"],
                "description": plan["description"],
            } if plan else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar detalhes do pagamento: {str(e)}"
        )


@router.get("/stats")
async def get_payment_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna estatísticas de pagamentos do usuário

    Returns:
        Estatísticas gerais (total gasto, pagamentos aprovados, etc)
    """
    try:
        payments_collection = get_payments_collection()

        # Agregação para estatísticas
        pipeline = [
            {
                "$match": {
                    "user_id": current_user["user_id"],
                    "flag_del": False
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_payments": {"$sum": 1},
                    "approved_payments": {
                        "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                    },
                    "pending_payments": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                    },
                    "rejected_payments": {
                        "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                    },
                    "total_spent": {
                        "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount", 0]}
                    },
                }
            }
        ]

        result = await payments_collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return {
                "total_payments": 0,
                "approved_payments": 0,
                "pending_payments": 0,
                "rejected_payments": 0,
                "total_spent": 0
            }

        return result[0]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )
