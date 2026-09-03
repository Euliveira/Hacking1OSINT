import re
import requests
import webbrowser
import os
import ipaddress

class RastreadorOrigemDigital:
    """
    Classe para engenharia reversa de cabeçalhos de e-mail e links de SMS
    com foco em extração de IP, geolocalização e mapeamento visual da infraestrutura,
    incorporando filtros para ignorar o próprio IP do investigador.
    """

    def __init__(self):
        self.headers_requisicao = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PericiaDigital/1.0'
        }
        # Detecta automaticamente o IP público do computador que está executando o script
        self.meu_ip_publico = self._obter_meu_ip_publico()

    def _obter_meu_ip_publico(self) -> str:
        """
        Consulta um serviço externo seguro para descobrir o IP público do próprio investigador.
        """
        try:
            res = requests.get("https://api.ipify.org?format=json", timeout=5)
            if res.status_code == 200:
                return res.json().get("ip")
        except Exception:
            pass
        return None

    def ip_eh_valido_e_externo(self, ip_str: str) -> bool:
        """
        Valida se o IP extraído é público e garante que NÃO seja o IP do próprio computador/perito.
        """
        try:
            ip_obj = ipaddress.ip_address(ip_str)

            # 1. Ignora redes privadas, loopback (127.0.0.1), link-local e multicast
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                return False

            # 2. Ignora explicitamente o próprio IP público do investigador
            if self.meu_ip_publico and ip_str == self.meu_ip_publico:
                return False

            return True
        except ValueError:
            return False

    def extrair_ips_cabecalho_email(self, cabecalho_bruto: str) -> list:
        """
        Analisa o cabeçalho do e-mail e extrai todos os IPs públicos presentes nos campos Received,
        descartando o IP do próprio investigador e redes internas.
        """
        padrao_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        linhas_received = [linha for linha in cabecalho_bruto.split('\n') if 'received:' in linha.lower()]
        ips_encontrados = []

        for linha in linhas_received:
            ips = re.findall(padrao_ip, linha)
            for ip in ips:
                if self.ip_eh_valido_e_externo(ip):
                    if ip not in ips_encontrados:
                        ips_encontrados.append(ip)

        return ips_encontrados

    def desenrolar_link_sms(self, url_curta: str) -> dict:
        """
        Faz a engenharia reversa do link do SMS, desfazendo encurtadores
        e identificando o domínio/IP final da infraestrutura hospedeira.
        """
        if not url_curta.startswith(('http://', 'https://')):
            url_curta = 'http://' + url_curta

        try:
            resposta = requests.head(url_curta, allow_redirects=True, timeout=10, headers=self.headers_requisicao)
            url_final = resposta.url
            dominio = url_final.split('/')[2]
            
            # Resolve o domínio para IP através da API DNS do Google
            ip_servidor = requests.get(f"https://dns.google/resolve?name={dominio}").json()['Answer'][0]['data']

            # Checa se por algum motivo o IP retornado não é o próprio IP local/investigador
            if not self.ip_eh_valido_e_externo(ip_servidor):
                return {"erro": "O IP resolvido do servidor pertence a uma rede interna ou corresponde ao seu próprio IP."}

            return {
                "url_inicial": url_curta,
                "url_destino_real": url_final,
                "dominio_final": dominio,
                "ip_servidor": ip_servidor,
                "status_http": resposta.status_code
            }
        except Exception as e:
            return {"erro": f"Falha ao rastrear URL do SMS: {str(e)}"}

    def geolocalizar_ip(self, ip: str) -> dict:
        """
        Consulta serviços públicos de geolocalização de IP para determinar
        país, estado, cidade, provedor (ISP) e gera os links para visualização em mapa.
        """
        try:
            url_api = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query"
            resposta = requests.get(url_api, timeout=10)
            dados = resposta.json()

            if dados.get("status") == "success":
                lat = dados.get("lat")
                lon = dados.get("lon")
                
                mapa_gmaps = f"https://www.google.com/maps?q={lat},{lon}"
                mapa_osm = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=13/{lat}/{lon}"

                return {
                    "ip": dados.get("query"),
                    "pais": dados.get("country"),
                    "estado": dados.get("regionName"),
                    "cidade": dados.get("city"),
                    "latitude": lat,
                    "longitude": lon,
                    "provedor_isp": dados.get("isp"),
                    "organizacao": dados.get("org"),
                    "link_google_maps": mapa_gmaps,
                    "link_openstreetmap": mapa_osm
                }
            else:
                return {"erro": dados.get("message", "IP não localizado")}
        except Exception as e:
            return {"erro": f"Erro na consulta de geolocalização: {str(e)}"}

    def gerar_mapa_html_interativo(self, dados_geo: dict, tipo_analise: str, detalhes_extras: dict = None, nome_arquivo="mapa_investigacao.html"):
        """
        Gera um relatório HTML contendo o mapa interativo e a ficha técnica completa da investigação.
        """
        lat = dados_geo.get("latitude")
        lon = dados_geo.get("longitude")
        ip = dados_geo.get("ip")
        cidade = dados_geo.get("cidade")
        estado = dados_geo.get("estado")
        pais = dados_geo.get("pais")
        isp = dados_geo.get("provedor_isp")
        org = dados_geo.get("organizacao")
        gmaps = dados_geo.get("link_google_maps")
        osm = dados_geo.get("link_openstreetmap")

        html_detalhes_extras = ""
        if tipo_analise == "SMS" and detalhes_extras:
            html_detalhes_extras = f"""
            <div class="info-block">
                <span class="label">URL Curta Recebida:</span> <span class="value">{detalhes_extras.get('url_inicial')}</span><br>
                <span class="label">URL Destino Real:</span> <span class="value highlight">{detalhes_extras.get('url_destino_real')}</span><br>
                <span class="label">Domínio Hospedeiro:</span> <span class="value">{detalhes_extras.get('dominio_final')}</span> | 
                <span class="label">Status HTTP:</span> <span class="value">{detalhes_extras.get('status_http')}</span>
            </div>
            """
        elif tipo_analise == "E-MAIL" and detalhes_extras:
            ips_cadeia = ", ".join(detalhes_extras.get('ips_encontrados', []))
            html_detalhes_extras = f"""
            <div class="info-block">
                <span class="label">Cadeia de IPs de Terceiros no Cabeçalho:</span> <span class="value">{ips_cadeia}</span><br>
                <span class="label">IP do Remetente Inicial (Analisado):</span> <span class="value highlight">{ip}</span>
            </div>
            """

        html_conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <title>Relatório Pericial OSINT: IP {ip}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; }}
        #map {{ height: 65vh; width: 100%; border-top: 1px solid #334155; }}
        .header {{ padding: 20px 25px; background-color: #1e293b; border-bottom: 3px solid #38bdf8; }}
        .header h2 {{ margin: 0 0 10px 0; color: #38bdf8; font-size: 22px; display: flex; align-items: center; gap: 10px; }}
        .badge {{ background-color: #0284c7; color: #fff; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .grid-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 15px; }}
        .info-card {{ background-color: #0f172a; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; }}
        .label {{ color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 3px; }}
        .value {{ color: #e2e8f0; font-size: 14px; font-weight: 500; word-break: break-all; }}
        .highlight {{ color: #38bdf8; font-weight: bold; }}
        .info-block {{ background-color: #0f172a; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px; font-size: 14px; }}
        .actions {{ margin-top: 10px; }}
        .btn-link {{
            display: inline-block;
            padding: 9px 16px;
            margin-right: 10px;
            background-color: #0284c7;
            color: #ffffff;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: bold;
            transition: background-color 0.2s;
        }}
        .btn-link:hover {{ background-color: #0369a1; }}
        .btn-osm {{ background-color: #334155; }}
        .btn-osm:hover {{ background-color: #475569; }}
        .leaflet-popup-content {{ color: #0f172a; font-size: 13px; line-height: 1.5; }}
        .leaflet-popup-content a {{ color: #0284c7; font-weight: bold; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🔍 RELATÓRIO PERICIAL DE INTELIGÊNCIA DIGITAL <span class="badge">ANÁLISE DE {tipo_analise}</span></h2>
        
        <div class="grid-info">
            <div class="info-card">
                <span class="label">Endereço IP Investigado</span>
                <span class="value highlight">{ip}</span>
            </div>
            <div class="info-card">
                <span class="label">Localização Estimada</span>
                <span class="value">{cidade} - {estado}, {pais}</span>
            </div>
            <div class="info-card">
                <span class="label">Provedor / Organização (ISP)</span>
                <span class="value">{isp} ({org})</span>
            </div>
            <div class="info-card">
                <span class="label">Coordenadas Geográficas</span>
                <span class="value">{lat}, {lon}</span>
            </div>
        </div>

        {html_detalhes_extras}

        <div class="actions">
            <a href="{gmaps}" target="_blank" class="btn-link">📍 Abrir no Google Maps</a>
            <a href="{osm}" target="_blank" class="btn-link btn-osm">🗺️ Abrir no OpenStreetMap</a>
        </div>
    </div>

    <div id="map"></div>

    <script>
        var map = L.map('map').setView([{lat}, {lon}], 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: 'Perícia Digital & OSINT'
        }}).addTo(map);

        var marker = L.marker([{lat}, {lon}]).addTo(map);
        var popupText = "<b>IP Investigado: {ip}</b><br>" +
                        "Tipo: {tipo_analise}<br>" +
                        "Localização: {cidade}, {pais}<br>" +
                        "Provedor: {isp}<br><br>" +
                        "<a href='{gmaps}' target='_blank'>📍 Ver no Google Maps</a>";
        marker.bindPopup(popupText).openPopup();
    </script>
</body>
</html>
"""
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html_conteudo)
        
        return os.path.abspath(nome_arquivo)


# --- INTERFACE INTERATIVA (INPUT DO ALUNO) ---
if __name__ == "__main__":
    rastreador = RastreadorOrigemDigital()

    print("=" * 65)
    print("  LABORATÓRIO DE ENGENHARIA REVERSA: RASTREAMENTO DE E-MAIL E SMS")
    print("=" * 65)
    
    if rastreador.meu_ip_publico:
        print(f"[🛡️ OPSEC ATIVA] Seu IP Público ({rastreador.meu_ip_publico}) foi ignorado nos filtros.")
    else:
        print("[!] Aviso: Não foi possível determinar o seu IP público para autofiltragem.")

    print("\nEscolha a opção para iniciar a investigação:")
    print(" [1] Rastrear origem real de um E-MAIL (via Cabeçalho Bruto)")
    print(" [2] Rastrear destino real de um SMS (via Link Suspeito)")

    opcao = input("\nDigite a opção desejada (1 ou 2): ").strip()

    geo_resultado = None
    tipo_analise = ""
    detalhes_extras = {}

    if opcao == "1":
        tipo_analise = "E-MAIL"
        print("\n[+] Cole abaixo o CABEÇALHO BRUTO do e-mail (Pressione Enter e finalize com 'FIM'):")
        linhas = []
        while True:
            linha = input()
            if linha.strip() == "FIM":
                break
            linhas.append(linha)
        
        cabecalho_input = "\n".join(linhas)
        ips = rastreador.extrair_ips_cabecalho_email(cabecalho_input)

        print("\n" + "-" * 50)
        print("RESULTADO DA ENGENHARIA REVERSA DO E-MAIL:")
        if ips:
            print(f"[!] IPs de Origem/Passagem de Terceiros Identificados: {ips}")
            ip_origem = ips[-1]  # O último IP externo costuma ser o servidor SMTP remetente
            print(f"[*] Analisando IP de Origem do Remetente: {ip_origem}\n")
            geo_resultado = rastreador.geolocalizar_ip(ip_origem)
            detalhes_extras = {"ips_encontrados": ips}
        else:
            print("[-] Nenhum IP público de terceiros foi encontrado nos campos Received.")

    elif opcao == "2":
        tipo_analise = "SMS"
        url_input = input("\n[+] Digite o link/URL recebido no SMS (ex: bit.ly/3xXyZ): ").strip()
        print("\n" + "-" * 50)
        print("RESULTADO DA DESMONTAGEM DO LINK DE SMS:")
        
        resultado_sms = rastreador.desenrolar_link_sms(url_input)
        
        if "erro" not in resultado_sms:
            print(f"[!] URL Final Redirecionada: {resultado_sms['url_destino_real']}")
            print(f"[!] Domínio do Servidor: {resultado_sms['dominio_final']}")
            print(f"[!] IP do Servidor Hospedeiro: {resultado_sms['ip_servidor']}")
            
            print("\n[*] Localizando a infraestrutura do servidor hospedeiro...\n")
            geo_resultado = rastreador.geolocalizar_ip(resultado_sms['ip_servidor'])
            detalhes_extras = resultado_sms
        else:
            print(f"[-] Erro: {resultado_sms['erro']}")

    else:
        print("\n[-] Opção inválida. Reinicie o programa.")

    # Exibição dos dados geográficos e geração de mapas
    if geo_resultado and "erro" not in geo_resultado:
        print("┌" + "─" * 58 + "┐")
        print("│ DADOS DE INTELIGÊNCIA GEOGRÁFICA DA INFRAESTRUTURA       │")
        print("├" + "─" * 58 + "┤")
        print(f"│ IP Extraído:     {geo_resultado['ip']}")
        print(f"│ Localização:    {geo_resultado['cidade']} - {geo_resultado['estado']}, {geo_resultado['pais']}")
        print(f"│ Coordenadas:    {geo_resultado['latitude']}, {geo_resultado['longitude']}")
        print(f"│ Provedor / ISP: {geo_resultado['provedor_isp']}")
        print("├" + "─" * 58 + "┤")
        print("│ MAPAS PARA INVESTIGAÇÃO VISUAL:                         │")
        print(f"│ 📍 Google Maps:   {geo_resultado['link_google_maps']}")
        print(f"│ 🗺️ OpenStreetMap: {geo_resultado['link_openstreetmap']}")
        print("└" + "─" * 58 + "┘")

        # Pergunta ao aluno se ele quer abrir o mapa no navegador
        abrir_mapa = input("\n[?] Deseja gerar e abrir o MAPA INTERATIVO no navegador? (s/n): ").strip().lower()
        if abrir_mapa == 's':
            caminho_mapa = rastreador.gerar_mapa_html_interativo(geo_resultado, tipo_analise, detalhes_extras)
            print(f"\n[+] Relatório HTML gerado com sucesso em: {caminho_mapa}")
            webbrowser.open('file://' + caminho_mapa)
    elif geo_resultado and "erro" in geo_resultado:
        print(f"[-] Erro ao geolocalizar IP: {geo_resultado['erro']}")