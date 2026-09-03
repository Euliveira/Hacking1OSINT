# -*- coding: utf-8 -*-
import asyncio
import json
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyUnregisteredError,
    PeerIdInvalidError,
)
from telethon.tl.types import User

# ==============================================================================
# CONFIGURAÇÕES DA API (Insira suas credenciais aqui)
# ==============================================================================
API_ID = input("SUA API_ID: ")
API_HASH = input("SEU API_HASH: ")
SESSION_NAME = "sessao_osint_gui"


def serializar_dados(obj):
  if isinstance(obj, datetime):
    return obj.isoformat()
  return str(obj)


class TelegramOSINTApp:

  def __init__(self, root):
    self.root = root
    self.root.title("OSINT Telegram - Painel de Consulta de IDs")
    self.root.geometry("750x600")
    self.root.minsize(650, 500)

    # Estilização visual moderna
    self.style = ttk.Style()
    self.style.theme_use("clam")

    # Configuração de Cores e Fontes
    bg_color = "#f4f6f9"
    self.root.configure(bg=bg_color)

    # --- TÍTULO DO PAINEL ---
    titulo_lbl = tk.Label(
        root,
        text="Painel Investigativo OSINT - Telegram",
        font=("Arial", 14, "bold"),
        bg=bg_color,
        fg="#333333",
    )
    titulo_lbl.pack(pady=10)

    # --- FRAME DE ENTRADA ---
    input_frame = ttk.LabelFrame(
        root, text=" Parâmetros de Consulta ", padding=15
    )
    input_frame.pack(fill="x", padx=15, pady=5)

    lbl_alvo = ttk.Label(
        input_frame, text="Alvo (ID Numérico, @username ou Telefone):"
    )
    lbl_alvo.pack(anchor="w", pady=2)

    self.entry_alvo = ttk.Entry(input_frame, font=("Arial", 11))
    self.entry_alvo.pack(fill="x", pady=5, ipady=3)

    # --- BOTÕES DE AÇÃO ---
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="x", padx=15, pady=10)

    self.btn_consultar = ttk.Button(
        btn_frame, text="🔍 Consultar Alvo", command=self.executar_consulta
    )
    self.btn_consultar.pack(side="left", expand=True, fill="x", padx=2)

    self.btn_listar = ttk.Button(
        btn_frame,
        text="📋 Listar Conversas Recentes",
        command=self.executar_listagem,
    )
    self.btn_listar.pack(side="left", expand=True, fill="x", padx=2)

    self.btn_limpar = ttk.Button(
        btn_frame, text="🧹 Limpar Tela", command=self.limpar_tela
    )
    self.btn_limpar.pack(side="left", expand=True, fill="x", padx=2)

    # --- ÁREA DE LOGS E RELATÓRIO ---
    output_frame = ttk.LabelFrame(root, text=" Relatório e Logs de Saída ", padding=10)
    output_frame.pack(fill="both", expand=True, padx=15, pady=5)

    self.txt_output = scrolledtext.ScrolledText(
        output_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#1e1e1e",
        fg="#00ffcc",
        insertbackground="white",
    )
    self.txt_output.pack(fill="both", expand=True)

    self.log(
        "[INFO] Sistema pronto. Insira um ID ou Username e clique em"
        " Consultar."
    )

  def log(self, mensagem):
    """Escreve mensagens na caixa de texto formatada."""
    self.txt_output.insert(tk.END, mensagem + "\n")
    self.txt_output.see(tk.END)

  def limpar_tela(self):
    self.txt_output.delete("1.0", tk.END)

  def executar_consulta(self):
    alvo = self.entry_alvo.get().strip()
    if not alvo:
      messagebox.showwarning(
          "Aviso", "Por favor, insira um ID ou username válido."
      )
      return
    # Roda a tarefa assíncrona em background para não travar a interface gráfica
    threading.Thread(target=lambda: asyncio.run(self._task_consultar(alvo))).start()

  def executar_listagem(self):
    threading.Thread(
        target=lambda: asyncio.run(self._task_listar_dialogos())
    ).start()

  async def _task_consultar(self, alvo):
    self.log(f"\n[*] Conectando ao Telegram para consultar: {alvo}...")
    if alvo.replace("-", "").isdigit():
      alvo = int(alvo)

    try:
      async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        entidade = await client.get_entity(alvo)

        if not isinstance(entidade, User):
          self.log(
              f"[!] A entidade não é um usuário (Tipo: {type(entidade).__name__})."
          )
          return

        dados = {
            "timestamp_coleta": datetime.utcnow().isoformat() + "Z",
            "user_id": entidade.id,
            "first_name": entidade.first_name or "",
            "last_name": entidade.last_name or "",
            "username": f"@{entidade.username}" if entidade.username else None,
            "phone": f"+{entidade.phone}" if entidade.phone else None,
            "is_bot": entidade.bot,
            "is_scam": entidade.scam,
            "is_fake": entidade.fake,
            "access_hash": entidade.access_hash,
        }

        # Exibição bonita no painel
        self.log("=" * 50)
        self.log("         RELATÓRIO OSINT DE USUÁRIO")
        self.log("=" * 50)
        self.log(f" ID Numérico (Fixo) : {dados['user_id']}")
        self.log(
            f" Nome Completo     : {dados['first_name']}"
            f" {dados['last_name']}".strip()
        )
        self.log(
            f" Username          :"
            f" {dados['username'] if dados['username'] else 'NÃO POSSUI'}"
        )
        self.log(
            f" Telefone Vinculado: {dados['phone'] if dados['phone'] else 'Oculto'}"
        )
        self.log(f" Sinalizado Scam?  : {'Sim' if dados['is_scam'] else 'Não'}")
        self.log(f" Access Hash       : {dados['access_hash']}")
        self.log("=" * 50)

        # Salva o JSON automaticamente
        filename = f"osint_{dados['user_id']}.json"
        with open(filename, "w", encoding="utf-8") as f:
          json.dump(dados, f, indent=4, ensure_ascii=False, default=serializar_dados)
        self.log(f"[+] Relatório exportado com sucesso para: {filename}\n")

    except PeerIdInvalidError:
      self.log(
          "[X] Erro: ID inválido ou conta sem histórico prévio com sua sessão."
      )
    except Exception as e:
      self.log(f"[X] Falha na consulta: {e}")

  async def _task_listar_dialogos(self):
    self.log("\n[*] Mapeando conversas recentes...")
    try:
      async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        self.log(f"{'ID':<15} | {'NOME / TÍTULO':<25} | {'USERNAME':<15}")
        self.log("-" * 60)
        async for dialog in client.iter_dialogs(limit=15):
          entidade = dialog.entity
          uname = (
              f"@{entidade.username}"
              if getattr(entidade, "username", None)
              else "SEM USER"
          )
          self.log(f"{dialog.id:<15} | {dialog.name[:23]:<25} | {uname:<15}")
        self.log("-" * 60)
        self.log("[+] Listagem concluída.\n")
    except Exception as e:
      self.log(f"[X] Erro ao listar diálogos: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = TelegramOSINTApp(root)
  root.mainloop()
