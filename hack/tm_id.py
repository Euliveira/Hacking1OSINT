import os
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError, UsernameInvalidError, UsernameNotOccupiedError

# ==============================================================================
# CONFIGURAÇÕES DA API DO TELEGRAM (Obtenha em https://my.telegram.org)
# ==============================================================================
API_ID =  # Substitua pelo seu API_ID (inteiro)
API_HASH = ".."  # Substitua pelo seu API_HASH (string)
SESSION_NAME = "sessao_investigacao"


async def investigar_alvo(client: TelegramClient, alvo: str):
    """Consulta os metadados e obtém o ID do alvo no Telegram."""
    alvo_limpo = alvo.strip()

    print("\n" + "=" * 55)
    print(f"[*] COLETANDO DADOS DO ALVO: {alvo_limpo}")
    print("=" * 55)

    try:
        # Resolve o objeto no Telegram (Usuário, Canal, Grupo ou Bot)
        entity = await client.get_entity(alvo_limpo)

        print(f"  [+] ID do Telegram : {entity.id}")
        print(f"  [+] Tipo de Entidade: {type(entity).__name__}")

        # Caso a entidade seja um Usuário/Bot
        if hasattr(entity, "first_name"):
            nome = entity.first_name or ""
            sobrenome = entity.last_name or ""
            nome_completo = f"{nome} {sobrenome}".strip()

            print(f"  [+] Nome Registrado : {nome_completo}")
            print(
                f"  [+] Username        : @{entity.username}"
                if entity.username
                else "  [+] Username        : Sem username público"
            )
            print(
                f"  [+] Telefone        : +{entity.phone}"
                if hasattr(entity, "phone") and entity.phone
                else "  [+] Telefone        : Oculto/Privado"
            )
            print(
                f"  [+] É Conta de Bot  : {'Sim' if getattr(entity, 'bot', False) else 'Não'}"
            )
            print(
                f"  [+] Restrito/Ban    : {'Sim' if getattr(entity, 'restricted', False) else 'Não'}"
            )

        # Caso a entidade seja um Canal ou Grupo
        elif hasattr(entity, "title"):
            print(f"  [+] Título do Grupo/Canal: {entity.title}")
            print(
                f"  [+] Username             : @{entity.username}"
                if entity.username
                else "  [+] Username             : Privado / Sem Link Direto"
            )
            print(
                f"  [+] É Supergrupo        : {'Sim' if getattr(entity, 'megagroup', False) else 'Não'}"
            )
            print(
                f"  [+] É Canal Transmissão : {'Sim' if getattr(entity, 'broadcast', False) else 'Não'}"
            )

    except (UsernameInvalidError, UsernameNotOccupiedError, ValueError):
        print(
            f"  [-] Erro: O alvo '{alvo_limpo}' não foi localizado ou não existe."
        )
    except RPCError as e:
        print(f"  [-] Erro de Comunicação com a API: {e}")
    except Exception as e:
        print(f"  [-] Erro Inesperado: {e}")


async def main():
    print("=" * 55)
    print("      FERRAMENTA OSINT - OBTENÇÃO DE ID NO TELEGRAM      ")
    print("=" * 55)

    # Validação simples de credenciais
    if (
        API_ID == 12345678
        or API_HASH == "SUA_API_HASH_AQUI"
        or not API_ID
        or not API_HASH
    ):
        print(
            "\n[-] ERRO: Configure seu API_ID e API_HASH válidos nas variáveis do código!"
        )
        return

    # O Context Manager 'async with' garante a abertura/fechamento seguro do arquivo SQLite
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        # Garante a autenticação caso a sessão seja nova
        if not await client.is_user_authorized():
            print("\n[*] Primeira execução detectada. Iniciando login...")
            await client.start()

        alvo_input = input(
            "\nDigite o @username, ID numérico ou link de convite: "
        ).strip()

        if not alvo_input:
            print("[-] Nenhum alvo fornecido. Encerrando execução.")
            return

        await investigar_alvo(client, alvo_input)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except TypeError as e:
        # Tratamento automático de exceção caso o banco de sessão corrompa novamente
        if "NoneType" in str(e):
            sess_file = f"{SESSION_NAME}.session"
            if os.path.exists(sess_file):
                os.remove(sess_file)
                print(
                    f"\n[!] A sessão '{sess_file}' estava corrompida e foi removida automaticamente."
                )
                print(
                    "[!] Execute o script novamente para realizar o login e criar uma nova sessão."
                )
        else:
            raise e
