# fiis_data_scraping

**fiis_data_scraping** é um bot, criado a partir de uma [iniciativa científica](https://pt.wikipedia.org/wiki/Inicia%C3%A7%C3%A3o_cient%C3%ADfica_j%C3%BAnior), cuja função tem de extrai dados de fundos imobiliários diretamente do site da B3 (Bolsa de Valores brasileira). 

Para obter infomações detalhadas sobre o funcionamento do porjeto acesse o [relatorio SIA](https://drive.google.com/file/d/1E3ZHYCcMQVnaateiQIzKCpCTFeISTFPk/view) e também o [vídeo de apresentação SIA](https://youtu.be/pbnMwXUm_eo) 

## Requisitos

Para executar este bot, são necessárias as seguintes bibliotecas:

| **Dependence Name** | **Comment**         |
|---------------------| ------------------- |
| Python (3.10)       |                     |
| Mozilla Firefox     | Web browser         |
| Geckodriver         | Needs to be in PATH |
| Beautiful Soup      | A Python Package    |
| Selenium            | A Python Package    |
| Requests            | A Python Package    |


- Essas bibliotecas estão listadas no arquivo `requirements.txt`. Para instalar todas as dependências, execute o seguinte comando:

````
pip install -r requirements.txt
````

Além disso, é necessário ter o Firefox instalado, já que o bot utiliza o driver do Firefox (geckodriver).

## Funcionalidades

O bot extrai os seguintes dados de cada fundo imobiliário:

- Data-base
- Valor do provento
- Período de referência
- Cotação de fechamento (referente à data-base do período de referência)

Com base nos dados extraídos, o bot calcula o "dividend yield" mensal de cada fundo imobiliário.

Os dados coletados são armazenados em um banco de dados SQLite, que é criado automaticamente na primeira execução do bot.

Para executar o bot, basta chamar o arquivo `main.py`. O bot irá extrair os dados de todos os fundos imobiliários listados na B3, do mês anterior ao mês atual.

## Licença

Este bot é uma iniciativa científica e está disponível sob a licença MIT. Sinta-se livre para utilizá-lo e modificá-lo da forma que desejar. Se possível, dê crédito ao autor original.