import os
import pandas as pd
import re
import numpy as np
from pandas.tseries.offsets import DateOffset
import matplotlib.pyplot as plt
import re
import statsmodels.api as sm

import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Tentar importar o pacote e instalar caso não esteja presente
try:
    import plotly
except ImportError:
    print("Plotly não está instalado. Instalando...")
    install_package("plotly")
    import plotly  # Importa novamente após a instalação

# Código que usa o plotly
print(plotly.__version__)



# Caminho para o diretório base com os arquivos Excel
base_dir = r"C:\Users\User\Desktop\mercado_exterior\Estatisticas do setor financeiro"

# Para arquivos .xls
xls = pd.ExcelFile(r"C:\Users\User\Desktop\mercado_exterior\Estatisticas do setor financeiro\BCB_2017_xls\Tabelas_de_estatisticas_do_setor_externo_201704.xls")
print("Sheets disponíveis:", xls.sheet_names)

# Para arquivos .xlsx
xlsx = pd.ExcelFile(r"C:\Users\User\Desktop\mercado_exterior\Estatisticas do setor financeiro\BCB_2018_xlsx\Tabelas_de_estatisticas_do_setor_externo_201807.xlsx")
print("Sheets disponíveis:", xlsx.sheet_names)
################Correção do código

# Função para listar arquivos e subpastas
def listar_arquivos_subpastas(diretorio):
    for root, dirs, files in os.walk(diretorio):
        for dir in dirs:
            print(f"Diretório: {os.path.join(root, dir)}")
        
        for file in files:
            print(f"Arquivo: {os.path.join(root, file)}")

# Diretório base onde estão os arquivos
base_dir = r"C:\Users\User\Desktop\mercado_exterior\Estatisticas do setor financeiro"

# DataFrames para a categoria balanco
balanco_df_list = []

# Função para carregar um arquivo de Excel e processar os dados das tabelas de balanco
def carregar_balanco(file_path, month_year, ano, mes):
    try:
        # Verificar as sheets disponíveis no arquivo
        xls = pd.ExcelFile(file_path)
        print(f"Sheets disponíveis no arquivo {file_path}: {xls.sheet_names}")

        # Determinar a sheet correta com base no ano e mês
        if ano < 2018 or (ano == 2018 and mes < 4):
            balanco_sheet = 'Quadro 1'
        else:
            balanco_sheet = 'Tabela 1'
        
        # Verificar se a sheet está presente no arquivo
        if balanco_sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=balanco_sheet)
            df['Tabela'] = balanco_sheet  
            df['Data'] = month_year  
        else:
            # Se "Quadro 1" não estiver presente, tente "Tabela 1" para o ano de 2018 a partir d0 mes 05
            if (ano == 2018 and mes >= 5) and 'Tabela 1' in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name='Tabela 1')
                df['Tabela'] = 'Tabela 1'
                df['Data'] = month_year
                return df
            print(f"A sheet '{balanco_sheet}' não está presente no arquivo {file_path}. Sheets disponíveis: {xls.sheet_names}")
            return None

    except Exception as e:
        print(f"Erro ao carregar o arquivo {file_path}: {e}")
        return None

# Iterar pelas pastas de cada ano
for year_folder in os.listdir(base_dir):
    year_path = os.path.join(base_dir, year_folder)

    if os.path.isdir(year_path):  
        # Extrair o ano da pasta
        try:
            ano = int(year_folder.split('_')[1])  
        except Exception as e:
            print(f"Erro ao extrair o ano do diretório {year_folder}: {e}")
            continue
        
        # Iterar pelos arquivos em cada subdiretório de ano
        for file_name in os.listdir(year_path):
            # Usar regex para verificar se o nome do arquivo contém a data no formato YYYYMM
            match = re.search(r'(\d{4})(\d{2})', file_name)
            if match:
                ano_arquivo = int(match.group(1))
                mes = int(match.group(2))
                # Definir a extensão correta com base na data
                if (ano_arquivo < 2018) or (ano_arquivo == 2018 and mes <= 4):
                    # Usar .xls até 04/2018
                    if file_name.endswith(".xls"):
                        file_path = os.path.join(year_path, file_name)
                        month_year = match.group(0)
                        df = carregar_balanco(file_path, month_year, ano_arquivo, mes)
                        if df is not None:
                            balanco_df_list.append(df)
                else:
                    # Usar .xlsx a partir de 05/2018
                    if file_name.endswith(".xlsx"):
                        file_path = os.path.join(year_path, file_name)
                        month_year = match.group(0)
                        df = carregar_balanco(file_path, month_year, ano_arquivo, mes)
                        if df is not None:
                            balanco_df_list.append(df)

# Função para salvar o DataFrame 
def salvar_csv(df_list, output_path):
    if df_list:
        merged_df = pd.concat(df_list, axis=0)
        merged_df.set_index('Data', inplace=True)  
        merged_df.to_csv(output_path)
        print(f"Arquivo salvo com sucesso: {output_path}")
    else:
        print(f"Nenhum DataFrame encontrado para {output_path}")

# Salvando o arquivo
salvar_csv(balanco_df_list, r"C:\Users\User\Desktop\mercado_exterior\balanco.csv")


###################################################################################################################
#limpeza banco de dados e seleção das variáveis de interesse

balanco = pd.read_csv(r"C:\Users\User\Desktop\mercado_exterior\balanco.csv")

balanco.columns



balanco['US$ milhões'] = np.where(
    balanco['Data'].astype(str).str[-2:].astype(int) <= 2,
    balanco['Unnamed: 3'],
    balanco['Unnamed: 4']
)

# Colunas desejadas
balanco_mes = balanco[['Data', 'Quadro I – Balanço de pagamentos', 'US$ milhões']]
balanco_mes = balanco_mes.rename(columns={'Quadro I – Balanço de pagamentos': 'tipo_investimento'})

# Limpeza do DataFrame
balanco_mes = balanco_mes.dropna(subset=[balanco_mes.columns[1], balanco_mes.columns[2]])
balanco_mes = balanco_mes[~balanco_mes[balanco_mes.columns[1]].isin(["Discriminação"])]


tabela = balanco[['Data', 'Tabela 1 – Balanço de pagamentos', 'US$ milhões']]
tabela = tabela.rename(columns={'Tabela 1 – Balanço de pagamentos': 'tipo_investimento'})
tabela = tabela.dropna(subset=[tabela.columns[1]])
tabela = tabela[~tabela[tabela.columns[1]].isin(["Discriminação"])]

# Concatenando os DataFrames
balanco_mes = pd.concat([balanco_mes, tabela], ignore_index=True)


balanco_mes.head(50)


#################Investimentos diretos no país
idp_index = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['      No país', '   Investimento direto no país'])].index
idp_index

indices_selecionados = []
for idx in idp_index:
    indices_selecionados.extend([idx, idx + 1, idx + 2])

IDP = balanco_mes.loc[indices_selecionados]
IDP
#################Investimentos em carteira ativos
ica_index = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['    Investimentos em carteira'])].index
ica_index_2 = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['   Investimento em carteira – ativos'])].index

indices_selecionados = []
for idx in ica_index:
    indices_selecionados.extend([idx, idx + 2, idx + 3])

indices_selecionados_2 = []
for idx in ica_index_2:
    indices_selecionados.extend([idx, idx + 1, idx + 2])


indices_totais = indices_selecionados + indices_selecionados_2
indices_totais = sorted(set(indices_totais))
ICA = balanco_mes.loc[indices_totais]
ICA

#################Investimentos em carteira passivos
icp_index = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['    Investimentos em carteira'])].index
icp_index_2 = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['   Investimento em carteira – passivos'])].index
balanco_mes['tipo_investimento'].unique()

indices_selecionados = []
for idx in icp_index:
    indices_selecionados.extend([idx, idx + 5, idx + 6])

indices_selecionados_2 = []
for idx in icp_index_2:
    indices_selecionados.extend([idx, idx + 1, idx + 2])

indices_totais = indices_selecionados + indices_selecionados_2
indices_totais = sorted(set(indices_totais))
ICP = balanco_mes.loc[indices_totais]
ICP

#################Derivativos
derivativos = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['    Derivativos', '   Derivativos – ativos e passivos'])]
derivativos

##################Outros investimentos
outros_investimentos_passivos_index = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['    Outros investimentos1/'])].index
outros_investimentos_passivos_index
print(balanco_mes.at[37, 'tipo_investimento'])
balanco[balanco.columns[1]].unique()
outros_investimentos_passivos_index
indices_selecionados = []
for idx in outros_investimentos_passivos_index:
    indices_selecionados.extend([idx+2])

outros_investimentos_passivos_1 = balanco_mes.loc[indices_selecionados]
outros_investimentos_passivos_1
outros_investimentos_passivos = balanco_mes[balanco_mes[balanco_mes.columns[1]].isin(['   Outros investimentos – passivos4/', '   Outros investimentos – passivos6/'])]
outros_investimentos_passivos  = pd.concat([outros_investimentos_passivos_1, outros_investimentos_passivos])

outros_investimentos_passivos.to_csv(r"C:\Users\User\Desktop\mercado_exterior\dfs_ETL\outros_investimentos_passivos.csv")
IDP.to_csv(r"C:\Users\User\Desktop\mercado_exterior\dfs_ETL\IDP.csv")
ICA.to_csv(r"C:\Users\User\Desktop\mercado_exterior\dfs_ETL\ICA.csv")
ICP.to_csv(r"C:\Users\User\Desktop\mercado_exterior\dfs_ETL\ICP.csv")
derivativos.to_csv(r"C:\Users\User\Desktop\mercado_exterior\dfs_ETL\derivativos.csv")

#corrigindo a data (estavam com as datas do relatório)
IDP['Data'].dtype
IDP['Data'] = IDP['Data'] = pd.to_datetime(IDP['Data'], format='%Y%m', errors='coerce')
IDP= IDP.rename(columns={'Data': 'Data_rel'})
IDP['Data'] = IDP['Data_rel'] - DateOffset(months=1)
IDP['Data'] = IDP['Data'].dt.strftime('%m-%Y')
cols = list(IDP.columns)  
cols.insert(1, cols.pop(cols.index('Data')))  
IDP = IDP[cols] 
IDP.head()


ICA['Data'].dtype
ICA['Data'] = ICA['Data'] = pd.to_datetime(ICA['Data'], format='%Y%m', errors='coerce')
ICA= ICA.rename(columns={'Data': 'Data_rel'})
ICA['Data'] = ICA['Data_rel'] - DateOffset(months=1)
ICA['Data'] = ICA['Data'].dt.strftime('%m-%Y')
cols = list(ICA.columns)  
cols.insert(1, cols.pop(cols.index('Data')))  
ICA = ICA[cols] 
ICA.head()



outros_investimentos_passivos['Data'] = pd.to_datetime(outros_investimentos_passivos['Data'], format='%Y%m', errors='coerce')
outros_investimentos_passivos = outros_investimentos_passivos.rename(columns={'Data':'Data_rel'})
outros_investimentos_passivos['Data'] = outros_investimentos_passivos['Data_rel'] - DateOffset(months=1) 
outros_investimentos_passivos['Data'] = outros_investimentos_passivos['Data'].dt.strftime('%m-%Y')
cols = list(outros_investimentos_passivos.columns)  
cols.insert(1, cols.pop(cols.index('Data')))  
outros_investimentos_passivos = outros_investimentos_passivos[cols]
outros_investimentos_passivos



ICP['Data'] = pd.to_datetime(ICP['Data'], format='%Y%m', errors='coerce')
ICP = ICP.rename(columns={'Data':'Data_rel'})
ICP['Data'] = ICP['Data_rel'] - DateOffset(months=1) 
ICP['Data'] = ICP['Data'].dt.strftime('%m-%Y')
cols = list(ICP.columns)  
cols.insert(1, cols.pop(cols.index('Data')))  
ICP = ICP[cols]
ICP


derivativos['Data'] = pd.to_datetime(derivativos['Data'], format='%Y%m', errors='coerce')
derivativos = derivativos.rename(columns={'Data':'Data_rel'})
derivativos['Data'] = derivativos['Data_rel'] - DateOffset(months=1) 
derivativos['Data'] = derivativos['Data'].dt.strftime('%m-%Y')
cols = list(derivativos.columns)  
cols.insert(1, cols.pop(cols.index('Data')))  
derivativos = derivativos[cols]
derivativos



####################Gráficos
print(balanco.columns)

idp_percent_pib_values = balanco[
    balanco['Quadro I – Balanço de pagamentos'].isin(['IED/PIB (%) ', '   Investimento direto no país / PIB (%)']) |
    balanco['Tabela 1 – Balanço de pagamentos'].isin(['IED/PIB (%) ', '   Investimento direto no país / PIB (%)'])
]

# Exibindo os valores correspondentes
idp_percent_pib_values

# Filtrando para obetr os valores do ano
idp_percent_pib_values = idp_percent_pib_values[idp_percent_pib_values['Data'].astype(str).str.endswith('06')]

# Selecionando apenas as colunas 'Data' e 'Unnamed: 3'
idp_percent_pib_values = idp_percent_pib_values[['Data', 'Unnamed: 3']]

idp_percent_pib_values

#corrigindo o ano
idp_percent_pib_values = idp_percent_pib_values[idp_percent_pib_values['Data'].astype(str).str.match(r'^\d{4}')]

# Convertendo a coluna 'Data' para string
idp_percent_pib_values['Data'] = idp_percent_pib_values['Data'].astype(str)

# Filtrando as linhas onde 'Data' começa com um ano (formato YYYY)
filtered_data = idp_percent_pib_values[idp_percent_pib_values['Data'].str.match(r'^\d{4}')]

# Extraindo o ano (YYYY) e criando a coluna 'Ano' com YYYY-1
filtered_data['Ano'] = filtered_data['Data'].str[:4].astype(int) - 1

# Exibindo o resultado
filtered_data =filtered_data.rename(columns = { 'Unnamed: 3': '  Investimento direto no país / PIB (%)'})
filtered_data = filtered_data.drop(columns= ['Data'])
cols = ['Ano'] + [col for col in filtered_data.columns if col != 'Ano']
filtered_data = filtered_data[cols]
filtered_data['  Investimento direto no país / PIB (%)'] = pd.to_numeric(filtered_data['  Investimento direto no país / PIB (%)'])
filtered_data[filtered_data.columns[1]] = filtered_data[filtered_data.columns[1]].round(2)
filtered_data
filtered_data.to_excel(r"C:\Users\User\Desktop\mercado_exterior\fluxo_anula_idp.xlsx")

#preparando dados para gráficos comparativos 

IDP['tipo_investimento'].unique()


idp_part_capital=IDP[IDP['tipo_investimento'].isin(['        Participação no capital', 
                                             '      Participação no capital5/', 
                                             '      Participação no capital'])]

idp_part_capital['US$ milhões'] = (pd.to_numeric(idp_part_capital['US$ milhões'])/1000).round(3)
idp_part_capital = idp_part_capital.rename(columns={'US$ milhões': 'US$ bilhões'})
idp_part_capital


IDP['tipo_investimento'].unique()
idp_oper_intercomp = IDP[IDP['tipo_investimento'].isin(['        Empréstimos intercompanhias',
                                                       '      Operações intercompanhia' ])]
idp_oper_intercomp['US$ milhões'] = (pd.to_numeric(idp_oper_intercomp['US$ milhões'])/1000).round(3)
idp_oper_intercomp = idp_oper_intercomp.rename(columns={'US$ milhões': 'US$ bilhões'})
idp_oper_intercomp


ICA['tipo_investimento'].unique()
ica_acoes = ICA[ICA['tipo_investimento'].isin(['        Ações',
                                               '      Ações e cotas em fundos',
                                               ])]
ica_acoes ['US$ milhões'] = (pd.to_numeric(ica_acoes['US$ milhões'])/1000).round(4)
ica_acoes = ica_acoes.rename(columns={'US$ milhões': 'US$ bilhões'})
ica_acoes

ica_titulos_dividas = ICA[ICA['tipo_investimento'].isin(['        Títulos de renda fixa',
                                                         '      Títulos de renda fixa',
                                                         '      Títulos de dívida'])]
ica_titulos_dividas['US$ milhões'] = (pd.to_numeric(ica_titulos_dividas['US$ milhões'])/1000).round(3)
ica_titulos_dividas = ica_titulos_dividas.rename(columns = {'US$ milhões': 'US$ bilhões'})
ica_titulos_dividas


ICP['tipo_investimento'].unique()
icp_acoes = ICP[ICP['tipo_investimento'].isin(['        Ações',
                                               '      Ações e cotas em fundos'])]
icp_acoes['US$ milhões'] = (pd.to_numeric(icp_acoes['US$ milhões'])/1000).round(3)
icp_acoes = icp_acoes.rename(columns = {'US$ milhões': 'US$ bilhões'})
icp_acoes


icp_titulos_dividas = ICP[ICP['tipo_investimento'].isin(['        Títulos de renda fixa',
                                                        '      Títulos de renda fixa',
                                                          '      Títulos de dívida'])]
icp_titulos_dividas['US$ milhões'] = (pd.to_numeric(icp_titulos_dividas['US$ milhões'])/1000).round(3)
icp_titulos_dividas = icp_titulos_dividas.rename(columns={'US$ milhões': 'US$ bilhões'})
icp_titulos_dividas


derivativos['US$ milhões'] = (pd.to_numeric(derivativos['US$ milhões'])/1000).round(3)
derivativos = derivativos.rename(columns = {'US$ milhões': 'US$ bilhões'})
derivativos

outros_investimentos_passivos['US$ milhões'] = (pd.to_numeric(outros_investimentos_passivos['US$ milhões'])/1000).round(4)
outros_investimentos_passivos = outros_investimentos_passivos.rename(columns={'US$ milhões': 'US$ bilhões'})
outros_investimentos_passivos

####Consolidando os dfs
dfs = {
    'idp_part_capital': idp_part_capital,
    'idp_oper_intercomp': idp_oper_intercomp,
    'ica_acoes': ica_acoes,
    'ica_titulos_dividas': ica_titulos_dividas,
    'icp_acoes': icp_acoes,
    'icp_titulos_dividas': icp_titulos_dividas,
    'derivativos': derivativos,
    'outros_investimentos_passivos': outros_investimentos_passivos
}

# Renomeando a coluna 'US$ bilhões' de cada DataFrame com o nome do DataFrame 
idp_part_capital_grafic = idp_part_capital[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'idp_part_capital'})
idp_oper_intercomp_grafic = idp_oper_intercomp[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'idp_oper_intercomp'})
ica_acoes_grafic = ica_acoes[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'ica_acoes'})
ica_titulos_dividas_grafic = ica_titulos_dividas[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'ica_titulos_dividas'})
icp_acoes_grafic = icp_acoes[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'icp_acoes'})
icp_titulos_dividas_grafic = icp_titulos_dividas[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'icp_titulos_dividas'})
derivativos_grafic = derivativos[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'derivativos'})
outros_investimentos_passivos_grafic = outros_investimentos_passivos[['Data', 'US$ bilhões']].rename(columns={'US$ bilhões': 'outros_investimentos_passivos'})

# Realizando o merge 
df_final = idp_part_capital_grafic.merge(idp_oper_intercomp_grafic, on='Data', how='outer') \
    .merge(ica_acoes_grafic, on='Data', how='outer') \
    .merge(ica_titulos_dividas_grafic, on='Data', how='outer') \
    .merge(icp_acoes_grafic, on='Data', how='outer') \
    .merge(icp_titulos_dividas_grafic, on='Data', how='outer') \
    .merge(derivativos_grafic, on='Data', how='outer') \
    .merge(outros_investimentos_passivos_grafic, on='Data', how='outer')



df_final.head(30)
df_final.columns



### Anual
data_inicial = balanco['Data'].min()
data_inicial = str(data_inicial)
data_inicial = data_inicial[0:4]
data_inicial = pd.to_numeric(data_inicial)
data_final = balanco['Data'].max()
data_final = str(data_final)
data_final = data_final[0:4]
data_final = pd.to_numeric(data_final)


intervalo_anos = list(range(data_inicial, data_final + 1))
balanco_anual = pd.DataFrame({'Ano': intervalo_anos})
balanco_anual
balanco_anual['Data'] = balanco_anual['Ano'].apply(lambda x: int(f"{x}12"))
balanco_anual.head(30)
balanco_anual['Ano'].unique()
#balanco = balanco.drop(columns=['Ano'])
balanco_anual.head(30)
# Extraindo apenas o ano da coluna Data em balanco
balanco_anual = balanco_anual.merge(balanco, on='Data', how='inner')
balanco_anual.head(30)
balanco_anual.columns

balanco_anual = balanco_anual[['Ano', 'Unnamed: 3', 'Quadro I - Balanço de pagamentos', 'Quadro I – Balanço de pagamentos', 'Tabela 1 – Balanço de pagamentos']]
balanco_anual.head(80)
balanco_anual.to_csv(r"C:\Users\User\Desktop\mercado_exterior\balanco_anual.csv")

#################Investimentos diretos no país
# Filtrando o df correto (balanco_anual)
idp_index_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['      No país', '   Investimento direto no país'])].index
idp_index_anual

indices_selecionados = []
for idx in idp_index_anual:
    indices_selecionados.extend([idx, idx + 1, idx + 2])

IDP_anual = balanco_anual.loc[indices_selecionados]
IDP
#################Investimentos em carteira ativos
ica_index_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['    Investimentos em carteira'])].index
ica_index_2_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['   Investimento em carteira – ativos'])].index

indices_selecionados = []
for idx in ica_index_anual:
    indices_selecionados.extend([idx, idx + 2, idx + 3])

indices_selecionados_2 = []
for idx in ica_index_2_anual:
    indices_selecionados.extend([idx, idx + 1, idx + 2])


indices_totais_anual = indices_selecionados + indices_selecionados_2
indices_totais_anual = sorted(set(indices_totais_anual))
ICA_anual = balanco_anual.loc[indices_totais_anual]
ICA

#################Investimentos em carteira passivos
icp_index_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['    Investimentos em carteira'])].index
icp_index_2_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['   Investimento em carteira – passivos'])].index


indices_selecionados = []
for idx in icp_index_anual:
    indices_selecionados.extend([idx, idx + 5, idx + 6])

indices_selecionados_2 = []
for idx in icp_index_2_anual:
    indices_selecionados.extend([idx, idx + 1, idx + 2])

indices_totais_anual = indices_selecionados + indices_selecionados_2
indices_totais_anual = sorted(set(indices_totais_anual))
ICP_anual = balanco_anual.loc[indices_totais_anual]
ICP_anual

#################Derivativos
derivativos_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['    Derivativos', '   Derivativos – ativos e passivos'])]
derivativos_anual

##################Outros investimentos
outros_investimentos_passivos_index_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['    Outros investimentos1/'])].index
outros_investimentos_passivos_index_anual

outros_investimentos_passivos_index_anual
indices_selecionados = []
for idx in outros_investimentos_passivos_index_anual:
    indices_selecionados.extend([idx+2])

outros_investimentos_passivos_1_anual = balanco_anual.loc[indices_selecionados]
outros_investimentos_passivos_1_anual
outros_investimentos_passivos_anual = balanco_anual[balanco_anual[balanco_anual.columns[1]].isin(['   Outros investimentos – passivos4/', '   Outros investimentos – passivos6/'])]
outros_investimentos_passivos_anual
outros_investimentos_passivos_anual_completo  = pd.concat([outros_investimentos_passivos_1_anual, outros_investimentos_passivos_anual])
outros_investimentos_passivos_anual_completo

balanco_anual.columns
balanco_anual['tipo_investimento'] = balanco_anual['Quadro I – Balanço de pagamentos'].fillna(balanco_anual['Tabela 1 – Balanço de pagamentos'])
balanco_anual = balanco_anual[['Ano', 'Unnamed: 3', 'tipo_investimento']]
balanco_anual = balanco_anual.rename(columns={'Unnamed: 3': 'US$ milhões'})
balanco_anual = balanco_anual.dropna(subset=['US$ milhões'])
balanco_anual = balanco_anual.dropna(subset=['tipo_investimento'])
balanco_anual = balanco_anual[~balanco_anual['tipo_investimento'].isin(['Discriminação'])]
balanco_anual.head(30)

coluna_a_mover = balanco_anual.columns[2]
novas_colunas = [balanco_anual.columns[0], coluna_a_mover] + [col for i, col in enumerate(balanco_anual.columns) if i not in [0, 2]]
balanco_anual = balanco_anual[novas_colunas]
balanco_anual = balanco_anual[balanco_anual['US$ milhões'] != 'Ano']
balanco_anual
balanco_anual['tipo_investimento'].unique()

index_ver = balanco_anual[balanco_anual['tipo_investimento'].isin(['    Outros investimentos1/'])].index
index_ver
valores_para_remover = ['  Balança comercial (FOB)', '    Exportações', '    Importações',
       '  Serviços', '  Rendas',
       '  Transferências unilaterais correntes (líquido)',
       'Transações correntes', 'Conta capital e financeira',
       '  Conta capital', '  Conta financeira',
       '    Investimento direto (líquido)', 
       'Erros e omissões', 'Variação de reservas ( - = aumento)',
       'Resultado global do balanço', 'Transações correntes/PIB (%)',
       'IED/PIB (%) ', 'I. Transações correntes',
       '   Balança comercial (bens)', '      Exportações1/',
       '      Importações2/', '   Serviços', '   Renda primária',
       '   Renda secundária', 'II. Conta capital',
       'III. Conta financeira3/', 
       '   Investimento direto no país / PIB (%)',
       
       '   Outros investimentos – ativos4/','   Transações correntes / PIB (%)', '   Ativos de reserva'
       ]
balanco_anual = balanco_anual[~balanco_anual['tipo_investimento'].isin(valores_para_remover)]
balanco_anual

exterior_index = balanco_anual[balanco_anual['tipo_investimento'].isin(['      No exterior', '   Investimento direto no exterior'])].index
exterior_index

indices_selecionados = []
for idx in exterior_index:
    indices_selecionados.extend([idx, idx+1, idx+2])
balanco_anual = balanco_anual.drop(indices_selecionados).reset_index(drop=True)

der_index = balanco_anual[balanco_anual['tipo_investimento'].isin(['    Derivativos'])].index
der_index

indices_selecionados = []
for idx in der_index:
    indices_selecionados.extend([idx+1])
balanco_anual = balanco_anual.drop(indices_selecionados).reset_index(drop=True)


ic_index = balanco_anual[balanco_anual['tipo_investimento'] == '    Investimentos em carteira'].index
ic_index
balanco_anual['tipo_investimento'].unique()
#Há uma observação Ativos logo após outros_investimentos para alguns anos. Preciso remover ante do calculo
indices_para_remover = []
for idx in ic_index:
    # Verificando se existe uma linha seguinte e se ela contém 'Ativos' no 'tipo_investimento'
    if (idx + 1 in balanco_anual.index and 'Ativos' in balanco_anual.loc[idx + 1, 'tipo_investimento']) or \
        (idx + 2 in balanco_anual.index and 'Ações' in balanco_anual.loc[idx + 2, 'tipo_investimento']) or \
            (idx + 3 in balanco_anual.index and 'Títulos de renda fixa' in balanco_anual.loc[idx + 3, 'tipo_investimento']) or\
                (idx + 4 in balanco_anual.index and 'Passivos' in balanco_anual.loc[idx + 4, 'tipo_investimento']):
        indices_para_remover.extend([idx + 1, idx + 2, idx + 3, idx + 4])
balanco_anual = balanco_anual.drop(indices_para_remover).reset_index(drop = True)
balanco_anual['tipo_investimento'].unique()

ic_ativo_index = balanco_anual[balanco_anual['tipo_investimento'] == '   Investimento em carteira – ativos'].index
ic_ativo_index
#Há uma observação Ativos logo após outros_investimentos para alguns anos. Preciso remover ante do calculo
indices_para_remover = []
for idx in ic_ativo_index:
    # Verificando se existe uma linha seguinte e se ela contém 'Ativos' no 'tipo_investimento'
    if (idx + 1 in balanco_anual.index and 'Ações e cotas em fundos' in balanco_anual.loc[idx + 1, 'tipo_investimento']) or \
        (idx + 2 in balanco_anual.index and ('Títulos de renda fixa' in balanco_anual.loc[idx + 2, 'tipo_investimento'] or 'Títulos de dívida' in balanco_anual.loc[idx + 2, 'tipo_investimento'])):
        indices_para_remover.extend([idx, idx + 1, idx + 2])
balanco_anual = balanco_anual.drop(indices_para_remover).reset_index(drop = True)
balanco_anual['tipo_investimento'].unique()


outros_invest_index = balanco_anual[balanco_anual['tipo_investimento'] == '    Outros investimentos1/'].index
outros_invest_index


indices_para_remover = []
for idx in outros_invest_index:
    # Verificando se existe uma linha seguinte e se ela contém 'Ativos' no 'tipo_investimento'
    if (idx + 1 in balanco_anual.index and 'Ativos' in balanco_anual.loc[idx + 1, 'tipo_investimento']):
        indices_para_remover.append(idx + 1)
balanco_anual = balanco_anual.drop(indices_para_remover).reset_index(drop = True)

balanco_anual['tipo_investimento'].unique()


balanco_anual['US$ milhões'] = (pd.to_numeric(balanco_anual['US$ milhões'])/1000).round(3)
balanco_anual = balanco_anual.rename(columns={'US$ milhões': 'US$ bilhões'})
balanco_anual['tipo_investimento'].unique()
balanco_anual.head(30)
balanco_anual['Ano'].unique()
substituicoes = {
    '      Passivos' : '   Outros investimentos – passivos',
    '      Participação no capital5/': '        Participação no capital',
    '      Participação no capital': '        Participação no capital',
    '    Investimentos em carteira': '   Investimento em carteira – passivos',
    '        Ações': '      Ações e cotas em fundos',
    '        Títulos de renda fixa': '      Títulos de dívida',
    '      Títulos de renda fixa': '      Títulos de dívida',
    '        Empréstimos intercompanhias': '      Operações intercompanhia',
    '   Outros investimentos – passivos6/': '   Outros investimentos – passivos',
    '   Outros investimentos – passivos4/': '   Outros investimentos – passivos',
    '    Derivativos': '   Derivativos – ativos e passivos'
    
}
balanco_anual['tipo_investimento'].unique()
derivativos_index = balanco_anual[balanco_anual['tipo_investimento'] == '    Derivativos'].index
indices_para_remover = [idx + 1 for idx in derivativos_index if idx + 1 in balanco_anual.index]
balanco_anual = balanco_anual.drop(indices_para_remover).reset_index(drop=True)
balanco_anual['tipo_investimento'] = balanco_anual['tipo_investimento'].replace('      Passivos', 'Outros investimentos passivos')
valores_para_remover = ['    Outros investimentos1/', '   Outros investimentos – ativos6/']
balanco_anual = balanco_anual[~balanco_anual['tipo_investimento'].isin(valores_para_remover)].reset_index(drop=True)
substituicoes = {
    '      Participação no capital5/': '      Participação no capital',
    '   Outros investimentos – passivos6/': '   Outros investimentos – passivos',
    '   Outros investimentos – passivos4/': '   Outros investimentos – passivos'
}

balanco_anual['tipo_investimento'] = balanco_anual['tipo_investimento'].replace(substituicoes)
balanco_anual_1 = balanco_anual.drop_duplicates(subset=['Ano', 'tipo_investimento'])
print(balanco_anual_1)
print(type(balanco_anual_1))

balanco_anual_1.to_excel(r"C:\Users\User\Desktop\mercado_exterior\balanco_anual.xlsx")

balanco_anual_1.columns
balanco_anual_1['tipo_investimento'].unique()
balanco_anual_1['tipo_investimento'] = balanco_anual_1['tipo_investimento'].str.strip()

# Substituições
substituicoes = {
    'Empréstimos intercompanhias': 'Operações intercompanhia',
    'Títulos de renda fixa': 'Títulos de dívida',
    'Ações': 'Ações e cotas em fundos',
    'Derivativos': 'Derivativos – ativos e passivos',
    'Outros investimentos passivos': 'Outros investimentos – passivos',
    'No país': 'Investimento direto no país',
    'Participação no capital': 'Participação no capital'
}
balanco_anual_1['tipo_investimento'] = balanco_anual_1['tipo_investimento'].replace(substituicoes)
print(balanco_anual_1[balanco_anual_1['Ano'] == 2023])
balanco_anual_1['tipo_investimento'].unique()

#Necessário em função da presença de subgrupos que ja são contabilizados nos grupos proncipais
grupos_principais = [
     'Participação no capital',
       'Operações intercompanhia',
       'Ações e cotas em fundos', 'Títulos de dívida',
       'Derivativos – ativos e passivos',
       'Outros investimentos – passivos']

balanco_anual_principais = balanco_anual_1[balanco_anual_1['tipo_investimento'].isin(grupos_principais)]
balanco_anual_principais.head(10)
# Calculando o total anual apenas para os grupos principais
tot_ano = balanco_anual_principais[balanco_anual_principais['tipo_investimento'].isin(grupos_principais)].groupby('Ano')['US$ bilhões'].sum()
tot_ano
# Atribuindor o total anual ao df completo, sem filtrar
balanco_anual_principais['tot_ano'] = balanco_anual_principais['Ano'].map(tot_ano)

balanco_anual_principais.head(10)

balanco_anual_principais.columns
balanco_anual_principais['tipo_investimento'].unique()

balanco_anual_principais.to_excel(r"C:\Users\User\Desktop\mercado_exterior\balanco_anual_subgrupos.xlsx")

####Gráfico de barras empilhadas
df = balanco_anual_principais
df['tipo_investimento'] = df['tipo_investimento'].str.strip()


color_map = {
    'Participação no capital': "#26547C",         
    'Operações intercompanhia': "#4A7B76",        
    'Ações e cotas em fundos': "#B2A566",         
    'Títulos de dívida': "#FFD97D",               
    'Derivativos – ativos e passivos': "#FFF9B0", 
    'Outros investimentos – passivos': "#B0B5B3"  
}


df_pivot = df.pivot(index='Ano', columns='tipo_investimento', values='US$ bilhões').fillna(0)
colors = [color_map.get(tipo.strip(), "#607D8B") for tipo in df_pivot.columns]  # Cinza se não estiver no color_map

# Configurando o gráfico de barras bidirecionais
fig, ax = plt.subplots(figsize=(12, 8))

# Iterando
bottom_positive = np.zeros(len(df_pivot.index))
bottom_negative = np.zeros(len(df_pivot.index))

for idx, tipo in enumerate(df_pivot.columns):
    values = df_pivot[tipo].values
    pos_values = np.where(values > 0, values, 0)
    neg_values = np.where(values < 0, values, 0)

    # Adicionando barras bidirecionais
    ax.bar(df_pivot.index, pos_values, bottom=bottom_positive, color=colors[idx], label=tipo)
    ax.bar(df_pivot.index, neg_values, bottom=bottom_negative, color=colors[idx])

    # Atualizando acumulados para o próximo tipo
    bottom_positive += pos_values
    bottom_negative += neg_values

# Adicionando a linha de tot_ano
tot_ano_values = df.groupby('Ano')['US$ bilhões'].sum()
ax.plot(df['Ano'].unique(), tot_ano_values, color='black', linestyle='--', marker='o', label='Total Anual (US$ bilhões)')

# Adicionando rótulos 
for x, y in zip(df['Ano'].unique(), tot_ano_values):
    ax.text(x, y, f'{y:.2f}', ha='right', va='bottom', fontsize=9, color='black')

# Ajustes no gráfico
ax.axhline(0, color='black', linewidth=0.8)  # Linha no eixo zero
ax.set_xlabel("Ano")
ax.set_ylabel("US$ bilhões")
ax.set_title("Investimento Estrangeiro por Tipo (2014 a 2023)", loc='left')
ax.legend(title="Tipo de Investimento", bbox_to_anchor=(1.05, 1), loc='upper left')


plt.tight_layout()
plt.show()

###Grafico de linhas

color_map = {
    'Participação no capital': "#26547C",         
    'Operações intercompanhia': "#4A7B76",        
    'Ações e cotas em fundos': "#B2A566",         
    'Títulos de dívida': "#FFD97D",               
    'Derivativos – ativos e passivos': "#FFF9B0", 
    'Outros investimentos – passivos': "#B0B5B3"  
}

df_pivot = balanco_anual_principais.pivot(index='Ano', columns='tipo_investimento', values='US$ bilhões').fillna(0)

#Gráfico de linhas
plt.figure(figsize=(14, 8))

for tipo, color in color_map.items():
    if tipo in df_pivot.columns:  
        plt.plot(df_pivot.index, df_pivot[tipo], label=tipo, color=color, marker='o', linewidth=2)


plt.xlabel("Ano")
plt.ylabel("US$ bilhões")
plt.title("Evolução dos Tipos de Investimento Estrangeiro por Ano")
plt.legend(title="Tipo de Investimento", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()


plt.show()


renda_primaria = pd.read_excel(r"C:\Users\User\Desktop\mercado_exterior\Renda Primária Investidor Externo.xlsx",  sheet_name='Geral')
renda_primaria.head(10)
selected_rows = renda_primaria.iloc[[1,2,3,5,6,7,8,9]]
selected_rows.columns
selected_rows.iloc[:, 1:] = selected_rows.iloc[:, 1:] / 1000
selected_rows = selected_rows.rename(columns={'2024 (jan-ago)':'2024'})
selected_rows.columns = ["Tipo de investimento estrangeiro", "2019", "2020", "2021", "2022", "2023", "2024"]
selected_rows.head(15)
selected_rows_long = pd.melt(selected_rows, id_vars=["Tipo de investimento estrangeiro"], 
                             var_name="Ano", value_name="Valor")

selected_rows_long['Tipo de investimento estrangeiro'].unique()
filtered_data = selected_rows_long[selected_rows_long['Ano'] != '2024']
filtered_data
valores_medios_investimentos = filtered_data.groupby('Tipo de investimento estrangeiro')['Valor'].mean().reset_index()

valores_medios_investimentos
selected_rows_long


#Gráfico

colors = ["#555555", "#1D2D44", "#3E5C76", "#013220", "#2D132C", "#D8973C", "#E0B98B"]

# Separar os dados para as barras e obter os dados de "Total despesas"
df_barras = selected_rows_long[selected_rows_long['Tipo de investimento estrangeiro'] != 'Total despesas']
df_total = selected_rows_long[selected_rows_long['Tipo de investimento estrangeiro'] == 'Total despesas']


fig, ax1 = plt.subplots(figsize=(10, 6))

# Obter a lista de anos únicos e garantir que estão ordenados
years = sorted(df_barras['Ano'].unique())
bottom_positive = [0] * len(years)  # Base para valores positivos
bottom_negative = [0] * len(years)  # Base para valores negativos

legend_entries = []

# Plotar cada categoria de investimento como uma camada empilhada
for i, tipo in enumerate(df_barras['Tipo de investimento estrangeiro'].unique()):
    subset = df_barras[df_barras['Tipo de investimento estrangeiro'] == tipo]
    
    valores = [subset[subset['Ano'] == year]['Valor'].values[0] if year in subset['Ano'].values else 0 for year in years]
    
    # Separar valores positivos e negativos
    valores_pos = [val if val >= 0 else 0 for val in valores]
    valores_neg = [val if val < 0 else 0 for val in valores]
    
    # Plotando as barras positivas e adicionar à legenda se for a primeira vez
    if any(valores_pos):
        bars = ax1.bar(years, valores_pos, bottom=bottom_positive, color=colors[i % len(colors)], label=tipo)
        legend_entries.append((bars[0], tipo))  

    # Plotar as barras negativas em vermelho e adicionar à legenda se for a primeira vez
    if any(valores_neg):
        bars = ax1.bar(years, valores_neg, bottom=bottom_negative, color="#A83C32", label=f"{tipo}")
        legend_entries.append((bars[0], f"{tipo}"))  
    
    # Atualizando o valor de "bottom" para a próxima camada da barra empilhada
    bottom_positive = [sum(x) for x in zip(bottom_positive, valores_pos)]
    bottom_negative = [sum(x) for x in zip(bottom_negative, valores_neg)]

# Obtendo os valores corretos para "Total despesas" a partir do DataFrame `df_total`
total_despesas_vals = [df_total[df_total['Ano'] == year]['Valor'].values[0] if year in df_total['Ano'].values else None for year in years]

# Plotando a linha de total de despesas com base nos valores da linha "Total despesas"
line, = ax1.plot(years, total_despesas_vals, color='black', marker='o', label='Total despesas', linewidth=2)
legend_entries.append((line, 'Total despesas'))

# Adicionando rótulos nos pontos da linha
for i, val in enumerate(total_despesas_vals):
    if val is not None:
        ax1.text(years[i], val, f'{val:.2f}', ha='center', va='bottom', fontsize=8, color='black')

ax1.set_xlabel("Ano")
ax1.set_ylabel("US$ bilhões")
plt.title("Distribuições ao investidor estrangeiro por tipo de investimento")


ax1.legend([entry[0] for entry in legend_entries], [entry[1] for entry in legend_entries], loc='upper left', bbox_to_anchor=(1, 1))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()




######Gráfico Foreign direct investment, net inflows
net_inflows = pd.read_excel(r"C:\Users\User\Desktop\mercado_exterior\planilhas_verificadas\Foreingn direct investiments for countries.xlsx")
net_inflows['Series Name'].unique()
print(net_inflows[net_inflows['Country Name'] == 'Luxembourg'])
net_inflows

gdp = pd.read_csv(
    r"C:\Users\User\Desktop\mercado_exterior\planilhas_verificadas\API_NY.GDP.PCAP.CD_DS2_en_csv_v2_142\API_NY.GDP.PCAP.CD_DS2_en_csv_v2_142.csv",
    encoding='ISO-8859-1',
    sep=",",
    skiprows=4  )
gdp

comp_net_inflow_pib = net_inflows[net_inflows['Series Name']=='Foreign direct investment, net inflows (% of GDP)']
comp_net_inflow_pib = pd.merge(comp_net_inflow_pib, gdp, on = 'Country Name', how = 'left')
comp_net_inflow_pib.columns
colunas_para_remover = ['Series Name', 'Series Code', '1960', '1961', '1962', '1963', '1964', '1965',
       '1966', '1967', '1968', '1969', '1970', '1971', '1972', '1973', '1974',
       '1975', '1976', '1977', '1978', '1979', '1980', '1981', '1982', '1983',
       '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992',
       '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001',
       '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
       '2011', '2012', '2013','Country Code_y', 'Indicator Name', 
                        'Indicator Code', 'Unnamed: 68']

comp_net_inflow_pib = comp_net_inflow_pib.drop(columns = colunas_para_remover)
comp_net_inflow_pib.rename(columns={col: f"net_inflows_{col[:4]}" for col in comp_net_inflow_pib.columns if "[YR" in col}, inplace=True)
comp_net_inflow_pib.rename(columns={col: f"gdp_{col}" for col in comp_net_inflow_pib.columns if col.isdigit()}, inplace=True)
comp_net_inflow_pib= comp_net_inflow_pib.sort_values(by='gdp_2023', ascending=False)
comp_net_inflow_pib.head(50)


other_country = comp_net_inflow_pib[comp_net_inflow_pib['Country Name'].isin(['United States', 'China', 'Mexico', 'India', 'Argentina'])]
other_country


comp_net_inflow_pib

net_inflows_columns = [col for col in comp_net_inflow_pib.columns if col.startswith('net_inflows_')]
gdp_columns = [col for col in comp_net_inflow_pib.columns if col.startswith('gdp_')]

# Reorganizando as colunas net_inflows_
net_inflows_melted = comp_net_inflow_pib.melt(
    id_vars=['Country Name'], 
    value_vars=net_inflows_columns, 
    var_name='Year_Net_Inflows', 
    value_name='Net Inflows'
)

# Reorganizando as colunas gdp_
gdp_melted = comp_net_inflow_pib.melt(
    id_vars=['Country Name'], 
    value_vars=gdp_columns, 
    var_name='Year_GDP', 
    value_name='GDP'
)

# Unificando os anos (extraindo o ano das colunas)
net_inflows_melted['Year'] = net_inflows_melted['Year_Net_Inflows'].str.extract(r'(\d{4})')
gdp_melted['Year'] = gdp_melted['Year_GDP'].str.extract(r'(\d{4})')


combined_df = pd.merge(
    net_inflows_melted.drop(columns=['Year_Net_Inflows']), 
    gdp_melted.drop(columns=['Year_GDP']), 
    on=['Country Name', 'Year'], 
    how='outer'
)

print(combined_df.head())


combined_df['GDP'] = pd.to_numeric(combined_df['GDP'], errors='coerce')
combined_df['Net Inflows'] = pd.to_numeric(combined_df['Net Inflows'], errors='coerce')
statistics = combined_df.describe()
print(statistics)
combined_df


net_trade = pd.read_csv(
    r"C:\Users\User\Desktop\mercado_exterior\planilhas_verificadas\API_BN.GSR.GNFS.CD_DS2_en_csv_v2_3838\API_BN.GSR.GNFS.CD_DS2_en_csv_v2_3838.csv",
    encoding='ISO-8859-1',
    sep=",",
    skiprows=4  
)
net_trade.columns
colunas_para_remover = ['Country Code','Indicator Name', 'Indicator Code',
       '1960', '1961', '1962', '1963', '1964', '1965', '1966', '1967', '1968',
       '1969', '1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977',
       '1978', '1979', '1980', '1981', '1982', '1983', '1984', '1985', '1986',
       '1987', '1988', '1989', '1990', '1991', '1992', '1993', '1994', '1995',
       '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004',
       '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013','Unnamed: 68']
net_trade = net_trade.drop(columns = colunas_para_remover)
net_trade.columns


# Reorganizando o df 
net_trade_melted = net_trade.melt(
    id_vars=['Country Name'], 
    value_vars=['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'], 
    var_name='Year', 
    value_name='Net Trade'
)


net_trade_melted['Year'] = pd.to_numeric(net_trade_melted['Year'], errors='coerce')
net_trade_melted
combined_df['Year'] = pd.to_numeric(combined_df['Year'], errors = 'coerce')
combined_df = pd.merge(combined_df, net_trade_melted, on= ['Country Name', 'Year'], how = 'left')
combined_df


################# IDP comparação países desenvolvidos, em desenvolvimento e Brasil
comparacao_idp = pd.read_csv(r"C:\Users\User\Desktop\mercado_exterior\planilhas_verificadas\unctad_world_investment_report_selected_fdi_flows.csv", encoding = 'utf-8', sep=";")
comparacao_idp
comparacao_idp = comparacao_idp.drop(index=range(0, 23)).reset_index(drop=True)
comparacao_idp.columns
comparacao_idp = comparacao_idp.rename(columns={'Year': 'Ano', 'Developed economies': 'Países desenvolvidos', 'Developing economies': 'Países em desenvolvimento', 'Brazil': 'Brasil'})
comparacao_idp


comparacao_idp['Países desenvolvidos'] = comparacao_idp['Países desenvolvidos'].astype(str).str.replace(',', '.').str.strip()
comparacao_idp['Países em desenvolvimento'] = comparacao_idp['Países em desenvolvimento'].astype(str).str.replace(',', '.').str.strip()
comparacao_idp['Brasil'] = comparacao_idp['Brasil'].astype(str).str.replace(',', '.').str.strip()
comparacao_idp['Países desenvolvidos'] = pd.to_numeric(comparacao_idp['Países desenvolvidos'], errors='coerce')
comparacao_idp['Países em desenvolvimento'] = pd.to_numeric(comparacao_idp['Países em desenvolvimento'], errors='coerce')
comparacao_idp['Brasil'] = pd.to_numeric(comparacao_idp['Brasil'], errors='coerce')

comparacao_idp.to_excel(r"C:\Users\User\Desktop\mercado_exterior\planilhas_verificadas\comparacao_idp.xlsx")

comparacao_idp

# Gráfico combinado
fig, ax = plt.subplots(figsize=(10, 6))

# "Países Desenvolvidos" e "Países em Desenvolvimento"
line1, = ax.plot(comparacao_idp['Ano'], comparacao_idp['Países desenvolvidos'], label='Países Desenvolvidos', color='blue', linewidth=2)
line2, = ax.plot(comparacao_idp['Ano'], comparacao_idp['Países em desenvolvimento'], label='Países em Desenvolvimento', color='green', linewidth=2)

# "Brasil"
line3, = ax.plot(comparacao_idp['Ano'], comparacao_idp['Brasil'], label='Brasil', color='red', linewidth=2)

# Configurações do eixo Y
ax.set_ylabel('Investimento (US$ milhões)', fontsize=12)
ax.set_ylim(0, 1500000)  
ax.set_yticks(range(0, 1500001, 250000))  
ax.set_yticklabels([f"{int(y/1000)}K" for y in range(0, 1500001, 250000)])  

# Configurações do eixo X
ax.set_xlabel('Ano', fontsize=12)
ax.set_xticks(comparacao_idp['Ano'])
ax.set_xticklabels(comparacao_idp['Ano'], rotation=45)

# Título e grade
plt.title('Evolução do Investimento Direto por Região (2013-2023)', fontsize=14)
ax.grid(True, linestyle='--', alpha=0.6)

# Legendas
lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
ax.legend(lines, labels, loc='upper left', fontsize=10)


plt.tight_layout()
plt.show()


###Gráficos separados
# Gráfico para "Países Desenvolvidos" e "Países em Desenvolvimento"
fig, ax1 = plt.subplots(figsize=(10, 6))

# "Países Desenvolvidos" e "Países em Desenvolvimento"
line1, = ax1.plot(comparacao_idp['Ano'], comparacao_idp['Países desenvolvidos'], label='Países Desenvolvidos', color='blue', linewidth=2)
line2, = ax1.plot(comparacao_idp['Ano'], comparacao_idp['Países em desenvolvimento'], label='Países em Desenvolvimento', color='green', linewidth=2)

# Configurações do eixo Y
ax1.set_ylabel('Investimento (US$ milhões)', fontsize=12)
ax1.set_ylim(0, 1500000)  
ax1.set_yticks(range(0, 1500001, 250000))  
ax1.set_yticklabels([f"{int(y/1000)}K" for y in range(0, 1500001, 250000)])  

# Configurações do eixo X
ax1.set_xlabel('Ano', fontsize=12)
ax1.set_xticks(comparacao_idp['Ano'])
ax1.set_xticklabels(comparacao_idp['Ano'], rotation=45)

# Título e grade
plt.title('Evolução do Investimento Direto por Países Desenvolvidos e em Desenvolvimento (2013-2023)', fontsize=14)
ax1.grid(True, linestyle='--', alpha=0.6)

# Legendas
lines = [line1, line2]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=10)


plt.tight_layout()
plt.show()



# "Brasil"
fig, ax2 = plt.subplots(figsize=(10, 6))

line3, = ax2.plot(comparacao_idp['Ano'], comparacao_idp['Brasil'], label='Brasil', color='red', linewidth=2)

# Configurações do eixo Y
ax2.set_ylabel('Investimento (US$ K)', fontsize=12)
ax2.set_ylim(0, 80000)  
ax2.set_yticks(range(0, 80001, 10000))  
ax2.set_yticklabels([f"{int(y/1000)}K" for y in range(0, 80001, 10000)])  

# Configurações do eixo X
ax2.set_xlabel('Ano', fontsize=12)
ax2.set_xticks(comparacao_idp['Ano'])
ax2.set_xticklabels(comparacao_idp['Ano'], rotation=45)

# Título e grade
plt.title('Evolução do Investimento Direto no Brasil (2013-2023)', fontsize=14)
ax2.grid(True, linestyle='--', alpha=0.6)

# Legendas
ax2.legend([line3], ['Brasil'], loc='upper left', fontsize=10)

plt.tight_layout()
plt.show()