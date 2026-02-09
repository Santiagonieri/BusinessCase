import pandas as pd


def guardar_df_en_formato_csv(df, ruta_destino,nombre_archivo):

    """Funcion para guardar un dataframe en formato csv, variable de entrada el dataframe y el nombre del archivo a guardar"""
    
    df.to_csv(f"{ruta_destino}/{nombre_archivo}.csv", index=False)