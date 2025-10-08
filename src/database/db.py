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

        # Criar índices para otimizar buscas
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_setor ON empresas(setor)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_cidade ON empresas(cidade)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON empresas(email)')

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
        self.cursor.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,))
        row = self.cursor.fetchone()
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
