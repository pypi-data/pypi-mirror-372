import pandas as pd
import mysql.connector
import decimal
import gspread
from google.oauth2 import service_account
from typing import Optional

# Função para gerar DataFrame a partir de uma view do Phoenix

def gerar_df_phoenix(
        db_phoenix: str, # Nome do banco de dados Phoenix
        request_select: str, # Comando SQL para seleção
        user_phoenix: str, # Nome de usuário do banco de dados
        password_phoenix: str, # Senha do banco de dados
        host_phoenix: str # Host do banco de dados
    ) -> pd.DataFrame:
    
    config = {
        'user': user_phoenix, 
        'password': password_phoenix, 
        'host': host_phoenix, 
        'database': db_phoenix
        }

    conexao = mysql.connector.connect(**config)

    cursor = conexao.cursor()

    request_name = request_select

    cursor.execute(request_name)

    resultado = cursor.fetchall()
    
    cabecalho = [desc[0] for desc in cursor.description]

    cursor.close()

    conexao.close()

    df = pd.DataFrame(
        resultado, 
        columns=cabecalho
    )

    df = df.applymap(
        lambda x: float(x) 
        if isinstance(x, decimal.Decimal) 
        else (
            x.decode() 
            if isinstance(x, (bytes, bytearray)) 
            else x
        )
    )

    return df

# Função para abrir uma planilha do Google Sheets

def abrir_planilha(
        id_gsheet: str, # ID da planilha do Google Sheets
        credenciais: dict # Credenciais do Google Sheets
    ) -> gspread.Spreadsheet:

    credentials = service_account.Credentials.from_service_account_info(credenciais)

    scope = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = credentials.with_scopes(scope)

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(id_gsheet)

    return spreadsheet

# Função para tratar colunas de um DataFrame

def tratar_colunas_df(
        df: pd.DataFrame, # DataFrame a ser tratado
        lista_colunas_numero: Optional[list] = None, # Lista de colunas numéricas
        nome_coluna_ref_ano_mes: Optional[str] = None, # Nome da coluna de referência para ano e mês
        lista_colunas_vazia_ou_none: Optional[list] = None, # Lista de colunas string p/ tratamento de ''
        lista_colunas_data: Optional[list] = None, # Lista de colunas de data
        formato_colunas_data: Optional[str] = None, # Formato das colunas de data
        lista_colunas_hora: Optional[list] = None, # Lista de colunas de hora
        formato_colunas_hora: Optional[str] = None # Formato das colunas de hora
    ) -> pd.DataFrame:

    # Função para adicionar colunas de ano, mês e mês/ano

    def adicionar_colunas_ano_mes(
            df: pd.DataFrame, # DataFrame a ser tratado
            coluna_data: Optional[str] = None # Nome da coluna de referência para ano e mês
        ) -> pd.DataFrame:

        if coluna_data is None:

            df['Mes_Ano'] = pd.to_datetime(
                df['Ano'].astype(int).astype(str) 
                + '-' 
                + df['Mes'].astype(int).astype(str) + '-01'
            ).dt.to_period('M')

        elif coluna_data != 'Nenhuma':

            df['Ano'] = pd.to_datetime(df[coluna_data]).dt.year

            df['Mes'] = pd.to_datetime(df[coluna_data]).dt.month

            df['Mes_Ano'] = pd.to_datetime(
                df['Ano'].astype(int).astype(str) 
                + '-' 
                + df['Mes'].astype(int).astype(str) + '-01'
            ).dt.to_period('M')

        return df

    if lista_colunas_vazia_ou_none:
        
        for coluna in lista_colunas_vazia_ou_none:

            df[coluna] = df[coluna].replace('', None)

    if lista_colunas_numero:

        if lista_colunas_numero=='Todas':

            lista_colunas_numero = df.columns.tolist()
        
        for coluna in lista_colunas_numero:

            df[coluna] = (
                df[coluna]
                .astype(str)
                .str.replace(',', '.', regex=False)
            )

            df[coluna] = pd.to_numeric(
                df[coluna], 
                errors='coerce'
            )

    if lista_colunas_data:

        for coluna in lista_colunas_data:

            df[coluna] = pd.to_datetime(
                df[coluna], 
                format=formato_colunas_data
            ).dt.date

    if lista_colunas_hora:

        for coluna in lista_colunas_hora:

            df[coluna] = pd.to_datetime(
                df[coluna], 
                format=formato_colunas_hora
            ).dt.time

    df = adicionar_colunas_ano_mes(
        df=df,
        coluna_data=nome_coluna_ref_ano_mes
    )

    return df

# Função para converter a aba do Google Sheets em um DataFrame

def gsheet_to_df(
        spread_sheet: gspread.Spreadsheet, # Planilha do Google
        nome_aba: str, # Nome da aba a ser convertida
        lista_colunas_numero: Optional[list] = None, # Lista de colunas numéricas
        nome_coluna_ref_ano_mes: Optional[str] = None, # Nome da coluna de referência para ano e mês
        lista_colunas_vazia_ou_none: Optional[list] = None, # Lista de colunas string p/ tratamento de ''
        lista_colunas_data: Optional[list] = None, # Lista de colunas de data
        formato_colunas_data: Optional[str] = None # Formato das colunas de data
    ) -> pd.DataFrame:

    sheet = spread_sheet.worksheet(nome_aba)

    sheet_data = sheet.get_all_values()

    df = pd.DataFrame(
        sheet_data[1:], 
        columns=sheet_data[0]
    )

    df = tratar_colunas_df(
        df=df,
        lista_colunas_numero=lista_colunas_numero,
        nome_coluna_ref_ano_mes=nome_coluna_ref_ano_mes,
        lista_colunas_vazia_ou_none=lista_colunas_vazia_ou_none,
        lista_colunas_data=lista_colunas_data,
        formato_colunas_data=formato_colunas_data
    )

    return df
