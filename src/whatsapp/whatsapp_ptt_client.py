#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente Python para WhatsApp PTT Service
Comunica-se com o serviço Node.js Baileys para enviar áudios PTT
"""

import os
import sys
import requests
from typing import Dict, Optional

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import Logger

logger = Logger()


class WhatsAppPTTClient:
    """Cliente para enviar áudios PTT via serviço Baileys"""

    def __init__(self, service_url: str = 'http://localhost:3001'):
        """
        Inicializar cliente PTT

        Args:
            service_url (str): URL do serviço Node.js Baileys
        """
        self.service_url = service_url.rstrip('/')
        logger.info(f'WhatsApp PTT Client inicializado: {self.service_url}')

    def check_status(self) -> Dict:
        """
        Verificar status da conexão WhatsApp no serviço

        Returns:
            dict: Status da conexão
        """
        try:
            response = requests.get(f'{self.service_url}/status', timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Erro ao verificar status: {e}')
            return {
                'connected': False,
                'error': str(e)
            }

    def get_qr_code(self) -> Optional[str]:
        """
        Obter QR Code para login

        Returns:
            str: QR Code string ou None
        """
        try:
            response = requests.get(f'{self.service_url}/qr', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('qrCode')
            return None
        except Exception as e:
            logger.error(f'Erro ao obter QR Code: {e}')
            return None

    def is_connected(self) -> bool:
        """
        Verificar se está conectado ao WhatsApp

        Returns:
            bool: True se conectado, False caso contrário
        """
        status = self.check_status()
        return status.get('connected', False)

    def send_audio_ptt(self, phone: str, audio_path: str, empresa_nome: str = '') -> Dict:
        """
        Enviar áudio como PTT (Push-to-Talk)

        Args:
            phone (str): Número do WhatsApp (formato: +5511999999999 ou 11999999999)
            audio_path (str): Caminho do arquivo de áudio
            empresa_nome (str): Nome do contato (opcional)

        Returns:
            dict: Resultado do envio
        """
        try:
            # Verificar se está conectado
            if not self.is_connected():
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Serviço PTT não está conectado ao WhatsApp. Execute: node whatsapp-ptt-service/server.js',
                    'timestamp': None
                }

            # Verificar se arquivo existe
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': f'Arquivo de áudio não encontrado: {audio_path}',
                    'timestamp': None
                }

            logger.info(f'Enviando PTT para {empresa_nome or phone}...')

            # Formatar telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55') and len(clean_phone) == 11:
                clean_phone = '55' + clean_phone

            # Preparar dados
            with open(audio_path, 'rb') as audio_file:
                files = {'audio': (os.path.basename(audio_path), audio_file)}
                data = {
                    'phone': clean_phone,
                    'name': empresa_nome
                }

                # Enviar requisição
                response = requests.post(
                    f'{self.service_url}/send-ptt',
                    files=files,
                    data=data,
                    timeout=30
                )

                response.raise_for_status()
                result = response.json()

                if result.get('success'):
                    logger.success(f'PTT enviado com sucesso para {empresa_nome or phone}')
                else:
                    logger.error(f'Falha ao enviar PTT: {result.get("error")}')

                return result

        except requests.exceptions.ConnectionError:
            error_msg = 'Não foi possível conectar ao serviço PTT. Certifique-se de que está rodando: node whatsapp-ptt-service/server.js'
            logger.error(error_msg)
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': None
            }

        except requests.exceptions.Timeout:
            error_msg = 'Timeout ao enviar PTT. O serviço pode estar sobrecarregado.'
            logger.error(error_msg)
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': None
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar PTT: {error_msg}')
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': None
            }

    def logout(self) -> bool:
        """
        Desconectar do WhatsApp

        Returns:
            bool: True se logout bem-sucedido
        """
        try:
            response = requests.post(f'{self.service_url}/logout', timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                logger.info('Logout realizado com sucesso')
                return True
            return False

        except Exception as e:
            logger.error(f'Erro ao fazer logout: {e}')
            return False


if __name__ == '__main__':
    # Teste do cliente
    import sys

    print('🧪 Testando WhatsApp PTT Client...\n')

    client = WhatsAppPTTClient()

    # Verificar status
    print('1. Verificando status...')
    status = client.check_status()
    print(f'   Status: {status}\n')

    # Verificar se está conectado
    print('2. Verificando conexão...')
    connected = client.is_connected()
    print(f'   Conectado: {connected}\n')

    if not connected:
        print('❌ Serviço não está conectado.')
        print('   Execute: node whatsapp-ptt-service/server.js')
        sys.exit(1)

    # Teste de envio (descomente para testar)
    # print('3. Enviando PTT de teste...')
    # result = client.send_audio_ptt(
    #     phone='5511999999999',
    #     audio_path='./test_audio.mp3',
    #     empresa_nome='Teste'
    # )
    # print(f'   Resultado: {result}\n')

    print('✅ Teste concluído!')
