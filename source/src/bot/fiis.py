from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import colorama
from colorama import Fore, Style
from banco_dados import salvar_dados
import json

colorama.init(autoreset=True)
option = Options()
option.headless = True


class Fii:

    def __init__(self, nome, **kwargs):
        self.nome = nome
        self.valor_provento = kwargs.get('valor_provento')
        self.data_base = kwargs.get('data_base')
        self.data_pagamento = kwargs.get('data_pagamento')
        self.periodo_referencia = kwargs.get('periodo_referencia')
        self.cotacao = kwargs.get('cotacao')
        self.dividend_yield = kwargs.get('dividend_yield')

    def scraping_all(self, periodo_inicial, periodo_final, ):
        # responsável por realizar o scraping e atribuir os devidos valores aos respectivos atributos
        with webdriver.Firefox(options=option) as browser:
            propriedade = Fii.__propriedades_fiis(self, periodo_inicial, periodo_final, browser)

            if propriedade is None:
                print(f"Não foi possível extrair propriedades referente ao FII {self.nome}")
                return False

            Fii.__extrair_valor_provento(self, propriedade)
            Fii.__extrair_data_base(self, propriedade)
            Fii.__extrair_data_pagamento_provento(self, propriedade)
            Fii.__extrair_periodo_referencia(self)
            Fii.__extrair_cotacao(self, browser)
            Fii.calcular_dividend_yield(self)
            return True

    def verifica_atributos(self):
        # responsável por verificar todos os atributos se todos os atributos do objeto está inicializado com algum valor
        if self.valor_provento is None or self.data_base is None or self.data_pagamento is None \
                or self.periodo_referencia is None or self.cotacao is None or self.dividend_yield is None \
                or self.nome is None:
            return False
        else:
            return True

    def salvar_dados_fiis(self, database):
        # salva os dados na base de dados
        # antes de realizar o salvamento é realizado uma verificação dos atributos referente ao fii
        # em caso de ausência de algum atributo retorna-se 'False' (erro) e o salvamento não é realizado
        if Fii.verifica_atributos(self):
            tab_valores = (self.periodo_referencia, self.cotacao, self.valor_provento, self.dividend_yield)
            tab_datas = (self.nome, self.data_base, self.data_pagamento, self.periodo_referencia)

            # tentativa de salvar dados
            # caso haja falha retorna-se 'False' (erro)
            try:
                salvar_dados(tab_datas, tab_valores, database)
                print(f"{Fore.GREEN}{Style.BRIGHT}Dados salvos com sucesso!")
                # em caso de sucesso em todas as operações a função retorna 'True' (sucesso)
                return True
            except:
                print(f"{Fore.RED}Erro! Falha ao salvar dados.")
                return False

        # condição onde há ausência de atributos referente ao fii analisado retornando 'False' (erro)
        elif not Fii.verifica_atributos(self):
            print(f"{Fore.RED}Erro! Atributos não preenchidos.")
            return False

    def __propriedades_fiis(self, periodo_inicial, periodo_final, browser):

        print("\n--------------------------------------------------------------------------------------")
        print(f"\n{Style.BRIGHT}Nome: {self.nome}")

        try:
            # incia o caminho da extração dos dados referentes aos FIIs analisados
            list_dicionarios_noticia = Fii.__efetuar_pesquisa(self, periodo_inicial, periodo_final, browser)
            credenciais_noticia = Fii.__encontrar_credenciais_noticia_qualificada(self, list_dicionarios_noticia)

            soup_link = Fii.__solicitar_noticia_qualificada(self, credenciais_noticia, browser)
            url_tabela = Fii.__encontrar_id_url_tabela_propriedades_fiis(self, soup_link)
            soup_tabela = Fii.__extrair_tabela(self, '/html/body/table[2]', url_tabela, browser)
            # armazena os dados extraídos e logo em seguida é retornado pela função
            propriedades_fiis = list(map(lambda span: span.text,
                                         list(soup_tabela.findAll('span', class_='dado-valores'))))
            print(f"{Fore.GREEN}(Propriedades FIIS ({self.nome}) extraídas)\n")

            return propriedades_fiis

        except():
            print(f"{Fore.RED}Erro de execução!!!")

    def __efetuar_pesquisa(self, periodo_inicial, periodo_final, browser):
        # efetuando a pesquisa pelo fii desejado
        try:

            # formatando data para utilizá-la na url de pesquisa
            data_final_format = f"{periodo_final.split('/')[2]}-" \
                                f"{periodo_final.split('/')[1]}-" \
                                f"{periodo_final.split('/')[0]}"

            data_inicial_format = f"{periodo_inicial.split('/')[2]}-" \
                                  f"{periodo_inicial.split('/')[1]}-" \
                                  f"{periodo_inicial.split('/')[0]}"

            # realizando request
            url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=' \
                  f'18&palavra={self.nome[0:4]}&dataInicial={data_inicial_format}&dataFinal={data_final_format}'
            print(f"{Fore.YELLOW}-> request: {Style.RESET_ALL}{url}")
            browser.get(url)

            # processando e capturando dados
            # processando json retornado pelo request realizado anteriormente
            arquivo_json = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body")))
            html_arquivo_json = arquivo_json.get_attribute('outerHTML')
            soup_json = BeautifulSoup(html_arquivo_json, 'html.parser')
            list_dicionarios = json.loads(soup_json.text)

            # retornando lista com dados referente ao fundo imobiliário analisado
            # lista de dicionários, que possui credenciais para acessar outras páginas no site da b3
            return list_dicionarios

        except:
            print(f"{Fore.RED}Erro! Pesquisa não pode ser solicitar.")

    def __encontrar_credenciais_noticia_qualificada(self, list_dicionarios_noticia):
        # responsável por encontrar o 'id' e 'dateTime' da notícia contendo o elemento 'Aviso aos Cotistas'
        try:
            print(f"{Style.BRIGHT}-- Encontrando credenciais da noticia qualificada ({self.nome}) --")

            credenciais = {"id": None, "dateTime": None}
            identificador = "Aviso aos Cotistas"

            # filtrando dicionário, que possui o tal identificador
            dic_qualificado = (list(
                filter(lambda noticia: identificador in str(noticia['NwsMsg']['headline']) and 'N' in str(
                    noticia['NwsMsg']['headline'][-2]),
                       list_dicionarios_noticia)))

            if len(dic_qualificado) == 0:
                print(f"{Fore.RED}Erro! Aviso as cotistas não encontrado")
                return None

            incremento_id = dic_qualificado[0]['NwsMsg']['id']
            incremento_data_noticia = dic_qualificado[0]['NwsMsg']['dateTime']

            credenciais.update(id=incremento_id, dateTime=incremento_data_noticia)
            print(f"{Style.DIM}dicionário qualificado: {dic_qualificado}")
            print(f"{Style.DIM}credenciais {self.nome}: {credenciais}")

            # retornando as credenciais encontradas
            return credenciais

        except:
            print(f"{Fore.RED}Erro! Card qualificado não encontrado")

    def __solicitar_noticia_qualificada(self, credenciais_noticia, browser):
        # responsável por solicitar a notícia qualificado referente ao FII analisado
        try:
            # iniciado requirimento para a página de notícia encontrada
            url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/' \
                  f'Detail?idNoticia={credenciais_noticia.get("id")}' \
                  f'&agencia=18&dataNoticia={credenciais_noticia.get("dateTime")}'
            print(f"{Fore.YELLOW}-> request noticia qualificada ({self.nome}): {Style.RESET_ALL}{url}")
            browser.get(url)

            # selecionado o conteúdo html da pagina de notícia encontrada
            link = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "conteudoDetalhe")))
            html_link = link.get_attribute('outerHTML')
            soup_link = BeautifulSoup(html_link, 'html.parser')

            return soup_link

        except:
            print(f"{Fore.RED}Erro! Ao solicitar notícia qualificada.")

    def __encontrar_id_url_tabela_propriedades_fiis(self, soup_link):
        # encontrando o 'id' tabela cuja contem os dados (propriedades) do FII analisado
        try:

            # obtendo o 'id' de identificação da tabela
            id_tabela = (list(map(lambda ancora: str(ancora['href']).split('=')[1], list(soup_link.findAll('a'))))[0])

            url_tabela = 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=' + id_tabela + '&#toolbar=0'
            print(f"{Fore.YELLOW}-> url tabela notícia ({self.nome}): {Style.RESET_ALL}{url_tabela}")
            return url_tabela

        except:
            print(f"{Fore.RED}Erro! id tabela não encontrado")

    def __extrair_cotacao(self, browser):
        try:
            print(f"{Style.BRIGHT}-- Capturando cotacao FIIS ({self.nome}) --")

            # definindo o dia se baseando na 'data_base'
            data = {'dia': self.data_base.split('/')[0],
                    'mes':  self.data_base.split('/')[1],
                    'ano':  self.data_base.split('/')[2]
                    }

            # função que retorna 'mes'/'ano' do mês anterior ao da data de execução do scraping
            data_pesquisa = f'{data.get("mes")}/{data.get("ano")}'

            # url de pesquisa
            url = f'https://bvmf.bmfbovespa.com.br/SIG/FormConsultaMercVista.asp?strTipoResumo=RES_MERC_VISTA' \
                  f'&strSocEmissora={self.nome}&strDtReferencia={data_pesquisa}&strIdioma=P&intCodNivel=2' \
                  f'&intCodCtrl=160 '

            print(f"{Fore.YELLOW}-> url: {Style.RESET_ALL}{url}")

            # realizando request e extraindo tabela para obter tabela com as cotações do FII pesquisado
            soup_tabela = Fii.__extrair_tabela(self,
                                               '/html/body/table[3]/tbody/tr/td/table/tbody/tr/td/table[1]/tbody/tr[2]'
                                               '/td/table',
                                               url, browser)

            if soup_tabela is None:
                return None

            # percorre e armazena todas as linhas da tabela
            tag_trs = list(soup_tabela.find_all('tr'))
            num_linha = None

            # encontra a linha com as cotações da qual é referente a data base
            for linha in range(tag_trs.__len__()):
                lista_linha = tag_trs[linha].text.split('\n')
                if data.get('dia') in lista_linha[0]:
                    num_linha = linha

            # seleciona a cotação de fechamento referente a data base
            linha_fundo_desejado = tag_trs[num_linha].text.split('\n')
            string_cotacao = (linha_fundo_desejado[-2]).replace(",", ".")
            cotacao_formatada = float(string_cotacao)

            self.cotacao = float(cotacao_formatada)

        except:
            print(f"{Fore.RED}Erro! Cotacao FIIs ({self.nome}) não pode ser extraída.")

    def __extrair_tabela(self, xpath, url, browser):
        # captura a tabela desejada e retorna um 'sopa' html
        try:
            print(f"{Style.BRIGHT}-- Extraindo tabela referente FIIs ({self.nome}) --")

            # utilizando a url faz o requerimento da tabela
            browser.get(url)
            print(url)

            # a partir do 'xpath' encontra-se a tabela e logo em seguida é armazenada em uma variável
            tabela = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

            # extrai o html da tabela que logo em seguida é retornado pela função
            html_tabela = tabela.get_attribute('outerHTML')
            soup_tabela = BeautifulSoup(html_tabela, 'html.parser')

            if len(list(soup_tabela.find_all('table'))) == 0:
                print(f"Table not found")
                return None

            return soup_tabela

        except:
            print(f"{Fore.RED}Erro! Tabela FIIs ({self.nome}) não pode ser solicitada.")

    def calcular_dividend_yield(self):
        # responsável por calcular o 'dividend_yield'
        # dividendo dividido pela (cotação) dia data base. Logo em seguida multiplica o resultado por 100
        try:
            self.dividend_yield = (self.valor_provento / self.cotacao) * 100
        except:
            print(f"{Fore.RED}Erro! Não foi possível calcular o dividend yield ({self.nome})")

    def __extrair_valor_provento(self, dados_fiis):
        # extraindo 'valor do provento' da tabela retornada pela função 'propriedades_fiis'
        string_valor_provento = str(dados_fiis[5]).replace(",", ".")
        # formatando-a para float
        self.valor_provento = float(string_valor_provento)


    def __extrair_data_base(self, dados_fiis):
        # extraindo 'data base' da tabela retornada pela função 'propriedades_fiis'
        self.data_base = (dados_fiis[3])

    def __extrair_data_pagamento_provento(self, dados_fiis):
        # capturando 'data pagamento' da sopa html
        self.data_pagamento = (dados_fiis[4])

    def __extrair_periodo_referencia(self):
        # extraindo a 'data referencia' utilizando a 'data base' como referencia
        data_referencia = self.data_base.split('/')
        # 'periodo_referencia' é a chave primaria do banco de dados
        self.periodo_referencia = f"{self.nome}.{data_referencia[2]}.{data_referencia[1]}"
