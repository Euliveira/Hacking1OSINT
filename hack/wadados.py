import sys
import requests

# Sua Chave de API gerada na InfoSimples
TOKEN_INFOSIMPLES = "..."

class InvestigacaoDigital:
    def __init__(self):
        self.token = TOKEN_INFOSIMPLES
        # Alterado para o endpoint unificado de busca cadastral por telefone da InfoSimples
        self.url_telefone = "https://api.infosimples.com/api/v1/consultas/telecom/telefone"
        self.url_receita = "https://api.infosimples.com/api/v1/consultas/receita-federal/cpf"

    def limpar_telefone(self, telefone: str) -> str:
        """Remove parênteses, espaços e traços, deixando apenas números."""
        return "".join(filter(str.isdigit, telefone))

    def executar_busca(self, telefone_input: str):
        """Executa a busca em duas etapas: Telefone -> CPF -> Endereço/Dados"""
        telefone_limpo = self.limpar_telefone(telefone_input)

        if len(telefone_limpo) < 10:
            print("[!] ERRO: O número de telefone inserido é inválido ou está incompleto.")
            return

        print(f"[*] Alvo: {telefone_limpo}")
        print("[*] Passo 1: Cruzando linha telefônica com base cadastral para extrair CPF...")

        # --- CONSULTA 1: TELEFONE PARA CPF ---
        params_fone = {
            "token": self.token,
            "telefone": telefone_limpo
        }

        try:
            resposta_fone = requests.get(self.url_telefone, params=params_fone, timeout=20)
            json_fone = resposta_fone.json()

            if json_fone.get("code") != 200 or not json_fone.get("data"):
                print("[!] FALHA: Não foi possível mapear um CPF vinculado a este WhatsApp nas bases públicas/operadoras.")
                print(f"[DEBUG] Resposta Bruta da API: {json_fone}")
                return

            # Extrai os dados iniciais do alvo
            dados_fone = json_fone["data"][0]
            cpf_alvo = dados_fone.get("cpf")
            nome_alvo = dados_fone.get("nome")

            print(f"[+] SUCESSO: Vínculo encontrado!")
            print(f"    ├── Nome: {nome_alvo}")
            print(f"    └── CPF:  {cpf_alvo}")
            print("[*] Passo 2: Consultando situação na Receita Federal para extrair endereço detalhado e CNPJ...")

            # --- CONSULTA 2: ENRIQUECIMENTO COMPLETO VIA CPF ---
            params_receita = {
                "token": self.token,
                "cpf": cpf_alvo
            }

            resposta_receita = requests.get(self.url_receita, params=params_receita, timeout=20)
            json_receita = resposta_receita.json()

            if json_receita.get("code") != 200 or not json_receita.get("data"):
                print("[!] AVISO: CPF localizado, mas a consulta detalhada de endereço na Receita falhou ou está instável.")
                return

            dados_finais = json_receita["data"][0]

            # --- FORMATAÇÃO DOS DADOS PARA O RELATÓRIO JURÍDICO ---
            self.imprimir_relatorio_final(nome_alvo, cpf_alvo, dados_finais)

        except requests.exceptions.RequestException as e:
            print(f"[!] ERRO DE CONEXÃO: Não foi possível comunicar com a API. Detalhes: {e}")

    def imprimir_relatorio_final(self, nome, cpf, dados):
        print("\n" + "="*70)
        print("          DOSSIÊ DE QUALIFICAÇÃO E LOCALIZAÇÃO CIVIL (OSINT)          ")
        print("="*70)
        print(f" [+] QUALIFICAÇÃO DO ALVO:")
        print(f"  ├── NOME COMPLETO: {nome}")
        print(f"  ├── CPF DO TITULAR: {cpf}  <-- [CONFERIDO]")
        print(f"  └── DATA NASCIMENTO: {dados.get('data_nascimento', 'Não informada')}")

        # Tratamento rigoroso do Endereço (Exigência dos Advogados)
        endereco = dados.get("endereco", {})
        if endereco:
            logradouro = endereco.get("logradouro", "Não localizado")
            numero = endereco.get("numero", "S/N")
            complemento = endereco.get("complemento", "")
            bairro = endereco.get("bairro", "Não localizado")
            cidade = endereco.get("cidade", "Não localizada")
            uf = endereco.get("uf", "UF")
            cep = endereco.get("cep", "Não localizado")

            str_comp = f" - {complemento}" if complemento else ""

            print(f"\n [+] ENDEREÇO DE CITAÇÃO ENCONTRADO:")
            print(f"  ├── LOGRADOURO: {logradouro}, Nº {numero}{str_comp}")
            print(f"  ├── BAIRRO:     {bairro}")
            print(f"  ├── CIDADE/UF:  {cidade} - {uf}")
            print(f"  └── CEP:        {cep}")
            print(f"  [➔] PRONTO PARA PETIÇÃO: {logradouro}, Nº {numero}{str_comp}, Bairro {bairro}, {cidade}-{uf}, CEP: {cep}")
        else:
            print(f"\n [!] ENDEREÇO: Nenhum endereço residencial estruturado foi retornado no espelho deste CPF.")

        # Tratamento de Vínculos de Empresa (CNPJ)
        empresas = dados.get("participacoes_societarias", []) or dados.get("empresas_vinculadas", [])
        if empresas:
            print(f"\n [+] PARTICIPAÇÃO EM EMPRESAS DETECTADA (Pessoa Jurídica):")
            for emp in empresas:
                print(f"  ├── RAZÃO SOCIAL: {emp.get('razao_social', 'N/A')}")
                print(f"  └── CNPJ:         {emp.get('cnpj', 'N/A')} ({emp.get('situacao', 'ATIVA')})")
        else:
            print(f"\n [i] EMPRESAS: Não foram localizados CNPJs ou MEI vinculados a este CPF.")

        print("="*70 + "\n")

# Inicialização do Script
if __name__ == "__main__":
    investigador = InvestigacaoDigital()

    # Execução interativa no terminal
    if len(sys.argv) > 1:
        alvo_input = sys.argv[1]
    else:
        alvo_input = input("Digite o número do WhatsApp (com DDD): ")

    investigador.executar_busca(alvo_input)
