from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import requests
from bs4 import BeautifulSoup
import urllib3

# Desabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GoogleMapsScraper:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.running = True
        self._setup_driver()

    def _setup_driver(self):
        """Configurar o driver do Selenium"""
        import os
        import shutil

        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        # Otimizações de performance e correção para ambiente Linux
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        # Argumentos essenciais para rodar em ambiente headless Linux
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--enable-automation')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--use-mock-keychain')

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Desabilitar imagens para performance (economiza ~70% de banda)
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.managed_default_content_settings.stylesheets': 2,
            'profile.managed_default_content_settings.cookies': 1,
            'profile.managed_default_content_settings.javascript': 1,
            'profile.managed_default_content_settings.plugins': 2,
            'profile.managed_default_content_settings.popups': 2,
            'profile.managed_default_content_settings.geolocation': 2,
            'profile.managed_default_content_settings.notifications': 2,
            'profile.managed_default_content_settings.media_stream': 2,
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # User agent
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )

        # Detectar qual navegador está instalado
        chromium_paths = [
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/snap/bin/chromium',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable'
        ]

        chrome_binary = None
        for path in chromium_paths:
            if os.path.exists(path):
                chrome_binary = path
                break

        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            print(f"🌐 Usando navegador: {chrome_binary}")

        # Instalar e configurar o ChromeDriver corretamente
        try:
            print("🔧 Instalando/verificando ChromeDriver...")
            driver_path = ChromeDriverManager().install()

            # Se o caminho aponta para o diretório ou arquivo errado, encontrar o executável correto
            if os.path.isdir(driver_path) or not os.path.basename(driver_path) == 'chromedriver':
                # Obter o diretório base
                base_dir = os.path.dirname(driver_path) if os.path.isfile(driver_path) else driver_path

                # Procurar especificamente pelo arquivo 'chromedriver' (sem extensão)
                chromedriver_path = os.path.join(base_dir, 'chromedriver')
                if os.path.isfile(chromedriver_path) and os.access(chromedriver_path, os.X_OK):
                    driver_path = chromedriver_path
                else:
                    # Se não encontrar no mesmo diretório, procurar recursivamente
                    found = False
                    for root, dirs, files in os.walk(base_dir):
                        if 'chromedriver' in files:
                            test_path = os.path.join(root, 'chromedriver')
                            if os.access(test_path, os.X_OK):
                                driver_path = test_path
                                found = True
                                break
                    if not found:
                        raise Exception(f"Executável 'chromedriver' não encontrado em {base_dir}")

            if os.path.isfile(driver_path) and os.access(driver_path, os.X_OK):
                print(f"✅ ChromeDriver encontrado em: {driver_path}")

                service = Service(driver_path)
                print("🚀 Iniciando Chrome...")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ Chrome iniciado com sucesso!")
            else:
                raise Exception(f"ChromeDriver não encontrado ou não é executável: {driver_path}")

        except Exception as e:
            print(f"❌ Erro ao configurar ChromeDriver: {str(e)}")
            print("💡 Tentando usar chromedriver do sistema...")
            try:
                # Tentar vários caminhos possíveis do sistema
                system_paths = [
                    '/usr/local/bin/chromedriver',
                    '/usr/bin/chromedriver',
                    shutil.which('chromedriver')
                ]

                driver_found = None
                for path in system_paths:
                    if path and os.path.isfile(path) and os.access(path, os.X_OK):
                        driver_found = path
                        break

                if driver_found:
                    service = Service(driver_found)
                    print(f"🚀 Iniciando Chrome com driver do sistema ({driver_found})...")
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    print("✅ Chrome iniciado com sucesso!")
                else:
                    raise Exception("ChromeDriver não encontrado no sistema")

            except Exception as e2:
                print(f"❌ Erro ao usar ChromeDriver do sistema: {str(e2)}")
                raise Exception(f"Falha ao inicializar ChromeDriver. Verifique se o Chrome/Chromium está instalado corretamente.\nErro 1: {str(e)}\nErro 2: {str(e2)}")

    def search_businesses(self, setor, cidade, max_results=50, db=None, progress_callback=None, continue_from_checkpoint=True, required_contacts=None):
        """Buscar empresas no Google Maps"""
        search_query = f"{setor} em {cidade}"
        search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

        # Filtros de contato padrão (se não especificado, aceita qualquer contato)
        if required_contacts is None:
            required_contacts = {
                'whatsapp': True,
                'telefone': True,
                'email': True,
                'website': True,
                'instagram': True,
                'facebook': True,
                'linkedin': True,
                'twitter': True
            }

        print(f"🔍 Buscando: {search_query}")
        print(f"📋 Filtros ativos: {', '.join([k.capitalize() for k, v in required_contacts.items() if v])}")
        print(f"📍 URL: {search_url}")

        # Verificar se existe checkpoint anterior
        start_index = 0
        checkpoint = None
        if db and continue_from_checkpoint:
            checkpoint = db.get_checkpoint(setor, cidade)
            if checkpoint and checkpoint['status'] == 'em_andamento':
                start_index = checkpoint['ultimo_indice']
                print(f"📌 Checkpoint encontrado! Continuando do índice {start_index}")
                print(f"   Já processados: {checkpoint['total_processados']} | Salvos: {checkpoint['total_salvos']}")
            elif checkpoint and checkpoint['status'] == 'concluido':
                print(f"✅ Busca já foi concluída anteriormente!")
                print(f"   Total processados: {checkpoint['total_processados']} | Salvos: {checkpoint['total_salvos']}")
                resposta = input("Deseja recomeçar do zero? (s/N): ").lower()
                if resposta == 's':
                    db.reset_checkpoint(setor, cidade)
                    start_index = 0
                    print("🔄 Checkpoint resetado! Começando do zero...")
                else:
                    return []

        self.driver.get(search_url)
        time.sleep(1)  # Reduzido de 3s para 1s

        businesses = []
        processed_count = 0
        saved_count = 0
        updated_count = 0
        skipped_count = 0

        try:
            # Localizar o painel de resultados
            results_panel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )

            # Fazer scroll inicial para carregar mais resultados
            print(f"📊 Fazendo scroll para carregar resultados...")
            self._scroll_results(results_panel, max_results)

            # Obter todos os URLs das empresas ANTES de começar a processar
            print(f"📊 Coletando URLs das empresas...")
            business_urls = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]')

            for element in result_elements[:max_results]:
                try:
                    url = element.get_attribute('href')
                    if url and url not in business_urls:
                        business_urls.append(url)
                except:
                    pass

            print(f"📊 Encontradas {len(business_urls)} empresas para processar")

            # Criar ou atualizar checkpoint inicial
            if db:
                db.create_or_update_checkpoint(
                    setor, cidade,
                    total_encontrados=len(business_urls),
                    total_processados=checkpoint['total_processados'] if checkpoint else 0,
                    total_salvos=checkpoint['total_salvos'] if checkpoint else 0,
                    ultimo_indice=start_index,
                    status='em_andamento'
                )

            # Limitar URLs ao max_results solicitado
            business_urls = business_urls[:max_results]

            # Pular URLs já processadas (baseado no checkpoint)
            if start_index > 0:
                print(f"⏭️  Pulando {start_index} empresas já processadas...")

                # Verificar se ainda há empresas para processar
                if start_index >= len(business_urls):
                    print(f"\n⚠️  AVISO: Checkpoint está no índice {start_index}, mas Google Maps retornou apenas {len(business_urls)} resultados.")
                    print(f"📌 Esta busca já foi completada! Não há novas empresas para processar.")
                    print(f"\n💡 Dicas para coletar mais empresas:")
                    print(f"   1. Divida por bairros: '{setor} em [Bairro], {cidade}'")
                    print(f"   2. Use termos mais específicos: '{setor} delivery', '{setor} artesanal', etc")
                    print(f"   3. Tente cidades vizinhas")
                    print(f"   4. Reset o checkpoint se quiser recomeçar a mesma busca\n")

                    # Marcar checkpoint como concluído
                    if db:
                        db.mark_checkpoint_complete(setor, cidade)
                        print(f"✅ Checkpoint marcado como CONCLUÍDO")

                    # Retornar resumo
                    print(f"\n{'=' * 50}")
                    print(f"📊 Resumo da busca:")
                    print(f"   Total processados: {checkpoint['total_processados'] if checkpoint else 0}")
                    print(f"   💾 Salvos: {checkpoint['total_salvos'] if checkpoint else 0}")
                    print(f"   🔄 Atualizados: {updated_count}")
                    print(f"   ⏭️  Ignorados: {skipped_count}")
                    print(f"{'=' * 50}\n")

                    return businesses

                business_urls = business_urls[start_index:]
                processed_count = start_index
                if checkpoint:
                    saved_count = checkpoint['total_salvos']
                    updated_count = checkpoint.get('total_atualizados', 0)

            # Processar em chunks para evitar sobrecarga de memória
            import os
            chunk_size = int(os.getenv('CHUNK_SIZE', 100))
            total_chunks = (len(business_urls) + chunk_size - 1) // chunk_size
            print(f"📦 Processando em {total_chunks} chunks de {chunk_size} empresas\n")

            # Processar cada URL diretamente
            for idx, url in enumerate(business_urls):
                if not self.running or processed_count >= max_results:
                    break

                try:
                    chunk_num = (idx // chunk_size) + 1
                    actual_index = start_index + idx
                    print(f"🔄 [Chunk {chunk_num}/{total_chunks}] [{actual_index + 1}/{start_index + len(business_urls)}] Acessando empresa...")

                    # Navegar diretamente para o URL da empresa
                    self.driver.get(url)
                    time.sleep(0.8)  # Reduzido de 2s para 0.8s

                    # Extrair dados
                    business_data = self._extract_business_data(setor, cidade)

                    if business_data and business_data.get('nome'):
                        # Verificar se tem pelo menos um dos contatos requeridos
                        has_required_contact = False

                        if required_contacts.get('whatsapp') and business_data.get('whatsapp'):
                            has_required_contact = True
                        if required_contacts.get('telefone') and business_data.get('telefone'):
                            has_required_contact = True
                        if required_contacts.get('email') and business_data.get('email'):
                            has_required_contact = True
                        if required_contacts.get('website') and business_data.get('website'):
                            has_required_contact = True
                        if required_contacts.get('instagram') and business_data.get('instagram'):
                            has_required_contact = True
                        if required_contacts.get('facebook') and business_data.get('facebook'):
                            has_required_contact = True
                        if required_contacts.get('linkedin') and business_data.get('linkedin'):
                            has_required_contact = True
                        if required_contacts.get('twitter') and business_data.get('twitter'):
                            has_required_contact = True

                        if has_required_contact:
                            businesses.append(business_data)

                            # Salvar ou atualizar no banco de dados
                            status = 'no_contact'
                            if db:
                                result = self._save_or_update_business(db, business_data)
                                if result == 'saved':
                                    saved_count += 1
                                    status = 'saved'
                                    print(f"✅ [{processed_count + 1}] {business_data['nome']} - SALVO")
                                elif result == 'updated':
                                    updated_count += 1
                                    status = 'updated'
                                    print(f"🔄 [{processed_count + 1}] {business_data['nome']} - ATUALIZADO")
                                else:
                                    skipped_count += 1
                                    status = 'skipped'
                                    print(f"⏭️  [{processed_count + 1}] {business_data['nome']} - JÁ EXISTE (sem novos dados)")
                            else:
                                saved_count += 1
                                status = 'saved'
                                print(f"✅ [{processed_count + 1}] {business_data['nome']}")

                            # Callback de progresso
                            if progress_callback:
                                progress_callback({
                                    'processed': processed_count + 1,
                                    'total': max_results,
                                    'saved': saved_count,
                                    'updated': updated_count,
                                    'skipped': skipped_count,
                                    'current_business': business_data['nome'],
                                    'status': status
                                })
                        else:
                            skipped_count += 1
                            # Mostrar quais contatos a empresa tem
                            available_contacts = []
                            if business_data.get('whatsapp'):
                                available_contacts.append('WhatsApp')
                            if business_data.get('telefone'):
                                available_contacts.append('Telefone')
                            if business_data.get('email'):
                                available_contacts.append('Email')
                            if business_data.get('website'):
                                available_contacts.append('Website')
                            if business_data.get('instagram'):
                                available_contacts.append('Instagram')
                            if business_data.get('facebook'):
                                available_contacts.append('Facebook')
                            if business_data.get('linkedin'):
                                available_contacts.append('LinkedIn')
                            if business_data.get('twitter'):
                                available_contacts.append('Twitter')

                            contacts_str = ', '.join(available_contacts) if available_contacts else 'Nenhum'
                            print(f"⏭️  [{processed_count + 1}] {business_data.get('nome')} - NÃO ATENDE FILTROS (tem: {contacts_str})")

                            # Callback de progresso
                            if progress_callback:
                                progress_callback({
                                    'processed': processed_count + 1,
                                    'total': max_results,
                                    'saved': saved_count,
                                    'updated': updated_count,
                                    'skipped': skipped_count,
                                    'current_business': business_data.get('nome', 'Sem nome'),
                                    'status': 'no_contact'
                                })

                except Exception as e:
                    print(f"❌ Erro ao processar empresa: {str(e)}")
                    # Continuar com a próxima empresa mesmo se houver erro
                    pass

                # Incrementar contador de processados
                processed_count += 1

                # Atualizar checkpoint a cada empresa processada
                if db:
                    db.update_checkpoint_progress(
                        setor, cidade,
                        processados_increment=0,  # Já incrementamos manualmente acima
                        salvos_increment=0,  # Já incrementamos manualmente acima
                        ultimo_indice=actual_index + 1  # Próximo índice a processar
                    )

                # Delay mínimo entre empresas (removido para máxima velocidade)
                # time.sleep(0.1)

            print(f"\n{'='*50}")
            print(f"📊 Resumo da busca:")
            print(f"   Total processados: {processed_count}")
            print(f"   💾 Salvos: {saved_count}")
            print(f"   🔄 Atualizados: {updated_count}")
            print(f"   ⏭️  Ignorados: {skipped_count}")
            print(f"{'='*50}\n")

            # Marcar checkpoint como concluído
            if db and processed_count >= max_results:
                db.mark_checkpoint_complete(setor, cidade)
                print(f"✅ Checkpoint marcado como concluído!")

        except TimeoutException:
            print("⏰ Timeout ao carregar resultados")
            # Salvar checkpoint mesmo em caso de erro
            if db:
                db.create_or_update_checkpoint(
                    setor, cidade,
                    total_processados=processed_count,
                    total_salvos=saved_count,
                    ultimo_indice=start_index + processed_count,
                    status='erro'
                )
        except Exception as e:
            print(f"❌ Erro durante a busca: {str(e)}")
            # Salvar checkpoint mesmo em caso de erro
            if db:
                db.create_or_update_checkpoint(
                    setor, cidade,
                    total_processados=processed_count,
                    total_salvos=saved_count,
                    ultimo_indice=start_index + processed_count,
                    status='erro'
                )

        return businesses

    def _scroll_results(self, results_panel, max_results):
        """Scroll no painel de resultados para carregar mais empresas"""
        previous_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 20
        no_new_results_count = 0

        while scroll_attempts < max_scroll_attempts:
            # Contar resultados antes do scroll
            result_count_before = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]'))

            # Scroll até o final
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', results_panel)
            time.sleep(2)

            # Verificar se carregou mais resultados
            current_height = self.driver.execute_script('return arguments[0].scrollHeight', results_panel)
            result_count_after = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]'))

            # Detectar se Google Maps atingiu o limite
            if current_height == previous_height and result_count_before == result_count_after:
                scroll_attempts += 1
                no_new_results_count += 1

                # Se não carregou nada novo por 3 tentativas, provavelmente atingiu o limite do Google
                if no_new_results_count >= 3:
                    print(f"\n⚠️  Google Maps atingiu o limite de resultados ({result_count_after} empresas)")
                    print(f"💡 Dica: Para encontrar mais empresas:")
                    print(f"   • Divida por bairros/regiões")
                    print(f"   • Use termos de busca mais específicos")
                    print(f"   • Tente variações do setor\n")
                    break
            else:
                scroll_attempts = 0
                no_new_results_count = 0

            previous_height = current_height

            # Verificar quantidade de resultados
            if result_count_after >= max_results:
                break

    def _extract_business_data(self, setor, cidade):
        """Extrair dados da empresa da página"""
        data = {}

        try:
            # Nome
            try:
                nome = self.driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text
                data['nome'] = nome
            except NoSuchElementException:
                data['nome'] = None

            # Endereço
            try:
                endereco = self.driver.find_element(
                    By.CSS_SELECTOR, 'button[data-item-id="address"] div.fontBodyMedium'
                ).text
                data['endereco'] = endereco
            except NoSuchElementException:
                data['endereco'] = None

            # Telefone
            try:
                telefone = self.driver.find_element(
                    By.CSS_SELECTOR, 'button[data-item-id^="phone:tel:"] div.fontBodyMedium'
                ).text
                data['telefone'] = telefone
                data['whatsapp'] = self._format_phone_to_whatsapp(telefone)
            except NoSuchElementException:
                data['telefone'] = None
                data['whatsapp'] = None

            # Website
            try:
                website = self.driver.find_element(
                    By.CSS_SELECTOR, 'a[data-item-id="authority"]'
                ).get_attribute('href')
                data['website'] = website

                # Tentar extrair email do website
                data['email'] = self._extract_email_from_website(website)
            except NoSuchElementException:
                data['website'] = None
                data['email'] = None

            # Redes Sociais - buscar todos os links da página
            social_links = self._extract_social_media()
            data['instagram'] = social_links.get('instagram')
            data['facebook'] = social_links.get('facebook')
            data['linkedin'] = social_links.get('linkedin')
            data['twitter'] = social_links.get('twitter')

            # Rating
            try:
                rating_text = self.driver.find_element(
                    By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]'
                ).text
                data['rating'] = float(rating_text.replace(',', '.'))
            except (NoSuchElementException, ValueError):
                data['rating'] = None

            # Total de avaliações
            try:
                reviews_text = self.driver.find_element(
                    By.CSS_SELECTOR, 'div.F7nice span[aria-label*="avaliações"]'
                ).text
                # Extrair apenas números
                reviews_num = re.sub(r'\D', '', reviews_text)
                data['total_reviews'] = int(reviews_num) if reviews_num else None
            except (NoSuchElementException, ValueError):
                data['total_reviews'] = None

            # Horário de funcionamento
            try:
                horario = self.driver.find_element(
                    By.CSS_SELECTOR, 'div[aria-label*="Horário"]'
                ).get_attribute('aria-label')
                data['horario_funcionamento'] = horario
            except NoSuchElementException:
                data['horario_funcionamento'] = None

            # URL do Google Maps
            data['google_maps_url'] = self.driver.current_url

            # Adicionar setor e cidade
            data['setor'] = setor
            data['cidade'] = cidade
            data['latitude'] = None
            data['longitude'] = None

        except Exception as e:
            print(f"❌ Erro ao extrair dados: {str(e)}")
            return None

        return data

    def _extract_social_media(self):
        """Extrair links de redes sociais da página"""
        social_links = {
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'twitter': None
        }

        try:
            # Buscar todos os links da página
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')

            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue

                    # Instagram
                    if 'instagram.com' in href and not social_links['instagram']:
                        social_links['instagram'] = href

                    # Facebook
                    elif ('facebook.com' in href or 'fb.com' in href) and not social_links['facebook']:
                        social_links['facebook'] = href

                    # LinkedIn
                    elif 'linkedin.com' in href and not social_links['linkedin']:
                        social_links['linkedin'] = href

                    # Twitter/X
                    elif ('twitter.com' in href or 'x.com' in href) and not social_links['twitter']:
                        social_links['twitter'] = href

                except:
                    continue

        except Exception as e:
            pass

        return social_links

    def _format_phone_to_whatsapp(self, phone):
        """Formatar telefone para WhatsApp (formato internacional)"""
        if not phone:
            return None

        # Remover caracteres não numéricos
        clean_phone = re.sub(r'\D', '', phone)

        # Se já começa com 55 (Brasil), retornar
        if clean_phone.startswith('55'):
            return clean_phone

        # Adicionar código do Brasil
        return '55' + clean_phone

    def _extract_email_from_website(self, website_url):
        """Extrair email do website da empresa (otimizado)"""
        if not website_url:
            return None

        try:
            # Fazer requisição ao website com timeout reduzido
            response = requests.get(
                website_url,
                timeout=3,  # Reduzido de 10s para 3s
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                allow_redirects=True,
                verify=False  # Ignora SSL para sites com certificado inválido
            )

            if response.status_code == 200:
                # Usar apenas o texto bruto sem BeautifulSoup para ser mais rápido
                page_text = response.text[:10000]  # Apenas primeiros 10KB (otimização)

                # Regex para email (mais eficiente)
                email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                match = re.search(email_pattern, page_text)

                if match:
                    email = match.group()
                    # Filtrar emails de exemplo
                    if not any(x in email.lower() for x in ['example', 'test', 'sample', 'domain', 'noreply', 'no-reply']):
                        return email

        except Exception:
            # Silenciar erros ao acessar website (timeout, SSL, etc)
            pass

        return None

    def _save_or_update_business(self, db, business_data):
        """Salvar ou atualizar empresa no banco de dados"""
        # Verificar se empresa já existe (apenas por nome se não tiver endereço)
        nome = business_data.get('nome')
        endereco = business_data.get('endereco')

        cursor = db.cursor

        if endereco:
            # Se tem endereço, verifica nome + endereço
            existing = cursor.execute(
                'SELECT * FROM empresas WHERE nome = ? AND endereco = ?',
                (nome, endereco)
            ).fetchone()
        else:
            # Se não tem endereço, verifica apenas nome
            existing = cursor.execute(
                'SELECT * FROM empresas WHERE nome = ?',
                (nome,)
            ).fetchone()

        if existing:
            existing_dict = dict(existing)

            # Verificar se há novos dados de contato para atualizar
            has_new_data = False
            updates = []

            # Verificar cada campo individualmente
            if business_data.get('telefone') and not existing_dict.get('telefone'):
                has_new_data = True
                updates.append(f"telefone: {business_data.get('telefone')}")

            if business_data.get('whatsapp') and not existing_dict.get('whatsapp'):
                has_new_data = True
                updates.append(f"whatsapp: {business_data.get('whatsapp')}")

            if business_data.get('email') and not existing_dict.get('email'):
                has_new_data = True
                updates.append(f"email: {business_data.get('email')}")

            if business_data.get('website') and not existing_dict.get('website'):
                has_new_data = True
                updates.append(f"website: {business_data.get('website')}")

            if business_data.get('instagram') and not existing_dict.get('instagram'):
                has_new_data = True
                updates.append(f"instagram: {business_data.get('instagram')}")

            if business_data.get('facebook') and not existing_dict.get('facebook'):
                has_new_data = True
                updates.append(f"facebook: {business_data.get('facebook')}")

            if business_data.get('linkedin') and not existing_dict.get('linkedin'):
                has_new_data = True
                updates.append(f"linkedin: {business_data.get('linkedin')}")

            if business_data.get('twitter') and not existing_dict.get('twitter'):
                has_new_data = True
                updates.append(f"twitter: {business_data.get('twitter')}")

            if has_new_data:
                # Atualizar apenas os campos que estão vazios
                cursor.execute('''
                    UPDATE empresas SET
                        telefone = COALESCE(telefone, ?),
                        whatsapp = COALESCE(whatsapp, ?),
                        email = COALESCE(email, ?),
                        website = COALESCE(website, ?),
                        instagram = COALESCE(instagram, ?),
                        facebook = COALESCE(facebook, ?),
                        linkedin = COALESCE(linkedin, ?),
                        twitter = COALESCE(twitter, ?),
                        rating = COALESCE(?, rating),
                        total_reviews = COALESCE(?, total_reviews),
                        horario_funcionamento = COALESCE(horario_funcionamento, ?),
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    business_data.get('telefone'),
                    business_data.get('whatsapp'),
                    business_data.get('email'),
                    business_data.get('website'),
                    business_data.get('instagram'),
                    business_data.get('facebook'),
                    business_data.get('linkedin'),
                    business_data.get('twitter'),
                    business_data.get('rating'),
                    business_data.get('total_reviews'),
                    business_data.get('horario_funcionamento'),
                    existing_dict['id']
                ))
                db.conn.commit()
                print(f"   📝 Atualizando: {', '.join(updates)}")
                return 'updated'
            else:
                print(f"   ℹ️  Empresa já tem todos os dados disponíveis")
                return 'skipped'
        else:
            # Inserir nova empresa
            result = db.insert_empresa(business_data)
            if result:
                return 'saved'
            else:
                # Se insert_empresa retornou None/0, pode ser UNIQUE constraint
                # Buscar empresa que pode ter sido ignorada e tentar atualizar
                print(f"   ⚠️  INSERT ignorado (possível duplicata) - buscando para atualizar...")

                # Tentar encontrar a empresa pelo nome (pode ter endereço levemente diferente)
                cursor = db.cursor
                similar = cursor.execute(
                    'SELECT * FROM empresas WHERE nome = ?',
                    (nome,)
                ).fetchone()

                if similar:
                    similar_dict = dict(similar)
                    print(f"   🔍 Empresa encontrada: {similar_dict['nome']} (ID: {similar_dict['id']})")
                    print(f"      Endereço BD: {similar_dict.get('endereco', 'N/A')}")
                    print(f"      Endereço novo: {endereco or 'N/A'}")

                    # Verificar se há novos dados de contato para atualizar
                    has_new_data = False
                    updates = []

                    if business_data.get('telefone') and not similar_dict.get('telefone'):
                        has_new_data = True
                        updates.append(f"telefone: {business_data.get('telefone')}")

                    if business_data.get('whatsapp') and not similar_dict.get('whatsapp'):
                        has_new_data = True
                        updates.append(f"whatsapp: {business_data.get('whatsapp')}")

                    if business_data.get('email') and not similar_dict.get('email'):
                        has_new_data = True
                        updates.append(f"email: {business_data.get('email')}")

                    if business_data.get('website') and not similar_dict.get('website'):
                        has_new_data = True
                        updates.append(f"website: {business_data.get('website')}")

                    if business_data.get('instagram') and not similar_dict.get('instagram'):
                        has_new_data = True
                        updates.append(f"instagram: {business_data.get('instagram')}")

                    if business_data.get('facebook') and not similar_dict.get('facebook'):
                        has_new_data = True
                        updates.append(f"facebook: {business_data.get('facebook')}")

                    if business_data.get('linkedin') and not similar_dict.get('linkedin'):
                        has_new_data = True
                        updates.append(f"linkedin: {business_data.get('linkedin')}")

                    if business_data.get('twitter') and not similar_dict.get('twitter'):
                        has_new_data = True
                        updates.append(f"twitter: {business_data.get('twitter')}")

                    if has_new_data:
                        cursor.execute('''
                            UPDATE empresas SET
                                telefone = COALESCE(telefone, ?),
                                whatsapp = COALESCE(whatsapp, ?),
                                email = COALESCE(email, ?),
                                website = COALESCE(website, ?),
                                instagram = COALESCE(instagram, ?),
                                facebook = COALESCE(facebook, ?),
                                linkedin = COALESCE(linkedin, ?),
                                twitter = COALESCE(twitter, ?),
                                rating = COALESCE(?, rating),
                                total_reviews = COALESCE(?, total_reviews),
                                horario_funcionamento = COALESCE(horario_funcionamento, ?),
                                data_atualizacao = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (
                            business_data.get('telefone'),
                            business_data.get('whatsapp'),
                            business_data.get('email'),
                            business_data.get('website'),
                            business_data.get('instagram'),
                            business_data.get('facebook'),
                            business_data.get('linkedin'),
                            business_data.get('twitter'),
                            business_data.get('rating'),
                            business_data.get('total_reviews'),
                            business_data.get('horario_funcionamento'),
                            similar_dict['id']
                        ))
                        db.conn.commit()
                        print(f"   ✅ Atualizado com: {', '.join(updates)}")
                        return 'updated'
                    else:
                        print(f"   ℹ️  Empresa já tem todos os dados disponíveis")
                        return 'skipped'
                else:
                    print(f"   ❌ Erro inesperado: INSERT falhou mas empresa não foi encontrada")
                    return 'skipped'

    def stop(self):
        """Parar o scraping"""
        self.running = False

    def close(self):
        """Fechar o navegador"""
        self.running = False
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def search_with_variations(self, setor, cidade, max_results_per_variation=50, db=None, progress_callback=None, required_contacts=None):
        """
        Buscar empresas usando múltiplas variações de termos

        Args:
            setor: Setor principal (ex: "Padaria")
            cidade: Cidade
            max_results_per_variation: Máximo de resultados por variação
            db: Instância do banco de dados
            progress_callback: Callback para progresso
            required_contacts: Filtros de contato

        Returns:
            Lista consolidada de empresas (sem duplicatas)
        """
        variations = self._generate_search_variations(setor)
        all_businesses = []
        seen_names = set()

        print(f"\n🔄 Iniciando busca com {len(variations)} variações de '{setor}'")
        print(f"📋 Variações: {', '.join(variations)}\n")

        for idx, variation in enumerate(variations, 1):
            print(f"\n{'='*60}")
            print(f"🔍 Variação {idx}/{len(variations)}: '{variation}'")
            print(f"{'='*60}\n")

            try:
                businesses = self.search_businesses(
                    setor=variation,
                    cidade=cidade,
                    max_results=max_results_per_variation,
                    db=db,
                    progress_callback=progress_callback,
                    continue_from_checkpoint=True,
                    required_contacts=required_contacts
                )

                # Filtrar duplicatas por nome
                new_businesses = 0
                for business in businesses:
                    if business['nome'] not in seen_names:
                        seen_names.add(business['nome'])
                        all_businesses.append(business)
                        new_businesses += 1

                print(f"✅ Variação concluída: {len(businesses)} encontradas, {new_businesses} novas")

            except Exception as e:
                print(f"❌ Erro na variação '{variation}': {str(e)}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ Busca com variações concluída!")
        print(f"📊 Total de empresas únicas: {len(all_businesses)}")
        print(f"{'='*60}\n")

        return all_businesses

    def search_by_neighborhoods(self, setor, cidade, neighborhoods, max_results_per_neighborhood=50, db=None, progress_callback=None, required_contacts=None):
        """
        Buscar empresas dividindo por bairros/regiões

        Args:
            setor: Setor (ex: "Padaria")
            cidade: Cidade
            neighborhoods: Lista de bairros/regiões (ex: ["Copacabana", "Ipanema", "Leblon"])
            max_results_per_neighborhood: Máximo de resultados por bairro
            db: Instância do banco de dados
            progress_callback: Callback para progresso
            required_contacts: Filtros de contato

        Returns:
            Lista consolidada de empresas (sem duplicatas)
        """
        all_businesses = []
        seen_names = set()

        print(f"\n🗺️  Iniciando busca por {len(neighborhoods)} bairros/regiões")
        print(f"📋 Bairros: {', '.join(neighborhoods)}\n")

        for idx, neighborhood in enumerate(neighborhoods, 1):
            print(f"\n{'='*60}")
            print(f"📍 Bairro {idx}/{len(neighborhoods)}: {neighborhood}, {cidade}")
            print(f"{'='*60}\n")

            try:
                # Buscar com localização específica
                search_query = f"{setor} em {neighborhood}, {cidade}"

                businesses = self.search_businesses(
                    setor=search_query,
                    cidade="",  # Já incluído no setor
                    max_results=max_results_per_neighborhood,
                    db=db,
                    progress_callback=progress_callback,
                    continue_from_checkpoint=True,
                    required_contacts=required_contacts
                )

                # Filtrar duplicatas por nome
                new_businesses = 0
                for business in businesses:
                    if business['nome'] not in seen_names:
                        seen_names.add(business['nome'])
                        all_businesses.append(business)
                        new_businesses += 1

                print(f"✅ Bairro concluído: {len(businesses)} encontradas, {new_businesses} novas")

            except Exception as e:
                print(f"❌ Erro no bairro '{neighborhood}': {str(e)}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ Busca por bairros concluída!")
        print(f"📊 Total de empresas únicas: {len(all_businesses)}")
        print(f"{'='*60}\n")

        return all_businesses

    def _generate_search_variations(self, setor):
        """
        Gerar variações de termos de busca para um setor

        Args:
            setor: Setor original (ex: "Padaria")

        Returns:
            Lista de variações
        """
        variations = [setor]  # Incluir o termo original

        # Dicionário de variações por setor comum
        sector_variations = {
            'padaria': ['padaria artesanal', 'pães e doces', 'confeitaria', 'padaria delivery'],
            'restaurante': ['restaurante delivery', 'comida caseira', 'marmitaria', 'food truck'],
            'farmácia': ['drogaria', 'farmácia de manipulação', 'farmácia 24h'],
            'mercado': ['supermercado', 'mercearia', 'minimercado', 'empório'],
            'pet shop': ['clínica veterinária', 'banho e tosa', 'produtos para pets'],
            'academia': ['crossfit', 'estúdio de pilates', 'box de luta', 'personal trainer'],
            'salão de beleza': ['barbearia', 'cabeleireiro', 'estética', 'manicure'],
            'lanchonete': ['hamburgueria', 'pizzaria', 'lanches delivery', 'fast food'],
            'advocacia': ['escritório de advocacia', 'advogado', 'consultoria jurídica'],
            'contabilidade': ['contador', 'escritório contábil', 'consultoria fiscal'],
        }

        # Buscar variações no dicionário (case insensitive)
        setor_lower = setor.lower()
        for key, vars in sector_variations.items():
            if key in setor_lower:
                variations.extend(vars)
                break

        # Se não encontrou variações específicas, adicionar modificadores genéricos
        if len(variations) == 1:
            variations.extend([
                f"{setor} delivery",
                f"{setor} artesanal",
                f"{setor} profissional"
            ])

        # Remover duplicatas mantendo ordem
        seen = set()
        unique_variations = []
        for v in variations:
            if v.lower() not in seen:
                seen.add(v.lower())
                unique_variations.append(v)

        return unique_variations
