#!/bin/bash

##############################################
# WhatsApp Business SaaS - Setup Script
# Autor: Desenvolvimento
# Data: 19/10/2025
##############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  WhatsApp Business SaaS - Setup${NC}"
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header

# 1. Check Prerequisites
print_step "Verificando pré-requisitos..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION instalado"
else
    print_error "Python 3.11+ não encontrado. Por favor, instale Python 3.11 ou superior."
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION instalado"
else
    print_error "Node.js não encontrado. Por favor, instale Node.js 18+."
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION instalado"
else
    print_error "npm não encontrado."
    exit 1
fi

# Check MongoDB
if command_exists mongod; then
    print_success "MongoDB instalado"
elif command_exists docker; then
    print_warning "MongoDB não encontrado localmente. Docker disponível para executar MongoDB em container."
else
    print_error "MongoDB não encontrado e Docker não disponível. Instale MongoDB ou Docker."
    exit 1
fi

echo ""

# 2. Setup Backend
print_step "Configurando Backend..."

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_step "Criando ambiente virtual Python..."
    python3 -m venv venv
    print_success "Ambiente virtual criado"
else
    print_success "Ambiente virtual já existe"
fi

# Activate virtual environment
print_step "Ativando ambiente virtual..."
source venv/bin/activate

# Install dependencies
print_step "Instalando dependências do backend..."
pip install -r requirements.txt -q
print_success "Dependências do backend instaladas"

# Setup .env if it doesn't exist
if [ ! -f ".env" ]; then
    print_step "Criando arquivo .env a partir do .env.example..."
    cp .env.example .env
    print_warning "IMPORTANTE: Configure as variáveis de ambiente em backend/.env"
    print_warning "  - Tokens de pagamento (Mercado Pago, Stripe, PayPal)"
    print_warning "  - Secrets do JWT"
    print_warning "  - Configurações do MongoDB"
else
    print_success "Arquivo .env já existe"
fi

cd ..
echo ""

# 3. Setup Frontend
print_step "Configurando Frontend..."

cd web/frontend

# Install dependencies
print_step "Instalando dependências do frontend..."
npm install --silent
print_success "Dependências do frontend instaladas"

# Setup .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_step "Criando arquivo .env.local..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=$(openssl rand -base64 32)
EOF
    print_success "Arquivo .env.local criado"
else
    print_success "Arquivo .env.local já existe"
fi

cd ../..
echo ""

# 4. MongoDB Setup
print_step "Verificando MongoDB..."

if pgrep -x mongod > /dev/null; then
    print_success "MongoDB já está rodando"
elif systemctl is-active --quiet mongod 2>/dev/null; then
    print_success "MongoDB está ativo (systemd)"
else
    print_warning "MongoDB não está rodando"
    print_warning "Inicie com: sudo systemctl start mongod"
    print_warning "Ou use Docker: docker run -d -p 27017:27017 --name mongodb mongo:7.0"
fi

echo ""

# 5. Summary
print_header
echo -e "${GREEN}✓ Setup concluído com sucesso!${NC}"
echo ""
echo "Próximos passos:"
echo ""
echo "1. Configure as variáveis de ambiente:"
echo "   ${YELLOW}backend/.env${NC}"
echo ""
echo "2. Inicie o MongoDB (se ainda não estiver rodando):"
echo "   ${YELLOW}sudo systemctl start mongod${NC}"
echo "   ou"
echo "   ${YELLOW}docker run -d -p 27017:27017 --name mongodb mongo:7.0${NC}"
echo ""
echo "3. Inicie o backend:"
echo "   ${YELLOW}cd backend${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python main.py${NC}"
echo ""
echo "4. Em outro terminal, inicie o frontend:"
echo "   ${YELLOW}cd web/frontend${NC}"
echo "   ${YELLOW}npm run dev${NC}"
echo ""
echo "5. Acesse o sistema:"
echo "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo "   Backend:  ${BLUE}http://localhost:8000${NC}"
echo "   Swagger:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Para um início rápido do sistema de pagamentos, leia:"
echo "   ${YELLOW}QUICK_START_PAGAMENTOS.md${NC}"
echo ""
print_success "Bom desenvolvimento! 🚀"
echo ""
