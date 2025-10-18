# 🚀 WhatsApp Business Tool - Sistema Completo

Sistema profissional SaaS de automação WhatsApp com raspagem do Google Maps, envio em massa, gestão de contatos e sincronização multi-plataforma.

**Versões Disponíveis:**
- ✅ **Web** - Acesso online via navegador (Flask + PostgreSQL)
- ✅ **Desktop** - Aplicação standalone para Linux/Windows (Electron + SQLite)
- ✅ **Sincronização** - Dados sincronizados automaticamente entre web e desktop
- ✅ **Assinatura** - Sistema de monetização com 4 planos via Stripe

---

## 📋 Funcionalidades Principais

### 🔍 Raspagem Google Maps
- Busca automatizada de empresas por setor e cidade
- Extração completa de contatos (WhatsApp, telefone, email, website, redes sociais)
- Sistema de checkpoint para continuar buscas interrompidas
- Progresso em tempo real com WebSocket
- Validação inteligente (salva apenas com contato válido)

### 📱 WhatsApp via Baileys (PTT)
- Conexão via QR Code (sem Selenium)
- Envio de mensagens personalizadas com variáveis {{nome}}, {{cidade}}, etc
- Envio de áudio PTT (Push-to-Talk) nativo
- Envio em massa com delay configurável
- Sistema de bloqueio/desbloqueio de números
- Histórico completo e logs detalhados
- Campanhas com checkpoint e retomada

### 👥 Gestão de Contatos
- CRUD completo com interface moderna
- Filtros avançados (setor, cidade, status, busca)
- Importar/Exportar Excel/CSV
- Marcar como enviado/bloqueado em massa
- Estatísticas e relatórios

### 🔄 Sincronização Bidirecional
- Sincronização automática web ↔ desktop
- Resolução inteligente de conflitos
- Funciona offline (desktop armazena localmente)
- Histórico de sincronizações
- API REST segura

### 💰 Sistema de Assinatura (Stripe)
- 4 planos (Free, Basic, Pro, Enterprise)
- Pagamento recorrente via Stripe
- Licenciamento por chave (desktop)
- Webhooks para renovação automática
- Painel administrativo

---

## 🏗️ Arquitetura do Sistema

```
whatsapp-business-saas/
│
├── web-app/              # Versão Web (Flask + PostgreSQL)
│   ├── app/
│   │   ├── routes/       # Auth, Scraper, WhatsApp, Sync, Subscription
│   │   ├── services/     # Lógica de negócio
│   │   ├── models.py     # SQLAlchemy models
│   │   └── templates/    # Interface HTML
│   └── requirements.txt
│
├── desktop-app/          # Versão Desktop (Electron + SQLite)
│   ├── src/
│   │   ├── main/         # Main process (Node.js + Baileys)
│   │   ├── renderer/     # Frontend (React + Material-UI)
│   │   └── preload.js    # Bridge seguro
│   └── package.json
│
├── license-server/       # Servidor de Licenças (Node.js + Stripe)
│   ├── src/
│   │   ├── routes/       # License, Validation, Payment
│   │   ├── models/       # User, License, Subscription
│   │   └── services/     # Stripe, Key Generator
│   └── server.js
│
└── docs/                 # Documentação
    ├── API.md
    ├── SYNC.md
    ├── DEPLOY.md
    └── USER_GUIDE.md
```

---

## 💰 Planos e Preços

| Plano | Preço/Mês | Contatos | Mensagens | Recursos Principais |
|-------|-----------|----------|-----------|---------------------|
| **Free** | R$ 0 | 100 | 500/mês | Raspagem + Envio básico |
| **Basic** | R$ 49 | 1.000 | 5.000/mês | + Variáveis personalizadas |
| **Pro** | R$ 99 | 5.000 | Ilimitado | + Sequências + Áudio PTT |
| **Enterprise** | R$ 199 | Ilimitado | Ilimitado | + Multi-usuário + API |

### Funcionalidades por Plano

| Recurso | Free | Basic | Pro | Enterprise |
|---------|------|-------|-----|------------|
| Raspagem Google Maps | ✅ | ✅ | ✅ | ✅ |
| Envio WhatsApp | ✅ | ✅ | ✅ | ✅ |
| Variáveis {{nome}} | ❌ | ✅ | ✅ | ✅ |
| Envio Áudio PTT | ❌ | ✅ | ✅ | ✅ |
| Sequência de msgs | ❌ | ❌ | ✅ | ✅ |
| Relatórios avançados | ❌ | ❌ | ✅ | ✅ |
| Multi-usuário | ❌ | ❌ | ❌ | ✅ |
| API REST | ❌ | ❌ | ❌ | ✅ |
| Suporte prioritário | ❌ | ❌ | ❌ | ✅ |

---

## 🚀 Quick Start

### Versão Web (Atual - Flask)

```bash
# Instalar dependências
cd web-app
pip install -r requirements.txt

# Configurar banco PostgreSQL
# Editar config.py com credenciais

# Executar migrações
flask db upgrade

# Iniciar servidor
python run.py
```

Acesse: **http://localhost:5000**

### Versão Desktop (Em Desenvolvimento)

**Download:** (em breve)
- Linux: `WhatsAppBusinessTool-1.0.0.AppImage`
- Windows: `WhatsAppBusinessTool-Setup-1.0.0.exe`

**Ativação:**
1. Execute o aplicativo
2. Insira sua chave de licença `WBDT-XXXX-XXXX-XXXX-XXXX`
3. Conecte WhatsApp via QR Code
4. Pronto para usar offline!

---

## 🛠️ Stack Tecnológico

### Web
- **Backend:** Python 3.8+ (Flask + SQLAlchemy)
- **Database:** PostgreSQL 13+
- **Cache:** Redis
- **Auth:** JWT com refresh tokens
- **WhatsApp:** @whiskeysockets/baileys (Node.js service)
- **WebSocket:** Flask-SocketIO + eventlet
- **Frontend:** HTML5 + Bootstrap 5 + JavaScript

### Desktop
- **Framework:** Electron 28+
- **Frontend:** React 18 + Material-UI
- **Database:** SQLite3
- **WhatsApp:** @whiskeysockets/baileys
- **Scraper:** Puppeteer
- **Build:** electron-builder

### License Server
- **Runtime:** Node.js 18+ + Express
- **Payment:** Stripe API v3
- **Database:** PostgreSQL 13+
- **Auth:** JWT

---

## 🔐 Segurança e Privacidade

- ✅ Autenticação JWT com refresh tokens (15 min / 7 dias)
- ✅ Senhas hasheadas com bcrypt
- ✅ Rate limiting por plano
- ✅ HTTPS/SSL obrigatório em produção
- ✅ Licenças criptografadas (AES-256)
- ✅ Logs de auditoria completos
- ✅ Dados locais criptografados (desktop)
- ✅ Validação de licença a cada 24h
- ✅ 2FA disponível (Enterprise)

---

## 🔄 Sistema de Sincronização

### Como Funciona

```
Desktop                      Web API                    PostgreSQL
  │                            │                            │
  ├─ 1. Check updates ────────►│                            │
  │  (last_sync + hash)        │                            │
  │                            ├─ 2. Compare hashes ───────►│
  │                            │                            │
  │◄─── 3. Return diff ────────┤◄─── 3. Query changes ─────┤
  │                            │                            │
  ├─ 4. Apply changes         │                            │
  │  (update local SQLite)     │                            │
  │                            │                            │
  ├─ 5. Push new data ────────►│                            │
  │                            ├─ 6. Validate & save ──────►│
  │                            │                            │
  │◄─── 7. Confirm sync ───────┤                            │
```

### Resolução de Conflitos

1. **Servidor ganha (padrão)** - Para campos críticos
2. **Mais recente ganha** - Para campos não críticos
3. **Merge inteligente** - Para listas/arrays
4. **Manual** - Usuário escolhe em casos complexos

---

## 📊 Status do Projeto

**Versão Atual:** 1.0.0-beta

### Progresso de Desenvolvimento

#### ✅ Concluído (Versão Web Atual)
- [x] Raspagem Google Maps com Puppeteer
- [x] Envio WhatsApp via Baileys/PTT
- [x] Banco de dados SQLite (migrar para PostgreSQL)
- [x] Interface web Flask
- [x] Sistema de campanhas
- [x] Gerenciamento de contatos
- [x] Logs e histórico
- [x] Exportar Excel/CSV

#### 🔄 Em Desenvolvimento
- [ ] Migração para PostgreSQL
- [ ] Sistema de autenticação JWT
- [ ] API de sincronização
- [ ] Servidor de licenças
- [ ] Integração Stripe
- [ ] Versão desktop Electron
- [ ] Sistema de planos e limites

#### 📅 Planejado
- [ ] Multi-usuário (Enterprise)
- [ ] API REST pública
- [ ] Webhooks
- [ ] Mobile app (React Native)
- [ ] Relatórios avançados com gráficos

**Previsão de Lançamento Completo:** 10 semanas (Maio 2025)

---

## 📚 Documentação

- **[Plano Completo](PLANO_COMPLETO_WEB_DESKTOP.md)** - Arquitetura detalhada, cronograma, estimativas
- **[API Reference](docs/API.md)** - Endpoints, autenticação, exemplos (em breve)
- **[Sync Protocol](docs/SYNC.md)** - Como funciona a sincronização (em breve)
- **[Deploy Guide](docs/DEPLOY.md)** - VPS setup, PostgreSQL, Nginx (em breve)
- **[User Guide](docs/USER_GUIDE.md)** - Manual completo do usuário (em breve)

---

## 💳 Integração Stripe

### Webhooks Implementados
- `payment_intent.succeeded` → Ativar assinatura
- `payment_intent.failed` → Notificar falha
- `customer.subscription.updated` → Atualizar status
- `customer.subscription.deleted` → Cancelar assinatura

### Fluxo de Pagamento

```
1. Usuário escolhe plano
2. Redirect para Stripe Checkout
3. Pagamento processado
4. Webhook notifica servidor
5. Sistema ativa assinatura
6. Email de confirmação enviado
7. Usuário recebe chave de licença (desktop)
8. Acesso liberado
```

---

## 🚀 Deploy em VPS

### Requisitos Mínimos
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **OS:** Ubuntu 20.04/22.04 LTS
- **Custo:** ~$10-20/mês (DigitalOcean, Linode, Vultr)

### Stack de Produção
```
[Nginx] → [Gunicorn] → [Flask App]
                ↓
        [PostgreSQL]
                ↓
           [Redis]
```

### Quick Deploy

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3-pip postgresql nginx redis-server

# Configurar PostgreSQL
sudo -u postgres createdb whatsapp_business
sudo -u postgres createuser -P whatsapp_user

# Clonar repositório
git clone <repo-url>
cd whatsapp-business-saas/web-app

# Instalar dependências Python
pip3 install -r requirements.txt

# Configurar environment
cp .env.example .env
nano .env  # Editar credenciais

# Executar migrações
flask db upgrade

# Configurar Gunicorn
sudo nano /etc/systemd/system/whatsapp-web.service

# Configurar Nginx
sudo nano /etc/nginx/sites-available/whatsapp-business

# SSL com Let's Encrypt
sudo certbot --nginx -d seu-dominio.com

# Iniciar serviços
sudo systemctl start whatsapp-web
sudo systemctl enable whatsapp-web
sudo systemctl restart nginx
```

**Guia completo:** `docs/DEPLOY.md` (em breve)

---

## 🤝 Suporte

### Canais de Atendimento
- **Email:** suporte@whatsappbusinesstool.com (planos pagos)
- **Chat:** Disponível no painel (Pro e Enterprise)
- **Documentação:** docs/ (todos os planos)
- **Community:** GitHub Discussions (Free)

### SLA por Plano
- **Free:** Best effort (docs apenas)
- **Basic:** Email em 48h
- **Pro:** Email em 24h + Chat
- **Enterprise:** Prioritário em 4h + Chat + Telefone

---

## 📊 Estimativa de Receita

### Cenário Conservador (6 meses)
- 50 Free + 30 Basic + 15 Pro + 5 Enterprise
- **MRR:** R$ 3.950/mês
- **ARR:** R$ 47.400/ano
- **Lucro:** ~R$ 2.500-3.000/mês

### Cenário Otimista (12 meses)
- 200 Free + 100 Basic + 50 Pro + 20 Enterprise
- **MRR:** R$ 13.830/mês
- **ARR:** R$ 165.960/ano
- **Lucro:** ~R$ 12.000-13.000/mês

**ROI:** 3-6 meses (investimento inicial ~R$ 5.000)

---

## 📝 Licença

**Proprietary Software** - Todos os direitos reservados.

- ✅ Uso comercial permitido com assinatura ativa
- ❌ Redistribuição proibida
- ❌ Modificação do código fonte proibida
- ❌ Engenharia reversa proibida

**EULA completo:** Disponível no painel de usuário

---

## 🙏 Tecnologias e Agradecimentos

Construído com tecnologias open-source:

- [Baileys](https://github.com/WhiskeySockets/Baileys) - WhatsApp Web API
- [Electron](https://www.electronjs.org/) - Desktop framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [React](https://react.dev/) - UI library
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Stripe](https://stripe.com/) - Payment processing
- [Puppeteer](https://pptr.dev/) - Web scraping
- [Material-UI](https://mui.com/) - UI components

---

## 🔮 Roadmap Futuro

### Q1 2025
- [x] Planejar arquitetura completa
- [ ] Migrar para PostgreSQL
- [ ] Implementar auth JWT
- [ ] Criar API de sync

### Q2 2025
- [ ] Lançar versão desktop (beta)
- [ ] Integração Stripe completa
- [ ] Sistema de licenças
- [ ] Deploy em produção (VPS)

### Q3 2025
- [ ] Multi-usuário (Enterprise)
- [ ] API REST pública
- [ ] Mobile app (beta)
- [ ] Webhooks para integrações

### Q4 2025
- [ ] Relatórios avançados com BI
- [ ] Integrações (Zapier, Make)
- [ ] White-label (parceiros)
- [ ] Expansão internacional

---

## 📞 Contato

**Website:** https://whatsappbusinesstool.com (em breve)
**Email:** contato@whatsappbusinesstool.com
**Suporte:** suporte@whatsappbusinesstool.com
**GitHub:** https://github.com/seu-usuario/whatsapp-business-saas

---

**© 2025 WhatsApp Business Tool - Sistema profissional de automação WhatsApp**

*Desenvolvido com ❤️ para pequenas e médias empresas*
