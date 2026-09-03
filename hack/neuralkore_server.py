import os
import joblib
import pandas as pd
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- INTEGRAÇÃO WEB EM TEMPO REAL ---
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
# Permitir conexões externas para funcionar no Android/Rede Local
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class NeuralKoreWAF:
    def __init__(self):
        self.model_path = "models/cyber_model.pkl"
        self.log_path = "logs/audit_forense.log"
        self.report_dir = "reports"
        self.target_stream = "server_access.log"
        
        # Aumentei o ngram para pegar padrões maiores de ataques
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 4), analyzer='char')
        self.clf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
        self.le = LabelEncoder()
        
        os.makedirs("models", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)

    def initialize_engine(self):
        if os.path.exists(self.model_path):
            print("🧠 [SISTEMA] Carregando inteligência pré-treinada...")
            # Corrigido carregamento para garantir que as 3 partes sejam recuperadas
            self.clf, self.vectorizer, self.le = joblib.load(self.model_path)
        else:
            print("🧠 [TREINO] Iniciando IA com padrões OWASP...")
            training_data = [
                ("index.php?id=1", "Safe"), ("api/v1/user", "Safe"),
                ("<script>alert(1)</script>", "XSS"), ("<svg/onload=alert(1)>", "XSS"),
                ("' OR 1=1 --", "SQLi"), ("SELECT * FROM users", "SQLi"),
                ("; rm -rf /", "RCE"), ("python -c 'import socket'", "RCE"),
                ("../../../etc/passwd", "LFI"), ("php://filter/", "LFI")
            ]
            df = pd.DataFrame(training_data, columns=['payload', 'label'])
            y = self.le.fit_transform(df['label'])
            X = self.vectorizer.fit_transform(df['payload'])
            self.clf.fit(X, y)
            joblib.dump((self.clf, self.vectorizer, self.le), self.model_path)

    def gerar_relatorio_detalhado(self, dados):
        data_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_relatorio = f"{self.report_dir}/incidente_{data_arquivo}.txt"
        
        conteudo = f"""
================================================================
          RELATÓRIO DE INCIDENTE DETECTADO PELA IA
================================================================
RESPONSÁVEL: Willian de Oliveira (IBSEC)
HORÁRIO: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
----------------------------------------------------------------
[DADOS DO INVASOR]
🌐 IP: {dados['ip']}
🖥 DISPOSITIVO: {dados['dispositivo']}

[ANÁLISE DO ATAQUE]
💉 CATEGORIA: {dados['categoria']}
🎯 CONFIANÇA DA IA: {dados['confianca']}%
💣 PAYLOAD: {dados['payload']}
----------------------------------------------------------------
Relatório gerado para fins de auditoria forense local.
================================================================
"""
        with open(nome_relatorio, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return nome_relatorio

    def inspect_payload(self, line):
        if not line.strip(): return
        
        # Garante que a linha processada não quebre o servidor se estiver mal formatada
        parts = line.split(" | ")
        if len(parts) >= 2:
            ip = parts[0]
            payload = parts[1]
            dispositivo = parts[2] if len(parts) > 2 else "Desconhecido"
        else:
            ip, payload, dispositivo = "127.0.0.1", line, "Sistema Local"

        X = self.vectorizer.transform([payload])
        prediction = self.clf.predict(X)[0]
        # Cálculo de probabilidade para dar a porcentagem de confiança
        confidence = max(self.clf.predict_proba(X)[0]) * 100
        category = self.le.inverse_transform([prediction])[0]
        
        # Só alerta se for algo perigoso
        if category != "Safe" and confidence > 70:
            horario_atual = datetime.now().strftime("%H:%M:%S")
            dados_ataque = {
                'ip': ip, 
                'payload': payload, 
                'dispositivo': dispositivo,
                'categoria': category,
                'confianca': round(confidence, 2),
                'hora': horario_atual
            }
            
            print(f"🚨 [ALERTA] {category} detectado!")
            self.gerar_relatorio_detalhado(dados_ataque)
            socketio.emit('attack_alert', dados_ataque)

    def start_monitoring(self):
        print(f"🛰️ Vigilância Ativa em: {self.target_stream}")
        if not os.path.exists(self.target_stream):
            with open(self.target_stream, 'w') as f: f.write("")

        with open(self.target_stream, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                self.inspect_payload(line.strip())

@app.route('/')
def index():
    return render_template('index.html')

# Adicionei uma rota de teste para você verificar se os logs aparecem
@app.route('/test-attack')
def test_attack():
    with open("server_access.log", "a") as f:
        f.write("192.168.1.50 | <script>alert('HACK')</script> | Android-Phone | Mozilla | Server1\n")
    return "Ataque de teste enviado ao log!"

if __name__ == "__main__":
    waf = NeuralKoreWAF()
    waf.initialize_engine()
    
    monitor_thread = threading.Thread(target=waf.start_monitoring, daemon=True)
    monitor_thread.start()

    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
