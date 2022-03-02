from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import banco_dados
import bot2

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
            url_tabela = encontrar_id__url_tabela(soup_link)
            soup_tabela = capturar_tabela(browser, '/html/body/table[2]', url_tabela)

        finally:
            salvar_dados(soup_tabela, nome, data_final, data_inicial, browser)
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
        tabela_noticias = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tabelaNoticias_wrapper"]')))


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


def encontrar_id__url_tabela(soup_link):
    # encontrando o id tabela
    try:
        # optendo o 'id' de identificação da tabela contendo os dados do fii
        for ancora in soup_link.findAll('a'):
            lista_link = str(ancora['href']).split('=')
            id_tabela = lista_link[1]

        url_tabela= 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id='+id_tabela+'&#toolbar=0'

        return url_tabela

    except:
        print("Erro! id tabela não encontrado")


def capturar_tabela(browser, xpath, url):
    # captura a tabela desejada e retorna um 'sopa' html
    try:

        # utilizando a url faz o requerimento da tabela
        browser.get(url)    

        # a partir do 'xpath' encotra-se a tabela e logo em seguida é armazenada em uma variável
        tabela = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        # extrai o html da tabela que logo em seguida é retornado pela função
        html_tabela = tabela.get_attribute('outerHTML')
        soup_tabela = BeautifulSoup(html_tabela, 'html.parser')

        return soup_tabela

    except:
        print("Erro! Tabela não pode ser solicitar.")
        
def salvar_dados(soup_tabela, nome, data_final, data_inicial, browser):
    # salvando tabela no banco de dados 
    try:        

        # lista que armazena dados da tabela encontrada
        soup_dados = [] 
        
        # solicitando os dados no interior da tabela
        for span in soup_tabela.findAll('span', class_='dado-valores'):
            soup_dados.append(span.text)

        # editando formato dos elementos encontrados para salvar no banco
        # fomatando nome do fundo para incluir '11' no fim de cada nome
        nome = (str(nome + "11"))

        # capturando da sopa html a string do 'valor do provento' e formatando-a para float
        string_valor_provento = soup_dados[5].split(',')
        valor_provento = float(string_valor_provento[0] + '.' + string_valor_provento[1])

        # capturando 'data base' da sopa html
        data_base = (soup_dados[3])

        # informando o dia em do qual a 'data_base' é situada para a função de cotação
        dia = data_base.split('/')       
        # chamando função do bot2 para capturar a cotação referente a data base  
        cotacao_data_base = bot2.get_cotacao(browser, nome, dia[0])

        # capturando 'data pagamento' da sopa html
        data_pagamento = (soup_dados[4])
        #formatando a 'data referencia' utilizando a 'data base' como referencia
        meses = ['jan', 'fev', 'mar', 'abr','maio','jun','jul','ago','set','out','nov','dez']
        data_referencia = data_base.split('/')
        # periodo_referencia é a chave primaria do banco de dados
        periodo_referencia = f"{nome}-{data_referencia[2]}.{meses[int(data_referencia[1]) - 1]}"

        # criando dicionário para utilizar como parâmetro na função 'insert_into_talela'
        dic = {
            'nome': [nome], 
            'data_base': [data_base],
            'cotacao_data_base': [cotacao_data_base],
            'valor_provento': [valor_provento], 
            'data_pagamento': [data_pagamento],
            'periodo_referencia': [periodo_referencia]
        }

        # salvando as informações obtidas no banco de dados
        banco_dados.insert_into_talela(dic, 'info_fii')

    except:
        print("Erro! Ao salvar tabela")