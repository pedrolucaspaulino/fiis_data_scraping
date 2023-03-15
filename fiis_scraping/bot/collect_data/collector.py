"""
    Responsável por instanciar, todos os fundos listados na b3, iniciando
    o processo de coleta dos seus atributos e por fim salvando
    na base de dados local.
"""

from fiis_scraping.util.formata.formata_data import data_inicial_final, fun_data
from fiis_scraping.bot.collect_data.credenciais import listar_credenciais_noticias
from fiis_scraping.bot.collect_data.fiis import Fiis
from logging import error


def start_data_collector(credencias: dict) -> bool:
    """
        Realiza o processo de coleta de dados de todos os FIIs listados na B3
        armazenando a coleta em sua base dados.

         Parameters:
            credencias.get('nome'): ticker do fundo a ser analisado

            credencias.get('id'): credencial de url necessária para acessar a notícia e posteriormente a tabela
                contendo as informações do provento.

            credencias.get('date_time'): credencial de url necessária para acessar a notícia e posteriormente a
            tabela contendo as informações do provento.

        Returns:
            bool: 'True' for success or 'False' for fail.
    """

    path = f"data/data_{fun_data().replace('/', '-')}.db"
    fii = Fiis(credencias.get('nome'))

    if fii.collect_data(credencias.get('id'), credencias.get('date_time')):
        # salva os dados extraídos na base de dados
        # função 'salvar dados fiis' retorna 'True' em caso de sucesso e 'False' em caso de erro
        return not fii.salvar_dados_fiis(path)

    error("Falha ao concluir o manipulate_data.")
    return True


def collect_all_b3(periodo_consulta: str) -> None:
    """
        Inicia a coleta dos dados de todos os fundos listados na B3, com base no período de consulta.

         Parameters:
            kwargs.get('data_inicial'): data inicial referente ao período de pesquisa dos dados coletados.

            kwargs.get('data_final'): data final referente ao período de pesquisa dos dados coletados.

        Returns:
            None
    """

    data_inicial = data_inicial_final(periodo_consulta).get('data_inicial')
    data_final = data_inicial_final(periodo_consulta).get('data_final')

    # realizando request das credências necessárias para efetuar pesquisa.
    credenciais = listar_credenciais_noticias(data_inicial, data_final)

    if credenciais is not None:

        # inicia a analisa de cada fundo listado na B3.
        remanescente = list(filter(start_data_collector, credenciais))

        # gerando relatório dos fundos que não foi possível extrair os dados.
        if len(remanescente) > 0:
            erro = list(filter(start_data_collector, remanescente))
    else:
        error("Falha ao obter credencias para acessar as notícias referentes aos "
              f"fundos analisados.")
