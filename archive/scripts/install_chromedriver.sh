#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║   🔧 INSTALAÇÃO DO CHROMEDRIVER           ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar Chrome
echo "1️⃣ Verificando Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    echo -e "${RED}❌ Google Chrome não encontrado${NC}"
    echo ""
    echo "Instale o Google Chrome primeiro:"
    echo "  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    echo "  sudo dpkg -i google-chrome-stable_current_amd64.deb"
    echo "  sudo apt-get install -f"
    exit 1
fi

CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d. -f1)
echo -e "${GREEN}✅ Chrome ${CHROME_VERSION} encontrado${NC}"
echo ""

# 2. Baixar ChromeDriver compatível
echo "2️⃣ Baixando ChromeDriver compatível..."

# URL do ChromeDriver para a versão do Chrome
DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR}")

if [ -z "$DRIVER_VERSION" ]; then
    echo -e "${RED}❌ Não foi possível determinar a versão do ChromeDriver${NC}"
    echo "Tentando versão alternativa..."

    # Tentar API antiga
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}")

    if [ -z "$DRIVER_VERSION" ]; then
        echo -e "${RED}❌ Erro ao obter versão do ChromeDriver${NC}"
        echo ""
        echo "Solução alternativa:"
        echo "  pip install --upgrade webdriver-manager"
        echo "  O sistema tentará baixar automaticamente quando conectar"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Versão do ChromeDriver: ${DRIVER_VERSION}${NC}"

# URL de download
DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip"

echo "Baixando de: ${DOWNLOAD_URL}"

# Criar diretório temporário
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Baixar
if ! wget -q --show-progress "$DOWNLOAD_URL" -O chromedriver.zip; then
    echo -e "${RED}❌ Erro ao baixar ChromeDriver${NC}"

    # Tentar URL antiga
    echo "Tentando URL alternativa..."
    DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"

    if ! wget -q --show-progress "$DOWNLOAD_URL" -O chromedriver.zip; then
        echo -e "${RED}❌ Erro ao baixar de ambas as URLs${NC}"
        rm -rf "$TMP_DIR"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Download concluído${NC}"
echo ""

# 3. Extrair
echo "3️⃣ Extraindo arquivo..."
if ! unzip -q chromedriver.zip; then
    echo -e "${RED}❌ Erro ao extrair${NC}"
    rm -rf "$TMP_DIR"
    exit 1
fi

# Encontrar o executável
DRIVER_PATH=$(find . -name "chromedriver" -type f | head -1)

if [ -z "$DRIVER_PATH" ]; then
    echo -e "${RED}❌ ChromeDriver não encontrado no arquivo${NC}"
    rm -rf "$TMP_DIR"
    exit 1
fi

echo -e "${GREEN}✅ Extraído com sucesso${NC}"
echo ""

# 4. Instalar
echo "4️⃣ Instalando ChromeDriver..."

# Remover versão antiga se existir
sudo rm -f /usr/local/bin/chromedriver

# Copiar novo
sudo cp "$DRIVER_PATH" /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

echo -e "${GREEN}✅ Instalado em /usr/local/bin/chromedriver${NC}"
echo ""

# 5. Verificar
echo "5️⃣ Verificando instalação..."
INSTALLED_VERSION=$(/usr/local/bin/chromedriver --version 2>&1 | head -1)
echo -e "${GREEN}✅ ${INSTALLED_VERSION}${NC}"
echo ""

# Limpar
rm -rf "$TMP_DIR"

echo "═══════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo ""
echo "ChromeDriver instalado com sucesso!"
echo ""
echo "Próximos passos:"
echo "  1. Reinicie o servidor: ${YELLOW}python app.py${NC}"
echo "  2. Acesse: ${YELLOW}http://localhost:5000/whatsapp${NC}"
echo "  3. Clique em '📱 Conectar ao WhatsApp'"
echo ""
