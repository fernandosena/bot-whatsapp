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

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

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
            driver_path = ChromeDriverManager().install()

            # Se o caminho aponta para o diretório, encontrar o executável correto
            if os.path.isdir(driver_path):
                # Procurar pelo arquivo chromedriver no diretório
                for root, dirs, files in os.walk(driver_path):
                    for file in files:
                        if file == 'chromedriver':
                            driver_path = os.path.join(root, file)
                            break

            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"❌ Erro ao configurar ChromeDriver: {str(e)}")
            print("💡 Tentando usar chromedriver do sistema...")
            # Tentar usar chromedriver do sistema
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def search_businesses(self, setor, cidade, max_results=50, db=None, progress_callback=None):
        """Buscar empresas no Google Maps"""
        search_query = f"{setor} em {cidade}"
        search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

        print(f"🔍 Buscando: {search_query}")
        print(f"📍 URL: {search_url}")

        self.driver.get(search_url)
        time.sleep(3)

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

            print(f"📊 Encontradas {len(business_urls)} empresas para processar\n")

            # Processar cada URL diretamente
            for idx, url in enumerate(business_urls):
                if not self.running or processed_count >= max_results:
                    break

                try:
                    print(f"🔄 [{processed_count + 1}/{len(business_urls)}] Acessando empresa...")

                    # Navegar diretamente para o URL da empresa
                    self.driver.get(url)
                    time.sleep(2)

                    # Extrair dados
                    business_data = self._extract_business_data(setor, cidade)

                    if business_data and business_data.get('nome'):
                        # Verificar se tem pelo menos um dado de contato
                        has_contact = (
                            business_data.get('telefone') or
                            business_data.get('email') or
                            business_data.get('whatsapp')
                        )

                        if has_contact:
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
                            print(f"⏭️  [{processed_count + 1}] {business_data.get('nome')} - SEM DADOS DE CONTATO")

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

                # Pequeno delay entre empresas
                time.sleep(0.3)

            print(f"\n{'='*50}")
            print(f"📊 Resumo da busca:")
            print(f"   Total processados: {processed_count}")
            print(f"   💾 Salvos: {saved_count}")
            print(f"   🔄 Atualizados: {updated_count}")
            print(f"   ⏭️  Ignorados: {skipped_count}")
            print(f"{'='*50}\n")

        except TimeoutException:
            print("⏰ Timeout ao carregar resultados")
        except Exception as e:
            print(f"❌ Erro durante a busca: {str(e)}")

        return businesses

    def _scroll_results(self, results_panel, max_results):
        """Scroll no painel de resultados para carregar mais empresas"""
        previous_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 20

        while scroll_attempts < max_scroll_attempts:
            # Scroll até o final
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', results_panel)
            time.sleep(2)

            # Verificar se carregou mais resultados
            current_height = self.driver.execute_script('return arguments[0].scrollHeight', results_panel)

            if current_height == previous_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0

            previous_height = current_height

            # Verificar quantidade de resultados
            result_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]'))
            if result_count >= max_results:
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
        """Extrair email do website da empresa"""
        if not website_url:
            return None

        try:
            # Fazer requisição ao website
            response = requests.get(website_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()

                # Regex para email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, page_text)

                if emails:
                    # Filtrar emails de exemplo
                    valid_emails = [
                        email for email in emails
                        if 'example.com' not in email.lower()
                        and 'test.com' not in email.lower()
                        and 'sample.com' not in email.lower()
                        and 'domain.com' not in email.lower()
                    ]

                    return valid_emails[0] if valid_emails else None

        except Exception:
            # Silenciar erros ao acessar website
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
