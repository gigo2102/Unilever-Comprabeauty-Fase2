import pandas as pd
import numpy as np
import json

print("="*80)
print("GENERANDO ARCHIVO FINAL: 06 update phxId customer location FINAL.xlsx")
print("="*80)

print("\nLeyendo archivos...")
# Leer archivo original
df_original = pd.read_excel('06 update phxId customer location.xlsx')
print(f"[OK] Archivo original leido: {len(df_original):,} registros")

# Leer archivo de actualizacion con erpIds correctos
df_update = pd.read_excel('UPDATE_CUSTOMER_LOCATION_ERPIDS_PISADOS.xlsx')
print(f"[OK] Archivo de actualizacion leido: {len(df_update):,} registros")

# Leer Tracy para obtener erpIds actuales
df_tracy = pd.read_excel('Tracy 2025 FINAL.xlsx')
print(f"[OK] Tracy leido: {len(df_tracy):,} registros")

print(f"\n{'='*80}")
print("ANALISIS DEL ARCHIVO ORIGINAL")
print(f"{'='*80}")

# Contar registros vacios en customerLocation.erpIds
total_registros = len(df_original)
vacios = df_original['customerLocation.erpIds'].isna().sum()
completos = total_registros - vacios

print(f"Total de registros: {total_registros:,}")
print(f"Registros con erpIds: {completos:,}")
print(f"Registros sin erpIds (vacios): {vacios:,}")

# Crear copia para trabajar
df_final = df_original.copy()

print(f"\n{'='*80}")
print("COMPLETANDO REGISTROS VACIOS")
print(f"{'='*80}")

# Crear diccionario de actualizacion por customerLocation.Id
update_dict = {}
for idx, row in df_update.iterrows():
    cl_id = str(row['customerLocation.Id']).replace(',', '').strip()
    erpids_json = row['customerLocation.erpIds']
    update_dict[cl_id] = erpids_json

print(f"Diccionario de actualizacion creado con {len(update_dict):,} registros")

# Completar los registros vacios
completados = 0
no_completados = 0

print("\nProcesando registros...")
for idx, row in df_final.iterrows():
    if idx % 1000 == 0:
        print(f"  Procesando registro {idx}/{len(df_final)}...")

    # Si el erpIds esta vacio, intentar completarlo
    if pd.isna(row['customerLocation.erpIds']):
        cl_id = row['customerLocation.Id']
        contacto_elvis = row['clienteelvis.contactoid']

        # Intentar buscar por customerLocation.Id
        if pd.notna(cl_id):
            cl_id_str = str(cl_id).replace(',', '').strip()

            if cl_id_str in update_dict:
                # Obtener erpIds del diccionario
                erpids_json = update_dict[cl_id_str]

                # Convertir JSON a formato array para Excel
                erpids_list = json.loads(erpids_json)

                # Formatear como el formato original: ["valor1" "valor2" "valor3"]
                erpids_formatted = '["' + '" "'.join(erpids_list) + '"]'

                df_final.at[idx, 'customerLocation.erpIds'] = erpids_formatted
                completados += 1
                continue

        # Si no se encontro por ID, intentar generar erpId basico por contacto
        if pd.notna(contacto_elvis):
            # Generar erpId basico: PhxId:{contacto}
            erpid_basico = f'PhxId:{int(contacto_elvis)}'
            erpids_formatted = f'["{erpid_basico}"]'

            df_final.at[idx, 'customerLocation.erpIds'] = erpids_formatted
            completados += 1
        else:
            no_completados += 1

print(f"\n{'='*80}")
print("RESULTADO DEL PROCESAMIENTO")
print(f"{'='*80}")
print(f"Registros completados exitosamente: {completados:,}")
print(f"Registros que no se pudieron completar: {no_completados:,}")

# Verificar resultado final
vacios_final = df_final['customerLocation.erpIds'].isna().sum()
completos_final = len(df_final) - vacios_final

print(f"\n{'='*80}")
print("ESTADO FINAL")
print(f"{'='*80}")
print(f"Total de registros: {len(df_final):,}")
print(f"Registros con erpIds: {completos_final:,}")
print(f"Registros sin erpIds: {vacios_final:,}")
print(f"\nMejora: {completos_final - completos:,} registros completados")

# Guardar archivo final
output_file = '06 update phxId customer location FINAL.xlsx'
print(f"\n{'='*80}")
print(f"GUARDANDO ARCHIVO FINAL: {output_file}")
print(f"{'='*80}")

df_final.to_excel(output_file, index=False)

print(f"[OK] Archivo guardado exitosamente!")

# Mostrar ejemplos de registros completados
print(f"\n{'='*80}")
print("EJEMPLOS DE REGISTROS COMPLETADOS")
print(f"{'='*80}")

# Encontrar registros que fueron completados (estaban vacios en original)
df_original['estaba_vacio'] = df_original['customerLocation.erpIds'].isna()
df_completados = df_final[df_original['estaba_vacio'] & df_final['customerLocation.erpIds'].notna()].head(10)

if len(df_completados) > 0:
    for idx, row in df_completados.iterrows():
        print(f"\nCustomer Location ID: {row['customerLocation.Id']}")
        print(f"  Contacto Elvis: {row['clienteelvis.contactoid']}")
        print(f"  ErpIds COMPLETADOS: {row['customerLocation.erpIds']}")
        print(f"  Usuario: {row['user.mail']}")
else:
    print("No hay ejemplos disponibles")

# Generar resumen estadistico
print(f"\n{'='*80}")
print("RESUMEN COMPARATIVO")
print(f"{'='*80}")

resumen = pd.DataFrame({
    'Archivo': ['Original', 'Final'],
    'Total Registros': [len(df_original), len(df_final)],
    'Con erpIds': [completos, completos_final],
    'Sin erpIds': [vacios, vacios_final],
    '% Completo': [
        f"{(completos/len(df_original)*100):.2f}%",
        f"{(completos_final/len(df_final)*100):.2f}%"
    ]
})

print(resumen.to_string(index=False))

print(f"\n{'='*80}")
print("PROCESO COMPLETADO EXITOSAMENTE!")
print(f"{'='*80}")
print(f"Archivo generado: {output_file}")
print(f"Total de registros completados: {completados:,}")
