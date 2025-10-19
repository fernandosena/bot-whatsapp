#!/bin/bash

# Script de Inicialização do WhatsApp Business SaaS API
# Uso: ./start.sh

echo "🚀 Iniciando WhatsApp Business SaaS API..."

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se estamos na pasta correta
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Erro: main.py não encontrado${NC}"
    echo "Execute este script da pasta backend/"
    exit 1
fi

# Verificar se MongoDB está rodando
echo "Verificando MongoDB..."

# Verificar se MongoDB está rodando (systemctl ou processo)
if systemctl is-active --quiet mongod 2>/dev/null; then
    echo -e "${GREEN}✅ MongoDB rodando (systemctl)${NC}"
elif pgrep -x mongod > /dev/null; then
    echo -e "${GREEN}✅ MongoDB rodando (processo)${NC}"
# Verificar se está rodando no Docker
elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q mongo; then
    echo -e "${GREEN}✅ MongoDB rodando (Docker)${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB não está rodando${NC}"

    # Verificar se Docker está disponível
    if command -v docker &> /dev/null; then
        echo "Tentando iniciar MongoDB com Docker..."

        # Verificar se container mongodb existe mas está parado
        if docker ps -a --format '{{.Names}}' | grep -q '^mongodb$'; then
            echo "Container 'mongodb' encontrado. Iniciando..."
            docker start mongodb
            sleep 3

            if docker ps --format '{{.Names}}' | grep -q '^mongodb$'; then
                echo -e "${GREEN}✅ MongoDB iniciado com sucesso (Docker)${NC}"
            else
                echo -e "${RED}❌ Erro ao iniciar container mongodb${NC}"
                echo "Verifique os logs: docker logs mongodb"
                exit 1
            fi
        else
            # Tentar com docker-compose
            if [ -f "../docker-compose.yml" ]; then
                echo "Usando docker-compose..."
                cd ..
                docker-compose up -d mongodb
                cd backend
                sleep 3

                if docker ps --format '{{.Names}}' | grep -q mongo; then
                    echo -e "${GREEN}✅ MongoDB iniciado com sucesso (docker-compose)${NC}"
                else
                    echo -e "${RED}❌ Erro ao iniciar MongoDB com docker-compose${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}❌ MongoDB não encontrado${NC}"
                echo ""
                echo "Opções para iniciar MongoDB:"
                echo ""
                echo "1. Docker Compose (Recomendado):"
                echo "   cd /home/fernando-sena/Documentos/bot"
                echo "   docker-compose up -d mongodb"
                echo ""
                echo "2. Docker container manual:"
                echo "   docker run -d --name mongodb -p 27017:27017 mongo:latest"
                echo ""
                echo "3. Systemctl (se instalado localmente):"
                echo "   sudo systemctl start mongod"
                echo ""
                exit 1
            fi
        fi
    else
        echo -e "${RED}❌ Docker não está disponível${NC}"
        echo "Instale o Docker ou MongoDB localmente"
        exit 1
    fi
fi

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado${NC}"
    echo "Criando ambiente virtual..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao criar ambiente virtual${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
fi

# Ativar venv
echo "Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao ativar ambiente virtual${NC}"
    exit 1
fi

# Verificar se requirements instalados
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependências não instaladas${NC}"
    echo "Instalando dependências..."
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependências instaladas${NC}"
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"

    if [ -f ".env.example" ]; then
        echo "Copiando .env.example para .env..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Configure o arquivo .env antes de prosseguir${NC}"
        echo ""
        echo "Configurações mínimas necessárias:"
        echo "  - MONGODB_URI"
        echo "  - SECRET_KEY (use: python -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo ""
        read -p "Deseja continuar mesmo assim? (s/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    else
        echo -e "${RED}❌ .env.example não encontrado${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
fi

# Verificar porta 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 8000 já está em uso${NC}"
    read -p "Deseja parar o processo existente? (s/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        PID=$(lsof -t -i:8000)
        kill -9 $PID
        echo -e "${GREEN}✅ Processo anterior finalizado${NC}"
        sleep 1
    else
        echo "Use outra porta: uvicorn main:app --reload --port 8001"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}▶️  Iniciando servidor FastAPI...${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "API:          http://localhost:8000"
echo "Swagger Docs: http://localhost:8000/docs"
echo "ReDoc:        http://localhost:8000/redoc"
echo "Health:       http://localhost:8000/health"
echo ""
echo -e "${YELLOW}Pressione CTRL+C para parar o servidor${NC}"
echo ""

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
