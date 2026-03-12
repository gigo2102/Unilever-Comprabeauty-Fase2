"""
Script para Generar SQL de Consolidación Final
==============================================
Genera el script SQL completo para consolidar customer locations
basándose en los resultados del análisis de consolidación.
"""

import pandas as pd
import os
import sys
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "datos_generados")

# Archivo de entrada - buscar en dos ubicaciones posibles
CONSOLIDACION_FILE = os.path.join(DATA_DIR, "10_consolidacion_completa.csv")
if not os.path.exists(CONSOLIDACION_FILE):
    CONSOLIDACION_FILE = os.path.join(DATA_DIR, "ArchivosGenerados", "10_consolidacion_completa.csv")
    DATA_DIR = os.path.join(DATA_DIR, "ArchivosGenerados")  # Actualizar DATA_DIR para salida

OUTPUT_DIR = DATA_DIR

# Nivel de confianza a procesar (ALTA, MEDIA, BAJA, o TODAS)
# Este valor se puede pasar como argumento al script
CONFIANZA_NIVEL = 'ALTA'  # Por defecto, procesar grupos de alta confianza


# ============================================================================
# FUNCIONES
# ============================================================================

def load_consolidation_data():
    """Carga los datos de consolidación."""
    print("=" * 80)
    print("CARGANDO DATOS DE CONSOLIDACION")
    print("=" * 80)

    if not os.path.exists(CONSOLIDACION_FILE):
        print(f"ERROR: No se encontró el archivo {CONSOLIDACION_FILE}")
        return None

    df = pd.read_csv(CONSOLIDACION_FILE)
    print(f"Total de registros cargados: {len(df)}")
    print(f"Grupos únicos: {df['grupo_consolidacion_id'].nunique()}")
    print(f"\nDistribución por confianza:")
    print(df['confianza'].value_counts())
    print()

    return df


def filter_by_confidence(df, nivel='ALTA'):
    """Filtra los datos por nivel de confianza."""
    print("=" * 80)
    print(f"FILTRANDO REGISTROS DE CONFIANZA: {nivel}")
    print("=" * 80)

    if nivel == 'TODAS':
        filtered = df.copy()
    else:
        filtered = df[df['confianza'] == nivel].copy()

    print(f"Registros filtrados: {len(filtered)}")
    print(f"Grupos únicos: {filtered['grupo_consolidacion_id'].nunique()}")
    print(f"Masters: {filtered['is_master'].sum()}")
    print(f"Duplicados a consolidar: {(~filtered['is_master']).sum()}")
    print()

    return filtered


def load_customer_locations():
    """Carga información adicional de customer locations."""
    csv_path = os.path.join(PROJECT_DIR, "Csvs", "CustomerLocation.csv")

    # Buscar en ubicaciones alternativas si no existe
    if not os.path.exists(csv_path):
        csv_path = os.path.join(DATA_DIR, "ArchivosGenerados", "CustomerLocation.csv")

    if not os.path.exists(csv_path):
        print("Advertencia: No se encontró CustomerLocation.csv")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    return df[['ID', 'TaxId', 'FantasyName']]


def generate_sql_script(consolidation_df, locations_df):
    """Genera el script SQL completo."""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Estadísticas
    grupos_totales = consolidation_df['grupo_consolidacion_id'].nunique()
    masters = consolidation_df['is_master'].sum()
    duplicados = (~consolidation_df['is_master']).sum()

    # Header del script
    sql = f"""-- ============================================================================
-- SCRIPT DE CONSOLIDACION DE CUSTOMER LOCATIONS - {CONFIANZA_NIVEL} CONFIANZA
-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================================
-- IMPORTANTE: Este script consolida locations duplicadas manteniendo
-- la integridad referencial y preservando el historial de pedidos.
--
-- Total de grupos a consolidar: {grupos_totales}
-- Masters a mantener: {masters}
-- Duplicados a marcar como deleted: {duplicados}
-- ============================================================================

-- PASO 1: Crear tabla de respaldo antes de comenzar
-- ============================================================================

-- Crear backup de CustomerLocation
CREATE TABLE CustomerLocation_Backup_{timestamp[:8]} AS
SELECT * FROM CustomerLocation;

-- Crear backup de orders
CREATE TABLE orders_Backup_{timestamp[:8]} AS
SELECT * FROM orders;

-- Crear backup de LogisticCode
CREATE TABLE LogisticCode_Backup_{timestamp[:8]} AS
SELECT * FROM LogisticCode;

-- Crear backup de SalesRepCustomerLocations
CREATE TABLE SalesRepCustomerLocations_Backup_{timestamp[:8]} AS
SELECT * FROM SalesRepCustomerLocations;

-- PASO 2: Crear tabla de mapeo de consolidacion
-- ============================================================================

CREATE TABLE IF NOT EXISTS ConsolidacionMapping (
    GrupoID VARCHAR(50),
    LocationDuplicadaID INT,
    LocationMasterID INT,
    CUIT VARCHAR(50),
    NombreComercial VARCHAR(255),
    CriterioAgrupacion VARCHAR(100),
    Confianza VARCHAR(20),
    FechaConsolidacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (LocationDuplicadaID)
);

-- PASO 3: Insertar mapeo de consolidacion
-- ============================================================================

"""

    # Agrupar por grupo de consolidación
    grupos = consolidation_df.groupby('grupo_consolidacion_id')

    insert_values = []

    for grupo_id, grupo_df in grupos:
        # Obtener el master
        master_row = grupo_df[grupo_df['is_master'] == True]
        if len(master_row) == 0:
            print(f"Advertencia: Grupo {grupo_id} no tiene master definido")
            continue

        master_id = master_row.iloc[0]['location_id']
        criterio = master_row.iloc[0]['criterio_agrupacion']
        confianza = master_row.iloc[0]['confianza']

        # Obtener info del master location
        master_info = locations_df[locations_df['ID'] == master_id]
        if len(master_info) > 0:
            cuit = str(master_info.iloc[0]['TaxId']).replace("'", "''") if pd.notna(master_info.iloc[0]['TaxId']) else ''
            nombre = str(master_info.iloc[0]['FantasyName']).replace("'", "''") if pd.notna(master_info.iloc[0]['FantasyName']) else ''
        else:
            cuit = ''
            nombre = ''

        # Procesar duplicados
        duplicados_df = grupo_df[grupo_df['is_master'] == False]

        for _, dup_row in duplicados_df.iterrows():
            dup_id = dup_row['location_id']
            insert_values.append(
                f"    ('{grupo_id}', {dup_id}, {master_id}, '{cuit}', '{nombre}', '{criterio}', '{confianza}')"
            )

    # Escribir INSERTs en bloques de 1000
    sql += "INSERT INTO ConsolidacionMapping (GrupoID, LocationDuplicadaID, LocationMasterID, CUIT, NombreComercial, CriterioAgrupacion, Confianza)\nVALUES\n"

    for i in range(0, len(insert_values), 1000):
        batch = insert_values[i:i+1000]
        sql += ",\n".join(batch)

        if i + 1000 < len(insert_values):
            sql += ";\n\nINSERT INTO ConsolidacionMapping (GrupoID, LocationDuplicadaID, LocationMasterID, CUIT, NombreComercial, CriterioAgrupacion, Confianza)\nVALUES\n"
        else:
            sql += ";\n\n"

    # PASO 4: Actualizar referencias en otras tablas
    sql += """-- PASO 4: Actualizar referencias de locations duplicadas
-- ============================================================================

-- 4.1: Actualizar orders
UPDATE orders o
INNER JOIN ConsolidacionMapping cm ON o.CustomerLocationId = cm.LocationDuplicadaID
SET o.CustomerLocationId = cm.LocationMasterID
WHERE o.CustomerLocationId = cm.LocationDuplicadaID;

-- 4.2: Transferir códigos logísticos de duplicados al master
-- Primero, actualizar los que ya existen en el master
UPDATE LogisticCode lc
INNER JOIN ConsolidacionMapping cm ON lc.CustomerLocationId = cm.LocationDuplicadaID
SET lc.CustomerLocationId = cm.LocationMasterID
WHERE lc.CustomerLocationId = cm.LocationDuplicadaID
AND NOT EXISTS (
    SELECT 1 FROM LogisticCode lc2
    WHERE lc2.CustomerLocationId = cm.LocationMasterID
    AND lc2.MarketplaceDistributorId = lc.MarketplaceDistributorId
    AND lc2.Code = lc.Code
);

-- Marcar como deleted los códigos que ya existen en el master
UPDATE LogisticCode lc
INNER JOIN ConsolidacionMapping cm ON lc.CustomerLocationId = cm.LocationDuplicadaID
SET lc.Deleted = 1, lc.DeletedDate = NOW()
WHERE lc.CustomerLocationId = cm.LocationDuplicadaID
AND EXISTS (
    SELECT 1 FROM LogisticCode lc2
    WHERE lc2.CustomerLocationId = cm.LocationMasterID
    AND lc2.MarketplaceDistributorId = lc.MarketplaceDistributorId
    AND lc2.Code = lc.Code
);

-- 4.3: Actualizar SalesRepCustomerLocations
UPDATE SalesRepCustomerLocations srcl
INNER JOIN ConsolidacionMapping cm ON srcl.CustomerLocationId = cm.LocationDuplicadaID
SET srcl.CustomerLocationId = cm.LocationMasterID
WHERE srcl.CustomerLocationId = cm.LocationDuplicadaID
AND NOT EXISTS (
    SELECT 1 FROM SalesRepCustomerLocations srcl2
    WHERE srcl2.CustomerLocationId = cm.LocationMasterID
    AND srcl2.SalesRepId = srcl.SalesRepId
);

-- Marcar como deleted los que ya existen en el master
UPDATE SalesRepCustomerLocations srcl
INNER JOIN ConsolidacionMapping cm ON srcl.CustomerLocationId = cm.LocationDuplicadaID
SET srcl.Deleted = 1, srcl.DeletedDate = NOW()
WHERE srcl.CustomerLocationId = cm.LocationDuplicadaID
AND EXISTS (
    SELECT 1 FROM SalesRepCustomerLocations srcl2
    WHERE srcl2.CustomerLocationId = cm.LocationMasterID
    AND srcl2.SalesRepId = srcl.SalesRepId
);

-- PASO 5: Marcar locations duplicadas como deleted
-- ============================================================================

UPDATE CustomerLocation cl
INNER JOIN ConsolidacionMapping cm ON cl.ID = cm.LocationDuplicadaID
SET cl.Deleted = 1,
    cl.DeletedDate = NOW(),
    cl.Observations = CONCAT(
        COALESCE(cl.Observations, ''),
        CASE WHEN COALESCE(cl.Observations, '') = '' THEN '' ELSE ' | ' END,
        'CONSOLIDADO EN MASTER ID: ', cm.LocationMasterID,
        ' - GRUPO: ', cm.GrupoID,
        ' - FECHA: ', DATE_FORMAT(NOW(), '%Y-%m-%d')
    )
WHERE cl.ID = cm.LocationDuplicadaID;

-- PASO 6: Verificaciones finales
-- ============================================================================

-- Verificar que no quedaron referencias huérfanas en orders
SELECT COUNT(*) as orders_huerfanos
FROM orders o
LEFT JOIN CustomerLocation cl ON o.CustomerLocationId = cl.ID
WHERE cl.ID IS NULL AND o.CustomerLocationId IS NOT NULL;

-- Verificar que las consolidaciones se aplicaron correctamente
SELECT
    cm.GrupoID as 'Grupo ID',
    cm.CriterioAgrupacion as 'Criterio de Agrupación',
    cm.Confianza,
    COUNT(*) as 'Duplicados Consolidados',
    cm.LocationMasterID as 'Master ID',
    cl.FantasyName as 'Nombre Master',
    cl.TaxId as 'CUIT Master'
FROM ConsolidacionMapping cm
INNER JOIN CustomerLocation cl ON cm.LocationMasterID = cl.ID
GROUP BY cm.GrupoID, cm.CriterioAgrupacion, cm.Confianza, cm.LocationMasterID, cl.FantasyName, cl.TaxId
ORDER BY cm.CriterioAgrupacion, cm.GrupoID;

-- Resumen de la consolidación
SELECT
    'Total Grupos Consolidados' as Metrica,
    COUNT(DISTINCT GrupoID) as Valor
FROM ConsolidacionMapping
UNION ALL
SELECT
    'Total Duplicados Consolidados' as Metrica,
    COUNT(*) as Valor
FROM ConsolidacionMapping
UNION ALL
SELECT
    'Total Masters' as Metrica,
    COUNT(DISTINCT LocationMasterID) as Valor
FROM ConsolidacionMapping
UNION ALL
SELECT
    'Orders Actualizados' as Metrica,
    COUNT(*) as Valor
FROM orders o
INNER JOIN ConsolidacionMapping cm ON o.CustomerLocationId = cm.LocationMasterID
WHERE EXISTS (
    SELECT 1 FROM ConsolidacionMapping cm2
    WHERE cm2.LocationMasterID = cm.LocationMasterID
);

-- Resumen por Criterio de Agrupación
SELECT
    CriterioAgrupacion as 'Criterio de Agrupación',
    COUNT(DISTINCT GrupoID) as 'Grupos Consolidados',
    COUNT(DISTINCT LocationMasterID) as 'Masters',
    COUNT(*) as 'Duplicados Consolidados',
    Confianza
FROM ConsolidacionMapping
GROUP BY CriterioAgrupacion, Confianza
ORDER BY CriterioAgrupacion, Confianza;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
"""

    return sql


def main(nivel_confianza=None):
    """Función principal."""
    if nivel_confianza is None:
        nivel_confianza = CONFIANZA_NIVEL

    print(f"\n{'='*80}")
    print(f"GENERADOR DE SQL DE CONSOLIDACION FINAL")
    print(f"Nivel de confianza: {nivel_confianza}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Cargar datos
    consolidation_df = load_consolidation_data()
    if consolidation_df is None:
        return

    # Filtrar por confianza
    filtered_df = filter_by_confidence(consolidation_df, nivel_confianza)

    if len(filtered_df) == 0:
        print("No hay registros para procesar.")
        return

    # Cargar información de locations
    locations_df = load_customer_locations()

    # Generar SQL
    print("=" * 80)
    print("GENERANDO SCRIPT SQL")
    print("=" * 80)

    sql_script = generate_sql_script(filtered_df, locations_df)

    # Guardar archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(OUTPUT_DIR, f"01_consolidar_{nivel_confianza.lower()}_confianza_{timestamp}.sql")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)

    print(f"Script SQL generado exitosamente:")
    print(f"  {output_file}")
    print(f"\nTamaño del archivo: {os.path.getsize(output_file) / 1024:.2f} KB")

    # Generar también CSV de resumen
    summary_file = os.path.join(OUTPUT_DIR, f"01_resumen_consolidacion_{timestamp}.csv")

    # Crear resumen por grupo
    summary_data = []
    grupos = filtered_df.groupby('grupo_consolidacion_id')

    for grupo_id, grupo_df in grupos:
        master_row = grupo_df[grupo_df['is_master'] == True]
        if len(master_row) == 0:
            continue

        master_id = master_row.iloc[0]['location_id']
        master_info = locations_df[locations_df['ID'] == master_id]

        summary_data.append({
            'grupo_id': grupo_id,
            'master_location_id': master_id,
            'master_taxid': master_info.iloc[0]['TaxId'] if len(master_info) > 0 else '',
            'master_nombre': master_info.iloc[0]['FantasyName'] if len(master_info) > 0 else '',
            'criterio_agrupacion': master_row.iloc[0]['criterio_agrupacion'],
            'confianza': master_row.iloc[0]['confianza'],
            'cantidad_duplicados': len(grupo_df) - 1,
            'locations_duplicadas': ';'.join(str(x) for x in grupo_df[grupo_df['is_master'] == False]['location_id'].tolist())
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')

    print(f"\nResumen CSV generado:")
    print(f"  {summary_file}")

    # Mostrar estadísticas por criterio de agrupación
    print()
    print("=" * 80)
    print("ESTADÍSTICAS POR CRITERIO DE AGRUPACIÓN")
    print("=" * 80)
    criterio_stats = filtered_df.groupby('criterio_agrupacion').agg({
        'grupo_consolidacion_id': 'nunique',
        'location_id': 'count'
    }).reset_index()
    criterio_stats.columns = ['Criterio', 'Grupos', 'Total Locations']

    # Calcular masters y duplicados por criterio
    for idx, row in criterio_stats.iterrows():
        criterio = row['Criterio']
        criterio_df = filtered_df[filtered_df['criterio_agrupacion'] == criterio]
        masters = criterio_df['is_master'].sum()
        duplicados = len(criterio_df) - masters
        criterio_stats.loc[idx, 'Masters'] = int(masters)
        criterio_stats.loc[idx, 'Duplicados'] = int(duplicados)

    print(criterio_stats.to_string(index=False))
    print()

    print()
    print("=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print(f"\nPróximos pasos:")
    print(f"1. Revisar el script SQL generado")
    print(f"2. Ejecutar en un ambiente de prueba primero")
    print(f"3. Verificar los resultados con las queries de validación")
    print(f"4. Ejecutar en producción si todo es correcto")
    print()


if __name__ == "__main__":
    # Permitir pasar el nivel de confianza como argumento
    if len(sys.argv) > 1:
        nivel = sys.argv[1].upper()
        if nivel in ['ALTA', 'MEDIA', 'BAJA', 'TODAS']:
            main(nivel)
        else:
            print(f"Error: Nivel de confianza inválido '{sys.argv[1]}'")
            print("Niveles válidos: ALTA, MEDIA, BAJA, TODAS")
    else:
        main()
