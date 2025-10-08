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


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


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

    # Construir query
    query = 'SELECT * FROM empresas WHERE 1=1'
    params = []

    if setor:
        query += ' AND setor = ?'
        params.append(setor)

    if cidade:
        query += ' AND cidade = ?'
        params.append(cidade)

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

    # Construir query
    query = 'SELECT * FROM empresas WHERE 1=1'
    params = []

    if setor:
        query += ' AND setor = ?'
        params.append(setor)

    if cidade:
        query += ' AND cidade = ?'
        params.append(cidade)

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


if __name__ == '__main__':
    print('\n🚀 Servidor web iniciado!')
    print('📍 Acesse: http://localhost:5000\n')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
