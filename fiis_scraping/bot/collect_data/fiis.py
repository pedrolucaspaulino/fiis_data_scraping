from fiis_scraping.bot.collect_data.filter_data import extrair_propriedades
from fiis_scraping.bot.collect_data.credenciais import montar_periodo_referencia
from fiis_scraping.bot.collect_data.credenciais import id_url_tabela_propriedades_fiis
from fiis_scraping.bot.webdriver.webdriver_request import request_webdriver
from fiis_scraping.util.constantes.const_search_types import search_by_id, search_by_xpath
from fiis_scraping.dao.banco_dados import salvar_dados
from fiis_scraping.util.constantes.const import *
from logging import info, error, debug


class Fiis:
    """
        Classe responsável pela coleta e cadastro de dados no que diz respeito aos
        fundos de Investimento Imobiliário (FII).
    """

    def __init__(self, nome: str, **kwargs):

        # propriedades fii
        self.nome = nome  # ticker
        self.valor_provento = kwargs.get(valor_provento)
        self.data_base = kwargs.get(data_base)
        self.data_pagamento = kwargs.get(data_pagamento)
        self.periodo_referencia = kwargs.get(periodo_referencia)
        self.cotacao = kwargs.get(cotacao)
        self.dividend_yield = kwargs.get(dividend_yield)

    def verifica_atributos(self) -> bool:

        """
            Verifica se todos os atributos do abjeto instanciado foram inicializados com algum valor.

            Returns:
            bool: 'True' for success or 'False' for fail.
        """

        if self.valor_provento is None or self.data_base is None or self.data_pagamento is None \
                or self.periodo_referencia is None or self.cotacao is None or self.dividend_yield is None \
                or self.nome is None:
            return False
        else:
            return True

    def collect_data(self, id_noticia: str, date_time: str) -> bool:

        """
            Realiza a coleta de dados, individual, de cada fundo analisado
            e atribuir os devidos valores aos respectivos atributos do objeto instanciado.

            Parameters:
                id_noticia (str): parâmetro de pesquisa padrão utilizado para request da notícia desejada no site B3.

                date_time (str): parâmetro de pesquisa padrão utilizado para request da notícia desejada no site B3.

            Returns:
                bool: 'True' for success or 'False' for fail.
        """

        # print("\n--------------------------------------------------------------------------------------")
        info(f"(Iniciando extracao Propriedades FIIS ({self.nome}))")

        # com base nas credências obtidas no site da b3 é construída a url de busca para o fundo analisado
        url_noticia_desejada = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/' \
                               f'Detail?idNoticia={id_noticia}' \
                               f'&agencia=18&dataNoticia={date_time}'

        # realiza o request da página de notícias referente ao FII analisado.
        result_page_noticia = request_webdriver(url_noticia_desejada,
                                                time=10,
                                                search_type=search_by_id,
                                                element="conteudoDetalhe")

        if not result_page_noticia.get(status_const):
            error("Não foi possível solicitar a noticia desejada!")
            return False

        # iniciando processo de extração das propriedades referentes aos FIIs.
        propriedade = Fiis.__propriedades(self, result_page_noticia)
        info(f"{propriedade}")

        if not propriedade.get(status_const):
            error(f"Não foi possível extrair propriedades referente ao FII {self.nome}")
            return False

        # atribuindo valores aos atributos do objeto instanciado
        self.valor_provento = propriedade.get(valor_provento)
        self.data_base = propriedade.get(data_base)
        self.data_pagamento = propriedade.get(data_pagamento)
        self.periodo_referencia = montar_periodo_referencia(self.data_base, self.nome)

        # com base nas propriedades inicia-se o processo para extrair a cotação refente ao fundo analisado.
        if not Fiis.__cotacao(self):
            error("")
            return False

        # inicia o cálculo do dividend yield com base nos dados encontrados.
        Fiis.calcular_dividend_yield(self)

        return True

    def __propriedades(self, result_page_noticia) -> dict:

        """
            Extrai as propriedades do FII analisado com base na notícia encontrada e o html da tabela de propriedades
            contendo as informações as seguintes informações: valor provento, data base e data pagamento do provento.

            Parameters:
                result_page_noticia: html da página de notícia do FII analisado

            Returns:
            propriedades_fiis (list): lista com os dados coletados da tabela. São eles:
            valor provento, data base e data pagamento do provento.
        """

        if result_page_noticia.get(status_const):
            url_tabela = id_url_tabela_propriedades_fiis(result_page_noticia.get('html'))
            soup_tabela = request_webdriver(url_tabela,
                                            time=10,
                                            search_type=search_by_xpath,
                                            element='/html/body/table[2]')

            if soup_tabela.get(status_const):
                # armazena os dados extraídos e logo em seguida são retornados pela função.
                propriedades_fiis = extrair_propriedades(soup_tabela.get("html"))

                debug(f"(Propriedades FIIS ({self.nome}) extraídas)")

                return propriedades_fiis

    def __cotacao(self) -> bool:

        """
            Extrai a cotação tomando como base a 'data base' referente ao fundo analisado.

            Returns:
                bool: 'True' for success or 'False' for fail.
        """

        debug(f"Capturando cotacao FIIS ({self.nome})")

        # definindo o dia se baseando na 'data_base'.
        data = {'dia': self.data_base.split('/')[0],
                'mes': self.data_base.split('/')[1],
                'ano': self.data_base.split('/')[2]
                }

        # função que retorna 'mes'/'ano' do mês anterior ao da data de execução da coleta dos dados.
        data_pesquisa = f'{data.get("mes")}/{data.get("ano")}'

        # url de pesquisa.
        url = f'https://bvmf.bmfbovespa.com.br/SIG/FormConsultaMercVista.asp?strTipoResumo=RES_MERC_VISTA' \
              f'&strSocEmissora={self.nome}&strDtReferencia={data_pesquisa}&strIdioma=P&intCodNivel=2' \
              f'&intCodCtrl=160'

        info(f"url: {url}")

        # realizando request e extraindo tabela com as cotações do FII pesquisado.
        element = '/html/body/table[3]/tbody/tr/td/table/tbody/tr/td/table[1]/tbody/tr[2]/td/table'
        soup_tabela = request_webdriver(url,
                                        time=10,
                                        search_type=search_by_xpath,
                                        element=element)

        if not soup_tabela.get(status_const):
            error("Tabela de Cotação não encontrada.")
            return False

        if soup_tabela.get(status_const):

            # percorre e armazena todas as linhas da tabela.
            tag_trs = list(soup_tabela.get('html').find_all('tr'))
            num_linha = None

            # encontra a linha com as cotações da qual é referente a data base.
            for linha in range(tag_trs.__len__()):
                lista_linha = tag_trs[linha].text.split('\n')
                if data.get('dia') in lista_linha[0]:
                    num_linha = linha

            if num_linha is None or len(list(
                    filter(lambda td: td.text in 'Resumo Diário',
                           list(soup_tabela.get('html').find_all('td'))))) == 0:
                error("Cotação de fechamento referente a data base não encontrada.")
                return False

            # seleciona a cotação de fechamento referente a data base.
            linha_fundo_desejado = tag_trs[num_linha].text.split('\n')

            string_cotacao = str((linha_fundo_desejado[-2]).replace('.', "")).replace(",", ".")
            cotacao_formatada = float(string_cotacao)

            self.cotacao = float(cotacao_formatada)
            return True

    def calcular_dividend_yield(self) -> None:

        """
            Calcula o 'dividend_yield' do fundo analisado.

            Returns:
                None
        """

        try:
            if self.valor_provento is not None and self.cotacao is not None:
                # formula para calcular 'dividend_yield'.
                self.dividend_yield = (self.valor_provento / self.cotacao) * 100
                return
            else:
                error(f"Não foi possível calcular o dividend yield. Fundo analisado: ({self.nome})")

        except ZeroDivisionError:
            error(f"Impossível de calcular Divisor igual a '0'. Fundo analisado: ({self.nome})")
            return

    def salvar_dados_fiis(self, database: str) -> bool:

        """
            Responsável por salvar os dados na base solicitada.

            Parameters:
                database (str): path referente à base de dados.

            Returns:
                bool: 'True' for success or 'False' for fail.
        """

        # verificação dos atributos preenchidos pelo objeto.
        if Fiis.verifica_atributos(self):

            # atribuindo valores às respectivas tabelas referents à base de dados.
            tab_valores = (self.periodo_referencia, self.cotacao, self.valor_provento, self.dividend_yield)
            tab_datas = (self.nome, self.data_base, self.data_pagamento, self.periodo_referencia)

            # iniciando tentativa de salvamento.
            status = salvar_dados(tab_datas, tab_valores, database)

            # informando e retornando status da operação
            if status:
                info("Dados salvos com sucesso!")
                return status

            error("Falha ao salvar dados.")
            return status

        # caso tenha algum atributo do objeto instanciado não preenchido.
        return False
