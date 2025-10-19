# 🐳 Guia Docker - WhatsApp Business SaaS

**Executar o projeto completo com Docker**

---

## 🚀 Quick Start com Docker

### 1. Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

```bash
# Verificar instalação
docker --version
docker-compose --version
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.docker.example .env.docker

# Editar com suas credenciais
nano .env.docker  # ou vim, code, etc
```

**Importante:** Configure pelo menos:
- `JWT_SECRET_KEY` (use: `openssl rand -base64 32`)
- `NEXTAUTH_SECRET` (use: `openssl rand -base64 32`)
- Credenciais de pagamento (sandbox para testes)

### 3. Iniciar Todos os Serviços

```bash
# Iniciar em background
docker-compose --env-file .env.docker up -d

# Ou iniciar com logs
docker-compose --env-file .env.docker up
```

### 4. Verificar Status

```bash
# Ver containers rodando
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Acessar o Sistema

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Swagger:** http://localhost:8000/docs
- **Mongo Express:** http://localhost:8081 (usuário/senha: admin/admin123)

---

## 📦 Serviços Disponíveis

### Backend (FastAPI)
- **Container:** whatsapp-saas-backend
- **Porta:** 8000
- **URL:** http://localhost:8000
- **Health:** http://localhost:8000/health

### Frontend (Next.js)
- **Container:** whatsapp-saas-frontend
- **Porta:** 3000
- **URL:** http://localhost:3000

### MongoDB
- **Container:** whatsapp-saas-mongodb
- **Porta:** 27017
- **Usuário:** admin (padrão)
- **Senha:** admin123 (padrão)

### Redis
- **Container:** whatsapp-saas-redis
- **Porta:** 6379

### Mongo Express (Interface Web)
- **Container:** whatsapp-saas-mongo-express
- **Porta:** 8081
- **URL:** http://localhost:8081
- **Usuário:** admin
- **Senha:** admin123

**Nota:** Mongo Express só inicia com profile "tools":
```bash
docker-compose --profile tools --env-file .env.docker up
```

---

## 🛠️ Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar e remover containers + volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart backend
docker-compose restart frontend

# Rebuildar imagens
docker-compose build

# Rebuildar e iniciar
docker-compose up -d --build
```

### Logs

```bash
# Ver logs de todos os serviços
docker-compose logs

# Seguir logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Executar Comandos nos Containers

```bash
# Backend - Acessar shell
docker-compose exec backend bash

# Backend - Executar comando Python
docker-compose exec backend python -c "print('Hello')"

# Backend - Migração do banco (quando implementado)
docker-compose exec backend python migrate.py

# Frontend - Acessar shell
docker-compose exec frontend sh

# Frontend - Instalar nova dependência
docker-compose exec frontend npm install pacote-novo

# MongoDB - Acessar shell do MongoDB
docker-compose exec mongodb mongosh

# MongoDB - Backup
docker-compose exec mongodb mongodump --out /data/backup

# Redis - Acessar CLI
docker-compose exec redis redis-cli
```

### Volumes e Dados

```bash
# Listar volumes
docker volume ls | grep whatsapp-saas

# Inspecionar volume
docker volume inspect bot_mongodb-data

# Backup do volume MongoDB
docker run --rm -v bot_mongodb-data:/data -v $(pwd):/backup ubuntu tar czf /backup/mongodb-backup.tar.gz /data

# Restaurar backup
docker run --rm -v bot_mongodb-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/mongodb-backup.tar.gz -C /
```

---

## 🔧 Desenvolvimento com Docker

### Hot Reload

Ambos backend e frontend estão configurados para hot reload:

**Backend:**
- Mudanças em arquivos `.py` recarregam automaticamente
- Usa `uvicorn --reload`

**Frontend:**
- Mudanças em arquivos `.tsx`, `.ts`, `.css` recarregam automaticamente
- Usa `npm run dev`

### Acessar Container para Debug

```bash
# Backend
docker-compose exec backend bash

# Dentro do container, você pode:
python
>>> from app.core.database import mongodb
>>> # testar código

# Frontend
docker-compose exec frontend sh

# Dentro do container:
npm run build  # testar build
```

### Modificar Código

O código está montado como volume, então:
- Edite arquivos normalmente no host
- Mudanças aparecem imediatamente no container
- Hot reload funciona

**Arquivos montados:**
- `./backend:/app` (backend)
- `./web/frontend:/app` (frontend)

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs backend

# Ver eventos do Docker
docker events

# Inspecionar container
docker inspect whatsapp-saas-backend
```

### MongoDB não conecta

```bash
# Verificar se MongoDB está rodando
docker-compose ps mongodb

# Ver logs do MongoDB
docker-compose logs mongodb

# Testar conexão
docker-compose exec backend python -c "from app.core.database import mongodb; print('OK')"
```

### Porta já em uso

```bash
# Verificar o que está usando a porta 8000
sudo lsof -i :8000

# Ou mudar porta no docker-compose.yml
# De: "8000:8000"
# Para: "8001:8000"
```

### Rebuildar tudo do zero

```bash
# Parar tudo
docker-compose down

# Remover volumes (CUIDADO!)
docker volume prune

# Rebuildar imagens
docker-compose build --no-cache

# Iniciar novamente
docker-compose up -d
```

### Limpar espaço em disco

```bash
# Ver uso de espaço
docker system df

# Limpar containers parados
docker container prune

# Limpar imagens não usadas
docker image prune

# Limpar tudo não usado (CUIDADO!)
docker system prune -a
```

---

## 📊 Monitoramento

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend (deve retornar HTML)
curl http://localhost:3000

# MongoDB (via backend)
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Redis
docker-compose exec redis redis-cli ping
```

### Uso de Recursos

```bash
# Ver uso de CPU/RAM/Rede
docker stats

# Ver uso de um container específico
docker stats whatsapp-saas-backend

# Ver processos rodando no container
docker-compose exec backend ps aux
```

---

## 🔒 Segurança

### Produção

**NUNCA use em produção sem:**

1. **Mudar senhas padrão**
   ```bash
   MONGO_ROOT_PASSWORD=senha-forte-aleatoria
   MONGO_EXPRESS_PASSWORD=outra-senha-forte
   ```

2. **Usar secrets do JWT**
   ```bash
   JWT_SECRET_KEY=$(openssl rand -base64 32)
   NEXTAUTH_SECRET=$(openssl rand -base64 32)
   ```

3. **Desabilitar DEBUG**
   ```bash
   DEBUG=False
   ENVIRONMENT=production
   ```

4. **Usar HTTPS**
   - Adicionar nginx como reverse proxy
   - Certificado SSL/TLS

5. **Restringir acesso ao Mongo Express**
   - Não expor porta publicamente
   - Ou usar autenticação forte

### Network Isolation

Todos os serviços estão na mesma rede Docker (`whatsapp-saas-network`):
- Comunicam entre si por nome do serviço
- Ex: backend acessa MongoDB via `mongodb://mongodb:27017`

---

## 📝 Variáveis de Ambiente

### Arquivo `.env.docker`

O Docker Compose usa `.env.docker` (não confundir com `backend/.env`).

**Estrutura:**
```bash
# MongoDB
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=...

# JWT
JWT_SECRET_KEY=...
NEXTAUTH_SECRET=...

# Payment Gateways
MERCADOPAGO_ACCESS_TOKEN=...
STRIPE_SECRET_KEY=...
PAYPAL_CLIENT_ID=...
```

### Sobrescrever Variáveis

```bash
# Passar variável direto no comando
FRONTEND_URL=http://192.168.1.100:3000 docker-compose up

# Ou exportar antes
export FRONTEND_URL=http://192.168.1.100:3000
docker-compose up
```

---

## 🚢 Deploy em Produção

### 1. Build para Produção

Crie `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      ENVIRONMENT: production
      DEBUG: "False"
    # ... resto da config

  frontend:
    build:
      context: ./web/frontend
      dockerfile: Dockerfile.prod
    # ... resto da config
```

### 2. Nginx Reverse Proxy

```bash
# Adicionar nginx ao docker-compose.prod.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

### 3. SSL com Let's Encrypt

```bash
# Usar certbot
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d seu-dominio.com
```

---

## 🎯 Profiles do Docker Compose

### Profile: tools

Serviços opcionais (Mongo Express):

```bash
# Iniciar com Mongo Express
docker-compose --profile tools up -d

# Iniciar sem Mongo Express (padrão)
docker-compose up -d
```

### Criar Novos Profiles

Adicione no `docker-compose.yml`:

```yaml
my-service:
  # ...
  profiles:
    - development
```

Então use:
```bash
docker-compose --profile development up
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

### Arquivos Importantes
- `docker-compose.yml` - Configuração principal
- `backend/Dockerfile` - Build do backend
- `web/frontend/Dockerfile.dev` - Build do frontend (dev)
- `.env.docker.example` - Template de variáveis

---

## ✅ Checklist de Uso

### Primeira Vez

- [ ] Instalar Docker e Docker Compose
- [ ] Copiar `.env.docker.example` para `.env.docker`
- [ ] Configurar variáveis em `.env.docker`
- [ ] Executar `docker-compose up -d`
- [ ] Verificar `docker-compose ps`
- [ ] Acessar http://localhost:3000

### Uso Diário

- [ ] `docker-compose up -d` - Iniciar
- [ ] `docker-compose logs -f` - Ver logs
- [ ] Desenvolver normalmente
- [ ] `docker-compose down` - Parar ao fim do dia

### Antes de Commitar

- [ ] `docker-compose exec backend pytest` - Rodar testes
- [ ] `docker-compose exec frontend npm run lint` - Lint
- [ ] `docker-compose exec frontend npm run build` - Testar build

---

**Última atualização:** 19/10/2025 - 23:30

**Dica:** Para desenvolvimento rápido sem Docker, use os scripts:
- `./setup.sh` - Setup inicial
- `./start.sh` - Iniciar backend e frontend

**Para produção, sempre use Docker!** 🐳
