import sys
import shodan

# Sua chave API fornecida
API_KEY = "i3gwQyJmXNX02q5ddFxYeJvycvK146KY"

try:
    api = shodan.Shodan(API_KEY)
except Exception as e:
    print(f"[-] Erro ao inicializar a API do Shodan: {e}")
    sys.exit(1)


def limpar_tela():
    print("\n" + "=" * 60 + "\n")


def consultar_ip():
    ip = input("\n[+] Digite o endereço IP do alvo: ").strip()
    if not ip:
        return
    try:
        print(f"\n[*] Consultando informações para {ip}...\n")
        host = api.host(ip)

        print(f"IP: {host.get('ip_str')}")
        print(f"Organização: {host.get('org', 'N/A')}")
        print(f"Provedor (ISP): {host.get('isp', 'N/A')}")
        print(f"País: {host.get('country_name', 'N/A')} ({host.get('country_code', 'N/A')})")
        print(f"Cidade: {host.get('city', 'N/A')}")
        print(f"Sistema Operacional: {host.get('os', 'N/A')}")
        print(f"Portas abertas: {host.get('ports')}\n")

        print("--- Serviços / Banners Encontrados ---")
        for item in host['data']:
            print(f"Porta: {item.get('port')} | Protocolo: {item.get('transport')}")
            product = item.get('product', 'Desconhecido')
            version = item.get('version', '')
            print(f"Serviço: {product} {version}")
            print("-" * 40)

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def buscar_geral():
    query = input("\n[+] Digite a query de busca (ex: port:22 country:BR): ").strip()
    if not query:
        return
    try:
        limite = int(input("[+] Quantos resultados deseja exibir? (padrão 10): ") or 10)
        print(f"\n[*] Pesquisando por '{query}'...\n")
        
        results = api.search(query, limit=limite)
        print(f"[+] Total de resultados encontrados na base: {results['total']}\n")

        for result in results['matches']:
            ip = result.get('ip_str')
            port = result.get('port')
            org = result.get('org', 'N/A')
            location = result.get('location', {})
            country = location.get('country_name', 'N/A')
            
            print(f"IP: {ip}:{port} | Org: {org} | País: {country}")

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")
    except ValueError:
        print("[-] Quantidade inválida.")


def contar_resultados():
    query = input("\n[+] Digite a query para contar ocorrências (ex: product:Apache): ").strip()
    if not query:
        return
    try:
        results = api.count(query)
        print(f"\n[+] Total de dispositivos expostos para '{query}': {results['total']}")
    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def resumo_facetas():
    query = input("\n[+] Digite o termo principal (ex: apache, mikrotik): ").strip()
    if not query:
        return
    
    # Facetas mais comuns para agrupamento de estatísticas
    FACETS = [
        ('country', 'Países Top'),
        ('org', 'Organizações Top'),
        ('port', 'Portas Top'),
        ('domain', 'Domínios Top')
    ]
    
    try:
        print(f"\n[*] Gerando estatísticas de resumo para '{query}'...\n")
        results = api.count(query, facets=FACETS)

        for facet_name, facet_title in FACETS:
            print(f"=== {facet_title} ===")
            if facet_name in results['facets']:
                for item in results['facets'][facet_name]:
                    print(f"  - {item['value']}: {item['count']}")
            print()

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def buscar_exploits():
    query = input("\n[+] Digite o CVE ou serviço para buscar exploits (ex: CVE-2021-44228 ou eternalblue): ").strip()
    if not query:
        return
    try:
        print(f"\n[*] Consultando banco de exploits do Shodan para '{query}'...\n")
        results = api.exploits.search(query)
        
        print(f"[+] Total de exploits encontrados: {results['total']}\n")
        for match in results['matches'][:10]:  # Limita aos 10 primeiros
            source = match.get('source', 'N/A')
            cve = ", ".join(match.get('cve', []))
            summary = match.get('description', 'Sem descrição')
            print(f"Fonte: {source} | CVEs: {cve}")
            print(f"Resumo: {summary[:150]}...")
            print("-" * 50)

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def buscar_screenshots():
    print("\n[*] Filtrando dispositivos que possuem Screenshots capturadas...")
    query = input("[+] Adicione filtros extras se desejar (ou pressione ENTER para tudo): ").strip()
    
    full_query = "has_screenshot:true"
    if query:
        full_query += f" {query}"

    try:
        results = api.search(full_query, limit=5)
        print(f"\n[+] Total de hosts com screenshots encontrados: {results['total']}\n")

        for result in results['matches']:
            ip = result.get('ip_str')
            port = result.get('port')
            org = result.get('org', 'N/A')
            opts = result.get('opts', {})
            screenshot_link = opts.get('screenshot', {}).get('url', 'N/A')

            print(f"IP: {ip}:{port} | Org: {org}")
            print(f"URL/Data da Imagem: {screenshot_link}")
            print("-" * 40)

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def menu():
    while True:
        limpar_tela()
        print("      === CENTRAL DE OPERAÇÕES SHODAN ===")
        print("1. Inspecionar IP específico (Host Lookup)")
        print("2. Buscar Dispositivos (Search Queries)")
        print("3. Contar total de Alvos (Count)")
        print("4. Estatísticas e Resumo por Facetas (Top Countries/Orgs/Ports)")
        print("5. Pesquisar Vulnerabilidades e Exploits (Shodan Exploits)")
        print("6. Listar Hosts com Screenshots Expostas")
        print("0. Sair")
        print("=" * 60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            consultar_ip()
        elif opcao == "2":
            buscar_geral()
        elif opcao == "3":
            contar_resultados()
        elif opcao == "4":
            resumo_facetas()
        elif opcao == "5":
            buscar_exploits()
        elif opcao == "6":
            buscar_screenshots()
        elif opcao == "0":
            print("\n[+] Encerrando aplicação...")
            break
        else:
            print("\n[-] Opção inválida! Tente novamente.")

        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    menu()