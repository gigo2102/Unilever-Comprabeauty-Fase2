import pandas as pd
import sys
from datetime import datetime
import os

def load_drogueria_mapping(mapping_file):
    """
    Carga el mapeo de droguerias Elvis -> Tracy desde archivo Excel.
    Maneja correctamente nombres de columnas con espacios y limpia los valores.
    """
    try:
        df_mapping = pd.read_excel(mapping_file)

        # Limpiar nombres de columnas (pueden tener espacios al final)
        df_mapping.columns = df_mapping.columns.str.strip()

        # Detectar columnas dinámicamente
        col_elvis = [c for c in df_mapping.columns if 'ELVIS' in c.upper()][0]
        col_tracy = [c for c in df_mapping.columns if 'TRACY' in c.upper()][0]

        print(f"Cargando mapeo de droguerias desde: {os.path.basename(mapping_file)}")
        print(f"  Columna origen: '{col_elvis}'")
        print(f"  Columna destino: '{col_tracy}'")

        # Limpiar valores (espacios al inicio y final)
        df_mapping[col_elvis] = df_mapping[col_elvis].str.strip()
        df_mapping[col_tracy] = df_mapping[col_tracy].str.strip()

        # Crear diccionario de mapeo
        mapping_dict = dict(zip(df_mapping[col_elvis], df_mapping[col_tracy]))

        print(f"  Total de mapeos cargados: {len(mapping_dict)}")
        print(f"  Ejemplos: '{list(mapping_dict.items())[0][0]}' -> '{list(mapping_dict.items())[0][1]}'")

        return mapping_dict

    except Exception as e:
        print(f"ERROR cargando mapeo de droguerias: {e}")
        import traceback
        traceback.print_exc()
        return {}

def map_estado(estado_elvis):
    """
    Mapea estados de Elvis a Tracy según documentación:
    - Validado -> FINALIZADO
    - Pendiente -> ENVIADO
    - Cancelado -> CANCELADO
    - Borrador -> BORRADOR
    - Otros -> NUEVO
    """
    if pd.isna(estado_elvis):
        return 'NUEVO'

    estado_str = str(estado_elvis).strip().upper()

    if estado_str in ['VALIDADO', 'VALIDADA']:
        return 'FINALIZADO'
    elif estado_str in ['PENDIENTE', 'PENDIENTE DE ENVIO']:
        return 'ENVIADO'
    elif estado_str in ['CANCELADO', 'CANCELADA']:
        return 'CANCELADO'
    elif estado_str in ['BORRADOR']:
        return 'BORRADOR'
    else:
        return 'NUEVO'

def transform_sheet(df_elvis, drogueria_map):
    """
    Transforma una hoja de Elvis a formato Tracy.
    Aplica todos los mapeos según documentación.
    """
    df_tracy = pd.DataFrame()

    # ORDER ERP ID: ID del pedido
    df_tracy['ORDER ERP ID'] = df_elvis['PEDIDO']

    # CUSTOMER LOCATION - ERP ID: CONTACTO ID con prefijo phxId:
    df_tracy['CUSTOMER LOCATION - ERP ID'] = 'phxId:' + df_elvis['CONTACTO ID'].astype(str)

    # Campos directos
    df_tracy['FECHA'] = df_elvis['FECHA']
    df_tracy['EAN'] = df_elvis['EAN 13']

    # ESTADO: mapear según reglas
    df_tracy['ESTADO'] = df_elvis['ESTADO'].apply(map_estado)

    # ORIGEN: siempre CB PHARMEXX según documentación
    df_tracy['ORIGEN'] = 'CB PHARMEXX'

    # DROGUERIA: mapear usando diccionario Excel
    if drogueria_map:
        # Limpiar espacios de los valores de Elvis antes de mapear
        drogueria_clean = df_elvis['DROGUERIA'].str.strip()
        # Aplicar mapeo, si no existe mantener valor limpio
        df_tracy['DROGUERIA'] = drogueria_clean.map(drogueria_map).fillna(drogueria_clean)
    else:
        df_tracy['DROGUERIA'] = df_elvis['DROGUERIA'].str.strip()

    # CODIGO CLIENTE
    df_tracy['CODIGO CLIENTE'] = df_elvis['CODIGO']

    # OBSERVACIONES: manejar variaciones de nombre de columna
    comentario_col = 'COMENTARIO' if 'COMENTARIO' in df_elvis.columns else 'COMENTARIO '
    df_tracy['OBSERVACIONES'] = df_elvis[comentario_col]

    # Campos numéricos
    df_tracy['CANTIDAD'] = df_elvis['P. U.']
    df_tracy['ATENDIDAS'] = df_elvis['ATENDIDAS']
    df_tracy['RECHAZADAS'] = df_elvis['P. U.'] - df_elvis['ATENDIDAS']
    df_tracy['P. COSTO BRUTO'] = df_elvis['P. COSTO BRUTO']
    df_tracy['P. DESCUENTO %'] = df_elvis['P. DESCUENTO %']
    df_tracy['P. COSTO NETO'] = df_elvis['P. COSTO NETO']
    df_tracy['COMBOS'] = df_elvis['COMBOS']
    df_tracy['P. DESCUENTO CUPON %'] = df_elvis['P. DESCUENTO CUPON %']
    df_tracy['CODIGOCUPON'] = df_elvis['CODIGOCUPON']

    return df_tracy

def transform_elvis_to_tracy(input_file, output_file, drogueria_mapping_file):
    """
    Transforma archivo Elvis completo a formato Tracy.
    Procesa todas las hojas de años y genera archivo de salida.
    """
    print("=" * 70)
    print("TRANSFORMACION ELVIS -> TRACY")
    print("=" * 70)
    print(f"\nArchivo entrada: {os.path.basename(input_file)}")
    print(f"Archivo salida:  {os.path.basename(output_file)}")
    print()

    # Cargar mapeo de droguerias
    drogueria_map = load_drogueria_mapping(drogueria_mapping_file)

    if not drogueria_map:
        print("\nADVERTENCIA: No se pudo cargar el mapeo de droguerias")
        print("Las droguerias se copiarán sin transformar\n")

    # Abrir archivo Excel
    print("\nAbriendo archivo Elvis...")
    xls = pd.ExcelFile(input_file)

    # Filtrar hojas de años (contienen "o 20" para detectar "Año 20XX")
    year_sheets = [s for s in xls.sheet_names if 'o 20' in s]

    print(f"Hojas de años encontradas: {len(year_sheets)}")
    for sheet in year_sheets:
        print(f"  - {sheet}")
    print()

    # Procesar cada hoja
    all_data = []

    for i, sheet_name in enumerate(year_sheets, 1):
        print(f"[{i}/{len(year_sheets)}] Procesando: {sheet_name}")

        # Leer datos
        df_elvis = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"  Registros leidos: {len(df_elvis):,}")

        # Transformar
        df_tracy = transform_sheet(df_elvis, drogueria_map)
        print(f"  Registros transformados: {len(df_tracy):,}")

        all_data.append(df_tracy)

        # Liberar memoria
        del df_elvis

    # Verificar que hay datos
    if not all_data:
        print("\nERROR: No se encontraron datos para transformar")
        return False

    # Guardar archivo
    total_records = sum(len(df) for df in all_data)

    print(f"\n{'=' * 70}")
    print(f"GUARDANDO ARCHIVO")
    print(f"{'=' * 70}")
    print(f"Total registros a guardar: {total_records:,}")
    print(f"Archivo: {output_file}\n")

    # Usar xlsxwriter (más rápido para archivos grandes)
    with pd.ExcelWriter(output_file, engine='xlsxwriter',
                       engine_kwargs={'options': {'strings_to_numbers': False}}) as writer:

        for sheet_name, df_year in zip(year_sheets, all_data):
            # Extraer año del nombre
            year = sheet_name.replace('Año ', '').replace('A�o ', '').replace('Ano ', '').strip()
            sheet_name_tracy = f'Año {year}'

            print(f"  Escribiendo hoja '{sheet_name_tracy}': {len(df_year):,} registros")
            df_year.to_excel(writer, sheet_name=sheet_name_tracy, index=False)

    print(f"\n{'=' * 70}")
    print(f"COMPLETADO EXITOSAMENTE")
    print(f"{'=' * 70}")
    print(f"Archivo generado: {output_file}")
    print(f"Total registros: {total_records:,}")
    print(f"{'=' * 70}\n")

    return True

if __name__ == "__main__":
    # Obtener directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir rutas absolutas
    input_file = os.path.join(script_dir, "Base Elvis 2025.xlsx")
    output_file = os.path.join(script_dir, "Tracy 2025.xlsx")
    drogueria_mapping_file = os.path.join(script_dir, "mapeo_droguerias_elvis_tracy.xlsx")

    try:
        success = transform_elvis_to_tracy(input_file, output_file, drogueria_mapping_file)
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n{'=' * 70}")
        print(f"ERROR FATAL")
        print(f"{'=' * 70}")
        print(f"{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
