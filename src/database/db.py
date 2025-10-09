import sqlite3
import os
from datetime import datetime
from pathlib import Path
import threading


class Database:
    def __init__(self, db_path='./database/empresas.db'):
        # Criar diretório se não existir
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._local = threading.local()
        self._create_tables()

    def _get_connection(self):
        """Obter conexão thread-safe"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _get_cursor(self):
        """Obter cursor thread-safe"""
        return self._get_connection().cursor()

    @property
    def conn(self):
        return self._get_connection()

    @property
    def cursor(self):
        return self._get_cursor()

    def _create_tables(self):
        """Criar tabelas do banco de dados"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                setor TEXT NOT NULL,
                cidade TEXT NOT NULL,
                endereco TEXT,
                telefone TEXT,
                whatsapp TEXT,
                email TEXT,
                website TEXT,
                instagram TEXT,
                facebook TEXT,
                linkedin TEXT,
                twitter TEXT,
                google_maps_url TEXT,
                rating REAL,
                total_reviews INTEGER,
                horario_funcionamento TEXT,
                latitude REAL,
                longitude REAL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nome, endereco)
            )
        ''')

        # Tabela de checkpoints para retomar buscas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setor TEXT NOT NULL,
                cidade TEXT NOT NULL,
                total_encontrados INTEGER DEFAULT 0,
                total_processados INTEGER DEFAULT 0,
                total_salvos INTEGER DEFAULT 0,
                ultimo_indice INTEGER DEFAULT 0,
                status TEXT DEFAULT 'em_andamento',
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(setor, cidade)
            )
        ''')

        # Tabela de templates de mensagens
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                mensagem TEXT NOT NULL,
                descricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de campanhas WhatsApp
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                total_empresas INTEGER DEFAULT 0,
                total_enviados INTEGER DEFAULT 0,
                total_falhas INTEGER DEFAULT 0,
                ultimo_indice INTEGER DEFAULT 0,
                status TEXT DEFAULT 'em_andamento',
                delay INTEGER DEFAULT 30,
                filtros TEXT,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_fim TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de log de envios WhatsApp
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campanha_id INTEGER,
                empresa_id INTEGER,
                empresa_nome TEXT,
                telefone TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                status TEXT NOT NULL,
                erro TEXT,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campanha_id) REFERENCES whatsapp_campaigns(id),
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')

        # Índice para buscar rapidamente quem já recebeu mensagem
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_empresa
            ON whatsapp_logs(empresa_id, campanha_id)
        ''')

        # Tabela de números bloqueados/ignorados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_blocked (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telefone TEXT NOT NULL UNIQUE,
                motivo TEXT,
                data_bloqueio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Índice para busca rápida de números bloqueados
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_whatsapp_blocked_telefone
            ON whatsapp_blocked(telefone)
        ''')

        # Criar índices para otimizar buscas
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_setor ON empresas(setor)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_cidade ON empresas(cidade)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON empresas(email)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_nome ON empresas(nome)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_nome_endereco ON empresas(nome, endereco)')

        # Otimizações de performance do SQLite
        self.cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging para melhor concorrência
        self.cursor.execute('PRAGMA synchronous=NORMAL')  # Balanço entre segurança e velocidade
        self.cursor.execute('PRAGMA cache_size=10000')  # Cache maior para consultas
        self.cursor.execute('PRAGMA temp_store=MEMORY')  # Usar memória para tabelas temporárias

        self.conn.commit()

    def insert_empresa(self, empresa_data):
        """Inserir empresa no banco de dados"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO empresas (
                    nome, setor, cidade, endereco, telefone, whatsapp,
                    email, website, instagram, facebook, linkedin, twitter,
                    google_maps_url, rating, total_reviews,
                    horario_funcionamento, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                empresa_data.get('nome'),
                empresa_data.get('setor'),
                empresa_data.get('cidade'),
                empresa_data.get('endereco'),
                empresa_data.get('telefone'),
                empresa_data.get('whatsapp'),
                empresa_data.get('email'),
                empresa_data.get('website'),
                empresa_data.get('instagram'),
                empresa_data.get('facebook'),
                empresa_data.get('linkedin'),
                empresa_data.get('twitter'),
                empresa_data.get('google_maps_url'),
                empresa_data.get('rating'),
                empresa_data.get('total_reviews'),
                empresa_data.get('horario_funcionamento'),
                empresa_data.get('latitude'),
                empresa_data.get('longitude')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Empresa já existe
            return None
        except Exception as e:
            print(f"❌ Erro ao inserir empresa: {e}")
            return None

    def update_empresa(self, empresa_id, empresa_data):
        """Atualizar dados de uma empresa"""
        self.cursor.execute('''
            UPDATE empresas SET
                telefone = ?,
                whatsapp = ?,
                email = ?,
                website = ?,
                instagram = ?,
                facebook = ?,
                linkedin = ?,
                twitter = ?,
                rating = ?,
                total_reviews = ?,
                horario_funcionamento = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            empresa_data.get('telefone'),
            empresa_data.get('whatsapp'),
            empresa_data.get('email'),
            empresa_data.get('website'),
            empresa_data.get('instagram'),
            empresa_data.get('facebook'),
            empresa_data.get('linkedin'),
            empresa_data.get('twitter'),
            empresa_data.get('rating'),
            empresa_data.get('total_reviews'),
            empresa_data.get('horario_funcionamento'),
            empresa_id
        ))
        self.conn.commit()

    def get_empresas_by_setor(self, setor):
        """Buscar empresas por setor"""
        self.cursor.execute(
            'SELECT * FROM empresas WHERE setor = ? ORDER BY data_criacao DESC',
            (setor,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_empresas_by_cidade(self, cidade):
        """Buscar empresas por cidade"""
        self.cursor.execute(
            'SELECT * FROM empresas WHERE cidade = ? ORDER BY data_criacao DESC',
            (cidade,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_empresas_by_setor_and_cidade(self, setor, cidade):
        """Buscar empresas por setor e cidade"""
        self.cursor.execute(
            'SELECT * FROM empresas WHERE setor = ? AND cidade = ? ORDER BY data_criacao DESC',
            (setor, cidade)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_empresas(self):
        """Buscar todas as empresas"""
        self.cursor.execute('SELECT * FROM empresas ORDER BY data_criacao DESC')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_empresa_by_id(self, empresa_id):
        """Buscar empresa por ID"""
        cursor = self._get_cursor()  # Usar cursor thread-safe
        cursor.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_stats(self):
        """Obter estatísticas das empresas"""
        self.cursor.execute('''
            SELECT
                setor,
                cidade,
                COUNT(*) as total,
                COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) as com_email,
                COUNT(CASE WHEN telefone IS NOT NULL AND telefone != '' THEN 1 END) as com_telefone,
                COUNT(CASE WHEN whatsapp IS NOT NULL AND whatsapp != '' THEN 1 END) as com_whatsapp
            FROM empresas
            GROUP BY setor, cidade
        ''')
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Fechar conexão com o banco de dados"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== MÉTODOS DE CHECKPOINT ====================

    def get_checkpoint(self, setor, cidade):
        """Obter checkpoint de uma busca"""
        cursor = self.cursor
        cursor.execute(
            'SELECT * FROM search_checkpoints WHERE setor = ? AND cidade = ?',
            (setor, cidade)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_or_update_checkpoint(self, setor, cidade, total_encontrados=0, total_processados=0, total_salvos=0, ultimo_indice=0, status='em_andamento'):
        """Criar ou atualizar checkpoint de uma busca"""
        cursor = self.cursor

        # Tentar atualizar primeiro
        cursor.execute('''
            UPDATE search_checkpoints SET
                total_encontrados = ?,
                total_processados = ?,
                total_salvos = ?,
                ultimo_indice = ?,
                status = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE setor = ? AND cidade = ?
        ''', (total_encontrados, total_processados, total_salvos, ultimo_indice, status, setor, cidade))

        # Se não atualizou nada, inserir novo
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO search_checkpoints (setor, cidade, total_encontrados, total_processados, total_salvos, ultimo_indice, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (setor, cidade, total_encontrados, total_processados, total_salvos, ultimo_indice, status))

        self.conn.commit()

    def update_checkpoint_progress(self, setor, cidade, processados_increment=1, salvos_increment=0, ultimo_indice=None):
        """Atualizar progresso do checkpoint"""
        cursor = self.cursor

        if ultimo_indice is not None:
            cursor.execute('''
                UPDATE search_checkpoints SET
                    total_processados = total_processados + ?,
                    total_salvos = total_salvos + ?,
                    ultimo_indice = ?,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE setor = ? AND cidade = ?
            ''', (processados_increment, salvos_increment, ultimo_indice, setor, cidade))
        else:
            cursor.execute('''
                UPDATE search_checkpoints SET
                    total_processados = total_processados + ?,
                    total_salvos = total_salvos + ?,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE setor = ? AND cidade = ?
            ''', (processados_increment, salvos_increment, setor, cidade))

        self.conn.commit()

    def mark_checkpoint_complete(self, setor, cidade):
        """Marcar checkpoint como concluído"""
        cursor = self.cursor
        cursor.execute('''
            UPDATE search_checkpoints SET
                status = 'concluido',
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE setor = ? AND cidade = ?
        ''', (setor, cidade))
        self.conn.commit()

    def reset_checkpoint(self, setor, cidade):
        """Resetar checkpoint para começar do zero"""
        cursor = self.cursor
        cursor.execute('DELETE FROM search_checkpoints WHERE setor = ? AND cidade = ?', (setor, cidade))
        self.conn.commit()

    def get_all_checkpoints(self):
        """Obter todos os checkpoints"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM search_checkpoints ORDER BY data_atualizacao DESC')
        return [dict(row) for row in cursor.fetchall()]

    # ==================== MÉTODOS DE TEMPLATES ====================

    def create_template(self, nome, mensagem, descricao=''):
        """Criar template de mensagem"""
        try:
            cursor = self.cursor
            cursor.execute('''
                INSERT INTO message_templates (nome, mensagem, descricao)
                VALUES (?, ?, ?)
            ''', (nome, mensagem, descricao))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_template(self, template_id):
        """Obter template por ID"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM message_templates WHERE id = ?', (template_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_template_by_name(self, nome):
        """Obter template por nome"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM message_templates WHERE nome = ?', (nome,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_templates(self):
        """Obter todos os templates"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM message_templates ORDER BY nome')
        return [dict(row) for row in cursor.fetchall()]

    def update_template(self, template_id, mensagem, descricao=''):
        """Atualizar template"""
        cursor = self.cursor
        cursor.execute('''
            UPDATE message_templates SET
                mensagem = ?,
                descricao = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (mensagem, descricao, template_id))
        self.conn.commit()

    def delete_template(self, template_id):
        """Deletar template"""
        cursor = self.cursor
        cursor.execute('DELETE FROM message_templates WHERE id = ?', (template_id,))
        self.conn.commit()

    # ==================== MÉTODOS DE CAMPANHAS WHATSAPP ====================

    def create_campaign(self, nome, mensagem, total_empresas, delay=30, filtros=None):
        """Criar nova campanha WhatsApp"""
        cursor = self.cursor
        import json
        filtros_json = json.dumps(filtros) if filtros else None

        cursor.execute('''
            INSERT INTO whatsapp_campaigns (nome, mensagem, total_empresas, delay, filtros)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, mensagem, total_empresas, delay, filtros_json))
        self.conn.commit()
        return cursor.lastrowid

    def get_campaign(self, campanha_id):
        """Obter campanha por ID"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM whatsapp_campaigns WHERE id = ?', (campanha_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_campaigns(self):
        """Obter todas as campanhas"""
        cursor = self.cursor
        cursor.execute('SELECT * FROM whatsapp_campaigns ORDER BY data_inicio DESC')
        return [dict(row) for row in cursor.fetchall()]

    def get_active_campaigns(self):
        """Obter campanhas ativas (em andamento)"""
        cursor = self.cursor
        cursor.execute('''
            SELECT * FROM whatsapp_campaigns
            WHERE status = 'em_andamento'
            ORDER BY data_inicio DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def update_campaign_progress(self, campanha_id, enviados_increment=1, falhas_increment=0, ultimo_indice=None):
        """Atualizar progresso da campanha"""
        cursor = self.cursor

        if ultimo_indice is not None:
            cursor.execute('''
                UPDATE whatsapp_campaigns SET
                    total_enviados = total_enviados + ?,
                    total_falhas = total_falhas + ?,
                    ultimo_indice = ?,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (enviados_increment, falhas_increment, ultimo_indice, campanha_id))
        else:
            cursor.execute('''
                UPDATE whatsapp_campaigns SET
                    total_enviados = total_enviados + ?,
                    total_falhas = total_falhas + ?,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (enviados_increment, falhas_increment, campanha_id))

        self.conn.commit()

    def complete_campaign(self, campanha_id):
        """Marcar campanha como concluída"""
        cursor = self.cursor
        cursor.execute('''
            UPDATE whatsapp_campaigns SET
                status = 'concluida',
                data_fim = CURRENT_TIMESTAMP,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (campanha_id,))
        self.conn.commit()

    def pause_campaign(self, campanha_id):
        """Pausar campanha"""
        cursor = self.cursor
        cursor.execute('''
            UPDATE whatsapp_campaigns SET
                status = 'pausada',
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (campanha_id,))
        self.conn.commit()

    def resume_campaign(self, campanha_id):
        """Retomar campanha pausada"""
        cursor = self.cursor
        cursor.execute('''
            UPDATE whatsapp_campaigns SET
                status = 'em_andamento',
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (campanha_id,))
        self.conn.commit()

    def check_empresa_already_sent(self, empresa_id, campanha_id):
        """Verificar se empresa já recebeu mensagem nesta campanha"""
        cursor = self.cursor
        cursor.execute('''
            SELECT COUNT(*) as count FROM whatsapp_logs
            WHERE empresa_id = ? AND campanha_id = ? AND status = 'sucesso'
        ''', (empresa_id, campanha_id))
        result = cursor.fetchone()
        return result['count'] > 0 if result else False

    def get_empresas_nao_enviadas(self, campanha_id, empresas_ids):
        """Filtrar empresas que ainda não receberam mensagem nesta campanha"""
        cursor = self.cursor
        placeholders = ','.join(['?' for _ in empresas_ids])

        cursor.execute(f'''
            SELECT e.* FROM empresas e
            WHERE e.id IN ({placeholders})
            AND e.id NOT IN (
                SELECT empresa_id FROM whatsapp_logs
                WHERE campanha_id = ? AND status = 'sucesso'
            )
        ''', empresas_ids + [campanha_id])

        return [dict(row) for row in cursor.fetchall()]

    # ==================== MÉTODOS DE LOG WHATSAPP ====================

    def log_whatsapp_send(self, campanha_id, empresa_id, empresa_nome, telefone, mensagem, status, erro=None):
        """Registrar envio de mensagem WhatsApp"""
        cursor = self._get_cursor()  # Thread-safe cursor
        cursor.execute('''
            INSERT INTO whatsapp_logs (campanha_id, empresa_id, empresa_nome, telefone, mensagem, status, erro)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (campanha_id, empresa_id, empresa_nome, telefone, mensagem, status, erro))
        self.conn.commit()
        return cursor.lastrowid

    def get_whatsapp_logs(self, campanha_id=None, limit=100):
        """Obter logs de envio WhatsApp"""
        cursor = self._get_cursor()  # Thread-safe cursor
        if campanha_id:
            cursor.execute('''
                SELECT * FROM whatsapp_logs
                WHERE campanha_id = ?
                ORDER BY data_envio DESC LIMIT ?
            ''', (campanha_id, limit))
        else:
            cursor.execute('SELECT * FROM whatsapp_logs ORDER BY data_envio DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_whatsapp_stats(self, campanha_id=None):
        """Obter estatísticas de envio WhatsApp"""
        cursor = self._get_cursor()  # Thread-safe cursor
        if campanha_id:
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'sucesso' THEN 1 END) as sucesso,
                    COUNT(CASE WHEN status = 'erro' THEN 1 END) as erro,
                    COUNT(CASE WHEN status = 'nao_existe' THEN 1 END) as nao_existe
                FROM whatsapp_logs
                WHERE campanha_id = ?
            ''', (campanha_id,))
        else:
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'sucesso' THEN 1 END) as sucesso,
                    COUNT(CASE WHEN status = 'erro' THEN 1 END) as erro,
                    COUNT(CASE WHEN status = 'nao_existe' THEN 1 END) as nao_existe
                FROM whatsapp_logs
            ''')
        row = cursor.fetchone()
        return dict(row) if row else {'total': 0, 'sucesso': 0, 'erro': 0, 'nao_existe': 0}

    # ==================== MÉTODOS DE NÚMEROS BLOQUEADOS ====================

    def block_number(self, telefone, motivo=''):
        """Bloquear/ignorar um número de WhatsApp"""
        try:
            cursor = self._get_cursor()
            cursor.execute('''
                INSERT INTO whatsapp_blocked (telefone, motivo)
                VALUES (?, ?)
            ''', (telefone, motivo))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Número já está bloqueado
            return None

    def unblock_number(self, telefone):
        """Desbloquear um número de WhatsApp"""
        cursor = self._get_cursor()
        cursor.execute('DELETE FROM whatsapp_blocked WHERE telefone = ?', (telefone,))
        self.conn.commit()
        return cursor.rowcount > 0

    def is_number_blocked(self, telefone):
        """Verificar se um número está bloqueado"""
        cursor = self._get_cursor()
        cursor.execute('SELECT COUNT(*) as count FROM whatsapp_blocked WHERE telefone = ?', (telefone,))
        result = cursor.fetchone()
        return result['count'] > 0 if result else False

    def get_blocked_numbers(self):
        """Obter todos os números bloqueados"""
        cursor = self._get_cursor()
        cursor.execute('SELECT * FROM whatsapp_blocked ORDER BY data_bloqueio DESC')
        return [dict(row) for row in cursor.fetchall()]

    def get_blocked_count(self):
        """Contar números bloqueados"""
        cursor = self._get_cursor()
        cursor.execute('SELECT COUNT(*) as count FROM whatsapp_blocked')
        result = cursor.fetchone()
        return result['count'] if result else 0
