#!/bin/bash

echo "🛑 Parando serviço PTT WhatsApp..."

if pgrep -f "node.*server.js" > /dev/null; then
    pkill -f "node.*server.js"
    echo "✅ Serviço parado!"
else
    echo "⚠️  Serviço não está rodando"
fi
