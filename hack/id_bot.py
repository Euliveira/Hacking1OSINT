import os
import asyncio
import base64
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    UserStatusOnline, UserStatusOffline, UserStatusRecently,
    UserStatusLastWeek, UserStatusLastMonth, User
)

# ---------------------------------------------------------------------
# CREDENCIAIS DA API DO TELEGRAM (Obtenha em my.telegram.org)
# ---------------------------------------------------------------------
API_ID = 37275908          # Substitua pelo seu API ID (número inteiro)
API_HASH = 'cd5599096bbd2de1763339c25de37676'  # Substitua pelo seu API Hash (string)

def gerar_relatorio_html(dados, fotos_base64):
    """Gera um relatório HTML interativo com o estilo dark mode / cyber."""
    uid = dados['user_id']
    username = dados['username']
    nome = dados['nome']
    tipo = dados['tipo_conta']
    bio = dados['bio']
    status = dados['status']
    restricao = dados['restricao']
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Renderização da galeria de fotos em Base64
    fotos_html = ""
    if fotos_base64:
        for idx, img_b64 in enumerate(fotos_base64, 1):
            fotos_html += f"""
            <div class="photo-card">
                <img src="data:image/jpeg;base64,{img_b64}" alt="Foto {idx}">
                <div class="photo-caption">Foto #{idx}</div>
            </div>"""
    else:
        fotos_html = '<p style="color: #94a3b8; font-style: italic;">Nenhuma foto de perfil pública ou acessível encontrada.</p>'

    user_link_button = f'<a href="https://t.me/{username}" target="_blank" class="tech-btn">🤖 Link Web Telegram</a>' if username else ''
    tgstat_button = f'<a href="https://tgstat.com/bot/{username}" target="_blank" class="tech-btn">📊 TGStat Analytics</a>' if username else ''
    user_str = f"@{username}" if username else "Sem @username definido"

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hunter Intel - Telegram Report #{uid}</title>
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
            max-width: 900px;
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
            font-size: 22pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-shadow: 0 0 12px rgba(0, 255, 102, 0.4);
            margin-bottom: 6px;
        }}

        .subtitle {{
            color: #ff0055; /* Vermelho Neon */
            font-size: 14pt;
            font-weight: bold;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }}

        .timestamp {{
            color: #64748b;
            font-size: 9pt;
            margin-top: 8px;
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

        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .photo-card {{
            background-color: #0d1321;
            border: 1px solid #1f293d;
            border-radius: 6px;
            overflow: hidden;
            text-align: center;
            padding: 8px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .photo-card:hover {{
            transform: scale(1.03);
            border-color: #00ff66;
        }}

        .photo-card img {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 4px;
        }}

        .photo-caption {{
            font-size: 9pt;
            color: #94a3b8;
            margin-top: 6px;
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
            font-size: 10.5pt;
            padding: 12px 20px;
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
            <div class="title">Hunter Intel - Report Telegram</div>
            <div class="subtitle">Análise Extrativa MTProto</div>
            <div class="timestamp">Relatório gerado em: {data_geracao}</div>
        </div>

        <!-- SEÇÃO 1: METADADOS PRINCIPAIS -->
        <div class="section-box">
            <span class="section-title">1. Identificação de Perfil & Atributos</span>
            <table class="data-grid">
                <tr>
                    <td class="data-label">User ID Permanente:</td>
                    <td class="data-value" style="color: #00ff66;">{uid}</td>
                </tr>
                <tr>
                    <td class="data-label">Nome de Exibição:</td>
                    <td class="data-value" style="color: #ffffff;">{nome}</td>
                </tr>
                <tr>
                    <td class="data-label">Username Registrado:</td>
                    <td class="data-value">{user_str}</td>
                </tr>
                <tr>
                    <td class="data-label">Tipo de Conta:</td>
                    <td class="data-value" style="color: #ffaa00;">{tipo}</td>
                </tr>
                <tr>
                    <td class="data-label">Status de Conexão:</td>
                    <td class="data-value" style="color: #00ff66;">{status}</td>
                </tr>
                <tr>
                    <td class="data-label">Bio / Descrição:</td>
                    <td class="data-value" style="color: #cbd5e1; font-family: sans-serif;">{bio}</td>
                </tr>
            </table>
        </div>

        <!-- SEÇÃO 2: SEGURANÇA E RESTRIÇÕES -->
        <div class="section-box danger">
            <span class="section-title">2. Sanções & Flags de Restrição da Plataforma</span>
            <table class="data-grid">
                <tr>
                    <td class="data-label">Status de Restrição:</td>
                    <td class="data-value">{restricao}</td>
                </tr>
            </table>
        </div>

        <!-- SEÇÃO 3: GALERIA DE FOTOS HISTÓRICAS -->
        <div class="section-box">
            <span class="section-title">3. Histórico de Imagens de Perfil ({len(fotos_base64)})</span>
            <div class="gallery-grid">
                {fotos_html}
            </div>
        </div>

        <!-- SEÇÃO 4: PIVOTAGEM & PESQUISA EXTERNA -->
        <div class="section-box">
            <span class="section-title">4. Pivotagem & Pesquisa Externa</span>
            <div class="btn-container">
                <a href="tg://user?id={uid}" class="tech-btn">⚡ Abrir Perfil via Protocolo ID</a>
                <a href="https://t.me/SangMataInfo_bot?start={uid}" target="_blank" class="tech-btn">📜 Histórico de Nomes (SangMata)</a>
                <a href="https://www.google.com/search?q=%22{uid}%22" target="_blank" class="tech-btn">🔍 Google Dork por User ID</a>
                {user_link_button}
                {tgstat_button}
            </div>
        </div>

        <div class="footer">
            Hunter Intel System • Relatório Técnico de Engenharia Reversa & Protocolo MTProto
        </div>
    </div>

</body>
</html>
"""
    filename = f"relatorio_telegram_{uid}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[+] RELATÓRIO HTML PORTÁTIL GERADO COM SUCESSO!")
    print(f"[+] Salvo em: {os.path.abspath(filename)}")


async def main():
    async with TelegramClient('sessao_hunter_intel', API_ID, API_HASH) as client:
        print("="*65)
        print("    HUNTER INTEL - EXTRATOR MTPROTO COM GERADOR HTML DE PERFIL")
        print("="*65)

        alvo_input = input("\n[>] Digite o nome do bot, @username ou User ID: ").strip()
        if not alvo_input:
            print("[-] Nenhuma entrada fornecida.")
            return

        alvo = int(alvo_input) if alvo_input.isdigit() else alvo_input

        try:
            entidade = await client.get_entity(alvo)
        except Exception as e:
            print(f"\n[-] Erro ao localizar o alvo no Telegram: {e}")
            return

        print("[*] Coletando atributos técnicos do alvo...")

        # 1. Tipo de Conta
        if getattr(entidade, 'bot', False):
            tipo_conta = "Bot (Automação / Robô)"
        elif isinstance(entidade, User):
            tipo_conta = "Perfil Pessoal"
        else:
            tipo_conta = "Canal / Grupo / Supergrupo"

        # 2. Bio / Descrição
        bio = "N/A ou Não Cadastrada"
        if isinstance(entidade, User):
            try:
                full_info = await client(GetFullUserRequest(entidade))
                bio = full_info.full_user.about or "Sem bio definida"
            except Exception:
                bio = "Oculto pelas configurações de privacidade do alvo"

        # 3. Status de Conexão
        status_str = "Desconhecido / Oculto pelo Usuário"
        if hasattr(entidade, 'status') and entidade.status:
            st = entidade.status
            if isinstance(st, UserStatusOnline):
                status_str = "Online AGORA"
            elif isinstance(st, UserStatusRecently):
                status_str = "Visto recentemente (Últimas 24h / 3 dias)"
            elif isinstance(st, UserStatusLastWeek):
                status_str = "Visto na última semana"
            elif isinstance(st, UserStatusLastMonth):
                status_str = "Visto no último mês"
            elif isinstance(st, UserStatusOffline):
                status_str = f"Offline (Última conexão: {st.was_online.strftime('%d/%m/%Y %H:%M:%S')} UTC)"

        # 4. Restrições e Bans
        restrito = getattr(entidade, 'restricted', False)
        if restrito:
            reasons = getattr(entidade, 'restriction_reason', [])
            detalhes = ", ".join([f"{r.platform}:{r.reason}" for r in reasons]) if reasons else "Restrição ativa"
            status_ban = f"⚠️ CONTA RESTRITA / BANIDA ({detalhes})"
        else:
            status_ban = " Sem restrições ou banimentos ativos detectados"

        # 5. Download e encode Base64 das fotos de perfil
        print("[*] Extraindo fotos de perfil e convertendo para HTML...")
        fotos_base64 = []
        try:
            fotos = await client.get_profile_photos(entidade)
            for idx, foto in enumerate(fotos, 1):
                raw_bytes = await client.download_media(foto, file=bytes)
                if raw_bytes:
                    b64_str = base64.b64encode(raw_bytes).decode('utf-8')
                    fotos_base64.append(b64_str)
        except Exception as e:
            print(f"[!] Não foi possível baixar fotos: {e}")

        # Nome de exibição
        nome_completo = f"{getattr(entidade, 'first_name', '') or ''} {getattr(entidade, 'last_name', '') or ''}".strip()
        if not nome_completo:
            nome_completo = getattr(entidade, 'title', 'N/A')

        dados_coletados = {
            "user_id": entidade.id,
            "nome": nome_completo,
            "username": getattr(entidade, 'username', None),
            "tipo_conta": tipo_conta,
            "bio": bio,
            "status": status_str,
            "restricao": status_ban
        }

        gerar_relatorio_html(dados_coletados, fotos_base64)

if __name__ == "__main__":
    asyncio.run(main())