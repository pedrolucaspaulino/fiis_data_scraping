from format_data import data_inicial_final
from fiis import Fiis
from colorama import Fore, Style
import colorama

colorama.init(autoreset=True)


def start(credencias: dict) -> bool:

    """
        Instancia objeto referente ao fii analisado. Chama a função de scraping atribuindo valores aos atributos do
        objeto instanciado.

         Parameters:
            credencias (dict): contem as credências necessárias para realizar o scraping dos dados.

            Returns:
                bool: 'True' for success or 'False' for fail.
    """

    try:
        fii = Fiis(credencias.get('nome'))
        if fii.scraping_data(credencias.get('id'), credencias.get('date_time')):

            # salva os dados extraídos na base de dados
            # função 'salvar dados fiis' retorna 'True' em caso de sucesso e 'False' em caso de erro
            return not fii.salvar_dados_fiis('data/dados2.db')

        return True
    except:
        print(f"{Fore.RED}{Style.BRIGHT}Erro! Falha ao concluir o scraping.")
        return True


def relatorio(path_file: str, conteudo) -> None:

    """
        Grava os nomes dos fundos não analisados em um arquivo texto.

        Parameters:
            path_file (str): caminho referente ao arquivo do relatório
            conteudo: conteúdo a ser armazenados no relatório

            Returns:
                None
    """

    with open(path_file, 'w') as file:
        for nome in conteudo:
            file.write(str(nome + "\n"))


def main():
    # realizando request das credências necessárias para efetuar pesquisa.
    credenciais = Fiis.listar_credenciais(data_inicial_final().get('data_inicial'),
                                          data_inicial_final().get('data_final'))

    remanescente = list(filter(start, credenciais))

    if len(remanescente) > 0:
        erro = list(filter(start, remanescente))
        relatorio('source/relatorio.txt', erro)


if __name__ == '__main__':
    main()
