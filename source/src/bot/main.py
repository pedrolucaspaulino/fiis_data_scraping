from nome_fii import list_fii, scrape_table
from scraping import execucao_tudo

def relatorio(path_file, conteudo):

    with open(path_file, 'w') as file:
         for nome in conteudo:
            file.write(str(nome + "\n"))                 

def main():

    scrape_table()
    fiis = list_fii()
    remanescente = list(filter(execucao_tudo, fiis))

    if len(remanescente) > 0:
        erro = list(filter(execucao_tudo, remanescente))
        relatorio('source/relatorio.txt', erro)

if __name__ == '__main__':
    main()