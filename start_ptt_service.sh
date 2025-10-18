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
