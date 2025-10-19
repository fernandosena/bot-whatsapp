# 📜 Guia de Scripts - WhatsApp Business SaaS

**Scripts de automação para desenvolvimento e deploy**

---

## 📦 Scripts Disponíveis

### 1. setup.sh - Setup Inicial
**Uso:** Primeira vez configurando o projeto

```bash
./setup.sh
```

**O que faz:**
- ✅ Verifica pré-requisitos (Python, Node.js, MongoDB)
- ✅ Cria ambiente virtual Python
- ✅ Instala dependências do backend
- ✅ Instala dependências do frontend
- ✅ Cria arquivos `.env` se não existirem
- ✅ Exibe próximos passos

**Quando usar:**
- Primeira vez clonando o repositório
- Após limpar instalação
- Configurar ambiente em novo computador

---

### 2. start.sh - Iniciar Sistema
**Uso:** Iniciar backend e frontend simultaneamente

```bash
./start.sh
```

**O que faz:**
- ✅ Verifica se MongoDB está rodando
- ✅ Inicia backend em background
- ✅ Inicia frontend em background
- ✅ Exibe PIDs e URLs
- ✅ Monitora processos
- ✅ Ctrl+C encerra tudo

**Quando usar:**
- Desenvolvimento diário
- Testes locais
- Demonstrações

**Logs:**
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`

**Ver logs em tempo real:**
```bash
# Terminal 1
./start.sh

# Terminal 2
tail -f logs/backend.log

# Terminal 3
tail -f logs/frontend.log
```

---

## 🐳 Docker

### docker-compose.yml - Ambiente Completo

**Uso:** Executar com Docker

```bash
# Primeira vez
cp .env.docker.example .env.docker
# Editar .env.docker com suas credenciais

# Iniciar
docker-compose --env-file .env.docker up -d

# Parar
docker-compose down
```

**Serviços inclusos:**
- MongoDB (porta 27017)
- Redis (porta 6379)
- Backend (porta 8000)
- Frontend (porta 3000)
- Mongo Express (porta 8081) - opcional

**Ver guia completo:** [DOCKER_GUIA.md](./DOCKER_GUIA.md)

---

## 🔧 Comandos Úteis

### Backend

```bash
# Ativar ambiente virtual
cd backend
source venv/bin/activate

# Rodar servidor manualmente
python main.py

# Rodar testes (quando implementado)
pytest

# Instalar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt
```

### Frontend

```bash
cd web/frontend

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Rodar produção localmente
npm run start

# Lint
npm run lint

# Instalar nova dependência
npm install nome-do-pacote
```

### MongoDB

```bash
# Iniciar (Linux)
sudo systemctl start mongod

# Verificar status
sudo systemctl status mongod

# Acessar shell
mongosh

# Usar database
use whatsapp_business

# Ver coleções
show collections

# Consultar dados
db.users.find()
db.payments.find({status: "approved"})
```

---

## 📊 Fluxo de Desenvolvimento

### Desenvolvimento Local (Sem Docker)

```bash
# 1. Setup inicial (primeira vez)
./setup.sh

# 2. Configurar .env
nano backend/.env
# Adicionar credenciais

# 3. Iniciar MongoDB
sudo systemctl start mongod

# 4. Iniciar sistema
./start.sh

# 5. Acessar
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Swagger:  http://localhost:8000/docs

# 6. Desenvolver
# Editar arquivos normalmente
# Hot reload funciona automaticamente

# 7. Encerrar (Ctrl+C no terminal do start.sh)
```

### Desenvolvimento com Docker

```bash
# 1. Setup inicial
cp .env.docker.example .env.docker
nano .env.docker  # Configurar

# 2. Iniciar
docker-compose --env-file .env.docker up -d

# 3. Ver logs
docker-compose logs -f

# 4. Desenvolver
# Editar arquivos normalmente
# Hot reload funciona

# 5. Executar comandos
docker-compose exec backend python manage.py migrate

# 6. Parar
docker-compose down
```

---

## 🧪 Testes

### Backend

```bash
cd backend
source venv/bin/activate

# Rodar todos os testes
pytest

# Rodar com coverage
pytest --cov=app

# Rodar testes específicos
pytest tests/test_auth.py

# Com Docker
docker-compose exec backend pytest
```

### Frontend

```bash
cd web/frontend

# Rodar testes
npm test

# Com coverage
npm run test:coverage

# E2E (quando implementado)
npm run test:e2e

# Com Docker
docker-compose exec frontend npm test
```

---

## 🚀 Deploy

### Preparação

```bash
# 1. Buildar frontend
cd web/frontend
npm run build

# 2. Verificar build
npm run start  # Testar localmente

# 3. Preparar backend
cd backend
# Assegurar .env de produção configurado
```

### Docker em Produção

```bash
# 1. Criar .env.docker de produção
cp .env.docker.example .env.docker.prod
# Configurar com credenciais de produção

# 2. Build
docker-compose -f docker-compose.prod.yml build

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 4. Verificar
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

---

## 🐛 Troubleshooting

### Scripts não executam

```bash
# Dar permissão de execução
chmod +x setup.sh
chmod +x start.sh
```

### Porta em uso

```bash
# Ver o que está usando porta 8000
sudo lsof -i :8000

# Matar processo
kill -9 PID

# Ou mudar porta no código
# backend/main.py: uvicorn.run(..., port=8001)
```

### MongoDB não conecta

```bash
# Verificar se está rodando
sudo systemctl status mongod

# Iniciar
sudo systemctl start mongod

# Logs
sudo journalctl -u mongod -f

# Ou usar Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### Dependências desatualizadas

```bash
# Backend
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd web/frontend
npm update
# ou
npm install
```

### Hot reload não funciona

**Backend:**
```bash
# Verificar se está usando --reload
python main.py  # Deve ter "reload=True"
```

**Frontend:**
```bash
# Verificar se está em modo dev
npm run dev  # Não npm run start
```

---

## 📝 Manutenção dos Scripts

### Atualizar setup.sh

Se adicionar nova dependência:

```bash
# 1. Adicionar ao requirements.txt ou package.json
# 2. Testar setup.sh
./setup.sh

# 3. Verificar se instala corretamente
```

### Atualizar docker-compose.yml

Se adicionar novo serviço:

```yaml
# 1. Adicionar em docker-compose.yml
  novo-servico:
    image: ...
    # config

# 2. Documentar em DOCKER_GUIA.md

# 3. Testar
docker-compose up -d novo-servico
```

---

## ⚙️ Variáveis de Ambiente

### Backend (.env)

```bash
# Localização
backend/.env

# Variáveis críticas
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET_KEY=...
MERCADOPAGO_ACCESS_TOKEN=...
STRIPE_SECRET_KEY=...
PAYPAL_CLIENT_ID=...
```

### Frontend (.env.local)

```bash
# Localização
web/frontend/.env.local

# Variáveis críticas
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=...
```

### Docker (.env.docker)

```bash
# Localização
.env.docker (raiz do projeto)

# Sobrescreve variáveis de ambos backend e frontend
# Ver .env.docker.example para lista completa
```

---

## 🔐 Segurança dos Scripts

### Nunca commitar

- ❌ `.env`
- ❌ `.env.local`
- ❌ `.env.docker`
- ❌ `logs/`

### Sempre commitar

- ✅ `.env.example`
- ✅ `.env.docker.example`
- ✅ `setup.sh`
- ✅ `start.sh`
- ✅ `docker-compose.yml`

### Proteção de Credenciais

```bash
# Verificar o que será commitado
git status

# Ver se há credenciais
git diff

# Usar git-secrets (recomendado)
git secrets --install
git secrets --register-aws
```

---

## 📚 Documentação Relacionada

### Quick Starts
- [QUICK_START.md](./QUICK_START.md) - Setup geral
- [QUICK_START_PAGAMENTOS.md](./QUICK_START_PAGAMENTOS.md) - Sistema de pagamentos

### Guias Técnicos
- [DOCKER_GUIA.md](./DOCKER_GUIA.md) - Docker completo
- [TESTE_SISTEMA_PAGAMENTOS.md](./TESTE_SISTEMA_PAGAMENTOS.md) - Testes

### Documentação Principal
- [README.md](./README.md) - Visão geral
- [PLANO_COMPLETO_WEB_DESKTOP.md](./PLANO_COMPLETO_WEB_DESKTOP.md) - Especificação

---

## ✅ Checklist de Uso

### Primeira Vez no Projeto

- [ ] Clonar repositório
- [ ] Executar `./setup.sh`
- [ ] Copiar `.env.example` para `.env` (backend e frontend)
- [ ] Configurar variáveis de ambiente
- [ ] Iniciar MongoDB (`sudo systemctl start mongod`)
- [ ] Executar `./start.sh`
- [ ] Acessar http://localhost:3000
- [ ] Criar primeiro usuário admin

### Uso Diário

- [ ] `git pull` (pegar atualizações)
- [ ] `./start.sh` (iniciar sistema)
- [ ] Desenvolver
- [ ] `Ctrl+C` no start.sh (parar)
- [ ] `git add . && git commit -m "..."` (commitar)
- [ ] `git push` (enviar)

### Antes de Fazer PR

- [ ] Rodar `pytest` (backend)
- [ ] Rodar `npm run lint` (frontend)
- [ ] Testar build: `npm run build`
- [ ] Ver logs: sem erros
- [ ] Testar fluxos principais
- [ ] Atualizar documentação se necessário

---

## 💡 Dicas

### Performance

**Backend:**
```bash
# Usar gunicorn com múltiplos workers em produção
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
# Otimizar build
npm run build -- --experimental-profiler
```

### Logs

```bash
# Ver apenas erros
tail -f logs/backend.log | grep ERROR

# Ver apenas warnings
tail -f logs/frontend.log | grep WARN

# Colorir output
tail -f logs/backend.log | grep --color ERROR
```

### Aliases Úteis

Adicione ao `.bashrc` ou `.zshrc`:

```bash
# Atalhos do projeto
alias wbs-setup='cd ~/projeto && ./setup.sh'
alias wbs-start='cd ~/projeto && ./start.sh'
alias wbs-logs='tail -f ~/projeto/logs/*.log'
alias wbs-backend='cd ~/projeto/backend && source venv/bin/activate'
alias wbs-frontend='cd ~/projeto/web/frontend'
```

---

## 🎯 Próximos Scripts a Criar

### Sugestões

1. **test.sh** - Rodar todos os testes
2. **deploy.sh** - Deploy automatizado
3. **backup.sh** - Backup do MongoDB
4. **migrate.sh** - Rodar migrações
5. **seed.sh** - Popular banco com dados de teste

### Contribuindo

Para adicionar novo script:

1. Criar arquivo `.sh`
2. Dar permissão: `chmod +x script.sh`
3. Documentar neste arquivo
4. Testar
5. Commitar

---

**Última atualização:** 19/10/2025 - 23:45

**Dúvidas?** Consulte:
- [DOCKER_GUIA.md](./DOCKER_GUIA.md)
- [README.md](./README.md)
- [QUICK_START.md](./QUICK_START.md)
