# 🚀 Quick Start - Sistema de Pagamentos

**Guia rápido para começar a usar o sistema de pagamentos**

---

## ⚡ Setup Rápido (5 minutos)

### 1. Configurar Variáveis de Ambiente

```bash
cd backend
cp .env.example .env
```

Edite o arquivo `.env` e configure:

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business

# JWT
SECRET_KEY=seu-secret-key-aqui-mude-em-producao
ALGORITHM=HS256

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000

# Mercado Pago (Sandbox)
MERCADOPAGO_ACCESS_TOKEN=TEST-seu-token-aqui

# Stripe (Test Mode)
STRIPE_SECRET_KEY=sk_test_seu-token-aqui
STRIPE_WEBHOOK_SECRET=whsec_seu-secret-aqui

# PayPal (Sandbox)
PAYPAL_CLIENT_ID=seu-client-id-aqui
PAYPAL_CLIENT_SECRET=seu-client-secret-aqui
PAYPAL_MODE=sandbox
```

### 2. Iniciar MongoDB

```bash
# Linux/Mac
sudo systemctl start mongod

# Ou usando Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### 3. Iniciar Backend

```bash
cd backend
source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
python main.py
```

Backend rodando em: **http://localhost:8000**

### 4. Iniciar Frontend

```bash
cd web/frontend
npm run dev
```

Frontend rodando em: **http://localhost:3000**

---

## 📝 Como Obter Credenciais de Teste

### Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Faça login ou crie conta
3. Vá em "Credenciais" → "Credenciais de teste"
4. Copie o **Access Token** de teste
5. Cole em `MERCADOPAGO_ACCESS_TOKEN`

### Stripe

1. Acesse: https://dashboard.stripe.com/register
2. Crie uma conta (não precisa verificar)
3. Ative o "Modo de teste" (toggle no canto superior direito)
4. Vá em "Developers" → "API keys"
5. Copie a **Secret key** (sk_test_...)
6. Cole em `STRIPE_SECRET_KEY`
7. Para webhook:
   - Vá em "Developers" → "Webhooks"
   - Clique "Add endpoint"
   - URL: `http://localhost:8000/api/payments/stripe/webhook`
   - Eventos: `checkout.session.completed`, `payment_intent.succeeded`
   - Copie o **Webhook secret** (whsec_...)

### PayPal

1. Acesse: https://developer.paypal.com/
2. Faça login ou crie conta
3. Vá em "Dashboard" → "My Apps & Credentials"
4. Em "Sandbox", clique "Create App"
5. Copie **Client ID** e **Secret**
6. Cole em `PAYPAL_CLIENT_ID` e `PAYPAL_CLIENT_SECRET`

---

## 🧪 Testar o Sistema

### 1. Criar um Plano

```bash
# Via Swagger: http://localhost:8000/docs
# POST /api/admin/plans/

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

### 2. Criar um Usuário

```bash
# POST /api/auth/register
{
  "email": "teste@teste.com",
  "password": "senha123",
  "name": "Usuário Teste"
}
```

### 3. Fazer Login

```bash
# POST /api/auth/login
{
  "email": "teste@teste.com",
  "password": "senha123"
}
```

Copie o `access_token` retornado.

### 4. Testar Fluxo de Pagamento

#### Opção A - Via Interface (Recomendado)

1. Acesse: http://localhost:3000/pricing
2. Clique em "Assinar" em qualquer plano
3. Escolha gateway (Mercado Pago, Stripe ou PayPal)
4. Escolha método de pagamento
5. Complete o pagamento

**Dados de teste Stripe:**
- Cartão: `4242 4242 4242 4242`
- CVV: `123`
- Data: `12/34`
- CEP: `12345`

#### Opção B - Via API (Swagger)

```bash
# POST /api/payments/stripe/create-checkout-session
{
  "plan_id": "id-do-plano-criado",
  "payment_method": "credit_card",
  "gateway": "stripe"
}
```

### 5. Verificar Pagamento

```bash
# GET /api/payments/my-payments
# Retorna lista de pagamentos do usuário

# GET /api/payments/my-subscription
# Retorna assinatura ativa
```

---

## 📊 Acessar Interfaces

### Swagger (API Docs)
http://localhost:8000/docs

### Frontend
- Homepage: http://localhost:3000
- Pricing: http://localhost:3000/pricing
- Checkout: http://localhost:3000/checkout?plan_id=XXX
- Histórico: http://localhost:3000/payments
- Assinatura: http://localhost:3000/subscription

### Admin Dashboard
http://localhost:3000/admin/dashboard

---

## 🔍 Verificar se Está Funcionando

### Backend

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar:
{
  "status": "healthy",
  "service": "WhatsApp Business SaaS API",
  "version": "1.0.0"
}
```

### Frontend

```bash
# Deve retornar HTML
curl http://localhost:3000 | head -5
```

### MongoDB

```bash
mongosh
use whatsapp_business
show collections
# Deve mostrar: payments, plans, subscriptions, users, sessions
```

---

## 🐛 Resolução de Problemas

### Backend não inicia

**Erro:** `ModuleNotFoundError: No module named 'fastapi'`

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### MongoDB não conecta

**Erro:** `ServerSelectionTimeoutError`

```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Iniciar se não estiver
sudo systemctl start mongod
```

### Frontend não carrega API

**Erro:** `Network Error` ou `CORS`

1. Verificar se backend está rodando: http://localhost:8000/health
2. Verificar `ALLOWED_ORIGINS` no `.env`
3. Verificar `NEXT_PUBLIC_API_URL` no frontend

### Pagamento não redireciona

**Problema:** Fica na tela de loading

1. Verificar console do navegador (F12)
2. Verificar logs do backend
3. Verificar se tokens estão corretos no `.env`
4. Testar endpoint direto no Swagger

### Webhook não chama

**Problema:** Pagamento não atualiza automaticamente

1. **Para desenvolvimento local**, usar ferramentas como:
   - Stripe CLI: `stripe listen --forward-to localhost:8000/api/payments/stripe/webhook`
   - ngrok: `ngrok http 8000`
   - localtunnel: `lt --port 8000`

2. Configurar webhook URL pública nas plataformas
3. Verificar logs do backend para ver se webhook foi chamado

---

## 📚 Documentação Completa

Para informações detalhadas, consulte:

- **SESSAO_FINAL_ATUALIZADA.md** - Resumo completo com todas as features
- **PAGAMENTOS_COMPLETO.md** - Guia detalhado de pagamentos
- **TESTE_SISTEMA_PAGAMENTOS.md** - Plano de testes completo
- **PAGAMENTOS_BACKEND_RESUMO.md** - Documentação técnica do backend

---

## 🎯 Checklist Rápido

- [ ] MongoDB rodando
- [ ] Backend rodando (http://localhost:8000/health)
- [ ] Frontend rodando (http://localhost:3000)
- [ ] Arquivo `.env` configurado
- [ ] Pelo menos um plano criado
- [ ] Usuário de teste criado
- [ ] Credenciais de sandbox obtidas
- [ ] Primeiro pagamento de teste realizado

---

## 💡 Dicas

1. **Use Swagger para testes rápidos:** http://localhost:8000/docs
2. **Modo de teste:** Sempre use credenciais de sandbox/test
3. **Logs:** Backend mostra logs detalhados no terminal
4. **MongoDB Compass:** Interface visual para ver dados
5. **Redux DevTools:** Para debug do estado do frontend

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs do backend
2. Abra o console do navegador (F12)
3. Consulte a documentação da plataforma de pagamento
4. Leia os documentos MD na raiz do projeto

---

**Sistema pronto para uso em modo de desenvolvimento!** 🎉

Para **produção**, lembre-se de:
- Usar credenciais de produção
- Configurar HTTPS
- Configurar webhooks públicos
- Adicionar rate limiting
- Configurar monitoramento (Sentry)
- Fazer backup do MongoDB

**Última atualização:** 19/10/2025 - 22:45
