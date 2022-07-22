from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

# função principal
def get_dados(data_inicial, data_final, nome, browser):

    print(f"\n\nNome: {nome}")

    try:

        list_dicionarios_noticia = efetuar_pesquisa(nome, data_inicial, data_final, browser)
        credenciais_noticia =  encontrar_credenciais_noticia_qualificada(list_dicionarios_noticia)

        soup_link =  solicitar_noticia_qualificada(credenciais_noticia, browser)
        url_tabela = encontrar_id__url_tabela(soup_link)
        soup_tabela = capturar_tabela(browser, '/html/body/table[2]', url_tabela)

        soup_dados = formata_tabela_bot1(soup_tabela)  

        nome_formato_11 = (str(nome + "11")) # acrescenta '11' ao final do nome do fiis
        valor_provento = formata_valor_provento(soup_dados)
        data_base = formata_data_base(soup_dados)
        data_pagamento = formata_data_pagamaneto_provento(soup_dados)
        periodo_referencia = formata_periodo_referencia(data_base, soup_dados, nome)
   
        data = (nome_formato_11, data_base, data_pagamento, periodo_referencia, valor_provento)  

        return data 

    except():
        print("Erro de execução!!!")

    finally:        
        print(f"{nome}: Processo de tentativa finalisado.")

def efetuar_pesquisa(nome, data_inicial, data_final, browser):
    # efetuando a pesquisa pelo fii desejado
    try:

        # formantado data para utlizá-la na url de pesquisa
        data_final_format = data_final.split('/')[2] + '-' + data_final.split('/')[1] + '-' + data_final.split('/')[0] 
        data_inicial_format = data_inicial.split('/')[2] + '-' + data_inicial.split('/')[1] + '-' + data_inicial.split('/')[0]  

        # realizando request 
        url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=18&palavra={nome}&dataInicial={data_inicial_format}&dataFinal={data_final_format}'        
        browser.get(url)     

        # processando e capturando dados
        # processando json retornado pelo request realizado anteriormente
        arquivo_json = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body")))
        html_arquivo_json = arquivo_json.get_attribute('outerHTML')
        soup_json = BeautifulSoup(html_arquivo_json, 'html.parser')
        list_dicionarios = json.loads(soup_json.text)
        
        # retornando lista com dados referente ao fundo imobiliário analisado
        # lista de dicionários, cuja qual, possui credenciais para acessar outras páginas no site da b3
        return list_dicionarios
   
    except:
        print("Erro! Pesquisa não pode ser solicitar.")

def encontrar_credenciais_noticia_qualificada(list_dicionarios_noticia):
    # econtrando o 'id' e 'dateTime' da notícia contendo o elemento 'Aviso aos Cotistas'    
    try:
        credenciais = []
        identificador = "Aviso aos Cotistas"

        # filtrando dicionário, cujo qual, possui o indentificador
        lista_dic_qualificado = (list(filter(lambda dicionario: identificador in str(dicionario['NwsMsg']['headline']) , list_dicionarios_noticia)))
        incremento_id = lista_dic_qualificado[-1]['NwsMsg']['id']
        incremento_data_noticia = lista_dic_qualificado[-1]['NwsMsg']['dateTime']        

        credenciais.append(incremento_id)
        credenciais.append(incremento_data_noticia)

        # retornando as credenciais encontradas 
        return credenciais

    except:
        print("Erro! Card qualificado não encotrado")

def solicitar_noticia_qualificada(credenciais_noticia, browser):
    # solicitando pele noticia na qual o elemento do card seja qualificado
    try:
        # inicinado requimento para a página de notícia encontrada
        url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Detail?idNoticia={credenciais_noticia[0]}&agencia=18&dataNoticia={credenciais_noticia[1]}'
        browser.get(url)
                
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

def formata_tabela_bot1(soup_tabela):
    # lista que armazena dados da tabela encontrada
    soup_dados = [] 
        
    # solicitando os dados no interior da tabela
    for span in soup_tabela.findAll('span', class_='dado-valores'):
        soup_dados.append(span.text)
    
    return soup_dados

def formata_valor_provento(soup_dados):

    # capturando da sopa html a string do 'valor do provento' e formatando-a para float
    string_valor_provento = soup_dados[5].split(',')
    valor_provento = float(string_valor_provento[0] + '.' + string_valor_provento[1])
    return valor_provento

def formata_data_base(soup_dados):
    
    # capturando 'data base' da sopa html
    data_base = (soup_dados[3])
    return data_base

def formata_data_pagamaneto_provento(soup_dados):

    # capturando 'data pagamento' da sopa html
    data_pagamento = (soup_dados[4])
    return data_pagamento

def formata_periodo_referencia(data_base, soup_dados, nome):

    #formatando a 'data referencia' utilizando a 'data base' como referencia
    data_referencia = data_base.split('/')
    # periodo_referencia é a chave primaria do banco de dados
    periodo_referencia = f"{nome}.{data_referencia[2]}.{data_referencia[1]}"
    return periodo_referencia
   