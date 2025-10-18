#!/bin/bash

# Script de inicialização do Bot de Pesquisa de Empresas

echo "🤖 Bot de Pesquisa de Empresas"
echo "================================"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado!"
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt --quiet

echo ""
echo "Escolha o modo de execução:"
echo "1) 🌐 Interface Web (Recomendado)"
echo "2) 💻 Terminal (CLI)"
echo ""
read -p "Opção [1]: " choice
choice=${choice:-1}

if [ "$choice" = "1" ]; then
    echo ""
    echo "🚀 Iniciando servidor web..."
    echo "📍 Acesse: http://localhost:5000"
    echo ""
    python app.py
else
    echo ""
    echo "🚀 Iniciando versão CLI..."
    echo ""
    python main.py
fi
