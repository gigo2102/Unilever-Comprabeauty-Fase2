"""
Script para extraer las solapas de años del Excel de Elvis,
dividirlas por trimestres y exportar a CSV.
"""
import pandas as pd
import os
import sys

def get_quarter(month):
    """Determina el trimestre basado en el mes."""
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'

def clean_dataframe_fields(df):
    """
    Limpia los campos del dataframe removiendo comas y punto y comas
    de las columnas de texto.

    Args:
        df: DataFrame de pandas a limpiar

    Returns:
        DataFrame limpio
    """
    df_clean = df.copy()

    # Iterar sobre cada columna
    for col in df_clean.columns:
        # Solo limpiar columnas de tipo texto/objeto
        if df_clean[col].dtype == 'object':
            # Remover comas y punto y comas
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '', regex=False)
            df_clean[col] = df_clean[col].astype(str).str.replace(';', '', regex=False)

    return df_clean

def extract_pedidos_by_quarter(excel_file_path, years=None, date_column=None):
    """
    Extrae las solapas de años, las divide por trimestres y exporta a CSV.

    Args:
        excel_file_path: Ruta al archivo Excel de Elvis
        years: Lista de años a procesar (default: 2020-2025)
        date_column: Nombre de la columna de fecha (se detectará automáticamente si no se proporciona)
    """
    if years is None:
        years = [2020, 2021, 2022, 2023, 2024, 2025]

    print(f"Abriendo archivo Excel: {excel_file_path}")
    print("Este proceso puede tardar varios minutos debido al tamaño del archivo...\n")

    try:
        # Abrir el archivo Excel
        excel_file = pd.ExcelFile(excel_file_path, engine='openpyxl')

        print("Solapas disponibles en el archivo:")
        for sheet in excel_file.sheet_names:
            print(f"  - {sheet}")
        print()

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Procesar cada año
        for year in years:
            sheet_name = f'Año {year}'

            if sheet_name not in excel_file.sheet_names:
                print(f"[AVISO] No se encontró la solapa '{sheet_name}', saltando...")
                continue

            print(f"Procesando: {sheet_name}")

            # Leer la solapa
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
            print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

            # Si no se especificó la columna de fecha, intentar detectarla
            if date_column is None:
                # Buscar columnas que contengan 'fecha' en el nombre
                date_columns = [col for col in df.columns if 'fecha' in col.lower()]
                if not date_columns:
                    # Buscar columnas de tipo datetime
                    date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

                if date_columns:
                    detected_date_column = date_columns[0]
                    print(f"  Columna de fecha detectada: '{detected_date_column}'")
                else:
                    print(f"  [ERROR] No se pudo detectar una columna de fecha en '{sheet_name}'")
                    print(f"  Columnas disponibles: {list(df.columns)[:10]}...")
                    continue
            else:
                detected_date_column = date_column

            # Convertir la columna a datetime si no lo es
            if not pd.api.types.is_datetime64_any_dtype(df[detected_date_column]):
                try:
                    df[detected_date_column] = pd.to_datetime(df[detected_date_column])
                except Exception as e:
                    print(f"  [ERROR] No se pudo convertir '{detected_date_column}' a fecha: {e}")
                    continue

            # Agregar columna de trimestre
            df['Quarter'] = df[detected_date_column].dt.month.apply(get_quarter)

            # Exportar por trimestre
            for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
                df_quarter = df[df['Quarter'] == quarter].copy()

                # Eliminar la columna auxiliar Quarter antes de exportar
                df_quarter = df_quarter.drop('Quarter', axis=1)

                if len(df_quarter) > 0:
                    # Limpiar campos de texto (remover comas y punto y comas)
                    df_quarter = clean_dataframe_fields(df_quarter)

                    output_filename = f'pedidos.elvis.{year}.{quarter}.csv'
                    output_path = os.path.join(script_dir, output_filename)

                    # Exportar con ; como separador y , como separador decimal
                    df_quarter.to_csv(
                        output_path,
                        index=False,
                        encoding='utf-8-sig',
                        sep=';',
                        decimal=','
                    )

                    file_size_mb = os.path.getsize(output_path) / (1024*1024)
                    print(f"  [OK] {output_filename} - {len(df_quarter)} filas - {file_size_mb:.2f} MB")
                else:
                    print(f"  [AVISO] {year}.{quarter} - Sin datos")

        print("\n[OK] Proceso completado exitosamente!")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo Excel en {excel_file_path}")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
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
            print("Uso: python extract_elvis_pedidos.py [nombre_archivo.xlsx]")
            sys.exit(1)
        elif len(excel_files) == 1:
            excel_path = os.path.join(script_dir, excel_files[0])
            print(f"Usando archivo encontrado: {excel_files[0]}\n")
        else:
            # Buscar archivos que contengan "Elvis" en el nombre
            elvis_files = [f for f in excel_files if 'Elvis' in f or 'elvis' in f]
            if elvis_files:
                excel_path = os.path.join(script_dir, elvis_files[0])
                print(f"Usando archivo de Elvis encontrado: {elvis_files[0]}\n")
            else:
                # Usar el primer archivo no temporal
                excel_path = os.path.join(script_dir, excel_files[0])
                print(f"Usando archivo: {excel_files[0]}\n")

    extract_pedidos_by_quarter(excel_path)
