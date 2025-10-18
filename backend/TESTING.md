# 🧪 Guia de Testes - Backend API

Este guia mostra como testar a API backend do WhatsApp Business SaaS.

## 📋 Pré-requisitos

1. MongoDB rodando em `mongodb://localhost:27017`
2. Backend iniciado: `python main.py` ou `uvicorn main:app --reload`
3. API rodando em: http://localhost:8000

## 🚀 Testando Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "WhatsApp Business SaaS API",
  "version": "1.0.0"
}
```

---

## 🔐 Autenticação

### 1. Registrar Novo Usuário

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha12345",
    "name": "João Silva",
    "phone": "+5511999999999"
  }'
```

**Resposta esperada:**
```json
{
  "_id": "6534abc123def...",
  "email": "teste@example.com",
  "name": "João Silva",
  "phone": "+5511999999999",
  "role": "user",
  "is_active": true,
  "email_verified": false,
  "subscription_status": "free",
  "created_at": "2025-10-18T16:30:00.000Z",
  "last_login": null
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha12345"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "_id": "6534abc123def...",
    "email": "teste@example.com",
    "name": "João Silva",
    ...
  }
}
```

**⚠️ Salve o `access_token` para usar nos próximos testes!**

### 3. Buscar Informações do Usuário Logado

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 4. Listar Sessões Ativas

```bash
curl -X GET http://localhost:8000/api/auth/sessions \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 5. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 6. Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "SEU_REFRESH_TOKEN_AQUI"
  }'
```

---

## 🎛️ Gerenciamento de Planos (Admin)

**⚠️ IMPORTANTE:** Primeiro, você precisa tornar seu usuário admin no MongoDB:

```javascript
// No MongoDB shell
db.users.updateOne(
  { email: "teste@example.com" },
  { $set: { role: "admin" } }
)
```

### 1. Criar Novo Plano

```bash
curl -X POST http://localhost:8000/api/admin/plans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI" \
  -d '{
    "name": "Pro",
    "slug": "pro",
    "description": "Plano profissional para empresas",
    "price_monthly": 9900,
    "price_yearly": 99000,
    "features": {
      "max_contacts": 5000,
      "max_messages_per_month": -1,
      "max_devices": 3,
      "has_variables": true,
      "has_sequence": true,
      "has_media": true,
      "has_advanced_reports": true,
      "has_api_access": false,
      "has_multi_user": false,
      "support_level": "email_chat"
    },
    "status": "active",
    "is_visible": true,
    "is_featured": true,
    "trial_days": 7,
    "setup_fee": 0,
    "available_gateways": ["mercadopago", "stripe", "paypal"]
  }'
```

### 2. Listar Todos os Planos

```bash
curl -X GET "http://localhost:8000/api/admin/plans/" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 3. Listar Apenas Planos Ativos

```bash
curl -X GET "http://localhost:8000/api/admin/plans/?include_inactive=false" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 4. Buscar Plano por ID

```bash
curl -X GET "http://localhost:8000/api/admin/plans/PLAN_ID_AQUI" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 5. Atualizar Plano

```bash
curl -X PUT "http://localhost:8000/api/admin/plans/PLAN_ID_AQUI" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI" \
  -d '{
    "price_monthly": 12900,
    "description": "Plano Pro - Agora com mais recursos!"
  }'
```

### 6. Ativar/Desativar Plano

```bash
curl -X POST "http://localhost:8000/api/admin/plans/PLAN_ID_AQUI/toggle-status" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 7. Deletar Plano (Soft Delete)

```bash
curl -X DELETE "http://localhost:8000/api/admin/plans/PLAN_ID_AQUI?reason=Plano%20descontinuado" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 8. Listar Planos Deletados

```bash
curl -X GET "http://localhost:8000/api/admin/plans/deleted/list" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 9. Restaurar Plano Deletado

```bash
curl -X POST "http://localhost:8000/api/admin/plans/deleted/PLAN_ID_AQUI/restore" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 10. Estatísticas de Planos

```bash
curl -X GET "http://localhost:8000/api/admin/plans/stats/summary" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

---

## 📊 Documentação Interativa

Acesse a documentação Swagger em seu navegador:

**http://localhost:8000/docs**

Lá você pode:
- Ver todos os endpoints disponíveis
- Testar diretamente pelo navegador
- Ver schemas de request/response
- Autorizar com seu token

---

## 🧪 Testando com Python

Crie um arquivo `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Registrar usuário
register_data = {
    "email": "teste@example.com",
    "password": "senha12345",
    "name": "João Silva",
    "phone": "+5511999999999"
}

response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
print("Register:", response.json())

# 2. Login
login_data = {
    "email": "teste@example.com",
    "password": "senha12345"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
tokens = response.json()
access_token = tokens["access_token"]
print("Login successful! Token:", access_token[:50] + "...")

# 3. Buscar info do usuário
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
print("User info:", response.json())

# 4. Criar plano (como admin)
plan_data = {
    "name": "Starter",
    "slug": "starter",
    "description": "Plano inicial",
    "price_monthly": 4900,
    "price_yearly": None,
    "features": {
        "max_contacts": 1000,
        "max_messages_per_month": 5000,
        "max_devices": 1,
        "has_variables": True,
        "has_sequence": False,
        "has_media": True,
        "has_advanced_reports": False,
        "has_api_access": False,
        "has_multi_user": False,
        "support_level": "email"
    },
    "status": "active",
    "is_visible": True,
    "is_featured": False,
    "trial_days": 0,
    "setup_fee": 0,
    "available_gateways": ["mercadopago"]
}

response = requests.post(f"{BASE_URL}/api/admin/plans/", json=plan_data, headers=headers)
print("Plan created:", response.json())

# 5. Listar planos
response = requests.get(f"{BASE_URL}/api/admin/plans/", headers=headers)
print("Plans:", response.json())
```

Execute:
```bash
python test_api.py
```

---

## 🔍 Verificando no MongoDB

```javascript
// Ver usuários
db.users.find().pretty()

// Ver planos
db.plans.find().pretty()

// Ver sessões
db.sessions.find().pretty()

// Ver logs de auditoria
db.audit_logs.find().sort({timestamp: -1}).limit(10).pretty()

// Ver apenas registros ativos (não deletados)
db.plans.find({flag_del: false}).pretty()

// Ver apenas registros deletados
db.plans.find({flag_del: true}).pretty()
```

---

## ✅ Checklist de Testes

- [ ] Health check retorna status healthy
- [ ] Registro de usuário funciona
- [ ] Login retorna tokens válidos
- [ ] Endpoint `/me` retorna dados do usuário
- [ ] Listar sessões funciona
- [ ] Logout invalida sessão
- [ ] Refresh token gera novos tokens
- [ ] Criar plano funciona (como admin)
- [ ] Listar planos retorna dados corretos
- [ ] Atualizar plano funciona
- [ ] Ativar/desativar plano funciona
- [ ] Soft delete não remove dados do MongoDB
- [ ] Restaurar plano deletado funciona
- [ ] Estatísticas de planos retornam dados corretos
- [ ] Documentação Swagger está acessível

---

## 🚨 Troubleshooting

### Erro: "MongoDB connection failed"
- Verifique se MongoDB está rodando: `sudo systemctl status mongod`
- Inicie MongoDB: `sudo systemctl start mongod`

### Erro: "Token inválido"
- Verifique se o token não expirou (15 minutos)
- Use refresh token para renovar

### Erro: "Acesso negado. Apenas administradores"
- Torne seu usuário admin no MongoDB:
  ```javascript
  db.users.updateOne({email: "seu@email.com"}, {$set: {role: "admin"}})
  ```

### Erro: "Email já cadastrado"
- Use outro email ou delete o usuário existente:
  ```javascript
  db.users.deleteOne({email: "teste@example.com"})
  ```

---

**🎉 Backend API está funcional e pronta para testes!**
