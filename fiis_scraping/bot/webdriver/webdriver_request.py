from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from logging import warning, debug

option = Options()
option.headless = True
geckodriver_log_path = "logs/geckodriver.log"


def request_webdriver(url: str, time: int, search_type: str, element: str) -> dict:
    """
        Responsável por realizar o request dos elementos desejados como parâmetro.

        Parameters:
            url (str): url de acesso à página solicitada.

            time (str): tempo limite de espera para o carregamento do elemento desejado presente na
             pesquisa solicitada.

            search_type (str): categoria de elemento a ser utilizado na como referencia na pesquisna

            element (str): elemento desejado de busca presente na página solicitada

        Returns:
            soup_page (BeautifulSoup): html do elemento desejado.
    """

    web_page_result = {"status": None, "html": None, "resume": None}
    browser = webdriver.Firefox(options=option, service_log_path=geckodriver_log_path)

    try:

        browser.get(url)
        web_page = WebDriverWait(browser, time).until(ec.presence_of_element_located((search_type, element)))
        html_page = web_page.get_attribute('outerHTML')
        soup_page = BeautifulSoup(html_page, 'html.parser')

        if web_page is not None:
            debug(f"Request realizado com sucesso!")
            web_page_result.update(status=True, html=soup_page, resume="Tabela obtida com sucesso!")

    except NoSuchElementException:
        warning("Elemento pesquisado não encontrado.")
        web_page_result.update(status=False, resume="Elemento buscado não encontrado.")

    except TimeoutException:
        warning("Tempo de busca exetido.")
        web_page_result.update(status=False, resume="Tempo de busca exetido.")

    except Exception as e:
        warning(f"Não foi possível realizar o request. {e}")
        web_page_result.update(status=False, resume=f"Erro insperado! {e}.")

    finally:
        browser.quit()
        return web_page_result
