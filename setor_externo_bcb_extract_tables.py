import os
import requests
import pandas as pd
from datetime import datetime


# Função para criar uma pasta se não existir
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Função para baixar arquivos XLS ou XLSX de uma URL
def download_file(year, month):
    # Verifica se o ano é até 2017 para ajustar a extensão do arquivo
    if year <= 2017:
        extension = 'xls'
    else:
        extension = 'xlsx'
    
    # Construindo a URL com o ano, mês e extensão adequada
    month_str = f"{month:02d}"  # Garante que o mês seja no formato 01, 02, ..., 12
    url = f"https://www.bcb.gov.br/content/estatisticas/hist_estatisticassetorexterno/{year}{month_str}_Tabelas_de_estatisticas_do_setor_externo.{extension}"
    
    # Verificando se a URL existe
    response = requests.get(url)
    if response.status_code == 200:
        # Define o caminho da pasta onde os arquivos serão salvos
        base_folder = r"C:\Users\User\Desktop\mercado_exterior\Estatisticas do setor financeiro"
        folder_path = os.path.join(base_folder, f"BCB_{year}_{extension}")
        
        # Cria a pasta para o ano correspondente
        create_folder(folder_path)
        
        # Nome do arquivo
        file_name = f"Tabelas_de_estatisticas_do_setor_externo_{year}{month_str}.{extension}"
        file_path = os.path.join(folder_path, file_name)  
        
        # Baixando o arquivo...
        print(f"Baixando {file_name} para o ano {year}, mês {month_str}...")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Arquivo {file_name} salvo em {folder_path}.\n")
    else:
        print(f"Erro ao acessar a URL: {url}")

# Função para baixar arquivos para anos e meses
def download_files_for_years(start_year, end_year, current_month):
    for year in range(start_year, end_year + 1):
        # Determinar o mês de término para o ano final
        if year == end_year:
            last_month = current_month - 1  
        else:
            last_month = 12  

        for month in range(1, last_month + 1):  
            download_file(year, month)


data_atual = datetime.now()

# Definindo o ano inicial
ano_inicial = 2014

if data_atual.month == 1:
    ano_final = data_atual.year - 1  
    mes_final = 12  
else:
    ano_final = data_atual.year  
    mes_final = data_atual.month - 1  

download_files_for_years(ano_inicial, ano_final, mes_final)





