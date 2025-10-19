# 🚀 Como Iniciar a Aplicação (com Docker)

## ⚡ Método Mais Rápido (2 comandos)

```bash
# 1. Iniciar MongoDB (Docker)
./start-mongodb.sh

# 2. Iniciar Backend (Python)
cd backend
./start.sh
```

**Pronto!** Aplicação rodando em http://localhost:8000

---

## 📝 Passo a Passo Detalhado

### 1️⃣ Iniciar MongoDB com Docker

```bash
cd /home/fernando-sena/Documentos/bot

# Opção A: Usar script automático (RECOMENDADO)
./start-mongodb.sh

# Opção B: Docker Compose manual
docker-compose up -d mongodb

# Opção C: Docker run manual
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

**Verificar se MongoDB está rodando:**
```bash
docker ps | grep mongo
```

### 2️⃣ Iniciar Backend (FastAPI)

```bash
cd backend

# Usar script automático (RECOMENDADO)
./start.sh

# OU manual:
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Verificar se Está Funcionando

**Abrir no navegador:**
- http://localhost:8000/docs (Swagger)
- http://localhost:8000/health (Health Check)

**Ou testar no terminal:**
```bash
curl http://localhost:8000/health
```

---

## 🛑 Parar a Aplicação

### Parar Backend
```
CTRL + C (no terminal onde está rodando)
```

### Parar MongoDB
```bash
# Se usou docker-compose
docker-compose stop mongodb

# Se usou docker run
docker stop mongodb
```

---

## 🐛 Problemas Comuns

### "Docker não está rodando"
```bash
sudo systemctl start docker
sudo systemctl status docker
```

### "Porta 27017 em uso"
```bash
# Ver o que está usando
sudo lsof -i :27017

# Parar MongoDB local (se tiver)
sudo systemctl stop mongod
```

### "Porta 8000 em uso"
```bash
# Matar processo
sudo lsof -i :8000
kill -9 PID
```

### "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 Documentação Completa

- **COMO_INICIAR.md** - Guia completo com todos os detalhes
- **INICIAR_COM_DOCKER.md** - Guia específico para Docker
- **QUICK_WINS_IMPLEMENTADOS.md** - O que foi implementado

---

## 🎯 URLs Importantes

| Serviço | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## ✅ Checklist

- [ ] Docker rodando
- [ ] MongoDB iniciado (Docker)
- [ ] Backend iniciado (Python)
- [ ] Health check passou
- [ ] Swagger acessível

---

**Tudo certo!** Agora você pode começar a testar a API! 🎉
