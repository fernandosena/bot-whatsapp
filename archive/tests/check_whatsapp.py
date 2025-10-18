#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

db_path = './database/empresas.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verificar primeiras empresas
print("\n=== PRIMEIRAS 10 EMPRESAS ===")
cursor.execute("SELECT id, nome, whatsapp, telefone FROM empresas LIMIT 10")
empresas = cursor.fetchall()

for emp in empresas:
    print(f"\nID: {emp['id']}")
    print(f"Nome: {emp['nome']}")
    print(f"WhatsApp: '{emp['whatsapp']}' (tipo: {type(emp['whatsapp'])})")
    print(f"Telefone: '{emp['telefone']}'")

# Estatísticas
print("\n\n=== ESTATÍSTICAS ===")
cursor.execute("SELECT COUNT(*) as total FROM empresas")
total = cursor.fetchone()['total']
print(f"Total de empresas: {total}")

cursor.execute("SELECT COUNT(*) as total FROM empresas WHERE whatsapp IS NOT NULL")
whatsapp_not_null = cursor.fetchone()['total']
print(f"Com whatsapp não nulo: {whatsapp_not_null}")

cursor.execute("SELECT COUNT(*) as total FROM empresas WHERE whatsapp IS NOT NULL AND whatsapp != ''")
whatsapp_valido = cursor.fetchone()['total']
print(f"Com whatsapp válido: {whatsapp_valido}")

# Se o usuário passar IDs como argumento
if len(sys.argv) > 1:
    print("\n\n=== VERIFICANDO IDs ESPECÍFICOS ===")
    for empresa_id in sys.argv[1:]:
        cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
        emp = cursor.fetchone()
        if emp:
            print(f"\nID {empresa_id}:")
            print(f"  Nome: {emp['nome']}")
            print(f"  WhatsApp: '{emp['whatsapp']}' (NULL={emp['whatsapp'] is None}, vazio={emp['whatsapp'] == ''})")
            print(f"  Telefone: '{emp['telefone']}'")
        else:
            print(f"\nID {empresa_id}: NÃO ENCONTRADO")

conn.close()
