from fiis_scraping.bot.collect_data.collector import collect_all_b3
from fiis_scraping.util.formata.formata_data import fun_data
from logging import basicConfig, FileHandler, StreamHandler, INFO


def main():
    perido_consulta = fun_data().replace("/", "-")

    # iniciando as configurações de log do programa
    # criando path para o arquivo log do programa
    path_file_log = f'logs/{perido_consulta.replace("/", "-")}_relatorio.log'

    # crindo especificações de log
    file_handler = FileHandler(path_file_log, "a")
    file_handler.setLevel(INFO)

    stream_handler = StreamHandler()

    basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s',
                level=INFO,
                handlers=[file_handler, stream_handler])

    # realizando a chamada da função
    # responsável por coletar todos os fundos
    # listados na B3 no período de consulta
    collect_all_b3(perido_consulta)


if __name__ == '__main__':
    main()
