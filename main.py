#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db import Database
from scraper.google_maps_scraper import GoogleMapsScraper
from utils.logger import Logger

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar logger
logger = Logger()


def show_menu():
    """Exibir menu principal"""
    print('\n╔════════════════════════════════════════════╗')
    print('║   🤖 BOT DE PESQUISA DE EMPRESAS          ║')
    print('╚════════════════════════════════════════════╝\n')
    print('1. 🔍 Buscar empresas')
    print('2. 📊 Ver estatísticas')
    print('3. 📋 Listar empresas salvas')
    print('4. 🚪 Sair\n')

    choice = input('Escolha uma opção: ').strip()
    return choice


def buscar_empresas(db):
    """Buscar empresas no Google Maps"""
    print('\n═══════════════════════════════════════════════')
    print('           BUSCAR EMPRESAS')
    print('═══════════════════════════════════════════════\n')

    setor = input('Digite o setor (ex: lanchonetes, pizzarias, academias): ').strip()
    cidade = input('Digite a cidade (ex: São Paulo, Rio de Janeiro): ').strip()
    max_results_input = input('Quantidade máxima de resultados (padrão: 50): ').strip()

    max_results = int(max_results_input) if max_results_input else 50

    print('\n⏳ Iniciando busca...\n')
    logger.info(f'Iniciando busca: {setor} em {cidade}')

    headless = os.getenv('HEADLESS', 'True').lower() == 'true'

    try:
        with GoogleMapsScraper(headless=headless) as scraper:
            # Passar o banco de dados para o scraper processar em tempo real
            businesses = scraper.search_businesses(setor, cidade, max_results, db=db)

            logger.success(f'Busca concluída: {len(businesses)} empresas com dados de contato encontradas')

    except Exception as e:
        print(f'❌ Erro durante a busca: {str(e)}')
        logger.error(f'Erro na busca: {str(e)}')


def ver_estatisticas(db):
    """Exibir estatísticas das empresas"""
    print('\n═══════════════════════════════════════════════')
    print('           ESTATÍSTICAS')
    print('═══════════════════════════════════════════════\n')

    stats = db.get_stats()

    if not stats:
        print('📭 Nenhuma empresa cadastrada ainda.\n')
        return

    for stat in stats:
        total = stat['total']
        com_email = stat['com_email']
        com_telefone = stat['com_telefone']
        com_whatsapp = stat['com_whatsapp']

        print(f"📍 {stat['setor']} em {stat['cidade']}")
        print(f"   Total: {total}")
        print(f"   Com email: {com_email} ({(com_email / total * 100):.1f}%)")
        print(f"   Com telefone: {com_telefone} ({(com_telefone / total * 100):.1f}%)")
        print(f"   Com WhatsApp: {com_whatsapp} ({(com_whatsapp / total * 100):.1f}%)")
        print()


def listar_empresas(db):
    """Listar empresas salvas"""
    print('\n═══════════════════════════════════════════════')
    print('           EMPRESAS SALVAS')
    print('═══════════════════════════════════════════════\n')

    filtrar = input('Filtrar por setor e cidade? (s/n): ').strip().lower()

    if filtrar == 's':
        setor = input('Setor: ').strip()
        cidade = input('Cidade: ').strip()
        empresas = db.get_empresas_by_setor_and_cidade(setor, cidade)
    else:
        empresas = db.get_all_empresas()

    if not empresas:
        print('📭 Nenhuma empresa encontrada.\n')
        return

    print(f'\n📊 Total: {len(empresas)} empresas\n')

    # Mostrar primeiras 10 empresas
    for i, empresa in enumerate(empresas[:10], 1):
        print(f"{i}. {empresa['nome']}")
        print(f"   📍 {empresa['endereco'] or 'Endereço não disponível'}")
        if empresa['telefone']:
            print(f"   📞 {empresa['telefone']}")
        if empresa['whatsapp']:
            print(f"   💬 WhatsApp: {empresa['whatsapp']}")
        if empresa['email']:
            print(f"   📧 {empresa['email']}")
        if empresa['website']:
            print(f"   🌐 {empresa['website']}")
        print()

    if len(empresas) > 10:
        print(f'... e mais {len(empresas) - 10} empresas.\n')

    # Opção de exportar
    exportar = input('Deseja exportar para CSV? (s/n): ').strip().lower()
    if exportar == 's':
        exportar_csv(empresas)


def exportar_csv(empresas):
    """Exportar empresas para arquivo CSV"""
    # Criar diretório exports
    exports_dir = Path('exports')
    exports_dir.mkdir(exist_ok=True)

    # Nome do arquivo
    filename = f"empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = exports_dir / filename

    # Escrever CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Nome', 'Setor', 'Cidade', 'Endereço', 'Telefone', 'WhatsApp',
            'Email', 'Website', 'Rating', 'Reviews', 'URL Google Maps'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for empresa in empresas:
            writer.writerow({
                'Nome': empresa['nome'],
                'Setor': empresa['setor'],
                'Cidade': empresa['cidade'],
                'Endereço': empresa['endereco'] or '',
                'Telefone': empresa['telefone'] or '',
                'WhatsApp': empresa['whatsapp'] or '',
                'Email': empresa['email'] or '',
                'Website': empresa['website'] or '',
                'Rating': empresa['rating'] or '',
                'Reviews': empresa['total_reviews'] or '',
                'URL Google Maps': empresa['google_maps_url'] or ''
            })

    print(f'\n✅ Arquivo exportado: {filepath}\n')
    logger.success(f'CSV exportado: {filename}')


def main():
    """Função principal"""
    print('\n🚀 Bot iniciado!\n')
    logger.info('Bot iniciado')

    # Conectar ao banco de dados
    db_path = os.getenv('DB_PATH', './database/empresas.db')
    db = Database(db_path)

    running = True

    try:
        while running:
            choice = show_menu()

            if choice == '1':
                buscar_empresas(db)
            elif choice == '2':
                ver_estatisticas(db)
            elif choice == '3':
                listar_empresas(db)
            elif choice == '4':
                running = False
                print('\n👋 Até logo!\n')
                logger.info('Bot encerrado')
            else:
                print('\n❌ Opção inválida!\n')

    except KeyboardInterrupt:
        print('\n\n⚠️  Interrompido pelo usuário\n')
        logger.warning('Bot interrompido pelo usuário')
    finally:
        db.close()


if __name__ == '__main__':
    main()
