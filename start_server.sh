#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║   🚀 INICIANDO SERVIDOR WHATSAPP BOT      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Erro: app.py não encontrado${NC}"
    echo "Execute este script no diretório do bot"
    exit 1
fi

echo "1️⃣ Verificando ambiente..."

# Verificar DISPLAY
if [ -z "$DISPLAY" ]; then
    echo -e "${YELLOW}⚠️  DISPLAY não configurado, definindo para :0${NC}"
    export DISPLAY=:0
else
    echo -e "${GREEN}✅ DISPLAY: $DISPLAY${NC}"
fi

# Dar permissão X11
echo "2️⃣ Configurando permissões X11..."
if xhost +local:$USER 2>/dev/null 1>&2; then
    echo -e "${GREEN}✅ Permissão X11 concedida${NC}"
else
    echo -e "${YELLOW}⚠️  Não foi possível configurar xhost (pode estar sem X11)${NC}"
fi

# Verificar ambiente virtual
echo "3️⃣ Verificando ambiente virtual..."
if [ -d ".venv" ]; then
    if [ ! -f ".venv/bin/activate" ]; then
        echo -e "${RED}❌ Ambiente virtual corrompido${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Ambiente virtual encontrado${NC}"
    echo "   Ativando..."
    source .venv/bin/activate

    # Verificar se ativou corretamente
    if [ "$VIRTUAL_ENV" != "" ]; then
        echo -e "${GREEN}✅ Ambiente ativado: $VIRTUAL_ENV${NC}"
    else
        echo -e "${RED}❌ Falha ao ativar ambiente${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado em .venv${NC}"
    echo "   Usando Python global..."
fi

# Verificar dependências críticas
echo "4️⃣ Verificando dependências..."

MISSING_DEPS=0

# Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ Flask não instalado${NC}"
    MISSING_DEPS=1
fi

# Flask-SocketIO
if ! python3 -c "import flask_socketio" 2>/dev/null; then
    echo -e "${RED}❌ Flask-SocketIO não instalado${NC}"
    MISSING_DEPS=1
fi

# PyAutoGUI (para WhatsApp)
if ! python3 -c "import pyautogui; pyautogui.size()" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyAutoGUI não funcional (display pode estar indisponível)${NC}"
    echo "   WhatsApp Bot não funcionará até corrigir"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ Dependências faltando!${NC}"
    echo "Instale com: pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}✅ Dependências principais OK${NC}"

# Verificar banco de dados
echo "5️⃣ Verificando banco de dados..."
if [ -f "database/empresas.db" ]; then
    echo -e "${GREEN}✅ Banco de dados encontrado${NC}"

    # Verificar se tem empresas
    EMPRESAS=$(python3 -c "
import sqlite3
conn = sqlite3.connect('database/empresas.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM empresas')
print(cur.fetchone()[0])
conn.close()
" 2>/dev/null)

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $EMPRESAS empresas cadastradas${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Banco de dados será criado na primeira execução${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ TUDO PRONTO!${NC}"
echo ""
echo "Iniciando servidor Flask..."
echo ""
echo "═══════════════════════════════════════════════"
echo ""

# Iniciar servidor
python app.py
