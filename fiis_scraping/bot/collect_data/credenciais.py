"""
    Responsável por realizar
    filtrar as credenciais
    de notícias referentes
    aos FIIs solicitados.
"""

from bs4 import BeautifulSoup
from logging import info, error, critical
import requests


def credenciais_noticia_qualificada(list_dicionarios_noticia: dict) -> list:
    """
        Responsável por encontrar o 'id' e 'dateTime' referente às notícias encontradas.

        Parameters:
            list_dicionarios_noticia (dict): lista com dicionários contendo credenciais de acessoas às notícias
                presentes no site da b3.

        Returns:
            lista_credenciais (list): lista com as credenciais das notícias dos fundos selecionados pela filtragem.
            As notícias selecionadas possuem os seguintes elementos: 'Aviso aos Cotistas', em sua estrutura, e
            seguido por '(N)' que se severe às Normas / Notas.
    """

    # identificador utilizado para filtrar as notícias qualificadas.
    identificador = "Aviso aos Cotistas"

    # lista de credenciais retornadas pela função
    lista_credenciais = []

    # filtrando dicionário, que possui em seu escopo os identificadores.
    dicionarios_qualificados = (list(
        filter(lambda noticia: identificador in str(noticia['NwsMsg']['headline']) and 'N' in str(
            noticia['NwsMsg']['headline'][-2]),
               list_dicionarios_noticia)))

    if len(dicionarios_qualificados) == 0:
        error("Aviso as cotistas não encontrado")
        return []

    # adicionando as credenciais selecionadas dos 'dicionarios qualificados' em uma nova lista.
    # tal lista é responsável por armazenar as variáveis responsáveis por realizar
    # pesquisa refentes fundos analisados.
    for index in range(len(dicionarios_qualificados)):
        # criando molde do dicionário padronizado que será retornado pela função.
        credenciais = {"nome": None, "id": None, "date_time": None}

        # atribuindo valores as variáveis que serão adicionadas ao dicionário.
        id_dicionarios_qualificados = dicionarios_qualificados[index]['NwsMsg']['id']
        datetime_dicionarios_qualificados = dicionarios_qualificados[index]['NwsMsg']['dateTime']
        nome_dicionarios_qualificados = \
            f"{str(dicionarios_qualificados[index]['NwsMsg']['headline']).split('(')[1][0:4]}11"

        # adicionando os valores extraídos ao dicionário.
        credenciais.update(nome=nome_dicionarios_qualificados,
                           id=id_dicionarios_qualificados,
                           date_time=datetime_dicionarios_qualificados)

        # adicionando dicionario a lista de dicionários que será retornado pela função.
        lista_credenciais.append(credenciais)

    # retornando as credenciais encontradas.
    return lista_credenciais


def listar_credenciais_noticias(periodo_inicial: str, periodo_final: str, nome: str = None) -> list:
    """
        Efetua pesquisa em busca das credências das notícias presente no site da B3.

        Parameters:
            nome: ticker referente ao fundo a ser solicitado, caso seja None será solicitado todos os fundos listados

            periodo_inicial (str): data inicial do período de notícias que serão pesquisados.

            periodo_final (str): data final do período de notícias que serão pesquisados.

        Returns:
        lista_credenciais (list): lista com os dados coletados da tabela com as credenciais das notícias
        responsáveis por direcionar acesso para as notícias desejadas e qualificadas.
    """

    # formatando data para utilizá-la na url de pesquisa.
    data_final_format = f"{periodo_final.split('/')[2]}-" \
                        f"{periodo_final.split('/')[1]}-" \
                        f"{periodo_final.split('/')[0]}"

    data_inicial_format = f"{periodo_inicial.split('/')[2]}-" \
                          f"{periodo_inicial.split('/')[1]}-" \
                          f"{periodo_inicial.split('/')[0]}"

    if nome is not None:
        url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=' \
              f'18&palavra={nome}&dataInicial={data_inicial_format}&dataFinal={data_final_format}'
    else:
        url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=' \
              f'18&palavra=&dataInicial={data_inicial_format}&dataFinal={data_final_format}'

    # iniciando request
    info(f"request: {url}")
    page = requests.get(url)

    if page.status_code == 200:
        # processando json retornado pelo request realizado.
        list_dicionarios = page.json()

        # retornando lista com dados, qualificados, de acesso referente as notícias dos fundos imobiliários
        # da b3.
        return credenciais_noticia_qualificada(list_dicionarios)

    elif page.status_code == 404:
        critical("Pesquisa, referente as credenciais, não encontrada.")

    else:
        critical("Pesquisa, referente as credenciais, não pode ser solicitada.")


def id_url_tabela_propriedades_fiis(soup_link: BeautifulSoup) -> str:
    """
        Encontra o 'id' de acesso à tabela de propriedades do fundo analisado.

        Parameters:
            soup_link (BeautifulSoup): html da página de notícia referente ao fundo analisado.

        Returns:
            url_tabela (str): url, contendo 'id' encontrado, de acesso à tabela 'propriedades' referente
            ao FII analisado.
    """

    # obtendo o 'id' de identificação da tabela.
    id_tabela = (list(map(lambda ancora: str(ancora['href']).split('=')[1],
                          list(soup_link.findAll('a'))))[0])

    # adicionando 'id' à url para realizar a pesquisa pela tabela 'propriedades' referente ao FII analisado.
    url_tabela = 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=' + id_tabela + '&#toolbar=0'
    info(f"url tabela notícia: {url_tabela}")
    return url_tabela


def montar_periodo_referencia(data_base: str, nome: str) -> str:
    """
        Cria o período de referência referente a data dos dados coletados.

        Returns:
            periodo_referencia: consiste em criar uma referência no formato 'ticker + ano + mês'
    """

    # extraindo a 'data referencia' utilizando a 'data base' como referencia.
    data_referencia = data_base.split('/')
    # 'periodo_referencia' é a chave primaria do banco de dados.
    periodo_referencia = f"{nome}.{data_referencia[2]}.{data_referencia[1]}"

    return periodo_referencia
