# 🚀 Guia Rápido de Início

## Instalação em 3 Passos

### 1️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Escolher modo de execução

**Interface Web (Recomendado):**
```bash
python app.py
```
Acesse: http://localhost:5000

**Terminal (CLI):**
```bash
python main.py
```

### 3️⃣ Usar o bot

#### Via Interface Web:

1. Abra o navegador em `http://localhost:5000`
2. Preencha o setor (ex: lanchonetes) e cidade (ex: São Paulo)
3. Clique em "Iniciar Busca"
4. Acompanhe o progresso em tempo real
5. Use os filtros para refinar resultados
6. Exporte para Excel ou CSV

#### Via Terminal:

1. Escolha opção "1" para buscar empresas
2. Digite setor e cidade
3. Aguarde a coleta
4. Escolha opção "3" para listar e exportar

## 🎯 Funcionalidades Principais

### Interface Web

| Funcionalidade | Descrição |
|---------------|-----------|
| 📊 Dashboard | Estatísticas em tempo real |
| 🚀 Buscar | Iniciar/parar busca com progresso ao vivo |
| 🔍 Filtrar | Por setor, cidade, email, telefone, WhatsApp |
| 📥 Exportar | Excel e CSV com filtros aplicados |
| 🗑️ Gerenciar | Deletar empresas individualmente |

### Filtros Disponíveis

- **Por setor**: Filtra por categoria (lanchonetes, pizzarias, etc.)
- **Por cidade**: Filtra por localização
- **Com email**: Mostra apenas empresas com email
- **Com telefone**: Mostra apenas empresas com telefone
- **Com WhatsApp**: Mostra apenas empresas com WhatsApp
- **Busca livre**: Procura no nome ou endereço

## 📥 Exportação de Dados

### Excel
- Dados organizados em planilha
- Pronto para análise
- Formato `.xlsx`

### CSV
- Formato universal
- Compatível com qualquer sistema
- Encoding UTF-8

## 🔧 Configurações (.env)

```bash
# Modo headless (sem abrir navegador)
HEADLESS=True

# Configurações padrão
DEFAULT_SECTOR=lanchonetes
DEFAULT_CITY=São Paulo

# Caminho do banco de dados
DB_PATH=./database/empresas.db
```

## ⚡ Dicas de Uso

### Para melhores resultados:

1. **Seja específico no setor**: Use termos claros como "pizzarias" ao invés de "comida"
2. **Use cidades completas**: "São Paulo, SP" ao invés de só "SP"
3. **Ajuste a quantidade**: Comece com 20-30 empresas para testar
4. **Use filtros**: Filtre apenas empresas com contato completo
5. **Exporte regularmente**: Faça backup dos dados em Excel/CSV

### Evitar bloqueios:

- Não execute buscas muito longas (máx 100 empresas por vez)
- Aguarde alguns minutos entre buscas
- Use modo headless para economia de recursos

## 🐛 Resolução Rápida de Problemas

| Problema | Solução |
|----------|---------|
| Erro ao abrir navegador | Instale Chromium: `sudo apt install chromium-browser` |
| Timeout na busca | Aumente o tempo em `.env` |
| Poucos resultados | Tente termos mais genéricos |
| Sem dados de contato | Normal, nem toda empresa tem |

## 📞 Dados Extraídos

✅ Sempre extraído (quando disponível):
- Nome
- Endereço
- Setor
- Cidade
- URL Google Maps
- Rating
- Total de avaliações
- Horário de funcionamento

✅ Extraído quando disponível:
- Telefone
- WhatsApp (gerado do telefone)
- Email (extraído do website)
- Website

⚠️ **Importante**: O bot só salva empresas com pelo menos um dado de contato (telefone, email ou WhatsApp)

## 🎨 Interface Web - Visão Geral

### Seções Principais:

1. **Header**: Título e estatísticas gerais
2. **Controles**: Iniciar/parar busca
3. **Progresso**: Barra e estatísticas em tempo real
4. **Filtros**: Refinar resultados
5. **Tabela**: Visualizar e gerenciar empresas
6. **Exportação**: Download Excel/CSV

### Atalhos:

- `Enter` nos campos de busca: Aplicar filtros
- Scroll automático: Acompanha progresso
- Auto-refresh: Atualiza stats a cada 5s

## 📊 Exemplo de Uso Completo

```bash
# 1. Ativar ambiente
source .venv/bin/activate

# 2. Iniciar web
python app.py

# 3. No navegador (localhost:5000):
#    - Setor: lanchonetes
#    - Cidade: São Paulo
#    - Quantidade: 30
#    - Clicar "Iniciar Busca"

# 4. Aguardar processamento

# 5. Aplicar filtros:
#    ✓ Apenas com Email
#    ✓ Apenas com Telefone

# 6. Exportar para Excel
```

## 🔄 Atualização de Dados

O bot é inteligente:

- **Empresa nova**: Salva todos os dados
- **Empresa existente com novos dados**: Atualiza apenas campos vazios
- **Empresa existente sem novos dados**: Ignora
- **Empresa sem contato**: Não salva

## 🚀 Próximos Passos

Depois de dominar o básico:

1. Explore diferentes setores
2. Compare dados entre cidades
3. Crie listas segmentadas
4. Integre com seu CRM
5. Automatize buscas recorrentes

---

**Dica Final**: Comece pequeno, teste com 10-20 empresas primeiro para entender o comportamento do bot! 🎯
