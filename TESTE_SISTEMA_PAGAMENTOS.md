# 🧪 TESTE DO SISTEMA DE PAGAMENTOS

**Data:** 19/10/2025
**Status:** ✅ Sistema implementado e pronto para testes

---

## 📋 CHECKLIST DE TESTES

### ✅ Backend - Estrutura
- [x] Models criados (`backend/app/models/payment.py`)
- [x] Rotas Mercado Pago (`backend/app/routes/payments/mercadopago.py`)
- [x] Rotas Stripe (`backend/app/routes/payments/stripe.py`)
- [x] Rotas PayPal (`backend/app/routes/payments/paypal.py`)
- [x] Rotas History (`backend/app/routes/payments/history.py`)
- [x] Rotas registradas no `main.py`
- [x] Collection de payments adicionada ao `database.py`

### ✅ Frontend - Estrutura
- [x] API Client atualizado (`src/lib/api.ts`)
- [x] Página de Checkout (`src/app/checkout/page.tsx`)
- [x] Página de Sucesso (`src/app/checkout/success/page.tsx`)
- [x] Página de Falha (`src/app/checkout/failed/page.tsx`)
- [x] Página de Assinatura (`src/app/subscription/page.tsx`)
- [x] Página de Histórico (`src/app/payments/page.tsx`)

### ✅ Dependências
- [x] Backend: fastapi, motor, stripe, mercadopago, paypal ✅
- [x] Frontend: recharts, date-fns ✅
- [x] Frontend: Mercado Pago SDK, Stripe SDK, PayPal SDK (NPM instalado)

### 🔧 Configuração
- [x] `.env` criado a partir do `.env.example`
- [ ] Variáveis de ambiente configuradas (precisa de tokens reais)
- [ ] MongoDB rodando
- [ ] Backend rodando
- [x] Frontend rodando ✅ (PID: 25145)

---

## 🧪 PLANO DE TESTES

### Fase 1: Testes Unitários (Backend)

#### 1.1 Teste de Importações
```bash
cd backend
source venv/bin/activate
python -c "from app.models.payment import PaymentSchema, PaymentGateway, PaymentStatus, PaymentMethod; print('✅ Models OK')"
python -c "from app.routes.payments import mercadopago, stripe, paypal, history; print('✅ Routes OK')"
```

#### 1.2 Teste de Inicialização do Server
```bash
cd backend
source venv/bin/activate
python main.py
# Verificar se inicia sem erros
# Verificar logs: "✅ Aplicação pronta!"
# Acessar: http://localhost:8000/docs
```

#### 1.3 Teste de Endpoints (Swagger)
- Acessar http://localhost:8000/docs
- Verificar se aparecem todos os endpoints:
  - **Mercado Pago**: 3 endpoints
  - **Stripe**: 5 endpoints
  - **PayPal**: 4 endpoints
  - **History**: 4 endpoints
  - **Total**: 16 endpoints de pagamento

### Fase 2: Testes de Integração (Backend + MongoDB)

#### 2.1 Setup MongoDB
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Se não estiver, iniciar
sudo systemctl start mongod

# Criar banco de dados de teste
mongosh
use whatsapp_business
db.createCollection("payments")
db.createCollection("subscriptions")
db.createCollection("plans")
```

#### 2.2 Criar Plano de Teste
```bash
# Via Swagger: POST /api/admin/plans/
{
  "name": "Plano Teste",
  "description": "Para testes de pagamento",
  "price_monthly": 50.00,
  "price_yearly": 500.00,
  "is_active": true,
  "features": {
    "max_contacts": 1000,
    "max_messages_per_month": 5000,
    "max_devices": 1,
    "gmaps_scraping": true,
    "mass_messaging": true,
    "scheduling": true
  }
}
```

#### 2.3 Criar Usuário de Teste
```bash
# Via Swagger: POST /api/auth/register
{
  "email": "teste@teste.com",
  "password": "senha123",
  "name": "Usuário Teste"
}

# Fazer login e pegar token JWT
# POST /api/auth/login
{
  "email": "teste@teste.com",
  "password": "senha123"
}

# Copiar access_token para usar nos próximos testes
```

### Fase 3: Testes de Pagamento (Frontend + Backend)

#### 3.1 Fluxo Completo - Mercado Pago (PIX)

**Pré-requisitos:**
- Token de teste do Mercado Pago em `.env`
- Backend rodando
- Frontend rodando

**Passos:**
1. Acessar http://localhost:3000/pricing
2. Clicar em "Assinar" em qualquer plano
3. Selecionar "Mercado Pago"
4. Selecionar "PIX"
5. Clicar em "Continuar para Pagamento"
6. Verificar se:
   - [ ] Redireciona para página do Mercado Pago
   - [ ] QR Code PIX é exibido
   - [ ] Código PIX pode ser copiado
   - [ ] Timer de 30 minutos aparece
7. Simular pagamento no sandbox do Mercado Pago
8. Verificar se webhook é chamado
9. Verificar se redireciona para `/checkout/success`
10. Verificar se assinatura foi ativada no MongoDB

**MongoDB - Verificar:**
```javascript
db.payments.findOne({gateway: "mercadopago"})
// Verificar status: "approved"
// Verificar paid_at: <data>

db.subscriptions.findOne({user_id: "..."})
// Verificar status: "active"
```

#### 3.2 Fluxo Completo - Stripe (Card)

**Pré-requisitos:**
- Token de teste do Stripe em `.env`
- Webhook secret do Stripe em `.env`

**Passos:**
1. Acessar http://localhost:3000/pricing
2. Clicar em "Assinar" em qualquer plano
3. Selecionar "Stripe"
4. Selecionar "Cartão de Crédito"
5. Clicar em "Continuar para Pagamento"
6. Verificar se:
   - [ ] Redireciona para Stripe Checkout
   - [ ] Checkout aparece corretamente
7. Usar cartão de teste: `4242 4242 4242 4242`
8. CVV: `123`, Data: `12/34`
9. Completar pagamento
10. Verificar webhook
11. Verificar redirecionamento para `/checkout/success`

#### 3.3 Fluxo Completo - PayPal

**Pré-requisitos:**
- Conta sandbox do PayPal
- Client ID e Secret em `.env`

**Passos:**
1. Acessar http://localhost:3000/pricing
2. Clicar em "Assinar"
3. Selecionar "PayPal"
4. Clicar em "Continuar para Pagamento"
5. Fazer login com conta sandbox
6. Aprovar pagamento
7. Verificar capture do order
8. Verificar redirecionamento

### Fase 4: Testes de UI (Frontend)

#### 4.1 Página de Checkout (`/checkout`)
- [ ] Resumo do plano aparece (esquerda)
- [ ] 3 cards de gateway aparecem
- [ ] Seleção de gateway funciona
- [ ] Métodos de pagamento aparecem por gateway:
  - Mercado Pago: PIX, Boleto, Cartão
  - Stripe: Cartão (Apple Pay e Google Pay automáticos)
  - PayPal: PayPal
- [ ] Botão "Continuar" desabilitado se nada selecionado
- [ ] Loading state ao processar
- [ ] Erro mostrado se falhar
- [ ] Responsivo (mobile + desktop)

#### 4.2 Página de Sucesso (`/checkout/success`)
- [ ] Confetti animation aparece
- [ ] Ícone de sucesso animado
- [ ] Detalhes da assinatura corretos
- [ ] Data de próxima cobrança
- [ ] Próximos passos mostrados
- [ ] Botão "Ir para Dashboard" funciona
- [ ] Botão "Ver Perfil" funciona

#### 4.3 Página de Falha (`/checkout/failed`)
- [ ] Motivo do erro mostrado
- [ ] 4 cards de problemas comuns aparecem
- [ ] Sugestões de solução claras
- [ ] Métodos alternativos sugeridos
- [ ] Botão "Tentar Novamente" funciona

#### 4.4 Página de Assinatura (`/subscription`)
- [ ] Status da assinatura correto
- [ ] Badge "Ativa" ou "Inativa"
- [ ] Valor mensal correto
- [ ] Próxima cobrança formatada
- [ ] Recursos inclusos listados
- [ ] Último pagamento mostrado
- [ ] Botão "Cancelar" abre modal
- [ ] Modal pede motivo (opcional)
- [ ] Cancelamento funciona (Stripe)
- [ ] Toast de sucesso aparece
- [ ] Aviso amarelo se "cancel_at_period_end"

#### 4.5 Página de Histórico (`/payments`)
- [ ] 4 cards de estatísticas corretos:
  - Total de Pagamentos
  - Aprovados
  - Pendentes
  - Total Gasto
- [ ] Filtro de status funciona
- [ ] Filtro de gateway funciona
- [ ] Tabela mostra pagamentos
- [ ] Datas formatadas (pt-BR)
- [ ] Status badges coloridos
- [ ] Botão "Ver Detalhes" abre modal
- [ ] Modal mostra:
  - Status
  - Valor
  - Plano
  - Método e Gateway
  - Datas (criação e pagamento)
  - PIX QR Code (se aplicável) + botão copiar
  - Boleto URL (se aplicável)
  - Cartão últimos 4 dígitos (se aplicável)
  - ID da transação
- [ ] Empty state se sem pagamentos
- [ ] Botão "Atualizar" funciona

### Fase 5: Testes de Segurança

#### 5.1 Autenticação
- [ ] Endpoints protegidos exigem JWT
- [ ] Token expirado retorna 401
- [ ] Refresh token funciona
- [ ] User só vê próprios pagamentos
- [ ] User só vê própria assinatura

#### 5.2 Validação
- [ ] Pydantic valida requests
- [ ] Enums rejeitam valores inválidos
- [ ] Plan_id válido obrigatório
- [ ] Gateway válido obrigatório
- [ ] Payment_method válido obrigatório

#### 5.3 Webhooks
- [ ] Stripe webhook valida assinatura
- [ ] Mercado Pago valida origem
- [ ] PayPal valida evento
- [ ] Webhooks não autorizados rejeitados

### Fase 6: Testes de Performance

#### 6.1 Carga
- [ ] 10 usuários simultâneos
- [ ] 50 pagamentos em histórico carregam rápido
- [ ] Filtros não causam lag
- [ ] Modal abre sem delay

#### 6.2 Otimização
- [ ] Planos carregados uma vez (mapeados)
- [ ] Queries eficientes (sem N+1)
- [ ] Agregações MongoDB performáticas

---

## 🐛 BUGS CONHECIDOS

### Backend
- [ ] Nenhum reportado ainda

### Frontend
- [ ] Nenhum reportado ainda

---

## 📊 RESULTADO DOS TESTES

### Status Geral
- **Backend**: ⏳ Aguardando testes
- **Frontend**: ⏳ Aguardando testes
- **Integração**: ⏳ Aguardando testes

### Cobertura
- **Endpoints**: 0/16 testados
- **Páginas**: 0/5 testadas
- **Fluxos**: 0/3 testados

---

## 🚀 PRÓXIMOS PASSOS APÓS TESTES

1. **Se tudo passar:**
   - Criar documentação de API
   - Criar guia de teste para QA
   - Preparar para deploy

2. **Se houver bugs:**
   - Documentar bugs encontrados
   - Priorizar correções
   - Refazer testes após correções

3. **Melhorias identificadas:**
   - Rate limiting nos webhooks
   - Retry logic para falhas
   - Cache de planos (Redis)
   - Logs estruturados

---

**Última atualização:** 19/10/2025 - 22:00
