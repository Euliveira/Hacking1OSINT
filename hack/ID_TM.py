from telethon import TelegramClient
import asyncio

# Insira suas credenciais fixas diretamente aqui
API_ID = input("Cole sua api_id: ")                 # Coloque seu número de API ID (sem aspas)
API_HASH = input("Cole sua api_hash: ")    # Coloque seu API Hash entre as aspas

async def main():
    # Inicializa a sessão (na primeira execução, pedirá seu telefone e o código enviado ao seu Telegram)
    client = TelegramClient('sessao_investigacao', API_ID, API_HASH)
    await client.start()
    
    username = input("\nDigite o username do alvo (com ou sem @): ").strip()
    if username.startswith('@'):
        username = username[1:]
        
    try:
        # O método get_entity faz a busca direta na rede do Telegram pelo username
        entidade = await client.get_entity(username)
        
        print("\n" + "="*40)
        print("ALVO LOCALIZADO COM SUCESSO")
        print("="*40)
        print(f"Chat ID Fixo: {entidade.id}")
        print(f"Nome no Perfil: {entidade.first_name} {entidade.last_name or ''}")
        print(f"Username atual: @{entidade.username}")
        print(f"Restrito pelo Telegram: {entidade.restricted}")
        print("="*40)
        
    except Exception as e:
        print(f"\n[!] Erro ao buscar o usuário: {e}")
        print("Verifique se o username está correto ou se a conta foi deletada.")

# Executa o script
asyncio.run(main())
