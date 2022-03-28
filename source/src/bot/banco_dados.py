import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_fiis_datas(conn, dados):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO fiis_datas(nome, data_base, data_pagamento, periodo_referencia)
              VALUES(?,?,?,?) '''    

    cur = conn.cursor()
    cur.execute(sql, dados)
    conn.commit()

    return cur.lastrowid

def create_fiis_valores(conn, dados):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO fiis_valores(periodo_referencia, cotacao_data_base, valor_provento, dividend_yield)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, dados)
    conn.commit()

    return cur.lastrowid

def salvar_dados(dados_tab1, dados_tab2):
    database = 'projeto_cientifico/data/dados.db'

    sql_create_fiis_valores = """ CREATE TABLE IF NOT EXISTS fiis_valores (
                                        periodo_referencia TEXT PRIMARY KEY, 
                                        cotacao_data_base REAL, 
                                        valor_provento REAL,                                        
                                        dividend_yield REAL                                        
                                    ); """

    sql_create_fiis_datas = """ CREATE TABLE IF NOT EXISTS fiis_datas (
                                        nome TEXT,
                                        data_base TEXT,                                        
                                        data_pagamento TEXT,                                        
                                        periodo_referencia TEXT,   
                                        FOREIGN KEY (periodo_referencia) REFERENCES fiis_valores (periodo_referencia)                                 
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:

        # create projects table
        create_table(conn, sql_create_fiis_valores)
        create_table(conn, sql_create_fiis_datas)
        create_fiis_datas(conn, dados_tab1)
        create_fiis_valores(conn, dados_tab2)        

    else:
        print("Error! cannot create the database connection.")
