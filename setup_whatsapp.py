#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para configurar o WhatsApp Bot
- Adiciona templates padrão
- Testa configuração
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db import Database
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def setup_templates(db):
    """Adicionar templates padrão"""
    print('📝 Criando templates padrão...\n')

    templates = [
        {
            'nome': 'Apresentação Comercial',
            'mensagem': '''Olá, {nome}!

Somos especialistas em soluções digitais para empresas de {setor}.

Notamos que você está em {cidade} e gostaríamos de apresentar nossos serviços que podem ajudar a aumentar suas vendas.

Podemos agendar uma conversa rápida?

Atenciosamente,
Equipe de Vendas''',
            'descricao': 'Template para primeira abordagem comercial'
        },
        {
            'nome': 'Follow-up',
            'mensagem': '''Olá, {nome}!

Enviei uma mensagem há alguns dias sobre nossos serviços para {setor}.

Você teve chance de ver? Gostaria de saber mais?

Estou à disposição para esclarecer qualquer dúvida.

Abraços!''',
            'descricao': 'Template para follow-up de contatos anteriores'
        },
        {
            'nome': 'Pesquisa de Mercado',
            'mensagem': '''Olá, {nome}!

Estamos realizando uma pesquisa com empresas de {setor} em {cidade}.

Gostaríamos de conhecer suas principais necessidades e desafios.

Você teria 5 minutos para responder algumas perguntas?

Sua opinião é muito importante para nós!''',
            'descricao': 'Template para pesquisa de mercado'
        },
        {
            'nome': 'Oferta Especial',
            'mensagem': '''🎉 Olá, {nome}!

Temos uma oferta exclusiva para empresas de {setor} em {cidade}!

[Descreva aqui sua oferta especial]

Esta promoção é válida por tempo limitado.

Tem interesse em saber mais detalhes?''',
            'descricao': 'Template para divulgar ofertas e promoções'
        },
        {
            'nome': 'Convite para Evento',
            'mensagem': '''Olá, {nome}!

Gostaríamos de convidar você para participar do nosso evento sobre [tema].

📅 Data: [data]
🕐 Horário: [horário]
📍 Local: [local/online]

O evento é voltado para empresas de {setor} em {cidade}.

Posso confirmar sua presença?''',
            'descricao': 'Template para convidar para eventos e webinars'
        }
    ]

    created = 0
    existing = 0

    for template_data in templates:
        result = db.create_template(
            template_data['nome'],
            template_data['mensagem'],
            template_data['descricao']
        )

        if result:
            print(f"✅ Template criado: {template_data['nome']}")
            created += 1
        else:
            print(f"ℹ️  Template já existe: {template_data['nome']}")
            existing += 1

    print(f'\n📊 Resumo:')
    print(f'   - Criados: {created}')
    print(f'   - Já existentes: {existing}')
    print(f'   - Total: {created + existing}\n')


def check_dependencies():
    """Verificar se todas as dependências estão instaladas"""
    print('🔍 Verificando dependências...\n')

    dependencies = [
        ('flask', 'flask'),
        ('flask_socketio', 'flask-socketio'),
    ]

    all_ok = True

    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f'✅ {package_name} instalado')
        except ImportError:
            print(f'❌ {package_name} NÃO instalado')
            all_ok = False

    # Verificar pywhatkit e pyautogui sem importar (evita erro de display)
    try:
        import importlib.util
        spec = importlib.util.find_spec('pywhatkit')
        if spec is not None:
            print(f'✅ pywhatkit instalado')
        else:
            print(f'❌ pywhatkit NÃO instalado')
            all_ok = False
    except:
        print(f'❌ pywhatkit NÃO instalado')
        all_ok = False

    try:
        import importlib.util
        spec = importlib.util.find_spec('pyautogui')
        if spec is not None:
            print(f'✅ pyautogui instalado')
        else:
            print(f'❌ pyautogui NÃO instalado')
            all_ok = False
    except:
        print(f'❌ pyautogui NÃO instalado')
        all_ok = False

    print()

    if not all_ok:
        print('⚠️  Algumas dependências estão faltando.')
        print('Execute: pip install -r requirements.txt\n')
        return False

    print('✅ Todas as dependências estão instaladas!\n')
    print('ℹ️  Nota: O WhatsApp Bot requer interface gráfica (X11) para funcionar.')
    print('   Certifique-se de estar em um ambiente com display gráfico ao usar o bot.\n')
    return True


def test_database():
    """Testar conexão com banco de dados"""
    print('🔍 Testando banco de dados...\n')

    try:
        db_path = os.getenv('DB_PATH', './database/empresas.db')
        db = Database(db_path)

        # Verificar se as tabelas existem
        cursor = db.cursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]

        required_tables = ['empresas', 'message_templates', 'whatsapp_logs']

        for table in required_tables:
            if table in tables:
                print(f'✅ Tabela {table} existe')
            else:
                print(f'❌ Tabela {table} não encontrada')

        print()
        db.close()
        return True

    except Exception as e:
        print(f'❌ Erro ao conectar ao banco: {e}\n')
        return False


def show_stats(db):
    """Mostrar estatísticas"""
    print('📊 Estatísticas do sistema:\n')

    # Empresas
    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas')
    total_empresas = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE whatsapp IS NOT NULL AND whatsapp != ""')
    total_whatsapp = cursor.fetchone()['total']

    print(f'   Empresas cadastradas: {total_empresas}')
    print(f'   Com WhatsApp: {total_whatsapp}')

    # Templates
    templates = db.get_all_templates()
    print(f'   Templates criados: {len(templates)}')

    # Logs WhatsApp
    stats = db.get_whatsapp_stats()
    print(f'\n   Mensagens enviadas:')
    print(f'   - Total: {stats["total"]}')
    print(f'   - Sucesso: {stats["sucesso"]}')
    print(f'   - Falhas: {stats["erro"]}')

    if stats['total'] > 0:
        taxa_sucesso = (stats['sucesso'] / stats['total'] * 100)
        print(f'   - Taxa de sucesso: {taxa_sucesso:.1f}%')

    print()


def main():
    print('╔════════════════════════════════════════════╗')
    print('║   💬 SETUP DO WHATSAPP BOT                ║')
    print('╚════════════════════════════════════════════╝\n')

    # Verificar dependências
    if not check_dependencies():
        print('❌ Configure as dependências antes de continuar.\n')
        return

    # Testar banco de dados
    if not test_database():
        print('❌ Erro ao acessar banco de dados.\n')
        return

    # Conectar ao banco
    db_path = os.getenv('DB_PATH', './database/empresas.db')
    db = Database(db_path)

    try:
        # Configurar templates
        print('═══════════════════════════════════════════════\n')
        setup_templates(db)

        # Mostrar estatísticas
        print('═══════════════════════════════════════════════\n')
        show_stats(db)

        # Instruções finais
        print('═══════════════════════════════════════════════\n')
        print('✅ Setup concluído com sucesso!\n')
        print('📖 Próximos passos:\n')
        print('   1. Inicie o servidor: python app.py')
        print('   2. Acesse: http://localhost:5000/whatsapp')
        print('   3. Faça login no WhatsApp Web')
        print('   4. Comece a enviar mensagens!\n')
        print('📚 Leia o guia completo em: WHATSAPP_BOT_GUIDE.md\n')

    finally:
        db.close()


if __name__ == '__main__':
    main()
