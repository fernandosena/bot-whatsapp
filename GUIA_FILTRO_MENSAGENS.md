# 📊 Guia de Filtro de Mensagens

## 🎯 O que é?

Uma página web completa para visualizar e filtrar quais empresas já receberam mensagens via WhatsApp e quais ainda não foram contactadas.

## 🚀 Como Usar

### 1. Acessar a Página

```
http://localhost:5000/filtro-mensagens
```

### 2. Estatísticas em Tempo Real

A página exibe 4 cards principais:

- **📋 Total de Empresas**: Total com WhatsApp cadastrado
- **✅ Mensagens Enviadas**: Empresas que já receberam mensagem
- **⏳ Não Enviadas**: Empresas que ainda não receberam
- **🚫 Bloqueadas**: Números bloqueados/inexistentes

### 3. Filtros Disponíveis

#### Filtro por Status (Clique nos Cards)

- **📋 Todos**: Mostra todas as empresas
- **✅ Enviados**: Apenas empresas que receberam mensagem
- **⏳ Não Enviados**: Apenas empresas que NÃO receberam
- **🚫 Bloqueados**: Apenas números bloqueados

#### Outros Filtros

- **Buscar**: Nome ou telefone da empresa
- **Setor**: Filtrar por setor específico
- **Cidade**: Filtrar por cidade
- **Campanha**: Filtrar por campanha de envio específica

### 4. Tabela de Resultados

Exibe as seguintes informações:

| Coluna | Descrição |
|--------|-----------|
| Nome | Nome da empresa |
| Setor | Setor de atuação |
| Cidade | Localização |
| WhatsApp | Número de WhatsApp |
| Status | Badge colorido (Enviado/Não Enviado/Bloqueado) |
| Data de Envio | Quando a mensagem foi enviada |
| Detalhes | ℹ️ Passe o mouse para ver mais informações |

### 5. Exportar Resultados

Clique em **📥 Exportar Excel** para baixar os dados filtrados em formato Excel.

O arquivo incluirá:
- Todas as colunas da empresa
- Status de envio
- Data de envio
- Mensagem de erro (se houver)
- Motivo de bloqueio (se aplicável)

---

## 🔧 Funcionalidades Técnicas

### Endpoints da API

#### 1. Listar Empresas com Status de Envio

```
GET /api/empresas/com-status-envio
```

**Parâmetros:**
- `setor` (opcional): Filtrar por setor
- `cidade` (opcional): Filtrar por cidade
- `campanha_id` (opcional): Filtrar por campanha específica
- `status_envio` (opcional): `enviado`, `nao_enviado`, `bloqueado`
- `search` (opcional): Buscar por nome ou telefone

**Resposta:**
```json
{
  "empresas": [
    {
      "id": 1,
      "nome": "Empresa A",
      "whatsapp": "5511999999999",
      "status_envio": "enviado",
      "data_envio": "2025-01-15 10:30:00",
      "status_msg": "sucesso",
      "erro": null,
      "motivo_bloqueio": null
    }
  ],
  "stats": {
    "total": 100,
    "enviados": 45,
    "nao_enviados": 50,
    "bloqueados": 5
  }
}
```

#### 2. Exportar para Excel

```
GET /api/export/mensagens-excel
```

**Parâmetros:** (mesmos da API acima)

**Resposta:** Arquivo Excel para download

---

## 📊 Como o Status é Determinado

### Lógica de Status

```sql
CASE
    WHEN numero está em whatsapp_blocked THEN 'bloqueado'
    WHEN existe registro em whatsapp_logs THEN 'enviado'
    ELSE 'nao_enviado'
END
```

### Prioridade

1. **Bloqueado**: Tem prioridade máxima (número na lista de bloqueio)
2. **Enviado**: Se existe log de envio (mesmo com erro)
3. **Não Enviado**: Se nunca foi processado

---

## 💡 Casos de Uso

### Caso 1: Identificar Quem Ainda Não Recebeu Mensagem

1. Acesse `/filtro-mensagens`
2. Clique no card **⏳ Não Enviados**
3. Filtre por setor/cidade se necessário
4. Exporte para Excel
5. Use esses dados para criar nova campanha de envio

### Caso 2: Verificar Mensagens com Erro

1. Acesse `/filtro-mensagens`
2. Clique em **✅ Enviados**
3. Na tabela, passe o mouse sobre o ℹ️ na coluna **Detalhes**
4. Verifique quais tiveram erro
5. Corrija os números e reenvie

### Caso 3: Gerenciar Números Bloqueados

1. Acesse `/filtro-mensagens`
2. Clique em **🚫 Bloqueados**
3. Veja a lista de números bloqueados
4. Na coluna **Detalhes**, veja o motivo do bloqueio
5. Se necessário, desbloqueie pela página `/whatsapp`

### Caso 4: Análise de Campanha Específica

1. Acesse `/filtro-mensagens`
2. Selecione a campanha no dropdown
3. Veja quantos foram enviados com sucesso
4. Identifique falhas ou números bloqueados
5. Exporte relatório

---

## 🎨 Código de Cores

- **Verde** 🟢 = Enviado com sucesso
- **Laranja** 🟠 = Não enviado (aguardando)
- **Vermelho** 🔴 = Bloqueado

---

## 🔄 Atualização Automática

A página se atualiza automaticamente a cada **30 segundos** para mostrar os dados mais recentes.

---

## 🛠️ Integração com WhatsApp

### Fluxo Completo

1. **Coleta de Dados** (`/` - Página Principal)
   - Buscar empresas no Google Maps
   - Empresas são salvas no banco

2. **Envio de Mensagens** (`/whatsapp`)
   - Selecionar empresas
   - Enviar mensagens
   - Logs são registrados

3. **Análise de Resultados** (`/filtro-mensagens` - **NOVA PÁGINA**)
   - Visualizar quem recebeu
   - Filtrar por status
   - Exportar relatórios

---

## 📈 Exemplo de Relatório Excel

O arquivo exportado terá as seguintes colunas:

```
| id | nome | status_envio | setor | cidade | whatsapp | data_envio | status_msg | erro | motivo_bloqueio |
|----|------|--------------|-------|--------|----------|------------|------------|------|-----------------|
| 1  | Emp A| Enviado      | Pad.  | SP     | 5511...  | 2025-01-15 | sucesso    | -    | -               |
| 2  | Emp B| Não Enviado  | Pad.  | RJ     | 5521...  | -          | -          | -    | -               |
| 3  | Emp C| Bloqueado    | Pad.  | SP     | 5511...  | -          | -          | -    | Número não existe|
```

---

## 🚨 Observações Importantes

### 1. Números Bloqueados Automaticamente

Quando uma mensagem falha com status `nao_existe`, o número é **automaticamente bloqueado** para evitar tentativas futuras.

### 2. Campanha vs Empresa

- Uma **empresa** pode receber mensagens de múltiplas **campanhas**
- O filtro por campanha mostra apenas envios daquela campanha específica
- Sem filtro de campanha, mostra o envio mais recente

### 3. Duplicatas

O sistema agrupa empresas duplicadas e mostra apenas o **envio mais recente**.

---

## 🎯 Próximos Passos

### Funcionalidades Futuras (Sugestões)

1. **Reenvio em Massa**
   - Botão para reenviar mensagens para "Não Enviados"

2. **Gráficos**
   - Pizza mostrando distribuição de status
   - Linha temporal de envios

3. **Filtros Avançados**
   - Data de envio (entre X e Y)
   - Horário de envio
   - Taxa de sucesso por setor

4. **Desbloquear em Massa**
   - Selecionar vários números bloqueados e desbloquear

---

## ❓ FAQ

**P: Como sei se um número foi bloqueado?**
R: Na coluna "Status" aparecerá uma badge vermelha "🚫 Bloqueado". Passe o mouse sobre o ℹ️ para ver o motivo.

**P: Posso desbloquear um número?**
R: Sim, vá para a página `/whatsapp`, na seção "Números Bloqueados".

**P: O que significa "Enviado" com erro?**
R: A mensagem foi tentada, mas falhou (ex: número inexistente, erro de conexão). Passe o mouse sobre ℹ️ para ver detalhes.

**P: Posso filtrar por data de envio?**
R: Atualmente não, mas você pode exportar para Excel e filtrar lá.

**P: A página atualiza automaticamente?**
R: Sim, a cada 30 segundos. Você também pode clicar em "Aplicar Filtros" para atualizar manualmente.

---

## 🔗 Navegação Rápida

- **Início**: `http://localhost:5000/` - Buscar empresas
- **WhatsApp**: `http://localhost:5000/whatsapp` - Enviar mensagens
- **Filtro de Mensagens**: `http://localhost:5000/filtro-mensagens` - **Nova página!**

---

Desenvolvido com ❤️ para facilitar o gerenciamento de campanhas WhatsApp
