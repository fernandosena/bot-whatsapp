#!/bin/bash

# Script de instalação do serviço PTT WhatsApp
# Autor: Bot Assistant
# Data: 2025-10-16

set -e  # Parar em caso de erro

echo "============================================================"
echo "🎤 Instalação do Serviço PTT WhatsApp"
echo "============================================================"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de log
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    log_error "Execute este script no diretório raiz do projeto!"
    exit 1
fi

# 1. Verificar Node.js
echo "📦 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    log_warning "Node.js não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y nodejs npm
    log_success "Node.js instalado!"
else
    NODE_VERSION=$(node --version)
    log_success "Node.js já instalado: $NODE_VERSION"
fi

# 2. Verificar npm
echo ""
echo "📦 Verificando npm..."
if ! command -v npm &> /dev/null; then
    log_error "npm não encontrado!"
    exit 1
else
    NPM_VERSION=$(npm --version)
    log_success "npm instalado: $NPM_VERSION"
fi

# 3. Criar diretório do serviço (se não existir)
echo ""
echo "📁 Verificando estrutura de diretórios..."
if [ ! -d "whatsapp-ptt-service" ]; then
    log_error "Diretório whatsapp-ptt-service não encontrado!"
    exit 1
fi
log_success "Diretório encontrado"

# 4. Instalar dependências Node.js
echo ""
echo "📦 Instalando dependências do serviço PTT..."
cd whatsapp-ptt-service

if [ ! -f "package.json" ]; then
    log_error "package.json não encontrado!"
    exit 1
fi

npm install

if [ $? -eq 0 ]; then
    log_success "Dependências instaladas com sucesso!"
else
    log_error "Erro ao instalar dependências"
    exit 1
fi

cd ..

# 5. Verificar Python
echo ""
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 não encontrado!"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    log_success "Python instalado: $PYTHON_VERSION"
fi

# 6. Criar diretórios necessários
echo ""
echo "📁 Criando diretórios..."
mkdir -p uploads/audio
mkdir -p logs
log_success "Diretórios criados"

# 7. Verificar se PM2 está instalado (opcional)
echo ""
echo "🔧 Verificando PM2 (gerenciador de processos)..."
if ! command -v pm2 &> /dev/null; then
    log_warning "PM2 não instalado (opcional para produção)"
    echo "   Para instalar: npm install -g pm2"
else
    PM2_VERSION=$(pm2 --version)
    log_success "PM2 instalado: $PM2_VERSION"
fi

# 8. Criar script de inicialização
echo ""
echo "📝 Criando script de inicialização..."

cat > start_ptt_service.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando serviço PTT WhatsApp..."

cd whatsapp-ptt-service

# Verificar se já está rodando
if pgrep -f "node.*server.js" > /dev/null; then
    echo "⚠️  Serviço já está rodando!"
    echo "   Para parar: pkill -f 'node.*server.js'"
    exit 1
fi

# Iniciar em segundo plano
nohup node server.js > ../logs/ptt-service.log 2>&1 &

PID=$!
echo "✅ Serviço iniciado! PID: $PID"
echo "📊 Logs: tail -f logs/ptt-service.log"
echo "📍 Status: curl http://localhost:3001/status"
EOF

chmod +x start_ptt_service.sh
log_success "Script criado: ./start_ptt_service.sh"

# 9. Criar script de parada
cat > stop_ptt_service.sh << 'EOF'
#!/bin/bash

echo "🛑 Parando serviço PTT WhatsApp..."

if pgrep -f "node.*server.js" > /dev/null; then
    pkill -f "node.*server.js"
    echo "✅ Serviço parado!"
else
    echo "⚠️  Serviço não está rodando"
fi
EOF

chmod +x stop_ptt_service.sh
log_success "Script criado: ./stop_ptt_service.sh"

# 10. Resumo final
echo ""
echo "============================================================"
echo "✅ Instalação concluída com sucesso!"
echo "============================================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Iniciar o serviço PTT:"
echo "   ./start_ptt_service.sh"
echo ""
echo "2. Iniciar o Flask (em outro terminal):"
echo "   python app.py"
echo ""
echo "3. Acessar a interface:"
echo "   http://localhost:5000/enviar-ptt"
echo ""
echo "4. Escanear o QR Code com seu WhatsApp"
echo ""
echo "5. Enviar seu primeiro PTT!"
echo ""
echo "============================================================"
echo "📚 Documentação: cat README_PTT.md"
echo "📊 Ver logs: tail -f logs/ptt-service.log"
echo "🛑 Parar serviço: ./stop_ptt_service.sh"
echo "============================================================"
echo ""
