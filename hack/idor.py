import requests
import os
import time
from datetime import datetime
import re

def analisar_idor(url_completa, lang_pref):
    resultado_geral = []
    
    # Lógica aprimorada: Encontra o último número na URL para usar como ID base
    numeros na_url = re.findall(r'\d+', url_completa)
    if not numeros:
        print("❌ Erro: Não encontrei nenhum ID numérico na URL fornecida.")
        print("Exemplo correto: https://api.site.com/v1/user/1000")
        return None
    
    base_id_str = numeros[-1]
    base_id = int(base_id_str)
    # Cria um template da URL trocando o ID por um marcador
    url_template = url_completa.rsplit(base_id_str, 1)
    
    correcoes_db = {
        "1": {"nome": "Python", "fix": "Verifique se o ID do recurso pertence ao ID do usuário autenticado na sessão (Object-level Authorization)."},
        "2": {"nome": "Node.js", "fix": "Utilize middlewares para validar o 'owner' do documento antes de executar a query no Banco de Dados."},
        "3": {"nome": "PHP", "fix": "Sempre inclua o ID do usuário na cláusula WHERE: 'SELECT * FROM orders WHERE id = $id AND user_id = $my_id'."}
    }

    print(f"\n🎯 ID Base Detectado: {base_id}")
    print(f"🕵️ Testando arredores de {url_completa}...")

    # Testamos 5 IDs abaixo e 5 IDs acima (total 10 testes reais)
    faixa_teste = range(base_id - 5, base_id + 6)

    for test_id in faixa_teste:
        if test_id == base_id: continue
        
        # Monta a nova URL com o ID vizinho
        alvo = url_template[0] + str(test_id) + (url_template[1] if len(url_template] > 1 else "")
        
        try:
            # Simulando o ataque real de troca de ID
            res = requests.get(alvo, timeout=7)
            
            # Se retornar 200 (Sucesso) e o corpo não for vazio, é um forte indício de IDOR
            if res.status_code == 200 and len(res.text) > 100:
                print(f"💰 [POSSÍVEL IDOR] Acesso confirmado ao ID: {test_id}")
                resultado_geral.append({
                    "url_vulneravel": alvo,
                    "id_testado": test_id,
                    "status": res.status_code,
                    "impacto": "Quebra de controle de acesso: Usuário consegue visualizar dados de terceiros apenas alterando o ID.",
                    "correcao": correcoes_db[lang_pref]["fix"]
                })
        except Exception as e:
            print(f"⚠️ Erro ao testar ID {test_id}: {e}")
        
        time.sleep(1) # Delay para evitar bloqueio (WAF/Rate Limit)

    return resultado_geral

def gerar_relatorio_idor(url_original, achados):
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    nome_arquivo = f"reports/Report_IDOR_{int(time.time())}.md"
    
    conteudo = f"""# Relatório Profissional: IDOR (Insecure Direct Object Reference)
**URL Alvo Original:** {url_original}
**Data da Auditoria:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---

## 🛡️ Descrição da Falha
A aplicação permite a referência direta a objetos internos por meio da manipulação de identificadores (IDs) na URL. A falta de uma verificação de permissão no nível do objeto (BOLA) permite que um usuário autenticado acesse informações de outros usuários.



---

## 🚨 Provas de Conceito (PoC) Detectadas
"""
    if not achados:
        conteudo += "\n✅ Nenhum IDOR detectado nos IDs vizinhos testados.\n"
    else:
        for r in achados:
            conteudo += f"### ID Vulnerável: `{r['id_testado']}`\n"
            conteudo += f"- **URL Exposta:** {r['url_vulneravel']}\n"
            conteudo += f"- **Impacto:** {r['impacto']}\n"
            conteudo += f"- **Correção Sugerida:** {r['correcao']}\n\n---\n"

    conteudo += "\n\n*Relatório gerado automaticamente para Bug Bounty - Auditor: Willian de Oliveira.*"

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"\n[+] Relatório IDOR pronto para HackerOne: {nome_arquivo}")

if __name__ == "__main__":
    print("="*50)
    print("           IDOR HUNTER - REAL ATTACK PROOF")
    print("="*50)

    url_input = input("🔗 Insira a URL completa com o seu ID (ex: https://site.com/api/user/500): ").strip()
    
    print("\nLinguagem do Analista para Correção:\n1. Python | 2. Node.js | 3. PHP")
    escolha_lang = input("Opção: ")
    if escolha_lang not in ["1", "2", "3"]: escolha_lang = "1"

    recs = analisar_idor(url_input, escolha_lang)
    
    if recs is not None:
        gerar_relatorio_idor(url_input, recs)
