import os
import re
import sys
import base64
import requests
from datetime import datetime

def limpar_tela():
    os.system('clear' if os.name == 'posix' else 'cls')

# =====================================================================
# ENGENHARIA REVERSA & ANÁLISE DE USER ID / PLATAFORMA
# =====================================================================

def analisar_user_id(user_id_str):
    """Extrai informações técnicas, estimativas e links de busca pelo User ID."""
    if not user_id_str or not user_id_str.isdigit():
        return {
            "id_num": "Não Informado / Inválido",
            "estimativa": "N/A",
            "link_protocolo": "#",
            "hex_id": "N/A"
        }
    
    uid = int(user_id_str)
    
    # Estimativa de janela temporal baseada na sequência de alocação de IDs do Telegram
    if uid < 100000000:
        janela = "2013 - 2015 (Conta legada / Antiga)"
    elif uid < 500000000:
        janela = "2016 - 2017"
    elif uid < 1000000000:
        janela = "2018 - 2019"
    elif uid < 2000000000:
        janela = "2020 - 2022"
    elif uid < 6000000000:
        janela = "2023 - 2024"
    else:
        janela = "2025 - 2026 (Conta Recente / Alta volatilidade)"
        
    return {
        "id_num": str(uid),
        "estimativa": janela,
        "link_protocolo": f"tg://user?id={uid}",
        "hex_id": hex(uid).upper()
    }

def gerar_links_osint_id(user_id_str):
    """Gera links de pesquisa focados em rastrear o ID numérico em fontes externas e bots de histórico."""
    if not user_id_str or not user_id_str.isdigit():
        return {}
    
    uid = user_id_str.strip()
    return {
        "google_id": f"https://www.google.com/search?q=%22{uid}%22",
        "telegram_dork_id": f"https://www.google.com/search?q=site:t.me+%22{uid}%22",
        "sangmata_bot": f"https://t.me/SangMataInfo_bot?start={uid}",
        "userinfo_bot": f"https://t.me/userinfobot"
    }

def checar_status_plataforma(username):
    """Consulta os servidores web do Telegram para checar status e metadados (se username for fornecido)."""
    user_clean = username.replace("@", "").strip() if username else ""
    if not user_clean:
        return "N/A (Consulta via User ID)", "N/A", "N/A"
        
    url = f"https://t.me/{user_clean}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    status = "INATIVO OU PRIVADO"
    nome = "N/A"
    bio = "N/A"
    
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            html = r.text
            if "tgme_page_title" in html:
                status = "ATIVO / ONLINE"
                
                nome_match = re.search(r'<div class="tgme_page_title"[^>]*><span[^>]*>(.*?)</span></div>', html)
                if nome_match:
                    nome = nome_match.group(1).strip()
                    
                bio_match = re.search(r'<div class="tgme_page_description"[^>]*>(.*?)</div>', html)
                if bio_match:
                    bio = bio_match.group(1).replace('<br>', ' ').strip()
    except Exception:
        status = "ERRO NA CONSULTA DE REDE"
        
    return status, nome, bio

def analisar_deep_link(hash_str):
    """Descompila a hash/payload de resgate."""
    res_b64, res_b32, res_nums = "N/A", "N/A", "N/A"
    if not hash_str:
        return res_b64, res_b32, res_nums

    try:
        padded_hash = hash_str + '=' * (-len(hash_str) % 4)
        res_b64 = base64.b64decode(padded_hash).decode('utf-8', errors='ignore')
    except Exception:
        res_b64 = "Falha no decode Base64"

    try:
        padded_hash32 = hash_str + '=' * (-len(hash_str) % 8)
        res_b32 = base64.b32decode(padded_hash32.upper()).decode('utf-8', errors='ignore')
    except Exception:
        pass

    numeros = re.findall(r'\d+', hash_str)
    if numeros:
        res_nums = ', '.join(numeros)

    return res_b64, res_b32, res_nums

# =====================================================================
# GERADOR DE RELATÓRIO HTML (ESTRUTURA ORIGINAL PRESERVADA)
# =====================================================================

def gerar_relatorio_html(username, user_id_raw, hash_str):
    user_clean = username.replace("@", "").strip() if username else ""
    
    # Executa análises ativas
    dados_id = analisar_user_id(user_id_raw)
    links_id = gerar_links_osint_id(user_id_raw)
    bot_status, nome_exibicao, bio_desc = checar_status_plataforma(user_clean)
    b64_res, b32_res, nums_res = analisar_deep_link(hash_str)
    
    tgstat_link = f"https://tgstat.com/bot/{user_clean}" if user_clean else "#"
    telemetrio_link = f"https://telemetr.io/en/channels?search={user_clean}" if user_clean else "#"

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hunter Intel - Relatório de Investigação</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }}

        body {{
            background-color: #0b0f19;
            color: #e2e8f0;
            padding: 30px 20px;
            font-size: 11pt;
            line-height: 1.5;
        }}

        .container {{
            max-width: 850px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #1e293b;
            margin-bottom: 30px;
        }}

        .title {{
            color: #00ff66; /* Verde Neon */
            font-size: 20pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 255, 102, 0.4);
            margin-bottom: 8px;
        }}

        .subtitle {{
            color: #ff0055; /* Vermelho Neon */
            font-size: 18pt;
            font-weight: bold;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }}

        .section-box {{
            background-color: #111827;
            border: 1px solid #1f293d;
            border-left: 4px solid #00ff66;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        }}

        .section-box.danger {{
            border-left-color: #ff0055;
        }}

        .section-title {{
            color: #f8fafc;
            font-size: 13pt;
            font-weight: bold;
            margin-bottom: 15px;
            display: block;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 8px;
        }}

        .data-grid {{
            width: 100%;
            border-collapse: collapse;
        }}

        .data-grid td {{
            padding: 10px 6px;
            vertical-align: top;
        }}

        .data-label {{
            color: #94a3b8;
            font-weight: 600;
            width: 30%;
        }}

        .data-value {{
            color: #38bdf8;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
        }}

        .btn-container {{
            margin-top: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
        }}

        .tech-btn {{
            display: inline-block;
            background-color: #ff0055;
            color: #ffffff !important;
            text-decoration: none;
            font-weight: bold;
            font-size: 11pt;
            padding: 12px 22px;
            border-radius: 4px;
            border: 1px solid #ff3377;
            box-shadow: 0 0 12px rgba(255, 0, 85, 0.3);
            transition: all 0.25s ease-in-out;
            cursor: pointer;
            text-align: center;
        }}

        .tech-btn:hover {{
            background-color: #000000 !important;
            color: #ff0055 !important;
            border: 1px solid #ff0055;
            box-shadow: 0 0 18px rgba(255, 0, 85, 0.7);
            transform: translateY(-2px);
        }}

        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 9pt;
            color: #64748b;
            border-top: 1px solid #1e293b;
            padding-top: 20px;
        }}
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <div class="title">Hunter Intel - Investigador Digital</div>
            <div class="subtitle">Engenharia Reversa realizada</div>
        </div>

        <div class="section-box">
            <span class="section-title">1. Identificação Técnica do Alvo</span>
            <table class="data-grid">
                <tr>
                    <td class="data-label">User ID Numérico:</td>
                    <td class="data-value" style="color: #00ff66;">{dados_id['id_num']}</td>
                </tr>
                <tr>
                    <td class="data-label">Username Registrado:</td>
                    <td class="data-value">@{user_clean if user_clean else "Não Informado / Busca por ID"}</td>
                </tr>
                <tr>
                    <td class="data-label">Nome Exibido (Bot):</td>
                    <td class="data-value" style="color: #ffffff;">{nome_exibicao}</td>
                </tr>
                <tr>
                    <td class="data-label">Status no Telegram:</td>
                    <td class="data-value" style="color: #00ff66;">{bot_status}</td>
                </tr>
                <tr>
                    <td class="data-label">Estimativa de Registro:</td>
                    <td class="data-value" style="color: #ffaa00;">{dados_id['estimativa']}</td>
                </tr>
                <tr>
                    <td class="data-label">HEX ID / Protocolo:</td>
                    <td class="data-value">{dados_id['hex_id']} ({dados_id['link_protocolo']})</td>
                </tr>
                <tr>
                    <td class="data-label">Bio / Descrição do Bot:</td>
                    <td class="data-value" style="color: #cbd5e1;">{bio_desc}</td>
                </tr>
            </table>
        </div>

        <div class="section-box danger">
            <span class="section-title">2. Análise de Payload & Deep Link</span>
            <table class="data-grid">
                <tr>
                    <td class="data-label">Hash Detectada:</td>
                    <td class="data-value">{hash_str if hash_str else 'Nenhuma hash informada'}</td>
                </tr>
                <tr>
                    <td class="data-label">Base64 Decode:</td>
                    <td class="data-value">{b64_res}</td>
                </tr>
                <tr>
                    <td class="data-label">Base32 Decode:</td>
                    <td class="data-value">{b32_res}</td>
                </tr>
                <tr>
                    <td class="data-label">Números Extraídos:</td>
                    <td class="data-value">{nums_res}</td>
                </tr>
            </table>
        </div>

        <div class="section-box">
            <span class="section-title">3. Pivoting de OSINT & Rastreamento Web por ID e Username</span>
            <p style="color: #94a3b8; margin-bottom: 15px;">
                Clique nos botões tecnológicos abaixo para consultar o histórico do ID e rastros indexados na web:
            </p>

            <div class="btn-container">
                <a href="{dados_id['link_protocolo']}" class="tech-btn">⚡ Abrir Perfil via ID</a>
                <a href="{links_id.get('sangmata_bot', '#')}" target="_blank" class="tech-btn">📜 Consultar Histórico Nomes (SangMata)</a>
                <a href="{links_id.get('google_id', '#')}" target="_blank" class="tech-btn">🔍 Google Search por User ID</a>
                <a href="{links_id.get('telegram_dork_id', '#')}" target="_blank" class="tech-btn">📡 Rastrear ID em Logs Telegram</a>
                {f'<a href="https://t.me/{user_clean}" target="_blank" class="tech-btn">🤖 Perfil Web Telegram</a>' if user_clean else ''}
                {f'<a href="https://github.com/search?q={user_clean}&type=code" target="_blank" class="tech-btn">💻 GitHub Code Search</a>' if user_clean else ''}
                {f'<a href="{tgstat_link}" target="_blank" class="tech-btn">📊 TGStat Analytics</a>' if user_clean else ''}
            </div>
        </div>

        <div class="section-box">
            <span class="section-title">4. Procedimento de Extração e Histórico pelo ID</span>
            <ol style="margin-left: 20px; color: #cbd5e1; line-height: 1.8;">
                <li>O botão <strong>"Consultar Histórico Nomes (SangMata)"</strong> abre a consulta direta do ID no robô de registros do Telegram.</li>
                <li>O botão <strong>"Google Search por User ID"</strong> localiza mensagens e citações antigas vinculadas ao número do ID antes da troca de nome.</li>
            </ol>
        </div>

        <div class="footer">
            Relatório gerado automaticamente por Hunter Intel System | Engenharia Reversa & OSINT
        </div>
    </div>

</body>
</html>
"""
    
    filename = f"relatorio_id_{user_id_raw if user_id_raw else 'alvo'}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n[+] RELATÓRIO HTML GERADO COM SUCESSO!")
    print(f"[+] Arquivo salvo em: {os.path.abspath(filename)}")

# =====================================================================
# EXECUÇÃO DO TERMINAL
# =====================================================================

def main():
    limpar_tela()
    print("="*60)
    print("      HUNTER INTEL - EXTRAÇÃO DE DATA & PLATAFORMA TELEGRAM    ")
    print("="*60)
    
    id_in = input("[>] Digite o User ID Numérico (OBRIGATÓRIO): ").strip()
    username_in = input("[>] Digite o @username (OPCIONAL - Pressione Enter para pular): ").strip()
    hash_in = input("[>] Digite a Hash/Payload do Gift (OPCIONAL - Pressione Enter para pular): ").strip()

    if not id_in:
        print("\n[-] Erro: É necessário fornecer ao menos o User ID Numérico.")
        return

    print("\n[*] Processando rastreio por ID numérico e preparando relatório...")
    gerar_relatorio_html(username_in, id_in, hash_in)

if __name__ == "__main__":
    main()