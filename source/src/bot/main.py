from nome_fii import list_fii
from scraping import execucao_tudo

def relatorio(path_file, conteudo):

    with open(path_file, 'w') as file:
        for nome in conteudo:
            file.write(str(nome + "\n"))                  

def main():

    fiis = list_fii()
    erro = list(filter(execucao_tudo, fiis))
    relatorio('projeto_cientifico/source/relatorio.txt', erro)   

if __name__ == '__main__':
    main()