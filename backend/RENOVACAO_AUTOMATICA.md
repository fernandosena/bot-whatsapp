# Sistema de Renovação Automática de Assinaturas

## Visão Geral

Sistema completo para gerenciar renovações automáticas de assinaturas através de diferentes gateways de pagamento (Stripe, Mercado Pago, PayPal).

## Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                     SCHEDULER (APScheduler)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  check_expiring_subscriptions (Diário 9h)            │  │
│  │  • Verifica assinaturas expirando em 3 dias          │  │
│  │  • Envia email de aviso                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  process_expired_subscriptions (Diário 00:30)        │  │
│  │  • Marca assinaturas expiradas como inactive         │  │
│  │  • Remove acesso do usuário                          │  │
│  │  • Envia email de expiração                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  renew_subscriptions (Diário 2h)                     │  │
│  │  • Renova assinaturas Stripe automaticamente         │  │
│  │  • Atualiza datas de período                         │  │
│  │  • Envia email de confirmação                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  cleanup_old_sessions (Semanal Domingo 3h)           │  │
│  │  • Remove sessões expiradas há >30 dias              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  cleanup_pending_payments (Mensal Dia 1 4h)          │  │
│  │  • Cancela pagamentos pendentes >7 dias              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Renovação

```
┌──────────────────────────────────────────────────────────────┐
│                  FLUXO DE RENOVAÇÃO AUTOMÁTICA                │
└──────────────────────────────────────────────────────────────┘

1. VERIFICAÇÃO (T-3 dias)
   ┌─────────────────────────┐
   │ check_expiring_         │
   │ subscriptions           │
   └────────────┬────────────┘
                │
                ├─► Busca assinaturas expirando em 3 dias
                ├─► Envia email de aviso
                └─► Marca como notificado

2. EXPIRAÇÃO (T+0 dias)
   ┌─────────────────────────┐
   │ process_expired_        │
   │ subscriptions           │
   └────────────┬────────────┘
                │
                ├─► Atualiza status: inactive
                ├─► Remove acesso do usuário
                ├─► Envia email de expiração
                └─► Log de auditoria

3. RENOVAÇÃO AUTOMÁTICA (Stripe)
   ┌─────────────────────────┐
   │ renew_subscriptions     │
   └────────────┬────────────┘
                │
                ├─► Consulta Stripe Subscription
                ├─► Verifica status (active)
                ├─► Atualiza período no banco
                ├─► Envia email de confirmação
                └─► Log de auditoria

4. RENOVAÇÃO MANUAL (Mercado Pago/PayPal)
   ┌─────────────────────────┐
   │ Webhooks                │
   └────────────┬────────────┘
                │
                ├─► Recebe notificação de pagamento
                ├─► process_approved_payment()
                ├─► Cria/renova assinatura
                ├─► Envia email de confirmação
                └─► Log de auditoria
```

## Configuração

### 1. Variáveis de Ambiente

```env
# Scheduler
ENABLE_SCHEDULER=true

# Stripe (renovação automática)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Mercado Pago (renovação manual via webhook)
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...
MERCADOPAGO_PUBLIC_KEY=APP_USR-...

# PayPal (renovação manual via webhook)
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=sandbox

# Email (notificações)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Inicialização

O scheduler é iniciado automaticamente no lifecycle da aplicação:

```python
# backend/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    enable_scheduler = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    if enable_scheduler:
        start_scheduler()

    yield

    # Shutdown
    if enable_scheduler:
        stop_scheduler()
```

## Gateways de Pagamento

### Stripe - Renovação Automática Nativa

O Stripe possui renovação automática integrada através de Subscriptions.

#### Como Funciona

1. **Criação da Subscription**
   ```python
   stripe_subscription = stripe.Subscription.create(
       customer=customer_id,
       items=[{"price": price_id}],
       payment_behavior="default_incomplete",
       expand=["latest_invoice.payment_intent"]
   )
   ```

2. **Stripe Renova Automaticamente**
   - Stripe cobra automaticamente no final do período
   - Webhook notifica sobre invoice.paid
   - Sistema atualiza assinatura no banco

3. **Job Sync (renew_subscriptions)**
   ```python
   # Busca subscription no Stripe
   stripe_sub = stripe.Subscription.retrieve(subscription_id)

   # Atualiza datas no banco
   new_period_end = datetime.fromtimestamp(
       stripe_sub.current_period_end
   )

   await subscriptions_collection.update_one(
       {"_id": subscription["_id"]},
       {"$set": {"current_period_end": new_period_end}}
   )
   ```

#### Webhooks Stripe

```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
    )

    if event.type == "invoice.paid":
        # Renovação bem-sucedida
        await process_stripe_renewal(event.data.object)

    elif event.type == "invoice.payment_failed":
        # Renovação falhou
        await process_stripe_failure(event.data.object)
```

### Mercado Pago - Renovação Manual

Mercado Pago não possui renovação automática nativa. Requer implementação manual.

#### Estratégias de Renovação

**1. Recorrência via Planos Mercado Pago**

```python
# Criar preapproval (assinatura recorrente)
preapproval_data = {
    "reason": "Plano Premium",
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 99.00,
        "currency_id": "BRL"
    },
    "back_url": f"{frontend_url}/subscription",
    "payer_email": user_email
}

preapproval = sdk.preapproval().create(preapproval_data)
```

**2. Cobrança Manual Programada**

```python
async def renew_mercadopago_subscription(subscription):
    """Cria novo pagamento para renovação"""

    # Buscar método de pagamento salvo
    saved_card = await get_user_saved_card(subscription["user_id"])

    if saved_card:
        # Criar pagamento com card_id
        payment_data = {
            "transaction_amount": plan["price_monthly"],
            "payment_method_id": "credit_card",
            "payer": {"email": user["email"]},
            "token": saved_card["token"]
        }

        payment = sdk.payment().create(payment_data)

        if payment["status"] == "approved":
            await process_approved_payment(payment_id, payment["id"])
```

**3. Email de Renovação Manual**

```python
async def send_renewal_reminder(subscription):
    """Envia email solicitando renovação manual"""

    await email_service.send_renewal_reminder_email(
        user_email=user["email"],
        plan_name=plan["name"],
        amount=plan["price_monthly"],
        renewal_link=f"{frontend_url}/checkout/{plan_id}"
    )
```

### PayPal - Renovação Automática via Subscriptions

PayPal possui suporte a assinaturas recorrentes.

#### Criar Subscription

```python
# 1. Criar plano no PayPal
plan = {
    "product_id": product_id,
    "name": "Plano Premium",
    "billing_cycles": [{
        "frequency": {
            "interval_unit": "MONTH",
            "interval_count": 1
        },
        "tenure_type": "REGULAR",
        "sequence": 1,
        "total_cycles": 0,  # Infinito
        "pricing_scheme": {
            "fixed_price": {
                "value": "99.00",
                "currency_code": "BRL"
            }
        }
    }],
    "payment_preferences": {
        "auto_bill_outstanding": True
    }
}

# 2. Criar subscription
subscription = {
    "plan_id": plan_id,
    "subscriber": {
        "email_address": user_email
    },
    "application_context": {
        "brand_name": "WhatsApp Business SaaS",
        "return_url": f"{frontend_url}/subscription/success",
        "cancel_url": f"{frontend_url}/subscription/cancel"
    }
}
```

#### Webhooks PayPal

```python
@router.post("/webhook")
async def paypal_webhook(request: Request):
    payload = await request.json()

    event_type = payload.get("event_type")

    if event_type == "BILLING.SUBSCRIPTION.PAYMENT.COMPLETED":
        # Renovação bem-sucedida
        await process_paypal_renewal(payload["resource"])

    elif event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        # Renovação falhou
        await process_paypal_failure(payload["resource"])
```

## Jobs Detalhados

### check_expiring_subscriptions

**Frequência**: Diariamente às 9h

**Função**: Avisa usuários sobre assinaturas próximas do vencimento

```python
async def check_expiring_subscriptions():
    # Data de corte: 3 dias a partir de agora
    three_days_from_now = datetime.utcnow() + timedelta(days=3)

    # Buscar assinaturas
    expiring_subscriptions = await subscriptions_collection.find({
        "status": "active",
        "flag_del": False,
        "current_period_end": {
            "$gte": datetime.utcnow(),
            "$lte": three_days_from_now
        },
        "expiration_warning_sent": {"$ne": True}
    }).to_list(length=None)

    # Processar cada assinatura
    for subscription in expiring_subscriptions:
        user = await users_collection.find_one(...)
        plan = await plans_collection.find_one(...)

        # Enviar email
        await send_expiring_notification(
            user_email=user["email"],
            user_name=user["name"],
            plan_name=plan["name"],
            expires_at=subscription["current_period_end"],
            days=3
        )

        # Marcar como notificado
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {"$set": {"expiration_warning_sent": True}}
        )
```

### process_expired_subscriptions

**Frequência**: Diariamente às 00:30

**Função**: Desativa assinaturas que expiraram

```python
async def process_expired_subscriptions():
    now = datetime.utcnow()

    # Buscar assinaturas expiradas ainda ativas
    expired_subscriptions = await subscriptions_collection.find({
        "status": "active",
        "flag_del": False,
        "current_period_end": {"$lt": now},
        "cancel_at_period_end": {"$ne": True}
    }).to_list(length=None)

    for subscription in expired_subscriptions:
        # Atualizar status
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

        # Remover acesso do usuário
        await users_collection.update_one(
            {"_id": ObjectId(subscription["user_id"])},
            {
                "$set": {
                    "current_plan_id": None,
                    "subscription_status": "expired"
                }
            }
        )

        # Enviar email
        await send_expired_notification(...)

        # Auditoria
        await log_audit(...)
```

### renew_subscriptions

**Frequência**: Diariamente às 2h

**Função**: Sincroniza renovações automáticas do Stripe

```python
async def renew_subscriptions():
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    today_end = today_start + timedelta(days=1)

    # Buscar assinaturas Stripe expirando hoje
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

    for subscription in subscriptions_to_renew:
        try:
            # Consultar Stripe
            stripe_sub = stripe.Subscription.retrieve(
                subscription["gateway_subscription_id"]
            )

            if stripe_sub.status == "active":
                # Atualizar período
                new_period_end = datetime.fromtimestamp(
                    stripe_sub.current_period_end
                )

                await subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "current_period_end": new_period_end,
                            "last_renewed_at": datetime.utcnow()
                        }
                    }
                )

                # Enviar email
                await send_renewed_notification(...)

                # Auditoria
                await log_audit(...)

        except stripe.error.StripeError as e:
            logger.error(f"Erro Stripe: {str(e)}")
```

## API de Gerenciamento

### Listar Jobs

```http
GET /api/admin/jobs
Authorization: Bearer <admin_token>
```

**Response**:
```json
{
  "total": 5,
  "jobs": [
    {
      "id": "check_expiring_subscriptions",
      "name": "check_expiring_subscriptions",
      "next_run": "2025-10-20T09:00:00",
      "trigger": "cron[day_of_week='*', hour='9', minute='0']"
    },
    ...
  ]
}
```

### Pausar Job

```http
POST /api/admin/jobs/check_expiring_subscriptions/pause
Authorization: Bearer <admin_token>
```

### Resumir Job

```http
POST /api/admin/jobs/check_expiring_subscriptions/resume
Authorization: Bearer <admin_token>
```

### Disparar Manualmente

```http
POST /api/admin/jobs/check_expiring_subscriptions/trigger
Authorization: Bearer <admin_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Job 'check_expiring_subscriptions' disparado manualmente",
  "triggered_by": "admin@example.com",
  "triggered_at": "2025-10-19T15:30:00"
}
```

### Estatísticas

```http
GET /api/admin/jobs/stats/summary
Authorization: Bearer <admin_token>
```

**Response**:
```json
{
  "total_jobs": 5,
  "next_execution": "2025-10-20T00:30:00",
  "jobs_by_type": {
    "subscription_jobs": 3,
    "cleanup_jobs": 2
  }
}
```

## Monitoramento

### Logs

```bash
# Ver logs em tempo real
tail -f logs/app.log | grep -E "(Job|Assinatura|Renovação)"

# Exemplos de logs
🔍 Verificando assinaturas expirando...
📊 Encontradas 5 assinaturas expirando
📧 Email de expiração enviado para user@example.com
✅ Job concluído: 5 notificações enviadas

🔍 Processando assinaturas expiradas...
📊 Encontradas 2 assinaturas expiradas
✅ Job concluído: 2 assinaturas expiradas processadas

🔄 Processando renovações automáticas...
📊 Encontradas 10 assinaturas para renovar
✅ Assinatura renovada via Stripe: user@example.com
✅ Job concluído: 10 renovadas, 0 falharam
```

### Métricas

```python
# Prometheus metrics
from prometheus_client import Counter, Gauge

subscriptions_renewed = Counter(
    'subscriptions_renewed_total',
    'Total de assinaturas renovadas'
)

subscriptions_expired = Counter(
    'subscriptions_expired_total',
    'Total de assinaturas expiradas'
)

active_subscriptions = Gauge(
    'active_subscriptions',
    'Número de assinaturas ativas'
)
```

### Alertas

Configure alertas para:

- ❌ Job falhando consecutivamente
- ⚠️ Alta taxa de renovações falhadas
- 📊 Aumento de assinaturas expirando
- 🔔 Email service down

## Testes

### Testar Jobs Localmente

```python
# test_jobs.py
import asyncio
from app.jobs.subscription_jobs import (
    check_expiring_subscriptions,
    process_expired_subscriptions,
    renew_subscriptions
)

async def test_jobs():
    # Testar verificação de expiração
    result = await check_expiring_subscriptions()
    print(f"✅ Expiring: {result}")

    # Testar processamento de expirados
    result = await process_expired_subscriptions()
    print(f"✅ Expired: {result}")

    # Testar renovações
    result = await renew_subscriptions()
    print(f"✅ Renewed: {result}")

asyncio.run(test_jobs())
```

### Criar Dados de Teste

```python
# Criar assinatura expirando em 3 dias
subscription_data = {
    "user_id": str(user_id),
    "plan_id": str(plan_id),
    "status": "active",
    "current_period_end": datetime.utcnow() + timedelta(days=3),
    "expiration_warning_sent": False,
    "created_at": datetime.utcnow()
}

await subscriptions_collection.insert_one(subscription_data)
```

## Troubleshooting

### Job não está executando

1. **Verificar se scheduler está habilitado**
   ```bash
   echo $ENABLE_SCHEDULER  # deve ser 'true'
   ```

2. **Verificar logs de inicialização**
   ```
   ✅ Aplicação pronta!
   📅 Scheduler iniciado
   📋 5 jobs registrados
   ```

3. **Listar jobs via API**
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/admin/jobs
   ```

### Stripe não renovando

1. **Verificar webhook configurado**
   - Dashboard Stripe → Developers → Webhooks
   - URL: `https://yourdomain.com/api/payments/stripe/webhook`
   - Events: `invoice.paid`, `invoice.payment_failed`

2. **Testar webhook**
   ```bash
   stripe trigger invoice.payment_succeeded
   ```

3. **Verificar logs**
   ```bash
   tail -f logs/app.log | grep -i stripe
   ```

### Email não enviando

Ver [SISTEMA_NOTIFICACOES.md](./SISTEMA_NOTIFICACOES.md)

## Manutenção

### Atualizar Frequência de Jobs

```python
# app/core/scheduler.py

# De diário para 2x ao dia
scheduler.add_job(
    check_expiring_subscriptions,
    trigger=CronTrigger(hour="9,21", minute=0),  # 9h e 21h
    id='check_expiring_subscriptions'
)
```

### Adicionar Novo Job

```python
# 1. Criar função no arquivo de jobs
async def send_monthly_report():
    # Lógica do job
    pass

# 2. Registrar no scheduler
scheduler.add_job(
    send_monthly_report,
    trigger=CronTrigger(day=1, hour=10, minute=0),  # Dia 1 às 10h
    id='send_monthly_report',
    max_instances=1
)
```

## Referências

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Mercado Pago Preapprovals](https://www.mercadopago.com.br/developers/pt/docs/subscriptions/integration-api)
- [PayPal Subscriptions](https://developer.paypal.com/docs/subscriptions/)
