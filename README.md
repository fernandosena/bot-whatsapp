# 🚀 WhatsApp Business SaaS - Sistema Completo

Sistema SaaS completo para gerenciamento de WhatsApp Business com planos configuráveis, pagamentos integrados e aplicativo desktop multiplataforma.

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Documentação](#documentação)
- [Progresso](#progresso)

## ✨ Características

### 🔐 Sistema de Autenticação Robusto
- NextAuth.js v5 com múltiplos providers (Google, GitHub, LinkedIn)
- Autenticação por email/senha com CAPTCHA
- Device fingerprinting e rastreamento de sessões
- Sistema de bloqueio por IP/MAC

### 💰 Planos Totalmente Configuráveis
- **Admin cria e gerencia planos pelo painel** (não são fixos!)
- Funcionalidades customizáveis por plano
- Suporte a trial, setup fee e múltiplas formas de pagamento
- Exemplo de planos: Free, Basic, Pro, Enterprise, ou personalizados

### 💳 Pagamentos Multi-Gateway
- **Mercado Pago** (PIX, Boleto)
- **Stripe** (Apple Pay, Google Pay, Cartão)
- **PayPal**
- Webhooks para todos os gateways
- Renovação automática de assinaturas

### 🗑️ Sistema de Soft Delete
- **NUNCA deleta dados fisicamente**
- Todos os schemas possuem `flag_del` para marcar exclusões
- Painel admin para recuperar dados deletados
- Auditoria completa (quem deletou, quando, por quê)

### 💻 Aplicativo Desktop (Electron)
- **100% online** - sem banco de dados local
- Funciona em Linux, macOS e Windows
- Sistema de ativação por chave
- Atualizações obrigatórias
- Sincronização em tempo real com backend

### 📱 Funcionalidades WhatsApp
- Raspagem de contatos do Google Maps
- Envio em massa com variáveis personalizadas
- Sequências de mensagens
- Envio de mídia (áudio, imagem, vídeo)
- Campanhas agendadas
- Relatórios avançados

## 🛠️ Tecnologias

### Backend
- **FastAPI 0.109+** - Framework web assíncrono
- **MongoDB 7.0+** - Banco de dados NoSQL
- **Motor** - Driver assíncrono para MongoDB
- **Pydantic** - Validação de dados
- **Python 3.11+**

### Frontend Web
- **Next.js 15** - Framework React com App Router
- **NextAuth.js v5** - Autenticação
- **Shadcn UI** - Componentes UI
- **TailwindCSS** - Estilização
- **TypeScript** - Tipagem estática

### Desktop
- **Electron** - Framework para apps desktop
- **Electron Forge** - Build e distribuição

### DevOps
- **Docker** - Containerização
- **Nginx** - Reverse proxy
- **PM2** - Process manager
- **GitHub Actions** - CI/CD

### Monitoramento
- **Sentry** - Error tracking
- **Prometheus + Grafana** - Métricas
- **Redis** - Cache

## 🏗️ Arquitetura

```
whatsapp-business-saas/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Configurações (database, config)
│   │   ├── models/            # Schemas Pydantic/MongoDB
│   │   ├── routes/            # Endpoints da API
│   │   │   ├── admin/         # Rotas admin (planos, usuários, etc)
│   │   │   ├── auth/          # Autenticação
│   │   │   ├── payments/      # Pagamentos (Mercado Pago, Stripe, PayPal)
│   │   │   ├── desktop/       # Updates e ativação desktop
│   │   │   └── whatsapp/      # Funcionalidades WhatsApp
│   │   ├── middleware/        # Middlewares (auth, rate limit, etc)
│   │   └── utils/             # Utilitários (soft_delete, audit, etc)
│   ├── main.py                # Entry point FastAPI
│   ├── requirements.txt       # Dependências Python
│   └── .env.example           # Variáveis de ambiente
│
├── web/                       # Next.js frontend
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── app/           # App Router
│   │   │   │   ├── (auth)/    # Páginas de autenticação
│   │   │   │   ├── admin/     # Painel administrativo
│   │   │   │   ├── dashboard/ # Dashboard usuário
│   │   │   │   └── pricing/   # Página de preços
│   │   │   ├── components/    # Componentes React
│   │   │   ├── lib/           # Utilitários
│   │   │   └── types/         # TypeScript types
│   │   ├── public/            # Assets estáticos
│   │   └── package.json
│   └── auth.ts                # NextAuth.js config
│
├── desktop/                   # Electron app
│   ├── main.js               # Processo principal
│   ├── preload.js            # IPC bridge
│   ├── renderer/             # UI do desktop
│   └── package.json
│
├── src/                      # Código legado (será refatorado)
│   ├── whatsapp/             # Integração WhatsApp (MANTER)
│   ├── scraper/              # Scraping Google Maps (MANTER)
│   └── database/             # SQLite (MIGRAR para MongoDB)
│
├── archive/                  # Arquivos movidos (não usar)
│   ├── scripts/              # Scripts shell antigos
│   └── tests/                # Testes antigos
│
├── PLANO_COMPLETO_WEB_DESKTOP.md    # 📄 Documentação completa
├── PROGRESSO_IMPLEMENTACAO.md       # 📊 Checklist de progresso
└── README.md                         # 📖 Este arquivo
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- MongoDB 7.0+
- Redis 7.0+

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whatsapp-business-saas.git
cd whatsapp-business-saas
```

### 2. Backend (FastAPI)

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Iniciar servidor
python main.py
# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend rodando em: http://localhost:8000
Documentação da API: http://localhost:8000/docs

### 3. Frontend Web (Next.js)

```bash
cd web/frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Edite o .env.local com suas credenciais

# Instalar Shadcn UI components
npx shadcn@latest init

# Iniciar servidor de desenvolvimento
npm run dev
```

Frontend rodando em: http://localhost:3000

### 4. Desktop (Electron)

```bash
cd desktop

# Instalar dependências
npm install

# Iniciar em modo desenvolvimento
npm run dev

# Build para produção
npm run make  # Cria builds para todas as plataformas
```

## 📚 Documentação

### Documentos Principais

1. **[PLANO_COMPLETO_WEB_DESKTOP.md](./PLANO_COMPLETO_WEB_DESKTOP.md)**
   - Documentação técnica completa do sistema
   - Especificações de todos os módulos
   - Schemas MongoDB detalhados
   - Fluxos de autenticação e pagamento
   - Dicas de robustez e segurança

2. **[PROGRESSO_IMPLEMENTACAO.md](./PROGRESSO_IMPLEMENTACAO.md)**
   - Checklist completo de implementação
   - Status atual de cada módulo
   - Roadmap por fases
   - Métricas de sucesso

### API Documentation

Acesse a documentação interativa da API em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principais

#### Planos (Admin)
- `GET /api/admin/plans` - Listar planos
- `POST /api/admin/plans` - Criar plano
- `PUT /api/admin/plans/{id}` - Atualizar plano
- `DELETE /api/admin/plans/{id}` - Deletar plano (soft delete)
- `POST /api/admin/plans/deleted/{id}/restore` - Restaurar plano

#### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token

#### Pagamentos
- `POST /api/payments/mercadopago/create` - Criar pagamento Mercado Pago
- `POST /api/payments/stripe/create` - Criar pagamento Stripe
- `POST /api/payments/paypal/create` - Criar pagamento PayPal

## 📊 Progresso

### Status Atual (19/10/2025)

| Módulo | Progresso | Status |
|--------|-----------|--------|
| **Backend (FastAPI)** | 50% | ✅ Sessões e Perfil Completos |
| **Frontend (Next.js)** | 75% | ✅ 9 Páginas Funcionais |
| **Desktop (Electron)** | 0% | ⏳ Não Iniciado |
| **MongoDB** | 50% | ✅ Schemas Criados |
| **Autenticação (JWT)** | 100% | ✅ Completo |
| **Pagamentos** | 0% | ⏳ Próxima Prioridade |
| **WhatsApp** | 15% | ⚠️ Código Legado |

**Progresso Geral: 60%** 🎉

**📄 Documentação Completa:** 15 arquivos MD (~9.000 linhas)

### O que está pronto:

✅ **Backend - API Completa**
- FastAPI 0.109+ configurado com CORS
- MongoDB com Motor (async driver)
- Sistema de soft delete (10 funções utilitárias)
- Sistema de auditoria completo
- Schemas: User, Plan, Subscription, Session
- **Autenticação JWT completa** (7 endpoints)
- **CRUD de planos admin** (10 endpoints)
- **Dashboard admin com métricas** (8 endpoints)
- Middleware de autenticação/autorização
- Requirements.txt com 40+ dependências
- Documentação completa da API

✅ **Frontend - Interface Completa**
- Next.js 15 + App Router
- TypeScript 5.3 + TailwindCSS 3.3
- Shadcn UI (8 componentes)
- Recharts (gráficos interativos)
- Cliente API com axios e auto-refresh
- **9 páginas funcionais:**
  - Homepage (landing page)
  - Login/Registro
  - Pricing (consome API de planos)
  - Dashboard do usuário
  - **Painel Admin de Planos** (CRUD completo)
  - **Dashboard Admin** (gráficos e métricas)
  - **Perfil do Usuário** (edição e segurança)
  - **Sessões Ativas** (gerenciamento de dispositivos) 🆕
- Proteção de rotas (middleware + HOC)
- Toast notifications
- Loading states
- Error handling

✅ **Documentação**
- 15 documentos MD (~9.000 linhas)
- PLANO_COMPLETO_WEB_DESKTOP.md (4.380 linhas)
- PROGRESSO_IMPLEMENTACAO.md (checklist completo)
- ENCERRAMENTO_SESSAO.md (resumo final da sessão)
- PROXIMA_SESSAO_GUIA.md (guia para próxima sessão)
- SESSAO_EXTENSA_FINAL.md (resumo completo)
- API_ENDPOINTS.md (referência completa)
- TESTING.md (guia de testes)

### Próximos passos:

1. **Sistema de Pagamentos** - Mercado Pago, Stripe, PayPal
2. **Dashboard Admin** - Gráficos e métricas gerais
3. **Perfil de Usuário** - Edição de dados, alterar senha
4. **Gerenciamento de Sessões** - Visualizar e encerrar sessões ativas
5. **Desktop App** - Configurar Electron
6. **Refatoração WhatsApp** - Integrar código legado com novo sistema

## 🔑 Conceitos Importantes

### 1. Soft Delete
O sistema **NUNCA** deleta dados fisicamente. Todos os schemas possuem:
- `flag_del`: Boolean (true = deletado)
- `deleted_at`: Data da exclusão
- `deleted_by`: Quem deletou
- `deleted_reason`: Motivo da exclusão

### 2. Planos Configuráveis
Os planos **NÃO são fixos**. O administrador pode:
- Criar planos customizados
- Definir preços e funcionalidades
- Ativar/desativar/arquivar planos
- Criar planos promocionais sazonais

### 3. Desktop 100% Online
O aplicativo desktop **NÃO possui banco de dados local**:
- Todos os dados ficam no servidor
- Requisição ao backend para tudo
- Sincronização em tempo real
- Atualizações obrigatórias

## 🤝 Contribuindo

Este é um projeto privado em desenvolvimento. Para contribuir:

1. Leia o [PLANO_COMPLETO_WEB_DESKTOP.md](./PLANO_COMPLETO_WEB_DESKTOP.md)
2. Consulte o [PROGRESSO_IMPLEMENTACAO.md](./PROGRESSO_IMPLEMENTACAO.md)
3. Nunca delete dados fisicamente (use soft delete)
4. Sempre use auditoria para ações críticas
5. Mantenha a documentação atualizada

## 📝 Notas Importantes

- **Soft Delete**: NUNCA use `deleteOne()` ou `deleteMany()` - sempre use soft delete
- **Planos**: Admin gerencia via painel, não são fixos no código
- **Desktop**: 100% online, sem banco local
- **Auditoria**: Todas ações críticas devem ser logadas
- **Segurança**: Device fingerprinting, rate limiting, bloqueio de IP

## 📄 Licença

Projeto privado - Todos os direitos reservados.

---

**Desenvolvido com ❤️ para transformar o WhatsApp Business em SaaS**
