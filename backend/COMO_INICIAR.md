# 🚀 Como Iniciar a Aplicação - Guia Completo

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- ✅ Python 3.10+
- ✅ MongoDB (local ou Atlas)
- ✅ Node.js 18+ (para o frontend, se aplicável)
- ✅ pip ou poetry

---

## 📋 Checklist Rápido

```bash
# 1. Verificar versões
python --version    # Deve ser 3.10+
mongod --version    # Verificar se MongoDB está instalado

# 2. Verificar se MongoDB está rodando
sudo systemctl status mongod
# OU (se usar Docker)
docker ps | grep mongo
```

---

## 🔧 Configuração Inicial (Primeira Vez)

### 1. Preparar Ambiente Python

```bash
# Navegue até a pasta do backend
cd /home/fernando-sena/Documentos/bot/backend

# Criar ambiente virtual (se não tiver)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip
```

### 2. Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação
pip list | grep fastapi
pip list | grep motor
pip list | grep apscheduler
```

### 3. Configurar MongoDB

**Opção A: MongoDB Local**

```bash
# Iniciar MongoDB
sudo systemctl start mongod

# Verificar se está rodando
sudo systemctl status mongod

# Conectar e verificar
mongosh
# No shell do MongoDB:
show dbs
use whatsapp_business
exit
```

**Opção B: MongoDB Atlas (Cloud)**

1. Criar conta em https://www.mongodb.com/cloud/atlas
2. Criar cluster gratuito
3. Criar database user
4. Pegar connection string

### 4. Criar Arquivo .env

```bash
# Copiar exemplo
cp .env.example .env

# Editar com suas configurações
nano .env
# OU
code .env
```

**Configuração Mínima do .env:**

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business

# JWT
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-123456
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Scheduler
ENABLE_SCHEDULER=true

# Email (OPCIONAL - pode deixar vazio para testes)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Stripe (OPCIONAL)
STRIPE_SECRET_KEY=
STRIPE_PUBLIC_KEY=
STRIPE_WEBHOOK_SECRET=

# Mercado Pago (OPCIONAL)
MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_PUBLIC_KEY=

# PayPal (OPCIONAL)
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_MODE=sandbox
```

**Gerar SECRET_KEY seguro:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ▶️ INICIAR A APLICAÇÃO

### Método 1: Desenvolvimento (Recomendado)

```bash
# Certifique-se de estar na pasta backend com venv ativado
cd /home/fernando-sena/Documentos/bot/backend
source venv/bin/activate

# Iniciar servidor de desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# OU usando Python diretamente
python main.py
```

**Você deve ver:**

```
INFO:     Will watch for changes in these directories: ['/home/fernando-sena/Documentos/bot/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
🚀 Iniciando aplicação...
📦 MongoDB conectado
✅ Rate Limiter iniciado
📅 Scheduler iniciado
📋 5 jobs registrados:
  - check_expiring_subscriptions (diário 9h)
  - process_expired_subscriptions (diário 00:30)
  - renew_subscriptions (diário 2h)
  - cleanup_old_sessions (semanal domingo 3h)
  - cleanup_pending_payments (mensal dia 1 4h)
✅ Aplicação pronta!
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Método 2: Produção

```bash
# Com Gunicorn (melhor performance)
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Método 3: Docker (se configurado)

```bash
# Se tiver Docker Compose
cd /home/fernando-sena/Documentos/bot
docker-compose up -d backend

# Verificar logs
docker-compose logs -f backend
```

---

## ✅ Verificar se Funcionou

### 1. Testar Health Check

```bash
# Em outro terminal
curl http://localhost:8000/health

# Deve retornar:
{
  "status": "healthy",
  "service": "WhatsApp Business SaaS API",
  "version": "1.0.0"
}
```

### 2. Acessar Documentação Automática

Abra no navegador:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Testar Endpoint Root

```bash
curl http://localhost:8000/

# Deve retornar:
{
  "message": "WhatsApp Business SaaS API",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 🧪 Testar Funcionalidades

### 1. Testar Registro de Usuário

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha12345",
    "name": "Usuário Teste",
    "phone": "+5511999999999"
  }'
```

### 2. Testar Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha12345"
  }'

# Salvar o access_token retornado
```

### 3. Testar Rate Limiting

```bash
# Fazer 10 requests rápidas
for i in {1..10}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"wrong@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n\n"
done

# Após 5 requests, deve retornar 429 (Too Many Requests)
```

### 4. Testar Password Reset

```bash
# Solicitar reset
curl -X POST http://localhost:8000/api/auth/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@example.com"}'

# Verificar logs para pegar o token (ou email se configurado)
# Depois confirmar reset
curl -X POST http://localhost:8000/api/auth/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_AQUI",
    "new_password": "nova_senha_123"
  }'
```

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError"

```bash
# Certifique-se de que o venv está ativado
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Problema: "Connection refused" (MongoDB)

```bash
# Iniciar MongoDB
sudo systemctl start mongod

# Verificar status
sudo systemctl status mongod

# Ver logs do MongoDB
sudo journalctl -u mongod -f
```

### Problema: "Port 8000 already in use"

```bash
# Encontrar processo usando porta 8000
sudo lsof -i :8000

# Matar processo
kill -9 PID_DO_PROCESSO

# OU usar outra porta
uvicorn main:app --reload --port 8001
```

### Problema: "SMTP not configured"

É normal se você não configurou email. A aplicação funciona sem SMTP, apenas não envia emails.

Para configurar:

```env
# Gmail (precisa de senha de app)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
```

### Problema: Import errors relacionados a "backend.app"

O código está usando imports absolutos com `backend.app`. Se der erro:

**Opção 1: Ajustar PYTHONPATH**
```bash
export PYTHONPATH="${PYTHONPATH}:/home/fernando-sena/Documentos/bot"
```

**Opção 2: Mudar imports para relativos**
```python
# De:
from backend.app.core.database import ...

# Para:
from app.core.database import ...
```

---

## 📊 Verificar Status dos Serviços

### Verificar Jobs Agendados

```bash
# Primeiro faça login e pegue o token de admin
# Depois:

TOKEN="seu-token-aqui"

curl http://localhost:8000/api/admin/jobs \
  -H "Authorization: Bearer $TOKEN"
```

### Verificar Logs em Tempo Real

```bash
# Se estiver rodando no terminal, os logs aparecem automaticamente

# Se rodando em background:
tail -f logs/app.log

# Filtrar apenas jobs:
tail -f logs/app.log | grep -E "(Job|🔍|📊|✅)"
```

### Verificar MongoDB

```bash
mongosh

use whatsapp_business

# Ver coleções
show collections

# Contar usuários
db.users.countDocuments()

# Ver último usuário criado
db.users.find().sort({created_at: -1}).limit(1)

exit
```

---

## 🛑 Parar a Aplicação

### Método 1: Se estiver em terminal

```
CTRL + C
```

### Método 2: Se estiver em background

```bash
# Encontrar processo
ps aux | grep uvicorn

# Matar processo
kill PID_DO_PROCESSO

# OU matar todos os uvicorn
pkill -f uvicorn
```

### Método 3: Docker

```bash
docker-compose down
```

---

## 📦 Script de Inicialização Rápida

Criar arquivo `start.sh`:

```bash
#!/bin/bash

echo "🚀 Iniciando WhatsApp Business SaaS API..."

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se MongoDB está rodando
if ! systemctl is-active --quiet mongod; then
    echo -e "${RED}❌ MongoDB não está rodando${NC}"
    echo "Iniciando MongoDB..."
    sudo systemctl start mongod
    sleep 2
fi

# Verificar MongoDB novamente
if systemctl is-active --quiet mongod; then
    echo -e "${GREEN}✅ MongoDB rodando${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar MongoDB${NC}"
    exit 1
fi

# Ativar venv
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo -e "${RED}⚠️  Por favor, configure o arquivo .env antes de continuar${NC}"
    exit 1
fi

# Iniciar aplicação
echo -e "${GREEN}▶️  Iniciando servidor...${NC}"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Dar permissão e usar:

```bash
chmod +x start.sh
./start.sh
```

---

## 🎯 Checklist de Inicialização

- [ ] MongoDB rodando
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] SECRET_KEY gerado
- [ ] MONGODB_URI correto
- [ ] Aplicação iniciada
- [ ] Health check passou
- [ ] Swagger acessível

---

## 📞 URLs Importantes

| Serviço | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| MongoDB (local) | mongodb://localhost:27017 |

---

**Pronto!** Sua aplicação deve estar rodando em http://localhost:8000

Use **CTRL+C** para parar o servidor quando quiser.
