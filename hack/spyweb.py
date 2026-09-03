import re
import urllib.parse
from bs4 import BeautifulSoup
import requests


class OSINTTrackerPivot:

    def __init__(self, target_url):
        self.target_url = (
            target_url
            if target_url.startswith('http')
            else f'http://{target_url}'
        )
        self.domain = urllib.parse.urlparse(self.target_url).netloc
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        }
        self.found_trackers = {}

    def fetch_page_source(self):
        """Baixa o HTML do site alvo."""
        try:
            print(f'[*] Baixando código-fonte de: {self.target_url}...')
            response = requests.get(
                self.target_url, headers=self.headers, timeout=12
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f'[-] Erro ao acessar o site: {e}')
            return None

    def extract_trackers(self, html_content):
        """Extrai IDs de rastreamento usando Expressões Regulares (Regex)."""
        print('[*] Analisando o código-fonte em busca de tags e IDs...')

        patterns = {
            'Google Analytics (UA)': r'UA-\d+-\d+',
            'Google Analytics 4 (GA4)': r'G-[A-Z0-9]{8,12}',
            'Google AdSense': r'(?:ca-pub-|pub-)\d{16}',
            'Google Tag Manager (GTM)': r'GTM-[A-Z0-9]{5,10}',
            'Facebook Pixel': r'fbq\([\'"]init[\'"]\s*,\s*[\'"](\d{14,16})[\'"]\)',
            'Yandex Metrica': r'ym\(\s*(\d{7,9})\s*,',
            'Hotjar Site ID': r'hj\s*=\s*hj\s*\|\|\s*function\(\)\{;\s*hjsv\s*=\s*(\d{6,8})',
        }

        for tracker_type, pattern in patterns.items():
            matches = list(set(re.findall(pattern, html_content)))
            if matches:
                # Trata casos em que a regex captura grupos específicos
                cleaned_matches = [
                    m[0] if isinstance(m, tuple) else m for m in matches
                ]
                self.found_trackers[tracker_type] = cleaned_matches

        return self.found_trackers

    def pivot_publicwww(self, tracker_id):
        """Consulta o PublicWWW para encontrar outras páginas com a mesma tag."""
        print(f'\n[+] Realizando busca de pivoteamento no PublicWWW para: {tracker_id}')
        encoded_query = urllib.parse.quote(f'"{tracker_id}"')
        url = f'https://publicwww.com/websites/{encoded_query}/'

        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Extrai os domínios listados na tabela de resultados do PublicWWW
                links = soup.select('td.m-cell-site a[target="_blank"]')
                domains = list(set([link.text.strip() for link in links]))

                if domains:
                    print(
                        f'    [!] {len(domains)} sites associados encontrados:'
                    )
                    for d in domains[:15]:  # Exibe os 15 primeiros
                        print(f'        -> {d}')
                    if len(domains) > 15:
                        print(f'        ... e mais {len(domains) - 15} domínios.')
                else:
                    print('    [-] Nenhum site adicional indexado publicamente.')
            else:
                print(f'    [-] Status HTTP {res.status_code} ao consultar PublicWWW.')
        except requests.RequestException as e:
            print(f'    [-] Erro na consulta ao PublicWWW: {e}')

    def generate_spyonweb_link(self, tracker_id):
        """Gera o link direto do SpyOnWeb para investigação complementar."""
        # Limpa prefixos caso existam
        clean_id = tracker_id.replace('ca-pub-', 'pub-')
        return f'https://spyonweb.com/{clean_id}'


def main():
    print('=' * 65)
    print('    OSINT TRACKER & ANALYTICS PIVOT - INVESTIGAÇÃO DE AUTORIA    ')
    print('=' * 65)

    target = input('\n[+] Digite o domínio/URL alvo (ex: site-investigado.com): ').strip()
    if not target:
        print('[-] Nenhum alvo informado. Encerrando.')
        return

    investigator = OSINTTrackerPivot(target)
    html = investigator.fetch_page_source()

    if not html:
        return

    trackers = investigator.extract_trackers(html)

    if not trackers:
        print('\n[-] Nenhum ID de rastreamento conhecido foi encontrado no HTML.')
        return

    print('\n' + '=' * 50)
    print('         TAGS / IDs ENCONTRADOS NO SITE ALVO       ')
    print('=' * 50)
    
    for category, ids in trackers.items():
        print(f'► {category}:')
        for tracker_id in ids:
            print(f'  • {tracker_id}')

    print('\n' + '=' * 50)
    print('            INICIANDO PIVOTEAMENTO OSINT           ')
    print('=' * 50)

    for category, ids in trackers.items():
        for tracker_id in ids:
            investigator.pivot_publicwww(tracker_id)
            spyonweb_url = investigator.generate_spyonweb_link(tracker_id)
            print(f'    [Acesso Direto SpyOnWeb]: {spyonweb_url}')


if __name__ == '__main__':
    main()