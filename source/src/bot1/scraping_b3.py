from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import banco_dados
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

option = Options()
option.headless = True

# função principal
def get_dados(data_inicial, data_final, nome):

    print(f"\n\nNome: {nome}")

    with webdriver.Firefox(options=option) as browser:

        try:
            soup_cards_noticia = efetuar_pesquisa(nome, data_inicial, data_final, browser)
            incremento =  encontrar_card_qualificado(soup_cards_noticia, nome)

        except:
            print("Erro! Não foi possivel concluir a extração. Falha ao efetuar pesquisa")

        else:
            soup_link =  solicitar_noticia_qualificada(incremento, browser)
            id_tabela = encontrar_id_tabela(soup_link)
            soup_tabela = capturar_tabela(id_tabela, browser)

        finally:
            salvar_dados(soup_tabela, nome, data_final, data_inicial)
            print(f"{nome}: Processo finalisado.")


def efetuar_pesquisa(nome, data_inicial, data_final, browser):
    # efetuando a pesquisa pelo fii desejado
    try:
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
        pesquisa = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='large-3 columns']/button[@id='btnBuscar']")))
        pesquisa.click()
        
        # atribuindo o html dos cards de notícias em 'html_tabela_noticias'
        tabela_noticias = browser.find_element(By.ID, "tabelaNoticias")
        #tabela_noticias = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "tabelaNoticias")))
        sleep(5)

        html_tabela_noticias = tabela_noticias.get_attribute('outerHTML') 
        soup_cards_noticia = BeautifulSoup(html_tabela_noticias, 'html.parser') 

        return soup_cards_noticia

    except:
        print("Erro! Pesquisa não pode ser solicitar.")


def encontrar_card_qualificado(soup_cards_noticia, nome):
    # econtrando o card de notícia contendo o elemento 'Aviso aos Cotistas'    
    try:
        nome_lapidado = str("(" + nome + ")" + " Aviso aos Cotistas")
        ancora = soup_cards_noticia.find_all("a")
        lista_link = (list(filter(lambda ancora: nome_lapidado in str(ancora) , list(ancora))))
        incremento_url_noticia = lista_link[1]['href']

        return incremento_url_noticia

    except:
        print("Erro! Card qualificado não encotrado")


def solicitar_noticia_qualificada(incremento, browser):
    # solicitando pele noticia na qual o elemento do card seja qualificado
    try:
        # inicinado requimento para a página de notícia encontrada
        url_segundaria = 'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/' + incremento
        browser.get(url_segundaria)
                
        # selecionado o conteúdo html da pagina de notícia encotrada
        link = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "conteudoDetalhe")))
        html_link = link.get_attribute('outerHTML')
        soup_link = BeautifulSoup(html_link, 'html.parser')

        return soup_link

    except:
        print("Erro! Ao requerir notícia qualificada.") 


def encontrar_id_tabela(soup_link):
    # encontrando o id tabela
    try:
        # optendo o 'id' de identificação da tabela contendo os dados do fii
        for ancora in soup_link.findAll('a'):
            lista_link = str(ancora['href']).split('=')
            id_tabela = lista_link[1]

        return id_tabela

    except:
        print("Erro! id tabela não encontrado")


def capturar_tabela(id_tabela, browser):
    # soliciando pela tabela com o id encontrado 
    try:
        # formando a url da tabela de exibição com base no 'id' encontrado anteriormente 
        url_tabela_dados = 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id='+id_tabela+'&#toolbar=0'
        browser.get(url_tabela_dados)               

        # obtendo o html da tabela de exibição com os dados do fii pesquisado
        tabela = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[2]")))
        html_tabela = tabela.get_attribute('outerHTML')
        soup_tabela = BeautifulSoup(html_tabela, 'html.parser')

        return soup_tabela
    
    except: 
        print("Erro! Ao solicitar tabela")


def salvar_dados(soup_tabela, nome, data_final, data_inicial):
    # salvando tabela no banco de dados 
    try:        

        # lista que armazena dados da tabela encontrada
        soup_dados = [] 
        
        # solicitando os dados no interior da tabela
        for span in soup_tabela.findAll('span', class_='dado-valores'):
            soup_dados.append(span.text)

        # editando editando formato dos elementos encontrados para salvar no banco
        nome = (str(nome + "11"))

        string_valor_provento = soup_dados[5].split(',')
        valor_provento = float(string_valor_provento[0] + '.' + string_valor_provento[1])

        data_base = (soup_dados[3])
        meses = ['jan', 'fev', 'mar', 'abr','maio','jun','jul','ago','set','out','nov','dez']
        data_referencia = data_base.split('/')
        periodo_referencia = f"{data_referencia[2]}.{meses[int(data_referencia[1]) - 1]}"

        # criando dicionário para utilizar como parâmetro na função 'insert_into_talela'
        dic = {
            'nome': [nome], 
            'data_base': [data_base], 
            'valor_provento': [valor_provento], 
            'periodo_referencia': [periodo_referencia]
        }

        # salvando as informações obtidas no banco de dados
        banco_dados.insert_into_talela(dic, 'info_fii')

    except:
        print("Erro! Ao salvar tabela")