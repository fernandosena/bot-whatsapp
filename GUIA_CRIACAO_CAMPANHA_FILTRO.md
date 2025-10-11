# 📤 Guia: Criar Campanha a partir do Filtro de Mensagens

## 🎯 Nova Funcionalidade

Agora você pode **criar campanhas WhatsApp diretamente da página de filtro**, sem precisar ir até a página `/whatsapp`!

## ✨ Como Funciona

### Fluxo Completo

```
1. Filtrar empresas não enviadas
2. Selecionar empresas desejadas
3. Clicar em "Criar Campanha"
4. Configurar mensagem
5. Iniciar envio automático
```

---

## 📋 Passo a Passo Detalhado

### 1️⃣ Acessar Filtro de Mensagens

```
http://localhost:5000/filtro-mensagens
```

### 2️⃣ Filtrar Empresas Não Enviadas

Clique no card **⏳ Não Enviados** para ver apenas empresas que ainda não receberam mensagem.

Você também pode filtrar por:
- Setor
- Cidade
- Busca por nome

### 3️⃣ Selecionar Empresas

**Opção A: Seleção Individual**
- Marque o checkbox de cada empresa que deseja incluir na campanha

**Opção B: Selecionar Todas**
- Marque o checkbox no cabeçalho da tabela (ao lado de "Nome")
- Todas as empresas visíveis serão selecionadas

**Resultado:**
Uma barra aparecerá mostrando quantas empresas foram selecionadas:

```
┌─────────────────────────────────────────────┐
│ 15 selecionados                             │
│ [📤 Criar Campanha WhatsApp] [✖️ Limpar]   │
└─────────────────────────────────────────────┘
```

### 4️⃣ Criar Campanha

Clique no botão **📤 Criar Campanha WhatsApp**

Um modal aparecerá com os seguintes campos:

#### **Nome da Campanha**
- Gerado automaticamente: `Campanha 11/10/2025 14:30`
- Você pode alterar para algo mais descritivo

#### **Mensagem**
Digite a mensagem que será enviada. Você pode usar variáveis:

```
Olá {nome}!

Somos especializados em {setor} e estamos em {cidade}.

Temos uma promoção especial para você!

Interessado? Responda esta mensagem.
```

**Variáveis disponíveis:**
- `{nome}` - Nome da empresa
- `{setor}` - Setor de atuação
- `{cidade}` - Cidade da empresa

#### **Delay entre mensagens**
- Padrão: 30 segundos
- Mínimo: 10 segundos
- Máximo: 300 segundos (5 minutos)

**Recomendado:** 30-60 segundos para evitar bloqueios pelo WhatsApp

### 5️⃣ Iniciar Campanha

Clique em **🚀 Iniciar Campanha**

O sistema irá:

1. ✅ Verificar se você está conectado ao WhatsApp
2. ✅ Criar a campanha no banco de dados
3. ✅ Iniciar envio via WebSocket
4. ✅ Redirecionar para acompanhamento

**Após iniciar:**
- Modal fecha automaticamente em 3 segundos
- Seleção é limpa
- Tabela é atualizada automaticamente

---

## 🚨 Pré-requisitos

### IMPORTANTE: Estar Conectado ao WhatsApp

Antes de criar a campanha, você precisa:

1. Ir para `/whatsapp`
2. Clicar em **"Conectar ao WhatsApp"**
3. Escanear o QR Code (se necessário)
4. Aguardar login

**Verificação Automática:**
O sistema verifica automaticamente se você está conectado antes de iniciar a campanha.

Se não estiver conectado, você verá:

```
❌ Você precisa estar conectado ao WhatsApp!

Vá para a página /whatsapp e clique em "Conectar ao WhatsApp".
```

---

## 💡 Casos de Uso

### Caso 1: Enviar para Todas as Empresas Não Contactadas

```
1. Acesse /filtro-mensagens
2. Clique em "⏳ Não Enviados"
3. Marque o checkbox "Selecionar Todos"
4. Clique em "Criar Campanha"
5. Configure a mensagem
6. Inicie!
```

### Caso 2: Enviar para Setor Específico

```
1. Acesse /filtro-mensagens
2. Filtrar por Setor: "Padaria"
3. Clicar em "⏳ Não Enviados"
4. Selecionar empresas desejadas
5. Criar campanha
```

### Caso 3: Enviar para Cidade Específica

```
1. Acesse /filtro-mensagens
2. Filtrar por Cidade: "São Paulo"
3. Clicar em "⏳ Não Enviados"
4. Selecionar todas
5. Criar campanha
```

### Caso 4: Reenviar para Quem Teve Erro

```
1. Acesse /filtro-mensagens
2. Clicar em "✅ Enviados"
3. Verificar detalhes (passar mouse sobre ℹ️)
4. Identificar empresas com erro
5. Selecionar apenas essas
6. Criar nova campanha
```

---

## 🎨 Interface Visual

### Antes de Selecionar

```
┌──────────────────────────────────────────┐
│ [☐] Nome      Setor     Cidade  WhatsApp │
│ [☐] Empresa A Padaria   SP      5511...  │
│ [☐] Empresa B Farmácia  RJ      5521...  │
│ [☐] Empresa C Mercado   MG      5531...  │
└──────────────────────────────────────────┘
```

### Após Selecionar

```
┌──────────────────────────────────────────┐
│ 3 selecionados                           │
│ [📤 Criar Campanha] [✖️ Limpar]         │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ [☑] Nome      Setor     Cidade  WhatsApp │
│ [☑] Empresa A Padaria   SP      5511...  │
│ [☑] Empresa B Farmácia  RJ      5521...  │
│ [☑] Empresa C Mercado   MG      5531...  │
└──────────────────────────────────────────┘
```

### Modal de Campanha

```
╔════════════════════════════════════════╗
║ 📤 Criar Campanha WhatsApp         [×] ║
╠════════════════════════════════════════╣
║ ℹ️ Você está criando uma campanha     ║
║    para 3 empresas selecionadas.       ║
║                                         ║
║ Nome da Campanha:                       ║
║ ┌────────────────────────────────────┐ ║
║ │ Campanha 11/10/2025 14:30          │ ║
║ └────────────────────────────────────┘ ║
║                                         ║
║ Mensagem:                               ║
║ ┌────────────────────────────────────┐ ║
║ │ Olá {nome}!                        │ ║
║ │                                    │ ║
║ │ Temos uma promoção especial...     │ ║
║ └────────────────────────────────────┘ ║
║                                         ║
║ Delay: [30] segundos                   ║
║                                         ║
║ ⚠️ Importante:                         ║
║ • Certifique-se de estar conectado     ║
║ • Não feche o navegador                ║
║                                         ║
║           [Cancelar] [🚀 Iniciar]      ║
╚════════════════════════════════════════╝
```

---

## 📊 Monitoramento em Tempo Real

### Durante o Envio

A tabela **atualiza automaticamente** a cada 5 mensagens enviadas:

```
Antes:  ⏳ Não Enviado
Durante: ⏳ Não Enviado (processando...)
Depois: ✅ Enviado
```

### Acompanhar Progresso Detalhado

Para ver progresso em tempo real:

1. Abra `/whatsapp` em outra aba
2. Acompanhe os logs de envio
3. Veja estatísticas atualizadas

---

## 🔧 Tecnologias Usadas

- **WebSocket** (Socket.IO): Comunicação em tempo real
- **Modal**: Interface limpa e intuitiva
- **Checkboxes**: Seleção múltipla fácil
- **Validações**: Garantia de dados corretos
- **Auto-refresh**: Atualização automática da tabela

---

## ⚠️ Avisos Importantes

### 1. Números Bloqueados

Se uma empresa estiver bloqueada, ela **não aparecerá** na lista de "Não Enviados".

Para ver bloqueados:
- Clique em **🚫 Bloqueados**
- Desbloqueie se necessário via `/whatsapp`

### 2. Limite de Seleção

- Não há limite técnico de empresas
- Recomendado: Máximo 100 por campanha para melhor gerenciamento
- Para grandes volumes, divida em múltiplas campanhas

### 3. Delay Recomendado

| Quantidade | Delay Recomendado |
|------------|-------------------|
| 1-50       | 30 segundos       |
| 51-100     | 45 segundos       |
| 101-200    | 60 segundos       |
| 201+       | 90 segundos       |

### 4. Mensagens Personalizadas

As variáveis `{nome}`, `{setor}`, `{cidade}` são **substituídas automaticamente** para cada empresa.

**Exemplo:**

Mensagem configurada:
```
Olá {nome}! Somos de {cidade}.
```

Mensagem enviada para "Padaria do João" em "São Paulo":
```
Olá Padaria do João! Somos de São Paulo.
```

---

## 🎯 Fluxo Completo Ilustrado

```
┌─────────────────────┐
│ 1. Filtrar Empresas │
│    (Não Enviados)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Selecionar       │
│    Empresas         │
│    (Checkboxes)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Criar Campanha   │
│    (Botão)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Configurar       │
│    Mensagem (Modal) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Verificar        │
│    Conexão WhatsApp │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Iniciar Envio    │
│    (WebSocket)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. Acompanhar       │
│    Progresso        │
└─────────────────────┘
```

---

## 🚀 Atalhos Rápidos

### Envio Rápido para Todos

```javascript
// No console do navegador (F12)
// Selecionar todas as empresas visíveis
document.getElementById('select-all').click();

// Abrir modal
criarCampanha();
```

### Limpar Seleção Rápido

```
Pressione ESC ou clique em "Limpar Seleção"
```

---

## 📞 Suporte

Problemas? Verifique:

1. ✅ Está conectado ao WhatsApp? (`/whatsapp`)
2. ✅ Servidor Flask está rodando? (`python3 app.py`)
3. ✅ Empresas têm número WhatsApp válido?
4. ✅ WebSocket está conectado? (Console do navegador)

---

## 🎉 Benefícios

| Antes | Depois |
|-------|--------|
| Ir para /whatsapp | Tudo em uma página |
| Buscar empresas manualmente | Filtro automático |
| Copiar IDs um por um | Seleção com checkbox |
| Sem visualização de status | Status em tempo real |
| Difícil identificar não enviados | Um clique em "Não Enviados" |

---

Desenvolvido com ❤️ para facilitar o envio de campanhas WhatsApp!
