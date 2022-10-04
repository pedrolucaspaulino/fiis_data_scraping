from format_data import data_inicial_final
from fiis import Fiis
from colorama import Fore, Style
import colorama

colorama.init(autoreset=True)


def start(credencias: dict) -> bool:

    """
        Instancia objeto referente ao fii analisado
        Caso houver algum erro no processo retorna 'True' (indicando que houve algum erro no processo)
        Caso as operações forem realizadas com sucesso a função retorna 'False' (indicando que houve sucesso)
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
    with open(path_file, 'w') as file:
        for nome in conteudo:
            file.write(str(nome + "\n"))


def main():
    # realizando request das credências necessárias para efetuar pesquisa
    credenciais = Fiis.lista_credenciais(data_inicial_final().get('data_inicial'),
                                         data_inicial_final().get('data_final'))

    remanescente = list(filter(start, credenciais))

    if len(remanescente) > 0:
        erro = list(filter(start, remanescente))
        relatorio('source/relatorio.txt', erro)


if __name__ == '__main__':
    main()
