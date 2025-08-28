import pandas as pd
import os
from unidecode import unidecode

def QuitarPuntosDecimalesTextos(df, columnas):
    """Convierte las columnas especificadas a string y elimina el sufijo '.0' de los valores numéricos.
    Returns:
        pd.DataFrame: El DataFrame con las columnas modificadas.
    """
    df[columnas] = df[columnas].astype(str).replace(r'^(\d+)\.0$', r'\1', regex=True)
    return df


def mergeBases(dataframe1, dataframe2, lefton, righton):
    """Une dos DataFrames de Pandas asegurando que no haya duplicados en el cruce y detectando registros sin coincidencias en cada DataFrame.

    Parámetros:
    - dataframe1: Primer DataFrame de Pandas.
    - dataframe2: Segundo DataFrame de Pandas.
    - lefton: Lista de columnas clave en dataframe1.
    - righton: Lista de columnas clave en dataframe2.

    Retorna:
    - dfmerge: DataFrame con la unión.
    - df_no_match_left: Registros en dataframe1 que no encontraron match en dataframe2.
    - df_no_match_right: Registros en dataframe2 que no encontraron match en dataframe1.
    - alerta_duplicados: Mensaje de alerta si hay duplicados en la clave.
    """

    # Realizar el merge con how='left'
    if lefton == righton:
        dfmerge = pd.merge(dataframe1, dataframe2, on=lefton, how='left',suffixes=('','_right'))
    else:
        dfmerge = pd.merge(dataframe1, dataframe2, left_on=lefton, right_on=righton, how='left', suffixes=('','_right'))

    # Eliminar columnas duplicadas generadas por el merge
    if isinstance(righton, list):  # Si righton es una lista de columnas
        for col in righton:
            columna_duplicada = f"{col}_right"
            if columna_duplicada in dfmerge.columns:
                dfmerge = dfmerge.drop(columns=[columna_duplicada])
    else:  # Si righton es una sola columna
        columna_duplicada = f"{righton}_right"
        if columna_duplicada in dfmerge.columns:
            dfmerge = dfmerge.drop(columns=[columna_duplicada])

    # Detectar registros de df1 que no tienen coincidencias en df2 (valores NaN en columnas de df2)
    columnas_df2 = [col for col in dataframe2.columns if col not in righton]
    df_no_match_left = dfmerge[dfmerge[columnas_df2].isna().all(axis=1)]

    # Detectar registros de df2 que no tienen coincidencias en df1
    claves_merge = set(dfmerge[lefton].drop_duplicates().itertuples(index=False, name=None))
    df_no_match_right = dataframe2[~dataframe2[righton].apply(lambda x: tuple(x) in claves_merge, axis=1)]

    # Detectar duplicados en las claves del merge
    duplicados = dfmerge.groupby(lefton).size()
    duplicados = duplicados[duplicados > 1]  # Filtrar claves duplicadas

    alerta_duplicados = "⚠️ Hay duplicados en la clave del cruce" if len(duplicados) > 0 else "✅ No hay duplicados en la clave"

    return dfmerge, df_no_match_left, df_no_match_right, alerta_duplicados


# Quita las tildes de un DataFrame
def dfSinTildes(dataframe):
    for columna in dataframe.columns:
        if dataframe[columna].dtype == 'object':
            dataframe[columna] = dataframe[columna].apply(unidecode)
    return  dataframe

# Quita las tildes de los encabezados de un DataFrame        
def dfEncabezadosSinTildes(dataframe):
    nuevos_nombres_columnas = [unidecode(columna) 
        if dataframe[columna].dtype == 'object' else columna for columna in dataframe.columns]
    dataframe.columns = nuevos_nombres_columnas
    return  dataframe

def GuardarRemplazarExcel(dataframe,rutaParaGuardado,nombreHoja, ejecutar=True):  
    if ejecutar:
        if os.path.exists(rutaParaGuardado):
            os.remove(rutaParaGuardado)
        dataframe.to_excel(rutaParaGuardado,sheet_name=nombreHoja, index=False)

def GuardarRemplazarCsv(dataframe,rutaParaGuardado, ejecutar=True):  
    if ejecutar:
        if os.path.exists(rutaParaGuardado):
            os.remove(rutaParaGuardado)
        dataframe.to_csv(rutaParaGuardado, index=False)

def GuardarRemplazarParquet(dataframe,rutaParaGuardado, ejecutar=True, engine="fastparquet"):  
    if ejecutar:
        if os.path.exists(rutaParaGuardado):
            os.remove(rutaParaGuardado)
        dataframe.to_parquet(rutaParaGuardado, index=False, engine=engine)