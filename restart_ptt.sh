#!/bin/bash

# Script para reiniciar o serviço PTT do WhatsApp
# Uso: ./restart_ptt.sh

echo "🔄 Reiniciando Serviço PTT..."
echo ""

# Parar processo existente
echo "1️⃣ Parando processo existente..."
pkill -f "node.*whatsapp-ptt-service/server.js" 2>/dev/null || true
sleep 2

# Limpar sessão (opcional - descomente se quiser forçar novo login)
# echo "2️⃣ Limpando sessão antiga..."
# rm -rf whatsapp-ptt-service/auth_baileys/

echo "2️⃣ Verificando diretórios..."
mkdir -p logs
mkdir -p whatsapp-ptt-service/uploads

# Reiniciar serviço
echo "3️⃣ Iniciando serviço PTT..."
cd "$(dirname "$0")"
nohup node whatsapp-ptt-service/server.js > logs/ptt-service.log 2>&1 &

PID=$!
echo "✅ Serviço PTT iniciado (PID: $PID)"
echo ""

# Aguardar inicialização
sleep 3

# Verificar status
echo "4️⃣ Verificando status..."
STATUS=$(curl -s http://localhost:3001/status 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Serviço PTT está rodando!"
    echo ""
    echo "📊 Status: $STATUS"
    echo ""
    echo "📍 Acesse para escanear QR Code:"
    echo "   http://localhost:5000/enviar-ptt"
    echo ""
    echo "📄 Ver logs:"
    echo "   tail -f logs/ptt-service.log"
else
    echo "❌ Erro: Serviço não está respondendo"
    echo "   Verifique os logs: tail -f logs/ptt-service.log"
fi

echo ""
echo "✅ Reinicialização concluída!"
