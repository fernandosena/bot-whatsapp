# 💻 Requisitos do Sistema - WhatsApp Bot

## ⚠️ Importante: Interface Gráfica Necessária

O WhatsApp Bot **requer um ambiente com interface gráfica** para funcionar, pois:

1. Utiliza o **WhatsApp Web** através do navegador
2. Automatiza a interface usando `pyautogui`
3. Precisa de um display X11 (Linux) ou equivalente (Windows/Mac)

---

## 🖥️ Ambientes Suportados

### ✅ Funcionam

- **Linux Desktop** (Ubuntu, Fedora, etc.)
  - Com interface gráfica (GNOME, KDE, XFCE, etc.)
  - X11 ou Wayland

- **Windows** (10/11)
  - Sistema desktop normal

- **macOS**
  - Sistema desktop normal

### ❌ NÃO Funcionam

- **Servidores Linux sem GUI**
  - Ubuntu Server
  - Debian Server
  - CentOS/RHEL sem desktop

- **Docker containers** (sem X11)

- **SSH remoto** (sem X11 forwarding)

- **WSL sem interface gráfica**

- **Ambientes cloud** (AWS, GCP, Azure) sem desktop

---

## 🔧 Verificando seu Ambiente

### Linux

#### Verificar se tem interface gráfica:

```bash
# Verificar display
echo $DISPLAY
# Deve retornar algo como ":0" ou ":1"

# Verificar se X11 está rodando
ps aux | grep X
# Deve mostrar processos do X11
```

#### Instalar dependências necessárias:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-tk python3-dev scrot

# Fedora
sudo dnf install -y python3-tkinter python3-devel

# Arch
sudo pacman -S tk python-pip
```

### Windows

No Windows, tudo funciona normalmente. Apenas certifique-se de ter:
- Python 3.8+
- Google Chrome instalado

### macOS

No macOS, você pode precisar dar permissões de acessibilidade:

1. System Preferences → Security & Privacy → Privacy
2. Accessibility → Adicione Python/Terminal

---

## 🐧 Linux: Soluções Alternativas

### Opção 1: Executar em Desktop

Se você está em um servidor Linux, a melhor opção é:
1. Usar uma máquina com interface gráfica (seu computador pessoal)
2. Instalar o bot localmente
3. Executar de lá

### Opção 2: VNC/Remote Desktop

Configure um desktop remoto:

```bash
# Instalar VNC server
sudo apt-get install tightvncserver

# Iniciar VNC
vncserver :1

# Conectar via cliente VNC
# Use VNC Viewer para conectar em seu_ip:5901
```

### Opção 3: X11 Virtual (xvfb) - Avançado

Use um display virtual (pode ter limitações):

```bash
# Instalar xvfb
sudo apt-get install xvfb

# Executar com display virtual
xvfb-run python app.py
```

⚠️ **Nota:** O xvfb pode não funcionar perfeitamente com automação de navegador.

---

## 🔍 Testando Instalação

### 1. Testar Python e Dependências

```bash
python3 -c "import sys; print(f'Python: {sys.version}')"
python3 -c "import tkinter; print('Tkinter: OK')"
```

### 2. Testar PyAutoGUI

```bash
python3 -c "import pyautogui; print(f'Screen size: {pyautogui.size()}')"
```

Se este comando funcionar sem erros, seu ambiente está OK!

### 3. Executar Setup

```bash
python setup_whatsapp.py
```

Se o setup completar com sucesso, você está pronto para usar o bot.

---

## 🚫 Erros Comuns

### Erro: "Can't connect to display"

```
Xlib.error.DisplayConnectionError: Can't connect to display ":0"
```

**Causa:** Não há interface gráfica ou DISPLAY não está configurado

**Solução:**
1. Certifique-se de estar em um ambiente desktop
2. Verifique `echo $DISPLAY`
3. Se vazio, configure: `export DISPLAY=:0`
4. Considere usar VNC se estiver remoto

### Erro: "No module named '_tkinter'"

```
ModuleNotFoundError: No module named '_tkinter'
```

**Solução:**

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Erro: "Authorization required"

```
Authorization required, but no authorization protocol specified
```

**Solução:**

```bash
# Dar permissão ao seu usuário
xhost +local:$USER

# Ou adicionar ao .bashrc
echo "xhost +local:$USER" >> ~/.bashrc
```

---

## 📱 Alternativas ao WhatsApp Bot

Se você **não pode** usar interface gráfica, considere:

1. **APIs Oficiais:**
   - WhatsApp Business API (paga)
   - Twilio API for WhatsApp (paga)

2. **Bibliotecas Alternativas:**
   - `yowsup` (não oficial, pode ser bloqueado)
   - `whatsapp-web.js` (Node.js, requer navegador headless)

3. **Serviços de Terceiros:**
   - Zapier
   - Make (Integromat)
   - N8n

⚠️ **Atenção:** O WhatsApp pode bloquear contas que usam métodos não oficiais.

---

## 🎯 Recomendação

Para melhor experiência com o WhatsApp Bot:

1. ✅ Use em computador desktop (Linux/Windows/Mac)
2. ✅ Tenha interface gráfica ativa
3. ✅ Mantenha WhatsApp Web logado
4. ✅ Monitore o bot durante execução
5. ✅ Respeite limites de envio (30-60s delay, max 100/dia)

---

## 📞 Suporte

Se tiver problemas:

1. Verifique requisitos desta página
2. Execute os testes de diagnóstico
3. Consulte os logs em `logs/`
4. Leia `WHATSAPP_BOT_GUIDE.md`

---

## ✅ Checklist Pré-Uso

Antes de usar o WhatsApp Bot, certifique-se:

- [ ] Estou em ambiente com interface gráfica
- [ ] `echo $DISPLAY` retorna um valor (Linux)
- [ ] Python 3.8+ instalado
- [ ] Tkinter instalado (`python3-tk`)
- [ ] Chrome/Chromium instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Setup executado com sucesso (`python setup_whatsapp.py`)
- [ ] WhatsApp Web funcionando no navegador
- [ ] Li o `WHATSAPP_BOT_GUIDE.md`

Se todos os itens estão OK, você está pronto! 🚀

---

**Última atualização:** Outubro 2025
