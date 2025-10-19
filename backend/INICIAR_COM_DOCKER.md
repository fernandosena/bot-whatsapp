# 🐳 Iniciar Aplicação com Docker

## Método 1: Iniciar Apenas MongoDB (Recomendado para Desenvolvimento)

Se você quer rodar o MongoDB no Docker mas o backend localmente (para desenvolvimento):

### Passo 1: Iniciar MongoDB com Docker

```bash
# Ir para a pasta raiz do projeto
cd /home/fernando-sena/Documentos/bot

# Iniciar apenas o MongoDB
docker-compose up -d mongodb

# Verificar se está rodando
docker ps
```

### Passo 2: Configurar .env

```bash
cd backend

# Copiar exemplo (se não tiver .env)
cp .env.example .env

# Editar .env
nano .env
```

**Configuração do MongoDB para Docker:**
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business
```

### Passo 3: Iniciar Backend Localmente

```bash
# Usar o script
./start.sh

# OU manualmente
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Método 2: Iniciar Tudo com Docker Compose

Para rodar MongoDB + Backend + Frontend (tudo no Docker):

### Passo 1: Verificar docker-compose.yml

```bash
cd /home/fernando-sena/Documentos/bot
cat docker-compose.yml
```

### Passo 2: Iniciar Todos os Serviços

```bash
# Iniciar todos os containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver apenas logs do backend
docker-compose logs -f backend
```

### Passo 3: Verificar Status

```bash
# Ver containers rodando
docker-compose ps

# Deve mostrar:
# - mongodb
# - backend (se configurado)
# - frontend (se configurado)
```

---

## Comandos Úteis Docker

### Gerenciar MongoDB

```bash
# Iniciar MongoDB
docker-compose up -d mongodb

# Parar MongoDB
docker-compose stop mongodb

# Ver logs do MongoDB
docker-compose logs -f mongodb

# Acessar shell do MongoDB
docker-compose exec mongodb mongosh

# Reiniciar MongoDB
docker-compose restart mongodb
```

### Gerenciar Backend (se rodar no Docker)

```bash
# Iniciar backend
docker-compose up -d backend

# Ver logs em tempo real
docker-compose logs -f backend

# Entrar no container do backend
docker-compose exec backend bash

# Reiniciar backend
docker-compose restart backend
```

### Parar Tudo

```bash
# Parar todos os serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover containers E volumes (CUIDADO: apaga dados)
docker-compose down -v
```

---

## Script Rápido (Apenas MongoDB)

Crie o arquivo `start-mongodb.sh`:

```bash
#!/bin/bash

echo "🐳 Iniciando MongoDB com Docker..."

# Ir para pasta raiz
cd /home/fernando-sena/Documentos/bot

# Verificar se MongoDB já está rodando
if docker ps --format '{{.Names}}' | grep -q mongo; then
    echo "✅ MongoDB já está rodando"
else
    echo "Iniciando MongoDB..."
    docker-compose up -d mongodb
    sleep 3

    if docker ps --format '{{.Names}}' | grep -q mongo; then
        echo "✅ MongoDB iniciado com sucesso"
    else
        echo "❌ Erro ao iniciar MongoDB"
        exit 1
    fi
fi

# Mostrar status
echo ""
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ MongoDB disponível em: mongodb://localhost:27017"
echo ""
echo "Para parar: docker-compose stop mongodb"
```

Tornar executável:
```bash
chmod +x start-mongodb.sh
```

Usar:
```bash
./start-mongodb.sh
```

---

## Troubleshooting Docker

### Problema: "Cannot connect to the Docker daemon"

```bash
# Iniciar Docker
sudo systemctl start docker

# Verificar status
sudo systemctl status docker

# Adicionar seu usuário ao grupo docker (para não usar sudo)
sudo usermod -aG docker $USER
# Depois faça logout/login
```

### Problema: "Port 27017 already in use"

```bash
# Ver o que está usando a porta
sudo lsof -i :27017

# Se for outro MongoDB, pare-o
sudo systemctl stop mongod

# Ou mate o processo
kill -9 PID_DO_PROCESSO
```

### Problema: "docker-compose: command not found"

```bash
# Instalar docker-compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verificar instalação
docker compose version
```

### Problema: Container sai imediatamente

```bash
# Ver logs para descobrir o erro
docker-compose logs mongodb

# Verificar se há problemas com volumes
docker-compose down -v
docker-compose up -d mongodb
```

---

## Verificar MongoDB está Funcionando

### Método 1: Docker logs

```bash
docker-compose logs mongodb | tail -20
# Deve mostrar: "Waiting for connections"
```

### Método 2: Acessar MongoDB shell

```bash
docker-compose exec mongodb mongosh

# No shell do MongoDB:
show dbs
use whatsapp_business
db.stats()
exit
```

### Método 3: Testar conexão do Python

```bash
cd backend
source venv/bin/activate
python

# No Python:
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.whatsapp_business
    print(await db.list_collection_names())

asyncio.run(test())
# Deve funcionar sem erros
```

---

## Fluxo Completo: Do Zero ao Funcionando

```bash
# 1. Iniciar MongoDB com Docker
cd /home/fernando-sena/Documentos/bot
docker-compose up -d mongodb

# Aguardar 3 segundos
sleep 3

# 2. Verificar se MongoDB está rodando
docker ps | grep mongo

# 3. Ir para backend
cd backend

# 4. Configurar .env (primeira vez)
if [ ! -f .env ]; then
    cp .env.example .env
    # Editar MONGODB_URI=mongodb://localhost:27017
    nano .env
fi

# 5. Ativar venv e instalar dependências
source venv/bin/activate
pip install -r requirements.txt

# 6. Iniciar backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Resumo dos Comandos

| Ação | Comando |
|------|---------|
| Iniciar MongoDB | `docker-compose up -d mongodb` |
| Ver logs MongoDB | `docker-compose logs -f mongodb` |
| Parar MongoDB | `docker-compose stop mongodb` |
| Acessar MongoDB shell | `docker-compose exec mongodb mongosh` |
| Ver status | `docker-compose ps` |
| Parar tudo | `docker-compose down` |
| Iniciar backend (local) | `cd backend && ./start.sh` |

---

## Configuração do .env para Docker

```env
# MongoDB (Docker)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=whatsapp_business

# OU se backend também estiver no Docker:
# MONGODB_URI=mongodb://mongodb:27017
# (usa o nome do serviço definido no docker-compose.yml)
```

---

**Pronto!** Agora você pode usar Docker para o MongoDB! 🐳

Use `./start.sh` e ele vai detectar automaticamente se MongoDB está no Docker.
