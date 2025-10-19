"""
Stripe Payment Routes

Integração completa com Stripe:
- Cartão de Crédito
- Apple Pay
- Google Pay
- Assinaturas recorrentes
- Webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
import stripe
import os
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.payment import (
    CreatePaymentRequest,
    CreateSubscriptionRequest,
    CancelSubscriptionRequest,
    PaymentResponse,
    PaymentStatus,
    PaymentMethod,
    PaymentGateway
)
from app.core.database import (
    get_payments_collection,
    get_plans_collection,
    get_users_collection,
    get_subscriptions_collection
)
from app.middleware.auth import get_current_user
from app.utils.audit import log_audit

router = APIRouter()

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


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


async def get_or_create_stripe_customer(user_id: str, email: str, name: str):
    """Busca ou cria cliente no Stripe"""
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    # Se já tem customer_id, retornar
    stripe_customer_id = user.get("stripe_customer_id")
    if stripe_customer_id:
        try:
            customer = stripe.Customer.retrieve(stripe_customer_id)
            return customer
        except:
            pass  # Se não encontrou, criar novo

    # Criar novo customer
    customer = stripe.Customer.create(
        email=email,
        name=name,
        metadata={
            "user_id": user_id
        }
    )

    # Salvar customer_id no usuário
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"stripe_customer_id": customer.id}}
    )

    return customer


# ==================== Endpoints ====================

@router.post("/create-checkout-session", response_model=PaymentResponse)
async def create_stripe_checkout_session(
    request: CreatePaymentRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    user_agent: Optional[str] = Header(None)
):
    """
    Cria sessão de checkout do Stripe

    Suporta:
    - Cartão de Crédito/Débito
    - Apple Pay
    - Google Pay

    Returns:
        PaymentResponse com checkout_url
    """
    try:
        # Buscar plano
        plan = await get_plan_by_id(request.plan_id)

        # Determinar valor (mensal ou anual)
        amount = plan["price_monthly"]

        # Buscar ou criar customer
        customer = await get_or_create_stripe_customer(
            user_id=current_user["user_id"],
            email=current_user.get("email"),
            name=current_user.get("full_name", "")
        )

        # Criar sessão de checkout
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],  # card inclui Apple Pay e Google Pay automaticamente
            line_items=[{
                "price_data": {
                    "currency": "usd",  # Stripe trabalha principalmente com USD
                    "product_data": {
                        "name": plan["name"],
                        "description": plan["description"],
                    },
                    "unit_amount": int(amount * 100),  # Stripe usa centavos
                },
                "quantity": 1,
            }],
            mode="payment",  # Pagamento único
            success_url=f"{os.getenv('FRONTEND_URL')}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/checkout/failed",
            metadata={
                "user_id": current_user["user_id"],
                "plan_id": request.plan_id,
                "payment_method": request.payment_method.value
            }
        )

        # Criar registro de pagamento
        payments_collection = get_payments_collection()

        payment_data = {
            "user_id": current_user["user_id"],
            "plan_id": request.plan_id,
            "gateway": PaymentGateway.STRIPE.value,
            "gateway_payment_id": session.id,
            "gateway_customer_id": customer.id,
            "amount": amount,
            "currency": "USD",
            "payment_method": request.payment_method.value,
            "status": PaymentStatus.PENDING.value,
            "gateway_response": {
                "session_id": session.id,
                "customer_id": customer.id
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
            description=f"Criou pagamento Stripe ({request.payment_method.value})",
            metadata={
                "payment_id": str(result.inserted_id),
                "amount": amount,
                "plan_id": request.plan_id,
                "gateway": "stripe"
            }
        )

        return PaymentResponse(
            payment_id=str(result.inserted_id),
            status=PaymentStatus.PENDING,
            amount=amount,
            currency="USD",
            payment_method=request.payment_method,
            gateway=PaymentGateway.STRIPE,
            checkout_url=session.url,
            gateway_payment_id=session.id,
            created_at=payment_data["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar checkout Stripe: {str(e)}"
        )


@router.post("/create-subscription")
async def create_stripe_subscription(
    request: CreateSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Cria assinatura recorrente no Stripe

    Args:
        request: Dados da assinatura (plan_id, interval, card_token)

    Returns:
        Subscription criada com próxima cobrança
    """
    try:
        # Buscar plano
        plan = await get_plan_by_id(request.plan_id)

        # Determinar valor baseado no interval
        if request.interval == "yearly":
            amount = plan["price_yearly"]
        else:
            amount = plan["price_monthly"]

        # Buscar ou criar customer
        customer = await get_or_create_stripe_customer(
            user_id=current_user["user_id"],
            email=current_user.get("email"),
            name=current_user.get("full_name", "")
        )

        # Criar produto no Stripe (ou buscar existente)
        plan_stripe_product_id = plan.get("stripe_product_id")

        if not plan_stripe_product_id:
            # Criar produto
            product = stripe.Product.create(
                name=plan["name"],
                description=plan["description"],
                metadata={"plan_id": request.plan_id}
            )
            plan_stripe_product_id = product.id

            # Salvar no plano
            plans_collection = get_plans_collection()
            await plans_collection.update_one(
                {"_id": ObjectId(request.plan_id)},
                {"$set": {"stripe_product_id": plan_stripe_product_id}}
            )

        # Criar price no Stripe
        price = stripe.Price.create(
            product=plan_stripe_product_id,
            unit_amount=int(amount * 100),  # centavos
            currency="usd",
            recurring={
                "interval": "year" if request.interval == "yearly" else "month"
            }
        )

        # Anexar método de pagamento ao customer
        payment_method = stripe.PaymentMethod.attach(
            request.card_token,
            customer=customer.id
        )

        # Definir como método padrão
        stripe.Customer.modify(
            customer.id,
            invoice_settings={
                "default_payment_method": payment_method.id
            }
        )

        # Criar subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price.id}],
            metadata={
                "user_id": current_user["user_id"],
                "plan_id": request.plan_id,
                "interval": request.interval
            }
        )

        # Salvar subscription no MongoDB
        subscriptions_collection = get_subscriptions_collection()

        next_billing = datetime.fromtimestamp(subscription.current_period_end)

        subscription_data = {
            "user_id": current_user["user_id"],
            "plan_id": request.plan_id,
            "gateway": PaymentGateway.STRIPE.value,
            "gateway_subscription_id": subscription.id,
            "gateway_customer_id": customer.id,
            "status": "active" if subscription.status == "active" else "inactive",
            "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
            "current_period_end": next_billing,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "flag_del": False
        }

        await subscriptions_collection.insert_one(subscription_data)

        # Log de auditoria
        await log_audit(
            user_id=current_user["user_id"],
            action="create_subscription",
            description=f"Criou assinatura Stripe ({request.interval})",
            metadata={
                "plan_id": request.plan_id,
                "amount": amount,
                "interval": request.interval,
                "subscription_id": subscription.id
            }
        )

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_end": next_billing,
            "amount": amount,
            "currency": "USD",
            "interval": request.interval
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar assinatura Stripe: {str(e)}"
        )


@router.post("/cancel-subscription")
async def cancel_stripe_subscription(
    request: CancelSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancela assinatura recorrente no Stripe

    Args:
        request: Dados do cancelamento (reason, cancel_at_period_end)

    Returns:
        Confirmação de cancelamento
    """
    try:
        # Buscar subscription do usuário
        subscriptions_collection = get_subscriptions_collection()

        subscription = await subscriptions_collection.find_one({
            "user_id": current_user["user_id"],
            "gateway": PaymentGateway.STRIPE.value,
            "flag_del": False,
            "status": "active"
        })

        if not subscription:
            raise HTTPException(status_code=404, detail="Assinatura ativa não encontrada")

        # Cancelar no Stripe
        stripe_subscription_id = subscription["gateway_subscription_id"]

        if request.cancel_at_period_end:
            # Cancelar no fim do período
            stripe_sub = stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=True
            )
        else:
            # Cancelar imediatamente
            stripe_sub = stripe.Subscription.cancel(stripe_subscription_id)

        # Atualizar no MongoDB
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {"$set": {
                "status": "cancelled" if not request.cancel_at_period_end else "active",
                "cancel_at_period_end": request.cancel_at_period_end,
                "cancelled_at": datetime.utcnow(),
                "cancel_reason": request.reason,
                "updated_at": datetime.utcnow()
            }}
        )

        # Log de auditoria
        await log_audit(
            user_id=current_user["user_id"],
            action="cancel_subscription",
            description=f"Cancelou assinatura Stripe",
            metadata={
                "subscription_id": stripe_subscription_id,
                "reason": request.reason,
                "cancel_at_period_end": request.cancel_at_period_end
            }
        )

        return {
            "success": True,
            "message": "Assinatura cancelada com sucesso",
            "cancel_at_period_end": request.cancel_at_period_end,
            "current_period_end": subscription["current_period_end"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cancelar assinatura: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Webhook do Stripe

    Recebe eventos:
    - checkout.session.completed (checkout concluído)
    - payment_intent.succeeded (pagamento bem-sucedido)
    - payment_intent.payment_failed (pagamento falhou)
    - invoice.paid (fatura paga)
    - invoice.payment_failed (fatura não paga)
    - customer.subscription.deleted (assinatura cancelada)

    Documentação: https://stripe.com/docs/webhooks
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        # Verificar assinatura do webhook
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return {"error": "Invalid payload"}, 400
        except stripe.error.SignatureVerificationError:
            return {"error": "Invalid signature"}, 400

        # Processar evento
        event_type = event["type"]
        data = event["data"]["object"]

        print(f"[Stripe Webhook] Event: {event_type}")

        payments_collection = get_payments_collection()
        subscriptions_collection = get_subscriptions_collection()

        if event_type == "checkout.session.completed":
            # Checkout concluído
            session_id = data["id"]
            metadata = data.get("metadata", {})

            # Atualizar pagamento
            await payments_collection.update_one(
                {"gateway_payment_id": session_id},
                {"$set": {
                    "status": PaymentStatus.APPROVED.value,
                    "paid_at": datetime.utcnow(),
                    "gateway_response": data
                }}
            )

            # Ativar assinatura
            if metadata.get("user_id") and metadata.get("plan_id"):
                await subscriptions_collection.update_one(
                    {
                        "user_id": metadata["user_id"],
                        "plan_id": metadata["plan_id"],
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

        elif event_type == "payment_intent.succeeded":
            # Pagamento bem-sucedido
            payment_intent_id = data["id"]

            await payments_collection.update_one(
                {"gateway_payment_id": payment_intent_id},
                {"$set": {
                    "status": PaymentStatus.APPROVED.value,
                    "paid_at": datetime.utcnow(),
                    "gateway_response": data
                }}
            )

        elif event_type == "payment_intent.payment_failed":
            # Pagamento falhou
            payment_intent_id = data["id"]

            await payments_collection.update_one(
                {"gateway_payment_id": payment_intent_id},
                {"$set": {
                    "status": PaymentStatus.REJECTED.value,
                    "gateway_error": data.get("last_payment_error", {}).get("message"),
                    "gateway_response": data
                }}
            )

        elif event_type == "customer.subscription.deleted":
            # Assinatura cancelada
            subscription_id = data["id"]

            await subscriptions_collection.update_one(
                {"gateway_subscription_id": subscription_id},
                {"$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )

        return {"status": "processed", "event_type": event_type}

    except Exception as e:
        print(f"[Stripe Webhook] Erro: {str(e)}")
        return {"status": "error", "error": str(e)}


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Consulta status de um pagamento Stripe

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

        # Consultar status no Stripe
        try:
            session = stripe.checkout.Session.retrieve(payment["gateway_payment_id"])

            # Mapear status
            if session.payment_status == "paid":
                new_status = PaymentStatus.APPROVED
            elif session.payment_status == "unpaid":
                new_status = PaymentStatus.PENDING
            else:
                new_status = PaymentStatus.REJECTED

            # Atualizar se mudou
            if new_status.value != payment["status"]:
                await payments_collection.update_one(
                    {"_id": payment["_id"]},
                    {"$set": {
                        "status": new_status.value,
                        "gateway_response": dict(session),
                        "updated_at": datetime.utcnow()
                    }}
                )
                payment["status"] = new_status.value

        except Exception as e:
            print(f"Erro ao consultar Stripe: {str(e)}")

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
