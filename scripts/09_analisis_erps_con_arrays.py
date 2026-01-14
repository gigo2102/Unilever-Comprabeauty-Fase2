import pandas as pd
import re
import ast

print("Leyendo archivos...")
df_correcto = pd.read_excel('06 update phxId customer location.xlsx')
df_tracy = pd.read_excel('Tracy 2025 FINAL.xlsx')

# Función para parsear el array de erpIds
def parsear_erpids_array(erpids_str):
    if pd.isna(erpids_str):
        return []
    try:
        # Convertir el formato numpy array string a lista Python
        # Ejemplo: ["PhxId:621" "TauOldId:1110-10100-30708489766*01" "10100-88836"]
        # Primero, agregar comas entre los elementos
        erpids_str = str(erpids_str)
        # Reemplazar '" "' con '", "'
        erpids_fixed = erpids_str.replace('" "', '", ')
        # Intentar evaluar como lista
        erpids_list = ast.literal_eval(erpids_fixed)
        return erpids_list
    except:
        return []

# Obtener todos los erpIds únicos que están siendo usados en Tracy
print("Obteniendo erpIds únicos de Tracy...")
erpids_en_tracy_set = set(df_tracy['CUSTOMER LOCATION - ERP ID'].dropna().unique())

# Normalizar para comparación (convertir PhxId a phxId)
erpids_en_tracy_normalized = {}
for erp in erpids_en_tracy_set:
    normalized = erp.replace('PhxId:', 'phxId:')
    erpids_en_tracy_normalized[normalized] = erp  # Guardar original

print(f"Total de erpIds únicos en Tracy: {len(erpids_en_tracy_set)}")

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

print(f"\n{'='*80}")
print(f"ANÁLISIS COMPLETO CON ARRAYS DE ERPIDs")
print(f"{'='*80}")
print(f"Total de customer locations: {total}")
print(f"Customer locations CORRECTOS (al menos 1 erpId existe en Tracy): {correctos}")
print(f"Customer locations PISADOS (ningún erpId existe en Tracy): {pisados}")
print(f"Porcentaje de correctos: {(correctos/total)*100:.2f}%")
print(f"Porcentaje de pisados: {(pisados/total)*100:.2f}%")

print(f"\n{'='*80}")
print("EJEMPLOS DE CUSTOMER LOCATIONS CORRECTOS:")
print(f"{'='*80}")
ejemplos_correctos = df_resultado[df_resultado['estado'] == 'CORRECTO'].head(10)
for idx, ejemplo in ejemplos_correctos.iterrows():
    print(f"\nCustomer Location ID: {ejemplo['customerLocation.Id']}")
    print(f"  Contacto Elvis: {ejemplo['contacto_elvis']}")
    print(f"  ErpIds encontrados en Tracy: {ejemplo['erpIds_encontrados_en_tracy']}")
    print(f"  ErpIds NO encontrados: {ejemplo['erpIds_no_encontrados']}")

print(f"\n{'='*80}")
print("EJEMPLOS DE CUSTOMER LOCATIONS PISADOS:")
print(f"{'='*80}")
ejemplos_pisados = df_resultado[df_resultado['estado'] == 'PISADO'].head(10)
for idx, ejemplo in ejemplos_pisados.iterrows():
    print(f"\nCustomer Location ID: {ejemplo['customerLocation.Id']}")
    print(f"  Contacto Elvis: {ejemplo['contacto_elvis']}")
    print(f"  ErpIds que deberían estar: {ejemplo['erpIds_correctos_completo'][:100]}...")
    print(f"  Estado: {ejemplo['erpIds_encontrados_en_tracy']}")

# Análisis adicional
print(f"\n{'='*80}")
print("ANÁLISIS ESTADÍSTICO DETALLADO:")
print(f"{'='*80}")

# Customer locations con y sin ID
con_id = df_resultado['customerLocation.Id'].notna().sum()
sin_id = total - con_id
print(f"Customer locations con ID: {con_id}")
print(f"Customer locations sin ID: {sin_id}")

# De los correctos, cuántos erpIds tienen en promedio
promedio_erpids_correctos = df_resultado[df_resultado['estado'] == 'CORRECTO']['cantidad_erpIds_totales'].mean()
promedio_encontrados = df_resultado[df_resultado['estado'] == 'CORRECTO']['cantidad_encontrados'].mean()
print(f"\nCustomer locations CORRECTOS:")
print(f"  Promedio de erpIds totales por customer location: {promedio_erpids_correctos:.2f}")
print(f"  Promedio de erpIds encontrados en Tracy: {promedio_encontrados:.2f}")

# De los pisados
promedio_erpids_pisados = df_resultado[df_resultado['estado'] == 'PISADO']['cantidad_erpIds_totales'].mean()
print(f"\nCustomer locations PISADOS:")
print(f"  Promedio de erpIds totales por customer location: {promedio_erpids_pisados:.2f}")

# Guardar resultado
output_file = 'analisis_erps_con_arrays.xlsx'
print(f"\n{'='*80}")
print(f"Guardando análisis en {output_file}...")
df_resultado.to_excel(output_file, index=False)

print(f"\n¡Análisis completado!")
print(f"Archivo guardado: {output_file}")
