#!/bin/bash

##############################################
# WhatsApp Business SaaS - Start Script
# Inicia backend e frontend simultaneamente
# Autor: Desenvolvimento
# Data: 19/10/2025
##############################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  WhatsApp Business SaaS - Iniciando${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Encerrando serviços...${NC}"

    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_success "Backend encerrado"
    fi

    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "Frontend encerrado"
    fi

    echo ""
    print_success "Serviços encerrados. Até logo! 👋"
    exit 0
}

# Setup trap for Ctrl+C
trap cleanup SIGINT SIGTERM

print_header

# Check if MongoDB is running
print_step "Verificando MongoDB..."
if pgrep -x mongod > /dev/null || systemctl is-active --quiet mongod 2>/dev/null; then
    print_success "MongoDB está rodando"
else
    print_warning "MongoDB não está rodando!"
    echo ""
    echo "Inicie o MongoDB primeiro:"
    echo "  ${YELLOW}sudo systemctl start mongod${NC}"
    echo "  ou"
    echo "  ${YELLOW}docker run -d -p 27017:27017 --name mongodb mongo:7.0${NC}"
    echo ""
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Start Backend
print_step "Iniciando Backend..."
cd backend

if [ ! -d "venv" ]; then
    print_error "Ambiente virtual não encontrado. Execute ./setup.sh primeiro."
    exit 1
fi

# Activate virtual environment and start backend in background
source venv/bin/activate
python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a bit and check if backend started
sleep 3
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend iniciado (PID: $BACKEND_PID)"
    print_info "Logs: logs/backend.log"
else
    print_error "Falha ao iniciar backend. Verifique logs/backend.log"
    exit 1
fi

cd ..
echo ""

# Start Frontend
print_step "Iniciando Frontend..."
cd web/frontend

npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait a bit and check if frontend started
sleep 5
if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend iniciado (PID: $FRONTEND_PID)"
    print_info "Logs: logs/frontend.log"
else
    print_error "Falha ao iniciar frontend. Verifique logs/frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

cd ../..
echo ""

# Success message
print_header
echo -e "${GREEN}✓ Sistema iniciado com sucesso!${NC}"
echo ""
echo "Serviços rodando:"
echo "  ${CYAN}Frontend:${NC}  http://localhost:3000"
echo "  ${CYAN}Backend:${NC}   http://localhost:8000"
echo "  ${CYAN}Swagger:${NC}   http://localhost:8000/docs"
echo ""
echo "PIDs dos processos:"
echo "  ${CYAN}Backend:${NC}   $BACKEND_PID"
echo "  ${CYAN}Frontend:${NC}  $FRONTEND_PID"
echo ""
echo "Logs em tempo real:"
echo "  ${YELLOW}tail -f logs/backend.log${NC}"
echo "  ${YELLOW}tail -f logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar todos os serviços${NC}"
echo ""

# Keep script running
while true; do
    # Check if processes are still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        print_error "Backend parou inesperadamente!"
        print_info "Verifique logs/backend.log"
        cleanup
    fi

    if ! ps -p $FRONTEND_PID > /dev/null; then
        print_error "Frontend parou inesperadamente!"
        print_info "Verifique logs/frontend.log"
        cleanup
    fi

    sleep 5
done
