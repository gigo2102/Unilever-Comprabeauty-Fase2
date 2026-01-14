"""
Script para analizar coincidencias entre columnas de archivos Elvis y Tracy.
Identifica qué columnas de diferentes archivos tienen valores en común.
"""
import pandas as pd
import os
from collections import defaultdict

def load_csv_safely(file_path, sep=';'):
    """Carga un CSV de forma segura, manejando diferentes formatos."""
    try:
        # Intentar con el separador especificado
        df = pd.read_csv(file_path, sep=sep, encoding='utf-8-sig', low_memory=False)
        return df
    except:
        # Intentar con coma si falla
        try:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8-sig', low_memory=False)
            return df
        except Exception as e:
            print(f"Error al cargar {file_path}: {e}")
            return None

def get_sample_values(df, column, n=10):
    """Obtiene valores de muestra no nulos de una columna."""
    non_null = df[column].dropna()
    if len(non_null) == 0:
        return []
    # Convertir a string y limpiar
    values = non_null.astype(str).str.strip()
    # Filtrar valores vacíos y 'nan'
    values = values[values != ''].unique()
    values = [v for v in values if v.lower() != 'nan']
    return list(values[:n])

def find_value_matches(files_data, min_matches=5):
    """
    Encuentra columnas de diferentes archivos que tienen valores en común.

    Args:
        files_data: Dict con nombre_archivo -> dataframe
        min_matches: Mínimo de valores coincidentes para considerar match
    """
    print("\n" + "="*80)
    print("ANÁLISIS DE COINCIDENCIAS ENTRE COLUMNAS")
    print("="*80)

    matches_found = []

    # Comparar Elvis con cada archivo de Tracy
    elvis_file = 'clientes.elvis.csv'
    if elvis_file not in files_data:
        print(f"Error: No se encontró {elvis_file}")
        return

    elvis_df = files_data[elvis_file]
    tracy_files = [f for f in files_data.keys() if f.startswith('tracy.')]

    print(f"\nComparando Elvis ({elvis_df.shape[0]} filas) con {len(tracy_files)} archivos Tracy...")

    for tracy_file in tracy_files:
        tracy_df = files_data[tracy_file]
        print(f"\n{'-'*80}")
        print(f"Comparando: clientes.elvis.csv <-> {tracy_file}")
        print(f"{'-'*80}")

        found_matches = False

        # Comparar cada columna de Elvis con cada columna de Tracy
        for elvis_col in elvis_df.columns:
            # Obtener valores únicos de Elvis (sample)
            elvis_values = set(elvis_df[elvis_col].dropna().astype(str).str.strip().unique()[:1000])

            if len(elvis_values) == 0:
                continue

            for tracy_col in tracy_df.columns:
                # Obtener valores únicos de Tracy
                tracy_values = set(tracy_df[tracy_col].dropna().astype(str).str.strip().unique())

                if len(tracy_values) == 0:
                    continue

                # Encontrar valores en común
                common_values = elvis_values & tracy_values

                if len(common_values) >= min_matches:
                    found_matches = True
                    match_percentage_elvis = (len(common_values) / len(elvis_values)) * 100
                    match_percentage_tracy = (len(common_values) / len(tracy_values)) * 100

                    print(f"\n[OK] COINCIDENCIA ENCONTRADA:")
                    print(f"  Elvis: [{elvis_col}] <-> Tracy: [{tracy_col}]")
                    print(f"  Valores coincidentes: {len(common_values)}")
                    print(f"  % coincidencia en Elvis: {match_percentage_elvis:.1f}%")
                    print(f"  % coincidencia en Tracy: {match_percentage_tracy:.1f}%")
                    print(f"  Ejemplos de valores coincidentes: {list(common_values)[:5]}")

                    matches_found.append({
                        'tracy_file': tracy_file,
                        'elvis_column': elvis_col,
                        'tracy_column': tracy_col,
                        'common_values': len(common_values),
                        'match_pct_elvis': match_percentage_elvis,
                        'match_pct_tracy': match_percentage_tracy,
                        'examples': list(common_values)[:5]
                    })

        if not found_matches:
            print(f"\n  [!] No se encontraron coincidencias significativas (>= {min_matches} valores)")

    return matches_found

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Archivos a analizar
    files_to_analyze = [
        'clientes.elvis.csv',
        'tracy.customer.locations.V2.csv',
        'tracy.distributors.V2.csv',
        'tracy.ecommerce.users.V2.csv',
        'tracy.logistic.code.V2.csv'
    ]

    print("="*80)
    print("CARGANDO ARCHIVOS")
    print("="*80)

    files_data = {}

    for file_name in files_to_analyze:
        file_path = os.path.join(script_dir, file_name)

        if not os.path.exists(file_path):
            print(f"[!] Archivo no encontrado: {file_name}")
            continue

        print(f"\nCargando: {file_name}")
        df = load_csv_safely(file_path)

        if df is not None:
            files_data[file_name] = df
            print(f"  [OK] Cargado: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"  Columnas: {', '.join(df.columns[:10])}" +
                  (f"... (+{len(df.columns)-10} mas)" if len(df.columns) > 10 else ""))

    if not files_data:
        print("\n[!] No se cargaron archivos para analizar.")
        return

    # Buscar coincidencias
    matches = find_value_matches(files_data, min_matches=5)

    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE COINCIDENCIAS")
    print("="*80)

    if matches:
        print(f"\nTotal de coincidencias encontradas: {len(matches)}")

        # Agrupar por archivo Tracy
        by_tracy_file = defaultdict(list)
        for match in matches:
            by_tracy_file[match['tracy_file']].append(match)

        for tracy_file, file_matches in by_tracy_file.items():
            print(f"\n{tracy_file}:")
            for match in file_matches:
                print(f"  - {match['elvis_column']} -> {match['tracy_column']} " +
                      f"({match['common_values']} valores, {match['match_pct_tracy']:.0f}% en Tracy)")
    else:
        print("\nNo se encontraron coincidencias significativas.")
        print("\nSugerencia: Revisa manualmente los archivos para identificar patrones.")

if __name__ == "__main__":
    main()
