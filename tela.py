import scraping_b3
import PySimpleGUI as sg

def iniciar_tela():

    # tema da interface
    sg.change_look_and_feel('LightGreen9')

    # layout da interface
    layout = [  [sg.Text("Digite o fundo imobiliário desejado:")],
                [sg.Input(key='nome')],
                [sg.Text("Digite a data inicial: ")],
                [sg.Input(key='data_inicial')],
                [sg.Text("Digite a data final: ")],
                [sg.Input(key='data_final')],           
                [sg.Button('Pesquisar'), sg.Button('Sair')]]

    window = sg.Window('Web Scraping', layout)
    
    while True:

        event, values = window.read()    

        if event == sg.WIN_CLOSED or event == 'Sair':
            scraping_b3.adicionando_data_frame()
            break
        
        # efetua pesquisa com as dados lidos
        if event == 'Pesquisar' and values['nome'] != '' and values['data_inicial'] != '' and values['data_final'] != '':
            try:
                scraping_b3.get_dados(values['nome'], values['data_inicial'], values['data_final']) 
            except:
                print("Algo deu errado! Função get dados não pode ser chamada")
        else:
            print("Compos não preenchidos.")        
    
    window.close()         
