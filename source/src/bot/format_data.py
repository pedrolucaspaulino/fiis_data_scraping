from datetime import datetime


def fun_data() -> str:
    """
        Com base, no mês atual da execução desta função, retorna-se o mês anterior no formato '%m/%Y'
    """

    # separando a data atual em 'mês' e 'ano'
    data_atual = datetime.today().strftime('%m/%Y')
    fragmento_data = data_atual.split('/')
    # fazendo a associação as variáveis
    fragmento_data_mes = fragmento_data[0]
    fragmento_data_ano = fragmento_data[1]

    # subtrai menos um mês para efetuar a pesquisa do mês anterior
    if fragmento_data_mes != 1:
        data_formatada = str((int(fragmento_data_mes) - 1)) + '/' + fragmento_data_ano
    else:
        data_formatada = '12' + '/' + str((int(fragmento_data_ano) - 1))

    return data_formatada


def data_inicial_final() -> dict:
    """
        Com base, no mês atual da execução desta função, retornam-se duas datas
        referente ao período dos últimos 30 dias do mês anterior
    """

    datas = {"data_inicial": None,
             "data_final": None}

    data = fun_data().split('/')

    mes = data[0]
    ano = data[1]

    # verificando se o ano é ano biossestos
    if int(ano) % 4 == 0:
        ano_bissexto = True
    else:
        ano_bissexto = False

    # formatando string 'mes'
    if int(mes) < 10:
        mes = '0' + mes

    # verificando se o ano é bissexto

    if mes == '02' and ano_bissexto is False:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '28' + '/' + mes + '/' + ano

    elif mes == '02' and ano_bissexto is True:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '29' + '/' + mes + '/' + ano

    # define um período dos últimos 30 dias referentes ao mês anterior à execução da função

    elif mes == '01' or mes == '03' or mes == '05' or mes == '07' or mes == '08' or mes == '10' or mes == '12':
        data_inicial = '02' + '/' + mes + '/' + ano
        data_final = '31' + '/' + mes + '/' + ano

    else:
        data_inicial = '01' + '/' + mes + '/' + ano
        data_final = '30' + '/' + mes + '/' + ano

    datas.update(data_inicial=data_inicial)
    datas.update(data_final=data_final)

    # retorna o período de 30 dias refente ao mês anterior
    return datas
