import scraping_b3
import PySimpleGUI as sg
from functools import partial

def iniciar_tela():

    # tema da interface
    sg.change_look_and_feel('LightGreen9')

    # layout da interface
    layout = [  [sg.Text("Digite o fundo imobiliário desejado:")],
                [sg.Input(key='nome')],          
                [sg.Button('Pesquisar'), sg.Button('Sair')]]

    window = sg.Window('Web Scraping', layout)
    
    while True:

        event, values = window.read()    

        if event == sg.WIN_CLOSED or event == 'Sair':
            break
        
        # efetua pesquisa com as dados lidos
        if event == 'Pesquisar' and values['nome'] != '' :
            try:
                scraping = partial(scraping_b3.get_dados, '29/11/2021', '30/11/2021')
                scraping(values['nome'])
            except:
                print("Algo deu errado! Função get dados não pode ser chamada")
        else:
            print("Compos não preenchidos.")        
    
    window.close()         