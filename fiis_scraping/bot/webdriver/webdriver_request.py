from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from colorama import Fore, Style
import colorama

colorama.init(autoreset=True)


def request_webdriver(browser: webdriver, url: str, time: int, search_type: str, element: str) -> dict:
    """
        Responsável por realizar o request dos elementos desejados como parâmetro.

        Parameters:
            browser: acessar a internet para possibilitar a extração de dados

            url (str): url de acesso à página solicitada.

            time (str): tempo limite de espera para o carregamento do elemento desejado presente na
             pesquisa solicitada.

            search_type (str): categoria de pesquisa utilizada

            element (str): elemento desejado de busca presente na página solicitada

        Returns:
            soup_page (BeautifulSoup): html do elemento desejado.
    """

    web_page = None
    web_page_result = {"status": None, "html": None, "resume": None}

    try:

        browser.get(url)

        # selecionado o conteúdo html da pagina de notícia encontrada
        if search_type.upper() == "ID":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.ID, element)))
        if search_type.upper() == "XPATH":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.XPATH, element)))
        if search_type.upper() == "CLASSNAME":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.CLASS_NAME, element)))
        if search_type.upper() == "CSSSELECTOR":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, element)))
        if search_type.upper() == "NAME":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.NAME, element)))
        if search_type.upper() == "TAGNAME":
            web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located(
                (By.TAG_NAME, element)))

        html_page = web_page.get_attribute('outerHTML')
        soup_page = BeautifulSoup(html_page, 'html.parser')

        if web_page is not None:
            print(f"{Fore.GREEN}{Style.BRIGHT}Request realizado com sucesso!\n")
            web_page_result.update(status=True, html=soup_page, resume="Tabela obtida com sucesso!")
            return web_page_result

    except NoSuchElementException:
        print(f"{Fore.RED}Erro! Elemento não encontrado.")
        web_page_result.update(status=False, resume="Elemento buscado não encontrado.")
        browser.quit()
        return web_page_result

    except TimeoutException:
        print(f"{Fore.RED}Erro! Tempo de busca exetido.")
        web_page_result.update(status=False, resume="Tempo de busca exetido.")
        browser.quit()
        return web_page_result

    print(f"{Fore.RED}Erro! Não foi possível realizar o request.")
    web_page_result.update(status=False, resume="Erro insperado! Não foi possível realizar o request.")
    browser.quit()
    return web_page_result
