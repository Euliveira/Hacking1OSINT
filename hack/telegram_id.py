#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import json
import sys
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyUnregisteredError,
    PeerIdInvalidError,
    UserNotParticipantError,
)
from telethon.tl.types import User

# ==============================================================================
# CONFIGURAÇÕES DA API (Obtenha em https://my.telegram.org)
# ==============================================================================
API_ID = input("coloque sua api_id: ")          # Insira seu API ID (int)
API_HASH = input("api_hash: ") # Insira sua API HASH (string)
SESSION_NAME = 'sessao_osint'


def serializar_dados(obj):
    """Converte objetos complexos ou datas para tipos nativos do JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


async def extrair_alvo(client: TelegramClient, alvo: str, salvar_json: bool = True):
    """Realiza a consulta da entidade via MTProto API e gera o relatório."""
    print(f"\n[*] Consultando entidade na rede Telegram: {alvo}...")

    # Se for ID numérico recebido como string, converte para int
    if alvo.replace('-', '').isdigit():
        alvo = int(alvo)

    try:
        entidade = await client.get_entity(alvo)

        if not isinstance(entidade, User):
            print(f"[!] A entidade tratada não é um usuário (tipo: {type(entidade).__name__}).")
            return

        # Montagem do relatório estruturado
        dados = {
            "timestamp_coleta": datetime.utcnow().isoformat() + "Z",
            "user_id": entidade.id,
            "first_name": entidade.first_name or "",
            "last_name": entidade.last_name or "",
            "username": f"@{entidade.username}" if entidade.username else None,
            "phone": f"+{entidade.phone}" if entidade.phone else None,
            "is_bot": entidade.bot,
            "is_verified": entidade.verified,
            "is_scam": entidade.scam,
            "is_fake": entidade.fake,
            "is_premium": getattr(entidade, 'premium', False),
            "access_hash": entidade.access_hash,
            "lang_code": getattr(entidade, 'lang_code', None),
            "restriction_reason": [
                {"platform": r.platform, "reason": r.reason, "text": r.text}
                for r in getattr(entidade, 'restriction_reason', [])
            ] if getattr(entidade, 'restriction_reason', None) else []
        }

        # Exibição formatada no terminal
        print("\n" + "=" * 60)
        print("          RELATÓRIO OSINT DE USUÁRIO - TELEGRAM")
        print("=" * 60)
        print(f" ID Numérico (Fixo) : {dados['user_id']}")
        print(f" Nome Completo     : {dados['first_name']} {dados['last_name']}".strip())
        print(f" Username          : {dados['username'] if dados['username'] else 'NÃO POSSUI USERNAME'}")
        print(f" Telefone Vinculado: {dados['phone'] if dados['phone'] else 'Oculto / Não visível'}")
        print(f" Conta de Bot?     : {'Sim' if dados['is_bot'] else 'Não'}")
        print(f" Sinalizado Scam?  : {'Sim' if dados['is_scam'] else 'Não'}")
        print(f" Sinalizado Fake?  : {'Sim' if dados['is_fake'] else 'Não'}")
        print(f" Access Hash       : {dados['access_hash']}")
        print("=" * 60)

        if not dados['username']:
            print("\n[ALERTA OSINT] O usuário não possui username configurado.")
            print(f"O identificador único e imutável para correlação é o ID: {dados['user_id']}")

        # Salva o resultado em arquivo JSON
        if salvar_json:
            filename = f"osint_telegram_{dados['user_id']}_{int(datetime.now().timestamp())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False, default=serializar_dados)
            print(f"\n[+] Relatório exportado com sucesso: {filename}")

    except PeerIdInvalidError:
        print("[X] Erro: O ID fornecido é inválido ou a conta não possui histórico/interação prévia com sua sessão.")
    except Exception as e:
        print(f"[X] Falha na extração de dados: {e}")


async def listar_dialogos(client: TelegramClient, limite: int = 20):
    """Lista as conversas recentes da conta para mapear IDs rápidos."""
    print(f"\n[*] Mapeando as últimas {limite} conversas ativas da sessão...\n")
    print(f"{'ID':<15} | {'TIPO':<10} | {'NOME / TÍTULO':<30} | {'USERNAME':<20}")
    print("-" * 80)

    async for dialog in client.iter_dialogs(limit=limite):
        entidade = dialog.entity
        tipo = "Usuário" if isinstance(entidade, User) else "Grupo/Canal"
        username = f"@{entidade.username}" if getattr(entidade, 'username', None) else "SEM USERNAME"
        print(f"{dialog.id:<15} | {tipo:<10} | {dialog.name[:28]:<30} | {username:<20}")
    print("-" * 80)


async def main():
    parser = argparse.ArgumentParser(description="Ferramenta de Coleta e Reconhecimento OSINT no Telegram (MTProto API)")
    parser.add_argument("-t", "--target", help="ID numérico, @username ou +Telefone do alvo")
    parser.add_argument("-l", "--list", action="store_true", help="Lista as conversas e IDs recentes")
    args = parser.parse_args()

    # Validação inicial de credenciais
    if API_ID == 1234567 or API_HASH == 'SUA_API_HASH':
        print("[X] Erro: Configure seu API_ID e API_HASH no início do script antes de executar.")
        sys.exit(1)

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        if args.list:
            await listar_dialogos(client)
        elif args.target:
            await extrair_alvo(client, args.target)
        else:
            # Modo interativo caso não passe argumentos via terminal
            print("\n--- MODO INTERATIVO DE PESQUISA ---")
            print("1. Extrair alvo específico (ID, Username ou Telefone)")
            print("2. Listar conversas recentes da conta (Pegar IDs)")
            print("3. Sair")
            opcao = input("\nSelecione uma opção [1-3]: ").strip()

            if opcao == '1':
                alvo = input("Insira o ID numérico, @username ou +Telefone: ").strip()
                if alvo:
                    await extrair_alvo(client, alvo)
            elif opcao == '2':
                await listar_dialogos(client)
            else:
                print("Saindo...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ApiIdInvalidError, AuthKeyUnregisteredError):
        print("[X] Erro de autenticação: Credenciais de API inválidas.")
    except KeyboardInterrupt:
        print("\n[!] Operação cancelada pelo usuário.")
