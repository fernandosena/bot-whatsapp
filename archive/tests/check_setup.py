#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de verificação do ambiente
Verifica se todas as dependências estão instaladas corretamente
"""

import sys
import os

print("🔍 Verificando instalação do Bot de Pesquisa de Empresas...\n")

errors = []
warnings = []

# Verificar Python
print("✓ Python version:", sys.version.split()[0])

# Verificar módulos essenciais
modules = [
    ('selenium', 'Selenium'),
    ('webdriver_manager', 'WebDriver Manager'),
    ('bs4', 'BeautifulSoup4'),
    ('requests', 'Requests'),
    ('dotenv', 'Python-dotenv'),
    ('flask', 'Flask'),
    ('flask_socketio', 'Flask-SocketIO'),
    ('openpyxl', 'OpenPyXL'),
    ('pandas', 'Pandas'),
]

print("\n📦 Verificando módulos Python:")
for module, name in modules:
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name} - NÃO INSTALADO")
        errors.append(f"{name} não está instalado")

# Verificar navegadores
print("\n🌐 Verificando navegadores:")
browsers = [
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
]

browser_found = False
for browser in browsers:
    if os.path.exists(browser):
        print(f"  ✓ Navegador encontrado: {browser}")
        browser_found = True
        break

if not browser_found:
    print("  ⚠ Nenhum navegador Chrome/Chromium encontrado")
    warnings.append("Instale Chrome ou Chromium: sudo apt install chromium-browser")

# Verificar estrutura de diretórios
print("\n📁 Verificando estrutura do projeto:")
dirs = ['src', 'src/database', 'src/scraper', 'src/utils', 'templates']
for dir_path in dirs:
    if os.path.exists(dir_path):
        print(f"  ✓ {dir_path}/")
    else:
        print(f"  ✗ {dir_path}/ - NÃO ENCONTRADO")
        errors.append(f"Diretório {dir_path} não encontrado")

# Verificar arquivos principais
print("\n📄 Verificando arquivos principais:")
files = [
    'app.py',
    'main.py',
    'requirements.txt',
    'src/database/db.py',
    'src/scraper/google_maps_scraper.py',
    'templates/index.html',
]

for file_path in files:
    if os.path.exists(file_path):
        print(f"  ✓ {file_path}")
    else:
        print(f"  ✗ {file_path} - NÃO ENCONTRADO")
        errors.append(f"Arquivo {file_path} não encontrado")

# Verificar .env
print("\n⚙️  Verificando configurações:")
if os.path.exists('.env'):
    print("  ✓ Arquivo .env existe")
else:
    print("  ⚠ Arquivo .env não encontrado (usando .env.example como base)")
    warnings.append("Crie um arquivo .env baseado em .env.example")

# Resumo
print("\n" + "="*60)
if errors:
    print("❌ ERROS ENCONTRADOS:")
    for error in errors:
        print(f"  - {error}")
    print("\n💡 Execute: pip install -r requirements.txt")
    sys.exit(1)
elif warnings:
    print("⚠️  AVISOS:")
    for warning in warnings:
        print(f"  - {warning}")
    print("\n✅ Ambiente configurado com avisos!")
    print("   O bot deve funcionar, mas considere resolver os avisos.")
else:
    print("✅ AMBIENTE TOTALMENTE CONFIGURADO!")
    print("\n🚀 Você pode iniciar o bot:")
    print("   Interface Web: python app.py")
    print("   Terminal CLI:  python main.py")
    print("   Script auto:   ./run.sh")

print("="*60 + "\n")
