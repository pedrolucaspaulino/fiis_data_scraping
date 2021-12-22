from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

data_base = []
valor_provento = []
periodo_reverencia = []
nome_fii = []

dados = {
    "Nome": nome_fii,
    'Data Base': data_base,
    'Provento': valor_provento,
    'Periodo Reverencia': periodo_reverencia
}

option = Options()
option.headless = True

# função principal
def get_dados(nome, data_inicial, data_final):

    try:
        # efetuando a pesquisa pelo fii desejado
        soup_cards_noticia = efetuar_pesquisa(nome, data_inicial, data_final)

        # econtrando o card de notícia contendo o elemento 'Aviso aos Cotistas'
        incremento =  encontrar_card_qualificado(soup_cards_noticia)

        # solicitando pele noticia na qual o elemento do card seja qualificado
        soup_link =  solicitando_noticia_qualificada(incremento)

        # encontrando o id tabela 
        id_tabela = encontrado_id_tabela(soup_link)

        # soliciando pela tabela com o id encontrado 
        soup_tabela = solicitando_tabela(id_tabela)

        # salvando tabela em arquivo csv como nome personalisado de cada fii
        salvando_tabela(soup_tabela, nome, data_final, data_inicial)

    except:
        print("Erro! Não foi possivel concluir a extração")    


def efetuar_pesquisa(nome, data_inicial, data_final):
    try:
        with webdriver.Firefox(options=option) as browser:

            url = 'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Index?agencia=18'
            browser.get(url)

            # requerindo pelo fii desejado
            elem_name = browser.find_element(By.ID, 'txtPalavraChave') 
            elem_name.send_keys(nome)

            # pesquisando a data inicial de pesquisa 
            elem_data_inicial = browser.find_element(By.ID, 'txtPeriodoDe')
            elem_data_inicial.send_keys(data_inicial)

            # pesquisando a data final de pesquisa 
            elem_data_final = browser.find_element(By.ID, 'txtPeriodoAte') 
            elem_data_final.send_keys(data_final)

            # efetuando a pesquisa de notícias
            browser.find_element_by_xpath("//div[@class='large-3 columns']/button[@id='btnBuscar']").click()                 
            sleep(5)

            # atribuindo o html dos cards de notícias em 'html_tabela_noticias'
            tabela_noticias = browser.find_element(By.ID, 'divTabelaNoticias')

            html_tabela_noticias = tabela_noticias.get_attribute('outerHTML') 
            soup_cards_noticia = BeautifulSoup(html_tabela_noticias, 'html.parser') 

        return soup_cards_noticia

    except:
        print("Erro! Pesquisa não pode ser solicitar.")


def encontrar_card_qualificado(soup_cards_noticia):

    try:
        # selecionando cards com texto contendo o seguinte elemento: 'Aviso aos Cotistas'  
        for noticia in soup_cards_noticia.find_all("div",class_='row'):
            for noticia_card in noticia.find_all("div",class_='card clickable'):
                for noticia_texto in noticia_card.find_all('h4'):
                    if 'Aviso aos Cotistas' in noticia_texto.text:
                        sub_incremento = noticia.find_all("a")
                        incremento_url_noticia = str(sub_incremento[1]['href'])

        return incremento_url_noticia

    except:
        print("Erro! Card qualificado não encotrado")


def solicitando_noticia_qualificada(incremento):
    try:
        with webdriver.Firefox(options=option) as browser:
            # inicinado requimento para a página de notícia encontrada
            url_segundaria = 'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/' + incremento
            browser.get(url_segundaria)
            sleep(5)
                
            # selecionado o conteúdo html da pagina de notícia encotrada
            link = browser.find_element(By.ID, 'conteudoDetalhe')
            html_link = link.get_attribute('outerHTML')
            soup_link = BeautifulSoup(html_link, 'html.parser')

        return soup_link

    except:
        print("Erro! Ao requerir notícia qualificada.") 


def encontrado_id_tabela(soup_link):
    try:
        # optendo o 'id' de identificação da tabela contendo os dados do fii
        for ancora in soup_link.findAll('a'):
            lista_link = str(ancora['href']).split('=')
            id_tabela = lista_link[1]

        return id_tabela

    except:
        print("Erro! id tabela não encontrado")


def solicitando_tabela(id_tabela):
    try:
        with webdriver.Firefox(options=option) as browser:
            # formando a url da tabela de exibição com base no 'id' encontrado anteriormente 
            url_tabela_dados = 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id='+id_tabela+'&#toolbar=0'
            browser.get(url_tabela_dados)
            sleep(10)                

            # obtendo o html da tabela de exibição com os dados do fii pesquisado
            tabela = browser.find_element_by_xpath("/html/body/table[2]")
            html_tabela = tabela.get_attribute('outerHTML')
            soup_tabela = BeautifulSoup(html_tabela, 'html.parser')

        return soup_tabela
    
    except: 
        print("Erro! Ao solicitar tabela")


def salvando_tabela(soup_tabela, nome, data_final, data_inicial):
    try:

        soup_dados = [] 
        
        for span in soup_tabela.findAll('span', class_='dado-valores'):
            if span.text != "":
                soup_dados.append(span.text)

        valor_provento.append(soup_dados[3])
        data_base.append(soup_dados[1]) 

        nome_completo_fii = nome.upper() + "11"
        nome_fii.append(nome_completo_fii)
        
        periodo = data_inicial + ' - ' + data_final
        periodo_reverencia.append(periodo)              

    except:
        print("Erro! Ao salvar tabela")

def adicionando_data_frame():
    try:
        df = pd.DataFrame(dados)
        df.to_csv('dados_b3.csv')
        print(df)
    except:
        print("Erro não foi possível formar o DataFrame")