# 🚀 Guia de Busca Expandida - Google Maps

## 🤔 Por que o Google Maps limita os resultados?

O Google Maps tem um **limite técnico de ~120-400 empresas por busca**. Quando você rola a página, eventualmente ele para de carregar novos resultados, mesmo que existam mais empresas na região.

## ✅ Soluções Implementadas

### 1️⃣ **Busca por Bairros/Regiões** (Mais Eficaz)

Dividir a busca geograficamente multiplica seus resultados.

**Como funciona:**
```python
scraper.search_by_neighborhoods(
    setor="Padaria",
    cidade="Rio de Janeiro",
    neighborhoods=["Copacabana", "Ipanema", "Leblon"],
    max_results_per_neighborhood=30  # 30 x 3 = 90 empresas
)
```

**Resultado:**
- Sem divisão: ~120 empresas máximo
- Com 10 bairros: ~300-1200 empresas

**Quando usar:**
- Cidades grandes (São Paulo, Rio, etc)
- Quando precisa de cobertura completa
- Setores com muitas empresas

---

### 2️⃣ **Busca com Variações de Termos**

Usa sinônimos e termos relacionados automaticamente.

**Como funciona:**
```python
scraper.search_with_variations(
    setor="Restaurante",  # Vai buscar também: "comida caseira", "marmitaria", etc
    cidade="São Paulo",
    max_results_per_variation=30  # 30 por variação
)
```

**Variações automáticas incluem:**
- **Padaria**: padaria artesanal, pães e doces, confeitaria, padaria delivery
- **Restaurante**: restaurante delivery, comida caseira, marmitaria, food truck
- **Farmácia**: drogaria, farmácia de manipulação, farmácia 24h
- **Pet Shop**: clínica veterinária, banho e tosa, produtos para pets
- **Academia**: crossfit, estúdio de pilates, box de luta, personal trainer
- E mais...

**Quando usar:**
- Setores com múltiplos nomes/variações
- Quando quer capturar nichos específicos
- Para aumentar diversidade

---

### 3️⃣ **Combinação: Bairros + Variações** (Mais Poderoso)

Combina as duas estratégias para resultados máximos.

**Exemplo:**
```python
variacoes = ["Farmácia", "Drogaria", "Farmácia 24h"]
bairros = ["Centro", "Zona Sul", "Zona Norte"]

# 3 variações x 3 bairros x 20 resultados = ~180 empresas únicas
```

**Quando usar:**
- Quando precisa do maior número possível
- Projetos comerciais/vendas
- Análise de mercado completa

---

### 4️⃣ **Detecção Inteligente de Limite**

O sistema agora detecta quando o Google Maps parou de carregar e avisa:

```
⚠️  Google Maps atingiu o limite de resultados (127 empresas)
💡 Dica: Para encontrar mais empresas:
   • Divida por bairros/regiões
   • Use termos de busca mais específicos
   • Tente variações do setor
```

---

## 📊 Comparação de Resultados

| Método | Empresas Encontradas | Tempo | Complexidade |
|--------|---------------------|-------|--------------|
| Busca Normal | 120-400 | ⚡ Rápido | Simples |
| Por Bairros (10) | 300-1200 | ⚡⚡ Médio | Média |
| Com Variações (4) | 200-800 | ⚡⚡ Médio | Média |
| Combinado (10 bairros x 4 variações) | 1000-5000 | ⚡⚡⚡ Lento | Complexa |

---

## 🎯 Exemplos Práticos

### Exemplo 1: Padarias no Rio (Máximo de resultados)
```python
bairros_zona_sul = ["Copacabana", "Ipanema", "Leblon", "Botafogo"]
bairros_zona_norte = ["Tijuca", "Grajaú", "Vila Isabel"]
bairros_centro = ["Centro", "Lapa", "Santa Teresa"]

scraper.search_by_neighborhoods(
    setor="Padaria",
    cidade="Rio de Janeiro",
    neighborhoods=bairros_zona_sul + bairros_zona_norte + bairros_centro,
    max_results_per_neighborhood=30
)
# Resultado: ~330 empresas únicas
```

### Exemplo 2: Restaurantes em SP (Com variações)
```python
scraper.search_with_variations(
    setor="Restaurante",
    cidade="São Paulo",
    max_results_per_variation=50
)
# Busca automática por: restaurante, restaurante delivery,
# comida caseira, marmitaria, food truck
# Resultado: ~200 empresas únicas
```

### Exemplo 3: Farmácias em BH (Estratégia combinada)
```python
# Máxima cobertura
bairros = ["Centro", "Savassi", "Pampulha", "Barreiro"]
variacoes = ["Farmácia", "Drogaria", "Farmácia 24h"]

# Código no exemplo_busca_expandida.py
# Resultado: ~250 empresas únicas
```

---

## 💡 Dicas de Uso

### ✅ Boas Práticas

1. **Comece pequeno**: Teste com 2-3 bairros primeiro
2. **Use filtros**: Ative apenas os contatos que precisa (WhatsApp, Telefone, etc)
3. **Seja específico**: "Padaria artesanal" é melhor que só "Padaria"
4. **Evite duplicação**: O sistema já filtra duplicatas automaticamente
5. **Use checkpoints**: As buscas são salvas e podem ser retomadas

### ⚠️ Evite

1. Buscar TODOS os bairros de cidades muito grandes (pode demorar horas)
2. Usar variações muito genéricas ("comércio", "loja")
3. Executar múltiplas buscas paralelas (pode ser bloqueado)

---

## 🔧 Como Usar

### Opção 1: Script Interativo
```bash
python3 exemplo_busca_expandida.py
```

### Opção 2: Integrar no seu código
```python
from src.scraper.google_maps_scraper import GoogleMapsScraper
from src.database.db import Database

db = Database()

with GoogleMapsScraper(headless=True) as scraper:
    # Escolha um dos métodos acima
    empresas = scraper.search_by_neighborhoods(...)
```

---

## 🚀 Próximos Passos

Outras opções para expandir ainda mais:

1. **Google Places API** (Oficial, sem limites)
   - Requer cadastro e chave API
   - Cobrado por requisição (~$17 por 1000 empresas)
   - Mais confiável e rápido

2. **Múltiplas Cidades**
   - Buscar em cidades vizinhas
   - Região metropolitana

3. **Outras Plataformas**
   - Bing Maps
   - Yellow Pages
   - Redes sociais (Instagram, Facebook)

---

## ❓ FAQ

**P: Quanto tempo demora?**
R: ~0.8s por empresa. Para 500 empresas: ~7 minutos.

**P: Posso ser bloqueado?**
R: Risco baixo, mas use delays e não abuse (max 1000-2000 empresas/dia).

**P: Os checkpoints funcionam com bairros?**
R: Sim! Cada combinação setor+cidade tem seu checkpoint.

**P: Como resetar checkpoint?**
R: Use o menu principal ou `db.reset_checkpoint(setor, cidade)`.

---

## 📞 Suporte

Dúvidas ou problemas? Abra uma issue no repositório!
