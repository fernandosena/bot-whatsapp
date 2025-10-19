"""
PayPal Payment Routes

Integração básica com PayPal:
- Pagamentos únicos
- Webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
import os
from datetime import datetime
from bson import ObjectId
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
import json

from app.models.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PaymentMethod,
    PaymentGateway
)
from app.core.database import get_payments_collection, get_plans_collection
from app.middleware.auth import get_current_user
from app.utils.audit import log_audit

router = APIRouter()

# Configurar PayPal
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox ou live

# Criar client
if PAYPAL_MODE == "live":
    environment = LiveEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
else:
    environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)

paypal_client = PayPalHttpClient(environment)


# ==================== Helper Functions ====================

async def get_plan_by_id(plan_id: str):
    """Busca plano por ID"""
    plans_collection = get_plans_collection()
    plan = await plans_collection.find_one({
        "_id": ObjectId(plan_id),
        "flag_del": False
    })
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return plan


# ==================== Endpoints ====================

@router.post("/create-order", response_model=PaymentResponse)
async def create_paypal_order(
    request: CreatePaymentRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    user_agent: Optional[str] = Header(None)
):
    """
    Cria ordem de pagamento no PayPal

    Args:
        request: Dados do pagamento

    Returns:
        PaymentResponse com checkout_url
    """
    try:
        # Buscar plano
        plan = await get_plan_by_id(request.plan_id)

        # Determinar valor
        amount = plan["price_monthly"]

        # Criar ordem no PayPal
        order_request = OrdersCreateRequest()
        order_request.prefer('return=representation')

        order_request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": str(amount)
                },
                "description": plan["name"],
                "custom_id": f"{current_user['user_id']}:{request.plan_id}"
            }],
            "application_context": {
                "return_url": f"{os.getenv('FRONTEND_URL')}/checkout/success",
                "cancel_url": f"{os.getenv('FRONTEND_URL')}/checkout/failed",
                "brand_name": "WhatsApp Business SaaS",
                "user_action": "PAY_NOW"
            }
        })

        # Executar request
        response = paypal_client.execute(order_request)

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao criar ordem PayPal: {response.status_code}"
            )

        order = response.result

        # Obter link de aprovação
        approval_link = None
        for link in order.links:
            if link.rel == "approve":
                approval_link = link.href
                break

        # Criar registro de pagamento
        payments_collection = get_payments_collection()

        payment_data = {
            "user_id": current_user["user_id"],
            "plan_id": request.plan_id,
            "gateway": PaymentGateway.PAYPAL.value,
            "gateway_payment_id": order.id,
            "amount": amount,
            "currency": "USD",
            "payment_method": PaymentMethod.PAYPAL.value,
            "status": PaymentStatus.PENDING.value,
            "gateway_response": {
                "order_id": order.id,
                "status": order.status
            },
            "created_at": datetime.utcnow(),
            "ip_address": http_request.client.host if http_request.client else None,
            "user_agent": user_agent,
            "flag_del": False
        }

        result = await payments_collection.insert_one(payment_data)

        # Log de auditoria
        await log_audit(
            user_id=current_user["user_id"],
            action="create_payment",
            description=f"Criou pagamento PayPal",
            metadata={
                "payment_id": str(result.inserted_id),
                "amount": amount,
                "plan_id": request.plan_id,
                "gateway": "paypal"
            }
        )

        return PaymentResponse(
            payment_id=str(result.inserted_id),
            status=PaymentStatus.PENDING,
            amount=amount,
            currency="USD",
            payment_method=PaymentMethod.PAYPAL,
            gateway=PaymentGateway.PAYPAL,
            checkout_url=approval_link,
            gateway_payment_id=order.id,
            created_at=payment_data["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar ordem PayPal: {str(e)}"
        )


@router.post("/capture-order/{order_id}")
async def capture_paypal_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Captura ordem aprovada do PayPal

    Args:
        order_id: ID da ordem no PayPal

    Returns:
        Status da captura
    """
    try:
        # Capturar ordem
        request = OrdersCaptureRequest(order_id)
        response = paypal_client.execute(request)

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao capturar ordem: {response.status_code}"
            )

        order = response.result

        # Atualizar pagamento no MongoDB
        payments_collection = get_payments_collection()

        # Mapear status
        if order.status == "COMPLETED":
            new_status = PaymentStatus.APPROVED
        else:
            new_status = PaymentStatus.PENDING

        await payments_collection.update_one(
            {"gateway_payment_id": order_id},
            {"$set": {
                "status": new_status.value,
                "paid_at": datetime.utcnow() if new_status == PaymentStatus.APPROVED else None,
                "gateway_response": {
                    "order_id": order.id,
                    "status": order.status,
                    "capture_id": order.purchase_units[0].payments.captures[0].id if order.purchase_units else None
                },
                "updated_at": datetime.utcnow()
            }}
        )

        # Se aprovado, ativar assinatura
        if new_status == PaymentStatus.APPROVED:
            payment = await payments_collection.find_one({"gateway_payment_id": order_id})

            if payment:
                from app.core.database import get_subscriptions_collection
                from datetime import timedelta

                subscriptions_collection = get_subscriptions_collection()

                await subscriptions_collection.update_one(
                    {
                        "user_id": payment["user_id"],
                        "plan_id": payment["plan_id"],
                        "flag_del": False
                    },
                    {"$set": {
                        "status": "active",
                        "current_period_start": datetime.utcnow(),
                        "current_period_end": datetime.utcnow() + timedelta(days=30),
                        "updated_at": datetime.utcnow()
                    }},
                    upsert=True
                )

        # Log de auditoria
        await log_audit(
            user_id=current_user["user_id"],
            action="capture_payment",
            description=f"Capturou pagamento PayPal",
            metadata={
                "order_id": order_id,
                "status": order.status
            }
        )

        return {
            "success": True,
            "order_id": order.id,
            "status": order.status,
            "amount": order.purchase_units[0].amount.value if order.purchase_units else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao capturar ordem: {str(e)}"
        )


@router.post("/webhook")
async def paypal_webhook(request: Request):
    """
    Webhook do PayPal

    Recebe eventos:
    - PAYMENT.CAPTURE.COMPLETED
    - PAYMENT.CAPTURE.DENIED
    - PAYMENT.CAPTURE.REFUNDED

    Documentação: https://developer.paypal.com/docs/api-basics/notifications/webhooks/
    """
    try:
        # Obter dados do webhook
        body = await request.json()

        print(f"[PayPal Webhook] Event: {body.get('event_type')}")

        event_type = body.get("event_type")
        resource = body.get("resource", {})

        payments_collection = get_payments_collection()

        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            # Pagamento capturado com sucesso
            order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")

            if order_id:
                await payments_collection.update_one(
                    {"gateway_payment_id": order_id},
                    {"$set": {
                        "status": PaymentStatus.APPROVED.value,
                        "paid_at": datetime.utcnow(),
                        "gateway_response": resource,
                        "updated_at": datetime.utcnow()
                    }}
                )

        elif event_type == "PAYMENT.CAPTURE.DENIED":
            # Pagamento negado
            order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")

            if order_id:
                await payments_collection.update_one(
                    {"gateway_payment_id": order_id},
                    {"$set": {
                        "status": PaymentStatus.REJECTED.value,
                        "gateway_response": resource,
                        "updated_at": datetime.utcnow()
                    }}
                )

        elif event_type == "PAYMENT.CAPTURE.REFUNDED":
            # Pagamento reembolsado
            order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")

            if order_id:
                await payments_collection.update_one(
                    {"gateway_payment_id": order_id},
                    {"$set": {
                        "status": PaymentStatus.REFUNDED.value,
                        "gateway_response": resource,
                        "updated_at": datetime.utcnow()
                    }}
                )

        return {"status": "processed", "event_type": event_type}

    except Exception as e:
        print(f"[PayPal Webhook] Erro: {str(e)}")
        return {"status": "error", "error": str(e)}


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Consulta status de um pagamento PayPal

    Args:
        payment_id: ID do pagamento no MongoDB

    Returns:
        Status atualizado do pagamento
    """
    try:
        payments_collection = get_payments_collection()

        # Buscar pagamento
        payment = await payments_collection.find_one({
            "_id": ObjectId(payment_id),
            "user_id": current_user["user_id"],
            "flag_del": False
        })

        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        # Consultar status no PayPal
        try:
            request = OrdersGetRequest(payment["gateway_payment_id"])
            response = paypal_client.execute(request)

            if response.status_code == 200:
                order = response.result

                # Mapear status
                status_map = {
                    "COMPLETED": PaymentStatus.APPROVED,
                    "APPROVED": PaymentStatus.PENDING,
                    "VOIDED": PaymentStatus.CANCELLED,
                    "CREATED": PaymentStatus.PENDING
                }

                new_status = status_map.get(order.status, PaymentStatus.PENDING)

                # Atualizar se mudou
                if new_status.value != payment["status"]:
                    await payments_collection.update_one(
                        {"_id": payment["_id"]},
                        {"$set": {
                            "status": new_status.value,
                            "gateway_response": {"order_id": order.id, "status": order.status},
                            "updated_at": datetime.utcnow()
                        }}
                    )
                    payment["status"] = new_status.value

        except Exception as e:
            print(f"Erro ao consultar PayPal: {str(e)}")

        return {
            "payment_id": str(payment["_id"]),
            "status": payment["status"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "payment_method": payment["payment_method"],
            "created_at": payment["created_at"],
            "paid_at": payment.get("paid_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar status: {str(e)}"
        )
