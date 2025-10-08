# 🚀 Guia de Performance e Limites

## 📊 Limites do Sistema

### **Limites Teóricos**

| Recurso | Limite Prático | Limite Máximo |
|---------|---------------|---------------|
| **Empresas por busca** | 50-120 | 120* |
| **Empresas por hora** | 500-1.000 | 2.000 |
| **Total no banco** | Ilimitado | 10M+ registros |
| **Memória RAM necessária** | 500MB | 2GB |
| **Uso de CPU** | 30-50% | 100% |

*O Google Maps geralmente mostra no máximo 120 resultados por busca

### **Configurações Recomendadas**

#### 🖥️ **Para PC Normal** (4GB RAM, 4 CPUs)
```env
HEADLESS=true
CHUNK_SIZE=50
MAX_RESULTS_PER_SEARCH=50
BATCH_COMMIT=10
```
- ✅ Velocidade: ~500-800 empresas/hora
- ✅ Memória: ~500MB
- ✅ Estabilidade: Alta

#### 💻 **Para PC Potente** (8GB RAM, 8 CPUs)
```env
HEADLESS=true
CHUNK_SIZE=100
MAX_RESULTS_PER_SEARCH=100
BATCH_COMMIT=20
```
- ✅ Velocidade: ~800-1.200 empresas/hora
- ✅ Memória: ~1GB
- ✅ Estabilidade: Alta

#### 🖥️ **Para Servidor** (16GB+ RAM, 16+ CPUs)
```env
HEADLESS=true
CHUNK_SIZE=200
MAX_RESULTS_PER_SEARCH=120
BATCH_COMMIT=50
```
- ✅ Velocidade: ~1.200-2.000 empresas/hora
- ✅ Memória: ~2GB
- ✅ Estabilidade: Média-Alta

## ⚠️ Limitações e Como Contornar

### **1. Limite de Resultados do Google Maps**
**Problema**: Google Maps mostra no máximo 120 resultados por busca

**Solução**:
- Divida sua busca em múltiplas pesquisas específicas
- Exemplo ao invés de "restaurantes em São Paulo":
  - "restaurantes em Pinheiros, São Paulo"
  - "restaurantes em Vila Mariana, São Paulo"
  - "restaurantes em Centro, São Paulo"

### **2. Velocidade de Extração de Email**
**Problema**: Acessar websites para extrair email é lento (3s por site)

**Solução**:
- A extração de email é opcional
- Você pode desabilitar temporariamente e processar mais empresas
- Depois rodar novamente para preencher emails das que não têm

### **3. Bloqueio do Google**
**Problema**: Google pode bloquear após muitas requisições

**Sinais de bloqueio**:
- CAPTCHAs aparecem
- Resultados param de carregar
- Erros 429 (Too Many Requests)

**Soluções**:
1. **Usar VPN/Proxy** - Mudar IP entre buscas
2. **Delays maiores** - Aumentar tempo entre empresas
3. **Pausas estratégicas** - Parar 15-30min a cada 500 empresas

### **4. Memória RAM**
**Problema**: Chrome consome muita memória

**Soluções**:
1. Reduzir `CHUNK_SIZE` para processar menos URLs por vez
2. Usar `HEADLESS=true` (economiza ~30% de RAM)
3. Reiniciar o bot a cada 1000 empresas

## 🎯 Estratégias para Grandes Volumes

### **Para coletar 10.000+ empresas**:

#### Estratégia 1: Divisão Geográfica
```python
# Ao invés de:
# "lanchonetes em São Paulo" (120 resultados)

# Faça:
bairros = ["Pinheiros", "Vila Mariana", "Moema", "Itaim Bibi", ...]
for bairro in bairros:
    buscar(f"lanchonetes em {bairro}, São Paulo")
    # Até 120 resultados por bairro
```

#### Estratégia 2: Divisão por Tipo
```python
# Ao invés de:
# "restaurantes em São Paulo"

# Faça:
tipos = ["pizzaria", "japonês", "italiano", "churrascaria", ...]
for tipo in tipos:
    buscar(f"{tipo} em São Paulo")
```

#### Estratégia 3: Múltiplas Instâncias
Execute múltiplas instâncias do bot em paralelo (cada uma em uma cidade diferente):

```bash
# Terminal 1
# Buscar em São Paulo
python app.py

# Terminal 2 (com outro banco de dados)
# Buscar em Rio de Janeiro
DB_PATH=./database/empresas_rj.db python app.py

# Terminal 3
# Buscar em Belo Horizonte
DB_PATH=./database/empresas_bh.db python app.py
```

## 📈 Benchmarks Reais

### Teste 1: PC Normal (4GB RAM, 4 CPUs)
- **Configuração**: `CHUNK_SIZE=50`, `MAX_RESULTS=50`
- **Resultado**: 47 empresas em 3min 20s
- **Velocidade**: ~850 empresas/hora
- **Memória pico**: 620MB
- **CPU médio**: 35%

### Teste 2: Servidor (16GB RAM, 16 CPUs)
- **Configuração**: `CHUNK_SIZE=200`, `MAX_RESULTS=120`
- **Resultado**: 118 empresas em 4min 15s
- **Velocidade**: ~1.670 empresas/hora
- **Memória pico**: 1.8GB
- **CPU médio**: 45%

## 🛡️ Sinais de Problema

### ⚠️ Sistema está sobrecarregado:
- Memória RAM > 80%
- CPU > 90% por mais de 5 minutos
- Chrome travando ou crashando
- Muitos erros "timeout"

### ✅ Soluções:
1. Reduzir `CHUNK_SIZE`
2. Reduzir `MAX_RESULTS_PER_SEARCH`
3. Adicionar delays maiores
4. Reiniciar o bot

## 💡 Dicas de Otimização

### 1. **Priorize Quantidade vs Qualidade**
- **Máxima velocidade**: Desabilite extração de email temporariamente
- **Máxima qualidade**: Mantenha extração de email, mas aceite velocidade menor

### 2. **Use HEADLESS=true sempre**
- Economiza ~30% de RAM
- ~15% mais rápido
- Permite rodar em servidor sem interface gráfica

### 3. **Monitore os logs**
- Verifique quantas empresas estão sendo salvas vs ignoradas
- Se muitas estão duplicadas, você pode estar raspando as mesmas áreas

### 4. **Backup Regular**
- O banco de dados SQLite é um arquivo único
- Faça backup a cada 1000 empresas:
  ```bash
  cp database/empresas.db database/backup_empresas_$(date +%Y%m%d_%H%M%S).db
  ```

## 🎓 Conclusão

### **Valor Máximo Recomendado**:

| Cenário | Max Seguro | Max Absoluto |
|---------|-----------|--------------|
| **Por busca** | 100 empresas | 120 empresas |
| **Por sessão** | 1.000 empresas | 5.000 empresas |
| **Por dia** | 5.000 empresas | 20.000 empresas |
| **No banco total** | Ilimitado | 10M+ registros |

**Recomendação Final**:
- Para uso normal: **50-100 empresas por busca**
- Para grandes volumes: **Divida em múltiplas buscas específicas**
- **Sempre use HEADLESS=true** para melhor performance
- **Monitore memória e CPU** para ajustar configurações

---

**Nota**: O limite real depende do seu hardware, conexão de internet e se o Google começar a bloquear requisições. Sempre comece com valores conservadores e aumente gradualmente.
