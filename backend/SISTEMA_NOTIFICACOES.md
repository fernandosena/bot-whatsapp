# Sistema de Notificações por Email

## Visão Geral

Sistema completo de envio de emails transacionais para notificar usuários sobre eventos importantes relacionados a assinaturas e pagamentos.

## Configuração

### Variáveis de Ambiente

```env
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Frontend URL (para links nos emails)
FRONTEND_URL=http://localhost:3000
```

### Gmail - Configuração de Senha de App

Para usar Gmail como servidor SMTP:

1. Acesse https://myaccount.google.com/security
2. Ative a "Verificação em duas etapas"
3. Vá em "Senhas de app"
4. Gere uma senha para "Mail"
5. Use essa senha em `SMTP_PASSWORD`

### Outros Provedores SMTP

#### SendGrid
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-api-key
```

#### Mailgun
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.com
SMTP_PASSWORD=your-mailgun-password
```

#### AWS SES
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-aws-smtp-username
SMTP_PASSWORD=your-aws-smtp-password
```

## Tipos de Emails

### 1. Assinatura Expirando (3 dias antes)

**Trigger**: Job `check_expiring_subscriptions` (diário às 9h)

**Conteúdo**:
- Aviso de expiração
- Data exata da expiração
- Dias restantes
- Botão para renovar

**Preview**:
```
⚠️ Aviso de Expiração

Sua assinatura do plano "Premium" expira em 3 dias!
Data de expiração: 25/10/2025 às 14:30

[Renovar Agora]
```

### 2. Assinatura Expirada

**Trigger**: Job `process_expired_subscriptions` (diário às 00:30)

**Conteúdo**:
- Notificação de expiração
- Data da expiração
- Consequências (acesso suspenso)
- Botão para renovar

**Preview**:
```
❌ Assinatura Expirada

Sua assinatura do plano "Premium" expirou.
Data de expiração: 22/10/2025 às 14:30

Seu acesso foi suspenso.
Seus dados estão seguros por 30 dias.

[Renovar Assinatura]
```

### 3. Assinatura Renovada

**Trigger**: Job `renew_subscriptions` (diário às 2h)

**Conteúdo**:
- Confirmação de renovação
- Valor cobrado
- Nova data de expiração
- Detalhes do plano

**Preview**:
```
✅ Renovação Confirmada!

Sua assinatura foi renovada com sucesso!

Plano: Premium
Valor: R$ 99,00
Válido até: 22/11/2025 às 14:30

[Acessar Dashboard]
```

### 4. Pagamento Aprovado

**Trigger**: Webhooks dos gateways de pagamento

**Conteúdo**:
- Confirmação de pagamento
- Detalhes da transação
- ID da transação
- Botão para dashboard

**Preview**:
```
✅ Pagamento Aprovado!

Seu pagamento foi aprovado com sucesso!

Plano: Premium
Valor: R$ 99,00
Forma de pagamento: Cartão de Crédito
ID da transação: MP-1234567890

[Começar Agora]
```

### 5. Boas-vindas

**Trigger**: Registro de novo usuário

**Conteúdo**:
- Mensagem de boas-vindas
- Próximos passos
- Links úteis

**Preview**:
```
🎉 Bem-vindo!

É um prazer ter você conosco!

Próximos Passos:
1. Escolha seu plano
2. Configure sua conta
3. Crie sua primeira campanha

[Ver Planos]
```

## Arquitetura

### Estrutura de Arquivos

```
backend/
├── app/
│   ├── core/
│   │   └── email.py              # Serviço de email (EmailService)
│   ├── jobs/
│   │   ├── subscription_jobs.py  # Jobs que enviam emails
│   │   └── cleanup_jobs.py
│   └── utils/
│       └── payment_processor.py  # Processa pagamentos e envia emails
```

### EmailService

Classe principal para envio de emails:

```python
from app.core.email import email_service

# Enviar email personalizado
await email_service.send_email(
    to="user@example.com",
    subject="Assunto",
    html_content="<html>...</html>",
    text_content="Texto alternativo"
)

# Enviar email de expiração
await email_service.send_subscription_expiring_email(
    user_email="user@example.com",
    user_name="João Silva",
    plan_name="Premium",
    expires_at=datetime.now() + timedelta(days=3),
    days_remaining=3
)
```

### Funções Auxiliares

```python
from app.core.email import (
    send_expiring_notification,
    send_expired_notification,
    send_renewed_notification,
    send_payment_notification,
    send_welcome
)

# Uso simplificado
await send_expiring_notification(
    user_email="user@example.com",
    user_name="João",
    plan_name="Premium",
    expires_at=datetime.now() + timedelta(days=3),
    days=3
)
```

## Design dos Emails

### Características

- **Responsivo**: Funciona em desktop e mobile
- **HTML + Texto**: Fallback para clientes que não suportam HTML
- **Inline CSS**: Compatibilidade com clientes de email
- **Branding**: Cores e estilos consistentes

### Cores

```css
/* Gradientes principais */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* Primário */
background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%);  /* Sucesso */
background: linear-gradient(135deg, #f56565 0%, #c53030 100%);  /* Erro */

/* Cores de destaque */
#667eea  /* Botões */
#48bb78  /* Sucesso */
#ffc107  /* Aviso */
#f56565  /* Erro */
```

### Template Base

Todos os emails seguem a estrutura:

```html
<div class="container">
    <div class="header">
        <!-- Título com gradiente -->
    </div>
    <div class="content">
        <!-- Saudação -->
        <!-- Conteúdo principal -->
        <!-- Box de destaque -->
        <!-- Informações em tabela -->
        <!-- Botão de ação -->
        <!-- Assinatura -->
    </div>
    <div class="footer">
        <!-- Informações legais -->
    </div>
</div>
```

## Integração com Jobs

### check_expiring_subscriptions

```python
# app/jobs/subscription_jobs.py

async def check_expiring_subscriptions():
    """Verifica assinaturas expirando em 3 dias"""

    # Buscar assinaturas
    expiring_subscriptions = await subscriptions_collection.find({
        "status": "active",
        "current_period_end": {
            "$gte": datetime.utcnow(),
            "$lte": datetime.utcnow() + timedelta(days=3)
        },
        "expiration_warning_sent": {"$ne": True}
    }).to_list(length=None)

    # Enviar emails
    for subscription in expiring_subscriptions:
        user = await get_user(subscription["user_id"])
        plan = await get_plan(subscription["plan_id"])

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

```python
async def process_expired_subscriptions():
    """Processa assinaturas expiradas"""

    expired_subscriptions = await subscriptions_collection.find({
        "status": "active",
        "current_period_end": {"$lt": datetime.utcnow()}
    }).to_list(length=None)

    for subscription in expired_subscriptions:
        # Atualizar status
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {"$set": {"status": "inactive"}}
        )

        # Enviar email
        user = await get_user(subscription["user_id"])
        plan = await get_plan(subscription["plan_id"])

        await send_expired_notification(
            user_email=user["email"],
            user_name=user["name"],
            plan_name=plan["name"],
            expired_at=datetime.utcnow()
        )
```

### renew_subscriptions

```python
async def renew_subscriptions():
    """Renova assinaturas automaticamente"""

    subscriptions_to_renew = await subscriptions_collection.find({
        "gateway": "stripe",
        "status": "active",
        "current_period_end": {
            "$gte": today_start,
            "$lt": today_end
        }
    }).to_list(length=None)

    for subscription in subscriptions_to_renew:
        # Processar renovação via Stripe
        stripe_sub = stripe.Subscription.retrieve(
            subscription["gateway_subscription_id"]
        )

        if stripe_sub.status == "active":
            # Atualizar datas
            new_period_end = datetime.fromtimestamp(
                stripe_sub.current_period_end
            )

            await subscriptions_collection.update_one(
                {"_id": subscription["_id"]},
                {"$set": {"current_period_end": new_period_end}}
            )

            # Enviar email
            user = await get_user(subscription["user_id"])
            plan = await get_plan(subscription["plan_id"])

            await send_renewed_notification(
                user_email=user["email"],
                user_name=user["name"],
                plan_name=plan["name"],
                new_period_end=new_period_end,
                amount=plan["price_monthly"]
            )
```

## Integração com Pagamentos

### Payment Processor

```python
# app/utils/payment_processor.py

from app.core.email import send_payment_notification

async def process_approved_payment(payment_id: str, gateway_payment_id: str):
    """Processa pagamento aprovado"""

    # Buscar dados
    payment = await get_payment(payment_id)
    user = await get_user(payment["user_id"])
    plan = await get_plan(payment["plan_id"])

    # Criar/renovar assinatura
    subscription = await create_or_renew_subscription(payment)

    # Atualizar pagamento
    await payments_collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": "approved"}}
    )

    # Enviar email
    await send_payment_notification(
        user_email=user["email"],
        user_name=user["name"],
        plan_name=plan["name"],
        amount=payment["amount"],
        payment_method="Cartão de Crédito",
        transaction_id=gateway_payment_id
    )
```

## Testes

### Testar Email Localmente

```python
# test_email.py
import asyncio
from datetime import datetime, timedelta
from app.core.email import email_service

async def test_emails():
    # Email de expiração
    await email_service.send_subscription_expiring_email(
        user_email="test@example.com",
        user_name="João Teste",
        plan_name="Premium",
        expires_at=datetime.now() + timedelta(days=3),
        days_remaining=3
    )

    print("✅ Email de teste enviado!")

asyncio.run(test_emails())
```

### Desabilitar Emails em Desenvolvimento

```env
# .env
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
```

Quando não configurado, o sistema apenas loga:
```
⚠️ SMTP não configurado. Emails não serão enviados.
📧 Email não enviado (SMTP desabilitado): user@example.com - Assunto
```

## Monitoramento

### Logs

Todos os envios são logados:

```
✅ Email service configurado: smtp.gmail.com:587
✅ Email enviado: user@example.com - ⚠️ Sua assinatura expira em 3 dias
❌ Erro ao enviar email para user@example.com: [Errno 111] Connection refused
```

### Auditoria

Envios de email são registrados na auditoria:

```python
await log_audit(
    collection_name="subscriptions",
    document_id=subscription_id,
    action="expiration_warning_sent",
    user_id=user_id,
    details={
        "expires_at": expires_at.isoformat(),
        "days_remaining": 3
    }
)
```

## Troubleshooting

### Email não está sendo enviado

1. **Verificar configuração SMTP**
   ```bash
   echo $SMTP_USER
   echo $SMTP_HOST
   ```

2. **Verificar logs**
   ```bash
   tail -f logs/app.log | grep "Email"
   ```

3. **Testar conexão SMTP**
   ```python
   import smtplib

   smtp = smtplib.SMTP('smtp.gmail.com', 587)
   smtp.starttls()
   smtp.login('user@gmail.com', 'password')
   smtp.quit()
   ```

### Gmail bloqueando acesso

- Use "Senha de app" em vez da senha normal
- Ative "Acesso a apps menos seguros" (não recomendado)
- Use OAuth2 (mais seguro)

### Emails indo para spam

1. Configure SPF, DKIM e DMARC no DNS
2. Use domínio verificado
3. Evite palavras "spam" no assunto
4. Use serviço profissional (SendGrid, Mailgun)

## Próximos Passos

- [ ] Adicionar templates personalizáveis por empresa
- [ ] Sistema de preferências de notificação
- [ ] Suporte a múltiplos idiomas
- [ ] Emails com anexos (recibos PDF)
- [ ] Tracking de abertura de emails
- [ ] A/B testing de templates
- [ ] Notificações por SMS/WhatsApp

## Referências

- [aiosmtplib Documentation](https://aiosmtplib.readthedocs.io/)
- [Email HTML Best Practices](https://www.campaignmonitor.com/dev-resources/guides/coding-html-emails/)
- [SMTP Settings - Gmail](https://support.google.com/mail/answer/7126229)
