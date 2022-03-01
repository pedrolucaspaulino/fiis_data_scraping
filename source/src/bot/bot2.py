from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import bot1
import format_data

option = Options()
option.headless = True

def get_cotacao(browser, nome, dia):

    try:
        # formata a url para pesquisa
        url_nome = url_pesquisa(nome)
        # efetua a pesquisa e caputara a tabela retornando seu html (função aproveitado do bot1)
        soup_tabela = bot1.capturar_tabela(browser, '/html/body/table[3]/tbody/tr/td/table/tbody/tr/td/table[1]/tbody/tr[2]/td/table', url_nome)
        # encotra e retorna a cotação de fechamento seguindo como referência a data base
        cotacao = capturar_cotacao(soup_tabela, dia)
        return cotacao
    
    except:
        print("Erro! Não foi possível realizar a captura da cotação referente a data base.")


def url_pesquisa(nome):
    # formatando a url do fii desejado
    try:
        # função que formata a data para 'mes'/'ano' do mês anterior ao da data de execução do bot
        data_formatada = format_data.fun_data()    
        # url de pesquisa
        url = f'https://bvmf.bmfbovespa.com.br/SIG/FormConsultaMercVista.asp?strTipoResumo=RES_MERC_VISTA&strSocEmissora={nome}&strDtReferencia={data_formatada}&strIdioma=P&intCodNivel=2&intCodCtrl=160'
        
        
        return url

    except:
        print("Erro! Pesquisa não pode ser solicitar.")

def capturar_cotacao(soup_tabela, dia):
    try:
        tag_trs = []

        # percorre e armazena todas as linhas da tabela
        for tr in soup_tabela.find_all('tr'):
            tag_trs.append(tr)

        # encontra a linha com as cotações da qual é referente a data base
        for linha in range(tag_trs.__len__()):
            lista_linha = tag_trs[linha].text.split('\n')
            if dia in lista_linha[0]:
                num_linha = linha

        # seleciona a cotação de fechamento referente a data base
        linha_fundo_desejado = tag_trs[num_linha].text.split('\n')
        string_cotacao = (linha_fundo_desejado[-2]).replace(",", ".")
        cotacao_formatada = float(string_cotacao)

        return cotacao_formatada

    except:
        print("Erro! Tabela não pode ser capturada.")   