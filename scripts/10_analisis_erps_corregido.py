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
        # El formato es: ["valor1" "valor2" "valor3"]
        # Necesitamos extraer todos los valores entre comillas
        pattern = r'"([^"]+)"'
        matches = re.findall(pattern, str(erpids_str))
        return matches
    except Exception as e:
        print(f"Error parseando: {erpids_str}, error: {e}")
        return []

# Obtener todos los erpIds únicos que están siendo usados en Tracy
print("Obteniendo erpIds únicos de Tracy...")
erpids_en_tracy_set = set(df_tracy['CUSTOMER LOCATION - ERP ID'].dropna().unique())

# Crear un diccionario normalizado para búsqueda más eficiente
erpids_en_tracy_normalized = {}
for erp in erpids_en_tracy_set:
    # Normalizar: convertir PhxId a phxId para comparación
    normalized = erp.replace('PhxId:', 'phxId:')
    erpids_en_tracy_normalized[normalized] = erp  # Guardar el valor original

print(f"Total de erpIds únicos en Tracy: {len(erpids_en_tracy_set)}")

# Mostrar algunos ejemplos de erpIds en Tracy
print("\nEjemplos de erpIds en Tracy:")
for erp in list(erpids_en_tracy_set)[:10]:
    print(f"  {erp}")

# Analizar cada customer location
print("\nAnalizando customer locations...")
resultados = []

for idx, row in df_correcto.iterrows():
    if idx % 1000 == 0:
        print(f"Procesando registro {idx}/{len(df_correcto)}...")

    customer_location_id = row['customerLocation.Id']
    erpids_array = parsear_erpids_array(row['customerLocation.erpIds'])
    contacto_elvis = row['clienteelvis.contactoid']
    user_mail = row['user.mail']

    # Buscar si alguno de los erpIds del array está en Tracy
    erpids_encontrados = []
    erpids_no_encontrados = []

    for erp in erpids_array:
        # Normalizar para comparación
        erp_normalized = erp.replace('PhxId:', 'phxId:')

        if erp_normalized in erpids_en_tracy_normalized:
            # Este erpId SÍ está en Tracy
            erpids_encontrados.append(erp)
        else:
            erpids_no_encontrados.append(erp)

    # Determinar el estado
    if len(erpids_encontrados) > 0:
        estado = 'CORRECTO'
        erpid_usado_en_tracy = ', '.join(erpids_encontrados)
    else:
        if len(erpids_array) == 0:
            estado = 'SIN ERPIDS'
            erpid_usado_en_tracy = 'NO GENERADO'
        else:
            estado = 'PISADO'
            erpid_usado_en_tracy = 'NINGUNO ENCONTRADO'

    resultado = {
        'customerLocation.Id': customer_location_id,
        'contacto_elvis': contacto_elvis,
        'erpIds_correctos_completo': str(erpids_array),
        'erpIds_encontrados_en_tracy': erpid_usado_en_tracy,
        'erpIds_no_encontrados': ', '.join(erpids_no_encontrados) if erpids_no_encontrados else 'N/A',
        'estado': estado,
        'cantidad_erpIds_totales': len(erpids_array),
        'cantidad_encontrados': len(erpids_encontrados),
        'cantidad_no_encontrados': len(erpids_no_encontrados),
        'user.mail': user_mail
    }

    resultados.append(resultado)

df_resultado = pd.DataFrame(resultados)

# Estadísticas
total = len(df_resultado)
correctos = (df_resultado['estado'] == 'CORRECTO').sum()
pisados = (df_resultado['estado'] == 'PISADO').sum()
sin_erpids = (df_resultado['estado'] == 'SIN ERPIDS').sum()

print(f"\n{'='*80}")
print(f"ANÁLISIS COMPLETO CON ARRAYS DE ERPIDs")
print(f"{'='*80}")
print(f"Total de customer locations: {total}")
print(f"Customer locations CORRECTOS (al menos 1 erpId existe en Tracy): {correctos}")
print(f"Customer locations PISADOS (ningún erpId existe en Tracy): {pisados}")
print(f"Customer locations SIN ERPIDS (no se generaron erpIds): {sin_erpids}")
print(f"\nPorcentajes:")
print(f"  CORRECTOS: {(correctos/total)*100:.2f}%")
print(f"  PISADOS: {(pisados/total)*100:.2f}%")
print(f"  SIN ERPIDS: {(sin_erpids/total)*100:.2f}%")

print(f"\n{'='*80}")
print("EJEMPLOS DE CUSTOMER LOCATIONS CORRECTOS:")
print(f"{'='*80}")
ejemplos_correctos = df_resultado[df_resultado['estado'] == 'CORRECTO'].head(15)
for idx, ejemplo in ejemplos_correctos.iterrows():
    print(f"\nCustomer Location ID: {ejemplo['customerLocation.Id']}")
    print(f"  Contacto Elvis: {ejemplo['contacto_elvis']}")
    print(f"  ErpIds completos: {ejemplo['erpIds_correctos_completo']}")
    print(f"  ErpIds ENCONTRADOS en Tracy: {ejemplo['erpIds_encontrados_en_tracy']}")
    if ejemplo['erpIds_no_encontrados'] != 'N/A':
        print(f"  ErpIds NO encontrados: {ejemplo['erpIds_no_encontrados']}")

print(f"\n{'='*80}")
print("EJEMPLOS DE CUSTOMER LOCATIONS PISADOS:")
print(f"{'='*80}")
ejemplos_pisados = df_resultado[df_resultado['estado'] == 'PISADO'].head(15)
for idx, ejemplo in ejemplos_pisados.iterrows():
    print(f"\nCustomer Location ID: {ejemplo['customerLocation.Id']}")
    print(f"  Contacto Elvis: {ejemplo['contacto_elvis']}")
    print(f"  ErpIds que deberían estar: {ejemplo['erpIds_correctos_completo']}")
    print(f"  Estado en Tracy: {ejemplo['erpIds_encontrados_en_tracy']}")

# Análisis adicional
print(f"\n{'='*80}")
print("ANÁLISIS ESTADÍSTICO DETALLADO:")
print(f"{'='*80}")

# Customer locations con y sin ID
con_id = df_resultado['customerLocation.Id'].notna().sum()
sin_id = total - con_id
print(f"Customer locations con ID: {con_id}")
print(f"Customer locations sin ID: {sin_id}")

# De los correctos, análisis de erpIds
if correctos > 0:
    promedio_erpids_correctos = df_resultado[df_resultado['estado'] == 'CORRECTO']['cantidad_erpIds_totales'].mean()
    promedio_encontrados = df_resultado[df_resultado['estado'] == 'CORRECTO']['cantidad_encontrados'].mean()
    print(f"\nCustomer locations CORRECTOS:")
    print(f"  Promedio de erpIds totales: {promedio_erpids_correctos:.2f}")
    print(f"  Promedio de erpIds encontrados en Tracy: {promedio_encontrados:.2f}")

# De los pisados
if pisados > 0:
    promedio_erpids_pisados = df_resultado[df_resultado['estado'] == 'PISADO']['cantidad_erpIds_totales'].mean()
    print(f"\nCustomer locations PISADOS:")
    print(f"  Promedio de erpIds totales: {promedio_erpids_pisados:.2f}")
    print(f"  Todos estos erpIds deberían estar en Tracy pero NO están")

# Guardar resultado
output_file = 'analisis_erps_completo_corregido.xlsx'
print(f"\n{'='*80}")
print(f"Guardando análisis en {output_file}...")
df_resultado.to_excel(output_file, index=False)

print(f"\n¡Análisis completado!")
print(f"Archivo guardado: {output_file}")
