#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migração do banco de dados
Adiciona colunas de redes sociais sem perder dados existentes
"""

import sqlite3
import os

db_path = './database/empresas.db'

def migrate_database():
    """Adicionar colunas de redes sociais se não existirem"""

    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return

    print(f"🔄 Iniciando migração do banco de dados...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obter colunas existentes
    cursor.execute("PRAGMA table_info(empresas)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    print(f"📋 Colunas existentes: {', '.join(existing_columns)}")

    # Colunas a adicionar
    new_columns = {
        'instagram': 'TEXT',
        'facebook': 'TEXT',
        'linkedin': 'TEXT',
        'twitter': 'TEXT'
    }

    # Adicionar colunas que não existem
    columns_added = []
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE empresas ADD COLUMN {column_name} {column_type}")
                columns_added.append(column_name)
                print(f"✅ Coluna '{column_name}' adicionada com sucesso!")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Erro ao adicionar coluna '{column_name}': {e}")
        else:
            print(f"ℹ️  Coluna '{column_name}' já existe")

    conn.commit()
    conn.close()

    if columns_added:
        print(f"\n✨ Migração concluída! {len(columns_added)} colunas adicionadas: {', '.join(columns_added)}")
    else:
        print(f"\n✅ Banco de dados já está atualizado!")

if __name__ == '__main__':
    migrate_database()
