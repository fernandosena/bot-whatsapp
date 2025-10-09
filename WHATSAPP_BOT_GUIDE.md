# 💬 Guia do WhatsApp Bot - Disparador de Mensagens

## 📋 Índice
1. [Requisitos](#requisitos)
2. [Instalação](#instalação)
3. [Como Usar](#como-usar)
4. [Templates de Mensagens](#templates-de-mensagens)
5. [Logs e Monitoramento](#logs-e-monitoramento)
6. [Boas Práticas](#boas-práticas)
7. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 Requisitos

### Requisitos do Sistema
- Python 3.8 ou superior
- Google Chrome instalado
- Conexão com internet estável
- WhatsApp Web acessível

### Bibliotecas Python
Todas as dependências estão listadas em `requirements.txt`:
- `pywhatkit` - Envio de mensagens via WhatsApp Web
- `pyautogui` - Automação de interface
- Flask e Flask-SocketIO - API e comunicação em tempo real

---

## 🚀 Instalação

### 1. Instalar Dependências

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar novas dependências
pip install pywhatkit pyautogui

# Ou instalar todas as dependências
pip install -r requirements.txt
```

### 2. Migrar Banco de Dados

O bot criará automaticamente as novas tabelas necessárias:
- `message_templates` - Templates de mensagens
- `whatsapp_logs` - Logs de envio

```bash
python app.py
```

---

## 📱 Como Usar

### 1. Iniciar o Servidor

```bash
python app.py
```

Acesse: **http://localhost:5000/whatsapp**

### 2. Preparar WhatsApp Web

**IMPORTANTE:** Antes de iniciar os envios:

1. Abra o WhatsApp Web em seu navegador: https://web.whatsapp.com
2. Escaneie o QR Code com seu celular
3. Mantenha a sessão ativa
4. **Mantenha o WhatsApp Web aberto durante os envios**

### 3. Selecionar Empresas

1. **Filtrar Empresas:**
   - Use os filtros de busca, setor e cidade
   - Marque "Apenas com WhatsApp" para ver só empresas com número
   - Clique em "🔍 Buscar"

2. **Selecionar Destinatários:**
   - Marque individualmente as empresas desejadas
   - Ou use "Selecionar Todos" para marcar todas de uma vez

### 4. Criar/Escolher Mensagem

#### Opção A: Usar Template Existente
1. Selecione um template no dropdown
2. A mensagem será carregada automaticamente

#### Opção B: Escrever Mensagem Personalizada
Digite sua mensagem no campo de texto.

**Variáveis disponíveis:**
- `{nome}` - Nome da empresa
- `{cidade}` - Cidade da empresa
- `{setor}` - Setor da empresa
- `{telefone}` - Telefone
- `{email}` - Email
- `{endereco}` - Endereço

**Exemplo:**
```
Olá, {nome}!

Somos especialistas em soluções digitais para {setor} em {cidade}.

Gostaríamos de apresentar nossos serviços que podem ajudar a aumentar suas vendas.

Podemos agendar uma conversa?
```

### 5. Configurar Delay

- **Recomendado:** 30-60 segundos entre envios
- **Mínimo:** 10 segundos
- **Máximo:** 300 segundos (5 minutos)

⚠️ **Importante:** Delays menores podem resultar em bloqueio temporário pelo WhatsApp.

### 6. Iniciar Envio

1. Clique em "🚀 Iniciar Envio"
2. O bot abrirá automaticamente o WhatsApp Web para cada envio
3. Acompanhe o progresso em tempo real
4. **NÃO FECHE O NAVEGADOR** durante o processo

### 7. Monitorar Progresso

A interface mostra em tempo real:
- **Barra de progresso** - Percentual concluído
- **Estatísticas:**
  - Total de envios
  - Enviados com sucesso
  - Falhas
- **Log detalhado** - Status de cada envio

---

## 📝 Templates de Mensagens

### Criar Template

1. Acesse a aba "📝 Templates"
2. Preencha:
   - **Nome:** Identificação do template
   - **Mensagem:** Conteúdo (use variáveis)
   - **Descrição:** Informações adicionais (opcional)
3. Clique em "💾 Salvar Template"

### Usar Template

1. Na aba "📤 Enviar Mensagens"
2. Selecione o template desejado no dropdown
3. A mensagem será carregada automaticamente
4. Você pode editá-la antes de enviar

### Exemplos de Templates

#### Template: Apresentação Comercial
```
Olá, {nome}!

Somos a [Sua Empresa] e oferecemos soluções em [seu serviço] para empresas do setor de {setor}.

Notamos que vocês estão em {cidade} e gostaríamos de conhecer melhor suas necessidades.

Podemos agendar uma conversa rápida?

Atenciosamente,
[Seu Nome]
```

#### Template: Pesquisa de Satisfação
```
Olá, {nome}!

Estamos realizando uma pesquisa com empresas de {setor} em {cidade}.

Gostaríamos de conhecer sua opinião sobre [assunto].

Você teria 5 minutos para responder algumas perguntas?
```

#### Template: Oferta Especial
```
🎉 Promoção Especial para {nome}!

Estamos com uma oferta exclusiva para empresas de {setor} em {cidade}.

[Descreva a oferta]

Válido até [data].

Tem interesse em saber mais?
```

---

## 📊 Logs e Monitoramento

### Ver Logs

1. Acesse a aba "📊 Logs"
2. Visualize:
   - Total de envios realizados
   - Taxa de sucesso/falha
   - Detalhes de cada envio com timestamp

### Estatísticas

- **Total:** Quantidade total de mensagens enviadas
- **Sucessos:** Mensagens entregues com sucesso
- **Falhas:** Tentativas que falharam

### Exportar Logs

Os logs ficam salvos no banco de dados e podem ser consultados via API:

```bash
curl http://localhost:5000/api/whatsapp/logs?limit=100
```

---

## ✅ Boas Práticas

### 1. Respeite Limites do WhatsApp

- **Não envie SPAM**
- Use delays adequados (30-60s recomendado)
- Não envie para números desconhecidos
- Respeite horário comercial (8h-18h)
- Máximo recomendado: 50-100 mensagens por dia

### 2. Personalize as Mensagens

- Use variáveis para personalizar
- Seja cordial e profissional
- Identifique-se claramente
- Ofereça opção de opt-out

### 3. Monitore os Resultados

- Acompanhe taxa de resposta
- Analise logs regularmente
- Ajuste estratégia conforme necessário

### 4. Segurança e Privacidade

- Não compartilhe dados sensíveis
- Respeite a LGPD
- Mantenha backup dos logs
- Use senha forte no servidor

### 5. Manutenção da Sessão WhatsApp

- Mantenha o WhatsApp Web logado
- Não saia da conta durante envios
- Verifique conexão antes de iniciar
- Teste com poucos contatos primeiro

---

## 🔧 Solução de Problemas

### Problema: "Bot já está em execução"

**Solução:**
1. Aguarde o envio atual terminar
2. Ou clique em "⏹️ Parar" para cancelar
3. Reinicie o servidor se necessário

### Problema: Mensagens não estão sendo enviadas

**Possíveis causas:**
1. **WhatsApp Web não está logado**
   - Solução: Faça login no WhatsApp Web

2. **Navegador bloqueado**
   - Solução: Permita que o bot controle o navegador

3. **Números inválidos**
   - Solução: Verifique formato do número (+55XXXXXXXXXXX)

4. **Delay muito curto**
   - Solução: Aumente o delay para 30-60 segundos

### Problema: Erro "Tkinter not found"

**Solução:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Problema: Bot está muito lento

**Solução:**
1. Aumente o delay entre envios
2. Reduza quantidade de envios simultâneos
3. Verifique conexão com internet
4. Feche outros programas

### Problema: Erro ao instalar pyautogui

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev python3-pip
sudo apt-get install python3-tk python3-dev
pip install pyautogui
```

### Problema: WhatsApp bloqueou temporariamente

**Solução:**
1. Pare os envios imediatamente
2. Aguarde 24-48 horas
3. Reduza volume de mensagens
4. Aumente delays entre envios
5. Revise conteúdo das mensagens

---

## 🔌 API Endpoints

### Templates

```bash
# Listar templates
GET /api/templates

# Criar template
POST /api/templates
{
  "nome": "Nome do Template",
  "mensagem": "Conteúdo da mensagem",
  "descricao": "Descrição opcional"
}

# Atualizar template
PUT /api/templates/{id}
{
  "mensagem": "Nova mensagem",
  "descricao": "Nova descrição"
}

# Deletar template
DELETE /api/templates/{id}
```

### Logs WhatsApp

```bash
# Obter logs
GET /api/whatsapp/logs?limit=100

# Obter estatísticas
GET /api/whatsapp/stats
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique esta documentação
2. Consulte os logs em `/api/whatsapp/logs`
3. Reinicie o servidor
4. Verifique as issues no repositório

---

## ⚠️ Avisos Legais

1. **Use com responsabilidade** - Não envie SPAM
2. **Respeite a privacidade** - Cumpra LGPD/GDPR
3. **Termos do WhatsApp** - Este bot pode violar os termos de serviço
4. **Bloqueios** - WhatsApp pode bloquear seu número por uso indevido
5. **Sem garantias** - Use por sua conta e risco

---

## 📄 Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

---

**Desenvolvido com ❤️ para automação de marketing**
