import requests
import json
import webbrowser
from datetime import datetime
import urllib.parse

def obter_access_token(email, senha, expiracao_horas=1):
    url_auth = "https://api.deskdata.com.br/auth"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "username": email,
        "password": senha,
        "expires_in": expiracao_horas
    }
    try:
        response = requests.post(url_auth, json=payload, headers=headers)
        if response.status_code == 200:
            resultado = response.json()
            token = resultado.get("data", {}).get("access_token")
            return token
        else:
            print(f"Erro na autenticação: Status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Falha de conexão ao autenticar: {e}")
        return None

def limpar_data(data_str):
    if not data_str:
        return "N/A"
    try:
        dt = datetime.strptime(data_str.split('T')[0], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return data_str

def formatar_endereco(item):
    rua = f"{item.get('street_type', '')} {item.get('street_name', '')}".strip()
    numero = item.get('number', '')
    complemento = item.get('complement', '')
    bairro = item.get('neighborhood', '')
    cidade = item.get('city', '')
    estado = item.get('state', '')
    cep = item.get('zip_code', '')
    
    partes = []
    if rua: partes.append(rua)
    if numero: partes.append(f"Nº {numero}")
    if complemento: partes.append(f"({complemento})")
    if bairro: partes.append(bairro)
    if cidade: partes.append(f"{cidade}-{estado}")
    if cep: partes.append(f"CEP: {cep}")
    
    return ", ".join(partes)

def gerar_url_mapa(item):
    rua = f"{item.get('street_type', '')} {item.get('street_name', '')}".strip()
    numero = item.get('number', '')
    cidade = item.get('city', '')
    estado = item.get('state', '')
    
    query = f"{rua}, {numero}, {cidade} - {estado}, Brasil"
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"

def processar_e_gerar_relatorio(resultado_json, telefone_alvo):
    data = resultado_json.get("data", {})
    
    basic_data = data.get("basic_data", {}) or {}
    if isinstance(basic_data, list) and len(basic_data) > 0:
        basic_data = basic_data[0]
        
    nome = basic_data.get("name", "NÃO LOCALIZADO")
    cpf = basic_data.get("tax_id", "NÃO LOCALIZADO")
    genero = basic_data.get("gender", "N/A")
    data_nascimento = limpar_data(basic_data.get("birth_date", ""))
    nome_mae = basic_data.get("mother_name", "N/A")
    
    addresses_data = data.get("addresses", {}) or {}
    items_enderecos = addresses_data.get("items", []) or []
    
    def obter_data_ordenacao(x):
        d = x.get("last_seen_date")
        return d if d else "1900-01-01T00:00:00Z"
    
    items_enderecos = sorted(items_enderecos, key=obter_data_ordenacao, reverse=True)

    print("\n" + "="*50)
    print("           DADOS EXTRAÍDOS E HIGIENIZADOS")
    print("="*50)
    print(f"Telefone Consultado: {telefone_alvo}")
    print(f"Nome Completo:       {nome}")
    print(f"CPF:                 {cpf}")
    print(f"Gênero:              {genero}")
    print(f"Data de Nascimento:  {data_nascimento}")
    print(f"Nome da Mãe:         {nome_mae}")
    print("-"*50)
    print(f"Endereços Vinculados ({len(items_enderecos)} encontrados):")
    
    for i, item in enumerate(items_enderecos, 1):
        end_formatado = formatar_endereco(item)
        visto_ultimo = limpar_data(item.get("last_seen_date", ""))
        prioridade = "PRINCIPAL" if item.get("is_main") else f"Secundário (Prioridade {item.get('priority', i)})"
        print(f" [{i}] {end_formatado}")
        print(f"     Status: {prioridade} | Última vez visto: {visto_ultimo}")
    print("="*50 + "\n")

    nome_arquivo_html = f"relatorio_osint_{telefone_alvo}.html"
    
    linhas_enderecos_html = ""
    for i, item in enumerate(items_enderecos, 1):
        end_text = formatar_endereco(item)
        url_mapa = gerar_url_mapa(item)
        visto_primeiro = limpar_data(item.get("first_seen_date", ""))
        visto_ultimo = limpar_data(item.get("last_seen_date", ""))
        tipo = "HOME" if item.get("type") == "HOME" else "WORK"
        principal_badge = '<span class="badge badge-main">Principal</span>' if item.get("is_main") else '<span class="badge badge-sec">Secundário</span>'
        
        linhas_enderecos_html += f'''
        <tr>
            <td>{i}</td>
            <td>{principal_badge}</td>
            <td>{tipo}</td>
            <td><strong>{end_text}</strong></td>
            <td>{visto_primeiro}</td>
            <td>{visto_ultimo}</td>
            <td>
                <a href="{url_mapa}" target="_blank" class="btn-mapa">🗺️ Abrir no Maps</a>
            </td>
        </tr>
        '''
        
    if not items_enderecos:
        linhas_enderecos_html = '<tr><td colspan="7" style="text-align:center; padding: 20px; color: #888;">Nenhum endereço vinculado encontrado.</td></tr>'

    # HTML template using string replacements instead of f-strings to avoid curly brace parsing issues
    html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório OSINT - {{TELEFONE}}</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-color: #38bdf8;
            --accent-hover: #0ea5e9;
            --border-color: #334155;
            --success: #10b981;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        
        .container {
            width: 100%;
            max-width: 1000px;
        }
        
        header {
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        
        h1 {
            font-size: 24px;
            color: var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .meta-header {
            font-size: 12px;
            color: var(--text-muted);
            text-align: right;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        @media (min-width: 768px) {
            .grid {
                grid-template-columns: 1fr 1fr;
            }
        }
        
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
        }
        
        .card h2 {
            font-size: 16px;
            color: var(--accent-color);
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-left: 4px solid var(--accent-color);
            padding-left: 8px;
        }
        
        .data-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #2d3748;
        }
        
        .data-row:last-child {
            border-bottom: none;
        }
        
        .label {
            color: var(--text-muted);
            font-weight: 500;
        }
        
        .value {
            font-weight: bold;
            color: var(--text-main);
        }
        
        .table-container {
            overflow-x: auto;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-top: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }
        
        th {
            background-color: #111827;
            color: var(--accent-color);
            font-weight: 600;
            padding: 12px 16px;
            text-transform: uppercase;
            font-size: 12px;
            border-bottom: 2px solid var(--border-color);
        }
        
        td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            vertical-align: middle;
        }
        
        tr:hover {
            background-color: #243249;
        }
        
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .badge-main {
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--success);
            border: 1px solid var(--success);
        }
        
        .badge-sec {
            background-color: rgba(148, 163, 184, 0.2);
            color: var(--text-muted);
            border: 1px solid var(--text-muted);
        }
        
        .btn-mapa {
            display: inline-block;
            background-color: var(--accent-color);
            color: #000;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        
        .btn-mapa:hover {
            background-color: var(--accent-hover);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Relatório de Inteligência (OSINT)</h1>
                <p style="color: var(--text-muted); margin-top: 5px;">Alvo: Consulta via Linha Telefônica</p>
            </div>
            <div class="meta-header">
                <p>Gerado em: {{GERADO_EM}}</p>
                <p>Status: Higienização Completa</p>
            </div>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2>Dados do Alvo</h2>
                <div class="data-row">
                    <span class="label">Telefone Analisado</span>
                    <span class="value" style="color: var(--accent-color);">{{TELEFONE}}</span>
                </div>
                <div class="data-row">
                    <span class="label">Nome Completo</span>
                    <span class="value">{{NOME}}</span>
                </div>
                <div class="data-row">
                    <span class="label">CPF Cadastrado</span>
                    <span class="value">{{CPF}}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Informações Adicionais</h2>
                <div class="data-row">
                    <span class="label">Gênero</span>
                    <span class="value">{{GENERO}}</span>
                </div>
                <div class="data-row">
                    <span class="label">Data de Nascimento</span>
                    <span class="value">{{NASCIMENTO}}</span>
                </div>
                <div class="data-row">
                    <span class="label">Nome da Mãe</span>
                    <span class="value">{{MAE}}</span>
                </div>
            </div>
        </div>
        
        <h2 style="font-size: 18px; color: var(--accent-color); margin-bottom: 10px; text-transform: uppercase;">Endereços Históricos e Ativos</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 12%">Status</th>
                        <th style="width: 10%">Tipo</th>
                        <th style="width: 43%">Endereço Completo</th>
                        <th style="width: 10%">Primeiro Registro</th>
                        <th style="width: 10%">Último Registro</th>
                        <th style="width: 10%">Localização</th>
                    </tr>
                </thead>
                <tbody>
                    {{LINHAS}}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

    # Realizando as substituições manuais no template
    html_content = html_template.replace("{{TELEFONE}}", telefone_alvo)
    html_content = html_content.replace("{{GERADO_EM}}", datetime.now().strftime('%d/%m/%Y às %H:%M:%S'))
    html_content = html_content.replace("{{NOME}}", nome)
    html_content = html_content.replace("{{CPF}}", cpf)
    html_content = html_content.replace("{{GENERO}}", genero)
    html_content = html_content.replace("{{NASCIMENTO}}", data_nascimento)
    html_content = html_content.replace("{{MAE}}", nome_mae)
    html_content = html_content.replace("{{LINHAS}}", linhas_enderecos_html)
    
    with open(nome_arquivo_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"-> Relatório HTML gerado com sucesso: {nome_arquivo_html}")
    try:
        webbrowser.open(nome_arquivo_html)
    except Exception:
        pass

# --- CONFIGURAÇÃO DOS SEUS DADOS DA DESK DATA ---
EMAIL_PLATAFORMA = "SEU E-MAIL"
SENHA_PLATAFORMA = "SUA SENHA"

# --- EXECUÇÃO DO FLUXO PRINCIPAL ---
if __name__ == "__main__":
    print("=== SISTEMA DE BUSCA REVERSA OSINT ===")
    telefone_alvo = input("Digite o número de telefone com DDD (apenas números, ex: 11000000000): ")
    telefone_alvo = "".join(filter(str.isdigit, telefone_alvo))

    if not telefone_alvo:
        print("Erro: Você precisa digitar um número válido.")
        exit()

    token_jwt = obter_access_token(EMAIL_PLATAFORMA, SENHA_PLATAFORMA)

    if token_jwt:
        url_queries = "https://api.deskdata.com.br/queries"
        
        headers_queries = {
            "Authorization": f"Bearer {token_jwt}",
            "Content-Type": "application/json"
        }
        
        payload_busca = {
            "type": "persons",
            "key_type": "phone",
            "key_value": telefone_alvo,
            "datasets": ["basic_data", "addresses"] 
        }
        
        print(f"\nIniciando busca reversa para o número: {telefone_alvo}...")
        
        try:
            response = requests.post(url_queries, json=payload_busca, headers=headers_queries)
            
            if response.status_code == 200:
                resultado_final = response.json()
                processar_e_gerar_relatorio(resultado_final, telefone_alvo)
            else:
                print(f"Erro na consulta: Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Erro ao conectar com a API de consultas: {e}")
    else:
        print("Não foi possível iniciar a busca devido a erro na autenticação.")
