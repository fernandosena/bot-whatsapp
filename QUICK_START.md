# ⚡ Quick Start - Iniciando o Projeto

Guia rápido para começar a usar o WhatsApp Business SaaS.

---

## 🚀 Início Rápido (5 minutos)

### 1. Instalar Dependências Backend

```bash
cd /home/fernando-sena/Documentos/bot/backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar (use seu editor favorito)
nano .env
```

**Mínimo necessário para testar:**
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Iniciar MongoDB

```bash
# Iniciar MongoDB
sudo systemctl start mongod

# Verificar se está rodando
sudo systemctl status mongod
```

### 4. Iniciar Backend

```bash
# Certifique-se de estar na pasta backend com venv ativado
cd /home/fernando-sena/Documentos/bot/backend
source venv/bin/activate

# Iniciar servidor
python main.py

# OU usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Backend rodando em: http://localhost:8000**
**📚 Documentação: http://localhost:8000/docs**

---

## 🧪 Testar API (2 minutos)

### Teste 1: Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "WhatsApp Business SaaS API",
  "version": "1.0.0"
}
```

### Teste 2: Registrar Usuário

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin12345",
    "name": "Admin User"
  }'
```

### Teste 3: Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin12345"
  }'
```

**Copie o `access_token` da resposta!**

### Teste 4: Criar Plano (como Admin)

Primeiro, torne o usuário admin no MongoDB:

```bash
mongosh

use whatsapp_business

db.users.updateOne(
  { email: "admin@test.com" },
  { $set: { role: "admin" } }
)

exit
```

Agora crie um plano:

```bash
# Substitua SEU_TOKEN pelo access_token do login
curl -X POST http://localhost:8000/api/admin/plans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "name": "Pro",
    "slug": "pro",
    "description": "Plano profissional",
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

### Teste 5: Listar Planos

```bash
curl -X GET http://localhost:8000/api/admin/plans/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 📊 Verificar no MongoDB

```bash
mongosh

use whatsapp_business

# Ver usuários
db.users.find().pretty()

# Ver planos
db.plans.find().pretty()

# Ver sessões
db.sessions.find().pretty()

# Ver logs de auditoria
db.audit_logs.find().sort({timestamp: -1}).limit(5).pretty()

exit
```

---

## 🌐 Acessar Documentação Interativa

Abra no navegador:

**http://localhost:8000/docs**

Lá você pode:
- ✅ Ver todos os endpoints
- ✅ Testar diretamente
- ✅ Autorizar com seu token
- ✅ Ver schemas de request/response

---

## 📁 Estrutura do Projeto

```
bot/
├── backend/                    # ✅ FastAPI backend (FUNCIONAL)
│   ├── app/
│   │   ├── core/              # Database, security
│   │   ├── models/            # User, Plan, Subscription, Session
│   │   ├── routes/            # Endpoints
│   │   │   ├── admin/         # Plans CRUD
│   │   │   └── auth/          # Authentication
│   │   ├── middleware/        # Auth middleware
│   │   └── utils/             # Soft delete, audit
│   ├── main.py                # FastAPI app
│   ├── requirements.txt       # Dependências
│   ├── .env.example           # Config exemplo
│   └── TESTING.md             # Guia de testes
│
├── web/                       # ⏳ Next.js frontend (NÃO INICIADO)
├── desktop/                   # ⏳ Electron app (NÃO INICIADO)
│
├── src/                       # ⚠️ Código legado (MANTER)
│   ├── whatsapp/              # Integração WhatsApp
│   └── scraper/               # Google Maps scraper
│
├── PLANO_COMPLETO_WEB_DESKTOP.md    # 📄 Documentação completa
├── PROGRESSO_IMPLEMENTACAO.md       # 📊 Checklist
├── RESUMO_SESSAO.md                 # 📝 O que foi feito
├── QUICK_START.md                   # ⚡ Este arquivo
└── README.md                         # 📖 Documentação geral
```

---

## 🔥 Comandos Úteis

### Backend

```bash
# Ativar ambiente virtual
cd backend && source venv/bin/activate

# Iniciar servidor
python main.py

# Iniciar com reload automático
uvicorn main:app --reload

# Instalar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt
```

### MongoDB

```bash
# Iniciar
sudo systemctl start mongod

# Parar
sudo systemctl stop mongod

# Reiniciar
sudo systemctl restart mongod

# Ver logs
sudo journalctl -u mongod -f

# Acessar MongoDB shell
mongosh
```

### Git

```bash
# Ver status
git status

# Adicionar alterações
git add .

# Commit
git commit -m "feat: descrição da mudança"

# Push
git push origin main
```

---

## 🐛 Troubleshooting

### Erro: "MongoDB connection failed"

```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Se não estiver, iniciar
sudo systemctl start mongod

# Habilitar para iniciar com o sistema
sudo systemctl enable mongod
```

### Erro: "Module not found"

```bash
# Certifique-se de estar com venv ativado
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Port 8000 already in use"

```bash
# Encontrar processo usando a porta
lsof -i :8000

# Matar processo
kill -9 PID_DO_PROCESSO

# OU usar outra porta
uvicorn main:app --reload --port 8001
```

### Erro: "Token inválido"

- Token expira em 15 minutos
- Use o endpoint `/api/auth/refresh` para renovar
- Ou faça login novamente

---

## 📚 Documentação Completa

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | Visão geral do projeto |
| `PLANO_COMPLETO_WEB_DESKTOP.md` | Especificação técnica completa |
| `PROGRESSO_IMPLEMENTACAO.md` | Checklist de implementação |
| `RESUMO_SESSAO.md` | O que foi feito nesta sessão |
| `backend/TESTING.md` | Guia completo de testes |
| `QUICK_START.md` | Este guia rápido |

---

## ✅ Checklist Primeira Execução

- [ ] MongoDB instalado e rodando
- [ ] Python 3.11+ instalado
- [ ] Dependências backend instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Backend rodando (`python main.py`)
- [ ] Health check funcionando (`curl http://localhost:8000/health`)
- [ ] Usuário registrado
- [ ] Login funcionando
- [ ] Token obtido
- [ ] Usuário promovido a admin no MongoDB
- [ ] Plano criado com sucesso
- [ ] Documentação Swagger acessível (`http://localhost:8000/docs`)

---

## 🎯 Próximos Passos

1. **Explorar a API** - http://localhost:8000/docs
2. **Ler documentação** - `backend/TESTING.md`
3. **Ver o que falta** - `PROGRESSO_IMPLEMENTACAO.md`
4. **Começar frontend** - Configurar Next.js

---

**🚀 Backend está 100% funcional! Boa codificação!**
