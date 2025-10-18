# 🎯 Próximos Passos - Roadmap de Desenvolvimento

Este documento detalha os próximos passos para levar o projeto de 45% para 100%.

---

## 📊 Status Atual

- **Backend:** 40% ✅ Funcional
- **Frontend:** 50% ✅ Funcional
- **Desktop:** 0% ⏳ Não iniciado
- **Pagamentos:** 0% ⏳ Não iniciado
- **WhatsApp:** 15% ⚠️ Código legado

**Progresso Geral:** 45%

---

## 🚀 Fase 1: Completar Frontend (50% → 80%)

### Prioridade: ALTA
**Tempo Estimado:** 1 semana

### 1.1 Painel Admin - Gerenciamento de Planos

**Arquivo:** `web/frontend/src/app/admin/plans/page.tsx`

**Features:**
- Tabela com todos os planos
- Botões de ação (editar, deletar, toggle status)
- Modal de criação de plano
- Modal de edição de plano
- Confirmação de deleção
- Visualização de planos deletados
- Botão de restaurar
- Estatísticas resumidas

**Componentes necessários:**
```bash
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add select
npx shadcn@latest add form
npx shadcn@latest add switch
npx shadcn@latest add alert-dialog
```

**Endpoints a usar:**
- GET /api/admin/plans/
- POST /api/admin/plans/
- PUT /api/admin/plans/{id}
- DELETE /api/admin/plans/{id}
- POST /api/admin/plans/{id}/toggle-status
- GET /api/admin/plans/deleted/list
- POST /api/admin/plans/deleted/{id}/restore
- GET /api/admin/plans/stats/summary

### 1.2 Painel Admin - Dashboard

**Arquivo:** `web/frontend/src/app/admin/dashboard/page.tsx`

**Features:**
- Métricas gerais (total usuários, receita, assinaturas ativas)
- Gráficos (usando recharts ou similar)
- Lista de últimas ações
- Top planos mais populares
- Últimos pagamentos

**Dependências:**
```bash
npm install recharts date-fns
```

### 1.3 Gerenciamento de Sessões

**Arquivo:** `web/frontend/src/app/settings/sessions/page.tsx`

**Features:**
- Lista de sessões ativas
- Info de cada sessão (IP, device, última atividade)
- Botão para encerrar sessão específica
- Botão para encerrar todas exceto atual

**Endpoint:**
- GET /api/auth/sessions
- DELETE /api/auth/sessions/{id}

### 1.4 Perfil do Usuário

**Arquivo:** `web/frontend/src/app/profile/page.tsx`

**Features:**
- Formulário de edição de dados
- Upload de avatar (futuramente)
- Alterar senha
- Verificar email

---

## 💳 Fase 2: Sistema de Pagamentos (0% → 100%)

### Prioridade: ALTA
**Tempo Estimado:** 2 semanas

### 2.1 Integração Mercado Pago

**Backend:** `backend/app/routes/payments/mercadopago.py`

**Endpoints a criar:**
```python
POST /api/payments/mercadopago/create-preference
POST /api/payments/mercadopago/webhook
GET /api/payments/mercadopago/status/{payment_id}
```

**Frontend:** `web/frontend/src/app/checkout/page.tsx`

**Features:**
- Página de checkout
- Integração com SDK do Mercado Pago
- Seleção de método (PIX, Boleto, Cartão)
- Redirecionamento pós-pagamento
- Página de sucesso/falha

**Instalação:**
```bash
# Backend
pip install mercadopago

# Frontend
npm install @mercadopago/sdk-react
```

### 2.2 Integração Stripe

**Backend:** `backend/app/routes/payments/stripe.py`

**Endpoints:**
```python
POST /api/payments/stripe/create-checkout-session
POST /api/payments/stripe/webhook
POST /api/payments/stripe/create-subscription
GET /api/payments/stripe/subscription/{id}
```

**Instalação:**
```bash
# Backend
pip install stripe

# Frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 2.3 Integração PayPal

**Backend:** `backend/app/routes/payments/paypal.py`

**Instalação:**
```bash
pip install paypalrestsdk
```

### 2.4 Gerenciamento de Assinaturas

**Backend:** `backend/app/routes/subscriptions.py`

**Endpoints:**
```python
GET /api/subscriptions/my-subscription
POST /api/subscriptions/cancel
POST /api/subscriptions/resume
PUT /api/subscriptions/change-plan
```

**Frontend:** `web/frontend/src/app/subscription/page.tsx`

**Features:**
- Detalhes da assinatura atual
- Botão de upgrade/downgrade
- Cancelar assinatura
- Histórico de pagamentos

---

## 🤖 Fase 3: Automações e Cron Jobs (0% → 100%)

### Prioridade: MÉDIA
**Tempo Estimado:** 1 semana

### 3.1 Cron Jobs

**Arquivo:** `backend/app/cron/jobs.py`

**Jobs a criar:**

1. **Aviso de Expiração** (diário às 9h)
   - Buscar assinaturas que expiram em 3 dias
   - Enviar email para usuário
   - Enviar email para admin

2. **Processar Assinaturas Expiradas** (diário às 0h)
   - Buscar assinaturas expiradas
   - Atualizar status para "expired"
   - Limitar acesso do usuário

3. **Renovação Automática** (diário às 2h)
   - Buscar assinaturas para renovar
   - Processar pagamento
   - Atualizar período

4. **Limpeza de Sessões** (diário às 4h)
   - Remover sessões antigas (>30 dias)
   - Limpar tokens expirados

5. **Notificar Updates Desktop** (diário às 10h)
   - Verificar se há nova versão
   - Notificar usuários desktop

**Instalação:**
```bash
pip install apscheduler
```

**Executar:**
```python
# backend/app/cron/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(check_expiring_subscriptions, 'cron', hour=9)
scheduler.add_job(process_expired_subscriptions, 'cron', hour=0)
# ...
scheduler.start()
```

### 3.2 Sistema de Emails

**Arquivo:** `backend/app/utils/email.py`

**Templates:**
- Boas-vindas
- Ativação de conta
- Pagamento aprovado
- Pagamento falhou
- Assinatura expirando
- Assinatura expirada
- Assinatura renovada

**Instalação:**
```bash
pip install aiosmtplib jinja2
```

---

## 💻 Fase 4: Desktop App (0% → 100%)

### Prioridade: MÉDIA
**Tempo Estimado:** 2 semanas

### 4.1 Configurar Electron

**Arquivos:**
```
desktop/
├── main.js              # Processo principal
├── preload.js           # IPC bridge
├── package.json         # Deps
└── renderer/            # UI
    └── index.html
```

**Instalação:**
```bash
cd desktop
npm init -y
npm install electron electron-builder
```

### 4.2 Sistema de Ativação

**Backend:** `backend/app/routes/desktop/activation.py`

**Endpoints:**
```python
POST /api/desktop/activate
GET /api/desktop/validate-key/{key}
POST /api/desktop/deactivate
```

**Frontend Desktop:**
- Tela de primeira ativação
- Input de chave de ativação
- Validação com backend
- Salvar credenciais (encrypted storage)

### 4.3 Sistema de Atualização

**Backend:** `backend/app/routes/desktop/updates.py`

**Endpoints:**
```python
GET /api/desktop/updates/latest
GET /api/desktop/updates/download/{version}
```

**Frontend Desktop:**
- Verificação automática de updates
- Download em background
- Instalação automática
- Bloqueio se update obrigatório

### 4.4 Build Multi-plataforma

**Configurar:** `desktop/package.json`

```json
{
  "build": {
    "appId": "com.whatsapp-business.app",
    "mac": {
      "target": "dmg"
    },
    "linux": {
      "target": ["AppImage", "deb"]
    },
    "win": {
      "target": ["nsis", "msi"]
    }
  }
}
```

**Build:**
```bash
npm run build:win
npm run build:mac
npm run build:linux
```

---

## 📱 Fase 5: WhatsApp Integration (15% → 100%)

### Prioridade: ALTA
**Tempo Estimado:** 2 semanas

### 5.1 Refatorar Código Existente

**Passos:**
1. Mover de `src/whatsapp/` para `backend/app/services/whatsapp/`
2. Substituir SQLite por MongoDB
3. Adicionar verificações de limites por plano
4. Integrar com sistema de auditoria

### 5.2 Criar Endpoints

**Arquivo:** `backend/app/routes/whatsapp/campaigns.py`

```python
POST /api/whatsapp/campaigns
GET /api/whatsapp/campaigns
GET /api/whatsapp/campaigns/{id}
PUT /api/whatsapp/campaigns/{id}
DELETE /api/whatsapp/campaigns/{id}
POST /api/whatsapp/campaigns/{id}/start
POST /api/whatsapp/campaigns/{id}/pause
GET /api/whatsapp/campaigns/{id}/stats
```

### 5.3 Gerenciamento de Contatos

**Arquivo:** `backend/app/routes/whatsapp/contacts.py`

```python
POST /api/whatsapp/contacts
GET /api/whatsapp/contacts
POST /api/whatsapp/contacts/import-csv
POST /api/whatsapp/contacts/import-gmaps
DELETE /api/whatsapp/contacts/{id}
```

### 5.4 Frontend - Campanhas

**Arquivo:** `web/frontend/src/app/campaigns/page.tsx`

**Features:**
- Lista de campanhas
- Criar nova campanha
- Editor de mensagem com variáveis
- Preview da mensagem
- Agendar campanha
- Iniciar/pausar campanha
- Ver estatísticas

---

## 📈 Fase 6: Monitoramento e Performance

### Prioridade: BAIXA
**Tempo Estimado:** 1 semana

### 6.1 Sentry (Error Tracking)

**Backend:**
```bash
pip install sentry-sdk[fastapi]
```

```python
# backend/main.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

**Frontend:**
```bash
npm install @sentry/nextjs
```

### 6.2 Prometheus + Grafana

**Instalação:**
```bash
pip install prometheus-client
```

**Métricas:**
- Requisições por segundo
- Tempo de resposta
- Erros por endpoint
- Usuários ativos
- Mensagens enviadas

### 6.3 Redis (Cache)

**Instalação:**
```bash
pip install redis aioredis
```

**Uso:**
- Cache de planos
- Rate limiting
- Session storage

---

## 🧪 Fase 7: Testes

### Prioridade: MÉDIA
**Tempo Estimado:** 1 semana

### 7.1 Testes Backend

**Instalação:**
```bash
pip install pytest pytest-asyncio httpx
```

**Criar:** `backend/tests/`

```
tests/
├── test_auth.py
├── test_plans.py
├── test_subscriptions.py
└── test_payments.py
```

**Executar:**
```bash
pytest backend/tests/ -v --cov
```

### 7.2 Testes Frontend

**Instalação:**
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @playwright/test
```

**Testes unitários:**
```bash
npm run test
```

**Testes E2E:**
```bash
npm run test:e2e
```

---

## 🚀 Fase 8: Deploy

### Prioridade: ALTA (quando estiver 90%+)
**Tempo Estimado:** 1 semana

### 8.1 Preparar Servidor

**Opções:**
- VPS (DigitalOcean, Linode, Vultr)
- Cloud (AWS, GCP, Azure)
- Managed (Heroku, Railway, Render)

**Instalar:**
- MongoDB
- Redis
- Nginx
- PM2
- Certbot (SSL)

### 8.2 Deploy Backend

```bash
# No servidor
git clone repo
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pm2 start main.py --name whatsapp-api
```

### 8.3 Deploy Frontend

**Opção 1: Vercel (recomendado)**
```bash
npm install -g vercel
vercel
```

**Opção 2: Build próprio**
```bash
npm run build
pm2 start npm --name whatsapp-web -- start
```

### 8.4 CI/CD

**GitHub Actions:** `.github/workflows/deploy.yml`

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy-backend:
    # ...
  deploy-frontend:
    # ...
```

---

## 📅 Timeline Sugerido

| Fase | Duração | Progresso |
|------|---------|-----------|
| Fase 1: Frontend 50→80% | 1 semana | 45% → 60% |
| Fase 2: Pagamentos | 2 semanas | 60% → 75% |
| Fase 3: Automações | 1 semana | 75% → 80% |
| Fase 4: Desktop | 2 semanas | 80% → 85% |
| Fase 5: WhatsApp | 2 semanas | 85% → 95% |
| Fase 6: Monitoramento | 1 semana | 95% → 97% |
| Fase 7: Testes | 1 semana | 97% → 99% |
| Fase 8: Deploy | 1 semana | 99% → 100% |
| **TOTAL** | **11 semanas** | **45% → 100%** |

---

## 🎯 Próxima Sessão - Sugestão

**Prioridade 1:** Painel Admin de Planos
- Criar tabela de planos
- Modal de criação
- Modal de edição
- Implementar deleção com confirmação

**Arquivos a criar:**
1. `web/frontend/src/app/admin/plans/page.tsx`
2. `web/frontend/src/components/admin/PlanForm.tsx`
3. `web/frontend/src/components/admin/PlansTable.tsx`

**Componentes necessários:**
```bash
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add form
```

---

**📌 Mantenha este arquivo atualizado conforme avança!**
