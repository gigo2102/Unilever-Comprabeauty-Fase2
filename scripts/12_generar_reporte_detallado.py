"""
Generador de Reporte Detallado de Consolidación
================================================
Enriquece los resultados de consolidación con información detallada
de cada location para facilitar la revisión manual.
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CSV_PATH = "../Csvs"
INPUT_PATH = "../datos_generados"
OUTPUT_PATH = "../datos_generados"

# ============================================================================
# CARGA DE DATOS
# ============================================================================

print("=" * 80)
print("GENERANDO REPORTE DETALLADO DE CONSOLIDACION")
print("=" * 80)
print()

print("Cargando datos...")

# Cargar consolidación completa
consolidacion = pd.read_csv(f"{INPUT_PATH}/consolidacion_completa.csv")
print(f"  Consolidacion completa: {len(consolidacion)} registros")

# Cargar datos originales
locations = pd.read_csv(f"{CSV_PATH}/CustomerLocation.csv")
print(f"  Customer Locations: {len(locations)} registros")

users = pd.read_csv(f"{CSV_PATH}/EcommerceUsers.csv")
print(f"  Ecommerce Users: {len(users)} registros")

logistic_codes = pd.read_csv(f"{CSV_PATH}/LogisticCode.csv")
print(f"  Logistic Codes: {len(logistic_codes)} registros")

distributors = pd.read_csv(f"{CSV_PATH}/MarketplaceDistributors.csv")
print(f"  Distributors: {len(distributors)} registros")

orders = pd.read_csv(f"{CSV_PATH}/orders.csv")
print(f"  Orders: {len(orders)} registros")

print()

# ============================================================================
# ENRIQUECER DATOS
# ============================================================================

print("Enriqueciendo datos de consolidacion...")

# Agregar info de locations
consolidacion = consolidacion.merge(
    locations[['ID', 'MarketplaceId', 'FantasyName', 'FullAddress',
               'Latitude', 'Longitude', 'TaxId', 'ApprovalStatus',
               'CreatedDate', 'EcommerceUserCreatorId']],
    left_on='location_id',
    right_on='ID',
    how='left'
)

# Agregar info de usuario creador
user_info = users[['ID', 'FullName', 'Email']].rename(columns={
    'ID': 'UserId',
    'FullName': 'CreatorName',
    'Email': 'CreatorEmail'
})

consolidacion = consolidacion.merge(
    user_info,
    left_on='EcommerceUserCreatorId',
    right_on='UserId',
    how='left'
)

# Contar pedidos por location
orders_filtered = orders[
    (orders['State'] != 'BORRADOR') &
    ((orders['Deleted'] != True) | (orders['Deleted'].isna()))
]

order_counts = orders_filtered.groupby('CustomerLocationId').size().reset_index(name='order_count')
consolidacion = consolidacion.merge(
    order_counts,
    left_on='location_id',
    right_on='CustomerLocationId',
    how='left'
)
consolidacion['order_count'] = consolidacion['order_count'].fillna(0).astype(int)

# Contar códigos logísticos por location
logistic_filtered = logistic_codes[
    (logistic_codes['Deleted'] != True) | (logistic_codes['Deleted'].isna())
]

code_counts = logistic_filtered.groupby('CustomerLocationId').agg({
    'Code': 'count',
    'MarketplaceDistributorId': lambda x: x.nunique()
}).reset_index()
code_counts.columns = ['CustomerLocationId', 'logistic_code_count', 'distributor_count']

consolidacion = consolidacion.merge(
    code_counts,
    left_on='location_id',
    right_on='CustomerLocationId',
    how='left'
)
consolidacion['logistic_code_count'] = consolidacion['logistic_code_count'].fillna(0).astype(int)
consolidacion['distributor_count'] = consolidacion['distributor_count'].fillna(0).astype(int)

print(f"  Datos enriquecidos: {len(consolidacion)} registros")
print()

# ============================================================================
# GENERAR REPORTES
# ============================================================================

# Seleccionar columnas para el reporte
report_columns = [
    'grupo_consolidacion_id',
    'location_id',
    'is_master',
    'criterio_agrupacion',
    'confianza',
    'requiere_revision',
    'alerta',
    'locations_en_grupo',
    'FantasyName',
    'FullAddress',
    'TaxId',
    'Latitude',
    'Longitude',
    'CreatorName',
    'CreatorEmail',
    'dominio',
    'order_count',
    'logistic_code_count',
    'distributor_count',
    'ApprovalStatus',
    'CreatedDate'
]

# Reporte completo
output_file = f"{OUTPUT_PATH}/reporte_consolidacion_detallado.csv"
consolidacion[report_columns].to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"Reporte completo guardado en: {output_file}")

# Reporte de grupos que requieren revisión
review_groups = consolidacion[consolidacion['requiere_revision'] == True]
output_file = f"{OUTPUT_PATH}/reporte_grupos_revision.csv"
review_groups[report_columns].to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"Grupos para revision guardados en: {output_file}")

# Reporte de grupos de ALTA confianza (listos para consolidar)
high_confidence = consolidacion[consolidacion['confianza'] == 'ALTA']
output_file = f"{OUTPUT_PATH}/reporte_grupos_alta_confianza.csv"
high_confidence[report_columns].to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"Grupos de ALTA confianza guardados en: {output_file}")

# Estadísticas por grupo
print()
print("=" * 80)
print("GENERANDO ESTADISTICAS POR GRUPO")
print("=" * 80)
print()

group_stats = consolidacion.groupby('grupo_consolidacion_id').agg({
    'location_id': 'count',
    'is_master': 'sum',
    'criterio_agrupacion': 'first',
    'confianza': 'first',
    'requiere_revision': 'first',
    'TaxId': lambda x: x.nunique(),
    'dominio': lambda x: x.nunique(),
    'order_count': 'sum',
    'logistic_code_count': 'sum',
    'distributor_count': 'max'
}).reset_index()

group_stats.columns = [
    'grupo_consolidacion_id',
    'locations_count',
    'masters_count',
    'criterio_agrupacion',
    'confianza',
    'requiere_revision',
    'taxids_unicos',
    'dominios_unicos',
    'orders_total',
    'codigos_logisticos_total',
    'distribuidores_max'
]

output_file = f"{OUTPUT_PATH}/estadisticas_por_grupo.csv"
group_stats.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"Estadisticas por grupo guardadas en: {output_file}")

# Top 20 grupos más grandes
print()
print("TOP 20 GRUPOS MAS GRANDES:")
print("-" * 80)
top_groups = group_stats.nlargest(20, 'locations_count')[
    ['grupo_consolidacion_id', 'locations_count', 'criterio_agrupacion',
     'confianza', 'orders_total', 'taxids_unicos']
]
print(top_groups.to_string(index=False))

print()
print("=" * 80)
print("PROCESO COMPLETADO")
print("=" * 80)
