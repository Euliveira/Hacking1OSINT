import re
import html
import urllib.parse
from datetime import datetime

def extract_all_artifacts(text):
    """
    Extrai IoCs tradicionais e Artefatos de Atribuição do Atacante/Criador.
    """
    # Decodifica URLs/caracteres percent-encoded caso o texto venha de uma URL de e-mail ou payload bruto
    decoded_text = urllib.parse.unquote(text)

    # 1. IoCs Tradicionais (IPs, URLs e Telefones/SMS)
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    url_pattern = r'https?://[^\s<>"{}|\\^`]+'
    # Padrão para números de telefone, shortcodes de SMS (5 dígitos) e DDI/DDD
    phone_pattern = r'\b(?:\+?[0-9]{1,3}\s?)?(?:\([0-9]{2,3}\)\s?)?[0-9]{4,5}[-.\s]?[0-9]{4}\b|\b[0-9]{4,6}\b'
    
    ips = list(set(re.findall(ip_pattern, decoded_text)))
    urls = list(set(re.findall(url_pattern, decoded_text)))
    domains = list(set([urllib.parse.urlparse(u).netloc for u in urls if urllib.parse.urlparse(u).netloc]))
    phones = list(set(re.findall(phone_pattern, decoded_text)))

    # 2. Artefatos do Criador / Atribuição (Vazamentos)
    telegram_tokens = list(set(re.findall(r'\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b', decoded_text)))
    telegram_chats = list(set(re.findall(r'(?:chat_id=|chat_id":\s*)(-?[0-9]{5,15})', decoded_text, re.IGNORECASE)))
    emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', decoded_text)))
    analytics_ids = list(set(re.findall(r'\b(?:UA-\d+-\d+|G-[A-Z0-9]{8,12}|GTM-[A-Z0-9]{6,10})\b', decoded_text)))
    crypto_btc = list(set(re.findall(r'\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\b', decoded_text)))
    crypto_eth = list(set(re.findall(r'\b0x[a-fA-F0-9]{40}\b', decoded_text)))

    artifacts = {
        "telegram_tokens": telegram_tokens,
        "telegram_chats": telegram_chats,
        "emails": emails,
        "phones": phones,
        "analytics": analytics_ids,
        "crypto": crypto_btc + crypto_eth
    }

    return ips, urls, domains, artifacts

def generate_html_report(sender, raw_input, ips, urls, domains, artifacts):
    # Processa blocos de Atribuição
    creator_found = any(len(v) > 0 for v in artifacts.values())
    
    creator_rows = ""
    if creator_found:
        if artifacts["telegram_tokens"]:
            for token in artifacts["telegram_tokens"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-danger">Telegram Bot Token</span></td>
                    <td><code>{token}</code></td>
                    <td><a href="https://api.telegram.org/bot{token}/getMe" target="_blank" class="btn btn-vt">Verificar Bot via API</a></td>
                </tr>"""
        if artifacts["telegram_chats"]:
            for chat in artifacts["telegram_chats"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-danger">Telegram Chat ID</span></td>
                    <td><code>{chat}</code></td>
                    <td><a href="https://t.me/SangMataInfo_bot?start={chat}" target="_blank" class="btn btn-info">Checar SangMata</a></td>
                </tr>"""
        if artifacts["emails"]:
            for email_addr in artifacts["emails"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-warning">E-mail Exposto</span></td>
                    <td><code>{email_addr}</code></td>
                    <td>
                        <a href="https://epieos.com/?q={email_addr}" target="_blank" class="btn btn-info">EPIEOS (OSINT)</a>
                        <a href="https://intelx.io/?s={email_addr}" target="_blank" class="btn btn-shodan">IntelX</a>
                    </td>
                </tr>"""
        if artifacts["phones"]:
            for phone in artifacts["phones"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-warning">Remetente / SMS (Telefone)</span></td>
                    <td><code>{phone}</code></td>
                    <td><a href="https://www.truecaller.com/search/global/{phone}" target="_blank" class="btn btn-info">Truecaller / OSINT</a></td>
                </tr>"""
        if artifacts["analytics"]:
            for tracker in artifacts["analytics"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-warning">Tracking ID</span></td>
                    <td><code>{tracker}</code></td>
                    <td><a href="https://builtwith.com/relationships/{tracker}" target="_blank" class="btn btn-whois">BuiltWith Pivot</a></td>
                </tr>"""
        if artifacts["crypto"]:
            for wallet in artifacts["crypto"]:
                creator_rows += f"""
                <tr>
                    <td><span class="badge-warning">Carteira Crypto</span></td>
                    <td><code>{wallet}</code></td>
                    <td><a href="https://www.blockchain.com/explorer/search?search={wallet}" target="_blank" class="btn btn-info">Blockchain Explorer</a></td>
                </tr>"""
    else:
        creator_rows = "<tr><td colspan='3' class='empty'>Nenhum artefato direto do criador (Bot Token, E-mail, Analytics, Telefones) foi identificado no texto colado.</td></tr>"

    # Tabela de IPs
    ip_rows = ""
    if ips:
        for ip in ips:
            ip_rows += f"""
            <tr>
                <td><strong class="highlight">{ip}</strong></td>
                <td>
                    <a href="https://www.abuseipdb.com/check/{ip}" target="_blank" class="btn btn-abuse">AbuseIPDB</a>
                    <a href="https://www.virustotal.com/gui/ip-address/{ip}" target="_blank" class="btn btn-vt">VirusTotal</a>
                    <a href="https://www.shodan.io/host/{ip}" target="_blank" class="btn btn-shodan">Shodan</a>
                    <a href="https://ipinfo.io/{ip}" target="_blank" class="btn btn-info">IPInfo</a>
                </td>
            </tr>"""
    else:
        ip_rows = "<tr><td colspan='2' class='empty'>Nenhum IP direto encontrado.</td></tr>"

    # Tabela de URLs / Domínios
    url_rows = ""
    targets = list(set(urls + domains))
    if targets:
        for target in targets:
            encoded_target = urllib.parse.quote_plus(target)
            url_rows += f"""
            <tr>
                <td><code>{html.escape(target)}</code></td>
                <td>
                    <a href="https://urlscan.io/search/#'{encoded_target}'" target="_blank" class="btn btn-info">URLScan.io</a>
                    <a href="https://www.virustotal.com/gui/search/{encoded_target}" target="_blank" class="btn btn-vt">VirusTotal</a>
                    <a href="https://centralops.net/co/DomainDossier.aspx?addr={encoded_target}" target="_blank" class="btn btn-whois">WHOIS / Dossier</a>
                </td>
            </tr>"""
    else:
        url_rows = "<tr><td colspan='2' class='empty'>Nenhuma URL encontrada.</td></tr>"

    # HTML
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Atribuição OSINT - Threat Report</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #161e2e;
            --border-color: #2d3748;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --accent-red: #f43f5e;
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
        }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 30px; line-height: 1.5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: var(--card-bg); padding: 30px; border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .header {{ border-bottom: 2px solid var(--border-color); padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
        h1 {{ color: var(--accent-red); margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; }}
        .badge-danger {{ background: #881337; color: #fecdd3; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge-warning {{ background: #78350f; color: #fef3c7; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #0f172a; padding: 15px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid var(--accent-red); }}
        .meta-item span {{ color: var(--text-muted); font-size: 12px; display: block; }}
        .meta-item strong {{ font-size: 14px; color: var(--text-main); }}
        .raw-box {{ background: #0b0f19; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 13px; color: #cbd5e1; border: 1px solid var(--border-color); overflow-x: auto; white-space: pre-wrap; word-break: break-all; margin-bottom: 25px; }}
        h3 {{ color: var(--accent-blue); margin-top: 25px; margin-bottom: 10px; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .section-alert {{ border: 1px solid var(--accent-amber); background: #1a1500; border-radius: 8px; padding: 15px; margin-bottom: 25px; }}
        .section-alert h3 {{ color: var(--accent-amber); margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color); }}
        th, td {{ padding: 12px 16px; text-align: left; font-size: 13px; border-bottom: 1px solid var(--border-color); }}
        th {{ background-color: #1e293b; color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; }}
        .highlight {{ color: #f43f5e; }}
        .empty {{ color: var(--text-muted); font-style: italic; }}
        .btn {{ display: inline-block; padding: 5px 10px; margin: 2px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: 600; color: #ffffff; transition: opacity 0.2s; }}
        .btn:hover {{ opacity: 0.8; }}
        .btn-abuse {{ background-color: #ea580c; }}
        .btn-vt {{ background-color: #2563eb; }}
        .btn-shodan {{ background-color: #dc2626; }}
        .btn-info {{ background-color: #0284c7; }}
        .btn-whois {{ background-color: #059669; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 OSINT Threat & Creator Attribution Report</h1>
        </div>

        <div class="meta-grid">
            <div class="meta-item">
                <span>Data da Análise</span>
                <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
            </div>
            <div class="meta-item">
                <span>Origem / Remetente Informado</span>
                <strong>{html.escape(sender if sender else 'Não especificado')}</strong>
            </div>
        </div>

        <!-- SEÇÃO DE ATRIBUIÇÃO DE CRIADOR -->
        <div class="section-alert">
            <h3>⚠️ Dados de Atribuição / Artefatos do Criador</h3>
            <table>
                <thead>
                    <tr>
                        <th>Tipo de Artefato</th>
                        <th>Valor Encontrado</th>
                        <th>Ação de Investigação OSINT</th>
                    </tr>
                </thead>
                <tbody>
                    {creator_rows}
                </tbody>
            </table>
        </div>

        <h3>🌐 Infraestrutura & IPs</h3>
        <table>
            <thead>
                <tr>
                    <th>Endereço IP</th>
                    <th>Plataformas</th>
                </tr>
            </thead>
            <tbody>{ip_rows}</tbody>
        </table>

        <h3>🔗 Domínios e URLs</h3>
        <table>
            <thead>
                <tr>
                    <th>Alvo</th>
                    <th>Ferramentas</th>
                </tr>
            </thead>
            <tbody>{url_rows}</tbody>
        </table>

        <h3>📝 Conteúdo Analisado (Payload)</h3>
        <div class="raw-box">{html.escape(raw_input)}</div>
    </div>
</body>
</html>"""

    filename = f"osint_attribution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    return filename

def main():
    print("=" * 65)
    print(" 🎯 OSINT ATTRIBUTION & IOC INVESTIGATOR")
    print("=" * 65)
    
    remetente = input("\n[1] Digite a origem/remetente (opcional): ").strip()
    
    print("\n[2] Cole o SMS, código HTML da página phishing, parâmetros ou texto do payload.")
    print("    (Para concluir a entrada, digite 'FIM' em uma nova linha e aperte Enter):")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "FIM":
                break
            lines.append(line)
        except EOFError:
            break
            
    raw_payload = "\n".join(lines).strip()
    
    if not raw_payload:
        print("\n[!] Nenhuma entrada fornecida.")
        return

    print("\n[*] Analisando payload e extraindo artefatos de atribuição...")
    ips, urls, domains, artifacts = extract_all_artifacts(raw_payload)
    
    print(f"    ├─ IPs: {len(ips)}")
    print(f"    ├─ URLs/Domínios: {len(urls) + len(domains)}")
    print(f"    ├─ Telefones / SMS: {len(artifacts['phones'])}")
    print(f"    ├─ Telegram Tokens/Chats: {len(artifacts['telegram_tokens']) + len(artifacts['telegram_chats'])}")
    print(f"    ├─ E-mails Expostos: {len(artifacts['emails'])}")
    print(f"    └─ IDs de Analytics/Trackers: {len(artifacts['analytics'])}")

    report_file = generate_html_report(remetente, raw_payload, ips, urls, domains, artifacts)
    print(f"\n[✓] Relatório de Atribuição gerado: {report_file}")

if __name__ == "__main__":
    main()