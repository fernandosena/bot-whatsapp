#!/usr/bin/env python3
"""
Exemplo de uso das novas funcionalidades de busca expandida
"""

from src.scraper.google_maps_scraper import GoogleMapsScraper
from src.database.db import Database

def exemplo_busca_por_bairros():
    """
    Exemplo 1: Buscar por múltiplos bairros
    Ideal para cidades grandes - multiplica os resultados por número de bairros
    """
    print("=" * 80)
    print("EXEMPLO 1: Busca por Bairros")
    print("=" * 80)

    db = Database()

    # Definir bairros importantes da cidade
    # Para São Paulo, por exemplo:
    bairros_sp = [
        "Pinheiros",
        "Vila Madalena",
        "Moema",
        "Itaim Bibi",
        "Jardins",
        "Vila Mariana",
        "Santana",
        "Tatuapé"
    ]

    # Para Rio de Janeiro:
    bairros_rj = [
        "Copacabana",
        "Ipanema",
        "Leblon",
        "Botafogo",
        "Tijuca",
        "Barra da Tijuca"
    ]

    with GoogleMapsScraper(headless=True) as scraper:
        # Buscar padarias em múltiplos bairros do Rio
        empresas = scraper.search_by_neighborhoods(
            setor="Padaria",
            cidade="Rio de Janeiro",
            neighborhoods=bairros_rj,
            max_results_per_neighborhood=30,  # 30 por bairro = ~180 empresas
            db=db,
            required_contacts={
                'whatsapp': True,
                'telefone': True,
                'email': False,  # Email opcional
                'website': False,
                'instagram': False,
                'facebook': False,
                'linkedin': False,
                'twitter': False
            }
        )

        print(f"\n✅ Total de empresas únicas encontradas: {len(empresas)}")

def exemplo_busca_com_variacoes():
    """
    Exemplo 2: Buscar com variações de termos
    Encontra empresas usando sinônimos e termos relacionados
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Busca com Variações de Termos")
    print("=" * 80)

    db = Database()

    with GoogleMapsScraper(headless=True) as scraper:
        # Buscar restaurantes com variações automáticas
        # O sistema vai buscar: "restaurante", "restaurante delivery",
        # "comida caseira", "marmitaria", "food truck"
        empresas = scraper.search_with_variations(
            setor="Restaurante",
            cidade="São Paulo",
            max_results_per_variation=30,  # 30 por variação = ~150 empresas
            db=db,
            required_contacts={
                'whatsapp': True,
                'telefone': True,
                'email': False,
                'website': False,
                'instagram': False,
                'facebook': False,
                'linkedin': False,
                'twitter': False
            }
        )

        print(f"\n✅ Total de empresas únicas encontradas: {len(empresas)}")

def exemplo_combinado():
    """
    Exemplo 3: Combinar bairros + variações
    A estratégia mais poderosa - multiplica os resultados exponencialmente
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Combinação de Bairros + Variações")
    print("=" * 80)

    db = Database()

    bairros = ["Centro", "Zona Sul", "Zona Norte"]
    variacoes = ["Farmácia", "Drogaria", "Farmácia 24h"]

    with GoogleMapsScraper(headless=True) as scraper:
        todas_empresas = []
        nomes_vistos = set()

        for variacao in variacoes:
            print(f"\n{'='*60}")
            print(f"🔍 Processando variação: {variacao}")
            print(f"{'='*60}")

            empresas = scraper.search_by_neighborhoods(
                setor=variacao,
                cidade="Belo Horizonte",
                neighborhoods=bairros,
                max_results_per_neighborhood=20,  # 20 x 3 bairros x 3 variações = ~180 empresas
                db=db,
                required_contacts={
                    'whatsapp': True,
                    'telefone': True,
                    'email': False,
                    'website': False,
                    'instagram': False,
                    'facebook': False,
                    'linkedin': False,
                    'twitter': False
                }
            )

            # Filtrar duplicatas
            for empresa in empresas:
                if empresa['nome'] not in nomes_vistos:
                    nomes_vistos.add(empresa['nome'])
                    todas_empresas.append(empresa)

        print(f"\n{'='*80}")
        print(f"✅ TOTAL FINAL de empresas únicas: {len(todas_empresas)}")
        print(f"{'='*80}")

def exemplo_busca_simples_melhorada():
    """
    Exemplo 4: Busca simples com detecção melhorada de limite
    Agora avisa quando o Google Maps não carrega mais resultados
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Busca Simples com Detecção de Limite")
    print("=" * 80)

    db = Database()

    with GoogleMapsScraper(headless=True) as scraper:
        # Busca normal - agora avisa quando atingir o limite do Google
        empresas = scraper.search_businesses(
            setor="Pet Shop",
            cidade="Curitiba",
            max_results=200,  # Pode pedir 200, mas Google vai limitar
            db=db,
            required_contacts={
                'whatsapp': True,
                'telefone': True,
                'email': False,
                'website': False,
                'instagram': False,
                'facebook': False,
                'linkedin': False,
                'twitter': False
            }
        )

        print(f"\n✅ Total encontrado: {len(empresas)}")
        print("💡 Se atingiu o limite, use busca por bairros ou variações!")


if __name__ == "__main__":
    print("\n🚀 EXEMPLOS DE BUSCA EXPANDIDA NO GOOGLE MAPS\n")
    print("Escolha um exemplo para executar:\n")
    print("1 - Busca por Bairros (multiplica resultados por número de bairros)")
    print("2 - Busca com Variações (usa sinônimos e termos relacionados)")
    print("3 - Combinação Bairros + Variações (estratégia mais poderosa)")
    print("4 - Busca Simples Melhorada (detecta limite do Google Maps)")
    print("0 - Sair\n")

    escolha = input("Digite o número do exemplo: ").strip()

    if escolha == "1":
        exemplo_busca_por_bairros()
    elif escolha == "2":
        exemplo_busca_com_variacoes()
    elif escolha == "3":
        exemplo_combinado()
    elif escolha == "4":
        exemplo_busca_simples_melhorada()
    elif escolha == "0":
        print("👋 Até logo!")
    else:
        print("❌ Opção inválida!")
