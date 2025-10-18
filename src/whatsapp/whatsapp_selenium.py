#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WhatsApp Bot com Selenium
- Sessão persistente (não precisa logar toda vez)
- Mais estável que pywhatkit
- Controle total do navegador
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import Logger

logger = Logger()


class WhatsAppSelenium:
    """Bot WhatsApp usando Selenium com sessão persistente"""

    def __init__(self, session_name='default', headless=False):
        """
        Inicializar bot WhatsApp

        Args:
            session_name (str): Nome da sessão (para múltiplas contas)
            headless (bool): Executar em modo headless (sem interface)
        """
        self.session_name = session_name
        self.headless = headless
        self.driver = None
        self.is_logged_in = False
        self.session_dir = Path('whatsapp_sessions') / session_name

        # Criar diretório de sessão
        self.session_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f'WhatsApp Bot inicializado (sessão: {session_name})')

    def _create_driver(self):
        """Criar instância do ChromeDriver com configurações"""
        chrome_options = Options()

        # Diretório de dados do usuário (sessão persistente)
        user_data_dir = str(self.session_dir.absolute())
        chrome_options.add_argument(f'user-data-dir={user_data_dir}')

        # Configurações adicionais
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')

        # Desabilitar notificações
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # Modo headless (opcional)
        if self.headless:
            chrome_options.add_argument('--headless')

        # Criar driver - Tentar várias abordagens
        driver = None

        # Tentativa 1: Usar ChromeDriverManager (precisa de internet)
        try:
            logger.info('Tentando usar ChromeDriverManager...')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info('ChromeDriverManager: Sucesso!')
            return driver
        except Exception as e:
            logger.warning(f'ChromeDriverManager falhou: {e}')

        # Tentativa 2: Usar chromedriver do PATH
        try:
            logger.info('Tentando usar chromedriver do sistema...')
            driver = webdriver.Chrome(options=chrome_options)
            logger.info('ChromeDriver do sistema: Sucesso!')
            return driver
        except Exception as e:
            logger.warning(f'ChromeDriver do sistema falhou: {e}')

        # Tentativa 3: Tentar caminhos comuns
        common_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/snap/bin/chromium.chromedriver',
        ]

        for path in common_paths:
            if os.path.exists(path):
                try:
                    logger.info(f'Tentando usar chromedriver em {path}...')
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info(f'ChromeDriver em {path}: Sucesso!')
                    return driver
                except Exception as e:
                    logger.warning(f'ChromeDriver em {path} falhou: {e}')

        # Se chegou aqui, nenhuma tentativa funcionou
        raise Exception(
            'Não foi possível iniciar o ChromeDriver. '
            'Instale com: sudo apt install chromium-chromedriver'
        )

    def start(self):
        """Iniciar navegador e abrir WhatsApp Web"""
        try:
            logger.info('Iniciando navegador...')
            self.driver = self._create_driver()
            self.driver.maximize_window()

            logger.info('Abrindo WhatsApp Web...')
            self.driver.get('https://web.whatsapp.com')

            logger.info('Aguardando carregamento...')
            time.sleep(3)

            # Verificar se já está logado
            if self._check_if_logged_in():
                self.is_logged_in = True
                logger.success('Sessão ativa! Já está logado.')
            else:
                self.is_logged_in = False
                logger.info('Aguardando login via QR Code...')

            return True

        except Exception as e:
            logger.error(f'Erro ao iniciar navegador: {e}')
            return False

    def _check_if_logged_in(self, timeout=10):
        """
        Verificar se está logado no WhatsApp Web

        Args:
            timeout (int): Tempo máximo de espera em segundos

        Returns:
            bool: True se logado, False caso contrário
        """
        try:
            # Procurar por elemento que só aparece quando logado
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            return True
        except TimeoutException:
            return False

    def wait_for_login(self, timeout=120):
        """
        Aguardar usuário fazer login via QR Code

        Args:
            timeout (int): Tempo máximo de espera em segundos

        Returns:
            bool: True se login bem-sucedido, False se timeout
        """
        logger.info(f'Aguardando login (timeout: {timeout}s)...')
        logger.info('Escaneie o QR Code no navegador')

        try:
            # Aguardar até aparecer a caixa de busca (indica que está logado)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )

            self.is_logged_in = True
            logger.success('Login realizado com sucesso!')

            # Aguardar carregar completamente
            time.sleep(5)
            return True

        except TimeoutException:
            logger.error('Timeout aguardando login')
            return False

    def search_contact(self, phone_or_name):
        """
        Buscar contato por telefone ou nome

        Args:
            phone_or_name (str): Telefone ou nome do contato

        Returns:
            bool: True se encontrou, False caso contrário
        """
        try:
            # Clicar na caixa de busca
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )

            search_box.click()
            time.sleep(0.5)

            # Limpar busca anterior
            search_box.clear()
            time.sleep(0.5)

            # Digitar busca
            search_box.send_keys(phone_or_name)
            time.sleep(2)

            # Pressionar Enter para abrir conversa
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f'Erro ao buscar contato: {e}')
            return False

    def check_chat_history(self):
        """
        Verificar se já existe histórico de conversa no chat aberto

        Returns:
            bool: True se existe histórico, False caso contrário
        """
        try:
            # Procurar por mensagens no histórico do chat
            # Usar XPath para encontrar mensagens na área de conversa
            messages = self.driver.find_elements(By.XPATH, '//div[@role="row"]//div[contains(@class, "message-")]')

            # Se encontrou pelo menos uma mensagem, tem histórico
            if len(messages) > 0:
                logger.info(f'Histórico encontrado: {len(messages)} mensagens')
                return True

            # Alternativa: procurar pela div de mensagens
            try:
                chat_panel = self.driver.find_element(By.XPATH, '//div[@id="main"]//div[@data-tab="6"]')
                # Se encontrou o painel e tem conteúdo
                if chat_panel and chat_panel.text.strip():
                    logger.info('Histórico de conversa encontrado')
                    return True
            except:
                pass

            logger.info('Nenhum histórico de conversa encontrado')
            return False

        except Exception as e:
            logger.warning(f'Erro ao verificar histórico: {e}')
            return False

    def send_audio(self, phone, audio_path, empresa_nome=''):
        """
        Enviar áudio para um número (simula gravação PTT)

        Args:
            phone (str): Número de telefone (formato: +5511999999999)
            audio_path (str): Caminho do arquivo de áudio (.ogg, .mp3, .wav)
            empresa_nome (str): Nome da empresa (para log)

        Returns:
            dict: Resultado do envio
        """
        try:
            if not self.is_logged_in:
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Não está logado no WhatsApp Web',
                    'timestamp': datetime.now().isoformat()
                }

            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': f'Arquivo de áudio não encontrado: {audio_path}',
                    'timestamp': datetime.now().isoformat()
                }

            logger.info(f'Enviando áudio para {empresa_nome or phone}...')

            # Formatar telefone (remover caracteres especiais)
            clean_phone = ''.join(filter(str.isdigit, phone))

            # Abrir conversa via URL
            url = f'https://web.whatsapp.com/send?phone={clean_phone}'
            self.driver.get(url)
            time.sleep(3)

            # Verificar se o número existe
            try:
                error_element = self.driver.find_element(By.XPATH, '//*[contains(text(), "número de telefone") and contains(text(), "não") and contains(text(), "WhatsApp")]')
                logger.error(f'Número {phone} não existe no WhatsApp')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Número não existe no WhatsApp',
                    'status': 'nao_existe',
                    'timestamp': datetime.now().isoformat()
                }
            except:
                pass  # Número existe, continuar

            # Aguardar caixa de mensagem aparecer
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
            except TimeoutException:
                logger.error(f'Timeout ao aguardar caixa de mensagem para {phone}.')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Número provavelmente não existe no WhatsApp',
                    'status': 'nao_existe',
                    'timestamp': datetime.now().isoformat()
                }

            # Localizar botão de anexo (clipe)
            try:
                attach_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@title="Anexar" or @aria-label="Anexar"]'))
                )
                attach_button.click()
                time.sleep(1)
            except:
                # Tentar XPath alternativo
                try:
                    attach_button = self.driver.find_element(By.XPATH, '//span[@data-icon="plus" or @data-icon="attach-menu-plus"]/..')
                    attach_button.click()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f'Erro ao clicar no botão de anexo: {e}')
                    return {
                        'success': False,
                        'phone': phone,
                        'empresa': empresa_nome,
                        'error': 'Não foi possível abrir menu de anexo',
                        'timestamp': datetime.now().isoformat()
                    }

            # Localizar input de arquivo (invisível)
            try:
                # Tentar múltiplos seletores para o input de arquivo
                file_input = None
                input_selectors = [
                    '//input[@type="file"]',
                    '//input[@accept]',
                    '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]',
                    '//input[contains(@accept, "image")]'
                ]

                for selector in input_selectors:
                    try:
                        file_input = self.driver.find_element(By.XPATH, selector)
                        if file_input:
                            break
                    except:
                        continue

                if not file_input:
                    logger.error('Não foi possível encontrar input de arquivo')
                    return {
                        'success': False,
                        'phone': phone,
                        'empresa': empresa_nome,
                        'error': 'Não foi possível encontrar input de arquivo',
                        'timestamp': datetime.now().isoformat()
                    }

                # Enviar o arquivo de áudio
                absolute_path = os.path.abspath(audio_path)
                file_input.send_keys(absolute_path)

                logger.info(f'Arquivo de áudio carregado: {absolute_path}')

                # Aguardar mais tempo para o arquivo processar
                time.sleep(3)

            except Exception as e:
                logger.error(f'Erro ao enviar arquivo: {e}')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': f'Erro ao carregar arquivo: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }

            # Aguardar preview do arquivo e botão de enviar
            try:
                # Tentar múltiplos seletores para o botão de enviar
                send_button = None
                send_selectors = [
                    # XPath específico fornecido pelo usuário
                    '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div[2]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/div/div',
                    # Versão relativa do mesmo XPath
                    '//div[@role="button"]//span[@data-icon="send"]',
                    # Seletores alternativos
                    '//span[@data-icon="send"]',
                    '//button[@aria-label="Enviar"]',
                    '//button[contains(@aria-label, "Send")]',
                    '//div[@role="button" and @aria-label="Enviar"]',
                    '//span[@data-testid="send"]',
                    '//button[contains(@class, "send")]',
                    # Buscar pelo parent do ícone
                    '//span[@data-icon="send"]/parent::div[@role="button"]',
                    '//span[@data-icon="send"]/..'
                ]

                for selector in send_selectors:
                    try:
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if send_button:
                            logger.info(f'Botão de enviar encontrado com: {selector}')
                            break
                    except:
                        continue

                if not send_button:
                    logger.warning('Botão de enviar não encontrado com seletores conhecidos. Tentando alternativa...')

                    # Última tentativa: procurar por qualquer botão/span clicável na área de preview
                    try:
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "send")]//button'))
                        )
                    except:
                        return {
                            'success': False,
                            'phone': phone,
                            'empresa': empresa_nome,
                            'error': 'Não foi possível encontrar botão de enviar. Verifique se o arquivo foi carregado manualmente.',
                            'timestamp': datetime.now().isoformat()
                        }

                time.sleep(1)
                send_button.click()
                time.sleep(3)

                logger.success(f'Áudio enviado para {empresa_nome or phone}')

                return {
                    'success': True,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'audio_path': audio_path,
                    'timestamp': datetime.now().isoformat()
                }

            except TimeoutException:
                logger.error('Timeout ao aguardar botão de enviar')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Timeout ao tentar enviar o áudio. O arquivo pode ter sido carregado, verifique manualmente.',
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar áudio para {phone}: {error_msg}')
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }

    def send_message(self, phone, message, empresa_nome='', check_history=False):
        """
        Enviar mensagem para um número

        Args:
            phone (str): Número de telefone (formato: +5511999999999)
            message (str): Mensagem a enviar
            empresa_nome (str): Nome da empresa (para log)
            check_history (bool): Se True, verifica histórico antes de enviar

        Returns:
            dict: Resultado do envio
        """
        try:
            if not self.is_logged_in:
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Não está logado no WhatsApp Web',
                    'timestamp': datetime.now().isoformat()
                }

            logger.info(f'Enviando mensagem para {empresa_nome or phone}...')

            # Formatar telefone (remover caracteres especiais)
            clean_phone = ''.join(filter(str.isdigit, phone))

            # Abrir conversa via URL (mais confiável)
            url = f'https://web.whatsapp.com/send?phone={clean_phone}'
            self.driver.get(url)
            time.sleep(3)

            # Se check_history está ativo, verificar histórico
            if check_history:
                has_history = self.check_chat_history()
                if has_history:
                    logger.info(f'Conversa já iniciada com {empresa_nome or phone}. Pulando envio.')
                    return {
                        'success': False,
                        'phone': phone,
                        'empresa': empresa_nome,
                        'error': 'Conversa já iniciada anteriormente',
                        'status': 'ja_enviado',
                        'has_history': True,
                        'timestamp': datetime.now().isoformat()
                    }

            # Verificar se o número existe (procurar por mensagem de erro)
            try:
                error_element = self.driver.find_element(By.XPATH, '//*[contains(text(), "número de telefone") and contains(text(), "não") and contains(text(), "WhatsApp")]')
                logger.error(f'Número {phone} não existe no WhatsApp')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Número não existe no WhatsApp',
                    'status': 'nao_existe',
                    'timestamp': datetime.now().isoformat()
                }
            except:
                pass  # Número existe, continuar

            # Aguardar caixa de mensagem aparecer
            try:
                message_box = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
            except TimeoutException:
                # Pode ser que o número não exista
                logger.error(f'Timeout ao aguardar caixa de mensagem para {phone}. Número pode não existir.')
                return {
                    'success': False,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'error': 'Número provavelmente não existe no WhatsApp',
                    'status': 'nao_existe',
                    'timestamp': datetime.now().isoformat()
                }

            time.sleep(1)

            # Dividir mensagem em linhas e enviar
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:
                    # Shift+Enter para quebra de linha
                    message_box.send_keys(Keys.SHIFT, Keys.ENTER)

            time.sleep(0.5)

            # Enviar (Enter)
            message_box.send_keys(Keys.ENTER)

            time.sleep(2)

            # Verificar se enviou (procurar ícone de enviado)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check" or @data-icon="msg-dblcheck"]'))
                )
                logger.success(f'Mensagem enviada para {empresa_nome or phone}')

                return {
                    'success': True,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'timestamp': datetime.now().isoformat()
                }

            except TimeoutException:
                # Pode ter enviado mesmo sem encontrar o ícone
                logger.warning('Mensagem enviada mas não confirmada visualmente')
                return {
                    'success': True,
                    'phone': phone,
                    'empresa': empresa_nome,
                    'warning': 'Enviado mas não confirmado',
                    'timestamp': datetime.now().isoformat()
                }

        except TimeoutException:
            error_msg = 'Timeout aguardando elementos do WhatsApp'
            logger.error(f'{error_msg}: {phone}')
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar mensagem para {phone}: {error_msg}')
            return {
                'success': False,
                'phone': phone,
                'empresa': empresa_nome,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }

    def send_bulk_messages(self, empresas, message_template, delay=30, progress_callback=None):
        """
        Enviar mensagens para múltiplas empresas

        Args:
            empresas (list): Lista de empresas (dict com 'nome', 'whatsapp')
            message_template (str): Template da mensagem
            delay (int): Delay entre envios em segundos
            progress_callback (callable): Função para reportar progresso

        Returns:
            dict: Estatísticas do envio
        """
        if not self.is_logged_in:
            logger.error('Não está logado no WhatsApp Web')
            return {'total': 0, 'success': 0, 'failed': 0}

        total = len(empresas)
        success_count = 0
        failed_count = 0

        logger.info(f'Iniciando envio em massa para {total} empresas...')

        for i, empresa in enumerate(empresas, 1):
            try:
                # Personalizar mensagem
                message = self._personalize_message(message_template, empresa)

                # Enviar
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
                        'empresa_id': empresa.get('id'),
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa.get('nome', ''),
                        'phone': empresa.get('whatsapp', ''),
                        **result
                    })

                # Delay entre envios (exceto no último)
                if i < total:
                    logger.info(f'Aguardando {delay}s antes do próximo envio...')
                    time.sleep(delay)

            except Exception as e:
                logger.error(f'Erro ao processar empresa {empresa.get("nome", "")}: {str(e)}')
                failed_count += 1

                if progress_callback:
                    progress_callback({
                        'empresa_id': empresa.get('id'),
                        'current': i,
                        'total': total,
                        'success': success_count,
                        'failed': failed_count,
                        'empresa': empresa.get('nome', ''),
                        'phone': empresa.get('whatsapp', ''),
                        'success': False,
                        'error': str(e)
                    })

        stats = {
            'total': total,
            'success': success_count,
            'failed': failed_count,
            'success_rate': (success_count / total * 100) if total > 0 else 0
        }

        logger.success(f'Envio em massa concluído: {success_count}/{total} enviados')
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

    def get_session_info(self):
        """
        Obter informações da sessão

        Returns:
            dict: Informações da sessão
        """
        return {
            'session_name': self.session_name,
            'is_logged_in': self.is_logged_in,
            'session_dir': str(self.session_dir),
            'driver_active': self.driver is not None
        }

    def close(self):
        """Fechar navegador"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info('Navegador fechado')
            except:
                pass
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    # Teste do bot
    print('🧪 Testando WhatsApp Bot com Selenium...\n')

    bot = WhatsAppSelenium(session_name='test')

    # Iniciar
    if bot.start():
        print('✅ Navegador iniciado')

        if not bot.is_logged_in:
            print('📱 Escaneie o QR Code...')
            if bot.wait_for_login(timeout=60):
                print('✅ Login realizado!')
            else:
                print('❌ Timeout no login')
                bot.close()
                exit(1)

        # Teste de envio (substitua pelo seu número)
        # result = bot.send_message('+5511999999999', 'Teste do bot Selenium!', 'Teste')
        # print(f'Resultado: {result}')

        print('\n✅ Teste concluído. Feche o navegador ou aguarde...')
        input('Pressione Enter para fechar...')

        bot.close()
    else:
        print('❌ Erro ao iniciar navegador')
