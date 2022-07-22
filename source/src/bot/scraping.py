from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bot1 import get_dados
from bot2 import get_cotacao
from format_data import data_inicial_final
from banco_dados import salvar_dados

option = Options()
option.headless = True

def execucao_tudo(nome):

    try:
        browser = webdriver.Firefox(options=option)

        # definindo datas inicias e finais para ser parâmentros de execução referente ao bot1
        datas = data_inicial_final()
        data_inicial = datas[0]
        data_final = datas[1]    

        # executando o bot1 e alocando os dados recebidos em uma variável
        dados_bot1 = get_dados(data_inicial, data_final, nome, browser)

        # definindo o dia baseando na 'data_base' para servir de parâmetro para o bot2
        data_base_formatada = dados_bot1[1].split('/')  
        dia = data_base_formatada[0]

        # executando o bot2 e alocando os dados recebidos em uma variável
        cotacao_data_base = get_cotacao(nome, dia, browser)

        # calculando o dividend_yield
        valor_provento = dados_bot1[4]
        dividend_yield = calcular_dividend_yield(cotacao_data_base, valor_provento)

        tab2 = (dados_bot1[3], cotacao_data_base, valor_provento, dividend_yield)
        tab1 = (dados_bot1[0:4])

        salvar_dados(tab1, tab2)
                    
        return False

    except:
        print("Erro! Falha ao concluir o scraping.")
        return True

    finally:
        browser.quit()


def get_tabela_nome_fiis():

    try:
        browser = webdriver.Firefox(options=option)
        scraping_html(browser)
        return True

    except:
        print("Erro! Falha ao capturar tabela nome Fiis.")
        return False

    finally:
        browser.quit()


def calcular_dividend_yield(cotacao, provento):

    try:
        dividend_yield = (provento/cotacao) * 100
        return dividend_yield

    except:
        print("Erro! Não foi possivel calcular o dividend yield")