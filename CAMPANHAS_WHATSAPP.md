# 📋 Sistema de Campanhas WhatsApp

## 🎯 Visão Geral

O sistema de campanhas resolve um problema crítico: **evitar envios duplicados** e permitir **retomar campanhas interrompidas**.

### Problemas Resolvidos

✅ **Evita mensagens duplicadas** - Nunca envia duas vezes para a mesma empresa na mesma campanha
✅ **Checkpoint automático** - Salva progresso a cada envio
✅ **Retomada inteligente** - Continue exatamente de onde parou
✅ **Rastreamento completo** - Histórico detalhado de todas as campanhas
✅ **Proteção contra erros** - Se o bot travar, os dados estão salvos

---

## 🚀 Como Funciona

### 1. Criação de Campanha

Quando você inicia um envio, o sistema:

1. **Cria uma campanha** com nome único
2. **Salva os parâmetros**: mensagem, delay, lista de empresas
3. **Gera um ID** para rastreamento
4. **Marca status**: `em_andamento`

### 2. Durante o Envio

A cada mensagem enviada:

1. **Verifica duplicata** - Confere se empresa já recebeu
2. **Envia mensagem** - Usa WhatsApp Web
3. **Salva log** - Registra sucesso/falha
4. **Atualiza checkpoint** - Incrementa contador
5. **Continua** - Próxima empresa

### 3. Se Interromper

Quando você clica em "Parar" ou ocorre um erro:

1. **Pausa campanha** - Marca status como `pausada`
2. **Salva progresso** - Último índice processado
3. **Preserva dados** - Nada é perdido
4. **Permite retomar** - Botão "🔄 Continuar" aparece

### 4. Retomada

Ao continuar uma campanha pausada:

1. **Carrega dados** - Recupera mensagem e parâmetros
2. **Filtra enviados** - Lista apenas quem NÃO recebeu
3. **Retoma envio** - A partir do checkpoint
4. **Evita duplicatas** - Verificação dupla de segurança

---

## 📱 Interface - Aba Campanhas

### Visão Geral

A aba **📋 Campanhas** mostra todas as suas campanhas:

```
┌─────────────────────────────────────────┐
│ Campanha: Promoção Outubro 2025         │
│ Status: ⏸️ Pausada                       │
│                                         │
│ Mensagem: Olá, {nome}! Temos uma...    │
│                                         │
│ ┌─────┬─────────┬────────┬──────────┐  │
│ │Total│Enviados │ Falhas │Progresso │  │
│ │ 100 │   45    │   2    │  45%     │  │
│ └─────┴─────────┴────────┴──────────┘  │
│                                         │
│ [45%=================>          ]       │
│                                         │
│ [🔄 Continuar] [📊 Ver Logs]            │
└─────────────────────────────────────────┘
```

### Status das Campanhas

- **▶️ Em andamento** - Está enviando agora
- **⏸️ Pausada** - Interrompida, pode continuar
- **✅ Concluída** - Todas as mensagens enviadas

### Ações Disponíveis

- **🔄 Continuar** - Retoma campanha pausada (só aparece em pausadas)
- **📊 Ver Logs** - Mostra logs específicos desta campanha

---

## 🔧 Uso Prático

### Cenário 1: Envio Normal

```bash
1. Selecione empresas
2. Digite nome da campanha: "Black Friday 2025"
3. Escreva mensagem
4. Clique "🚀 Iniciar Envio"
5. Acompanhe progresso
6. Campanha concluída automaticamente
```

**Resultado:** Campanha finalizada, todas marcadas como enviadas.

### Cenário 2: Envio Interrompido

```bash
1. Iniciou envio para 100 empresas
2. Enviou 30 mensagens
3. Clicou "⏹️ Parar" (ou ocorreu erro)
4. Campanha pausada em 30/100
```

**Resultado:** 30 empresas marcadas como enviadas, 70 pendentes.

### Cenário 3: Retomada

```bash
1. Acesse aba "📋 Campanhas"
2. Veja campanha pausada: 30/100 (30%)
3. Clique "🔄 Continuar"
4. Sistema carrega automaticamente
5. Envia apenas para 70 restantes
6. Completa a campanha
```

**Resultado:** 100/100 empresas contactadas, zero duplicatas.

### Cenário 4: Erro e Recuperação

```bash
1. Iniciou campanha
2. Após 50 envios, internet caiu
3. Bot travou e foi fechado
4. Dados salvos: 50 empresas marcadas
5. Reiniciou servidor
6. Aba Campanhas mostra: 50/100 pausada
7. Clique "Continuar"
8. Retoma do ponto exato
```

**Resultado:** Recuperação completa, sem perda de dados.

---

## 🛡️ Proteções

### 1. Verificação de Duplicata

```python
# Antes de enviar, verifica:
if empresa_já_recebeu_nesta_campanha:
    pular_para_proxima()
```

### 2. Checkpoint Automático

```python
# Após cada envio bem-sucedido:
salvar_no_banco()
atualizar_contador()
marcar_empresa_como_enviada()
```

### 3. Isolamento de Campanha

Cada campanha é independente:
- Empresa pode receber da Campanha A
- Empresa pode receber da Campanha B
- Mas NÃO recebe 2x da mesma campanha

### 4. Transações Atômicas

```python
# Tudo ou nada:
try:
    enviar_mensagem()
    salvar_log()
    atualizar_checkpoint()
    commit()
except:
    rollback()  # Desfaz tudo
```

---

## 📊 Estrutura do Banco

### Tabela: `whatsapp_campaigns`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único da campanha |
| nome | TEXT | Nome da campanha |
| mensagem | TEXT | Texto da mensagem |
| total_empresas | INTEGER | Total de empresas |
| total_enviados | INTEGER | Quantos foram enviados |
| total_falhas | INTEGER | Quantos falharam |
| ultimo_indice | INTEGER | Último processado |
| status | TEXT | em_andamento/pausada/concluida |
| delay | INTEGER | Delay entre envios (segundos) |
| filtros | TEXT | JSON com filtros aplicados |
| data_inicio | TIMESTAMP | Quando começou |
| data_fim | TIMESTAMP | Quando terminou |
| data_atualizacao | TIMESTAMP | Última atualização |

### Tabela: `whatsapp_logs`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único do log |
| **campanha_id** | INTEGER | FK para campanha |
| empresa_id | INTEGER | FK para empresa |
| empresa_nome | TEXT | Nome (cache) |
| telefone | TEXT | WhatsApp |
| mensagem | TEXT | Texto enviado |
| status | TEXT | sucesso/erro |
| erro | TEXT | Mensagem de erro |
| data_envio | TIMESTAMP | Quando foi enviado |

### Índices

```sql
CREATE INDEX idx_whatsapp_logs_empresa
ON whatsapp_logs(empresa_id, campanha_id);
-- Para buscar rápido se empresa já recebeu

CREATE INDEX idx_whatsapp_logs_campanha
ON whatsapp_logs(campanha_id);
-- Para listar logs de uma campanha
```

---

## 🔍 Consultas Úteis

### Ver campanhas ativas

```bash
GET /api/whatsapp/campaigns/active
```

### Ver detalhes de campanha

```bash
GET /api/whatsapp/campaigns/123
```

### Ver logs de campanha

```bash
GET /api/whatsapp/campaigns/123/logs
```

### Verificar se empresa recebeu

```python
db.check_empresa_already_sent(empresa_id=45, campanha_id=10)
# Retorna: True/False
```

### Filtrar não enviadas

```python
empresas_pendentes = db.get_empresas_nao_enviadas(
    campanha_id=10,
    empresas_ids=[1,2,3,4,5]
)
# Retorna apenas IDs que NÃO receberam
```

---

## 💡 Boas Práticas

### 1. Nomeie Campanhas Claramente

```
❌ "Campanha 1"
❌ "Teste"
✅ "Black Friday - Desconto 50% - Outubro 2025"
✅ "Follow-up Clientes Inativos - Q4"
```

### 2. Pause Intencionalmente

Se precisar parar:
- Clique "⏹️ Parar"
- Sistema salva checkpoint
- Pode continuar depois com segurança

### 3. Verifique Campanhas Antigas

Antes de novo envio:
- Acesse aba Campanhas
- Veja se já contactou essas empresas
- Evite spam

### 4. Use Delays Adequados

- **30-60 segundos**: Seguro
- **< 20 segundos**: Risco de bloqueio
- **> 120 segundos**: Muito lento

### 5. Monitore Taxa de Erro

Se taxa de falha > 20%:
- Pause campanha
- Investigue erros
- Ajuste mensagem/delay
- Retome

---

## 🐛 Troubleshooting

### Campanha não continua

**Problema:** Cliquei "Continuar" mas não inicia.

**Solução:**
1. Verifique console do navegador (F12)
2. Certifique-se que WhatsApp Web está logado
3. Recarregue página
4. Tente novamente

### Todas as empresas já receberam

**Problema:** Diz que todas já receberam mas não recebi.

**Causa:** Você provavelmente já enviou nesta campanha antes.

**Solução:**
- Crie uma **nova campanha** com outro nome
- Ou envie para empresas diferentes

### Duplicatas mesmo com checkpoint

**Problema:** Empresa recebeu mensagem 2x.

**Investigar:**
```python
# Ver logs desta empresa
SELECT * FROM whatsapp_logs
WHERE empresa_id = 123
ORDER BY data_envio DESC;
```

**Possíveis causas:**
- Duas campanhas diferentes (OK, é permitido)
- Bug no código (reportar)

### Campanha travada "em_andamento"

**Problema:** Campanha mostra "em andamento" mas não está enviando.

**Solução:**
```python
# Via banco de dados:
UPDATE whatsapp_campaigns
SET status = 'pausada'
WHERE id = 123;
```

Ou use o script:
```bash
python -c "
from database.db import Database
db = Database()
db.pause_campaign(123)
"
```

---

## 📈 Estatísticas

### Ver progresso geral

```bash
curl http://localhost:5000/api/whatsapp/stats
```

### Ver progresso de campanha

```bash
curl http://localhost:5000/api/whatsapp/stats?campanha_id=123
```

### Exportar dados

Use a interface web ou API para exportar:
- Logs por campanha
- Empresas contactadas
- Taxa de sucesso/falha
- Tempo médio de envio

---

## 🎓 Exemplos Avançados

### Múltiplas Campanhas Paralelas

**NÃO recomendado**, mas possível:
- Campanha A: Promoção produto X
- Campanha B: Pesquisa de satisfação
- Campanha C: Convite para evento

Empresas podem receber as 3, pois são campanhas diferentes.

### Campanha Recorrente

```bash
1. Crie "Newsletter Mensal - Janeiro"
2. Envie para todas
3. Próximo mês: "Newsletter Mensal - Fevereiro"
4. Mesmas empresas receberão (campanhas diferentes)
```

### Segmentação

```bash
1. Filtre empresas por cidade: São Paulo
2. Crie campanha: "Evento SP - Março"
3. Próxima semana: Filtre por Rio
4. Crie campanha: "Evento RJ - Março"
```

---

## 🚨 Limitações

### 1. Não detecta resposta

O bot **NÃO** lê respostas. É apenas envio.

### 2. Uma campanha por vez

Não inicie duas campanhas simultaneamente.

### 3. Memória de campanha

Sistema lembra **para sempre**. Se enviou em Jan/2025, em Dez/2025 ainda lembra.

**Solução:** Use campanhas com nomes diferentes.

### 4. Não há expiração

Campanhas não expiram automaticamente. Gerencie manualmente.

---

## ✅ Checklist de Uso

Antes de enviar:

- [ ] Nomeei a campanha claramente
- [ ] Verifiquei se já contactei essas empresas
- [ ] Mensagem está personalizada com variáveis
- [ ] Delay configurado (30-60s)
- [ ] WhatsApp Web está logado
- [ ] Testei com 2-3 empresas primeiro
- [ ] Estou preparado para monitorar

Durante envio:

- [ ] Acompanho progresso em tempo real
- [ ] Vejo logs de sucesso/falha
- [ ] Taxa de falha está aceitável (<20%)
- [ ] Não fecho navegador
- [ ] Posso pausar se necessário

Após envio:

- [ ] Verifico estatísticas finais
- [ ] Reviso logs de erros
- [ ] Anoto taxa de resposta
- [ ] Planejo próxima campanha
- [ ] Limpo campanhas antigas (opcional)

---

## 📞 Suporte

Problemas com campanhas:

1. Verifique logs: `/api/whatsapp/campaigns/ID/logs`
2. Inspecione banco: `database/empresas.db`
3. Consulte `WHATSAPP_BOT_GUIDE.md`
4. Reporte issues no GitHub

---

**Última atualização:** Outubro 2025
**Versão:** 2.0 - Sistema de Campanhas com Checkpoint
