import os
import subprocess
import sys

print("🚀 Iniciando NeuralKore-WAF...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

server_file = "neuralkore_server.py"

if os.path.exists(server_file):
    subprocess.run([sys.executable, server_file])
else:
    print(f"❌ Arquivo {server_file} não encontrado.")