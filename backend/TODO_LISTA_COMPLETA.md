# 📋 Lista Completa de Tarefas Pendentes - Backend

**Status Geral do Projeto**: ~70% completo
**Última Atualização**: 19/10/2025

---

## 🚨 FASE 1: CRÍTICO (Fazer ANTES de Produção)

### 1.1 Correções Urgentes (5 minutos - 2 horas)

- [ ] **CRÍTICO**: Adicionar alias `require_admin` em `app/middleware/auth.py`
  - **Problema**: Usado em 13+ endpoints mas não existe
  - **Tempo**: 5 minutos
  - **Código**: `require_admin = Depends(get_current_admin_user)`

- [ ] **CRÍTICO**: Implementar Rate Limiting Middleware
  - **Local**: `app/middleware/rate_limit.py` (não existe)
  - **Tempo**: 2-3 horas
  - **Prioridade**: ALTA
  - **Sem isso**: API vulnerável a abuso/ataques

### 1.2 Autenticação e Segurança (6-10 horas)

- [ ] Implementar Password Reset Flow (2-3 horas)
  - `POST /api/auth/password-reset/request`
  - `POST /api/auth/password-reset/confirm`
  - Envio de email com token
  - Validação de token

- [ ] Implementar Email Verification (2-3 horas)
  - `POST /api/auth/email/send-verification`
  - `GET /api/auth/email/verify/{token}`
  - `POST /api/auth/email/resend-verification`

- [ ] Implementar 2FA - Two Factor Authentication (4-6 horas)
  - `POST /api/auth/2fa/setup`
  - `POST /api/auth/2fa/verify`
  - `POST /api/auth/2fa/disable`
  - `GET /api/auth/2fa/backup-codes`

### 1.3 WhatsApp Routes - FUNCIONALIDADE PRINCIPAL (2-3 semanas)

**Arquivo**: `app/routes/whatsapp/` (atualmente vazio)

- [ ] **Mensagens**
  - `POST /api/whatsapp/messages/send` - Enviar mensagem
  - `POST /api/whatsapp/messages/send-bulk` - Envio em massa
  - `GET /api/whatsapp/messages` - Listar mensagens
  - `GET /api/whatsapp/messages/{id}` - Detalhes mensagem

- [ ] **Sessão/Conexão**
  - `POST /api/whatsapp/session/start` - Iniciar sessão
  - `GET /api/whatsapp/session/qr` - Obter QR code
  - `GET /api/whatsapp/session/status` - Status da conexão
  - `DELETE /api/whatsapp/session/logout` - Desconectar

- [ ] **Contatos**
  - `GET /api/whatsapp/contacts` - Listar contatos
  - `POST /api/whatsapp/contacts` - Adicionar contato
  - `PUT /api/whatsapp/contacts/{id}` - Atualizar contato
  - `DELETE /api/whatsapp/contacts/{id}` - Remover contato
  - `POST /api/whatsapp/contacts/import` - Importar CSV

- [ ] **Campanhas**
  - `POST /api/whatsapp/campaigns` - Criar campanha
  - `GET /api/whatsapp/campaigns` - Listar campanhas
  - `GET /api/whatsapp/campaigns/{id}` - Detalhes campanha
  - `POST /api/whatsapp/campaigns/{id}/start` - Iniciar
  - `POST /api/whatsapp/campaigns/{id}/pause` - Pausar
  - `DELETE /api/whatsapp/campaigns/{id}` - Cancelar

- [ ] **Mídia**
  - `POST /api/whatsapp/media/upload` - Upload de arquivo
  - `GET /api/whatsapp/media/{id}` - Download de arquivo

### 1.4 Testes Automatizados (1-2 semanas)

**Diretório**: `backend/tests/` (não existe)

- [ ] **Estrutura Básica**
  - `tests/__init__.py`
  - `tests/conftest.py` - Fixtures pytest
  - `tests/test_auth.py` - Testes de autenticação
  - `tests/test_payments.py` - Testes de pagamento
  - `tests/test_subscriptions.py` - Ciclo de vida assinatura

- [ ] **Testes Unitários**
  - `tests/unit/test_security.py`
  - `tests/unit/test_soft_delete.py`
  - `tests/unit/test_audit.py`

- [ ] **Testes de Integração**
  - `tests/integration/test_payment_gateways.py`
  - `tests/integration/test_email_service.py`
  - `tests/integration/test_database.py`

- [ ] **Testes E2E**
  - `tests/e2e/test_payment_flow.py`
  - `tests/e2e/test_auth_flow.py`

---

## ⚡ FASE 2: ALTA PRIORIDADE (Funcionalidades Importantes)

### 2.1 Administração (1-2 semanas)

- [ ] **Gerenciamento de Usuários Admin**
  - Arquivo: `app/routes/admin/users.py` (não existe)
  - `GET /api/admin/users` - Listar usuários
  - `GET /api/admin/users/{id}` - Detalhes usuário
  - `POST /api/admin/users/{id}/suspend` - Suspender
  - `POST /api/admin/users/{id}/activate` - Ativar
  - `POST /api/admin/users/{id}/ban` - Banir
  - `DELETE /api/admin/users/{id}` - Deletar

- [ ] **Gerenciamento de Assinaturas Admin**
  - Arquivo: `app/routes/admin/subscriptions.py` (não existe)
  - `GET /api/admin/subscriptions` - Listar todas
  - `POST /api/admin/subscriptions` - Criar manual
  - `PUT /api/admin/subscriptions/{id}` - Editar
  - `POST /api/admin/subscriptions/{id}/extend` - Estender
  - `POST /api/admin/subscriptions/{id}/cancel` - Cancelar

### 2.2 Pagamentos - Funcionalidades Faltantes (1 semana)

- [ ] **Stripe - Complementar**
  - `GET /api/payments/stripe/invoices` - Histórico faturas
  - `POST /api/payments/stripe/refund` - Processar reembolso
  - `GET /api/payments/stripe/retry` - Tentar novamente

- [ ] **Mercado Pago - Complementar**
  - `POST /api/payments/mercadopago/refund` - Reembolso
  - `GET /api/payments/mercadopago/installments` - Parcelas

- [ ] **PayPal - Complementar**
  - `POST /api/payments/paypal/refund` - Reembolso
  - `POST /api/payments/paypal/subscription/create` - Recorrência
  - `GET /api/payments/paypal/disputes` - Disputas

### 2.3 Email Service - Completar (4-6 horas)

**Arquivo**: `app/core/email.py` (40% completo)

- [ ] Implementar funções faltantes:
  - `send_payment_failure_email()` - Falha no pagamento
  - `send_password_reset_email()` - Reset de senha
  - `send_email_verification_email()` - Verificação email
  - `send_2fa_code_email()` - Código 2FA

- [ ] Adicionar recursos:
  - Sistema de templates (Jinja2)
  - Retry logic para falhas
  - Fila de emails (Celery/Redis)
  - Unsubscribe management

### 2.4 Desktop Routes (1 semana)

**Arquivo**: `app/routes/desktop/` (vazio)

- [ ] **Ativação e Registro**
  - `POST /api/desktop/register` - Registrar app
  - `POST /api/desktop/activate` - Ativar com chave
  - `GET /api/desktop/verify` - Verificar ativação

- [ ] **Atualizações**
  - `GET /api/desktop/updates/check` - Verificar updates
  - `GET /api/desktop/updates/download` - Download update
  - `POST /api/desktop/updates/log` - Log de instalação

- [ ] **Configurações**
  - `GET /api/desktop/settings` - Obter configs
  - `PUT /api/desktop/settings` - Salvar configs

---

## 📝 FASE 3: MÉDIA PRIORIDADE (Melhorias)

### 3.1 OAuth Integration (3-5 dias)

- [ ] Google OAuth
  - `GET /api/auth/oauth/google` - Iniciar flow
  - `GET /api/auth/oauth/google/callback` - Callback

- [ ] GitHub OAuth
  - `GET /api/auth/oauth/github`
  - `GET /api/auth/oauth/github/callback`

- [ ] LinkedIn OAuth
  - `GET /api/auth/oauth/linkedin`
  - `GET /api/auth/oauth/linkedin/callback`

### 3.2 Perfil de Usuário - Complementar (2-3 dias)

**Arquivo**: `app/routes/users/profile.py` (50% completo)

- [ ] Avatar/Foto
  - `POST /api/profile/avatar` - Upload avatar
  - `DELETE /api/profile/avatar` - Remover avatar

- [ ] Segurança
  - `GET /api/profile/sessions` - Sessões ativas
  - `DELETE /api/profile/sessions/{id}` - Revogar sessão
  - `GET /api/profile/security-log` - Log de segurança

### 3.3 Models Faltantes (1-2 dias)

- [ ] `app/models/campaign.py` - Campanhas WhatsApp
- [ ] `app/models/contact.py` - Contatos
- [ ] `app/models/template.py` - Templates mensagens
- [ ] `app/models/audit_log.py` - Logs de auditoria
- [ ] `app/models/security_log.py` - Logs segurança
- [ ] `app/models/admin.py` - Admin/Staff específico

### 3.4 Jobs - Complementar (2-3 dias)

- [ ] Retry logic para renovações falhadas
- [ ] Grace period handling
- [ ] Chargeback processing job
- [ ] Refund processing job
- [ ] Email queue processing job

### 3.5 Segurança Adicional (3-5 dias)

- [ ] CSRF Protection
- [ ] API Key Management
  - `POST /api/profile/api-keys` - Gerar chave
  - `GET /api/profile/api-keys` - Listar chaves
  - `DELETE /api/profile/api-keys/{id}` - Revogar

- [ ] IP Whitelisting (schema existe)
  - `POST /api/admin/ip-whitelist` - Adicionar IP
  - `GET /api/admin/ip-whitelist` - Listar IPs
  - `DELETE /api/admin/ip-whitelist/{id}` - Remover

---

## 🎨 FASE 4: BAIXA PRIORIDADE (Polish & Nice-to-Have)

### 4.1 Documentação (1 semana)

- [ ] Swagger/OpenAPI completo
- [ ] Guia de Setup
- [ ] Variáveis de ambiente documentadas
- [ ] Schema do banco documentado
- [ ] Fluxogramas de pagamento
- [ ] Arquitetura documentada
- [ ] Deployment guide
- [ ] Testing guide

### 4.2 Infraestrutura (3-5 dias)

- [ ] Docker Compose production
- [ ] CI/CD Pipeline (GitHub Actions)
- [ ] Database migrations system
- [ ] Seed data scripts
- [ ] Health checks avançados

### 4.3 Monitoramento (2-3 dias)

- [ ] Integração Sentry (error tracking)
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Log aggregation (ELK/Loki)
- [ ] Performance monitoring (New Relic/DataDog)

### 4.4 Admin Dashboard - Avançado (1 semana)

- [ ] Sistema de tickets/suporte
- [ ] Busca avançada de usuários
- [ ] Analytics por plano
- [ ] Chargeback management
- [ ] Bulk operations
- [ ] Relatórios exportáveis (CSV/PDF)

### 4.5 Notificações Avançadas (3-5 dias)

- [ ] SMS notifications (Twilio)
- [ ] Push notifications (Firebase)
- [ ] In-app notifications
- [ ] Notification preferences
- [ ] Unsubscribe management

---

## 🐛 BUGS CONHECIDOS & CORREÇÕES

### Bugs Críticos

- [ ] **Stripe Customer Creation**
  - **Local**: `app/routes/payments/stripe.py:69-70`
  - **Problema**: `pass` em vez de criar customer
  - **Severidade**: MÉDIA
  - **Tempo**: 15 minutos

- [ ] **Admin ID Hardcoded**
  - **Local**: `app/routes/admin/plans.py` (múltiplas linhas)
  - **Problema**: `admin_id="system"` hardcoded
  - **Solução**: Usar `current_user` do contexto
  - **Severidade**: BAIXA
  - **Tempo**: 30 minutos

### Melhorias de Error Handling

- [ ] Custom exceptions por domínio
- [ ] Error codes padronizados
- [ ] Exception tracking (Sentry)
- [ ] Rate limit exceptions
- [ ] Validation error messages melhorados

---

## 📊 ESTATÍSTICAS DE PROGRESSO

### Por Categoria

| Categoria | Completo | Pendente | % |
|-----------|----------|----------|---|
| Core Auth | 75% | 25% | 🟨 |
| Payments | 65% | 35% | 🟨 |
| Subscriptions | 90% | 10% | 🟩 |
| Plans | 95% | 5% | 🟩 |
| Admin Dashboard | 70% | 30% | 🟨 |
| Cron Jobs | 95% | 5% | 🟩 |
| Email System | 40% | 60% | 🟥 |
| WhatsApp | 0% | 100% | 🟥 |
| Desktop | 0% | 100% | 🟥 |
| Tests | 0% | 100% | 🟥 |
| Security | 60% | 40% | 🟨 |
| Docs | 10% | 90% | 🟥 |

### Totais

- **Completo**: ~70%
- **Pendente**: ~30%
- **Horas Estimadas Restantes**: ~416 horas
- **Semanas Estimadas**: ~10 semanas (1 dev full-time)

---

## 🎯 PRIORIZAÇÃO RECOMENDADA

### Semana 1-2: CRÍTICO
1. Fix `require_admin` alias (5 min)
2. Rate Limiting (1 dia)
3. Password Reset (1 dia)
4. Email Verification (1 dia)
5. Testes básicos (3 dias)
6. WhatsApp routes básicos (5 dias)

### Semana 3-4: ALTA
1. Completar WhatsApp routes
2. Admin user management
3. 2FA implementation
4. Payment refunds
5. Email service completar

### Semana 5-6: MÉDIA
1. Desktop routes
2. OAuth integration
3. Profile enhancements
4. Models faltantes
5. Security adicional

### Semana 7-8: BAIXA
1. Documentação completa
2. CI/CD
3. Monitoramento
4. Admin dashboard avançado

### Semana 9-10: POLISH
1. Performance optimization
2. Advanced features
3. Bug fixes
4. Code review
5. Final testing

---

## ✅ QUICK WINS (Fazer Hoje)

Tarefas rápidas que trazem muito valor:

1. ✅ **Adicionar `require_admin` alias** (5 min)
2. ✅ **Fix Stripe customer creation** (15 min)
3. ✅ **Completar email notifications** (2 horas)
4. ✅ **Implementar password reset** (3 horas)
5. ✅ **Criar estrutura de testes** (2 horas)

**Total**: ~7-8 horas para resolver 5 problemas importantes

---

## 🚀 BLOCKERS PARA PRODUÇÃO

**NÃO PODE IR PARA PRODUÇÃO SEM**:

1. ❌ Rate Limiting implementado
2. ❌ WhatsApp routes básicos (é o core!)
3. ❌ Password reset funcional
4. ❌ Testes mínimos (auth + payments)
5. ❌ Email verification
6. ❌ Error tracking (Sentry)
7. ❌ Documentação API básica

---

## 📞 SUPORTE & REFERÊNCIAS

### Documentação Existente
- `SISTEMA_NOTIFICACOES.md` - Sistema de emails
- `RENOVACAO_AUTOMATICA.md` - Cron jobs
- `QUICK_START_CRON_JOBS.md` - Setup rápido
- `INDEX_DOCUMENTACAO.md` - Índice completo

### Próximos Passos
1. Escolher fase/categoria para trabalhar
2. Criar branch feature específica
3. Implementar + testar
4. Atualizar esta lista
5. Criar PR

---

**Última Atualização**: 19/10/2025
**Por**: Claude Code
**Status**: 🟨 70% Completo - 30% Pendente
