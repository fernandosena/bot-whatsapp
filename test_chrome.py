#!/usr/bin/env python3
"""Script para testar se o ChromeDriver está funcionando corretamente"""

import sys
sys.path.insert(0, '/home/fernando-sena/Documentos/bot')

from src.scraper.google_maps_scraper import GoogleMapsScraper

def test_chrome():
    print("=" * 60)
    print("🧪 TESTE DO CHROMEDRIVER")
    print("=" * 60)

    try:
        print("\n1️⃣ Inicializando scraper...")
        scraper = GoogleMapsScraper(headless=True)

        print("\n2️⃣ Testando acesso a uma página simples...")
        scraper.driver.get("https://www.google.com")

        title = scraper.driver.title
        print(f"✅ Página carregada com sucesso!")
        print(f"   Título: {title}")

        print("\n3️⃣ Fechando navegador...")
        scraper.close()

        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ ERRO NO TESTE:")
        print(f"   {str(e)}")
        print("\n" + "=" * 60)
        print("❌ TESTE FALHOU")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_chrome()
    sys.exit(0 if success else 1)
