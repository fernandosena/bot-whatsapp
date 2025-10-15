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


@app.route('/filtro-mensagens')
def filtro_mensagens():
    """Página de filtro de mensagens enviadas"""
    return render_template('filtro_mensagens.html')


@app.route('/gerenciar-numeros')
def gerenciar_numeros():
    """Página de gerenciamento de números"""
    return render_template('gerenciar_numeros.html')


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


@app.route('/api/empresas-com-status')
def get_empresas_com_status():
    """Listar empresas com status de envio e filtros avançados"""
    try:
        # Filtros
        setor = request.args.get('setor', '')
        cidade = request.args.get('cidade', '')
        has_whatsapp = request.args.get('has_whatsapp', 'true')
        search = request.args.get('search', '')
        search_numero = request.args.get('search_numero', '')
        status_envio = request.args.get('status_envio', '')

        # Query base com LEFT JOINs para verificar status
        query = '''
            SELECT DISTINCT
                e.*,
                CASE
                    WHEN wb.telefone IS NOT NULL THEN 'bloqueado'
                    WHEN wl.id IS NOT NULL THEN 'enviado'
                    ELSE 'nao_enviado'
                END as status_envio,
                wl.data_envio,
                wl.status as status_msg,
                wl.erro,
                wb.motivo as motivo_bloqueio
            FROM empresas e
            LEFT JOIN whatsapp_blocked wb ON wb.telefone = REPLACE(REPLACE(REPLACE(REPLACE(e.whatsapp, ' ', ''), '-', ''), '(', ''), ')', '')
            LEFT JOIN (
                SELECT empresa_id, MAX(id) as max_id
                FROM whatsapp_logs
                GROUP BY empresa_id
            ) latest_log ON latest_log.empresa_id = e.id
            LEFT JOIN whatsapp_logs wl ON wl.id = latest_log.max_id
            WHERE 1=1
        '''

        params = []

        # Filtrar por WhatsApp
        if has_whatsapp == 'true':
            query += ' AND e.whatsapp IS NOT NULL AND e.whatsapp != ""'

        # Filtrar por setor
        if setor:
            query += ' AND e.setor LIKE ?'
            params.append(f'%{setor}%')

        # Filtrar por cidade
        if cidade:
            query += ' AND e.cidade LIKE ?'
            params.append(f'%{cidade}%')

        # Buscar por nome ou endereço
        if search:
            query += ' AND (e.nome LIKE ? OR e.endereco LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])

        # Buscar por número
        if search_numero:
            # Remover caracteres especiais para busca
            numero_limpo = ''.join(filter(str.isdigit, search_numero))
            query += ' AND REPLACE(REPLACE(REPLACE(REPLACE(e.whatsapp, " ", ""), "-", ""), "(", ""), ")", "") LIKE ?'
            params.append(f'%{numero_limpo}%')

        query += ' ORDER BY e.data_criacao DESC'

        cursor = db.cursor
        cursor.execute(query, params)
        empresas_raw = [dict(row) for row in cursor.fetchall()]

        # Filtrar por status de envio (após query principal)
        if status_envio:
            empresas = [e for e in empresas_raw if e['status_envio'] == status_envio]
        else:
            empresas = empresas_raw

        # Estatísticas
        total = len(empresas)
        enviados = len([e for e in empresas if e['status_envio'] == 'enviado'])
        nao_enviados = len([e for e in empresas if e['status_envio'] == 'nao_enviado'])
        bloqueados = len([e for e in empresas if e['status_envio'] == 'bloqueado'])

        return jsonify({
            'empresas': empresas,
            'stats': {
                'total': total,
                'enviados': enviados,
                'nao_enviados': nao_enviados,
                'bloqueados': bloqueados
            }
        })

    except Exception as e:
        print(f"❌ Erro em get_empresas_com_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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
    block_resend = data.get('block_resend', True)  # Bloquear reenvio global (padrão: True)
    check_history = data.get('check_history', False)  # Verificar histórico de conversa

    # DEBUG: Imprimir dados recebidos
    print(f"\n🔍 DEBUG - Dados recebidos:")
    print(f"  - empresas_ids: {empresas_ids} (tipo: {type(empresas_ids)}, tamanho: {len(empresas_ids)})")
    print(f"  - mensagem: {mensagem[:50]}..." if len(mensagem) > 50 else f"  - mensagem: {mensagem}")
    print(f"  - delay: {delay}")
    print(f"  - campanha_nome: {campanha_nome}")
    print(f"  - block_resend: {block_resend}")
    print(f"  - check_history: {check_history}")

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
            empresas_ja_enviadas = []
            print(f"\n🔍 DEBUG - Buscando empresas no banco:")
            print(f"   Block Resend Ativo: {block_resend}")

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
                    # Verificar se já recebeu mensagem em qualquer campanha (se block_resend estiver ativo)
                    elif block_resend and db.check_empresa_already_sent_global(empresa['id']):
                        empresas_ja_enviadas.append(empresa['nome'])
                        print(f"    ⏭️ Já recebeu mensagem anteriormente (pulando)")
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
            if empresas_ja_enviadas:
                print(f"⏭️ Empresas já enviadas ignoradas ({len(empresas_ja_enviadas)}): {', '.join(empresas_ja_enviadas[:10])}{'...' if len(empresas_ja_enviadas) > 10 else ''}")

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

                # Registrar no log (apenas se não for ja_enviado, pois já foi registrado no bloco principal)
                if progress_data.get('status') != 'ja_enviado':
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
                else:
                    # Para ja_enviado, apenas atualizar checkpoint (log já foi feito)
                    db.update_campaign_progress(
                        campanha_id,
                        enviados_increment=1,
                        falhas_increment=0,
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
                        empresa['nome'],
                        check_history=check_history
                    )

                    # Verificar se número não existe e bloquear automaticamente
                    if result.get('status') == 'nao_existe':
                        telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))
                        db.block_number(telefone_normalizado, 'Número não existe no WhatsApp (bloqueado automaticamente)')
                        logger.info(f'Número {empresa["whatsapp"]} bloqueado automaticamente (não existe)')
                        failed_count += 1

                    # Se histórico foi encontrado, marcar como enviado
                    elif result.get('status') == 'ja_enviado':
                        telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))
                        # Registrar no log como sucesso (já enviado anteriormente)
                        db.log_whatsapp_send(
                            campanha_id=campanha_id,
                            empresa_id=empresa['id'],
                            empresa_nome=empresa['nome'],
                            telefone=telefone_normalizado,
                            mensagem='[Histórico de conversa detectado - não enviado]',
                            status='sucesso',
                            erro=None
                        )
                        logger.info(f'Histórico detectado para {empresa["nome"]} - marcado como enviado')
                        success_count += 1

                    elif result['success']:
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


@app.route('/api/whatsapp/mark-as-sent', methods=['POST'])
def mark_as_sent():
    """Marcar manualmente que uma mensagem foi enviada para uma empresa"""
    try:
        data = request.get_json()
        empresa_id = data.get('empresa_id')
        telefone = data.get('telefone')
        empresa_nome = data.get('empresa_nome', '')

        if not empresa_id or not telefone:
            return jsonify({'success': False, 'message': 'ID da empresa e telefone são obrigatórios'}), 400

        # Buscar ou criar campanha genérica para envios manuais
        campanha = db.get_or_create_manual_campaign()

        # Normalizar telefone
        telefone_normalizado = ''.join(filter(str.isdigit, telefone))

        # Verificar se já foi marcado
        if db.check_empresa_already_sent(empresa_id, campanha['id']):
            return jsonify({'success': False, 'message': 'Esta empresa já está marcada como enviada'}), 400

        # Registrar log como sucesso manual
        db.log_whatsapp_send(
            campanha_id=campanha['id'],
            empresa_id=empresa_id,
            empresa_nome=empresa_nome,
            telefone=telefone_normalizado,
            mensagem='[Marcado manualmente como enviado]',
            status='sucesso',
            erro=None
        )

        # Atualizar estatísticas da campanha
        db.update_campaign_progress(campanha['id'], enviados_increment=1, falhas_increment=0)

        return jsonify({
            'success': True,
            'message': f'Empresa "{empresa_nome}" marcada como enviada com sucesso!'
        })

    except Exception as e:
        logger.error(f'Erro ao marcar como enviado: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/mark-as-sent-batch', methods=['POST'])
def mark_as_sent_batch():
    """Marcar múltiplas empresas como enviadas"""
    try:
        data = request.get_json()
        empresa_ids = data.get('empresa_ids', [])

        if not empresa_ids:
            return jsonify({'success': False, 'message': 'Nenhuma empresa selecionada'}), 400

        # Buscar ou criar campanha genérica
        campanha = db.get_or_create_manual_campaign()

        success_count = 0
        skip_count = 0

        for empresa_id in empresa_ids:
            empresa = db.get_empresa_by_id(empresa_id)
            if not empresa or not empresa.get('whatsapp'):
                continue

            # Verificar se já foi marcado
            if db.check_empresa_already_sent(empresa_id, campanha['id']):
                skip_count += 1
                continue

            telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))

            # Registrar log
            db.log_whatsapp_send(
                campanha_id=campanha['id'],
                empresa_id=empresa_id,
                empresa_nome=empresa['nome'],
                telefone=telefone_normalizado,
                mensagem='[Marcado em massa como enviado]',
                status='sucesso',
                erro=None
            )

            success_count += 1

        # Atualizar estatísticas da campanha
        db.update_campaign_progress(campanha['id'], enviados_increment=success_count, falhas_increment=0)

        message = f'{success_count} número(s) marcado(s) como enviado!'
        if skip_count > 0:
            message += f' ({skip_count} já estavam marcados)'

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        logger.error(f'Erro ao marcar em massa: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/blocked-batch', methods=['POST'])
def block_batch():
    """Bloquear múltiplos números"""
    try:
        data = request.get_json()
        empresa_ids = data.get('empresa_ids', [])
        motivo = data.get('motivo', 'Bloqueado em massa')

        if not empresa_ids:
            return jsonify({'success': False, 'message': 'Nenhuma empresa selecionada'}), 400

        success_count = 0
        skip_count = 0

        for empresa_id in empresa_ids:
            empresa = db.get_empresa_by_id(empresa_id)
            if not empresa or not empresa.get('whatsapp'):
                continue

            telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))

            # Tentar bloquear
            if db.block_number(telefone_normalizado, motivo):
                success_count += 1
            else:
                skip_count += 1

        message = f'{success_count} número(s) bloqueado(s)!'
        if skip_count > 0:
            message += f' ({skip_count} já estavam bloqueados)'

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        logger.error(f'Erro ao bloquear em massa: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/whatsapp/unblocked-batch', methods=['POST'])
def unblock_batch():
    """Desbloquear múltiplos números"""
    try:
        data = request.get_json()
        empresa_ids = data.get('empresa_ids', [])

        if not empresa_ids:
            return jsonify({'success': False, 'message': 'Nenhuma empresa selecionada'}), 400

        success_count = 0

        for empresa_id in empresa_ids:
            empresa = db.get_empresa_by_id(empresa_id)
            if not empresa or not empresa.get('whatsapp'):
                continue

            telefone_normalizado = ''.join(filter(str.isdigit, empresa['whatsapp']))

            if db.unblock_number(telefone_normalizado):
                success_count += 1

        return jsonify({
            'success': True,
            'message': f'{success_count} número(s) desbloqueado(s)!'
        })

    except Exception as e:
        logger.error(f'Erro ao desbloquear em massa: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== ENDPOINT CONSULTAR NÚMEROS ====================

@app.route('/consultar-numeros')
def consultar_numeros_page():
    """Página de consulta de números"""
    return render_template('consultar_numeros.html')


@app.route('/api/consultar-numeros', methods=['POST'])
def consultar_numeros():
    """Consultar múltiplos números e retornar informações"""
    try:
        data = request.get_json()
        numeros = data.get('numeros', [])

        if not numeros:
            return jsonify({'success': False, 'message': 'Nenhum número fornecido'}), 400

        resultados = []
        stats = {
            'total': len(numeros),
            'encontrados': 0,
            'nao_encontrados': 0,
            'enviados': 0,
            'bloqueados': 0,
            'nao_enviados': 0
        }

        for numero in numeros:
            # Normalizar número
            numero_normalizado = ''.join(filter(str.isdigit, numero))

            # Formatar número para exibição (55 11 99999-9999)
            if len(numero_normalizado) >= 13:
                numero_formatado = f"{numero_normalizado[:2]} {numero_normalizado[2:4]} {numero_normalizado[4:9]}-{numero_normalizado[9:]}"
            elif len(numero_normalizado) >= 11:
                numero_formatado = f"{numero_normalizado[:2]} {numero_normalizado[2:6]}-{numero_normalizado[6:]}"
            else:
                numero_formatado = numero_normalizado

            # Buscar empresa pelo número
            cursor = db.cursor
            cursor.execute('''
                SELECT * FROM empresas
                WHERE REPLACE(REPLACE(REPLACE(REPLACE(whatsapp, ' ', ''), '-', ''), '(', ''), ')', '') = ?
                LIMIT 1
            ''', (numero_normalizado,))

            empresa = cursor.fetchone()

            if empresa:
                empresa = dict(empresa)
                stats['encontrados'] += 1

                # Verificar se está bloqueado
                is_blocked = db.is_number_blocked(numero_normalizado)

                # Verificar se já recebeu mensagem
                cursor.execute('''
                    SELECT data_envio, status, erro
                    FROM whatsapp_logs
                    WHERE empresa_id = ? AND status = 'sucesso'
                    ORDER BY data_envio DESC
                    LIMIT 1
                ''', (empresa['id'],))

                log = cursor.fetchone()
                enviado = log is not None

                # Buscar motivo do bloqueio se bloqueado
                motivo_bloqueio = None
                if is_blocked:
                    cursor.execute('SELECT motivo FROM whatsapp_blocked WHERE telefone = ?', (numero_normalizado,))
                    bloqueio = cursor.fetchone()
                    motivo_bloqueio = bloqueio['motivo'] if bloqueio else 'Bloqueado'

                # Determinar status
                if is_blocked:
                    status_envio = 'bloqueado'
                    stats['bloqueados'] += 1
                elif enviado:
                    status_envio = 'enviado'
                    stats['enviados'] += 1
                else:
                    status_envio = 'nao_enviado'
                    stats['nao_enviados'] += 1

                resultados.append({
                    'numero': numero_normalizado,
                    'numero_formatado': numero_formatado,
                    'encontrado': True,
                    'empresa_id': empresa['id'],
                    'nome': empresa['nome'],
                    'setor': empresa.get('setor'),
                    'cidade': empresa.get('cidade'),
                    'email': empresa.get('email'),
                    'status_envio': status_envio,
                    'data_envio': dict(log)['data_envio'] if log else None,
                    'motivo_bloqueio': motivo_bloqueio
                })
            else:
                stats['nao_encontrados'] += 1
                resultados.append({
                    'numero': numero_normalizado,
                    'numero_formatado': numero_formatado,
                    'encontrado': False,
                    'nome': None,
                    'setor': None,
                    'cidade': None,
                    'email': None,
                    'status_envio': None,
                    'data_envio': None,
                    'motivo_bloqueio': None
                })

        return jsonify({
            'success': True,
            'resultados': resultados,
            'stats': stats
        })

    except Exception as e:
        logger.error(f'Erro ao consultar números: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== ENDPOINTS FILTRO DE MENSAGENS ====================

@app.route('/api/empresas/com-status-envio')
def get_empresas_com_status_envio():
    """Listar empresas com status de envio de mensagens"""
    try:
        # Filtros da query
        setor = request.args.get('setor', '')
        cidade = request.args.get('cidade', '')
        campanha_id = request.args.get('campanha_id', type=int)
        status_envio = request.args.get('status_envio', '')  # 'enviado', 'nao_enviado', 'bloqueado'
        has_whatsapp = request.args.get('has_whatsapp', 'true')  # Sempre filtrar com whatsapp
        search = request.args.get('search', '')

        # Query base
        query = '''
            SELECT
                e.*,
                CASE
                    WHEN wb.telefone IS NOT NULL THEN 'bloqueado'
                    WHEN wl.id IS NOT NULL THEN 'enviado'
                    ELSE 'nao_enviado'
                END as status_envio,
                wl.data_envio,
                wl.status as status_msg,
                wl.erro,
                wb.motivo as motivo_bloqueio
            FROM empresas e
            LEFT JOIN whatsapp_blocked wb ON wb.telefone = REPLACE(REPLACE(REPLACE(e.whatsapp, ' ', ''), '-', ''), '(', '')
            LEFT JOIN whatsapp_logs wl ON wl.empresa_id = e.id
        '''

        params = []
        conditions = ['1=1']

        # Filtrar por campanha específica
        if campanha_id:
            query += ' AND wl.campanha_id = ?'
            params.append(campanha_id)

        # Sempre filtrar empresas com WhatsApp
        if has_whatsapp == 'true':
            conditions.append('e.whatsapp IS NOT NULL AND e.whatsapp != ""')

        if setor:
            conditions.append('e.setor LIKE ?')
            params.append(f'%{setor}%')

        if cidade:
            conditions.append('e.cidade LIKE ?')
            params.append(f'%{cidade}%')

        if search:
            conditions.append('(e.nome LIKE ? OR e.endereco LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])

        # Adicionar condições WHERE
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY e.data_criacao DESC'

        cursor = db.cursor
        cursor.execute(query, params)
        empresas_raw = [dict(row) for row in cursor.fetchall()]

        # Processar e agrupar empresas (remover duplicatas)
        empresas_dict = {}
        for emp in empresas_raw:
            empresa_id = emp['id']

            if empresa_id not in empresas_dict:
                empresas_dict[empresa_id] = emp
            else:
                # Se já existe, atualizar apenas se tem informação de envio mais recente
                if emp['data_envio'] and (not empresas_dict[empresa_id]['data_envio'] or
                                          emp['data_envio'] > empresas_dict[empresa_id]['data_envio']):
                    empresas_dict[empresa_id] = emp

        empresas = list(empresas_dict.values())

        # Filtrar por status de envio (após agrupar)
        if status_envio:
            empresas = [e for e in empresas if e['status_envio'] == status_envio]

        # Estatísticas
        total = len(empresas)
        enviados = len([e for e in empresas if e['status_envio'] == 'enviado'])
        nao_enviados = len([e for e in empresas if e['status_envio'] == 'nao_enviado'])
        bloqueados = len([e for e in empresas if e['status_envio'] == 'bloqueado'])

        return jsonify({
            'empresas': empresas,
            'stats': {
                'total': total,
                'enviados': enviados,
                'nao_enviados': nao_enviados,
                'bloqueados': bloqueados
            }
        })

    except Exception as e:
        print(f"❌ Erro em get_empresas_com_status_envio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/mensagens-excel')
def export_mensagens_excel():
    """Exportar empresas com status de envio para Excel"""
    try:
        # Obter mesmos filtros
        setor = request.args.get('setor', '')
        cidade = request.args.get('cidade', '')
        campanha_id = request.args.get('campanha_id', type=int)
        status_envio = request.args.get('status_envio', '')
        search = request.args.get('search', '')

        # Reutilizar a lógica da API
        # (Código similar ao endpoint acima, mas retorna Excel)
        query = '''
            SELECT
                e.*,
                CASE
                    WHEN wb.telefone IS NOT NULL THEN 'Bloqueado'
                    WHEN wl.id IS NOT NULL THEN 'Enviado'
                    ELSE 'Não Enviado'
                END as status_envio,
                wl.data_envio,
                wl.status as status_msg,
                wl.erro,
                wb.motivo as motivo_bloqueio
            FROM empresas e
            LEFT JOIN whatsapp_blocked wb ON wb.telefone = REPLACE(REPLACE(REPLACE(e.whatsapp, ' ', ''), '-', ''), '(', '')
            LEFT JOIN whatsapp_logs wl ON wl.empresa_id = e.id
            WHERE e.whatsapp IS NOT NULL AND e.whatsapp != ""
        '''

        params = []

        if campanha_id:
            query += ' AND wl.campanha_id = ?'
            params.append(campanha_id)

        if setor:
            query += ' AND e.setor LIKE ?'
            params.append(f'%{setor}%')

        if cidade:
            query += ' AND e.cidade LIKE ?'
            params.append(f'%{cidade}%')

        if search:
            query += ' AND (e.nome LIKE ? OR e.endereco LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])

        query += ' ORDER BY e.data_criacao DESC'

        cursor = db.cursor
        cursor.execute(query, params)
        empresas_raw = [dict(row) for row in cursor.fetchall()]

        # Agrupar duplicatas
        empresas_dict = {}
        for emp in empresas_raw:
            empresa_id = emp['id']
            if empresa_id not in empresas_dict:
                empresas_dict[empresa_id] = emp
            else:
                if emp['data_envio'] and (not empresas_dict[empresa_id]['data_envio'] or
                                          emp['data_envio'] > empresas_dict[empresa_id]['data_envio']):
                    empresas_dict[empresa_id] = emp

        empresas = list(empresas_dict.values())

        # Filtrar por status
        if status_envio:
            if status_envio == 'enviado':
                empresas = [e for e in empresas if e['status_envio'] == 'Enviado']
            elif status_envio == 'nao_enviado':
                empresas = [e for e in empresas if e['status_envio'] == 'Não Enviado']
            elif status_envio == 'bloqueado':
                empresas = [e for e in empresas if e['status_envio'] == 'Bloqueado']

        # Criar DataFrame
        df = pd.DataFrame(empresas)

        # Reordenar colunas
        columns_order = [
            'id', 'nome', 'status_envio', 'setor', 'cidade', 'endereco',
            'whatsapp', 'telefone', 'email', 'website', 'instagram', 'facebook',
            'data_envio', 'status_msg', 'erro', 'motivo_bloqueio',
            'rating', 'total_reviews', 'data_criacao'
        ]

        df = df[[col for col in columns_order if col in df.columns]]

        # Criar arquivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Status Mensagens')

        output.seek(0)

        filename = f"status_mensagens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('\n🚀 Servidor web iniciado!')
    print('📍 Acesse: http://localhost:5000\n')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
