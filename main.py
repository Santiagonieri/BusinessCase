import src.extract.load_data as ld  
import src.transform.transform_data as td
import src.save.save_data as sd
import variables as var

def procesar_transformaciones_comunes(df, nombre_hoja):
    df = td.estandarizar_nombres_columnas(df)
    df = td.definir_tipo_datos(df)
    df = td.estandarizar_cadenas_string(df)

    registros_con_nulos, df_sin_nulos = td.registros_con_valores_nulos(df)
    print(f"Hoja '{nombre_hoja}': {len(registros_con_nulos)} registros con valores nulos")

    return df_sin_nulos, registros_con_nulos





def main():

    libro = ld.lectura_libro_xlsx(var.Ruta_origen)
    reglas = td.reglas_de_negocio(var.Ruta_reglas_negocio)

    df_ga = None
    df_transacciones = None

    # Transformaciones comunes
    for nombre_hoja, df in libro.items():

        df_limpio, df_review = procesar_transformaciones_comunes(df, nombre_hoja)

        if nombre_hoja == var.Nombre_Hoja_GA:
            df_ga = df_limpio

        elif nombre_hoja == var.Nombre_Hoja_Transacciones:
            df_transacciones = df_limpio

    # ======================
    # ETAPA 1 - GOOGLE
    # ======================
    df_ga = td.aplicar_reglas_de_negocio(df_ga, reglas)
    df_ga = td.agrupar_por_canal(df_ga)
    df_ga = td.ratio_conversion_ga(df_ga)

    sd.guardar_df_en_formato_csv(
        df_ga,
        var.Ruta_guardado_archivos_procesados,
        var.Nombre_Hoja_GA
    )

    print("Etapa 1 (Google Analytics) finalizada")

    # ======================
    # ETAPA 2 - TRANSACCIONAL
    # ======================
    df_transacciones = td.distribucion_revenue_transacciones(df_ga, df_transacciones)
    df_transacciones = td.ratio_conversion_real(df_transacciones)

    sd.guardar_df_en_formato_csv(
        df_transacciones,
        var.Ruta_guardado_archivos_procesados,
        var.Nombre_Hoja_Transacciones
    )

    print("Etapa 2 (Transaccional) finalizada")


if __name__ == "__main__":
    main()




