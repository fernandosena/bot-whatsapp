# 🚀 Quick Start - WhatsApp Bot

## Instalação em 3 Passos

### 1️⃣ Instalar Dependências

```bash
source .venv/bin/activate  # Ativar ambiente virtual
pip install pywhatkit pyautogui
```

### 2️⃣ Configurar Templates

```bash
python setup_whatsapp.py
```

Este script irá:
- ✅ Verificar dependências
- ✅ Criar tabelas no banco de dados
- ✅ Adicionar 5 templates padrão
- ✅ Mostrar estatísticas do sistema

### 3️⃣ Iniciar Servidor

```bash
python app.py
```

Acesse: **http://localhost:5000/whatsapp**

---

## 📱 Usando o Bot

### Antes de Começar

1. **Abra o WhatsApp Web**: https://web.whatsapp.com
2. **Escaneie o QR Code** com seu celular
3. **Mantenha a aba aberta** durante os envios

### Passo a Passo

#### 1. Selecionar Empresas

- Use os filtros (setor, cidade, busca)
- Marque "Apenas com WhatsApp"
- Clique em "🔍 Buscar"
- Selecione as empresas desejadas

#### 2. Escolher/Criar Mensagem

**Opção A: Usar Template**
- Selecione um template do dropdown
- A mensagem será carregada automaticamente

**Opção B: Mensagem Personalizada**
- Digite sua mensagem no campo de texto
- Use variáveis: `{nome}`, `{cidade}`, `{setor}`

**Exemplo:**
```
Olá, {nome}!

Somos especialistas em soluções digitais para {setor} em {cidade}.

Podemos conversar?
```

#### 3. Configurar Delay

- Recomendado: **30-60 segundos**
- Mínimo: 10 segundos
- Evite delays curtos para não ser bloqueado

#### 4. Enviar

- Clique em "🚀 Iniciar Envio"
- Acompanhe o progresso em tempo real
- **Não feche o navegador!**

---

## 🎯 Dicas Importantes

### ✅ Faça

- ✅ Use delays de 30-60 segundos
- ✅ Teste com poucos contatos primeiro
- ✅ Personalize as mensagens
- ✅ Respeite horário comercial (8h-18h)
- ✅ Mantenha WhatsApp Web aberto
- ✅ Identifique-se claramente

### ❌ Evite

- ❌ Enviar SPAM
- ❌ Delays muito curtos (< 20s)
- ❌ Mais de 100 mensagens/dia
- ❌ Mensagens genéricas sem personalização
- ❌ Enviar fora do horário comercial
- ❌ Fechar navegador durante envio

---

## 📝 Templates Padrão

Após executar `setup_whatsapp.py`, você terá 5 templates:

1. **Apresentação Comercial** - Primeira abordagem
2. **Follow-up** - Retomar contato
3. **Pesquisa de Mercado** - Coletar feedback
4. **Oferta Especial** - Divulgar promoções
5. **Convite para Evento** - Convidar para eventos

Edite conforme sua necessidade!

---

## 🔧 Solução Rápida de Problemas

### Bot não envia mensagens?

1. Verifique se está logado no WhatsApp Web
2. Aumente o delay para 30-60 segundos
3. Teste com 1-2 contatos primeiro
4. Reinicie o servidor

### Erro "Tkinter not found"?

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk
```

### WhatsApp bloqueou?

1. Pare os envios imediatamente
2. Aguarde 24-48 horas
3. Reduza volume e aumente delays
4. Revise o conteúdo das mensagens

---

## 📊 Monitoramento

### Ver Estatísticas

Acesse a aba "📊 Logs" para ver:
- Total de envios
- Taxa de sucesso/falha
- Histórico detalhado com timestamps

### Via API

```bash
# Logs
curl http://localhost:5000/api/whatsapp/logs

# Estatísticas
curl http://localhost:5000/api/whatsapp/stats
```

---

## 🎓 Próximos Passos

1. ✅ Teste com 5-10 contatos
2. ✅ Analise os resultados
3. ✅ Ajuste mensagens conforme feedback
4. ✅ Crie seus próprios templates
5. ✅ Escale gradualmente (20-50-100 mensagens/dia)

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **[WHATSAPP_BOT_GUIDE.md](WHATSAPP_BOT_GUIDE.md)** - Guia completo
- **[README.md](README.md)** - Documentação geral do bot

---

## ⚠️ Aviso Legal

- Use com responsabilidade
- Não envie SPAM
- Respeite privacidade (LGPD)
- WhatsApp pode bloquear por uso indevido
- Sem garantias - use por sua conta e risco

---

**Desenvolvido com ❤️ para automação de marketing**
