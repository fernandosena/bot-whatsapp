#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Monkey patch ANTES de qualquer outro import
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import io

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db import Database
from scraper.google_maps_scraper import GoogleMapsScraper
from utils.logger import Logger
from whatsapp.whatsapp_bot import WhatsAppBot
from whatsapp.whatsapp_selenium import WhatsAppSelenium

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Inicializar logger
logger = Logger()

# Banco de dados
db_path = os.getenv('DB_PATH', './database/empresas.db')
db = Database(db_path)

# Variável global para controlar o bot
bot_running = False
scraper_instance = None
whatsapp_bot_running = False
whatsapp_bot_instance = None
whatsapp_selenium_instance = None  # Instância global do Selenium WhatsApp


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/whatsapp')
def whatsapp():
    """Página do WhatsApp Bot"""
    return render_template('whatsapp.html')


@app.route('/api/empresas')
def get_empresas():
    """Listar empresas com filtros"""
    setor = request.args.get('setor', '')
    cidade = request.args.get('cidade', '')
    has_email = request.args.get('has_email', '')
    has_telefone = request.args.get('has_telefone', '')
    has_whatsapp = request.args.get('has_whatsapp', '')
    has_website = request.args.get('has_website', '')
    has_instagram = request.args.get('has_instagram', '')
    has_facebook = request.args.get('has_facebook', '')
    has_linkedin = request.args.get('has_linkedin', '')
    has_twitter = request.args.get('has_twitter', '')
    search = request.args.get('search', '')

    # Construir query base
    query = 'SELECT * FROM empresas WHERE 1=1'
    params = []

    if setor:
        query += ' AND setor LIKE ?'
        params.append(f'%{setor}%')

    if cidade:
        query += ' AND cidade LIKE ?'
        params.append(f'%{cidade}%')

    if has_email == 'true':
        query += ' AND email IS NOT NULL AND email != ""'

    if has_telefone == 'true':
        query += ' AND telefone IS NOT NULL AND telefone != ""'

    if has_whatsapp == 'true':
        query += ' AND whatsapp IS NOT NULL AND whatsapp != ""'

    if has_website == 'true':
        query += ' AND website IS NOT NULL AND website != ""'

    if has_instagram == 'true':
        query += ' AND instagram IS NOT NULL AND instagram != ""'

    if has_facebook == 'true':
        query += ' AND facebook IS NOT NULL AND facebook != ""'

    if has_linkedin == 'true':
        query += ' AND linkedin IS NOT NULL AND linkedin != ""'

    if has_twitter == 'true':
        query += ' AND twitter IS NOT NULL AND twitter != ""'

    if search:
        query += ' AND (nome LIKE ? OR endereco LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY data_criacao DESC'

    cursor = db.cursor
    cursor.execute(query, params)
    empresas = [dict(row) for row in cursor.fetchall()]

    return jsonify(empresas)


@app.route('/api/stats')
def get_stats():
    """Obter estatísticas"""
    stats = db.get_stats()

    # Estatísticas gerais
    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas')
    result = cursor.fetchone()
    total = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE email IS NOT NULL AND email != ""')
    result = cursor.fetchone()
    total_email = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE telefone IS NOT NULL AND telefone != ""')
    result = cursor.fetchone()
    total_telefone = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE whatsapp IS NOT NULL AND whatsapp != ""')
    result = cursor.fetchone()
    total_whatsapp = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE website IS NOT NULL AND website != ""')
    result = cursor.fetchone()
    total_website = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE instagram IS NOT NULL AND instagram != ""')
    result = cursor.fetchone()
    total_instagram = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE facebook IS NOT NULL AND facebook != ""')
    result = cursor.fetchone()
    total_facebook = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE linkedin IS NOT NULL AND linkedin != ""')
    result = cursor.fetchone()
    total_linkedin = result['total'] if result else 0

    cursor = db.cursor
    cursor.execute('SELECT COUNT(*) as total FROM empresas WHERE twitter IS NOT NULL AND twitter != ""')
    result = cursor.fetchone()
    total_twitter = result['total'] if result else 0

    return jsonify({
        'total': total,
        'total_email': total_email,
        'total_telefone': total_telefone,
        'total_whatsapp': total_whatsapp,
        'total_website': total_website,
        'total_instagram': total_instagram,
        'total_facebook': total_facebook,
        'total_linkedin': total_linkedin,
        'total_twitter': total_twitter,
        'by_sector': stats
    })


@app.route('/api/setores')
def get_setores():
    """Listar setores únicos"""
    cursor = db.cursor
    cursor.execute('SELECT DISTINCT setor FROM empresas ORDER BY setor')
    setores = [row['setor'] for row in cursor.fetchall()]
    return jsonify(setores)


@app.route('/api/cidades')
def get_cidades():
    """Listar cidades únicas"""
    cursor = db.cursor
    cursor.execute('SELECT DISTINCT cidade FROM empresas ORDER BY cidade')
    cidades = [row['cidade'] for row in cursor.fetchall()]
    return jsonify(cidades)


@app.route('/api/export/excel')
def export_excel():
    """Exportar para Excel"""
    setor = request.args.get('setor', '')
    cidade = request.args.get('cidade', '')
    has_email = request.args.get('has_email', '')
    has_telefone = request.args.get('has_telefone', '')
    has_whatsapp = request.args.get('has_whatsapp', '')
    has_website = request.args.get('has_website', '')
    has_instagram = request.args.get('has_instagram', '')
    has_facebook = request.args.get('has_facebook', '')
    has_linkedin = request.args.get('has_linkedin', '')
    has_twitter = request.args.get('has_twitter', '')
    search = request.args.get('search', '')

    # Construir query
    query = 'SELECT * FROM empresas WHERE 1=1'
    params = []

    if setor:
        query += ' AND setor LIKE ?'
        params.append(f'%{setor}%')

    if cidade:
        query += ' AND cidade LIKE ?'
        params.append(f'%{cidade}%')

    if has_email == 'true':
        query += ' AND email IS NOT NULL AND email != ""'

    if has_telefone == 'true':
        query += ' AND telefone IS NOT NULL AND telefone != ""'

    if has_whatsapp == 'true':
        query += ' AND whatsapp IS NOT NULL AND whatsapp != ""'

    if has_website == 'true':
        query += ' AND website IS NOT NULL AND website != ""'

    if has_instagram == 'true':
        query += ' AND instagram IS NOT NULL AND instagram != ""'

    if has_facebook == 'true':
        query += ' AND facebook IS NOT NULL AND facebook != ""'

    if has_linkedin == 'true':
        query += ' AND linkedin IS NOT NULL AND linkedin != ""'

    if has_twitter == 'true':
        query += ' AND twitter IS NOT NULL AND twitter != ""'

    if search:
        query += ' AND (nome LIKE ? OR endereco LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY data_criacao DESC'

    cursor = db.cursor
    cursor.execute(query, params)
    empresas = [dict(row) for row in cursor.fetchall()]

    # Criar DataFrame
    df = pd.DataFrame(empresas)

    # Reordenar colunas
    columns_order = [
        'id', 'nome', 'setor', 'cidade', 'endereco', 'telefone', 'whatsapp',
        'email', 'website', 'instagram', 'facebook', 'linkedin', 'twitter',
        'rating', 'total_reviews', 'horario_funcionamento',
        'google_maps_url', 'latitude', 'longitude', 'data_criacao', 'data_atualizacao'
    ]

    df = df[[col for col in columns_order if col in df.columns]]

    # Criar arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Empresas')

    output.seek(0)

    filename = f"empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/export/csv')
def export_csv():
    """Exportar para CSV"""
    setor = request.args.get('setor', '')
    cidade = request.args.get('cidade', '')
    has_email = request.args.get('has_email', '')
    has_telefone = request.args.get('has_telefone', '')
    has_whatsapp = request.args.get('has_whatsapp', '')
    has_website = request.args.get('has_website', '')
    has_instagram = request.args.get('has_instagram', '')
    has_facebook = request.args.get('has_facebook', '')
    has_linkedin = request.args.get('has_linkedin', '')
    has_twitter = request.args.get('has_twitter', '')
    search = request.args.get('search', '')

    # Construir query
    query = 'SELECT * FROM empresas WHERE 1=1'
    params = []

    if setor:
        query += ' AND setor LIKE ?'
        params.append(f'%{setor}%')

    if cidade:
        query += ' AND cidade LIKE ?'
        params.append(f'%{cidade}%')

    if has_email == 'true':
        query += ' AND email IS NOT NULL AND email != ""'

    if has_telefone == 'true':
        query += ' AND telefone IS NOT NULL AND telefone != ""'

    if has_whatsapp == 'true':
        query += ' AND whatsapp IS NOT NULL AND whatsapp != ""'

    if has_website == 'true':
        query += ' AND website IS NOT NULL AND website != ""'

    if has_instagram == 'true':
        query += ' AND instagram IS NOT NULL AND instagram != ""'

    if has_facebook == 'true':
        query += ' AND facebook IS NOT NULL AND facebook != ""'

    if has_linkedin == 'true':
        query += ' AND linkedin IS NOT NULL AND linkedin != ""'

    if has_twitter == 'true':
        query += ' AND twitter IS NOT NULL AND twitter != ""'

    if search:
        query += ' AND (nome LIKE ? OR endereco LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY data_criacao DESC'

    cursor = db.cursor
    cursor.execute(query, params)
    empresas = [dict(row) for row in cursor.fetchall()]

    # Criar DataFrame
    df = pd.DataFrame(empresas)

    # Criar arquivo CSV em memória
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')

    output.seek(0)

    filename = f"empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@socketio.on('start_scraping')
def handle_start_scraping(data):
    """Iniciar scraping via WebSocket"""
    global bot_running, scraper_instance

    if bot_running:
        emit('scraping_error', {'message': 'Bot já está em execução!'})
        return

    setor = data.get('setor', '')
    cidade = data.get('cidade', '')
    max_results = data.get('max_results', 50)
    continue_from_checkpoint = data.get('continue_from_checkpoint', True)
    required_contacts = data.get('required_contacts', {})

    if not setor or not cidade:
        emit('scraping_error', {'message': 'Setor e cidade são obrigatórios!'})
        return

    bot_running = True

    def run_scraper():
        global bot_running, scraper_instance

        try:
            headless = os.getenv('HEADLESS', 'True').lower() == 'true'
            scraper_instance = GoogleMapsScraper(headless=headless)

            socketio.emit('scraping_status', {'status': 'started', 'message': 'Iniciando busca...'})

            # Função de callback para emitir progresso
            def progress_callback(progress_data):
                print(f"📊 Emitindo progresso: {progress_data}")
                socketio.emit('scraping_progress', progress_data)
                socketio.sleep(0)  # Permitir que o evento seja processado

            # Usar o método search_businesses com callback
            businesses = scraper_instance.search_businesses(
                setor,
                cidade,
                max_results,
                db=db,
                progress_callback=progress_callback,
                continue_from_checkpoint=continue_from_checkpoint,
                required_contacts=required_contacts
            )

            socketio.emit('scraping_complete', {
                'total': len(businesses),
                'message': f'Busca concluída! {len(businesses)} empresas com dados de contato encontradas.'
            })

        except Exception as e:
            print(f"❌ Erro no scraper: {e}")
            socketio.emit('scraping_error', {'message': str(e)})
        finally:
            if scraper_instance:
                scraper_instance.close()
            bot_running = False

    # Executar em greenlet separada com eventlet
    eventlet.spawn(run_scraper)


@socketio.on('stop_scraping')
def handle_stop_scraping():
    """Parar scraping"""
    global bot_running, scraper_instance

    bot_running = False

    if scraper_instance:
        scraper_instance.stop()

    emit('scraping_stopped', {'message': 'Scraping interrompido!'})


@app.route('/api/delete/<int:empresa_id>', methods=['DELETE'])
def delete_empresa(empresa_id):
    """Deletar empresa"""
    try:
        cursor = db.cursor
        cursor.execute('DELETE FROM empresas WHERE id = ?', (empresa_id,))
        db.conn.commit()
        return jsonify({'success': True, 'message': 'Empresa deletada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete-multiple', methods=['POST'])
def delete_multiple():
    """Deletar múltiplas empresas"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'Nenhuma empresa selecionada'}), 400

        cursor = db.cursor
        placeholders = ','.join(['?' for _ in ids])
        cursor.execute(f'DELETE FROM empresas WHERE id IN ({placeholders})', ids)
        db.conn.commit()

        return jsonify({'success': True, 'message': f'{len(ids)} empresas deletadas com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/clear-database', methods=['POST'])
def clear_database():
    """Limpar toda a base de dados"""
    try:
        cursor = db.cursor
        cursor.execute('DELETE FROM empresas')
        db.conn.commit()

        # Resetar o autoincrement
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="empresas"')
        db.conn.commit()

        return jsonify({'success': True, 'message': 'Base de dados limpa com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/checkpoints')
def get_checkpoints():
    """Listar todos os checkpoints"""
    try:
        checkpoints = db.get_all_checkpoints()
        return jsonify(checkpoints)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/checkpoints/<setor>/<cidade>', methods=['GET'])
def get_checkpoint(setor, cidade):
    """Obter checkpoint específico"""
    try:
        checkpoint = db.get_checkpoint(setor, cidade)
        if checkpoint:
            return jsonify(checkpoint)
        else:
            return jsonify({'error': 'Checkpoint não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/checkpoints/<setor>/<cidade>/reset', methods=['POST'])
def reset_checkpoint(setor, cidade):
    """Resetar checkpoint específico"""
    try:
        db.reset_checkpoint(setor, cidade)
        return jsonify({'success': True, 'message': 'Checkpoint resetado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/checkpoints/<setor>/<cidade>/delete', methods=['DELETE'])
def delete_checkpoint(setor, cidade):
    """Deletar checkpoint específico"""
    try:
        db.reset_checkpoint(setor, cidade)  # reset_checkpoint já deleta do banco
        return jsonify({'success': True, 'message': 'Checkpoint deletado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/checkpoints/reset-all', methods=['POST'])
def reset_all_checkpoints():
    """Resetar todos os checkpoints"""
    try:
        cursor = db.cursor
        cursor.execute('DELETE FROM search_checkpoints')
        db.conn.commit()
        return jsonify({'success': True, 'message': 'Todos os checkpoints foram resetados!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/checkpoints/delete-all', methods=['DELETE'])
def delete_all_checkpoints():
    """Deletar todos os checkpoints"""
    try:
        cursor = db.cursor
        cursor.execute('DELETE FROM search_checkpoints')
        db.conn.commit()
        return jsonify({'success': True, 'message': 'Todos os checkpoints foram deletados!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== ENDPOINTS WHATSAPP ====================

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Listar templates de mensagens"""
    try:
        templates = db.get_all_templates()
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates', methods=['POST'])
def create_template():
    """Criar template de mensagem"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        mensagem = data.get('mensagem')
        descricao = data.get('descricao', '')

        if not nome or not mensagem:
            return jsonify({'success': False, 'message': 'Nome e mensagem são obrigatórios'}), 400

        template_id = db.create_template(nome, mensagem, descricao)

        if template_id:
            return jsonify({'success': True, 'message': 'Template criado com sucesso!', 'id': template_id})
        else:
            return jsonify({'success': False, 'message': 'Template com este nome já existe'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Atualizar template"""
    try:
        data = request.get_json()
        mensagem = data.get('mensagem')
        descricao = data.get('descricao', '')

        if not mensagem:
            return jsonify({'success': False, 'message': 'Mensagem é obrigatória'}), 400

        db.update_template(template_id, mensagem, descricao)
        return jsonify({'success': True, 'message': 'Template atualizado com sucesso!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Deletar template"""
    try:
        db.delete_template(template_id)
        return jsonify({'success': True, 'message': 'Template deletado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/logs', methods=['GET'])
def get_whatsapp_logs():
    """Obter logs de envio WhatsApp"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = db.get_whatsapp_logs(limit)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/stats', methods=['GET'])
def get_whatsapp_stats():
    """Obter estatísticas de envio WhatsApp"""
    try:
        campanha_id = request.args.get('campanha_id', type=int)
        stats = db.get_whatsapp_stats(campanha_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/campaigns', methods=['GET'])
def get_campaigns():
    """Listar todas as campanhas"""
    try:
        campaigns = db.get_all_campaigns()
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/campaigns/active', methods=['GET'])
def get_active_campaigns():
    """Listar campanhas ativas"""
    try:
        campaigns = db.get_active_campaigns()
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/campaigns/<int:campanha_id>', methods=['GET'])
def get_campaign(campanha_id):
    """Obter detalhes de uma campanha"""
    try:
        campaign = db.get_campaign(campanha_id)
        if campaign:
            # Adicionar estatísticas
            stats = db.get_whatsapp_stats(campanha_id)
            campaign['stats'] = stats
            return jsonify(campaign)
        else:
            return jsonify({'error': 'Campanha não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/campaigns/<int:campanha_id>/logs', methods=['GET'])
def get_campaign_logs(campanha_id):
    """Obter logs de uma campanha"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = db.get_whatsapp_logs(campanha_id, limit)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@socketio.on('send_whatsapp')
def handle_send_whatsapp(data):
    """Enviar mensagem WhatsApp via WebSocket"""
    global whatsapp_bot_running, whatsapp_bot_instance

    if whatsapp_bot_running:
        emit('whatsapp_error', {'message': 'Bot WhatsApp já está em execução!'})
        return

    empresas_ids = data.get('empresas_ids', [])
    mensagem = data.get('mensagem', '')
    delay = data.get('delay', 30)
    campanha_nome = data.get('campanha_nome', f'Campanha {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    continuar_campanha_id = data.get('continuar_campanha_id')  # Para retomar campanha

    # DEBUG: Imprimir dados recebidos
    print(f"\n🔍 DEBUG - Dados recebidos:")
    print(f"  - empresas_ids: {empresas_ids} (tipo: {type(empresas_ids)}, tamanho: {len(empresas_ids)})")
    print(f"  - mensagem: {mensagem[:50]}..." if len(mensagem) > 50 else f"  - mensagem: {mensagem}")
    print(f"  - delay: {delay}")
    print(f"  - campanha_nome: {campanha_nome}")

    if not empresas_ids or not mensagem:
        emit('whatsapp_error', {'message': 'IDs das empresas e mensagem são obrigatórios!'})
        return

    whatsapp_bot_running = True

    def run_whatsapp_bot():
        global whatsapp_bot_running, whatsapp_bot_instance, whatsapp_selenium_instance
        campanha_id = None

        try:
            # Verificar se há sessão Selenium ativa
            if not whatsapp_selenium_instance or not whatsapp_selenium_instance.is_logged_in:
                socketio.emit('whatsapp_error', {
                    'message': 'Você precisa estar conectado ao WhatsApp! Clique em "Conectar ao WhatsApp" primeiro.'
                })
                return

            socketio.emit('whatsapp_status', {'status': 'started', 'message': 'Iniciando envio de mensagens...'})

            # Buscar empresas
            empresas = []
            empresas_bloqueadas = []
            print(f"\n🔍 DEBUG - Buscando empresas no banco:")
            for empresa_id in empresas_ids:
                empresa = db.get_empresa_by_id(empresa_id)
                print(f"  - ID {empresa_id}: {empresa['nome'] if empresa else 'NÃO ENCONTRADA'} | WhatsApp: {empresa.get('whatsapp') if empresa else 'N/A'}")
                # Verificar se empresa existe E tem whatsapp válido (não nulo e não vazio)
                if empresa and empresa.get('whatsapp') and str(empresa.get('whatsapp')).strip():
                    # Normalizar número
                    telefone_normalizado = ''.join(filter(str.isdigit, empresa.get('whatsapp')))

                    # Verificar se número está bloqueado
                    if db.is_number_blocked(telefone_normalizado):
                        empresas_bloqueadas.append(empresa['nome'])
                        print(f"    🚫 Número bloqueado/ignorado")
                    else:
                        empresas.append(empresa)
                        print(f"    ✅ Adicionada à lista")
                elif empresa:
                    print(f"    ❌ WhatsApp inválido: '{empresa.get('whatsapp')}'")
                else:
                    print(f"    ❌ Empresa não encontrada")

            print(f"\n📊 Total de empresas válidas: {len(empresas)}")
            if empresas_bloqueadas:
                print(f"🚫 Empresas bloqueadas ignoradas ({len(empresas_bloqueadas)}): {', '.join(empresas_bloqueadas)}")

            if not empresas:
                socketio.emit('whatsapp_error', {'message': 'Nenhuma empresa com WhatsApp encontrada'})
                return

            # Criar ou retomar campanha
            if continuar_campanha_id:
                campanha_id = continuar_campanha_id
                db.resume_campaign(campanha_id)
                socketio.emit('whatsapp_status', {
                    'status': 'resumed',
                    'message': f'Retomando campanha ID: {campanha_id}'
                })

                # Filtrar empresas que já receberam
                empresas_nao_enviadas = db.get_empresas_nao_enviadas(campanha_id, empresas_ids)
                empresas = empresas_nao_enviadas

                if not empresas:
                    socketio.emit('whatsapp_complete', {
                        'total': 0,
                        'success': 0,
                        'failed': 0,
                        'message': 'Todas as empresas desta campanha já receberam mensagens!'
                    })
                    return

                socketio.emit('whatsapp_status', {
                    'status': 'filtered',
                    'message': f'{len(empresas)} empresas restantes (pulando já enviadas)'
                })
            else:
                # Criar nova campanha
                campanha_id = db.create_campaign(
                    nome=campanha_nome,
                    mensagem=mensagem,
                    total_empresas=len(empresas),
                    delay=delay,
                    filtros={'empresas_ids': empresas_ids}
                )
                socketio.emit('whatsapp_status', {
                    'status': 'campaign_created',
                    'message': f'Campanha criada: {campanha_nome} (ID: {campanha_id})',
                    'campanha_id': campanha_id
                })

            # Callback de progresso
            def progress_callback(progress_data):
                socketio.emit('whatsapp_progress', progress_data)

                # Registrar no log
                empresa_id = progress_data.get('empresa_id')
                empresa_nome = progress_data.get('empresa', '')
                telefone = progress_data.get('phone', '')

                # Determinar status
                if progress_data.get('status') == 'nao_existe':
                    status = 'nao_existe'
                elif progress_data.get('success'):
                    status = 'sucesso'
                else:
                    status = 'erro'

                erro = progress_data.get('error')

                db.log_whatsapp_send(campanha_id, empresa_id, empresa_nome, telefone, mensagem, status, erro)

                # Atualizar checkpoint da campanha
                db.update_campaign_progress(
                    campanha_id,
                    enviados_increment=1 if status == 'sucesso' else 0,
                    falhas_increment=1 if status in ['erro', 'nao_existe'] else 0,
                    ultimo_indice=progress_data.get('current', 0)
                )

                socketio.sleep(0)

            # Enviar mensagens
            total = len(empresas)
            success_count = 0
            failed_count = 0

            for i, empresa in enumerate(empresas, 1):
                # Verificar se foi interrompido
                if not whatsapp_bot_running:
                    db.pause_campaign(campanha_id)
                    socketio.emit('whatsapp_paused', {
                        'campanha_id': campanha_id,
                        'message': f'Campanha pausada. {i-1}/{total} enviados. Você pode continuar depois.'
                    })
                    return

                try:
                    # Verificar se já foi enviado (segurança extra)
                    if db.check_empresa_already_sent(empresa['id'], campanha_id):
                        logger.info(f'Pulando {empresa["nome"]} - já recebeu mensagem nesta campanha')
                        continue

                    # Personalizar mensagem
                    mensagem_personalizada = whatsapp_selenium_instance._personalize_message(mensagem, empresa)

                    # Enviar usando Selenium
                    result = whatsapp_selenium_instance.send_message(
                        empresa['whatsapp'],
                        mensagem_personalizada,
                        empresa['nome']
                    )

                    # Verificar se número não existe e bloquear automaticamente
                    if result.get('status') == 'nao_existe':
                        telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))
                        db.block_number(telefone_normalizado, 'Número não existe no WhatsApp (bloqueado automaticamente)')
                        logger.info(f'Número {empresa["whatsapp"]} bloqueado automaticamente (não existe)')

                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1

                    progress_callback({
                        'empresa_id': empresa['id'],
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa['nome'],
                        'phone': empresa['whatsapp'],
                        **result
                    })

                    # Delay entre envios
                    if i < total:
                        socketio.sleep(delay)

                except Exception as e:
                    failed_count += 1
                    progress_callback({
                        'empresa_id': empresa['id'],
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa['nome'],
                        'phone': empresa.get('whatsapp', ''),
                        'success': False,
                        'error': str(e)
                    })

            # Marcar campanha como concluída
            db.complete_campaign(campanha_id)

            socketio.emit('whatsapp_complete', {
                'campanha_id': campanha_id,
                'total': total,
                'success': success_count,
                'failed': failed_count,
                'message': f'Envio concluído! {success_count}/{total} mensagens enviadas com sucesso.'
            })

        except Exception as e:
            print(f"❌ Erro no bot WhatsApp: {e}")
            if campanha_id:
                db.pause_campaign(campanha_id)
            socketio.emit('whatsapp_error', {'message': str(e), 'campanha_id': campanha_id})
        finally:
            whatsapp_bot_running = False
            # Nota: NÃO fechamos a instância Selenium aqui para manter a sessão ativa

    # Executar em greenlet separada
    eventlet.spawn(run_whatsapp_bot)


@socketio.on('stop_whatsapp')
def handle_stop_whatsapp():
    """Parar bot WhatsApp"""
    global whatsapp_bot_running, whatsapp_bot_instance

    whatsapp_bot_running = False
    whatsapp_bot_instance = None

    emit('whatsapp_stopped', {'message': 'Bot WhatsApp interrompido!'})


# ==================== ENDPOINTS WHATSAPP SELENIUM ====================

@app.route('/api/whatsapp/session/start', methods=['POST'])
def start_whatsapp_session():
    """Iniciar sessão do WhatsApp com Selenium"""
    global whatsapp_selenium_instance

    try:
        if whatsapp_selenium_instance and whatsapp_selenium_instance.driver:
            return jsonify({
                'success': False,
                'message': 'Sessão já está ativa'
            }), 400

        # Criar instância do WhatsApp Selenium
        whatsapp_selenium_instance = WhatsAppSelenium(session_name='default', headless=False)

        # Iniciar navegador
        if whatsapp_selenium_instance.start():
            return jsonify({
                'success': True,
                'is_logged_in': whatsapp_selenium_instance.is_logged_in,
                'message': 'Navegador iniciado. Aguarde ou escaneie o QR Code.' if not whatsapp_selenium_instance.is_logged_in else 'Sessão já está logada!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao iniciar navegador'
            }), 500

    except Exception as e:
        logger.error(f'Erro ao iniciar sessão WhatsApp: {e}')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/whatsapp/session/status', methods=['GET'])
def get_whatsapp_session_status():
    """Verificar status da sessão WhatsApp"""
    global whatsapp_selenium_instance

    try:
        if not whatsapp_selenium_instance:
            return jsonify({
                'active': False,
                'logged_in': False,
                'message': 'Nenhuma sessão ativa'
            })

        # Verificar se driver está ativo
        driver_active = whatsapp_selenium_instance.driver is not None

        if driver_active:
            # Tentar verificar login
            try:
                is_logged = whatsapp_selenium_instance._check_if_logged_in(timeout=5)
                whatsapp_selenium_instance.is_logged_in = is_logged
            except:
                is_logged = whatsapp_selenium_instance.is_logged_in
        else:
            is_logged = False

        return jsonify({
            'active': driver_active,
            'logged_in': is_logged,
            'message': 'Logado no WhatsApp' if is_logged else 'Aguardando login'
        })

    except Exception as e:
        return jsonify({
            'active': False,
            'logged_in': False,
            'message': str(e)
        }), 500


@app.route('/api/whatsapp/session/wait-login', methods=['POST'])
def wait_whatsapp_login():
    """Aguardar login no WhatsApp"""
    global whatsapp_selenium_instance

    try:
        if not whatsapp_selenium_instance:
            return jsonify({
                'success': False,
                'message': 'Nenhuma sessão ativa. Inicie a sessão primeiro.'
            }), 400

        timeout = request.json.get('timeout', 120)

        # Aguardar login em thread separada para não bloquear
        def wait_login():
            success = whatsapp_selenium_instance.wait_for_login(timeout=timeout)
            if success:
                socketio.emit('whatsapp_login_success', {
                    'message': 'Login realizado com sucesso!'
                })
            else:
                socketio.emit('whatsapp_login_timeout', {
                    'message': 'Timeout aguardando login'
                })

        eventlet.spawn(wait_login)

        return jsonify({
            'success': True,
            'message': f'Aguardando login (timeout: {timeout}s)...'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/whatsapp/session/close', methods=['POST'])
def close_whatsapp_session():
    """Fechar sessão do WhatsApp"""
    global whatsapp_selenium_instance

    try:
        if whatsapp_selenium_instance:
            whatsapp_selenium_instance.close()
            whatsapp_selenium_instance = None

        return jsonify({
            'success': True,
            'message': 'Sessão fechada com sucesso'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== ENDPOINTS NÚMEROS BLOQUEADOS ====================

@app.route('/api/whatsapp/blocked', methods=['GET'])
def get_blocked_numbers():
    """Listar números bloqueados"""
    try:
        blocked = db.get_blocked_numbers()
        count = db.get_blocked_count()
        return jsonify({
            'blocked': blocked,
            'count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whatsapp/blocked', methods=['POST'])
def block_number():
    """Bloquear um número"""
    try:
        data = request.get_json()
        telefone = data.get('telefone')
        motivo = data.get('motivo', 'Marcado manualmente')

        if not telefone:
            return jsonify({'success': False, 'message': 'Telefone é obrigatório'}), 400

        # Normalizar telefone (remover caracteres especiais)
        telefone_normalizado = ''.join(filter(str.isdigit, telefone))

        result = db.block_number(telefone_normalizado, motivo)

        if result:
            return jsonify({'success': True, 'message': 'Número bloqueado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Número já está bloqueado'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/blocked/<telefone>', methods=['DELETE'])
def unblock_number(telefone):
    """Desbloquear um número"""
    try:
        # Normalizar telefone
        telefone_normalizado = ''.join(filter(str.isdigit, telefone))

        success = db.unblock_number(telefone_normalizado)

        if success:
            return jsonify({'success': True, 'message': 'Número desbloqueado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Número não encontrado'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/blocked/check/<telefone>', methods=['GET'])
def check_blocked_number(telefone):
    """Verificar se um número está bloqueado"""
    try:
        telefone_normalizado = ''.join(filter(str.isdigit, telefone))
        is_blocked = db.is_number_blocked(telefone_normalizado)
        return jsonify({'blocked': is_blocked})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('\n🚀 Servidor web iniciado!')
    print('📍 Acesse: http://localhost:5000\n')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
