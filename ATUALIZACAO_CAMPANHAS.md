# 🔄 Atualização - Sistema de Campanhas

## O que mudou?

✅ **Sistema de campanhas** com checkpoint automático
✅ **Proteção contra duplicatas** - nunca envia 2x
✅ **Retomada inteligente** - continue de onde parou
✅ **Nova aba "Campanhas"** na interface

---

## ⚠️ Aviso Importante

Ao iniciar o servidor, você verá este aviso:

```
[WARNING] WhatsApp Bot não disponível: Can't connect to display ":0"
```

**Isso é NORMAL e esperado!**

O aviso aparece porque:
- O `pyautogui` tenta se conectar ao display ao ser importado
- Mas você está executando via SSH ou sem interface gráfica ativa
- **O servidor funciona normalmente mesmo com este aviso**
- O bot só precisa do display quando **realmente for enviar mensagens**

### Quando o display É necessário:

- ✅ Ao clicar "Iniciar Envio" na interface web
- ✅ Durante o envio de mensagens via WhatsApp Web

### Quando o display NÃO é necessário:

- ✅ Iniciar o servidor (`python app.py`)
- ✅ Navegar pela interface
- ✅ Ver campanhas, logs, estatísticas
- ✅ Gerenciar templates
- ✅ Listar empresas

---

## 🚀 Como Atualizar

### 1. Parar servidor (se estiver rodando)

```bash
# Ctrl+C no terminal onde está rodando
# Ou:
pkill -f "python app.py"
```

### 2. Executar migração

```bash
python migrate_whatsapp_campaigns.py
```

**Saída esperada:**
```
✅ Migração concluída com sucesso!
📋 Resumo:
   - Tabela whatsapp_campaigns criada
   - Tabela whatsapp_logs atualizada
   - Índices criados
   - Dados antigos preservados
```

### 3. Reiniciar servidor

```bash
python app.py
```

**Saída esperada:**
```
[WARNING] WhatsApp Bot não disponível...  ← NORMAL! Ignore este aviso
🚀 Servidor web iniciado!
📍 Acesse: http://localhost:5000
```

### 4. Acessar interface

```
http://localhost:5000/whatsapp
```

Você verá uma nova aba: **📋 Campanhas**

---

## 🎯 Novos Recursos

### 1. Nome de Campanha

Agora você pode dar um nome para cada campanha:

```
Campo: Nome da Campanha
Exemplo: "Promoção Black Friday 2025"
```

### 2. Aba Campanhas

Lista todas as campanhas com:
- Nome e status (em andamento/pausada/concluída)
- Progresso (ex: 45/100 = 45%)
- Estatísticas (enviados, falhas)
- Botão "Continuar" para campanhas pausadas
- Botão "Ver Logs" para detalhes

### 3. Checkpoint Automático

Sistema salva automaticamente:
- A cada mensagem enviada
- Quando você clica "Parar"
- Se ocorrer erro ou travamento

### 4. Proteção Contra Duplicatas

Verifica antes de enviar:
- Empresa já recebeu nesta campanha? → Pula
- Nunca envia 2x para a mesma empresa na mesma campanha

### 5. Retomada Inteligente

Se pausou em 30/100:
- Clique "Continuar" na aba Campanhas
- Sistema envia apenas para os 70 restantes
- Recupera mensagem e parâmetros originais

---

## 📝 Exemplo de Uso

### Cenário: Envio Interrompido

```bash
# 1. Iniciou envio para 100 empresas
Nome: "Newsletter Outubro"
Selecionadas: 100 empresas
Mensagem: "Olá {nome}!..."

# 2. Enviou 40 mensagens
Progresso: 40/100 (40%)
Status: enviando...

# 3. Internet caiu / Clicou "Parar"
Status: ⏸️ Pausada
Checkpoint salvo: 40/100

# 4. Mais tarde, retoma
Aba Campanhas → "Newsletter Outubro"
Clica "🔄 Continuar"

# 5. Sistema retoma
Filtra: 60 empresas restantes
Envia apenas para quem NÃO recebeu
Progresso: 41/100, 42/100... 100/100

# 6. Completa
Status: ✅ Concluída
Total: 100/100 (100%)
Zero duplicatas!
```

---

## 🛠️ Troubleshooting

### Erro: "no such column: campanha_id"

**Causa:** Migração não foi executada

**Solução:**
```bash
python migrate_whatsapp_campaigns.py
```

### Aviso: "WhatsApp Bot não disponível"

**Causa:** Sem display gráfico (normal em SSH)

**Solução:** Ignore o aviso, é esperado. O servidor funciona normalmente.

### Erro ao enviar: "Can't connect to display"

**Causa:** Tentou enviar mensagens sem display

**Solução:**
1. Use VNC ou acesse diretamente a máquina com interface gráfica
2. Ou execute em máquina com desktop ativo
3. Consulte `SYSTEM_REQUIREMENTS.md`

### Campanhas não aparecem

**Causa:** Migração não criou tabelas

**Verificar:**
```bash
python -c "from src.database.db import Database; db = Database(); print(f'Campanhas: {len(db.get_all_campaigns())}'); db.close()"
```

**Deve retornar:** `Campanhas: 0` (ou mais se já criou)

### Botão "Continuar" não funciona

**Causa:** JavaScript não carregou

**Solução:**
1. Abra console do navegador (F12)
2. Recarregue página (Ctrl+R)
3. Veja se há erros
4. Limpe cache do navegador

---

## 📊 Banco de Dados

### Novas Tabelas

**whatsapp_campaigns:**
- Armazena informações de cada campanha
- ID, nome, mensagem, estatísticas, status

**whatsapp_logs (atualizada):**
- Agora tem coluna `campanha_id`
- Relaciona cada log com sua campanha

### Backup

A migração cria backup automático:
- `whatsapp_logs_old` - Dados antigos preservados

Se algo der errado, dados estão seguros!

---

## 🔄 Reverter (se necessário)

Se precisar voltar à versão anterior:

```bash
# 1. Parar servidor
pkill -f "python app.py"

# 2. Restaurar tabela antiga (se existir)
python -c "
import sqlite3
conn = sqlite3.connect('database/empresas.db')
conn.execute('DROP TABLE whatsapp_logs')
conn.execute('ALTER TABLE whatsapp_logs_old RENAME TO whatsapp_logs')
conn.execute('DROP TABLE whatsapp_campaigns')
conn.commit()
conn.close()
print('✅ Revertido')
"

# 3. Reiniciar servidor
python app.py
```

---

## ✅ Checklist de Atualização

- [ ] Parei servidor atual
- [ ] Executei `migrate_whatsapp_campaigns.py`
- [ ] Vi mensagem "Migração concluída"
- [ ] Reiniciei servidor
- [ ] Ignorei aviso "WhatsApp Bot não disponível"
- [ ] Acessei http://localhost:5000/whatsapp
- [ ] Vi nova aba "📋 Campanhas"
- [ ] Testei criar uma campanha simples
- [ ] Li `CAMPANHAS_WHATSAPP.md`

---

## 📚 Documentação

Documentos criados:

1. **CAMPANHAS_WHATSAPP.md** - Guia completo do sistema
2. **SYSTEM_REQUIREMENTS.md** - Requisitos de sistema
3. **ATUALIZACAO_CAMPANHAS.md** - Este arquivo

Leia para aproveitar ao máximo o novo sistema!

---

## 🎉 Pronto!

Seu sistema agora tem:
- ✅ Campanhas rastreadas
- ✅ Checkpoint automático
- ✅ Zero duplicatas
- ✅ Retomada inteligente
- ✅ Interface completa

**Bom uso!** 🚀
