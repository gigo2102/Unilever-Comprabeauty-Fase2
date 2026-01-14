"""
Script para extraer la solapa 'fichero' del Excel de Elvis
y exportarla a un CSV compatible con Pandas.
"""
import pandas as pd
import os
import sys

def extract_fichero_to_csv(excel_file_path, output_csv_name='clientes.elvis.csv'):
    """
    Extrae la solapa 'fichero' de un archivo Excel y la guarda como CSV.

    Args:
        excel_file_path: Ruta al archivo Excel de Elvis
        output_csv_name: Nombre del archivo CSV de salida
    """
    print(f"Abriendo archivo Excel: {excel_file_path}")
    print("Este proceso puede tardar varios minutos debido al tamaño del archivo...")

    try:
        # Leer solo la solapa 'fichero' del Excel
        df = pd.read_excel(excel_file_path, sheet_name='Fichero', engine='openpyxl')

        print(f"Solapa 'fichero' cargada exitosamente.")
        print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

        # Limpiar campos de texto: remover comas y punto y coma
        print("Limpiando campos de texto...")
        for col in df.columns:
            if df[col].dtype == 'object':  # Solo campos de texto
                df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.replace(';', '', regex=False)
                # Reemplazar 'nan' por valores vacíos
                df[col] = df[col].replace('nan', '')

        # Obtener el directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, output_csv_name)

        # Exportar a CSV con punto y coma como separador y coma como decimal
        print(f"Exportando a CSV: {output_path}")
        df.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';', decimal=',')

        print(f"[OK] Archivo CSV creado exitosamente: {output_csv_name}")
        print(f"Tamaño del archivo: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo Excel en {excel_file_path}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Verifica que la solapa 'fichero' exista en el archivo Excel.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    # Buscar archivo Excel en el directorio actual
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Si se proporciona un argumento, usar ese archivo
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        if not os.path.isabs(excel_path):
            excel_path = os.path.join(script_dir, excel_path)
    else:
        # Buscar archivos .xlsx en el directorio (ignorar archivos temporales)
        excel_files = [f for f in os.listdir(script_dir)
                      if f.endswith('.xlsx') and not f.startswith('~$')]

        if not excel_files:
            print("No se encontró ningún archivo .xlsx en el directorio actual.")
            print("Uso: python extract_elvis_clientes.py [nombre_archivo.xlsx]")
            sys.exit(1)
        elif len(excel_files) == 1:
            excel_path = os.path.join(script_dir, excel_files[0])
            print(f"Usando archivo encontrado: {excel_files[0]}")
        else:
            # Buscar archivos que contengan "Elvis" en el nombre
            elvis_files = [f for f in excel_files if 'Elvis' in f or 'elvis' in f]
            if elvis_files:
                excel_path = os.path.join(script_dir, elvis_files[0])
                print(f"Usando archivo de Elvis encontrado: {elvis_files[0]}")
            else:
                # Usar el primer archivo no temporal
                excel_path = os.path.join(script_dir, excel_files[0])
                print(f"Usando archivo: {excel_files[0]}")

    extract_fichero_to_csv(excel_path)
