#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migração para adicionar suporte a campanhas WhatsApp
- Cria tabela de campanhas
- Atualiza tabela de logs
- Cria índices necessários
"""

import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    """Executar migração do banco de dados"""
    db_path = os.getenv('DB_PATH', './database/empresas.db')

    if not Path(db_path).exists():
        print(f'❌ Banco de dados não encontrado: {db_path}')
        return False

    print('🔄 Iniciando migração do banco de dados...\n')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se migração já foi feita (verificar estrutura completa)
        cursor.execute("PRAGMA table_info(whatsapp_logs)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'campanha_id' in columns:
            print('ℹ️  Migração já foi executada anteriormente.')
            print('   Tabelas de campanhas já existem.\n')
            conn.close()
            return True

        print('📝 Criando tabela de campanhas WhatsApp...')

        # Criar tabela de campanhas
        cursor.execute('''
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
        print('   ✅ Tabela whatsapp_campaigns criada')

        # Backup da tabela antiga de logs (se existir)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whatsapp_logs'")
        if cursor.fetchone():
            print('\n📦 Fazendo backup da tabela de logs antiga...')
            cursor.execute('ALTER TABLE whatsapp_logs RENAME TO whatsapp_logs_old')
            print('   ✅ Backup criado: whatsapp_logs_old')

        # Criar nova tabela de logs com campo campanha_id
        print('\n📝 Criando nova tabela de logs...')
        cursor.execute('''
            CREATE TABLE whatsapp_logs (
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
        print('   ✅ Tabela whatsapp_logs criada')

        # Migrar dados antigos (se existirem)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whatsapp_logs_old'")
        if cursor.fetchone():
            print('\n🔄 Migrando dados antigos...')
            try:
                cursor.execute('''
                    INSERT INTO whatsapp_logs (empresa_id, empresa_nome, telefone, mensagem, status, erro, data_envio)
                    SELECT empresa_id, empresa_nome, telefone, mensagem, status, erro, data_envio
                    FROM whatsapp_logs_old
                ''')
                migrated_count = cursor.rowcount
                print(f'   ✅ {migrated_count} registros migrados')
            except Exception as e:
                print(f'   ⚠️  Erro ao migrar dados: {e}')
                print('   Os dados antigos foram preservados em whatsapp_logs_old')

        # Criar índices
        print('\n📇 Criando índices...')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_empresa
            ON whatsapp_logs(empresa_id, campanha_id)
        ''')
        print('   ✅ Índice idx_whatsapp_logs_empresa criado')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_campanha
            ON whatsapp_logs(campanha_id)
        ''')
        print('   ✅ Índice idx_whatsapp_logs_campanha criado')

        # Commit das alterações
        conn.commit()
        print('\n✅ Migração concluída com sucesso!')
        print('\n📋 Resumo:')
        print('   - Tabela whatsapp_campaigns criada')
        print('   - Tabela whatsapp_logs atualizada com suporte a campanhas')
        print('   - Índices criados para melhor performance')
        print('   - Dados antigos preservados (se existiam)\n')

        # Estatísticas
        cursor.execute('SELECT COUNT(*) FROM whatsapp_logs')
        total_logs = cursor.fetchone()[0]
        print(f'📊 Total de logs no sistema: {total_logs}\n')

        conn.close()
        return True

    except Exception as e:
        print(f'\n❌ Erro durante migração: {e}')
        print('   O banco de dados não foi alterado.\n')
        return False


def main():
    print('╔════════════════════════════════════════════╗')
    print('║   🔄 MIGRAÇÃO - CAMPANHAS WHATSAPP        ║')
    print('╚════════════════════════════════════════════╝\n')

    success = migrate_database()

    if success:
        print('═══════════════════════════════════════════════\n')
        print('✅ Migração concluída!\n')
        print('📖 Próximos passos:\n')
        print('   1. Reinicie o servidor: python app.py')
        print('   2. Acesse: http://localhost:5000/whatsapp')
        print('   3. Veja a nova aba "📋 Campanhas"')
        print('   4. Comece a enviar mensagens com checkpoint automático!\n')
        print('💡 Recursos adicionados:')
        print('   - Campanhas rastreadas individualmente')
        print('   - Checkpoint automático a cada envio')
        print('   - Proteção contra duplicatas')
        print('   - Retomada de campanhas pausadas')
        print('   - Visualização de progresso detalhado\n')
    else:
        print('❌ Migração falhou. Verifique os erros acima.\n')


if __name__ == '__main__':
    main()
