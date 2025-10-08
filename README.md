# 🤖 Bot de Pesquisa de Empresas

Bot automatizado para pesquisar empresas de um setor específico em determinada cidade usando Google Maps com Selenium, extraindo dados de contato e salvando em banco de dados SQLite.

## 📋 Funcionalidades

- ✅ Busca automatizada de empresas no Google Maps
- 📞 Extração de dados de contato:
  - Nome da empresa
  - Endereço
  - Telefone
  - WhatsApp (formato internacional)
  - Email (extraído do website)
  - Website
  - **Redes Sociais** (Instagram, Facebook, LinkedIn, Twitter/X)
  - Avaliação e número de reviews
  - Horário de funcionamento
  - URL do Google Maps
- 💾 Armazenamento em banco de dados SQLite
- 🔄 **Processamento em tempo real**: Extrai e salva dados empresa por empresa
- ✨ **Validação inteligente**: Só salva empresas com pelo menos um dado de contato (telefone, email ou WhatsApp)
- 🔄 **Atualização automática**: Se a empresa já existe, atualiza apenas campos vazios com novos dados
- 📊 Estatísticas de coleta
- 📤 Exportação para CSV
- 📝 Sistema de logs

## 🚀 Instalação Rápida

### Script Automático (Linux/Mac)

```bash
./run.sh
```

O script irá:
- Criar ambiente virtual automaticamente
- Instalar todas as dependências
- Perguntar qual modo executar (Web ou CLI)

### Instalação Manual

#### Pré-requisitos

- Python 3.8+ instalado
- pip (gerenciador de pacotes Python)
- Google Chrome ou Chromium instalado

#### Passos

1. Clone ou baixe o projeto

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env` (opcional):
```bash
cp .env.example .env
```

Edite o `.env` se desejar alterar configurações padrão.

## 🔄 Migração do Banco de Dados

Se você já tem um banco de dados existente e quer adicionar suporte para redes sociais, execute:

```bash
python migrate_db.py
```

Isso adicionará as colunas `instagram`, `facebook`, `linkedin` e `twitter` ao banco de dados sem perder nenhum dado existente.

## 💻 Como Usar

### Opção 1: Interface Web (Recomendado)

A interface web oferece controle completo do bot com uma interface moderna e intuitiva:

```bash
# Instalar dependências web
pip install flask flask-socketio flask-cors openpyxl pandas eventlet

# Iniciar servidor web
python app.py
```

Acesse em seu navegador: **http://localhost:5000**

#### Funcionalidades da Interface Web:

- 📊 **Dashboard em tempo real** com estatísticas
- 🚀 **Controle do bot** direto pelo navegador
- 📈 **Barra de progresso** ao vivo durante a busca
- 🔍 **Filtros avançados** (setor, cidade, com email, telefone, WhatsApp)
- 📥 **Exportação** para Excel e CSV com filtros aplicados
- ✅ **Seleção múltipla** de empresas com checkboxes
- 🗑️ **Exclusão em massa** - Deletar várias empresas selecionadas de uma vez
- 🧹 **Limpar base de dados** - Remover todos os registros com confirmação dupla
- 🗂️ **Gerenciamento individual** - Deletar empresas uma por uma
- ⏸️ **Parar/Iniciar** busca em tempo real
- 🔄 **Atualização automática** das estatísticas

### Opção 2: Terminal (CLI)

```bash
python main.py
```

#### Menu Principal

1. **🔍 Buscar empresas** - Inicia uma nova busca
2. **📊 Ver estatísticas** - Mostra estatísticas das empresas coletadas
3. **📋 Listar empresas salvas** - Lista e exporta empresas do banco de dados
4. **🚪 Sair** - Encerra o bot

## 📁 Estrutura do Projeto

```
bot/
├── src/
│   ├── database/
│   │   └── db.py                    # Módulo do banco de dados
│   ├── scraper/
│   │   └── google_maps_scraper.py   # Scraper com Selenium
│   ├── utils/
│   │   └── logger.py                # Sistema de logs
├── templates/
│   └── index.html                   # Interface web
├── database/
│   └── empresas.db                  # Banco SQLite (gerado automaticamente)
├── logs/
│   └── bot-YYYY-MM-DD.log           # Logs diários (gerado automaticamente)
├── exports/
│   └── empresas_*.csv               # Arquivos CSV exportados
├── .env.example                     # Exemplo de configuração
├── .gitignore
├── requirements.txt                 # Dependências Python
├── app.py                           # Aplicação web (Flask)
├── main.py                          # Aplicação CLI (terminal)
└── README.md
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: `empresas`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único (auto incremento) |
| nome | TEXT | Nome da empresa |
| setor | TEXT | Setor/categoria da empresa |
| cidade | TEXT | Cidade |
| endereco | TEXT | Endereço completo |
| telefone | TEXT | Telefone |
| whatsapp | TEXT | WhatsApp (formato internacional) |
| email | TEXT | Email |
| website | TEXT | Website |
| instagram | TEXT | Link do Instagram |
| facebook | TEXT | Link do Facebook |
| linkedin | TEXT | Link do LinkedIn |
| twitter | TEXT | Link do Twitter/X |
| google_maps_url | TEXT | URL do Google Maps |
| rating | REAL | Avaliação (0-5) |
| total_reviews | INTEGER | Número total de avaliações |
| horario_funcionamento | TEXT | Horário de funcionamento |
| latitude | REAL | Latitude |
| longitude | REAL | Longitude |
| data_criacao | TIMESTAMP | Data de criação do registro |
| data_atualizacao | TIMESTAMP | Data da última atualização |

## 📊 Exportação de Dados

O bot permite exportar os dados coletados para CSV com todos os campos disponíveis. Os arquivos são salvos na pasta `exports/`.

### Formato do CSV

```csv
Nome,Setor,Cidade,Endereço,Telefone,WhatsApp,Email,Website,Rating,Reviews,URL Google Maps
"Empresa XYZ","lanchonetes","São Paulo","Rua ABC, 123","(11) 1234-5678","5511123456789","contato@empresa.com","https://empresa.com","4.5","120","https://maps.google.com/..."
```

## ⚙️ Tecnologias Utilizadas

- **Python 3.8+** - Linguagem de programação
- **Selenium** - Automação de navegador (web scraping)
- **WebDriver Manager** - Gerenciamento automático do ChromeDriver
- **SQLite3** - Banco de dados
- **BeautifulSoup4** - Parsing de HTML
- **Requests** - Requisições HTTP
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 🔧 Configurações

### Variáveis de Ambiente (.env)

```env
# Executar em modo headless (sem abrir janela do navegador)
HEADLESS=True

# Configurações padrão
DEFAULT_SECTOR=lanchonetes
DEFAULT_CITY=São Paulo

# Caminho do banco de dados
DB_PATH=./database/empresas.db

# Tempo de espera (segundos)
WAIT_TIME=2
PAGE_LOAD_TIMEOUT=30
```

### Ajustar quantidade de resultados

Ao buscar empresas, você pode especificar quantos resultados deseja coletar (padrão: 50).

### Modo Headless

Por padrão, o bot roda em modo headless (sem abrir janela do navegador). Para ver o navegador em ação, altere no `.env`:

```env
HEADLESS=False
```

## ⚠️ Considerações Importantes

### Uso Responsável

- Este bot é para fins educacionais e de pesquisa
- Respeite os Termos de Serviço do Google Maps
- Use com moderação para evitar bloqueios de IP
- Não sobrecarregue os servidores com requisições excessivas

### Limitações

- A extração de emails depende da disponibilidade no website da empresa
- Alguns dados podem não estar disponíveis para todas as empresas
- O Google pode bloquear requisições automatizadas em excesso
- A estrutura do HTML do Google Maps pode mudar, exigindo atualizações no código

## 🐛 Resolução de Problemas

### Erro ao iniciar o Selenium

O bot usa `webdriver-manager` que baixa automaticamente o ChromeDriver. Certifique-se de ter o Google Chrome instalado.

### Erro: "ChromeDriver incompatível"

```bash
pip install --upgrade webdriver-manager selenium
```

### Banco de dados travado

Se o banco de dados estiver travado, feche todas as conexões e reinicie o bot.

### Nenhum resultado encontrado

- Verifique a ortografia do setor e cidade
- Tente termos mais genéricos
- Verifique sua conexão com a internet
- Aumente o tempo de espera no código

### Erro de timeout

Aumente o `PAGE_LOAD_TIMEOUT` no arquivo `.env` ou diretamente no código.

### Erro "Stale Element Reference"

Esse erro acontece quando o DOM do Google Maps é atualizado enquanto o bot está processando. O bot já possui:
- ✅ **Sistema de retry automático** (3 tentativas)
- ✅ **Re-obtenção de elementos** a cada iteração
- ✅ **Delays estratégicos** para estabilização do DOM

Se ainda ocorrer, tente:
- Reduzir a velocidade aumentando os delays no código
- Processar menos empresas por vez (ex: 20 ao invés de 50)

## 📝 Logs

Os logs são salvos automaticamente na pasta `logs/` com o formato:

```
logs/bot-2025-10-07.log
```

Cada log contém timestamp, nível e mensagem:

```
[2025-10-07 20:00:00,000] [INFO] Bot iniciado
[2025-10-07 20:05:30,000] [INFO] ✅ Busca concluída: 25 empresas salvas
```

## 🔒 Privacidade e Segurança

- Os dados coletados são armazenados localmente em seu computador
- Nenhuma informação é enviada para servidores externos
- Use os dados coletados de forma ética e responsável
- Respeite as leis de proteção de dados (LGPD, GDPR, etc.)

## 🤝 Contribuindo

Sinta-se à vontade para fazer fork do projeto e enviar pull requests com melhorias!

### Possíveis melhorias futuras:

- [ ] Suporte para outras plataformas (Bing Maps, Yellow Pages, etc.)
- [ ] Validação de emails em tempo real
- [ ] Extração de redes sociais (Instagram, Facebook)
- [ ] Notificações por email/WhatsApp
- [ ] Agendamento de buscas automáticas
- [ ] API REST pública
- [ ] Integração com CRM

## 📄 Licença

ISC License

## ✨ Autor

Bot desenvolvido com Python e Selenium para automação de pesquisa de empresas e coleta de dados de contato.

---

**Nota:** Use este bot de forma ética e responsável, respeitando a privacidade e os termos de serviço das plataformas utilizadas.
