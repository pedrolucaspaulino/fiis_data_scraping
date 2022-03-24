import sqlite3
import pandas as pd

conexao = sqlite3.connect('projeto_cientifico/data/dados.db')
cursor = conexao.cursor()

def criando_tabela_infofii(nome_tabela):
    criando_sql = f"CREATE TABLE IF NOT EXISTS {nome_tabela} (nome TEXT, data_base TEXT, cotacao_data_base REAL, valor_provento REAL, data_pagamento TEXT, periodo_referencia TEXT PRIMARY KEY, dividend_yield REAL)"
    cursor.execute(criando_sql) 

# novos parametros para ser modificado: dodos, tabela
def insert_into_talela_infofii(nome, data_base, cotacao_data_base, valor_provento, data_pagamento, periodo_referencia, dividend_yield):
    try:
        criando_tabela_infofii(info_fii2)
        cursor.execute("INSERT INTO OR NOT info_fii2 VALUES (?,?,?,?,?,?,?)", (nome, data_base, cotacao_data_base, valor_provento, data_pagamento, periodo_referencia, dividend_yield))
        conexao.commit()
    except:
        print("Falha ao slavar no banco de dados")

def insert_into_talela(dados, nome_tabela):
    try:
        criando_tabela_infofii(nome_tabela)
        df = pd.DataFrame(dados)
        df.to_sql(nome_tabela, con=conexao, if_exists="append", index=False)
        conexao.commit()
    except:
        print("Falha ao slavar no banco de dados")