#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de envio de áudio via API
"""

import requests
import os
import sys

# Configuração da API
BASE_URL = 'http://localhost:5000'

def verificar_conexao():
    """Verifica se está conectado ao WhatsApp"""
    try:
        response = requests.get(f'{BASE_URL}/api/whatsapp/session/status')
        data = response.json()

        if data.get('logged_in'):
            print('✅ Conectado ao WhatsApp!')
            return True
        else:
            print('❌ Não está conectado ao WhatsApp.')
            print('   Acesse http://localhost:5000/enviar-audio para conectar.')
            return False
    except Exception as e:
        print(f'❌ Erro ao verificar conexão: {e}')
        return False


def enviar_audio_caminho(phone, audio_path, empresa_nome=''):
    """
    Enviar áudio passando o caminho do arquivo

    Args:
        phone (str): Número do WhatsApp (formato: +5511999999999)
        audio_path (str): Caminho do arquivo de áudio
        empresa_nome (str): Nome do contato (opcional)
    """
    print(f'\n📤 Enviando áudio para {phone}...')

    if not os.path.exists(audio_path):
        print(f'❌ Arquivo não encontrado: {audio_path}')
        return

    try:
        url = f'{BASE_URL}/api/whatsapp/send-audio'
        data = {
            'phone': phone,
            'audio_path': audio_path,
            'empresa_nome': empresa_nome
        }

        response = requests.post(url, json=data)
        result = response.json()

        if result.get('success'):
            print(f'✅ Áudio enviado com sucesso!')
            print(f'   Telefone: {result.get("phone")}')
            print(f'   Timestamp: {result.get("timestamp")}')
        else:
            print(f'❌ Erro ao enviar: {result.get("error")}')

    except Exception as e:
        print(f'❌ Erro: {e}')


def enviar_audio_upload(phone, audio_path, empresa_nome=''):
    """
    Enviar áudio fazendo upload do arquivo

    Args:
        phone (str): Número do WhatsApp (formato: +5511999999999)
        audio_path (str): Caminho do arquivo de áudio
        empresa_nome (str): Nome do contato (opcional)
    """
    print(f'\n📤 Enviando áudio (upload) para {phone}...')

    if not os.path.exists(audio_path):
        print(f'❌ Arquivo não encontrado: {audio_path}')
        return

    try:
        url = f'{BASE_URL}/api/whatsapp/send-audio-file'

        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {
                'phone': phone,
                'empresa_nome': empresa_nome
            }

            response = requests.post(url, files=files, data=data)
            result = response.json()

            if result.get('success'):
                print(f'✅ Áudio enviado com sucesso!')
                print(f'   Telefone: {result.get("phone")}')
                print(f'   Arquivo: {result.get("audio_path")}')
                print(f'   Timestamp: {result.get("timestamp")}')
            else:
                print(f'❌ Erro ao enviar: {result.get("error")}')

    except Exception as e:
        print(f'❌ Erro: {e}')


def menu():
    """Menu interativo"""
    print('\n' + '='*60)
    print('🎤 ENVIO DE ÁUDIO WHATSAPP')
    print('='*60)

    # Verificar conexão
    if not verificar_conexao():
        return

    print('\n1. Enviar áudio (caminho do arquivo)')
    print('2. Enviar áudio (upload)')
    print('0. Sair')

    opcao = input('\nEscolha uma opção: ').strip()

    if opcao == '0':
        print('👋 Até logo!')
        return

    if opcao not in ['1', '2']:
        print('❌ Opção inválida!')
        return

    # Solicitar dados
    phone = input('\nNúmero do WhatsApp (ex: +5511999999999): ').strip()
    audio_path = input('Caminho do arquivo de áudio: ').strip()
    empresa_nome = input('Nome do contato (opcional): ').strip()

    if not phone or not audio_path:
        print('❌ Número e caminho do áudio são obrigatórios!')
        return

    # Enviar
    if opcao == '1':
        enviar_audio_caminho(phone, audio_path, empresa_nome)
    elif opcao == '2':
        enviar_audio_upload(phone, audio_path, empresa_nome)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            # Modo CLI: python exemplo_envio_audio.py +5511999999999 audio.mp3 "Nome"
            phone = sys.argv[1]
            audio_path = sys.argv[2]
            empresa_nome = sys.argv[3] if len(sys.argv) > 3 else ''

            if verificar_conexao():
                enviar_audio_upload(phone, audio_path, empresa_nome)
        else:
            # Modo interativo
            menu()

    except KeyboardInterrupt:
        print('\n\n👋 Interrompido pelo usuário.')
    except Exception as e:
        print(f'\n❌ Erro: {e}')
