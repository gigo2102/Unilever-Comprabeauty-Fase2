import pandas as pd
import re

print("Leyendo archivos...")
df_correcto = pd.read_excel('06 update phxId customer location.xlsx')
df_tracy = pd.read_excel('Tracy 2025 FINAL.xlsx')

# Función para parsear el array de erpIds
def parsear_erpids_array(erpids_str):
    if pd.isna(erpids_str):
        return []
    try:
        pattern = r'"([^"]+)"'
        matches = re.findall(pattern, str(erpids_str))
        return matches
    except:
        return []

print("Obteniendo erpIds únicos de Tracy...")
erpids_en_tracy_set = set(df_tracy['CUSTOMER LOCATION - ERP ID'].dropna().unique())

# Crear diccionario normalizado
erpids_en_tracy_normalized = {}
for erp in erpids_en_tracy_set:
    normalized = erp.replace('PhxId:', 'phxId:')
    erpids_en_tracy_normalized[normalized] = erp

print(f"Total de erpIds únicos en Tracy: {len(erpids_en_tracy_set)}")

# Para cada contacto de Elvis, buscar qué erpIds están siendo usados en Tracy
print("\nBuscando erpIds actuales por contacto de Elvis...")

# Obtener la frecuencia de uso de cada erpId en Tracy (para saber cuál es el más usado)
erpid_counts = df_tracy['CUSTOMER LOCATION - ERP ID'].value_counts()

# Analizar cada customer location
print("Procesando customer locations...")
resultados = []

for idx, row in df_correcto.iterrows():
    if idx % 1000 == 0:
        print(f"Procesando registro {idx}/{len(df_correcto)}...")

    customer_location_id = row['customerLocation.Id']
    erpids_array = parsear_erpids_array(row['customerLocation.erpIds'])
    contacto_elvis = row['clienteelvis.contactoid']
    user_mail = row['user.mail']

    # Buscar cuáles de los erpIds correctos están en Tracy
    erpids_encontrados = []
    erpids_no_encontrados = []

    for erp in erpids_array:
        erp_normalized = erp.replace('PhxId:', 'phxId:')
        if erp_normalized in erpids_en_tracy_normalized:
            erpids_encontrados.append(erp)
        else:
            erpids_no_encontrados.append(erp)

    # Buscar si hay algún erpId en Tracy que corresponda a este contacto de Elvis
    # Buscar phxId:{contacto_elvis} en Tracy
    erpids_actuales_en_tracy = []
    if pd.notna(contacto_elvis):
        patron_busqueda = f"phxId:{int(contacto_elvis)}"
        patron_busqueda2 = f"PhxId:{int(contacto_elvis)}"

        # Buscar en el conjunto de erpIds
        if patron_busqueda in erpids_en_tracy_normalized:
            erpid_actual = erpids_en_tracy_normalized[patron_busqueda]
            count = erpid_counts.get(erpid_actual, 0)
            erpids_actuales_en_tracy.append(f"{erpid_actual} (usado en {count} pedidos)")

        if patron_busqueda2 in erpids_en_tracy_set:
            count = erpid_counts.get(patron_busqueda2, 0)
            if patron_busqueda2 not in [e.split(' ')[0] for e in erpids_actuales_en_tracy]:
                erpids_actuales_en_tracy.append(f"{patron_busqueda2} (usado en {count} pedidos)")

    # Determinar el estado
    if len(erpids_encontrados) > 0:
        estado = 'CORRECTO'
    elif len(erpids_array) == 0:
        estado = 'SIN ERPIDS'
    else:
        estado = 'PISADO'

    resultado = {
        'customerLocation.Id': customer_location_id,
        'contacto_elvis': contacto_elvis,
        'user.mail': user_mail,
        'erpIds_correctos_generados': '; '.join(erpids_array) if erpids_array else 'N/A',
        'erpIds_correctos_encontrados_en_tracy': '; '.join(erpids_encontrados) if erpids_encontrados else 'NINGUNO',
        'erpIds_correctos_NO_encontrados': '; '.join(erpids_no_encontrados) if erpids_no_encontrados else 'N/A',
        'erpId_actual_en_tracy': '; '.join(erpids_actuales_en_tracy) if erpids_actuales_en_tracy else 'NO ENCONTRADO',
        'estado': estado,
        'fue_pisado': 'SÍ' if estado == 'PISADO' else 'NO'
    }

    resultados.append(resultado)

df_resultado = pd.DataFrame(resultados)

# Estadísticas
total = len(df_resultado)
correctos = (df_resultado['estado'] == 'CORRECTO').sum()
pisados = (df_resultado['estado'] == 'PISADO').sum()
sin_erpids = (df_resultado['estado'] == 'SIN ERPIDS').sum()

print(f"\n{'='*80}")
print(f"RESUMEN FINAL")
print(f"{'='*80}")
print(f"Total de customer locations: {total:,}")
print(f"  CORRECTOS: {correctos:,} ({(correctos/total)*100:.2f}%)")
print(f"  PISADOS: {pisados:,} ({(pisados/total)*100:.2f}%)")
print(f"  SIN ERPIDS: {sin_erpids:,} ({(sin_erpids/total)*100:.2f}%)")

# Guardar resultado
output_file = '06_update_phxId_customer_location_CON_COMPARACION.xlsx'
print(f"\n{'='*80}")
print(f"Guardando archivo en {output_file}...")

# Ordenar las columnas para mejor visualización
df_resultado_ordenado = df_resultado[[
    'customerLocation.Id',
    'contacto_elvis',
    'estado',
    'fue_pisado',
    'erpIds_correctos_generados',
    'erpIds_correctos_encontrados_en_tracy',
    'erpId_actual_en_tracy',
    'erpIds_correctos_NO_encontrados',
    'user.mail'
]]

df_resultado_ordenado.to_excel(output_file, index=False)

# Crear también un resumen de los pisados
print("\nGenerando resumen de customer locations PISADOS...")
df_pisados = df_resultado[df_resultado['estado'] == 'PISADO'][
    ['customerLocation.Id', 'contacto_elvis', 'erpIds_correctos_generados',
     'erpId_actual_en_tracy', 'user.mail']
]

output_pisados = 'RESUMEN_CUSTOMER_LOCATIONS_PISADOS.xlsx'
df_pisados.to_excel(output_pisados, index=False)

print(f"\n{'='*80}")
print(f"ARCHIVOS GENERADOS:")
print(f"{'='*80}")
print(f"1. {output_file}")
print(f"   - Contiene TODOS los customer locations con comparación completa")
print(f"   - Columnas: ID, contacto Elvis, estado, erpIds correctos, erpIds actuales en Tracy")
print(f"\n2. {output_pisados}")
print(f"   - Contiene SOLO los {pisados:,} customer locations PISADOS")
print(f"   - Útil para revisar y corregir los que fueron afectados")

print(f"\n¡Análisis completado exitosamente!")
