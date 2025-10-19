# Quick Start - Cron Jobs e Notificações

Guia rápido para começar a usar o sistema de renovação automática e notificações.

## 1. Instalação (2 minutos)

```bash
# Backend já possui as dependências necessárias
cd backend

# Instalar dependências (se ainda não fez)
pip install -r requirements.txt

# ou usando Poetry
poetry install
```

**Dependências principais instaladas**:
- ✅ `apscheduler==3.10.4` - Cron jobs
- ✅ `aiosmtplib==3.0.1` - Email async
- ✅ `stripe==7.10.0` - Stripe API

## 2. Configuração Básica (5 minutos)

### Criar arquivo `.env` no backend

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# Scheduler - IMPORTANTE!
ENABLE_SCHEDULER=true

# Email - Configure para enviar emails reais
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
SMTP_FROM=noreply@seudominio.com

# Frontend URL - para links nos emails
FRONTEND_URL=http://localhost:3000

# Stripe (para renovação automática)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Configurar Email Gmail (Opcional)

Se usar Gmail, precisa criar uma "Senha de App":

1. Acesse https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Vá em "Senhas de app"
4. Crie senha para "Mail"
5. Use em `SMTP_PASSWORD`

**Alternativa**: Use outro provedor SMTP (SendGrid, Mailgun, etc)

## 3. Iniciar Aplicação (30 segundos)

```bash
cd backend

# Desenvolvimento
uvicorn main:app --reload

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Logs esperados**:
```
🚀 Iniciando aplicação...
📦 MongoDB conectado
📅 Scheduler iniciado
📋 5 jobs registrados:
  - check_expiring_subscriptions (diário 9h)
  - process_expired_subscriptions (diário 00:30)
  - renew_subscriptions (diário 2h)
  - cleanup_old_sessions (semanal domingo 3h)
  - cleanup_pending_payments (mensal dia 1 4h)
✅ Aplicação pronta!
```

## 4. Verificar Jobs Ativos (API)

### Listar todos os jobs

```bash
# Obter token admin primeiro
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r .access_token)

# Listar jobs
curl http://localhost:8000/api/admin/jobs \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Response esperado**:
```json
{
  "total": 5,
  "jobs": [
    {
      "id": "check_expiring_subscriptions",
      "name": "check_expiring_subscriptions",
      "next_run": "2025-10-20T09:00:00.000000",
      "trigger": "cron[day_of_week='*', hour='9', minute='0']"
    },
    ...
  ]
}
```

## 5. Testar Manualmente (Desenvolvimento)

### Opção 1: Via API (Recomendado)

```bash
# Disparar job manualmente
curl -X POST http://localhost:8000/api/admin/jobs/check_expiring_subscriptions/trigger \
  -H "Authorization: Bearer $TOKEN"
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

### Opção 2: Via Python Script

```python
# test_jobs.py
import asyncio
from app.jobs.subscription_jobs import check_expiring_subscriptions

async def test():
    result = await check_expiring_subscriptions()
    print(result)

asyncio.run(test())
```

```bash
# Executar
cd backend
python test_jobs.py
```

## 6. Criar Dados de Teste (Opcional)

Se quiser testar com dados reais:

```python
# create_test_data.py
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import connect_to_mongo, get_subscriptions_collection, get_users_collection

async def create_test_subscription():
    await connect_to_mongo()

    subscriptions = get_subscriptions_collection()
    users = get_users_collection()

    # Criar usuário de teste
    user_data = {
        "name": "João Teste",
        "email": "joao.teste@example.com",
        "password_hash": "hashed",
        "created_at": datetime.utcnow(),
        "flag_del": False
    }
    user_result = await users.insert_one(user_data)

    # Criar assinatura expirando em 3 dias
    subscription_data = {
        "user_id": str(user_result.inserted_id),
        "plan_id": "plan_id_aqui",
        "status": "active",
        "billing_cycle": "monthly",
        "current_period_start": datetime.utcnow(),
        "current_period_end": datetime.utcnow() + timedelta(days=3),
        "gateway": "stripe",
        "expiration_warning_sent": False,
        "created_at": datetime.utcnow(),
        "flag_del": False
    }

    result = await subscriptions.insert_one(subscription_data)
    print(f"✅ Assinatura criada: {result.inserted_id}")
    print("   Expira em 3 dias")
    print("   Job check_expiring_subscriptions vai detectar!")

asyncio.run(create_test_subscription())
```

## 7. Monitorar Logs

```bash
# Ver logs em tempo real
tail -f logs/app.log

# Filtrar apenas jobs
tail -f logs/app.log | grep -E "(Job|🔍|📊|✅)"

# Filtrar emails
tail -f logs/app.log | grep -E "(Email|📧)"
```

**Logs esperados**:
```
🔍 Verificando assinaturas expirando...
📊 Encontradas 2 assinaturas expirando
📧 Email de expiração enviado para joao@example.com
✅ Job concluído: 2 notificações enviadas
```

## 8. Testar Envio de Email

```python
# test_email.py
import asyncio
from datetime import datetime, timedelta
from app.core.email import email_service

async def test_email():
    result = await email_service.send_subscription_expiring_email(
        user_email="seu-email@example.com",  # TROQUE pelo seu email
        user_name="João Teste",
        plan_name="Premium",
        expires_at=datetime.utcnow() + timedelta(days=3),
        days_remaining=3
    )

    if result:
        print("✅ Email enviado com sucesso!")
        print("   Verifique sua caixa de entrada")
    else:
        print("❌ Erro ao enviar email")
        print("   Verifique configurações SMTP no .env")

asyncio.run(test_email())
```

```bash
# Executar teste
cd backend
python test_email.py
```

## 9. Pausar/Resumir Jobs

### Pausar um job

```bash
curl -X POST http://localhost:8000/api/admin/jobs/check_expiring_subscriptions/pause \
  -H "Authorization: Bearer $TOKEN"
```

### Resumir um job pausado

```bash
curl -X POST http://localhost:8000/api/admin/jobs/check_expiring_subscriptions/resume \
  -H "Authorization: Bearer $TOKEN"
```

## 10. Desabilitar Scheduler (Desenvolvimento)

Se não quiser jobs rodando automaticamente durante desenvolvimento:

```env
# .env
ENABLE_SCHEDULER=false
```

**Logs ao iniciar**:
```
🚀 Iniciando aplicação...
⏸ Scheduler desabilitado (ENABLE_SCHEDULER=false)
✅ Aplicação pronta!
```

Você ainda pode disparar jobs manualmente via API.

## Troubleshooting Rápido

### Problema: Jobs não estão executando

**Solução**:
```bash
# 1. Verificar se scheduler está habilitado
grep ENABLE_SCHEDULER .env
# Deve retornar: ENABLE_SCHEDULER=true

# 2. Verificar logs de inicialização
# Deve aparecer: "📅 Scheduler iniciado"

# 3. Listar jobs via API
curl http://localhost:8000/api/admin/jobs -H "Authorization: Bearer $TOKEN"
```

### Problema: Emails não estão sendo enviados

**Solução**:
```bash
# 1. Verificar configuração SMTP
grep SMTP_ .env

# 2. Testar com script test_email.py
python test_email.py

# 3. Ver logs de erro
tail -f logs/app.log | grep -i email
```

**Erros comuns**:
- `SMTP não configurado` → Faltam variáveis no .env
- `Connection refused` → SMTP_HOST/PORT incorretos
- `Authentication failed` → SMTP_USER/PASSWORD incorretos

### Problema: MongoDB connection error

**Solução**:
```bash
# 1. Verificar se MongoDB está rodando
mongosh

# 2. Se não estiver, iniciar
# Linux/Mac
sudo systemctl start mongod

# Docker
docker-compose up -d mongodb
```

## Próximos Passos

Após configurar e testar:

1. **Configurar Webhooks** nos gateways de pagamento
2. **Configurar DNS** para email (SPF, DKIM, DMARC)
3. **Monitoramento** em produção (Sentry, logs)
4. **Backup** do banco de dados
5. **Testes automatizados**

## Documentação Completa

Para informações detalhadas, consulte:

- **SISTEMA_NOTIFICACOES.md** - Sistema de emails
- **RENOVACAO_AUTOMATICA.md** - Renovação e gateways
- **SESSAO_CRON_NOTIFICACOES.md** - Resumo da implementação

## Comandos Úteis

```bash
# Ver próximas execuções
curl http://localhost:8000/api/admin/jobs/stats/summary \
  -H "Authorization: Bearer $TOKEN" | jq

# Disparar todos os jobs (teste)
for job in check_expiring_subscriptions process_expired_subscriptions renew_subscriptions; do
  curl -X POST http://localhost:8000/api/admin/jobs/$job/trigger \
    -H "Authorization: Bearer $TOKEN"
done

# Monitorar execução
watch -n 5 'curl -s http://localhost:8000/api/admin/jobs -H "Authorization: Bearer $TOKEN" | jq ".jobs[] | {id, next_run}"'
```

## Suporte

Se encontrar problemas:

1. Verifique os logs: `tail -f logs/app.log`
2. Consulte a documentação completa
3. Verifique issues no GitHub
4. Contate o suporte

---

**Tempo total de setup**: ~10 minutos
**Pronto para produção**: Sim (com configurações adequadas)
