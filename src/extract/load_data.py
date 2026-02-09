import pandas as pd
import variables as var

def lectura_libro_xlsx(ruta_origen):

    """Funcion para la lectura del libro de excel, variable de entrada ruta del archivo, 
    devuelve un diccionario con el nombre de las hojas como clave y el contenido de cada hoja en un dataframe como valor"""
   
    return pd.read_excel(ruta_origen, sheet_name=None)

    


