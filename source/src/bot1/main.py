from functools import partial
import nome_fii
import scraping_b3
import tela

scraping = partial(scraping_b3.get_dados, '29/11/2021', '30/11/2021')

def start():    
    fii = nome_fii.list_fii()
    for i in range(10):
        scraping(fii[i])

    #map(scraping_b3.get_dados(nome), fii)

#start()
#tela.iniciar_tela()
scraping('BCRI')