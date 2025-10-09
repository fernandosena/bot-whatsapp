#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sys
import time

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import Logger

logger = Logger()

# Importar pywhatkit e pyautogui apenas quando a classe for instanciada
# Isso evita erros de display ao importar o módulo
try:
    import pywhatkit as kit
    import pyautogui
    WHATSAPP_AVAILABLE = True
except Exception as e:
    WHATSAPP_AVAILABLE = False
    logger.warning(f'WhatsApp Bot não disponível: {e}')


class WhatsAppBot:
    """Bot para envio de mensagens no WhatsApp"""

    def __init__(self, wait_time=15, close_tab=True):
        """
        Inicializar bot do WhatsApp

        Args:
            wait_time (int): Tempo de espera após enviar mensagem (segundos)
            close_tab (True): Se deve fechar a aba após enviar
        """
        if not WHATSAPP_AVAILABLE:
            raise RuntimeError(
                'WhatsApp Bot não está disponível. '
                'Certifique-se de que:\n'
                '1. pywhatkit e pyautogui estão instalados (pip install pywhatkit pyautogui)\n'
                '2. Você está em um ambiente com interface gráfica (X11)\n'
                '3. A variável DISPLAY está configurada corretamente'
            )

        self.wait_time = wait_time
        self.close_tab = close_tab
        self.sent_messages = []
        self.failed_messages = []

    def format_phone(self, phone):
        """
        Formatar telefone para padrão internacional

        Args:
            phone (str): Número de telefone

        Returns:
            str: Telefone formatado (+55XXXXXXXXXXX)
        """
        # Remover caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))

        # Se não começar com código do país, adicionar +55 (Brasil)
        if not phone.startswith('55'):
            phone = '55' + phone

        # Garantir que tenha + no início
        if not phone.startswith('+'):
            phone = '+' + phone

        return phone

    def send_message(self, phone, message, empresa_nome=''):
        """
        Enviar mensagem para um número

        Args:
            phone (str): Número de telefone (com ou sem código do país)
            message (str): Mensagem a ser enviada
            empresa_nome (str): Nome da empresa (para log)

        Returns:
            dict: Resultado do envio
        """
        try:
            # Formatar telefone
            formatted_phone = self.format_phone(phone)

            logger.info(f'Enviando mensagem para {empresa_nome or formatted_phone}...')

            # Calcular horário de envio (agora + 1 minuto)
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1

            # Ajustar hora se minuto passar de 59
            if minute >= 60:
                minute = minute - 60
                hour = hour + 1
                if hour >= 24:
                    hour = 0

            # Enviar mensagem
            kit.sendwhatmsg(
                formatted_phone,
                message,
                hour,
                minute,
                self.wait_time,
                self.close_tab,
                3  # Tempo de espera para abrir o WhatsApp Web
            )

            # Pressionar Enter para enviar (caso não tenha enviado automaticamente)
            time.sleep(2)
            pyautogui.press('enter')

            result = {
                'success': True,
                'phone': formatted_phone,
                'empresa': empresa_nome,
                'timestamp': datetime.now().isoformat(),
                'message': 'Mensagem enviada com sucesso'
            }

            self.sent_messages.append(result)
            logger.success(f'Mensagem enviada para {empresa_nome or formatted_phone}')

            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar mensagem para {empresa_nome or phone}: {error_msg}')

            result = {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'timestamp': datetime.now().isoformat(),
                'error': error_msg
            }

            self.failed_messages.append(result)
            return result

    def send_bulk_messages(self, empresas, message_template, delay=30, progress_callback=None):
        """
        Enviar mensagens para múltiplas empresas

        Args:
            empresas (list): Lista de empresas (dict com 'nome', 'whatsapp')
            message_template (str): Template da mensagem (pode usar {nome}, {cidade}, etc)
            delay (int): Delay entre envios em segundos
            progress_callback (callable): Função para reportar progresso

        Returns:
            dict: Estatísticas do envio
        """
        total = len(empresas)
        success_count = 0
        failed_count = 0

        logger.info(f'Iniciando envio em massa para {total} empresas...')

        for i, empresa in enumerate(empresas, 1):
            try:
                # Personalizar mensagem
                message = self._personalize_message(message_template, empresa)

                # Enviar mensagem
                result = self.send_message(
                    empresa.get('whatsapp', ''),
                    message,
                    empresa.get('nome', '')
                )

                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1

                # Reportar progresso
                if progress_callback:
                    progress_callback({
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa.get('nome', ''),
                        'phone': empresa.get('whatsapp', '')
                    })

                # Delay entre envios (exceto no último)
                if i < total:
                    logger.info(f'Aguardando {delay} segundos antes do próximo envio...')
                    time.sleep(delay)

            except Exception as e:
                logger.error(f'Erro ao processar empresa {empresa.get("nome", "")}: {str(e)}')
                failed_count += 1

                if progress_callback:
                    progress_callback({
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa.get('nome', ''),
                        'error': str(e)
                    })

        stats = {
            'total': total,
            'success': success_count,
            'failed': failed_count,
            'success_rate': (success_count / total * 100) if total > 0 else 0
        }

        logger.success(f'Envio em massa concluído: {success_count}/{total} enviados com sucesso')

        return stats

    def _personalize_message(self, template, empresa):
        """
        Personalizar mensagem com dados da empresa

        Args:
            template (str): Template da mensagem
            empresa (dict): Dados da empresa

        Returns:
            str: Mensagem personalizada
        """
        # Substituir placeholders
        message = template

        replacements = {
            '{nome}': empresa.get('nome', ''),
            '{cidade}': empresa.get('cidade', ''),
            '{setor}': empresa.get('setor', ''),
            '{endereco}': empresa.get('endereco', ''),
            '{telefone}': empresa.get('telefone', ''),
            '{email}': empresa.get('email', ''),
            '{website}': empresa.get('website', '')
        }

        for placeholder, value in replacements.items():
            if placeholder in message:
                message = message.replace(placeholder, value or '')

        return message

    def get_stats(self):
        """
        Obter estatísticas de envio

        Returns:
            dict: Estatísticas
        """
        return {
            'total_sent': len(self.sent_messages),
            'total_failed': len(self.failed_messages),
            'sent_messages': self.sent_messages,
            'failed_messages': self.failed_messages
        }

    def clear_stats(self):
        """Limpar estatísticas"""
        self.sent_messages = []
        self.failed_messages = []
        logger.info('Estatísticas de envio limpas')


if __name__ == '__main__':
    # Teste do bot
    bot = WhatsAppBot()

    # Exemplo de envio único
    result = bot.send_message(
        '+5587999999999',
        'Olá! Esta é uma mensagem de teste.',
        'Empresa Teste'
    )

    print(result)
