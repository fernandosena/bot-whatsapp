# 🌐 Frontend - WhatsApp Business SaaS

Frontend Next.js 15 com App Router, Shadcn UI e integração completa com backend FastAPI.

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
cd web/frontend
npm install
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env.local
```

Edite `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

Frontend rodando em: **http://localhost:3000**

## 📁 Estrutura do Projeto

```
web/frontend/
├── src/
│   ├── app/                    # App Router (Next.js 15)
│   │   ├── auth/              # Páginas de autenticação
│   │   │   ├── login/         # Página de login
│   │   │   └── register/      # Página de registro
│   │   ├── globals.css        # Estilos globais + Tailwind
│   │   ├── layout.tsx         # Layout principal
│   │   └── page.tsx           # Homepage
│   │
│   ├── components/
│   │   └── ui/                # Componentes Shadcn UI
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       └── card.tsx
│   │
│   ├── lib/
│   │   ├── api.ts             # Cliente API (axios)
│   │   └── utils.ts           # Utilitários (cn)
│   │
│   └── types/
│       └── index.ts           # TypeScript types
│
├── components.json            # Config Shadcn UI
├── tailwind.config.ts         # Config Tailwind
├── tsconfig.json              # Config TypeScript
├── next.config.js             # Config Next.js
└── package.json               # Dependências
```

## ✅ O Que Está Pronto

### Configuração Base
- [x] Next.js 15 com App Router
- [x] TypeScript configurado
- [x] TailwindCSS + Shadcn UI
- [x] Configuração de variáveis de ambiente

### Componentes UI
- [x] Button
- [x] Input
- [x] Label
- [x] Card (Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter)

### API Client
- [x] Axios configurado com interceptors
- [x] Refresh token automático
- [x] Funções de autenticação
- [x] Funções de gerenciamento de planos
- [x] LocalStorage helper functions

### Páginas
- [x] Homepage (landing page com features)
- [x] Login (/auth/login)
- [x] Registro (/auth/register)

### Types TypeScript
- [x] User
- [x] Plan
- [x] PlanFeatures
- [x] Session
- [x] LoginResponse
- [x] ApiError

## 🔗 Integração com Backend

O frontend se comunica com o backend FastAPI através do cliente API em `src/lib/api.ts`.

### Endpoints Disponíveis

**Autenticação:**
- `authApi.register()` - Registrar usuário
- `authApi.login()` - Login
- `authApi.logout()` - Logout
- `authApi.me()` - Dados do usuário
- `authApi.getSessions()` - Sessões ativas
- `authApi.terminateSession(id)` - Encerrar sessão

**Planos (Admin):**
- `plansApi.list()` - Listar planos
- `plansApi.get(id)` - Buscar plano
- `plansApi.create()` - Criar plano
- `plansApi.update(id)` - Atualizar plano
- `plansApi.delete(id)` - Deletar plano
- `plansApi.toggleStatus(id)` - Ativar/desativar
- `plansApi.listDeleted()` - Listar deletados
- `plansApi.restore(id)` - Restaurar plano
- `plansApi.stats()` - Estatísticas

### Autenticação Automática

O cliente API possui interceptors que:
1. Adiciona token automaticamente em todas as requisições
2. Detecta token expirado (401)
3. Renova automaticamente usando refresh token
4. Redireciona para login se refresh falhar

## 🧪 Como Testar

### 1. Certifique-se que o Backend está rodando

```bash
# Em outro terminal
cd backend
source venv/bin/activate
python main.py
```

Backend deve estar em: http://localhost:8000

### 2. Inicie o Frontend

```bash
cd web/frontend
npm run dev
```

### 3. Teste o Fluxo

1. Acesse http://localhost:3000
2. Clique em "Começar Grátis"
3. Preencha o formulário de registro
4. Será redirecionado automaticamente após login

### 4. Verifique no MongoDB

```bash
mongosh

use whatsapp_business

# Ver usuário criado
db.users.find().pretty()

# Ver sessão criada
db.sessions.find().pretty()
```

## 📝 Próximos Passos

### Páginas a Criar
- [ ] `/pricing` - Página de preços (lista planos do backend)
- [ ] `/dashboard` - Dashboard do usuário
- [ ] `/admin/dashboard` - Dashboard admin
- [ ] `/admin/plans` - Gerenciamento de planos
- [ ] `/admin/users` - Gerenciamento de usuários

### Componentes a Criar
- [ ] Badge
- [ ] Table
- [ ] Dialog
- [ ] Select
- [ ] Form (react-hook-form)
- [ ] Loading spinner
- [ ] Navbar/Sidebar

### Funcionalidades
- [ ] NextAuth.js v5 (OAuth Google, GitHub, LinkedIn)
- [ ] Proteção de rotas (middleware)
- [ ] Dark mode toggle
- [ ] Perfil do usuário
- [ ] Gerenciamento de sessões ativas

## 🎨 Customização

### Cores

Edite `src/app/globals.css` para customizar as cores do tema:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

### Componentes Shadcn UI

Para adicionar novos componentes:

```bash
npx shadcn@latest add [component-name]
```

Exemplos:
```bash
npx shadcn@latest add badge
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add select
```

## 🐛 Troubleshooting

### Erro: "Cannot find module '@/components/ui/button'"

Certifique-se que os paths estão configurados em `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Erro: "Failed to fetch"

Verifique se:
1. Backend está rodando (http://localhost:8000)
2. `.env.local` está configurado corretamente
3. CORS está habilitado no backend

### Erro: "localStorage is not defined"

Ocorre em Server Components. Use `"use client"` no topo do arquivo para componentes que usam localStorage.

## 📦 Scripts Disponíveis

```bash
npm run dev        # Inicia servidor de desenvolvimento
npm run build      # Build para produção
npm run start      # Inicia servidor de produção
npm run lint       # Executa ESLint
```

## 🔗 Links Úteis

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Shadcn UI**: https://ui.shadcn.com

---

**🎉 Frontend está funcional e pronto para desenvolvimento!**
