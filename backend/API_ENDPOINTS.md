# 📡 API Endpoints Reference

Referência completa de todos os endpoints da API.

**Base URL:** `http://localhost:8000`

---

## 🏥 Sistema

### Health Check
Verifica se a API está funcionando.

```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "service": "WhatsApp Business SaaS API",
  "version": "1.0.0"
}
```

### Root
Informações básicas da API.

```http
GET /
```

**Resposta:**
```json
{
  "message": "WhatsApp Business SaaS API",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 🔐 Autenticação

Base path: `/api/auth`

### Registrar Usuário
Cria nova conta de usuário.

```http
POST /api/auth/register
Content-Type: application/json
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "senha12345",
  "name": "Nome Completo",
  "phone": "+5511999999999"
}
```

**Resposta (201):**
```json
{
  "_id": "6534abc...",
  "email": "user@example.com",
  "name": "Nome Completo",
  "phone": "+5511999999999",
  "role": "user",
  "is_active": true,
  "email_verified": false,
  "subscription_status": "free",
  "created_at": "2025-10-18T16:30:00.000Z",
  "last_login": null
}
```

### Login
Autentica usuário e retorna tokens.

```http
POST /api/auth/login
Content-Type: application/json
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "senha12345"
}
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "_id": "6534abc...",
    "email": "user@example.com",
    "name": "Nome Completo",
    "role": "user",
    ...
  }
}
```

### Logout
Encerra sessão atual.

```http
POST /api/auth/logout
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

### Refresh Token
Renova access token usando refresh token.

```http
POST /api/auth/refresh
Content-Type: application/json
```

**Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {...}
}
```

### Obter Usuário Atual
Retorna informações do usuário autenticado.

```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "_id": "6534abc...",
  "email": "user@example.com",
  "name": "Nome Completo",
  "phone": "+5511999999999",
  "role": "user",
  "is_active": true,
  "email_verified": false,
  "current_plan_id": null,
  "subscription_status": "free",
  "created_at": "2025-10-18T16:30:00.000Z",
  "last_login": "2025-10-18T17:00:00.000Z"
}
```

### Listar Sessões
Lista todas as sessões ativas do usuário.

```http
GET /api/auth/sessions
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "sessions": [
    {
      "_id": "6534def...",
      "user_id": "6534abc...",
      "device_fingerprint": "abc123...",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "is_active": true,
      "last_activity": "2025-10-18T17:00:00.000Z",
      "login_at": "2025-10-18T16:00:00.000Z",
      "is_desktop": false
    }
  ],
  "count": 1
}
```

### Encerrar Sessão Específica
Encerra uma sessão pelo ID.

```http
DELETE /api/auth/sessions/{session_id}
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "message": "Sessão encerrada com sucesso"
}
```

---

## 🎛️ Admin - Gerenciamento de Planos

Base path: `/api/admin/plans`
**⚠️ Requer role: `admin` ou `super_admin`**

### Criar Plano
Cria novo plano de assinatura.

```http
POST /api/admin/plans/
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:**
```json
{
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
}
```

**Resposta (201):**
```json
{
  "_id": "6534xyz...",
  "name": "Pro",
  "slug": "pro",
  "description": "Plano profissional para empresas",
  "price_monthly": 9900,
  "price_yearly": 99000,
  "features": {...},
  "status": "active",
  "is_visible": true,
  "is_featured": true,
  "trial_days": 7,
  "setup_fee": 0,
  "available_gateways": ["mercadopago", "stripe", "paypal"],
  "created_at": "2025-10-18T17:00:00.000Z",
  "updated_at": "2025-10-18T17:00:00.000Z"
}
```

### Listar Planos
Lista todos os planos.

```http
GET /api/admin/plans/?include_inactive=false&include_deleted=false
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `include_inactive` (boolean): Incluir planos inativos (default: false)
- `include_deleted` (boolean): Incluir planos deletados (default: false, apenas admin)

**Resposta (200):**
```json
[
  {
    "_id": "6534xyz...",
    "name": "Pro",
    "slug": "pro",
    "description": "Plano profissional",
    "price_monthly": 9900,
    "price_yearly": 99000,
    ...
  },
  ...
]
```

### Buscar Plano por ID
Obtém detalhes de um plano específico.

```http
GET /api/admin/plans/{plan_id}
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "_id": "6534xyz...",
  "name": "Pro",
  "slug": "pro",
  ...
}
```

### Atualizar Plano
Atualiza informações de um plano.

```http
PUT /api/admin/plans/{plan_id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body (campos opcionais):**
```json
{
  "name": "Pro Plus",
  "description": "Plano Pro - Agora com mais recursos!",
  "price_monthly": 12900,
  "features": {
    "max_contacts": 10000,
    ...
  }
}
```

**Resposta (200):**
```json
{
  "_id": "6534xyz...",
  "name": "Pro Plus",
  "description": "Plano Pro - Agora com mais recursos!",
  "price_monthly": 12900,
  ...
}
```

### Ativar/Desativar Plano
Alterna status do plano entre ativo e inativo.

```http
POST /api/admin/plans/{plan_id}/toggle-status
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "success": true,
  "new_status": "inactive",
  "message": "Plano inactive"
}
```

### Deletar Plano (Soft Delete)
Marca plano como deletado (não remove do banco).

```http
DELETE /api/admin/plans/{plan_id}?reason=Motivo%20da%20exclusão
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `reason` (string): Motivo da exclusão

**Resposta (200):**
```json
{
  "success": true,
  "message": "Plano arquivado com sucesso"
}
```

**Erro (400) - Se houver assinaturas ativas:**
```json
{
  "detail": "Não é possível excluir. 5 assinatura(s) ativa(s) usam este plano."
}
```

### Listar Planos Deletados
Lista todos os planos que foram deletados (soft delete).

```http
GET /api/admin/plans/deleted/list
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
[
  {
    "_id": "6534xyz...",
    "name": "Plano Antigo",
    "flag_del": true,
    "deleted_at": "2025-10-17T10:00:00.000Z",
    "deleted_by": "6534abc...",
    "deleted_reason": "Plano descontinuado",
    ...
  }
]
```

### Restaurar Plano Deletado
Restaura um plano que foi deletado.

```http
POST /api/admin/plans/deleted/{plan_id}/restore
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Plano restaurado com sucesso"
}
```

### Estatísticas de Planos
Retorna estatísticas sobre planos e assinaturas.

```http
GET /api/admin/plans/stats/summary
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "total_active": 5,
  "total_inactive": 2,
  "total_deleted": 1,
  "popular_plans": [
    {
      "_id": "6534xyz...",
      "name": "Pro",
      "slug": "pro",
      "subscribers_count": 150
    },
    ...
  ]
}
```

---

## 📊 Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| **200** | OK - Requisição bem-sucedida |
| **201** | Created - Recurso criado com sucesso |
| **400** | Bad Request - Dados inválidos |
| **401** | Unauthorized - Não autenticado ou token inválido |
| **403** | Forbidden - Sem permissão para acessar recurso |
| **404** | Not Found - Recurso não encontrado |
| **500** | Internal Server Error - Erro no servidor |

---

## 🔒 Autenticação

### Header de Autorização

Todos os endpoints protegidos requerem o header:

```
Authorization: Bearer {access_token}
```

### Expiração de Tokens

- **Access Token**: 15 minutos
- **Refresh Token**: 30 dias

Use `/api/auth/refresh` para renovar o access token.

---

## 🚨 Tratamento de Erros

### Formato de Erro Padrão

```json
{
  "detail": "Mensagem de erro descritiva"
}
```

### Exemplos de Erros Comuns

**Token inválido ou expirado:**
```json
{
  "detail": "Token inválido ou expirado"
}
```

**Sem permissão (não é admin):**
```json
{
  "detail": "Acesso negado. Apenas administradores."
}
```

**Email já cadastrado:**
```json
{
  "detail": "Email já cadastrado"
}
```

**Senha muito curta:**
```json
{
  "detail": "Senha deve ter no mínimo 8 caracteres"
}
```

---

## 📝 Notas Importantes

### Soft Delete
- Todos os endpoints de "delete" fazem **soft delete**
- Os dados NÃO são removidos fisicamente do banco
- Use endpoints de "restore" para recuperar dados deletados
- Apenas admins podem ver dados deletados

### Roles de Usuário
- `user`: Usuário comum
- `admin`: Administrador (acesso ao painel admin)
- `super_admin`: Super administrador (acesso total)

### Planos Configuráveis
- Planos NÃO são fixos no código
- Admin cria/edita/ativa/desativa planos via API
- Validação automática: não permite deletar planos com assinaturas ativas

---

## 🔗 Links Úteis

- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

**📡 API Endpoints completamente documentados!**
