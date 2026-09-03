import requests

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

# --- CONFIGURAÇÃO DOS SEUS DADOS DA DESK DATA ---
EMAIL_PLATAFORMA = "SEU E-MAIL"  # Mantido seu email cadastrado
SENHA_PLATAFORMA = "SENHA"        # Mantida sua senha de acesso

# 1. INPUT PARA O USUÁRIO DIGITAR O TELEFONE
print("=== SISTEMA DE BUSCA REVERSA OSINT ===")
telefone_alvo = input("Digite o número de telefone com DDD (apenas números, ex: 11000000000): ")

# Remove espaços em branco ou caracteres como parênteses e traços caso você digite
telefone_alvo = "".join(filter(str.isdigit, telefone_alvo))

if not telefone_alvo:
    print("Erro: Você precisa digitar um número válido.")
    exit()

# 2. Gera o token dinamicamente
token_jwt = obter_access_token(EMAIL_PLATAFORMA, SENHA_PLATAFORMA)

if token_jwt:
    url_queries = "https://api.deskdata.com.br/queries"
    
    headers_queries = {
        "Authorization": f"Bearer {token_jwt}",
        "Content-Type": "application/json"
    }
    
    # CORREÇÃO AQUI: Ajustado para os nomes de datasets aceitos pela API
    payload_busca = {
        "type": "persons",
        "key_type": "phone",
        "key_value": telefone_alvo,
        "datasets": ["basic_data", "addresses"] 
    }
    
    print(f"\nIniciando busca reversa para o número: {telefone_alvo}...")
    
    response = requests.post(url_queries, json=payload_busca, headers=headers_queries)
    
    if response.status_code == 200:
        print("\n--- DADOS LOCALIZADOS ---")
        resultado_final = response.json()
        print(resultado_final) # Exibe o JSON completo no terminal
    else:
        print(f"Erro na consulta: Status {response.status_code}")
        print(response.text)
else:
    print("Não foi possível iniciar a busca devido a erro na autenticação.")
