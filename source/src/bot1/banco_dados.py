import sqlite3
import pandas as pd

conexao = sqlite3.connect('projeto_cientifico/data/dados.db')
cursor = conexao.cursor()

def criando_tabela_infofii():
    criando_sql = 'CREATE TABLE IF NOT EXISTS info_fii (nome TEXT, data_base TEXT, valor_provento REAL, periodo_referencia TEXT)'
    cursor.execute(criando_sql) 

# novos parametros para ser modificado: dodos, tabela
def insert_into_talela_infofii(nome, data_base, valor_provento, periodo_referencia):
    try:
        cursor.execute("INSERT INTO OR NOT info_fii VALUES (?,?,?,?)", (nome, data_base, valor_provento, periodo_referencia))
        conexao.commit()
    except:
        print("Falha ao slavar no banco de dados")

def insert_into_talela(dados, nome_tabela):
    try:
        df = pd.DataFrame(dados)
        df.to_sql(nome_tabela, con=conexao, if_exists="append", index=False)
        conexao.commit()
    except:
        print("Falha ao slavar no banco de dados")