"""
Script de Consolidación de Customer Locations
==============================================
Identifica grupos de customer locations que deberían consolidarse
basándose en dominios de email, códigos logísticos y proximidad geográfica.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Obtener la ruta del directorio del script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(PROJECT_DIR, "Csvs")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "datos_generados")

# Dominios genéricos a excluir del análisis por dominio corporativo
GENERIC_DOMAINS = {
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'live.com', 'icloud.com', 'protonmail.com', 'aol.com',
    'email.com', 'mail.com', 'zoho.com'
}

# Tolerancia de distancia en metros para considerar misma ubicación
GEO_DISTANCE_THRESHOLD_METERS = 50

# Umbral de similitud de TaxID (Levenshtein normalizado)
TAXID_SIMILARITY_THRESHOLD = 0.8


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def extract_domain(email: str) -> str:
    """Extrae el dominio de un email."""
    if pd.isna(email) or not isinstance(email, str):
        return None
    match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', email.lower())
    return match.group(1) if match else None


def is_corporate_domain(domain: str) -> bool:
    """Determina si un dominio es corporativo (no genérico)."""
    if not domain:
        return False
    return domain not in GENERIC_DOMAINS


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en metros entre dos puntos usando Haversine.
    """
    if any(pd.isna([lat1, lon1, lat2, lon2])):
        return float('inf')

    # Radio de la Tierra en metros
    R = 6371000

    # Convertir a radianes
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula Haversine
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Calcula similitud Levenshtein normalizada (0-1).
    1 = idénticos, 0 = completamente diferentes
    """
    if pd.isna(s1) or pd.isna(s2):
        return 0.0

    s1, s2 = str(s1), str(s2)

    if s1 == s2:
        return 1.0

    # Matriz de distancias
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )

    # Normalizar por la longitud máxima
    max_len = max(m, n)
    return 1 - (dp[m][n] / max_len) if max_len > 0 else 1.0


def normalize_taxid(taxid: str) -> str:
    """Normaliza un TaxID eliminando guiones y espacios."""
    if pd.isna(taxid):
        return ''
    return str(taxid).replace('-', '').replace(' ', '').strip()


# ============================================================================
# CARGA DE DATOS
# ============================================================================

def load_data() -> Dict[str, pd.DataFrame]:
    """Carga todos los CSVs necesarios."""
    print("=" * 80)
    print("CARGANDO DATOS")
    print("=" * 80)

    data = {}

    files = {
        'locations': 'CustomerLocation.csv',
        'users': 'EcommerceUsers.csv',
        'logistic_codes': 'LogisticCode.csv',
        'distributors': 'MarketplaceDistributors.csv',
        'orders': 'orders.csv',
        'sales_rep_locations': 'SalesRepCustomerLocations.csv'
    }

    for key, filename in files.items():
        path = os.path.join(CSV_PATH, filename)
        print(f"Cargando {filename}... ", end='')
        data[key] = pd.read_csv(path)
        print(f"OK - {len(data[key])} registros")

    print()
    return data


# ============================================================================
# PROCESAMIENTO DE DATOS
# ============================================================================

def prepare_locations_data(data: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepara el DataFrame principal de locations con toda la información necesaria.
    Retorna: (locations_df, users_df)
    """
    print("=" * 80)
    print("PREPARANDO DATOS DE LOCATIONS")
    print("=" * 80)

    locations = data['locations'].copy()
    users = data['users'].copy()

    # Extraer dominios de usuarios
    users['domain'] = users['Email'].apply(extract_domain)
    users['is_corporate'] = users['domain'].apply(is_corporate_domain)

    # Crear diccionario de usuario_id -> email/domain
    user_info = users[['ID', 'Email', 'domain', 'is_corporate']].set_index('ID').to_dict('index')

    # Agregar info de usuario creador a locations
    locations['creator_email'] = locations['EcommerceUserCreatorId'].map(
        lambda x: user_info.get(x, {}).get('Email') if pd.notna(x) else None
    )
    locations['creator_domain'] = locations['EcommerceUserCreatorId'].map(
        lambda x: user_info.get(x, {}).get('domain') if pd.notna(x) else None
    )
    locations['creator_is_corporate'] = locations['EcommerceUserCreatorId'].map(
        lambda x: user_info.get(x, {}).get('is_corporate') if pd.notna(x) else False
    )

    # Normalizar TaxID
    locations['TaxId_normalized'] = locations['TaxId'].apply(normalize_taxid)

    # Parsear coordenadas (eliminar símbolos de grados y direcciones)
    def parse_coordinate(coord_str):
        if pd.isna(coord_str):
            return None
        coord_str = str(coord_str).replace('°', '').replace(' S', '').replace(' W', '').replace(' N', '').replace(' E', '')
        try:
            return float(coord_str)
        except:
            return None

    locations['Latitude_clean'] = locations['Latitude'].apply(parse_coordinate)
    locations['Longitude_clean'] = locations['Longitude'].apply(parse_coordinate)

    # Marcar coordenadas válidas (no null, no cero)
    locations['has_valid_coords'] = (
        locations['Latitude_clean'].notna() &
        locations['Longitude_clean'].notna() &
        (locations['Latitude_clean'] != 0) &
        (locations['Longitude_clean'] != 0)
    )

    print(f"Locations totales: {len(locations)}")
    print(f"Locations con dominio corporativo: {locations['creator_is_corporate'].sum()}")
    print(f"Locations con coordenadas válidas: {locations['has_valid_coords'].sum()}")
    print(f"Locations con TaxID válido: {(locations['TaxId_normalized'].str.len() > 0).sum()}")
    print()

    return locations, users


def get_location_logistic_codes(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Obtiene todas las combinaciones de location + distribuidor + código logístico.
    """
    logistic_codes = data['logistic_codes'].copy()
    distributors = data['distributors'].copy()

    # Join con distributors para obtener nombre
    logistic_codes = logistic_codes.merge(
        distributors[['ID', 'Name', 'MarketplaceId']],
        left_on='MarketplaceDistributorId',
        right_on='ID',
        how='left',
        suffixes=('', '_dist')
    )

    # Filtrar solo códigos activos (no deleted)
    logistic_codes = logistic_codes[
        (logistic_codes['Deleted'] != True) |
        (logistic_codes['Deleted'].isna())
    ]

    return logistic_codes[['CustomerLocationId', 'MarketplaceDistributorId', 'Code', 'Name']]


def get_location_users_from_orders(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Obtiene qué usuarios han hecho pedidos en cada location.
    """
    orders = data['orders'].copy()

    # Filtrar pedidos válidos (no borradores, no borrados)
    orders = orders[
        (orders['State'] != 'BORRADOR') &
        ((orders['Deleted'] != True) | (orders['Deleted'].isna())) &
        (orders['ConfirmedByUserId'].notna()) &
        (orders['CustomerLocationId'].notna())
    ]

    # Agrupar por location y usuario
    location_users = orders.groupby(['CustomerLocationId', 'ConfirmedByUserId']).size().reset_index(name='order_count')

    return location_users


def get_order_counts_by_location(data: Dict[str, pd.DataFrame]) -> Dict[int, int]:
    """
    Obtiene el conteo total de pedidos por location.
    Retorna un diccionario {location_id: count}
    """
    orders = data['orders'].copy()

    # Filtrar pedidos válidos
    orders = orders[
        (orders['State'] != 'BORRADOR') &
        ((orders['Deleted'] != True) | (orders['Deleted'].isna())) &
        (orders['CustomerLocationId'].notna())
    ]

    # Contar pedidos por location
    order_counts = orders.groupby('CustomerLocationId').size().to_dict()

    return order_counts


# ============================================================================
# FASE 1: CONSOLIDACIÓN POR DOMINIOS CORPORATIVOS
# ============================================================================

def consolidate_by_corporate_domain(
    locations: pd.DataFrame,
    logistic_codes: pd.DataFrame,
    location_users: pd.DataFrame,
    users_data: pd.DataFrame
) -> pd.DataFrame:
    """
    FASE 1: Agrupa locations por dominio corporativo con validaciones.

    Criterios:
    - Mismo dominio corporativo (no genérico)
    - Comparten al menos 1 combinación droguería+código
    - Sin conflictos de TaxID
    """
    print("=" * 80)
    print("FASE 1: CONSOLIDACIÓN POR DOMINIOS CORPORATIVOS")
    print("=" * 80)

    # Filtrar locations con dominio corporativo
    corporate_locations = locations[locations['creator_is_corporate'] == True].copy()
    print(f"Locations con dominio corporativo: {len(corporate_locations)}")

    # Agregar usuarios que han hecho pedidos en cada location
    location_to_users = defaultdict(set)

    # Usuarios por creación
    for _, row in corporate_locations.iterrows():
        if pd.notna(row['EcommerceUserCreatorId']):
            location_to_users[row['ID']].add(row['EcommerceUserCreatorId'])

    # Usuarios por pedidos
    for _, row in location_users.iterrows():
        location_to_users[row['CustomerLocationId']].add(row['ConfirmedByUserId'])

    # Crear mapeo de usuario -> dominio
    user_to_domain = users_data.set_index('ID')['domain'].to_dict()

    # Crear mapeo de location -> códigos logísticos
    location_to_codes = defaultdict(set)
    for _, row in logistic_codes.iterrows():
        code_key = f"{row['MarketplaceDistributorId']}_{row['Code']}"
        location_to_codes[row['CustomerLocationId']].add(code_key)

    # Agrupar locations por dominio
    domain_groups = defaultdict(list)
    for _, row in corporate_locations.iterrows():
        domain = row['creator_domain']
        if domain:
            domain_groups[domain].append(row['ID'])

    print(f"Dominios corporativos únicos: {len(domain_groups)}")

    # Construir grupos de consolidación
    consolidation_groups = []
    group_id = 1

    for domain, location_ids in domain_groups.items():
        if len(location_ids) < 2:
            # Solo 1 location con este dominio, no hay nada que consolidar
            continue

        # Obtener TaxIDs del grupo
        taxids = corporate_locations[corporate_locations['ID'].isin(location_ids)]['TaxId_normalized'].dropna().unique()

        # VALIDACIÓN: Verificar conflictos de TaxID
        has_taxid_conflict = len(taxids) > 1 and not all(tid == '' for tid in taxids)

        # Verificar códigos logísticos compartidos
        codes_by_location = {loc_id: location_to_codes[loc_id] for loc_id in location_ids}
        shared_codes = set.intersection(*codes_by_location.values()) if codes_by_location.values() else set()

        # Obtener todos los usuarios del dominio que operan estas locations
        all_users = set()
        for loc_id in location_ids:
            all_users.update(location_to_users.get(loc_id, set()))

        # Obtener emails de todos los usuarios del grupo
        user_emails = []
        for user_id in all_users:
            user_data = users_data[users_data['ID'] == user_id]
            if not user_data.empty and pd.notna(user_data.iloc[0]['Email']):
                user_emails.append(user_data.iloc[0]['Email'])
        emails_str = '; '.join(sorted(set(user_emails)))

        # Contar pedidos por location (para elegir master)
        location_order_counts = location_users[
            location_users['CustomerLocationId'].isin(location_ids)
        ].groupby('CustomerLocationId')['order_count'].sum().to_dict()

        # Elegir location master (más pedidos)
        master_location_id = max(
            location_ids,
            key=lambda x: (
                location_order_counts.get(x, 0),
                corporate_locations[corporate_locations['ID'] == x]['CreatedDate'].iloc[0]
            )
        )

        # Determinar nivel de confianza
        if has_taxid_conflict:
            confidence = 'BAJA'
            requires_review = True
            alert = 'CONFLICTO_TAXID'
        elif len(shared_codes) > 0:
            confidence = 'ALTA'
            requires_review = False
            alert = None
        else:
            confidence = 'MEDIA'
            requires_review = True
            alert = 'SIN_CODIGOS_COMPARTIDOS'

        # Crear registro del grupo
        for loc_id in location_ids:
            consolidation_groups.append({
                'grupo_consolidacion_id': f"CORP_{group_id:04d}",
                'location_id': loc_id,
                'is_master': loc_id == master_location_id,
                'criterio_agrupacion': 'DOMINIO_CORPORATIVO',
                'dominio': domain,
                'emails': emails_str,
                'confianza': confidence,
                'requiere_revision': requires_review,
                'alerta': alert,
                'locations_en_grupo': len(location_ids),
                'usuarios_en_grupo': len(all_users),
                'codigos_compartidos': len(shared_codes),
                'taxids_unicos': len(taxids) if len(taxids) > 0 else 0,
                'pedidos_total': sum(location_order_counts.values())
            })

        group_id += 1

    result_df = pd.DataFrame(consolidation_groups)

    if len(result_df) > 0:
        print(f"\nGrupos identificados: {result_df['grupo_consolidacion_id'].nunique()}")
        print(f"Locations en grupos: {len(result_df)}")
        print(f"Locations master: {result_df['is_master'].sum()}")
        print(f"\nDistribución por confianza:")
        print(result_df['confianza'].value_counts())
        print(f"\nGrupos que requieren revisión: {result_df[result_df['requiere_revision']]['grupo_consolidacion_id'].nunique()}")
    else:
        print("\nNo se identificaron grupos para consolidación.")

    print()
    return result_df


# ============================================================================
# FASE 2: CONSOLIDACIÓN POR PROXIMIDAD GEOGRÁFICA + TAXID
# ============================================================================

def consolidate_by_geo_proximity(
    locations: pd.DataFrame,
    phase1_location_ids: Set[int],
    order_counts: Dict[int, int],
    distance_threshold: float = GEO_DISTANCE_THRESHOLD_METERS
) -> pd.DataFrame:
    """
    FASE 2: Agrupa locations por proximidad geográfica y TaxID similar.
    Usa una estrategia de grid para optimizar el rendimiento.

    Criterios:
    - Distancia < threshold (default 50m)
    - TaxID idéntico O similitud > 0.8
    - No incluidas en FASE 1
    - Coordenadas válidas
    """
    print("=" * 80)
    print("FASE 2: CONSOLIDACION POR PROXIMIDAD GEOGRAFICA + TAXID")
    print("=" * 80)

    # Filtrar locations no procesadas en FASE 1 con coordenadas válidas
    available_locations = locations[
        (~locations['ID'].isin(phase1_location_ids)) &
        (locations['has_valid_coords'] == True) &
        (locations['TaxId_normalized'].str.len() > 0)
    ].copy()

    print(f"Locations disponibles para FASE 2: {len(available_locations)}")

    if len(available_locations) == 0:
        print("No hay locations disponibles para FASE 2.")
        return pd.DataFrame()

    # Estrategia de grid: Dividir el espacio en celdas de ~100m
    # 0.001 grados ~= 111 metros en latitud
    cell_size = 0.001

    available_locations['grid_lat'] = (available_locations['Latitude_clean'] / cell_size).astype(int)
    available_locations['grid_lon'] = (available_locations['Longitude_clean'] / cell_size).astype(int)

    # Agrupar por celda
    grid = defaultdict(list)
    for _, row in available_locations.iterrows():
        grid[(row['grid_lat'], row['grid_lon'])].append(row.to_dict())

    print(f"Celdas de grid creadas: {len(grid)}")

    # Crear grupos por proximidad
    consolidation_groups = []
    group_id = 1
    processed = set()

    for (grid_lat, grid_lon), locations_in_cell in grid.items():
        # Obtener locations de celdas adyacentes (vecindad de 9 celdas)
        nearby_locations = []
        for dlat in [-1, 0, 1]:
            for dlon in [-1, 0, 1]:
                cell_key = (grid_lat + dlat, grid_lon + dlon)
                nearby_locations.extend(grid.get(cell_key, []))

        # Procesar locations en esta celda
        for i, loc1 in enumerate(nearby_locations):
            if loc1['ID'] in processed:
                continue

            # Iniciar un nuevo grupo con esta location
            group = [loc1]
            processed.add(loc1['ID'])

            # Buscar locations cercanas en la vecindad
            for j, loc2 in enumerate(nearby_locations):
                if i >= j or loc2['ID'] in processed:
                    continue

                # Calcular distancia
                distance = haversine_distance(
                    loc1['Latitude_clean'], loc1['Longitude_clean'],
                    loc2['Latitude_clean'], loc2['Longitude_clean']
                )

                if distance > distance_threshold:
                    continue

                # Verificar TaxID
                taxid_match = loc1['TaxId_normalized'] == loc2['TaxId_normalized']
                taxid_similarity = levenshtein_similarity(
                    loc1['TaxId_normalized'],
                    loc2['TaxId_normalized']
                )

                if taxid_match or taxid_similarity >= TAXID_SIMILARITY_THRESHOLD:
                    group.append(loc2)
                    processed.add(loc2['ID'])

        # Solo crear grupo si hay 2+ locations
        if len(group) >= 2:
            # Calcular métricas del grupo
            taxids_in_group = set(loc['TaxId_normalized'] for loc in group)
            has_exact_taxid_match = len(taxids_in_group) == 1

            # Elegir location master por orden de prioridad:
            # 1. Más pedidos
            # 2. Fecha más antigua (si empate en pedidos)
            # 3. ID más bajo (si empate en todo)
            master_loc = max(group, key=lambda x: (
                order_counts.get(x['ID'], 0),  # Prioridad 1: más pedidos
                -pd.to_datetime(x['CreatedDate']).timestamp(),  # Prioridad 2: más antigua (negativo para invertir)
                -x['ID']  # Prioridad 3: ID más bajo
            ))

            # Determinar confianza
            if has_exact_taxid_match:
                confidence = 'ALTA'
                requires_review = False
                alert = None
            else:
                confidence = 'MEDIA'
                requires_review = True
                alert = 'TAXID_SIMILAR_NO_IDENTICO'

            # Obtener emails de creadores del grupo
            creator_emails = [loc.get('creator_email', '') for loc in group if loc.get('creator_email')]
            emails_str = '; '.join(sorted(set(filter(None, creator_emails))))

            # Crear registros del grupo
            for loc in group:
                consolidation_groups.append({
                    'grupo_consolidacion_id': f"GEO_{group_id:04d}",
                    'location_id': loc['ID'],
                    'is_master': loc['ID'] == master_loc['ID'],
                    'criterio_agrupacion': 'GEO_PROXIMIDAD_TAXID',
                    'dominio': loc.get('creator_domain', ''),
                    'emails': emails_str,
                    'confianza': confidence,
                    'requiere_revision': requires_review,
                    'alerta': alert,
                    'locations_en_grupo': len(group),
                    'taxids_unicos': len(taxids_in_group),
                    'distancia_max_metros': max(
                        haversine_distance(
                            master_loc['Latitude_clean'], master_loc['Longitude_clean'],
                            loc['Latitude_clean'], loc['Longitude_clean']
                        ) for loc in group
                    )
                })

            group_id += 1

    result_df = pd.DataFrame(consolidation_groups)

    if len(result_df) > 0:
        print(f"\nGrupos identificados: {result_df['grupo_consolidacion_id'].nunique()}")
        print(f"Locations en grupos: {len(result_df)}")
        print(f"Locations master: {result_df['is_master'].sum()}")
        print(f"\nDistribucion por confianza:")
        print(result_df['confianza'].value_counts())
        print(f"\nGrupos que requieren revision: {result_df[result_df['requiere_revision']]['grupo_consolidacion_id'].nunique()}")
    else:
        print("\nNo se identificaron grupos para consolidacion.")

    print()
    return result_df


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    print(f"\n{'='*80}")
    print(f"SCRIPT DE CONSOLIDACIÓN DE CUSTOMER LOCATIONS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Cargar datos
    data = load_data()

    # Preparar datos
    locations, users = prepare_locations_data(data)
    logistic_codes = get_location_logistic_codes(data)
    location_users = get_location_users_from_orders(data)
    order_counts = get_order_counts_by_location(data)

    print("=" * 80)
    print("DATOS PREPARADOS EXITOSAMENTE")
    print("=" * 80)
    print(f"Locations procesadas: {len(locations)}")
    print(f"Codigos logisticos activos: {len(logistic_codes)}")
    print(f"Combinaciones location-usuario: {len(location_users)}")
    print(f"Locations con pedidos: {len(order_counts)}")
    print()

    # FASE 1: Consolidación por dominios corporativos
    phase1_results = consolidate_by_corporate_domain(
        locations=locations,
        logistic_codes=logistic_codes,
        location_users=location_users,
        users_data=users
    )

    # Guardar resultados de FASE 1
    if len(phase1_results) > 0:
        output_file = os.path.join(OUTPUT_PATH, "fase1_consolidacion_dominios_corporativos.csv")
        phase1_results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Resultados de FASE 1 guardados en: {output_file}")
    else:
        print("No hay resultados de FASE 1 para guardar.")

    print()

    # FASE 2: Consolidación por geo-proximidad + TaxID
    phase1_location_ids = set(phase1_results['location_id'].unique()) if len(phase1_results) > 0 else set()

    phase2_results = consolidate_by_geo_proximity(
        locations=locations,
        phase1_location_ids=phase1_location_ids,
        order_counts=order_counts,
        distance_threshold=GEO_DISTANCE_THRESHOLD_METERS
    )

    # Guardar resultados de FASE 2
    if len(phase2_results) > 0:
        output_file = os.path.join(OUTPUT_PATH, "fase2_consolidacion_geo_proximidad.csv")
        phase2_results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Resultados de FASE 2 guardados en: {output_file}")
    else:
        print("No hay resultados de FASE 2 para guardar.")

    print()

    # Consolidar ambas fases
    all_results = pd.concat([phase1_results, phase2_results], ignore_index=True)

    if len(all_results) > 0:
        output_file = os.path.join(OUTPUT_PATH, "consolidacion_completa.csv")
        all_results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Consolidacion completa guardada en: {output_file}")

        # Generar resumen
        print()
        print("=" * 80)
        print("RESUMEN DE CONSOLIDACION")
        print("=" * 80)
        print(f"Total de grupos: {all_results['grupo_consolidacion_id'].nunique()}")
        print(f"Total de locations en grupos: {len(all_results)}")
        print(f"Locations master: {all_results['is_master'].sum()}")
        print(f"\nDistribucion por fase:")
        print(all_results['criterio_agrupacion'].value_counts())
        print(f"\nDistribucion por confianza:")
        print(all_results['confianza'].value_counts())
        print(f"\nGrupos que requieren revision: {all_results[all_results['requiere_revision']]['grupo_consolidacion_id'].nunique()}")

    print()
    print("=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    main()
