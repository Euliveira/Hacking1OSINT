import socket
from urllib.parse import quote, urlparse
import requests


def analisar_link(url_encurtada):
    print(f'[*] Realizando engenharia reversa na URL: {url_encurtada}')
    try:
        # Resolve os redirecionamentos do link encurtado
        resposta = requests.get(url_encurtada, allow_redirects=True, timeout=10)
        url_final = resposta.url
    except Exception as e:
        print(f'[-] Erro ao resolver o link: {e}')
        url_final = url_encurtada

    parsed_url = urlparse(url_final)
    dominio = parsed_url.netloc

    # Obtém o endereço IP do servidor de destino para geolocalização aproximada
    try:
        ip_destino = socket.gethostbyname(dominio)
    except socket.gaierror:
        ip_destino = 'IP não resolvido'

    # Consulta opcional de geolocalização por IP (ex: ip-api.com gratuito) para precisão no mapa de IP Logger
    lat, lon = None, None
    if ip_destino != 'IP não resolvido':
        try:
            geo_resp = requests.get(f'http://ip-api.com/json/{ip_destino}', timeout=5).json()
            if geo_resp.get('status') == 'success':
                lat = geo_resp.get('lat')
                lon = geo_resp.get('lon')
        except Exception:
            pass

    # Heurística básica de autenticidade (Pode ser integrada a APIs de Threat Intelligence)
    termos_suspeitos = [
        'phish',
        'login',
        'verify',
        'secure',
        'update',
        'banco',
        'free',
    ]
    autentico = not any(termo in url_final.lower() for termo in termos_suspeitos)

    # Links de redirecionamento para os botões (Mapa atualizado para coordenadas reais ou consulta por IP)
    vt_link = f'https://www.virustotal.com/gui/search/{quote(url_final)}'
    if lat and lon:
        mapa_link = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
    else:
        mapa_link = f'https://www.google.com/maps/search/?api=1&query={ip_destino}'

    dados = {
        'url_original': url_encurtada,
        'url_escondida': url_final,
        'dominio': dominio,
        'ip': ip_destino,
        'autentico': autentico,
        'vt_link': vt_link,
        'mapa_link': mapa_link,
    }

    gerar_relatorio_html(dados)


def gerar_relatorio_html(dados):
    status_texto = (
        'VERDADEIRO / SEGURO (Sem indícios óbvios de fraude)'
        if dados['autentico']
        else 'FALSO / SUSPEITO (Possível Phishing / Malicioso)'
    )
    status_classe = 'status-seguro' if dados['autentico'] else 'status-perigo'

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hunter Intel - Relatório de Engenharia Reversa</title>
    <style>
        body {{
            background-color: #030303;
            color: #00ff66;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #00ff66;
            width: 100%;
            max-width: 800px;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #00ff66;
            text-shadow: 0 0 10px #00ff66, 0 0 20px #00ff66, 0 0 30px #00ff66;
            font-size: 2.2em;
            margin: 0;
            letter-spacing: 2px;
        }}
        .container {{
            background: rgba(0, 15, 8, 0.9);
            border: 1px solid #00ff66;
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
            padding: 35px;
            border-radius: 6px;
            width: 100%;
            max-width: 800px;
            box-sizing: border-box;
        }}
        .info-group {{
            margin-bottom: 25px;
        }}
        .label {{
            font-weight: bold;
            color: #00cc55;
            font-size: 0.95em;
            text-transform: uppercase;
        }}
        .value {{
            color: #ffffff;
            word-break: break-all;
            background: rgba(0, 255, 102, 0.05);
            padding: 8px 12px;
            border-left: 3px solid #00ff66;
            margin-top: 5px;
            display: block;
            font-size: 1.05em;
        }}
        .status-seguro {{
            color: #00ff66;
            font-weight: bold;
            text-shadow: 0 0 8px #00ff66;
        }}
        .status-perigo {{
            color: #ff2222;
            font-weight: bold;
            text-shadow: 0 0 8px #ff2222;
        }}
        .button-container {{
            display: flex;
            justify-content: space-between;
            margin-top: 35px;
            gap: 20px;
        }}
        .cyber-btn {{
            flex: 1;
            background: transparent;
            border: 2px solid #00ff66;
            color: #00ff66;
            padding: 14px 20px;
            text-align: center;
            text-decoration: none;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            border-radius: 4px;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 255, 102, 0.2);
            cursor: pointer;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        .cyber-btn:hover {{
            background: #00ff66;
            color: #030303;
            box-shadow: 0 0 25px #00ff66;
        }}
        .map-btn {{
            border-color: #00e1ff;
            color: #00e1ff;
            box-shadow: 0 0 10px rgba(0, 225, 255, 0.2);
        }}
        .map-btn:hover {{
            background: #00e1ff;
            color: #030303;
            box-shadow: 0 0 25px #00e1ff;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Hunter Intel - Willoliveiradev</h1>
    </div>
    
    <div class="container">
        <div class="info-group">
            <span class="label">[+] URL SMS Encurtada (Entrada):</span>
            <span class="value">{dados['url_original']}</span>
        </div>
        
        <div class="info-group">
            <span class="label">[+] Página Oculta Revelada (Destino Final):</span>
            <span class="value">{dados['url_escondida']}</span>
        </div>
        
        <div class="info-group">
            <span class="label">[+] Host / IP do Alvo:</span>
            <span class="value">{dados['dominio']} ({dados['ip']})</span>
        </div>
        
        <div class="info-group">
            <span class="label">[+] Veredito de Autenticidade:</span>
            <span class="value {status_classe}">{status_texto}</span>
        </div>
        
        <div class="button-container">
            <a href="{dados['vt_link']}" target="_blank" class="cyber-btn">Consultar VirusTotal</a>
            <a href="{dados['mapa_link']}" target="_blank" class="cyber-btn map-btn">Localização do Servidor (Mapa)</a>
        </div>
    </div>
</body>
</html>
"""

    with open('relatorio_hunter_intel.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(
        '[+] Relatório gerado com sucesso: '
        '\033[92mrelatorio_hunter_intel.html\033[0m'
    )


if __name__ == '__main__':
    url_entrada = input(
        'Insira a URL encurtada recebida via SMS para engenharia reversa: '
    )
    analisar_link(url_entrada)