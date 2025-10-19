#!/bin/bash

# Script para iniciar MongoDB com Docker
# Uso: ./start-mongodb.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🐳 Iniciando MongoDB com Docker..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    echo "Inicie o Docker primeiro:"
    echo "  sudo systemctl start docker"
    exit 1
fi

# Verificar se MongoDB já está rodando
if docker ps --format '{{.Names}}' | grep -q mongo; then
    echo -e "${GREEN}✅ MongoDB já está rodando${NC}"
    CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep mongo | head -1)
    echo "Container: $CONTAINER_NAME"
else
    echo "Iniciando MongoDB..."

    # Verificar se docker-compose.yml existe
    if [ -f "docker-compose.yml" ]; then
        docker compose up -d mongodb
        sleep 3

        if docker ps --format '{{.Names}}' | grep -q mongo; then
            echo -e "${GREEN}✅ MongoDB iniciado com sucesso (docker compose)${NC}"
        else
            echo -e "${RED}❌ Erro ao iniciar MongoDB${NC}"
            echo "Ver logs: docker compose logs mongodb"
            exit 1
        fi
    else
        # Iniciar container standalone
        echo "docker-compose.yml não encontrado. Iniciando container standalone..."

        docker run -d \
            --name mongodb \
            -p 27017:27017 \
            -v mongodb_data:/data/db \
            mongo:latest

        sleep 3

        if docker ps --format '{{.Names}}' | grep -q mongodb; then
            echo -e "${GREEN}✅ MongoDB iniciado com sucesso (container standalone)${NC}"
        else
            echo -e "${RED}❌ Erro ao iniciar MongoDB${NC}"
            echo "Ver logs: docker logs mongodb"
            exit 1
        fi
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Mostrar containers rodando
docker ps --filter "name=mongo" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ MongoDB disponível em: mongodb://localhost:27017"
echo ""
echo "Comandos úteis:"
echo "  Ver logs:    docker logs -f \$(docker ps --filter 'name=mongo' -q)"
echo "  Parar:       docker stop \$(docker ps --filter 'name=mongo' -q)"
echo "  Acessar:     docker exec -it \$(docker ps --filter 'name=mongo' -q) mongosh"
echo ""
