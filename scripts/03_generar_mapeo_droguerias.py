"""
Script para extraer valores únicos de la columna DROGUERIA
de todos los CSVs de Elvis y generar un Excel con 2 columnas
para mapeo ELVIS -> TRACY
"""
import pandas as pd
import os

def extract_unique_droguerias():
    """
    Extrae valores únicos de DROGUERIA de todos los CSVs y crea un Excel
    con 2 columnas (DROGUERIAS ELVIS y DROGUERIAS TRACY) para mapeo.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Lista de archivos CSV a procesar
    csv_files = [
        'pedidos.elvis.2020.Q2.csv',
        'pedidos.elvis.2020.Q3.csv',
        'pedidos.elvis.2020.Q4.csv',
        'pedidos.elvis.2021.Q1.csv',
        'pedidos.elvis.2021.Q2.csv',
        'pedidos.elvis.2021.Q3.csv',
        'pedidos.elvis.2021.Q4.csv',
        'pedidos.elvis.2022.Q1.csv',
        'pedidos.elvis.2022.Q2.csv',
        'pedidos.elvis.2022.Q3.csv',
        'pedidos.elvis.2022.Q4.csv',
        'pedidos.elvis.2023.Q1.csv',
        'pedidos.elvis.2023.Q2.csv',
        'pedidos.elvis.2023.Q3.csv',
        'pedidos.elvis.2023.Q4.csv',
        'pedidos.elvis.2024.Q1.csv',
        'pedidos.elvis.2024.Q2.csv',
        'pedidos.elvis.2024.Q3.csv',
        'pedidos.elvis.2024.Q4.csv',
        'pedidos.elvis.2025.Q1.csv',
        'pedidos.elvis.2025.Q2.csv',
        'clientes.elvis.csv'
    ]

    print("Extrayendo valores únicos de la columna DROGUERIA...")
    print(f"Procesando {len(csv_files)} archivos CSV\n")

    # Set para almacenar valores únicos
    unique_droguerias = set()

    # Procesar cada archivo
    for csv_file in csv_files:
        file_path = os.path.join(script_dir, csv_file)

        if not os.path.exists(file_path):
            print(f"[AVISO] No se encontró: {csv_file}")
            continue

        try:
            # Leer CSV con separador ; y decimal ,
            df = pd.read_csv(file_path, sep=';', decimal=',', encoding='utf-8-sig')

            # Buscar columna DROGUERIA (puede estar en mayúsculas o minúsculas)
            drogueria_col = None
            for col in df.columns:
                if col.upper() == 'DROGUERIA':
                    drogueria_col = col
                    break

            if drogueria_col:
                # Extraer valores únicos no nulos
                valores = df[drogueria_col].dropna().unique()
                unique_droguerias.update(valores)
                print(f"[OK] {csv_file} - {len(valores)} droguerías únicas encontradas")
            else:
                print(f"[AVISO] {csv_file} - No tiene columna DROGUERIA")

        except Exception as e:
            print(f"[ERROR] {csv_file} - {e}")

    # Convertir set a lista ordenada
    droguerias_list = sorted(list(unique_droguerias))

    print(f"\n[OK] Total de droguerías únicas encontradas: {len(droguerias_list)}")

    # Crear DataFrame con 2 columnas idénticas
    df_output = pd.DataFrame({
        'DROGUERIAS ELVIS': droguerias_list,
        'DROGUERIAS TRACY': droguerias_list  # Inicialmente igual, para que el usuario las modifique
    })

    # Guardar como Excel
    output_file = os.path.join(script_dir, 'mapeo_droguerias_elvis_tracy.xlsx')
    df_output.to_excel(output_file, index=False, sheet_name='Mapeo Droguerias')

    print(f"\n[OK] Archivo Excel generado: mapeo_droguerias_elvis_tracy.xlsx")
    print(f"Filas: {len(df_output)}")
    print(f"Tamaño: {os.path.getsize(output_file) / 1024:.2f} KB")
    print("\nAhora puedes editar la columna 'DROGUERIAS TRACY' con los nombres correctos.")

if __name__ == "__main__":
    extract_unique_droguerias()
