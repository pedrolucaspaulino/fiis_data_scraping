"""
    Responsável por extrair/filtrar os dados
    obtidos pela coleta de dados.
"""

from bs4 import BeautifulSoup
from colorama import Fore
import colorama

colorama.init(autoreset=True)


def extrair_tabela_cotacao(soup_html: BeautifulSoup, dia_data_base: str) -> float:
    """
        Extrai a cotação tomando como base a 'data base' referente ao fundo analisado.

        Returns:
            bool: 'True' for success or 'False' for fail.
    """

    # percorre e armazena todas as linhas da tabela.
    tag_trs = list(soup_html.find_all('tr'))
    num_linha = None

    # encontra a linha com as cotações da qual é referente a data base.
    for linha in range(tag_trs.__len__()):
        lista_linha = tag_trs[linha].text.split('\n')
        if dia_data_base in lista_linha[0]:
            num_linha = linha

    if num_linha is None or len(
            list(filter(
                lambda td: td.text in 'Resumo Diário', list(soup_html.find_all('td'))))) == 0:
        print(f"{Fore.RED}Erro! Cotação de fechamento referente a data base não encontrada.")
        return False

    # seleciona a cotação de fechamento referente a data base.
    linha_fundo_desejado = tag_trs[num_linha].text.split('\n')

    string_cotacao = str((linha_fundo_desejado[-2]).replace('.', "")).replace(",", ".")
    cotacao_formatada = float(string_cotacao)

    cotacao = float(cotacao_formatada)
    return cotacao


def extrair_propriedades(html_table: BeautifulSoup) -> dict:
    """
        Responsável por extrair: o valor do provento, data base e data de pagamento do fundo analisado.

        Parameters:
            html_table (BeautifulSoup): html da tabela propriedades do Fii analisado

        Returns: result (dict): contém as propriedades extraídas da tabela. São elas: valor do provento, data base e
        data de pagamento
    """

    dados_fiis = list(map(lambda span: span.find('span', class_='dado-valores'),
                          list(html_table.findAll('tr'))))

    # extraindo 'valor do provento' da tabela retornada pela função 'propriedades_fiis'.
    string_valor_provento = str(dados_fiis[3].get_text()).replace(".", "").replace(",", ".")
    # formatando-a para float
    valor_provento = float(string_valor_provento)

    # extraindo 'data base' da tabela retornada pela função 'propriedades_fiis'.
    data_base = (dados_fiis[2].get_text())

    # capturando 'data pagamento' da sopa html
    data_pagamento = (dados_fiis[4].get_text())

    result = {"valor_provento": valor_provento,
              "data_base": data_base,
              "data_pagamento": data_pagamento}

    return result
