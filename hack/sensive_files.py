import requests
import os
import time
from datetime import datetime

def analisar_exposicao(url, lang_pref):
    resultado_geral = []
    
    # 20 ARQUIVOS E DIRETÓRIOS CRÍTICOS (Foco em Information Disclosure)
    arquivos_criticos = [
        ".env", ".git/config", ".git/index", "web.config", "config.php",
        "wp-config.php", "settings.py", ".env.bak", ".aws/credentials",
        "backup.sql", "database.sql", "dump.sql", "phpinfo.php",
        "server-status", ".htaccess", "docker-compose.yml", "package.json",
        ".svn/entries", ".gitignore", "robots.txt"
    ]

    correcoes_db = {
        "1": {"nome": "Python", "fix": "Adicione arquivos sensíveis ao seu .gitignore e use variáveis de ambiente seguras (os.environ)."},
        "2": {"nome": "Node.js", "fix": "Mantenha o .env fora da pasta 'public' e use o módulo 'dotenv' corretamente."},
        "3": {"nome": "PHP", "fix": "Mova arquivos de configuração para fora do diretório 'public_html' ou bloqueie acesso via .htaccess."}
    }

    print(f"🕵️ Buscando exposição de dados em {len(arquivos_criticos)} arquivos...")

    for arq in arquivos_criticos:
        alvo_completo = url.rstrip('/') + '/' + arq
        try:
            # allow_redirects=False para evitar falsos positivos de páginas de erro
            res = requests.get(alvo_completo, timeout=5, allow_redirects=False)
            
            # Se retornar 200 OK, o arquivo está lá e está acessível!
            if res.status_code == 200:
                # Verificação extra: se for um .env, procuramos palavras-chave
                sensivel = any(word in res.text.lower() for word in ["db_", "key", "password", "token"])
                
                resultado_geral.append({
                    "arquivo": arq,
                    "url_vulneravel": alvo_completo,
                    "risco": "Crítico" if sensivel else "Médio",
                    "impacto": "Exposição de credenciais, segredos de API ou estrutura interna do código.",
                    "correcao": correcoes_db[lang_pref]["fix"]
                })
        except:
            continue
        time.sleep(0.3)

    return resultado_geral

def gerar_relatorio_exposicao(url, recs):
    if not os.path.exists("reports"): os.makedirs("reports")
    nome_arquivo = f"reports/Report_Disclosure_{int(time.time())}.md"
    
    conteudo = f"# Relatório Técnico: Exposição de Arquivos Sensíveis\n\n**Alvo:** {url}\n\n---\n"
    
    if not recs:
        conteudo += "✅ Nenhum arquivo sensível óbvio foi encontrado nos diretórios padrão."
    else:
        for r in recs:
            conteudo += f"### 🚨 Arquivo Exposto: `{r['arquivo']}`\n"
            conteudo += f"- **Link Direto:** {r['url_vulneravel']}\n"
            conteudo += f"- **Nível de Risco:** {r['risco']}\n"
            conteudo += f"- **🔴 Impacto:** {r['impacto']}\n"
            conteudo += f"- **✅ Correção Sugerida:** {r['correcao']}\n\n---\n"
            
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"\n[+] Relatório de Exposição gerado: {nome_arquivo}")

if __name__ == "__main__":
    target = input("🔎 URL Alvo para Scan: ").strip()
    if not target.startswith("http"): target = "https://" + target
    lang = input("Linguagem (1-Py, 2-Node, 3-PHP): ")
    
    achados = analisar_exposicao(target, lang)
    gerar_relatorio_exposicao(target, achados)
