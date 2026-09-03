import sys
import numpy as np
import shodan
from sklearn.ensemble import RandomForestClassifier

# Sua chave API do Shodan
API_KEY = "i3gwQyJmXNX02q5ddFxYeJvycvK146KY"

# Inicialização da API do Shodan
try:
    api = shodan.Shodan(API_KEY)
except Exception as e:
    print(f"[-] Erro ao inicializar a API do Shodan: {e}")
    sys.exit(1)


# ==============================================================================
# MOTOR DE MACHINE LEARNING (scikit-learn)
# ==============================================================================
def treinar_modelo_ml():
    """
    Treina um modelo RandomForest com um dataset sintético de heurísticas de segurança.
    Features de Entrada:
      [0] Possui RDP (3389) ou VNC (5900)
      [1] Possui SMB (445) ou FTP (21) ou Telnet (23)
      [2] Possui Banco de Dados Exposto (MongoDB, Redis, MySQL, Postgres, Elastic)
      [3] Possui mais de 5 portas abertas
      [4] Possui CVE/Vulnerabilidade registrada no banner
    Rótulos (Target):
      0: Baixo Risco | 1: Médio Risco | 2: Alto Risco | 3: Risco Crítico
    """
    X_train = np.array([
        # [RDP/VNC, SMB/FTP/Telnet, DB_Exposto, >5_Portas, Tem_CVE]
        [0, 0, 0, 0, 0],  # Baixo Risco (ex: apenas web HTTP/HTTPS)
        [0, 1, 0, 0, 0],  # Médio Risco (ex: FTP/Telnet aberto)
        [1, 0, 0, 0, 0],  # Médio Risco (ex: RDP exposto sem CVE)
        [0, 0, 1, 0, 0],  # Alto Risco (ex: Banco de Dados exposto)
        [1, 1, 0, 1, 0],  # Alto Risco (Múltiplos serviços críticos)
        [1, 1, 1, 1, 0],  # Risco Crítico (Infraestrutura altamente exposta)
        [0, 0, 0, 0, 1],  # Risco Crítico (Presença de CVE direta)
        [1, 0, 1, 0, 1],  # Risco Crítico (DB + RDP + CVE)
    ])
    
    y_train = np.array([0, 1, 1, 2, 2, 3, 3, 3])

    clf = RandomForestClassifier(n_estimators=15, random_state=42)
    clf.fit(X_train, y_train)
    return clf


# Inicializa e treina o modelo de ML na memória (Instantâneo / Levíssimo)
modelo_risco = treinar_modelo_ml()
MAPA_RISCO = {
    0: "\033[92m[BAIXO RISCO]\033[0m",
    1: "\033[93m[MÉDIO RISCO]\033[0m",
    2: "\033[91m[ALTO RISCO]\033[0m",
    3: "\033[95m[RISCO CRÍTICO]\033[0m"
}


def extrair_features(host_data):
    """
    Vetoriza os dados brutos do Shodan para o formato que o scikit-learn entende.
    """
    ports = host_data.get('ports', [])
    vulns = host_data.get('vulns', [])
    
    rdp_vnc = 1 if any(p in ports for p in [3389, 5900]) else 0
    smb_ftp_telnet = 1 if any(p in ports for p in [21, 23, 445]) else 0
    db_exposto = 1 if any(p in ports for p in [27017, 6379, 3306, 5432, 9200]) else 0
    muitas_portas = 1 if len(ports) > 5 else 0
    tem_cve = 1 if len(vulns) > 0 else 0
    
    return np.array([[rdp_vnc, smb_ftp_telnet, db_exposto, muitas_portas, tem_cve]])


# ==============================================================================
# FUNÇÕES DO MENU E INTEGRAÇÃO SHODAN
# ==============================================================================
def limpar_tela():
    print("\n" + "=" * 65 + "\n")


def consultar_ip_com_ml():
    ip = input("\n[+] Digite o endereço IP do alvo: ").strip()
    if not ip:
        return
    try:
        print(f"\n[*] Consultando informações e executando análise ML para {ip}...\n")
        host = api.host(ip)

        # 1. Análise pelo Modelo do scikit-learn
        features = extrair_features(host)
        classe_risco = modelo_risco.predict(features)[0]
        probabilidades = modelo_risco.predict_proba(features)[0]
        confianca = probabilidades[classe_risco] * 100

        # 2. Exibição dos Dados do Host
        print(f"IP: {host.get('ip_str')}")
        print(f"Organização: {host.get('org', 'N/A')}")
        print(f"Provedor (ISP): {host.get('isp', 'N/A')}")
        print(f"País/Cidade: {host.get('country_name', 'N/A')} - {host.get('city', 'N/A')}")
        print(f"Sistema Operacional: {host.get('os', 'N/A')}")
        print(f"Portas Abertas: {host.get('ports')}")
        
        cves = list(host.get('vulns', {}).keys())
        if cves:
            print(f"Vulnerabilidades (CVEs): {', '.join(cves[:5])} (Total: {len(cves)})")
        else:
            print("Vulnerabilidades (CVEs): Nenhuma CVE mapeada no banner.")

        print("\n" + "-" * 40)
        print(">>> AVALIAÇÃO DE RISCO VIA MACHINE LEARNING (scikit-learn) <<<")
        print(f" Classificação: {MAPA_RISCO[classe_risco]}")
        print(f" Grau de Confiança do Modelo: {confianca:.1f}%")
        print("-" * 40 + "\n")

        # 3. Lista de Banners
        print("--- Detalhes dos Serviços Expostos ---")
        for item in host['data']:
            product = item.get('product', 'Serviço Não Identificado')
            version = item.get('version', '')
            print(f"Porta: {item.get('port')}/{item.get('transport')} | {product} {version}")

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def buscar_geral_com_classificacao():
    query = input("\n[+] Digite a query de busca (ex: port:22 country:BR): ").strip()
    if not query:
        return
    try:
        limite = int(input("[+] Quantos resultados deseja analisar? (padrão 5): ") or 5)
        print(f"\n[*] Pesquisando por '{query}' e aplicando classificação em lote...\n")
        
        results = api.search(query, limit=limite)
        print(f"[+] Total de resultados encontrados na base: {results['total']}\n")

        for idx, result in enumerate(results['matches'], start=1):
            ip = result.get('ip_str')
            port = result.get('port')
            org = result.get('org', 'N/A')
            
            # Simulando extração rápida para lote
            ports = [port]
            features_lote = np.array([[
                1 if port in [3389, 5900] else 0,
                1 if port in [21, 23, 445] else 0,
                1 if port in [27017, 6379, 3306, 5432, 9200] else 0,
                0, 0
            ]])
            
            risco = modelo_risco.predict(features_lote)[0]
            print(f"{idx}. IP: {ip}:{port} | Org: {org} | Avaliação ML: {MAPA_RISCO[risco]}")

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
    query = input("\n[+] Digite o termo principal para estatísticas (ex: mikrotik): ").strip()
    if not query:
        return
    
    FACETS = [('country', 'Países Top'), ('org', 'Organizações Top'), ('port', 'Portas Top')]
    
    try:
        print(f"\n[*] Gerando resumo estatístico para '{query}'...\n")
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
    query = input("\n[+] Digite a vulnerabilidade ou serviço (ex: CVE-2021-44228): ").strip()
    if not query:
        return
    try:
        print(f"\n[*] Consultando banco de exploits para '{query}'...\n")
        results = api.exploits.search(query)
        
        print(f"[+] Total de exploits encontrados: {results['total']}\n")
        for match in results['matches'][:5]:
            source = match.get('source', 'N/A')
            cve = ", ".join(match.get('cve', []))
            summary = match.get('description', 'Sem descrição')
            print(f"Fonte: {source} | CVEs: {cve}")
            print(f"Resumo: {summary[:150]}...")
            print("-" * 50)

    except shodan.APIError as e:
        print(f"[-] Erro na API do Shodan: {e}")


def menu():
    while True:
        limpar_tela()
        print("      === CENTRAL OSINT: SHODAN + SCIKIT-LEARN (ML) ===")
        print("1. Inspecionar IP + Classificação Automática de Risco (ML)")
        print("2. Buscar Dispositivos com Triagem por Risco (Search + ML)")
        print("3. Contar total de Alvos (Count)")
        print("4. Estatísticas e Resumo por Facetas (Top Countries/Orgs/Ports)")
        print("5. Pesquisar Vulnerabilidades e Exploits (Shodan Exploits)")
        print("0. Sair")
        print("=" * 65)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            consultar_ip_com_ml()
        elif opcao == "2":
            buscar_geral_com_classificacao()
        elif opcao == "3":
            contar_resultados()
        elif opcao == "4":
            resumo_facetas()
        elif opcao == "5":
            buscar_exploits()
        elif opcao == "0":
            print("\n[+] Encerrando aplicação...")
            break
        else:
            print("\n[-] Opção inválida! Tente novamente.")

        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    menu()