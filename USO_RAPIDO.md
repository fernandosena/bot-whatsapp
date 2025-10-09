# 🚀 Uso Rápido - WhatsApp Bot (Selenium)

## ⚡ Início Rápido (4 passos)

### 1. Preparar ambiente

```bash
cd /home/fernando-sena/Documentos/bot

# Ativar ambiente virtual
source .venv/bin/activate
```

### 2. Iniciar servidor

```bash
python app.py
```

**Saída esperada:**
```
🚀 Servidor web iniciado!
📍 Acesse: http://localhost:5000
```

### 3. Conectar ao WhatsApp

Abra navegador: **http://localhost:5000/whatsapp**

1. **Clique em "📱 Conectar ao WhatsApp"**
2. **Escaneie o QR Code** no navegador Chrome que abriu
3. **Aguarde** até ver: "✅ Conectado ao WhatsApp"

**IMPORTANTE:** Você só precisa fazer isso UMA VEZ! A sessão fica salva.

### 4. Usar interface

Agora você pode enviar mensagens normalmente!

---

## 📋 Primeira Campanha (Teste)

### No navegador:

**⚠️ IMPORTANTE:** Certifique-se de estar conectado (status verde) antes de enviar!

1. **Aba "📤 Enviar Mensagens"**

2. **Buscar empresas:**
   - Marque "Apenas com WhatsApp"
   - Clique "🔍 Buscar"
   - Selecione 1-2 empresas

3. **Preencher:**
   ```
   Nome da Campanha: Teste Inicial

   Mensagem:
   Olá {nome}!

   Este é um teste do sistema de envio.

   Att,
   Equipe
   ```

4. **Configurar:**
   - Delay: 30 segundos

5. **Enviar:**
   - Clique "🚀 Iniciar Envio"
   - Mensagens serão enviadas automaticamente
   - Aguarde o envio

6. **Acompanhar:**
   - Veja progresso em tempo real
   - Log de cada envio
   - Estatísticas

**OBS:** Não feche o navegador Chrome durante o envio!

---

## 🔄 Testar Checkpoint

### Cenário: Pausar e Retomar

1. **Inicie uma campanha** com 5-10 empresas

2. **Após 2-3 envios, clique "⏹️ Parar"**

3. **Vá na aba "📋 Campanhas"**
   - Verá sua campanha pausada
   - Exemplo: "Teste Inicial - 3/10 (30%)"

4. **Clique "🔄 Continuar"**
   - Sistema retoma automaticamente
   - Envia apenas para quem NÃO recebeu
   - Zero duplicatas!

5. **Verifique:**
   - Total de envios = número de empresas
   - Nenhuma recebeu 2x

---

## ⚠️ Status da Conexão

### 🔴 Desconectado
```
❌ Desconectado - Clique em "Conectar ao WhatsApp" para iniciar
```
**O que fazer:** Clique no botão "📱 Conectar ao WhatsApp"

### 🟡 Aguardando Login
```
⏳ Aguardando login - Escaneie o QR Code no navegador
```
**O que fazer:** Abra o WhatsApp no celular e escaneie o QR Code

### 🟢 Conectado
```
✅ Conectado ao WhatsApp - Pronto para enviar mensagens
```
**O que fazer:** Pode enviar mensagens normalmente!

---

## ⚠️ Se o Navegador Não Abrir

### Erro:
```
❌ Erro ao iniciar navegador
```

### Solução:
```bash
# Instalar/Atualizar dependências
pip install --upgrade selenium webdriver-manager

# Reiniciar servidor
python app.py
```

---

## 📊 Ver Campanhas

### Interface:

**Aba "📋 Campanhas"** mostra:

```
┌──────────────────────────────────────┐
│ Promoção Black Friday                │
│ Status: ⏸️ Pausada                    │
│ ████████████░░░░░░░░ 45%             │
│ 45/100 enviados | 2 falhas           │
│ [🔄 Continuar] [📊 Ver Logs]          │
└──────────────────────────────────────┘
```

---

## 💡 Dicas Importantes

### ✅ Faça

- ✅ Use delays de 30-60 segundos
- ✅ Teste com poucas empresas primeiro
- ✅ Dê nomes descritivos às campanhas
- ✅ Personalize mensagens com {nome}, {cidade}
- ✅ Mantenha WhatsApp Web aberto
- ✅ Use "Parar" se precisar interromper

### ❌ Evite

- ❌ Delays muito curtos (< 20s)
- ❌ Mais de 100 mensagens/dia
- ❌ Mensagens genéricas sem personalização
- ❌ Fechar navegador durante envio
- ❌ Enviar para mesma lista 2x sem verificar

---

## 🐛 Problemas Comuns

### 1. "Bot já está em execução"

**Causa:** Tentou iniciar novo envio enquanto outro roda

**Solução:** Aguarde ou clique "Parar" primeiro

### 2. "Nenhuma empresa com WhatsApp encontrada"

**Causa:** Empresas selecionadas não têm WhatsApp

**Solução:** Marque filtro "Apenas com WhatsApp"

### 3. WhatsApp Web não abre

**Causa:** Display não configurado

**Solução:** Execute `./fix_display.sh`

### 4. Mensagem enviada 2x

**Causa:** Criou nova campanha com mesma lista

**Solução:**
- Use "Continuar" em vez de nova campanha
- Ou use campanhas com nomes diferentes

### 5. "Migração não executada"

**Causa:** Banco desatualizado

**Solução:**
```bash
python migrate_whatsapp_campaigns.py
```

---

## 📚 Documentação Completa

- **CAMPANHAS_WHATSAPP.md** - Sistema de campanhas detalhado
- **SOLUCAO_DISPLAY.md** - Resolver problemas de display
- **WHATSAPP_BOT_GUIDE.md** - Guia completo do bot
- **SYSTEM_REQUIREMENTS.md** - Requisitos do sistema

---

## 🎯 Exemplo Completo

```bash
# 1. Preparar
cd /home/fernando-sena/Documentos/bot
source .venv/bin/activate

# 2. Iniciar servidor
python app.py

# 3. Abrir navegador
# http://localhost:5000/whatsapp

# 4. CONECTAR AO WHATSAPP (primeira vez):
#    - Clique "📱 Conectar ao WhatsApp"
#    - Navegador Chrome abrirá
#    - Escaneie QR Code com seu celular
#    - Aguarde status ficar verde ✅

# 5. Enviar mensagens:
#    - Busque empresas (marque "Apenas com WhatsApp")
#    - Selecione 2-3 para teste
#    - Nome: "Teste Sistema"
#    - Mensagem: "Olá {nome}! Teste."
#    - Delay: 30
#    - Clique "🚀 Iniciar Envio"

# 6. Testar Checkpoint:
#    - Após 1-2 envios, clique "⏹️ Parar"
#    - Vá em aba "📋 Campanhas"
#    - Clique "🔄 Continuar"
#    - Veja retomar do ponto exato!

# 7. Verificar:
#    - Aba "📊 Logs" → Ver todos os envios
#    - Aba "📋 Campanhas" → Status completo
#    - Zero duplicatas garantido!

# 8. Próximas vezes:
#    - Pule o passo 4 (já está conectado!)
#    - Inicie direto do passo 5
```

---

## ✅ Checklist Pré-Envio

Antes de cada campanha:

- [ ] Servidor rodando sem erros
- [ ] ✅ **Status VERDE** (Conectado ao WhatsApp) ← IMPORTANTE!
- [ ] Empresas selecionadas têm WhatsApp
- [ ] Mensagem personalizada com variáveis
- [ ] Nome da campanha descritivo
- [ ] Delay adequado (30-60s)
- [ ] Testou com 1-2 empresas primeiro
- [ ] Navegador Chrome aberto (não fechar durante envio)

---

## 🎉 Está Pronto!

Agora você pode:

- ✅ Enviar mensagens em massa
- ✅ Pausar e retomar quando quiser
- ✅ Nunca enviar duplicatas
- ✅ Rastrear todas as campanhas
- ✅ Ver estatísticas completas
- ✅ Recuperar de erros automaticamente

**Bom uso!** 🚀

---

**Última atualização:** Outubro 2025
