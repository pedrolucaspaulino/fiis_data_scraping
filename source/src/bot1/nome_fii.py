import pandas as pd
import lxml

def list_fii():

    code_list_of_REIT = []

    with open("projeto_cientifico/fiis/table_ifix.html", "r") as file:
        table_ifix = file.read()
        file.close()

    # pd.read_html return a list of DataFrames, in the html code "table_ifix" there is just
    # one table, so the slicing after the command is to pass the dataframe instead of a list with
    # just one DataFrame
    df_table_ifix = pd.read_html(table_ifix)[0]

    df_table_ifix = df_table_ifix.drop(columns=["Ação","Part. (%)", "Tipo", "Qtde. Teórica"])
    df_table_ifix = df_table_ifix.drop([103, 104])

    for x in range(0, len(df_table_ifix.values.tolist())):
        code_list_of_REIT.append(df_table_ifix.values.tolist()[x][0][0:4])

    return code_list_of_REIT
