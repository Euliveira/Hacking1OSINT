import os
import socket
import urllib.parse
import requests
from bs4 import BeautifulSoup
import pyfiglet

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

texto = "HUNTER INTEL"

banner = pyfiglet.figlet_format(texto)

for linha in banner.split("\n"):
    meio = len(linha) // 2
    direita = linha[meio:]
    esquerda = linha [:meio]

    print(f"{GREEN}{BOLD}{esquerda}{direita}{RESET}")

banner_sub = pyfiglet.figlet_format("OSINT")

print(f"{RED}{BOLD}{banner_sub}{RESET}")

# Cabeçalho para simular um navegador comum e evitar bloqueio
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def rastrear_url_final(url_inicial):
    """
    Siga redirecionamentos HTTP e metatags de redirecionamento em HTML
    para encontrar o destino final real sem precisar da API oficial.
    """
    if not url_inicial.startswith(('http://', 'https://')):
        url_inicial = 'https://' + url_inicial

    session = requests.Session()
    session.headers.update(HEADERS)

    print(f"[*] Rastreando redirecionamentos a partir de: {url_inicial}")
    
    try:
        # Segue redirecionamentos HTTP (301, 302, 307)
        response = session.get(url_inicial, allow_redirects=True, timeout=10)
        url_atual = response.url

        # Verifica se há redirecionamento via HTML Meta Refresh ou JavaScript
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_refresh = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'})
        
        if meta_refresh and 'content' in meta_refresh.attrs:
            content = meta_refresh['content']
            if 'url=' in content.lower():
                url_meta = content.lower().split('url=')[1].strip('\'"')
                url_atual = urllib.parse.urljoin(url_atual, url_meta)
                # Faz uma última requisição para confirmar a URL final
                res_final = session.get(url_atual, allow_redirects=True, timeout=10)
                url_atual = res_final.url

        print(f"[+] URL final de destino localizada: {url_atual}")
        return url_atual

    except Exception as e:
        print(f"[-] Erro ao rastrear a URL: {e}")
        return url_inicial

def extrair_partes_url(url_alvo):
    parsed = urllib.parse.urlparse(url_alvo)
    hostname = parsed.hostname or url_alvo
    parts = hostname.split('.')
    
    if len(parts) >= 2:
        domain = ".".join(parts[-2:])
        subdomain = ".".join(parts[:-2]) if len(parts) > 2 else "Nenhum"
    else:
        domain = hostname
        subdomain = "Nenhum"
        
    return hostname, domain, subdomain

def obter_ip_e_geo(hostname):
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        return "Indisponível", None, None

    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", headers=HEADERS, timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            return ip, data.get("lat"), data.get("lon")
    except Exception:
        pass
        
    return ip, None, None

def obter_whois_rdap(domain):
    try:
        resp = requests.get(f"https://rdap.org/domain/{domain}", headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            status = ", ".join(data.get("status", []))
            handle = data.get("handle", "N/A")
            return f"RDAP Handle: {handle}\nStatus: {status}"
    except Exception:
        pass
    return f"Consulta via API limitada. Verifique diretamente em: https://whois.domaintools.com/{domain}"

def gerar_relatorio_html(url_original, url_final, domain, subdomain, ip, lat, lon, whois_info):
    map_html = ""
    if lat and lon:
        map_html = f'''
        <div id="mapArea">
            <iframe src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05}%2C{lat-0.05}%2C{lon+0.05}%2C{lat+0.05}&layer=mapnik&marker={lat}%2C{lon}"></iframe>
            <p style="color:#ffffff;">Coordenadas Aproximadas (ISP): Lat {lat}, Lon {lon}</p>
        </div>
        '''
    else:
        map_html = '<p style="color:#ffffff;">Geolocalização não disponível para este IP.</p>'

    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Hunter Intel Engenharia Reversa</title>
  <style>
    body {{
      background-color: #000000;
      color: #ffffff;
      font-family: Arial, sans-serif;
      font-size: 14px;
      margin: 30px;
    }}
    h1 {{
      font-size: 18px;
      color: #00ff66;
      text-shadow: 0 0 10px #00ff66;
      margin-bottom: 25px;
    }}
    .item-row {{
      margin: 15px 0;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .label {{
      font-weight: bold;
      min-width: 140px;
    }}
    .btn-neon {{
      background-color: #0088ff;
      color: #ffffff;
      border: none;
      padding: 8px 16px;
      font-size: 14px;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
      box-shadow: 0 0 10px #0088ff;
      transition: 0.2s;
      text-decoration: none;
      display: inline-block;
    }}
    .btn-neon:hover {{
      box-shadow: 0 0 18px #00aaff;
      background-color: #00aaff;
    }}
    .box-container {{
      margin-top: 20px;
      display: none;
      border: 1px solid #0088ff;
      box-shadow: 0 0 10px #0088ff;
      padding: 15px;
      background: #050505;
    }}
    iframe {{
      width: 100%;
      height: 380px;
      border: none;
    }}
    pre {{
      white-space: pre-wrap;
      word-wrap: break-word;
      color: #00ff66;
    }}
  </style>
</head>
<body>

  <h1>Hunter Intel Engenharia Reversa</h1>

  <div class="item-row">
    <span class="label">URL do Instagram:</span>
    <span>{url_original}</span>
  </div>

  <div class="item-row">
    <span class="label">Destino Final:</span>
    <span>{url_final}</span>
  </div>

  <div class="item-row">
    <span class="label">Domínio:</span>
    <span>{domain}</span>
    <button class="btn-neon" onclick="toggleBox('whoisContainer')">WHOIS</button>
  </div>

  <div class="item-row">
    <span class="label">Subdomínio:</span>
    <span>{subdomain}</span>
  </div>

  <div class="item-row">
    <span class="label">IP do Servidor:</span>
    <button class="btn-neon" onclick="toggleBox('mapContainer')">{ip}</button>
  </div>

  <div id="mapContainer" class="box-container">
    <p style="color:#00ff66; font-weight:bold;">Mapa do IP Logger (Localidade do Servidor/Atacante):</p>
    {map_html}
  </div>

  <div id="whoisContainer" class="box-container">
    <p style="color:#00ff66; font-weight:bold;">Detalhes do Domínio no WHOIS:</p>
    <pre>{whois_info}</pre>
  </div>

  <script>
    function toggleBox(id) {{
      var el = document.getElementById(id);
      if (el.style.display === "block") {{
        el.style.display = "none";
      }} else {{
        el.style.display = "block";
      }}
    }}
  </script>
</body>
</html>
'''
    filename = "relatorio_hunter_intel_ig.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n[+] Relatório gerado com sucesso: {filename}")

def main():
    print("=== Hunter Intel - Engenharia Reversa de Links (Sem API) ===")
    url_input = input("\nCole o link do Instagram / Encurtador / Perfil: ").strip()
    
    if not url_input:
        print("[-] Nenhuma URL inserida.")
        return

    url_final = rastrear_url_final(url_input)
    
    print("[*] Extraindo dados de infraestrutura do destino...")
    hostname, domain, subdomain = extrair_partes_url(url_final)
    ip, lat, lon = obter_ip_e_geo(hostname)
    whois_info = obter_whois_rdap(domain)

    gerar_relatorio_html(url_input, url_final, domain, subdomain, ip, lat, lon, whois_info)

if __name__ == "__main__":
    main()
