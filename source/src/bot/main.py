from functools import partial
import nome_fii  
import bot1
import format_data

def main():  

    datas = format_data.data_inicial_final()
    data_inicial = datas[0]
    data_final = datas[1]
    scraping = partial(bot1.get_dados, data_inicial, data_final) 

    fii = nome_fii.list_fii()
    for nome in range(len(fii)):
        scraping(fii[nome])

if __name__ == '__main__':
    main()