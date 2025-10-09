#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║   🔧 CORREÇÃO AUTOMÁTICA - DISPLAY        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar DISPLAY
echo "1️⃣ Verificando variável DISPLAY..."
if [ -z "$DISPLAY" ]; then
    echo -e "${RED}❌ DISPLAY não configurado${NC}"
    echo "   Configurando para :0..."
    export DISPLAY=:0
else
    echo -e "${GREEN}✅ DISPLAY = $DISPLAY${NC}"
fi
echo ""

# 2. Dar permissão X11
echo "2️⃣ Concedendo permissão ao X11..."
if xhost +local:$USER 2>/dev/null; then
    echo -e "${GREEN}✅ Permissão X11 concedida${NC}"
else
    echo -e "${YELLOW}⚠️  xhost não disponível ou sem X11${NC}"
fi
echo ""

# 3. Verificar/Instalar tkinter
echo "3️⃣ Verificando python3-tk..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${GREEN}✅ python3-tk já instalado${NC}"
else
    echo -e "${YELLOW}📦 Instalando python3-tk...${NC}"
    sudo apt-get update -qq
    sudo apt-get install -y python3-tk python3-dev
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ python3-tk instalado${NC}"
    else
        echo -e "${RED}❌ Erro ao instalar python3-tk${NC}"
    fi
fi
echo ""

# 4. Testar PyAutoGUI
echo "4️⃣ Testando PyAutoGUI..."
python3 << 'EOF'
import sys
try:
    import pyautogui
    size = pyautogui.size()
    print(f"✅ PyAutoGUI funcionando! Tela: {size}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PyAutoGUI OK${NC}"
    PYAUTOGUI_OK=1
else
    echo -e "${RED}❌ PyAutoGUI com problemas${NC}"
    PYAUTOGUI_OK=0
fi
echo ""

# 5. Verificar pywhatkit
echo "5️⃣ Verificando pywhatkit..."
if python3 -c "import pywhatkit" 2>/dev/null; then
    echo -e "${GREEN}✅ pywhatkit instalado${NC}"
else
    echo -e "${YELLOW}⚠️  pywhatkit não instalado${NC}"
    echo "   Instale com: pip install pywhatkit"
fi
echo ""

# Resumo
echo "═══════════════════════════════════════════════"
echo ""
if [ $PYAUTOGUI_OK -eq 1 ]; then
    echo -e "${GREEN}✅ TUDO PRONTO!${NC}"
    echo ""
    echo "Você pode agora enviar mensagens no WhatsApp Bot."
    echo ""
    echo "Próximos passos:"
    echo "  1. Inicie o servidor: ${YELLOW}python app.py${NC}"
    echo "  2. Acesse: ${YELLOW}http://localhost:5000/whatsapp${NC}"
    echo "  3. Faça login no WhatsApp Web"
    echo "  4. Envie mensagens!"
    echo ""
    echo "💡 Dica: Para não precisar rodar este script toda vez, adicione ao ~/.bashrc:"
    echo "   ${YELLOW}echo 'xhost +local:\$USER 2>/dev/null' >> ~/.bashrc${NC}"
else
    echo -e "${RED}❌ AINDA HÁ PROBLEMAS${NC}"
    echo ""
    echo "Verifique:"
    echo "  1. Você está em um ambiente com interface gráfica?"
    echo "  2. X11 está rodando? (ps aux | grep X)"
    echo "  3. Não está via SSH sem X11 forwarding?"
    echo ""
    echo "Consulte: ${YELLOW}SOLUCAO_DISPLAY.md${NC}"
fi
echo ""
