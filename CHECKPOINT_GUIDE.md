# 📌 Guia do Sistema de Checkpoints

## 🎯 O que é o Sistema de Checkpoints?

O sistema de checkpoints permite que você:
- **Continue de onde parou** se a busca for interrompida
- **Não desperdice tempo** reprocessando empresas já coletadas
- **Processe grandes volumes** em múltiplas sessões
- **Retome buscas** mesmo após erros ou travamentos

## 🚀 Como Funciona

### Exemplo Prático

**Cenário**: Você quer buscar 500 lanchonetes em São Paulo

```bash
# Primeira execução: busca 100 empresas
Setor: lanchonetes
Cidade: São Paulo
Limite: 100

# O bot processa e salva um checkpoint
# ✅ 100 empresas processadas (índice 0-99)
```

**Se você rodar novamente** com os mesmos parâmetros:

```bash
# Segunda execução: CONTINUA de onde parou!
Setor: lanchonetes
Cidade: São Paulo
Limite: 200

# O bot detecta o checkpoint anterior
# 📌 "Checkpoint encontrado! Continuando do índice 100"
# ✅ Processa empresas 100-199 (NÃO reprocessa 0-99)
```

## 📊 Estados do Checkpoint

| Estado | Descrição | O que acontece? |
|--------|-----------|-----------------|
| **em_andamento** | Busca em progresso ou interrompida | Continua automaticamente |
| **concluido** | Busca finalizada com sucesso | Pergunta se quer recomeçar |
| **erro** | Busca teve erro | Continua do último ponto salvo |

## 💻 Usando via CLI (main.py)

### Primeira Busca
```bash
python main.py
# Escolha opção 1: Buscar empresas
Setor: restaurantes
Cidade: Rio de Janeiro
Limite: 100
```

**Resultado**: 100 empresas processadas, checkpoint salvo

### Continuar Busca
```bash
python main.py
# Escolha opção 1: Buscar empresas
Setor: restaurantes  # MESMOS parâmetros
Cidade: Rio de Janeiro
Limite: 200  # Novo limite (maior)
```

**Resultado**:
- Bot detecta checkpoint
- Pula empresas 0-99 (já processadas)
- Processa empresas 100-199

### Recomeçar do Zero
```bash
python main.py
# Escolha opção 1: Buscar empresas
Setor: restaurantes
Cidade: Rio de Janeiro
Limite: 100

# Se já existe checkpoint concluído:
# ✅ Busca já foi concluída anteriormente!
#    Total processados: 200 | Salvos: 150
# Deseja recomeçar do zero? (s/N): s
```

## 🌐 Usando via Interface Web

### Continuar Automaticamente
1. Acesse http://localhost:5000
2. Preencha **Setor** e **Cidade** (mesmos de antes)
3. Clique em **Iniciar Busca**
4. O bot **detecta automaticamente** se já existe checkpoint
5. Continua de onde parou! 🚀

### Ver Checkpoints Salvos
```python
# No terminal Python ou via API
from src.database.db import Database

db = Database()
checkpoints = db.get_all_checkpoints()

for cp in checkpoints:
    print(f"Setor: {cp['setor']}, Cidade: {cp['cidade']}")
    print(f"Processados: {cp['total_processados']}")
    print(f"Status: {cp['status']}\n")
```

## 🎓 Casos de Uso

### Caso 1: Coleta Gradual
**Objetivo**: Coletar 1000 empresas aos poucos

```bash
# Dia 1: 100 empresas
Setor: academias
Cidade: São Paulo
Limite: 100
# ✅ Checkpoint salvo (0-99)

# Dia 2: mais 100 empresas
Setor: academias
Cidade: São Paulo
Limite: 200
# ✅ Continua do 100, processa até 199

# Dia 3: mais 100 empresas
Setor: academias
Cidade: São Paulo
Limite: 300
# ✅ Continua do 200, processa até 299

# ... e assim por diante
```

### Caso 2: Recuperação de Erro
**Objetivo**: Retomar após travamento

```bash
# Execução inicial
Setor: padarias
Cidade: Belo Horizonte
Limite: 500

# Bot processa 237 empresas e trava (erro, falta de energia, etc)
# ✅ Checkpoint automático salvo (último índice: 237)

# Reiniciar busca
Setor: padarias
Cidade: Belo Horizonte
Limite: 500

# 📌 Bot detecta checkpoint
# ⏭️ Pula 237 empresas já processadas
# ✅ Continua do índice 237
```

### Caso 3: Múltiplas Cidades
**Objetivo**: Buscar em várias cidades sem perder progresso

```bash
# Cidade 1
Setor: pizzarias
Cidade: São Paulo
Limite: 100
# ✅ Checkpoint: pizzarias + São Paulo

# Cidade 2
Setor: pizzarias
Cidade: Rio de Janeiro
Limite: 100
# ✅ Checkpoint: pizzarias + Rio de Janeiro

# Voltar para Cidade 1 (expandir)
Setor: pizzarias
Cidade: São Paulo
Limite: 200
# 📌 Usa checkpoint de São Paulo
# ✅ Continua do 100
```

## 🛠️ Comandos Úteis

### Ver Checkpoints
```python
from src.database.db import Database

db = Database()

# Listar todos
checkpoints = db.get_all_checkpoints()
for cp in checkpoints:
    print(f"{cp['setor']} em {cp['cidade']}: {cp['total_processados']} processados ({cp['status']})")
```

### Resetar Checkpoint Específico
```python
from src.database.db import Database

db = Database()

# Resetar checkpoint específico
db.reset_checkpoint('lanchonetes', 'São Paulo')
print("✅ Checkpoint resetado! Próxima busca começará do zero.")
```

### Resetar TODOS os Checkpoints
```bash
sqlite3 database/empresas.db "DELETE FROM search_checkpoints;"
```

## ⚠️ Observações Importantes

### 1. **Checkpoints são por Setor + Cidade**
Cada combinação de setor e cidade tem seu próprio checkpoint:
- `lanchonetes` + `São Paulo` → Checkpoint A
- `lanchonetes` + `Rio de Janeiro` → Checkpoint B
- `pizzarias` + `São Paulo` → Checkpoint C

### 2. **Limite Crescente**
Sempre use um limite **maior ou igual** ao anterior:
- ✅ Correto: 100 → 200 → 300
- ❌ Errado: 200 → 100 (vai processar menos do que já tinha)

### 3. **Google Maps Limita a 120 Resultados**
Por busca, o Google Maps mostra no máximo ~120 resultados.
Para mais empresas, use estratégias diferentes:
- Dividir por bairros
- Dividir por tipos específicos
- Usar termos de busca mais específicos

### 4. **Backup Recomendado**
Faça backup do banco antes de resetar checkpoints:
```bash
cp database/empresas.db database/backup_$(date +%Y%m%d).db
```

## 📈 Monitoramento

### Via Banco de Dados
```sql
-- Ver checkpoints ativos
SELECT * FROM search_checkpoints
WHERE status = 'em_andamento'
ORDER BY data_atualizacao DESC;

-- Ver checkpoints concluídos
SELECT setor, cidade, total_processados, total_salvos
FROM search_checkpoints
WHERE status = 'concluido';

-- Ver progresso em %
SELECT
    setor,
    cidade,
    total_processados,
    total_encontrados,
    ROUND((total_processados * 100.0 / total_encontrados), 2) as progresso_pct
FROM search_checkpoints
WHERE status = 'em_andamento';
```

## 🎯 Melhores Práticas

1. **Sempre use os mesmos parâmetros** para continuar uma busca
2. **Incremente o limite** gradualmente (100 → 200 → 300)
3. **Faça backup** antes de resetar checkpoints
4. **Monitore o progresso** via banco de dados
5. **Divida buscas grandes** em múltiplas cidades/bairros

## 🐛 Resolução de Problemas

### Checkpoint não está sendo detectado
**Causa**: Parâmetros diferentes (setor ou cidade com maiúsculas/minúsculas diferentes)
**Solução**: Use exatamente os mesmos parâmetros

### Bot sempre começa do zero
**Causa**: Checkpoint foi resetado ou deletado
**Solução**: Verifique se existe checkpoint no banco:
```python
db.get_checkpoint('seu_setor', 'sua_cidade')
```

### Checkpoint mostra "concluído" mas quero continuar
**Solução**:
```python
db.reset_checkpoint('seu_setor', 'sua_cidade')
# Ou responda 's' quando perguntado se quer recomeçar
```

## 🎉 Conclusão

O sistema de checkpoints permite que você:
- ✅ Processe **milhares de empresas** aos poucos
- ✅ **Nunca perca progresso** em caso de erro
- ✅ **Retome automaticamente** de onde parou
- ✅ **Organize buscas** por cidade e setor

**Exemplo Real**:
```bash
# Objetivo: 500 empresas
# Dia 1: 100 empresas (1h)
# Dia 2: +100 empresas (1h) = 200 total
# Dia 3: +100 empresas (1h) = 300 total
# Dia 4: +100 empresas (1h) = 400 total
# Dia 5: +100 empresas (1h) = 500 total ✅

# Sem checkpoint: 5h total
# Com checkpoint: 1h por dia, flexível! 🚀
```
