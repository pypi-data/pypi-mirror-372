import numpy as np
import pandas as pd
import os 
import shutil
from unidecode import unidecode
import openpyxl
import time
import pythoncom
import win32com.client

# Borrar los archivos si existen en la carpeta de bases Banrep
def BorrrarArchivo(rutaArchivo):  
    if os.path.exists(rutaArchivo):# Verificar si el archivo ya existe
        os.remove(rutaArchivo)

# Mueve los archivos descargados a la carpeta que se requiere
def moverArchivo(RutaOrigen, RutaDestino):
    try:
        shutil.move(RutaOrigen, RutaDestino)
        print(f"El archivo '{RutaOrigen}' se ha movido correctamente a '{RutaDestino}'.")
    except Exception as e:
        print(f"No se pudo mover el archivo '{RutaOrigen}' a '{RutaDestino}': {e}")

def copiarArchivo(RutaOrigen, RutaDestino):
    try:
        shutil.copy2(RutaOrigen, RutaDestino)  # `copy2` copia metadatos (marca de tiempo) además del archivo
        print(f"El archivo '{RutaOrigen}' se ha copiado correctamente a '{RutaDestino}'.")
    except Exception as e:
        print(f"No se pudo copiar el archivo '{RutaOrigen}' a '{RutaDestino}': {e}")


def obtenerArchivoMasReciente(rutaCarpeta, formato=".txt"):
    # Obtener la lista de archivos en la carpeta
    archivos_en_carpeta = [archivo for archivo in os.listdir(rutaCarpeta) if archivo.endswith(formato)]
    # Verificar si hay archivos en la carpeta
    if archivos_en_carpeta:
        # Obtener el archivo más reciente basado en la última modificación
        archivo_mas_reciente = max(archivos_en_carpeta,key=lambda x: os.path.getmtime(os.path.join(rutaCarpeta, x)))
        # Obtener la fecha de modificación del archivo más reciente
        fecha_modificacion = os.path.getmtime(os.path.join(rutaCarpeta, archivo_mas_reciente))
        # Retornar nombre y fecha
        return archivo_mas_reciente, fecha_modificacion
    else:
        return None, None

def ExisteRuta(arregloDeCarpetas):
    carpeta_correcta = None
    for carpeta in arregloDeCarpetas:
        try:
            # Verifica si la ruta existe y es una carpeta
            if os.path.isdir(carpeta):
                print(f"La carpeta existe en: {carpeta}")
                carpeta_correcta = carpeta
                break  # Sale del ciclo si la carpeta existe
        except Exception as e:
            # Maneja otras posibles excepciones (e.g., problemas de permisos)
            print(f"Error al verificar la carpeta {carpeta}: {e}")
            continue
    if carpeta_correcta is None:
        print("La carpeta no se encontró en ninguna de las rutas proporcionadas.")
    else:
        # Aquí puedes continuar con el procesamiento usando la carpeta_correcta
        pass
    return carpeta_correcta

def cargaExcel(rutaArchivo,sheetName, AsString=False):
    df = pd.read_excel(rutaArchivo, sheet_name=sheetName, engine='openpyxl')
    if AsString:
        df=df.astype(str)
    return df

def ActualizarTodoExcel(ruta_archivo):
    pythoncom.CoInitialize()  # Inicializa COM correctamente

    try:
        ruta_archivo_absoluta = os.path.abspath(ruta_archivo)
        print(f"Intentando abrir el archivo: {ruta_archivo_absoluta}")

        if not os.path.exists(ruta_archivo_absoluta):
            print(f"⚠️ El archivo no existe en la ruta: {ruta_archivo_absoluta}")
            return
        # Iniciar Excel y hacerlo visible
        excel_app = win32com.client.DispatchEx("Excel.Application")
        excel_app.Visible = True  
        excel_app.DisplayAlerts = False
        # Abrir el archivo de Excel
        workbook = excel_app.Workbooks.Open(ruta_archivo_absoluta)
        print("📂 Archivo abierto correctamente, iniciando actualización...")

        # Activar la primera hoja (por si acaso)
        workbook.Sheets(1).Activate()
        # Iniciar actualización
        workbook.RefreshAll()
        print("🔄 Actualizando conexiones y tablas de Power Query...")
        # Esperar que Excel termine la actualización y cálculos
        while excel_app.CalculationState != 0:  # 0 significa "listo"
            print("⌛ Esperando que Excel termine los cálculos...")
            time.sleep(2)
        print("✅ Actualización completada.")
        # Guardar y cerrar Excel
        print(f'📁 Archivo actualizado y cerrado: {ruta_archivo_absoluta}')
    except Exception as e:
        print(f"❌ Error al actualizar el archivo {ruta_archivo_absoluta}: {e}")
    finally:
        # Asegurar que Excel se cierra correctamente
        if 'excel_app' in locals():
            a=10
        pythoncom.CoUninitialize()

def consolidarArchivosExcel(NombreConElQueIniciaLosArchivos,RutaALaCarpeta,TipoArchivos='.xlsx'):
    dataframes = []
    for archivo in os.listdir(RutaALaCarpeta):
        if archivo.endswith(TipoArchivos) and archivo.startswith(NombreConElQueIniciaLosArchivos):
            ruta_archivo = os.path.join(RutaALaCarpeta, archivo)
            df = pd.read_excel(ruta_archivo)
            dataframes.append(df)    
    df_consolidado = pd.concat(dataframes, ignore_index=True)
    return df_consolidado

