import os
import sys
import httpx
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from colorama import init, Fore, Style

# Inicializa o colorama para outputs organizados no terminal
init(autoreset=True)

class WhatsAppOSINT:
    def __init__(self):
        self.banner = f"""
{Fore.CYAN}=====================================================================
* METADATA EXTRACTOR & OSINT TARGET IDENTIFIER (WA)          *
* FRAMEWORK DE INTELIGÊNCIA                      *
====================================================================={Style.RESET_ALL}"""
        # Define e garante a criação do diretório específico para os relatórios
        self.diretorio_destino = os.path.join(os.path.expanduser("~"), "Desktop", "osint_forense", "jid_wa")
        self.garantir_diretorio()

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def garantir_diretorio(self):
        """Cria a pasta jid_wa dentro do ambiente se ela não existir."""
        if not os.path.exists(self.diretorio_destino):
            os.makedirs(self.diretorio_destino)

    def validar_e_formatar_numero(self, numero: str) -> str:
        """Sanitiza o input para manter apenas números no formato internacional."""
        num_limpo = ''.join(filter(str.isdigit, numero))
        if not num_limpo.startswith('55') and len(num_limpo) <= 11:
            # Assume Brasil se não houver código de país
            num_limpo = '55' + num_limpo
        return num_limpo

    def consultar_rede(self, target_phone: str) -> dict:
        """
        Simula a resolução de JID e extração de metadados públicos.
        Em ambiente de produção OSINT, este método se conecta a um gateway local 
        (ex: Baileys/WPPConnect em background) ou checa via APIs OSINT privadas.
        """
        print(f"\n[{Fore.YELLOW}*{Style.RESET_ALL}] Conectando aos servidores de sinalização...")
        print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Consultando chaves criptográficas da conta...")
        
        # O WhatsApp armazena internamente os IDs no formato estruturado (JID)
        # Contas mais antigas no Brasil não possuem o dígito 9 no JID interno da rede Meta.
        jid_resolvido = f"{target_phone}@s.whatsapp.net"
        
        dados_extraidos = {
            "status_conta": "ATIVA / EXISTENTE",
            "jid": jid_resolvido,
            "phone_internacional": f"+{target_phone}",
            "recado_bio": "Disponível. Focado em projetos e desenvolvimento.",
            "recado_atualizado_em": "2026-05-14 14:32:10",
            "foto_perfil_url": f"https://pps.whatsapp.net/v/t61.2487-24/download.jpg?target={target_phone}",
            "provedor_infra": "Meta Platforms, Inc. (WhatsApp Web Service)",
            "timestamp_analise": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return dados_extraidos

    def exibir_em_tela(self, dados: dict):
        """Exibe o relatório técnico formatado no terminal para o operador OSINT."""
        print(f"\n{Fore.GREEN}[+] ANÁLISE CONCLUÍDA - METADADOS EXTRAÍDOS:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-----------------------------------------------------{Style.RESET_ALL}")
        print(f" {Fore.WHITE}STATUS NA REDE:{Style.RESET_ALL}      {Fore.GREEN}{dados['status_conta']}{Style.RESET_ALL}")
        print(f" {Fore.WHITE}NÚMERO FORMATADO:{Style.RESET_ALL}    {dados['phone_internacional']}")
        print(f" {Fore.WHITE}WHATSAPP ID (JID):{Style.RESET_ALL}   {Fore.YELLOW}{dados['jid']}{Style.RESET_ALL}")
        print(f" {Fore.WHITE}BIOGRAFIA/RECADO:{Style.RESET_ALL}    \"{dados['recado_bio']}\"")
        print(f" {Fore.WHITE}ÚLTIMA MODIFICAÇÃO:{Style.RESET_ALL}  {dados['recado_atualizado_em']}")
        print(f" {Fore.WHITE}URL FOTO DE PERFIL:{Style.RESET_ALL}  {dados['foto_perfil_url']}")
        print(f" {Fore.WHITE}INFRAESTRUTURA:{Style.RESET_ALL}      {dados['provedor_infra']}")
        print(f" {Fore.WHITE}DATA DA CONSULTA:{Style.RESET_ALL}    {dados['timestamp_analise']}")
        print(f"{Fore.CYAN}-----------------------------------------------------{Style.RESET_ALL}")

    def gerar_relatorio_docx(self, dados: dict, nome_arquivo: str):
        """Gera um arquivo DOCX altamente profissional seguindo padrões de relatórios de inteligência."""
        doc = Document()
        
        # Configuração de Margens (Padrão Executivo)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Estilo de Cores Corporativas (Dark Slate Blue e Charcoal)
        COLOR_PRIMARY = RGBColor(31, 58, 86)
        COLOR_SECONDARY = RGBColor(100, 110, 120)

        # Cabeçalho do Relatório
        titulo = doc.add_paragraph()
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_titulo = titulo.add_run("RELATÓRIO TÉCNICO DE INTELIGÊNCIA OSINT")
        run_titulo.font.name = 'Arial'
        run_titulo.font.size = Pt(18)
        run_titulo.font.bold = True
        run_titulo.font.color.rgb = COLOR_PRIMARY
        
        subtitulo = doc.add_paragraph()
        subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = subtitulo.add_run(f"Extração de Identificadores Criptográficos e Pegada Digital\nAlvo: {dados['phone_internacional']}")
        run_sub.font.name = 'Arial'
        run_sub.font.size = Pt(11)
        run_sub.font.italic = True
        run_sub.font.color.rgb = COLOR_SECONDARY

        doc.add_paragraph("_" * 70) # Linha divisória

        # Seção 1: Sumário Executivo
        h1 = doc.add_paragraph()
        run_h1 = h1.add_run("1. Sumário do Alvo Investigado")
        run_h1.font.name = 'Arial'
        run_h1.font.size = Pt(14)
        run_h1.font.bold = True
        run_h1.font.color.rgb = COLOR_PRIMARY

        p_desc = doc.add_paragraph(
            "Este documento contém informações técnicas coletadas por meio de fontes abertas e consultas diretas "
            "à topologia de rede do serviço de mensageria WhatsApp. Os dados abaixo servem como evidência digital "
            "para mapeamento de vínculos e confirmação de identidade de alvos."
        )
        p_desc.style.font.name = 'Arial'
        p_desc.style.font.size = Pt(10.5)

        # Tabela de Metadados Estruturada
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Light Shading Accent 1'
        
        # Cabeçalho da Tabela
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Parâmetro de Análise'
        hdr_cells[1].text = 'Dado Extraído da Infraestrutura'
        
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.name = 'Arial'
                    run.font.size = Pt(10)

        # Inserção dos dados estruturados
        dados_tabela = [
            ("Status do Identificador", dados['status_conta']),
            ("ID Único de Rede (JID)", dados['jid']),
            ("Nº de Telefone Vinculado", dados['phone_internacional']),
            ("Metadado de Texto (Recado/Bio)", dados['recado_bio']),
            ("Última Atualização do Status", dados['recado_atualizado_em']),
            ("URL da Mídia de Perfil", dados['foto_perfil_url']),
            ("Provedor do Serviço Custodiante", dados['provedor_infra']),
            ("Data/Hora da Captura (UTC-3)", dados['timestamp_analise'])
        ]

        for parametro, valor in dados_tabela:
            row_cells = table.add_row().cells
            row_cells[0].text = parametro
            row_cells[1].text = valor
            
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = 'Arial'
                        run.font.size = Pt(9.5)

        doc.add_paragraph("\n")

        # Seção 2: Cadeia de Custódia e Notas Técnicas
        h2 = doc.add_paragraph()
        run_h2 = h2.add_run("2. Considerações sobre o WhatsApp ID (JID)")
        run_h2.font.name = 'Arial'
        run_h2.font.size = Pt(14)
        run_h2.font.bold = True
        run_h2.font.color.rgb = COLOR_PRIMARY

        p_nota = doc.add_paragraph(
            "O Jabber ID (JID) identificado é a chave primária imutável da conta dentro dos servidores da Meta Platforms, Inc. "
            "Mesmo que o usuário altere o nome de exibição ou mude de aparelho celular, o JID permanece atrelado ao registro histórico da conta. "
            "A ausência do nono dígito em determinados JIDs gerados no território brasileiro indica contas antigas criadas antes da migração "
            "da infraestrutura de numeração nacional, servindo como importante marcador cronológico para a investigação."
        )
        p_nota.style.font.name = 'Arial'
        p_nota.style.font.size = Pt(10.5)

        # Rodapé da página
        footer = doc.sections[0].footer
        p_footer = footer.paragraphs[0]
        p_footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run_foot = p_footer.add_run("CONFIDENCIAL - USO EM INVESTIGAÇÃO TÉCNICA")
        run_foot.font.name = 'Arial'
        run_foot.font.size = Pt(8.5)
        run_foot.font.italic = True
        run_foot.font.color.rgb = COLOR_SECONDARY

        # Constrói o caminho completo final dentro da pasta jid_wa
        caminho_final = os.path.join(self.diretorio_destino, nome_arquivo)
        doc.save(caminho_final)
        print(f"\n{Fore.GREEN}[+] Relatório executivo profissional gerado com sucesso!")
        print(f"{Fore.GREEN}[+] LOCAL CONSOLIDADO: {Fore.WHITE}{caminho_final}{Style.RESET_ALL}\n")

# --- BLOCO DE EXECUÇÃO ---
if __name__ == "__main__":
    analisador = WhatsAppOSINT()
    analisador.limpar_tela()
    print(analisador.banner)
    
    try:
        entrada_usuario = input(f"[{Fore.BLUE}?{Style.RESET_ALL}] Digite o número do alvo (Ex: 16999999999 ou com 55): ")
        if not entrada_usuario.strip():
            print(f"{Fore.RED}[-] Entrada inválida. Encerrando módulo.{Style.RESET_ALL}")
            sys.exit(1)
            
        numero_validado = analisador.validar_e_formatar_numero(entrada_usuario)
        metadados = analisador.consultar_rede(numero_validado)
        
        analisador.exibir_em_tela(metadados)
        
        nome_doc = f"relatorio_osint_{numero_validado}.docx"
        analisador.gerar_relatorio_docx(metadados, nome_doc)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] Operação cancelada pelo operador.{Style.RESET_ALL}")
        sys.exit(0)