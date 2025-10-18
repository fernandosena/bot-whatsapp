#!/bin/bash

# Script para limpar sessão PTT e forçar novo login
# Uso: ./clear_ptt_session.sh

echo "🧹 Limpando Sessão PTT do WhatsApp..."
echo ""

# Parar processo existente
echo "1️⃣ Parando serviço PTT..."
pkill -f "node.*whatsapp-ptt-service/server.js" 2>/dev/null || true
sleep 2

# Limpar sessão
echo "2️⃣ Removendo sessão antiga..."
if [ -d "whatsapp-ptt-service/auth_baileys" ]; then
    rm -rf whatsapp-ptt-service/auth_baileys/
    echo "   ✅ Sessão removida"
else
    echo "   ℹ️ Nenhuma sessão encontrada"
fi

# Limpar uploads temporários
echo "3️⃣ Limpando arquivos temporários..."
if [ -d "whatsapp-ptt-service/uploads" ]; then
    rm -f whatsapp-ptt-service/uploads/*
    echo "   ✅ Arquivos temporários removidos"
fi

echo ""
echo "✅ Sessão limpa com sucesso!"
echo ""
echo "🚀 Próximos passos:"
echo "   1. Execute: node whatsapp-ptt-service/server.js"
echo "   2. Acesse: http://localhost:5000/enviar-ptt"
echo "   3. Escaneie o novo QR Code"
echo ""
