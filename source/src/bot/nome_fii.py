from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def scrape_table():
    """
    # This bot is made to collect ID and percentage participation
    # of IFIX from B3's site by using HTML code
    """

    url = "https://sistemaswebb3-listados.b3.com.br/indexPage/theorical/IFIX?language=pt-br"  # noqa: E501

    # Setting up browser
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    # Accessing url and refreshing the page
    browser.get(url)
    browser.implicitly_wait(10)
    browser.refresh()
    browser.refresh()


    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[3]/div/table/tbody')))  # noqa: E501
    except:
        print("Table not found!")

    # By default, the table is set to 20 elements per page, by
    # using this command, selenium set 120 elements per page, which
    # means that there is just 1 page to scrape
    select_element = browser.find_element(By.XPATH, '//*[@id="selectPage"]')
    select_object = Select(select_element)

    # Try to select the last option, if any exception occurs, then
    # select the "120 elements per page" option
    try:
        all_available_options = select_object.options
        index_of_last_option = len(all_available_options) - 1
        select_object.select_by_index(index_of_last_option)
    except:
        select_object.select_by_visible_text("120")

    # Find the table
    table = browser.find_element(By.TAG_NAME, "table")

    # Get the HTML code of the table
    html_content = table.get_attribute("outerHTML")

    browser.quit()

    soup = BeautifulSoup(html_content, "html.parser")

    table_ifix = soup.find()

    with open("source/src/fiis/table_ifix.html", "w") as file:
        file.write(str(table_ifix))


def list_fii():
    code_list_of_REIT = []

    with open("source/src/fiis/table_ifix.html", "r") as file:
        table_ifix = file.read()
        file.close()

    # pd.read_html return a list of DataFrames, in the html code "table_ifix" there is just
    # one table, so the slicing after the command is to pass the dataframe instead of a list with
    # just one DataFrame
    df_table_ifix = pd.read_html(table_ifix)[0]

    df_table_ifix = df_table_ifix.drop(columns=["Ação", "Part. (%)", "Tipo", "Qtde. Teórica"])
    df_table_ifix = df_table_ifix.drop([103, 104])

    for index in range(0, len(df_table_ifix.values.tolist())):
        if '11' in df_table_ifix.values.tolist()[index][0][0:6]:
            code_list_of_REIT.append(df_table_ifix.values.tolist()[index][0][0:6])

    return code_list_of_REIT
