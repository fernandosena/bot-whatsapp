# 🚀 WhatsApp Bot com Selenium - Guia Completo

## 📋 Visão Geral

O WhatsApp Bot agora usa **Selenium WebDriver** para enviar mensagens através do WhatsApp Web oficial. Esta abordagem oferece:

✅ **Sessão Persistente** - Faça login uma vez e mantenha a sessão ativa
✅ **Mais Confiável** - Controle total do navegador
✅ **Verificação Visual** - Confirma envio através dos ícones de check
✅ **Melhor Controle** - Pausa, retoma e monitora em tempo real

---

## 🎯 Como Usar

### 1️⃣ Primeira Conexão

1. **Acesse a Interface**
   ```
   http://localhost:5000/whatsapp
   ```

2. **Clique em "📱 Conectar ao WhatsApp"**
   - Um navegador Chrome abrirá automaticamente
   - Você verá a tela de login do WhatsApp Web

3. **Escaneie o QR Code**
   - Abra o WhatsApp no seu celular
   - Vá em Configurações > Aparelhos Conectados
   - Toque em "Conectar Aparelho"
   - Escaneie o QR Code no navegador

4. **Aguarde a Confirmação**
   - O sistema detectará automaticamente quando você fizer login
   - Status mudará para: **"✅ Conectado ao WhatsApp"**

### 2️⃣ Enviando Mensagens

1. **Filtrar e Selecionar Empresas**
   - Use os filtros (setor, cidade, etc.)
   - Marque "Apenas com WhatsApp"
   - Clique em "🔍 Buscar"
   - Selecione as empresas desejadas

2. **Configurar Campanha**
   ```
   Nome da Campanha: Promoção Black Friday 2025

   Mensagem:
   Olá {nome}!

   Temos uma promoção especial para {cidade}.
   Entre em contato: {telefone}

   Att,
   Equipe

   Delay: 30 segundos
   ```

3. **Iniciar Envio**
   - Clique em "🚀 Iniciar Envio"
   - Acompanhe o progresso em tempo real
   - Veja logs de cada envio

### 3️⃣ Sessão Persistente

**A grande vantagem:** Você só precisa fazer login UMA VEZ!

- ✅ Feche o navegador → Sessão salva
- ✅ Reinicie o servidor → Sessão mantida
- ✅ Próxima vez → Já estará logado

**Para desconectar:**
- Clique em "🚪 Desconectar"
- Confirme a ação
- Próxima conexão precisará escanear QR Code novamente

---

## 📊 Status da Conexão

### 🔴 Desconectado
```
❌ Desconectado - Clique em "Conectar ao WhatsApp" para iniciar
```
- Nenhuma sessão ativa
- Precisa conectar antes de enviar

### 🟡 Aguardando Login
```
⏳ Aguardando login - Escaneie o QR Code no navegador
```
- Navegador aberto
- Aguardando você escanear o QR Code

### 🟢 Conectado
```
✅ Conectado ao WhatsApp - Pronto para enviar mensagens
```
- Login realizado com sucesso
- Pode enviar mensagens normalmente

---

## 🎛️ Recursos do Sistema

### Sistema de Campanhas

Cada envio é uma **campanha rastreada**:

```
┌─────────────────────────────────────┐
│ Promoção Black Friday               │
│ Status: ▶️ Em andamento              │
│ ████████████░░░░░░░░ 60%            │
│ 60/100 enviados | 2 falhas          │
│ [⏸️ Parar] [📊 Ver Logs]             │
└─────────────────────────────────────┘
```

**Funcionalidades:**
- ✅ Pausar a qualquer momento
- ✅ Continuar de onde parou
- ✅ Zero duplicatas garantido
- ✅ Histórico completo

### Checkpoint Automático

O sistema salva após **cada mensagem enviada**:

```
Enviando para empresa 1... ✅ Salvo
Enviando para empresa 2... ✅ Salvo
Enviando para empresa 3... ⏸️ PAROU
```

**Ao continuar:**
```
Retomando campanha...
Pulando empresa 1 (já enviado) ⏭️
Pulando empresa 2 (já enviado) ⏭️
Enviando para empresa 3... ✅
```

### Verificação de Envio

O Selenium **confirma visualmente** cada envio:

```python
# Procura pelo ícone de check (✓✓)
WebDriverWait(self.driver, 5).until(
    EC.presence_of_element_located((
        By.XPATH,
        '//span[@data-icon="msg-check" or @data-icon="msg-dblcheck"]'
    ))
)
```

**Resultado:**
- ✅ Viu o check → Mensagem enviada
- ⏱️ Não viu → Possível erro (mas pode ter enviado)

---

## 🔧 Configurações

### Delay Entre Envios

**Recomendações:**
- ⚠️ Mínimo: 20 segundos
- ✅ Recomendado: 30-60 segundos
- 🚫 Evite: < 20 segundos (risco de bloqueio)

### Limite Diário

Para evitar bloqueios do WhatsApp:
- ✅ Até 100 mensagens/dia: Seguro
- ⚠️ 100-200 mensagens/dia: Moderado
- 🚫 Mais de 200/dia: Alto risco

### Personalização de Mensagens

**Variáveis disponíveis:**
```
{nome}      → Nome da empresa
{cidade}    → Cidade
{setor}     → Setor/categoria
{endereco}  → Endereço completo
{telefone}  → Telefone
{email}     → Email
{website}   → Website
```

**Exemplo:**
```
Olá {nome}!

Somos especializados em atender empresas do setor de {setor}
na região de {cidade}.

Gostaria de conversar sobre uma parceria?

Nosso contato: {telefone}
```

---

## 🐛 Solução de Problemas

### ❌ "Você precisa estar conectado ao WhatsApp!"

**Causa:** Tentou enviar sem estar logado

**Solução:**
1. Clique em "📱 Conectar ao WhatsApp"
2. Escaneie o QR Code
3. Aguarde status ficar verde
4. Tente enviar novamente

### ❌ Navegador não abre

**Causa:** ChromeDriver não instalado ou incompatível

**Solução:**
```bash
pip install --upgrade selenium webdriver-manager
```

### ❌ Sessão perdida após reiniciar

**Causa:** Diretório de sessões foi deletado

**Solução:**
```bash
# Verificar se existe
ls whatsapp_sessions/

# Recriar se necessário
mkdir -p whatsapp_sessions
```

### ⚠️ "Timeout aguardando elementos do WhatsApp"

**Causa:** WhatsApp Web demorou para carregar

**Solução:**
1. Verifique sua conexão de internet
2. Tente novamente
3. Se persistir, aumente o timeout no código:
   ```python
   # Em whatsapp_selenium.py
   WebDriverWait(self.driver, 30)  # Era 20
   ```

### 🔄 Mensagem enviada mas não confirmada

**Causa:** Não encontrou o ícone de check

**Solução:**
- ✅ A mensagem provavelmente foi enviada
- Verifique manualmente no WhatsApp Web
- O log marcará como "warning" mas contabilizará como enviado

---

## 📁 Estrutura de Arquivos

```
bot/
├── src/
│   └── whatsapp/
│       ├── whatsapp_bot.py          # Antigo (pywhatkit)
│       └── whatsapp_selenium.py     # Novo (Selenium) ✨
├── whatsapp_sessions/
│   └── default/                     # Sessão persistente do Chrome
│       ├── Default/
│       │   ├── Cookies
│       │   ├── Local Storage/
│       │   └── ...
│       └── ...
├── database/
│   └── empresas.db
└── templates/
    └── whatsapp.html                # Interface com botão de login
```

---

## 🔐 Segurança da Sessão

### Onde ficam os dados?

A sessão é salva em:
```
whatsapp_sessions/default/
```

**Contém:**
- Cookies do WhatsApp Web
- Local Storage
- Configurações do navegador

### É seguro?

✅ **SIM** - Os dados ficam apenas no seu computador
✅ Nenhuma informação é enviada para servidores externos
✅ Use a mesma tecnologia do próprio navegador Chrome

### Compartilhar sessão?

❌ **NÃO recomendado**
- Cada máquina deve ter sua própria sessão
- Copiar a pasta pode causar conflitos

---

## 📊 Comparação: Selenium vs pywhatkit

| Recurso | pywhatkit (antigo) | Selenium (novo) |
|---------|-------------------|-----------------|
| Sessão persistente | ❌ Não | ✅ Sim |
| Precisa logar toda vez | ✅ Sim | ❌ Não |
| Verificação de envio | ❌ Não | ✅ Sim |
| Controle do navegador | ❌ Limitado | ✅ Total |
| Confiabilidade | ⚠️ Média | ✅ Alta |
| Velocidade | ⚠️ Média | ✅ Boa |
| Interface | ❌ Nenhuma | ✅ Completa |

---

## 🎓 Dicas de Uso

### ✅ Boas Práticas

1. **Teste Primeiro**
   - Envie para 1-2 empresas antes de lotes grandes
   - Verifique se a mensagem está correta

2. **Use Delays Adequados**
   - Mínimo 30 segundos entre mensagens
   - Máximo 100 mensagens por dia

3. **Personalize Sempre**
   - Use {nome} em todas as mensagens
   - Mensagens genéricas podem ser ignoradas

4. **Nomeie Campanhas**
   - Use nomes descritivos: "Black Friday 2025 - SP"
   - Facilita acompanhamento e retomada

5. **Mantenha o Navegador Aberto**
   - Não feche enquanto envia
   - Minimize se preferir

### ❌ Evite

1. **Spam**
   - Não envie a mesma mensagem 2x para mesma empresa
   - Use a aba "Campanhas" para verificar

2. **Delays Curtos**
   - Menos de 20 segundos pode causar bloqueio
   - WhatsApp detecta comportamento robótico

3. **Mensagens Muito Longas**
   - Limite: ~1000 caracteres
   - Mensagens grandes podem falhar

4. **Fechar Navegador Durante Envio**
   - Causará erros
   - Use "Parar" antes de fechar

---

## 🆘 Suporte

### Logs

Todos os envios são registrados em:
```
logs/bot-YYYY-MM-DD.log
```

### Verificar Status

**Via Interface:**
- Status visual sempre atualizado
- Indicador pulsante mostra conexão

**Via Endpoint:**
```bash
curl http://localhost:5000/api/whatsapp/session/status
```

### Reportar Problemas

Se encontrar bugs:
1. Verifique os logs em `logs/`
2. Veja a aba "📊 Logs" na interface
3. Copie a mensagem de erro
4. Reporte no GitHub

---

## 🚀 Próximos Passos

**Melhorias Futuras:**
- [ ] Envio de imagens/arquivos
- [ ] Agendamento de campanhas
- [ ] Templates com emojis personalizados
- [ ] Estatísticas avançadas
- [ ] Exportação de relatórios

---

**Última atualização:** Outubro 2025
**Versão:** 2.0 (Selenium)

✅ **Pronto para usar!**
