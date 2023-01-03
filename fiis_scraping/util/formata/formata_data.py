from datetime import datetime


def fun_data() -> str:

    """
        Retorna-se o mês anterior à execução da função.

        Returns:
            data_formatada (str): mês anterior no formato '%m/%Y'.
    """

    # separando a data atual em 'mês' e 'ano'.
    data_atual = datetime.today().strftime('%m/%Y')
    fragmento_data = data_atual.split('/')
    # fazendo a associação as variáveis
    fragmento_data_mes = fragmento_data[0]
    fragmento_data_ano = fragmento_data[1]

    # subtrai menos um mês para efetuar a pesquisa do mês anterior.
    if int(fragmento_data_mes) > 1:
        data_formatada = str((int(fragmento_data_mes) - 1)) + '/' + fragmento_data_ano
    else:
        data_formatada = '12' + '/' + str((int(fragmento_data_ano) - 1))

    return data_formatada


def data_inicial_final(peridodo_referencia) -> dict:

    """
        Retorna um período dos últimos 30 dias do mês anterior à execução da função.

        Returns:
            datas (dict): contem a data_inicial e data_final do período encontrado.
    """

    datas = {"data_inicial": None,
             "data_final": None}

    peridodo_referencia = peridodo_referencia.split('/')

    mes = peridodo_referencia[0]
    ano = peridodo_referencia[1]

    # verificando se o ano é ano biossestos.
    if int(ano) % 4 == 0:
        ano_bissexto = True
    else:
        ano_bissexto = False

    # formatando string 'mes'.
    if int(mes) < 10:
        mes = '0' + mes

    # define um período dos últimos 30 dias referentes ao mês anterior à execução da função

    if mes == '02' and ano_bissexto:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '28' + '/' + mes + '/' + ano

    elif mes == '02' and ano_bissexto:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '29' + '/' + mes + '/' + ano

    elif mes == '01' or mes == '03' or mes == '05' or mes == '07' or mes == '08' or mes == '10' or mes == '12':
        data_inicial = '02' + '/' + mes + '/' + ano
        data_final = '31' + '/' + mes + '/' + ano

    else:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '30' + '/' + mes + '/' + ano

    datas.update(data_inicial=data_inicial)
    datas.update(data_final=data_final)

    # retorna o período de 30 dias refente ao mês anterior.
    return datas
