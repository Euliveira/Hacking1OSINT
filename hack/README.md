# Cibersegurança

# # 🛡️ NeuralKore-WAF (Intelligent HIDS/WAF)

**Desenvolvido por:** Willian de Oliveira  
**Certificação:** Cibersegurança Essencial pela IBSEC (Instituto Brasileiro de Cirsegurança)  
**Versão:** 1.0.0

---

## 📖 Visão Geral

O **NeuralKore-WAF** é um sistema inteligente de detecção de intrusão (HIDS) focado em inspeção de payloads em tempo real. Diferente de firewalls tradicionais baseados em assinaturas estáticas (Regex), o NeuralKore utiliza **Machine Learning** para identificar comportamentos anômalos e tentativas de exploração no tráfego web.

Este projeto foi desenhado para atuar na vanguarda da defesa, fornecendo visibilidade total sobre o atacante e gerando documentação forense instantânea.

---

## 🧠 Diferenciais Estratégicos

### 1. Detecção Baseada em Inteligência Artificial
Utiliza o algoritmo **Random Forest** com vetorização de caracteres (**TF-IDF**), permitindo que o sistema identifique:
* **Ataques conhecidos:** SQLi, XSS, RCE, LFI.
* **Zero-Days:** Identificação de padrões suspeitos mesmo em payloads nunca antes catalogados.

### 2. Análise Forense Automatizada
Ao detectar uma ameaça, o sistema não apenas alerta, mas executa o triângulo da resposta a incidentes:
* **Exposição em Tempo Real:** Detalhes do invasor (IP, Dispositivo, User-Agent) exibidos no terminal.
* **Relatórios Legíveis (.txt):** Geração automática de "fichas criminais" detalhadas para auditoria.
* **Log de Auditoria:** Registro persistente para análise post-mortem.

### 3. Fingerprinting do Invasor
O sistema captura e correlaciona metadados críticos:
* **🌐 IP de Origem:** Identificação do ponto de ataque.
* **🖥 Dispositivo e UA:** Mapeamento do ambiente do atacante.
* **🕛 Timestamp Preciso:** Cronologia exata para resposta a incidentes.

---

## 🛠️ Arquitetura Técnica

* **Linguagem:** Python 3.x  
* **Launcher Principal:** app.py  
* **Servidor Web:** Flask  
* **Comunicação em Tempo Real:** Flask-SocketIO (WebSockets)  
* **Engine de IA:** Scikit-Learn (Random Forest Classifier)  
* **Vetorização de Texto:** TF-IDF (N-grams)  
* **Persistência de Modelo:** Joblib (.pkl)  
* **Processamento de Dados:** Pandas  
* **Interface Web:** HTML (templates/index.html)  
* **Monitoramento de Logs:** File Tailing (O(1) overhead)
---


 ## Como Executar:

### Clone o repositório

```bash
git clone https://github.com/euliveira/hack
cd hack
```

---

### Crie e ative o ambiente virtual (Opcional)

#### Linux / WSL
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

---

### Instale as dependências

```bash
pip install -r requirements.txt
```

---

### Execute o sistema

```bash
python app.py
```

---

### 🌐 Acesse no navegador

http://localhost:5000

---

## 🛡️ Pentest e Bug Bounty

Os scripts abaixo executam testes reais de exploração.

⚠️ Utilize apenas em ambientes autorizados e com permissão explícita.  
O uso indevido pode violar a LGPD e demais legislações aplicáveis.

```bash
python3 openredirect.py
python3 sqlinjection.py
python3 xss.py
python3 sensive_files.py
python3 idor.py
---

🔐 Projeto focado em Segurança Defensiva e Ofensiva com Inteligência Artificial.