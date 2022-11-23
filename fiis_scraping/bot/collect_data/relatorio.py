"""
    Responsável por escrever o arquivo de relatório
    de erros ao decorrer da execução do programa.
"""


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
