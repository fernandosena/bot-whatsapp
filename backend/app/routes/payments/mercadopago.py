"""
Mercado Pago Payment Routes

Integração completa com Mercado Pago:
- PIX
- Boleto
- Cartão de Crédito
- Webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
import mercadopago
import os
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PaymentMethod,
    PaymentGateway,
    WebhookPayload
)
from app.core.database import get_payments_collection, get_plans_collection, get_users_collection
from app.middleware.auth import get_current_user
from app.utils.audit import log_audit

router = APIRouter()

# Configurar SDK do Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)


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


async def create_payment_record(
    user_id: str,
    plan_id: str,
    gateway_payment_id: str,
    amount: float,
    payment_method: PaymentMethod,
    status: PaymentStatus,
    pix_qr_code: Optional[str] = None,
    pix_qr_code_base64: Optional[str] = None,
    boleto_url: Optional[str] = None,
    boleto_barcode: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    gateway_response: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Cria registro de pagamento no MongoDB"""
    payments_collection = get_payments_collection()

    payment_data = {
        "user_id": user_id,
        "plan_id": plan_id,
        "gateway": PaymentGateway.MERCADOPAGO.value,
        "gateway_payment_id": gateway_payment_id,
        "amount": amount,
        "currency": "BRL",
        "payment_method": payment_method.value,
        "status": status.value,
        "pix_qr_code": pix_qr_code,
        "pix_qr_code_base64": pix_qr_code_base64,
        "boleto_url": boleto_url,
        "boleto_barcode": boleto_barcode,
        "expires_at": expires_at,
        "gateway_response": gateway_response,
        "created_at": datetime.utcnow(),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "flag_del": False
    }

    result = await payments_collection.insert_one(payment_data)
    payment_data["_id"] = result.inserted_id
    return payment_data


# ==================== Endpoints ====================

@router.post("/create-preference", response_model=PaymentResponse)
async def create_mercadopago_preference(
    request: CreatePaymentRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    user_agent: Optional[str] = Header(None)
):
    """
    Cria preferência de pagamento no Mercado Pago

    Suporta:
    - PIX
    - Boleto
    - Cartão de Crédito/Débito

    Returns:
        PaymentResponse com checkout_url ou pix_qr_code
    """
    try:
        # Buscar plano
        plan = await get_plan_by_id(request.plan_id)

        # Determinar valor (mensal ou anual)
        amount = plan["price_monthly"]

        # Preparar item
        item = {
            "title": plan["name"],
            "description": plan["description"],
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(amount)
        }

        # Configurar preferência base
        preference_data = {
            "items": [item],
            "payer": {
                "email": current_user.get("email"),
                "name": current_user.get("full_name", ""),
            },
            "back_urls": {
                "success": f"{os.getenv('FRONTEND_URL')}/checkout/success",
                "failure": f"{os.getenv('FRONTEND_URL')}/checkout/failed",
                "pending": f"{os.getenv('FRONTEND_URL')}/checkout/pending"
            },
            "auto_return": "approved",
            "notification_url": f"{os.getenv('BACKEND_URL')}/api/payments/mercadopago/webhook",
            "metadata": {
                "user_id": current_user["user_id"],
                "plan_id": request.plan_id,
                "payment_method": request.payment_method.value
            }
        }

        # Configurar método de pagamento
        if request.payment_method == PaymentMethod.PIX:
            # PIX
            preference_data["payment_methods"] = {
                "excluded_payment_methods": [],
                "excluded_payment_types": [
                    {"id": "credit_card"},
                    {"id": "debit_card"},
                    {"id": "ticket"}  # boleto
                ],
                "installments": 1
            }
            preference_data["expires"] = True
            preference_data["expiration_date_from"] = datetime.utcnow().isoformat()
            preference_data["expiration_date_to"] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()

        elif request.payment_method == PaymentMethod.BOLETO:
            # Boleto
            preference_data["payment_methods"] = {
                "excluded_payment_methods": [],
                "excluded_payment_types": [
                    {"id": "credit_card"},
                    {"id": "debit_card"},
                ],
                "installments": 1
            }
            preference_data["date_of_expiration"] = (datetime.utcnow() + timedelta(days=3)).isoformat()

        elif request.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            # Cartão
            preference_data["payment_methods"] = {
                "excluded_payment_types": [
                    {"id": "ticket"}  # boleto
                ],
                "installments": 12  # Até 12x
            }

        # Criar preferência
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        if preference_response["status"] != 201:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao criar preferência: {preference_response.get('error', 'Erro desconhecido')}"
            )

        # Determinar URLs e dados
        checkout_url = preference.get("init_point")  # URL de checkout
        pix_qr_code = None
        pix_qr_code_base64 = None
        boleto_url = None
        expires_at = None

        # Se for PIX, buscar QR Code (será gerado após pagamento iniciado)
        if request.payment_method == PaymentMethod.PIX:
            expires_at = datetime.utcnow() + timedelta(minutes=30)

        # Se for Boleto
        elif request.payment_method == PaymentMethod.BOLETO:
            expires_at = datetime.utcnow() + timedelta(days=3)

        # Criar registro de pagamento
        payment_record = await create_payment_record(
            user_id=current_user["user_id"],
            plan_id=request.plan_id,
            gateway_payment_id=preference["id"],
            amount=amount,
            payment_method=request.payment_method,
            status=PaymentStatus.PENDING,
            pix_qr_code=pix_qr_code,
            pix_qr_code_base64=pix_qr_code_base64,
            boleto_url=boleto_url,
            expires_at=expires_at,
            gateway_response=preference,
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=user_agent
        )

        # Log de auditoria
        await log_audit(
            user_id=current_user["user_id"],
            action="create_payment",
            description=f"Criou pagamento Mercado Pago ({request.payment_method.value})",
            metadata={
                "payment_id": str(payment_record["_id"]),
                "amount": amount,
                "plan_id": request.plan_id,
                "gateway": "mercadopago"
            }
        )

        return PaymentResponse(
            payment_id=str(payment_record["_id"]),
            status=PaymentStatus.PENDING,
            amount=amount,
            currency="BRL",
            payment_method=request.payment_method,
            gateway=PaymentGateway.MERCADOPAGO,
            checkout_url=checkout_url,
            pix_qr_code=pix_qr_code,
            pix_qr_code_base64=pix_qr_code_base64,
            boleto_url=boleto_url,
            gateway_payment_id=preference["id"],
            expires_at=expires_at,
            created_at=payment_record["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar pagamento Mercado Pago: {str(e)}"
        )


@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    """
    Webhook do Mercado Pago

    Recebe notificações de:
    - payment (pagamento criado/atualizado)
    - merchant_order (ordem criada/atualizada)

    Documentação: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
    """
    try:
        # Obter dados do webhook
        body = await request.json()
        query_params = dict(request.query_params)

        # Log do webhook
        print(f"[Mercado Pago Webhook] Body: {body}")
        print(f"[Mercado Pago Webhook] Params: {query_params}")

        # Tipo de notificação
        topic = query_params.get("topic") or body.get("type")
        resource_id = query_params.get("id") or body.get("data", {}).get("id")

        if not topic or not resource_id:
            return {"status": "ignored", "reason": "missing_topic_or_id"}

        # Processar baseado no tipo
        if topic == "payment":
            # Buscar informações do pagamento
            payment_info = sdk.payment().get(resource_id)
            payment_data = payment_info["response"]

            if payment_info["status"] != 200:
                return {"status": "error", "reason": "failed_to_fetch_payment"}

            # Mapear status
            status_map = {
                "approved": PaymentStatus.APPROVED,
                "pending": PaymentStatus.PENDING,
                "in_process": PaymentStatus.PROCESSING,
                "rejected": PaymentStatus.REJECTED,
                "cancelled": PaymentStatus.CANCELLED,
                "refunded": PaymentStatus.REFUNDED,
                "charged_back": PaymentStatus.CHARGEBACK
            }

            new_status = status_map.get(payment_data["status"], PaymentStatus.PENDING)

            # Buscar payment no banco
            payments_collection = get_payments_collection()

            # Buscar pelo preference_id (metadata)
            metadata = payment_data.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_id = metadata.get("plan_id")

            if not user_id or not plan_id:
                # Tentar buscar pelo external_reference
                external_ref = payment_data.get("external_reference")
                if external_ref:
                    payment_record = await payments_collection.find_one({
                        "gateway_payment_id": external_ref,
                        "flag_del": False
                    })
                else:
                    return {"status": "ignored", "reason": "no_user_or_plan_in_metadata"}
            else:
                # Buscar ou criar payment record
                payment_record = await payments_collection.find_one({
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "gateway": PaymentGateway.MERCADOPAGO.value,
                    "flag_del": False
                })

            # Atualizar ou criar
            update_data = {
                "status": new_status.value,
                "gateway_response": payment_data,
                "updated_at": datetime.utcnow()
            }

            # Se aprovado, salvar data de pagamento
            if new_status == PaymentStatus.APPROVED:
                update_data["paid_at"] = datetime.utcnow()

                # Se tiver PIX QR Code
                if payment_data.get("point_of_interaction"):
                    poi = payment_data["point_of_interaction"]
                    if poi.get("transaction_data"):
                        td = poi["transaction_data"]
                        update_data["pix_qr_code"] = td.get("qr_code")
                        update_data["pix_qr_code_base64"] = td.get("qr_code_base64")

                # Ativar assinatura do usuário
                if payment_record:
                    from app.core.database import get_subscriptions_collection
                    subscriptions_collection = get_subscriptions_collection()

                    # Buscar ou criar subscription
                    subscription = await subscriptions_collection.find_one({
                        "user_id": payment_record["user_id"],
                        "plan_id": payment_record["plan_id"],
                        "flag_del": False
                    })

                    if subscription:
                        # Atualizar subscription existente
                        await subscriptions_collection.update_one(
                            {"_id": subscription["_id"]},
                            {"$set": {
                                "status": "active",
                                "current_period_start": datetime.utcnow(),
                                "current_period_end": datetime.utcnow() + timedelta(days=30),
                                "updated_at": datetime.utcnow()
                            }}
                        )
                    else:
                        # Criar nova subscription
                        await subscriptions_collection.insert_one({
                            "user_id": payment_record["user_id"],
                            "plan_id": payment_record["plan_id"],
                            "status": "active",
                            "current_period_start": datetime.utcnow(),
                            "current_period_end": datetime.utcnow() + timedelta(days=30),
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "flag_del": False
                        })

            if payment_record:
                # Atualizar
                await payments_collection.update_one(
                    {"_id": payment_record["_id"]},
                    {"$set": update_data}
                )
            else:
                # Criar novo (fallback)
                await payments_collection.insert_one({
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "gateway": PaymentGateway.MERCADOPAGO.value,
                    "gateway_payment_id": str(resource_id),
                    "amount": payment_data.get("transaction_amount", 0),
                    "currency": payment_data.get("currency_id", "BRL"),
                    "payment_method": PaymentMethod.PIX.value if payment_data.get("payment_type_id") == "bank_transfer" else PaymentMethod.CREDIT_CARD.value,
                    "created_at": datetime.utcnow(),
                    "flag_del": False,
                    **update_data
                })

            return {"status": "processed", "payment_status": new_status.value}

        elif topic == "merchant_order":
            # Merchant order atualizada
            return {"status": "ignored", "reason": "merchant_order_not_implemented"}

        return {"status": "ignored", "reason": "unknown_topic"}

    except Exception as e:
        print(f"[Mercado Pago Webhook] Erro: {str(e)}")
        return {"status": "error", "error": str(e)}


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Consulta status de um pagamento

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
            "user_id": current_user["user_id"],  # Só pode ver próprios pagamentos
            "flag_del": False
        })

        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        # Consultar status no Mercado Pago
        try:
            payment_info = sdk.payment().get(payment["gateway_payment_id"])
            if payment_info["status"] == 200:
                mp_payment = payment_info["response"]

                # Mapear status
                status_map = {
                    "approved": PaymentStatus.APPROVED,
                    "pending": PaymentStatus.PENDING,
                    "in_process": PaymentStatus.PROCESSING,
                    "rejected": PaymentStatus.REJECTED,
                    "cancelled": PaymentStatus.CANCELLED,
                    "refunded": PaymentStatus.REFUNDED,
                    "charged_back": PaymentStatus.CHARGEBACK
                }

                new_status = status_map.get(mp_payment["status"], PaymentStatus.PENDING)

                # Atualizar no banco se mudou
                if new_status.value != payment["status"]:
                    await payments_collection.update_one(
                        {"_id": payment["_id"]},
                        {"$set": {
                            "status": new_status.value,
                            "gateway_response": mp_payment,
                            "updated_at": datetime.utcnow()
                        }}
                    )
                    payment["status"] = new_status.value

        except Exception as e:
            print(f"Erro ao consultar Mercado Pago: {str(e)}")

        return {
            "payment_id": str(payment["_id"]),
            "status": payment["status"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "payment_method": payment["payment_method"],
            "created_at": payment["created_at"],
            "paid_at": payment.get("paid_at"),
            "pix_qr_code": payment.get("pix_qr_code"),
            "boleto_url": payment.get("boleto_url"),
            "expires_at": payment.get("expires_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar status: {str(e)}"
        )
