
import pandas as pd
import json
import numpy as np


def registros_con_valores_nulos(df):
    """Funcion para determinar si existen registros con valores nulos en el dataframe"""


    # Reemplazar los valores nulos por "Sin informacion"
    
    df = df.fillna("Sin informacion")

    # Filtrar los registros que contienen "Sin informacion" en alguna de sus columnas
    registros_con_vacios = df[(df == "Sin informacion").any(axis=1)]
    registros_sin_vacios = df[(df != "Sin informacion").any(axis=1)]

    return registros_con_vacios, registros_sin_vacios



def estandarizar_nombres_columnas(df):

    # Eliminar espacios en blanco y convertir nombres de columnas a minusculas

    df.columns = df.columns.str.strip().str.lower()

    # Renombrar la columna "aplicación" a "tipo_aplicacion" si existe

    if "aplicación" in df.columns:
        df.rename(columns={"aplicación": "tipo_aplicacion"}, inplace=True)

    return df




def definir_tipo_datos(df):

    columnas_string=["mercado","source","medium","campaign","tipo_aplicacion"]

    columnas_fechas=["fecha"]

    columnas_numericas=["sesiones","transacciones","revenue"]

    for col in columnas_fechas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in columnas_string:
        if col in df.columns:
            df[col] = df[col].astype(str)

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')           

    return df


def estandarizar_cadenas_string(df):

    # Identificar las columnas de tipo string en el dataframe

    columnas_string =  df.select_dtypes(include=["object", "string"]).columns
    
    # Eliminar espacios en blanco y convertir a minusculas las columnas de tipo string

    for col in columnas_string:
   
        df[col] = df[col].astype(str).str.strip().str.lower()

    return df


def reglas_de_negocio(reglas):

    with open(reglas, 'r') as f:
        return json.load(f)

def aplicar_reglas_de_negocio(df, reglas_de_negocio):

    """Se aplican las reglas de negocio para clasificar los registros en canal y canal_detail.
    Se itera sobre cada regla de negocio y se evaluan las condiciones para asignar el canal y canal_detail correspondiente.
    Si una regla tiene una referencia a otra columna para definir el canal_detail, se asigna el valor de esa columna. 
    Finalmente, se identifican los registros que no cumplen con ninguna regla y se les asigna un valor por defecto."""

    reglas=reglas_de_negocio

    # Crear columnas vacias para canal y canal_detail
    df["canal"] = None
    df["canal_detail"] = None


    for regla in reglas:

        validador = pd.Series(True, index=df.index)

        for col, value in regla["condiciones"].items():
            validador = validador & df[col].str.contains(value)

        validador =validador & df["canal"].isna()

        df.loc[validador, "canal"] = regla["canal"]

        detail_valor = regla["canal_detail"]

        # Regla especial, definifir el valor de Canal_Detail en base a una referencia a otra columna.
        if isinstance(detail_valor, str) and detail_valor.startswith("columna:"):
            nombre_columna = detail_valor.replace("columna:", "")
            df.loc[validador, "canal_detail"] = df.loc[validador, nombre_columna]
        else:    
            df.loc[validador, "canal_detail"] = regla["canal_detail"]

    # Identificar registros sin coincidencia en las reglas de negocio        
    canal_sin_identificar = df["canal"].isna()
    canal_detail_sin_identificar = df["canal_detail"].isna()
    
    # Asignar valores por defecto a los registros sin coincidencia en las reglas de negocio
    df.loc[canal_sin_identificar, "canal"] = "Canal no identificado"
    df.loc[canal_detail_sin_identificar, "canal_detail"] = "Detalle canal no identificado"

        

    return df
    


def agrupar_por_canal(df):


    """Funcion para agrupar el dataframe por canal y canal_detail, y calcular el peso de cada canal y canal_detail en
    base a las transacciones de cada canal y canal_detail respecto al total de transacciones de cada fecha, 
    mercado y tipo de aplicacion."""
    df.rename(columns={'transacciones':'transacciones_ga','sesiones':'sesiones_ga'}, inplace=True)
    df_agrupado = df.groupby(['fecha','mercado','tipo_aplicacion','canal','canal_detail']).agg({'transacciones_ga':'sum','sesiones_ga':'sum'}).reset_index()

    
    # Calculo de totales por fecha, mercado y tipo de aplicacion
    total_tx = df_agrupado.groupby(['fecha', 'mercado', 'tipo_aplicacion'])['transacciones_ga'].transform('sum')
    total_se = df_agrupado.groupby(['fecha', 'mercado', 'tipo_aplicacion'])['sesiones_ga'].transform('sum')

    # 3. Calcular Pesos Temporales
    # Si total_tx es 0, resultado es NaN
    peso_tx = df_agrupado['transacciones_ga'] / total_tx
    peso_se = df_agrupado['sesiones_ga'] / total_se

    # 4. Lógica Supletoria (Fallback)
    # Si peso_tx es nulo (porque no hubo ventas ese día), rellena con peso_se
    # Si peso_se también es nulo (no hubo ni sesiones), rellena con 0
    df_agrupado['peso_canal'] = peso_tx.fillna(peso_se).fillna(0)

    # 5. Guardamos los totales para auditoría en Power BI (opcional pero útil)
    df_agrupado['total_transacciones_ga'] = total_tx
    df_agrupado['total_sesiones_ga'] = total_se
    
    

    return df_agrupado


def distribucion_revenue_transacciones(GA_agrupado,df_transaccional):

    """Funcion para calcular la distribucion del revenue por canal y canal_detail, 
    se asume que el revenue se distribuye en base al peso de las transacciones de cada canal y canal_detail,
    supletoriamente se le asigna el peso de las sesiones."""
    
    df_transaccional_agrupado = df_transaccional.groupby(['fecha','mercado','tipo_aplicacion']).agg({'revenue': 'sum','transacciones': 'sum'}).reset_index()
    df_transaccional_agrupado.rename(columns={'transacciones':'transacciones_real'}, inplace=True)

    #Tabla base la transaccional, se le hace un merge de la tabla GA agrupada para obtener los pesos de cada canal y canal_detail 
    df_agrupado = df_transaccional_agrupado.merge(GA_agrupado, on=['fecha','mercado','tipo_aplicacion'], how='left')


    #Distribucion del revenue en base al peso de las transacciones de cada canal y canal_detail
    df_agrupado['revenue_distribuido'] = df_agrupado['peso_canal'] * df_agrupado['revenue']
    df_agrupado['transacciones_reales_distribuidas'] = df_agrupado['peso_canal'] * df_agrupado['transacciones_real']

    return df_agrupado

def ratio_conversion_ga(df):

    """Ratio de conversion en base a la cantidad de transacciones (GA) y sesiones de cada canal y canal_detail"""

    df['ratio_conversion_ga'] = df['transacciones_ga'] / df['sesiones_ga']
    

    return df


def ratio_conversion_real(df):

    """Ratio de conversion en base a la cantidad de transacciones (Real) y sesiones de cada canal y canal_detail"""

    df['ratio_conversion_real'] = df['transacciones_real'] / df['sesiones_ga']

    return df