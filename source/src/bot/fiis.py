from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from banco_dados import salvar_dados
from colorama import Fore, Style
import colorama
import json

colorama.init(autoreset=True)
option = Options()
option.headless = True


class Fiis:

    """
        Essa é uma classe para coleta de cadastro e coleta de dados no que diz respeito aos
        fundos de Investimento Imobiliário (FII).
    """

    def __init__(self, nome: str, **kwargs):
        self.nome = nome  # ticker
        self.valor_provento = kwargs.get('valor_provento')
        self.data_base = kwargs.get('data_base')
        self.data_pagamento = kwargs.get('data_pagamento')
        self.periodo_referencia = kwargs.get('periodo_referencia')
        self.cotacao = kwargs.get('cotacao')
        self.dividend_yield = kwargs.get('dividend_yield')

    def scraping_data(self, id_noticia: str, date_time: str) -> bool:

        """
            Função responsável por realizar o scraping (extração) de dados referente ao fundo analisado
            e atribuir os devidos valores aos respectivos atributos.

            Parameters:
                id_noticia (str): parâmetro de pesquisa padrão utilizado para request da notícia desejada no site B3.
                date_time (str): parâmetro de pesquisa padrão utilizado para request da notícia desejada no site B3.

            Returns:
                bool: 'True' for success or 'False' for fail.
        """

        # iniciando processo de extrairão das propriedades referentes aos FIIs
        with webdriver.Firefox(options=option) as browser:
            propriedade = Fiis.__propriedades_fiis(self, id_noticia, date_time, browser)
            print(propriedade)

            if propriedade is None:
                print(f"Não foi possível extrair propriedades referente ao FII {self.nome}")
                return False

            # iniciando processo de tratamento de dados
            Fiis.__extrair_valor_provento(self, propriedade)
            Fiis.__extrair_data_base(self, propriedade)
            Fiis.__extrair_data_pagamento_provento(self, propriedade)
            Fiis.__extrair_periodo_referencia(self)
            # com base nas propriedades inicia-se o processo para extrair a cotação refente ao fundo analisado
            Fiis.__extrair_cotacao(self, browser)
            # inicia o cálculo do dividend yield com base nos dados encontrados
            Fiis.calcular_dividend_yield(self)

            return True

    def verifica_atributos(self) -> bool:

        """
            Responsável por verificar todos os atributos se todos os atributos do objeto instanciado está
            inicializado com algum valor.

            Returns:
            bool: 'True' for success or 'False' for fail.
        """

        if self.valor_provento is None or self.data_base is None or self.data_pagamento is None \
                or self.periodo_referencia is None or self.cotacao is None or self.dividend_yield is None \
                or self.nome is None:
            return False
        else:
            return True

    def salvar_dados_fiis(self, database: str) -> bool:

        """
            Responsável por salvar os dados na base solicitada.

            Parameters:
                database (str): path para base de dados na qual deve-se salvar os dados.

            Returns:
                bool: 'True' for success or 'False' for fail.
        """

        # verificação dos atributos preenchidos pelo objeto
        if Fiis.verifica_atributos(self):
            # atribuindo valores às respectivas tabelas referents à base de dados
            tab_valores = (self.periodo_referencia, self.cotacao, self.valor_provento, self.dividend_yield)
            tab_datas = (self.nome, self.data_base, self.data_pagamento, self.periodo_referencia)

            # iniciando tentativa de salvamento
            try:
                salvar_dados(tab_datas, tab_valores, database)
                print(f"{Fore.GREEN}{Style.BRIGHT}Dados salvos com sucesso!")
                return True
            except:
                print(f"{Fore.RED}Erro! Falha ao salvar dados.")
                return False

        # caso tenha algum atributo do objeto instanciado não preenchido
        return False

    def __propriedades_fiis(self, id_noticia: str, date_time: str, browser: webdriver) -> list:

        """
            Função responsável por acessar e extrair tabela com as informações
            dos proventos pagos pelo fundo de investimento analisado.

            Parameters:
                id_noticia (str): credencial de url necessária para acessar a notícia e posteriormente a tabela
                  contendo as informações do provento
                date_time (str): credencial de url necessária para acessar a notícia e posteriormente a tabela
                  contendo as informações do provento
                browser (webdriver): webdriver de para realizar os requests necessários

            Returns:
            propriedades_fiis (list): lista com os dados coletados da tabela. São esses dados:
            valor provento, data base e data pagamento do provento.
        """

        print("\n--------------------------------------------------------------------------------------")
        print(f"\n{Style.BRIGHT}Nome: {self.nome}")

        try:
            # incia o processo de extração dos dados referentes aos FIIs analisados
            soup_link = Fiis.__solicitar_noticia_qualificada(self, id_noticia, date_time, browser)
            url_tabela = Fiis.__encontrar_id_url_tabela_propriedades_fiis(self, soup_link)
            soup_tabela = Fiis.__extrair_tabela(self, '/html/body/table[2]', url_tabela, browser)

            # armazena os dados extraídos e logo em seguida são retornados pela função
            propriedades_fiis = list(map(lambda span: span.find('span', class_='dado-valores'),
                                         list(soup_tabela.findAll('tr'))))

            print(f"{Fore.GREEN}(Propriedades FIIS ({self.nome}) extraídas)\n")

            return propriedades_fiis

        except():
            print(f"{Fore.RED}Erro de execução!!!")

    @staticmethod
    def lista_credenciais(periodo_inicial: str, periodo_final: str) -> list:

        """
            Função responsável por efetuar pesquisa retornando as credenciais das notícias
            responsáveis por direcionar acesso para as notícias desejadas e qualificadas.

            Podendo receber um fundo específico a ser analisado ou então não recebendo nenhum fundo específico e
            retornando todas as credenciais do periodo pesquisado.

            Parameters:
                periodo_inicial (str):
                periodo_final (str):

            Returns:
            lista_credenciais (list): lista com os dados coletados da tabela
        """

        try:

            # formatando data para utilizá-la na url de pesquisa
            data_final_format = f"{periodo_final.split('/')[2]}-" \
                                f"{periodo_final.split('/')[1]}-" \
                                f"{periodo_final.split('/')[0]}"

            data_inicial_format = f"{periodo_inicial.split('/')[2]}-" \
                                  f"{periodo_inicial.split('/')[1]}-" \
                                  f"{periodo_inicial.split('/')[0]}"

            with webdriver.Firefox(options=option) as browser:

                # iniciando request
                url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=' \
                      f'18&palavra=&dataInicial={data_inicial_format}&dataFinal={data_final_format}'

                print(f"{Fore.YELLOW}-> request: {Style.RESET_ALL}{url}")
                browser.get(url)

                # processando json retornado pelo request realizado anteriormente
                arquivo_json = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body")))
                html_arquivo_json = arquivo_json.get_attribute('outerHTML')
                soup_json = BeautifulSoup(html_arquivo_json, 'html.parser')

                # lista de dicionários, que possui credenciais para acessar notícias no site da b3
                list_dicionarios = json.loads(soup_json.text)

                # retornando lista com dados de acesso referente aos fundos imobiliários da b3
                return Fiis.encontrar_credenciais_noticia_qualificada(list_dicionarios)

        except:
            print(f"{Fore.RED}Erro! Pesquisa não pode ser solicitar.")

    @staticmethod
    def encontrar_credenciais_noticia_qualificada(list_dicionarios_noticia: dict) -> list:

        """
            Responsável por encontrar o 'id' e 'dateTime' referente às notícias encontradas.
            Filtra as notícias quem possuem os seguintes elementos: 'Aviso aos Cotistas', em sua estrutura, e
            seguido por '(N)' que se severe às Normas / Notas.

            Parameters:
                list_dicionarios_noticia (dict): lista com dicionários contendo credenciais de acessoas às notícias
                    presentes no site da b3

            Returns:
                lista_credenciais (list): lista com as credenciais das notícias dos fundos selecionados pela filtragem
        """

        try:

            identificador = "Aviso aos Cotistas"
            lista_credenciais = []

            # filtrando dicionário, que possui o tal identificador
            dicionarios_qualificados = (list(
                filter(lambda noticia: identificador in str(noticia['NwsMsg']['headline']) and 'N' in str(
                    noticia['NwsMsg']['headline'][-2]),
                       list_dicionarios_noticia)))

            if len(dicionarios_qualificados) == 0:
                print(f"{Fore.RED}Erro! Aviso as cotistas não encontrado")
                return []

            # adicionando credenciais desejadas dos 'dicionarios qualificados' em uma nova lista
            # tal lista contém variáveis responsáveis por realizar pesquisa refentes aos fundos analisados
            for index in range(len(dicionarios_qualificados)):
                # criando molde do dicionário padronizado que será retornado pela função
                credenciais = {"nome": None, "id": None, "date_time": None}

                # atribuindo valores as variáveis que serão adicionadas ao dicionário
                id_dicionarios_qualificados = dicionarios_qualificados[index]['NwsMsg']['id']
                datetime_dicionarios_qualificados = dicionarios_qualificados[index]['NwsMsg']['dateTime']
                nome_dicionarios_qualificados = f"{str(dicionarios_qualificados[index]['NwsMsg']['headline']).split('(')[1][0:4]}11"

                # adicionando os valores extraídos ao dicionário
                credenciais.update(nome=nome_dicionarios_qualificados,
                                   id=id_dicionarios_qualificados,
                                   date_time=datetime_dicionarios_qualificados)

                # adicionando dicionario a lista de dicionários que será retornado pela função
                lista_credenciais.append(credenciais)

            # retornando as credenciais encontradas
            return lista_credenciais

        except:
            print(f"{Fore.RED}Erro! Card qualificado não encontrado")

    def __solicitar_noticia_qualificada(self, id_noticia: str, date_time: str, browser: webdriver) -> BeautifulSoup:

        """
            Realiza o request da notícia referente ao FII analisado, com base nas credências informadas

            Parameters:
                id_noticia (str): parâmetro de url utilizado para realizar a pesquisa
                date_time (str): parâmetro de url utilizado para realizar a pesquisa
                browser (webdriver): webdriver responsável pelos requests necessários

            Returns:
                soup_link (BeautifulSoup): html da página solicitada
        """

        try:
            # iniciado request para a página da notícia parametrizada
            url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/' \
                  f'Detail?idNoticia={id_noticia}' \
                  f'&agencia=18&dataNoticia={date_time}'
            print(f"{Fore.YELLOW}-> request noticia qualificada ({self.nome}): {Style.RESET_ALL}{url}")
            browser.get(url)

            # selecionado o conteúdo html da pagina de notícia encontrada
            link = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "conteudoDetalhe")))
            html_link = link.get_attribute('outerHTML')
            soup_link = BeautifulSoup(html_link, 'html.parser')

            return soup_link

        except:
            print(f"{Fore.RED}Erro! Ao solicitar notícia qualificada.")

    def __encontrar_id_url_tabela_propriedades_fiis(self, soup_link: BeautifulSoup) -> str:

        """
            Encontra o 'id' de acesso, presente na página de notícia, para realizar a pesquisa pela
            tabela 'propriedades' referente ao FII analisado

            Parameters:
                soup_link (BeautifulSoup): html da página de notícia referente ao fundo analisado

            Returns:
                url_tabela (str): url, contendo 'id' encontrado, de acesso a tabela 'propriedades' referente
                ao FII analisado
        """

        try:

            # obtendo o 'id' de identificação da tabela
            id_tabela = (list(map(lambda ancora: str(ancora['href']).split('=')[1], list(soup_link.findAll('a'))))[0])

            url_tabela = 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=' + id_tabela + '&#toolbar=0'
            print(f"{Fore.YELLOW}-> url tabela notícia ({self.nome}): {Style.RESET_ALL}{url_tabela}")
            return url_tabela

        except:
            print(f"{Fore.RED}Erro! id tabela não encontrado")

    def __extrair_cotacao(self, browser: webdriver) -> None:

        """
            Extrai a cotação tomando como base a 'data base' referente ao fundo analisado

            Parameters:
                browser (webdriver): webdriver responsável pelos requests necessários

            Returns:
                None
        """

        try:
            print(f"{Style.BRIGHT}-- Capturando cotacao FIIS ({self.nome}) --")

            # definindo o dia se baseando na 'data_base'
            data = {'dia': self.data_base.split('/')[0],
                    'mes': self.data_base.split('/')[1],
                    'ano': self.data_base.split('/')[2]
                    }

            # função que retorna 'mes'/'ano' do mês anterior ao da data de execução do scraping
            data_pesquisa = f'{data.get("mes")}/{data.get("ano")}'

            # url de pesquisa
            url = f'https://bvmf.bmfbovespa.com.br/SIG/FormConsultaMercVista.asp?strTipoResumo=RES_MERC_VISTA' \
                  f'&strSocEmissora={self.nome}&strDtReferencia={data_pesquisa}&strIdioma=P&intCodNivel=2' \
                  f'&intCodCtrl=160 '

            print(f"{Fore.YELLOW}-> url: {Style.RESET_ALL}{url}")

            # realizando request e extraindo tabela para obter tabela com as cotações do FII pesquisado
            soup_tabela = Fiis.__extrair_tabela(self,
                                                '/html/body/table[3]/tbody/tr/td/table/tbody/tr/td/table[1]/tbody/tr[2]'
                                                '/td/table',
                                                url, browser)

            if soup_tabela is None:
                print(f"{Fore.RED}Erro! Tabela de Cotação não encontrada.")
                return None

            # percorre e armazena todas as linhas da tabela
            tag_trs = list(soup_tabela.find_all('tr'))
            num_linha = None

            # encontra a linha com as cotações da qual é referente a data base
            for linha in range(tag_trs.__len__()):
                lista_linha = tag_trs[linha].text.split('\n')
                if data.get('dia') in lista_linha[0]:
                    num_linha = linha

            if num_linha is None or len(
                    list(filter(lambda td: td.text in 'Resumo Diário', list(soup_tabela.find_all('td'))))) == 0:
                print(f"{Fore.RED}Erro! Cotação de fechamento referente a data base não encontrada.")
                return None

            # seleciona a cotação de fechamento referente a data base
            linha_fundo_desejado = tag_trs[num_linha].text.split('\n')
            print(linha_fundo_desejado[-2])

            string_cotacao = str((linha_fundo_desejado[-2]).replace('.', "")).replace(",", ".")
            cotacao_formatada = float(string_cotacao)

            self.cotacao = float(cotacao_formatada)

        except:
            print(f"{Fore.RED}Erro! Cotacao FIIs ({self.nome}) não pode ser extraída.")

    def __extrair_tabela(self, xpath: str, url: str, browser: webdriver) -> BeautifulSoup:

        """
            Extrai tabela de uma página web desejada

            Parameters:
                xpath (str): xpath referente ao caminho da tabela presente na página web
                url (str): url de acesso a página web
                browser (webdriver): webdriver responsável pelos requests necessários

            Returns:
                soup_tabela (BeautifulSoup): 'sopa' html da tabela encontrada
        """

        try:
            print(f"{Style.BRIGHT}-- Extraindo tabela referente FIIs ({self.nome}) --")

            # utilizando a url faz o requerimento da tabela
            print(url)
            browser.get(url)

            # a partir do 'xpath' encontra-se a tabela e logo em seguida é armazenada em uma variável
            tabela = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

            # extrai o html da tabela que logo em seguida é retornado pela função
            html_tabela = tabela.get_attribute('outerHTML')
            soup_tabela = BeautifulSoup(html_tabela, 'html.parser')

            if len(list(soup_tabela.find_all('table'))) == 0:
                print(f"{Fore.RED}Table not found")
                return BeautifulSoup()

            return soup_tabela

        except:
            print(f"{Fore.RED}Erro! Tabela FIIs ({self.nome}) não pode ser solicitada.")

    def calcular_dividend_yield(self) -> None:

        """
            Calcula o 'dividend_yield' do fundo analisado

            Returns:
                None
        """

        try:
            # formula para calcular 'dividend_yield'
            self.dividend_yield = (self.valor_provento / self.cotacao) * 100
        except:
            print(f"{Fore.RED}Erro! Não foi possível calcular o dividend yield ({self.nome})")

    def __extrair_valor_provento(self, dados_fiis: list) -> None:
        # extraindo 'valor do provento' da tabela retornada pela função 'propriedades_fiis'
        string_valor_provento = str(dados_fiis[5].get_text()).replace(".", "").replace(",", ".")
        # formatando-a para float
        self.valor_provento = float(string_valor_provento)

    def __extrair_data_base(self, dados_fiis: list) -> None:
        # extraindo 'data base' da tabela retornada pela função 'propriedades_fiis'
        self.data_base = (dados_fiis[3].get_text())

    def __extrair_data_pagamento_provento(self, dados_fiis: list) -> None:
        # capturando 'data pagamento' da sopa html
        self.data_pagamento = (dados_fiis[4].get_text())

    def __extrair_periodo_referencia(self) -> None:
        # extraindo a 'data referencia' utilizando a 'data base' como referencia
        data_referencia = self.data_base.split('/')
        # 'periodo_referencia' é a chave primaria do banco de dados
        self.periodo_referencia = f"{self.nome}.{data_referencia[2]}.{data_referencia[1]}"
