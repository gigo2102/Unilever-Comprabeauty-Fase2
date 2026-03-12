-- ============================================================================
-- SCRIPT DE VALIDACION PREVIA A LA CONSOLIDACION
-- Generado: 2026-03-02 18:27:54
-- ============================================================================
-- IMPORTANTE: Ejecutar este script ANTES del script de consolidacion
-- para verificar el estado de la base de datos y detectar posibles problemas.
-- ============================================================================

SET @masters_count = 4747;
SET @duplicados_count = 5868;

-- ============================================================================
-- 1. ESTADO ACTUAL DE LA BASE DE DATOS
-- ============================================================================

SELECT '=== ESTADO ACTUAL ===' as Seccion;

-- Total de locations activas
SELECT 
    'Locations activas (no deleted)' as Metrica,
    COUNT(*) as Cantidad,
    'Baseline antes de consolidacion' as Nota
FROM CustomerLocation
WHERE Deleted IS NULL OR Deleted = 0;

-- Total de pedidos activos
SELECT 
    'Pedidos activos' as Metrica,
    COUNT(*) as Cantidad,
    'Se van a redistribuir a masters' as Nota
FROM orders
WHERE Deleted IS NULL OR Deleted = 0;

-- Total de codigos logisticos activos
SELECT 
    'Codigos logisticos activos' as Metrica,
    COUNT(*) as Cantidad,
    'Se van a mover o marcar deleted' as Nota
FROM LogisticCode
WHERE Deleted IS NULL OR Deleted = 0;

-- ============================================================================
-- 2. VERIFICACION DE LOCATIONS A CONSOLIDAR
-- ============================================================================

SELECT '=== VERIFICACION DE LOCATIONS ===' as Seccion;

-- Verificar que los masters existen y no estan deleted
SELECT 
    'Masters que existen y estan activos' as Metrica,
    COUNT(*) as Cantidad,
    CONCAT('Esperado: ', @masters_count) as Esperado
FROM CustomerLocation
WHERE ID IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
  AND (Deleted IS NULL OR Deleted = 0);

-- Verificar masters que NO existen o estan deleted (PROBLEMA)
SELECT 
    'Masters con problemas (deleted o no existen)' as Metrica,
    COUNT(*) as Cantidad,
    'Esperado: 0 - Si > 0 revisar antes de consolidar' as Esperado
FROM (
    SELECT 5157 as ID
    UNION ALL SELECT 440
    UNION ALL SELECT 4299
    UNION ALL SELECT 1656
    UNION ALL SELECT 5190
    UNION ALL SELECT 3237
    UNION ALL SELECT 2162
    UNION ALL SELECT 2776
    UNION ALL SELECT 3831
    UNION ALL SELECT 4826
    UNION ALL SELECT 1860
    UNION ALL SELECT 16
    UNION ALL SELECT 2267
    UNION ALL SELECT 4601
    UNION ALL SELECT 1065
    UNION ALL SELECT 2352
    UNION ALL SELECT 2585
    UNION ALL SELECT 2540
    UNION ALL SELECT 2769
    UNION ALL SELECT 2662
) masters
LEFT JOIN CustomerLocation cl ON masters.ID = cl.ID AND (cl.Deleted IS NULL OR cl.Deleted = 0)
WHERE cl.ID IS NULL;

-- Verificar duplicados que existen y estan activos
SELECT 
    'Duplicados que existen y estan activos' as Metrica,
    COUNT(*) as Cantidad,
    CONCAT('Esperado: ', @duplicados_count) as Esperado
FROM CustomerLocation
WHERE ID IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
  AND (Deleted IS NULL OR Deleted = 0);

-- ============================================================================
-- 3. ANALISIS DE PEDIDOS
-- ============================================================================

SELECT '=== ANALISIS DE PEDIDOS ===' as Seccion;

-- Pedidos en locations master
SELECT 
    'Pedidos en masters' as Metrica,
    COUNT(*) as Cantidad,
    'Estos se mantienen en el master' as Nota
FROM orders
WHERE CustomerLocationId IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
  AND (Deleted IS NULL OR Deleted = 0);

-- Pedidos en locations duplicadas (se van a mover)
SELECT 
    'Pedidos en duplicados' as Metrica,
    COUNT(*) as Cantidad,
    'Se van a mover al master correspondiente' as Nota
FROM orders
WHERE CustomerLocationId IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
  AND (Deleted IS NULL OR Deleted = 0);

-- Verificar pedidos huerfanos (sin CustomerLocation)
SELECT 
    'Pedidos huerfanos (sin location)' as Metrica,
    COUNT(*) as Cantidad,
    'Esperado: 0 - Si > 0 hay un problema de integridad' as Nota
FROM orders o
LEFT JOIN CustomerLocation cl ON o.CustomerLocationId = cl.ID
WHERE cl.ID IS NULL
  AND (o.Deleted IS NULL OR o.Deleted = 0);

-- ============================================================================
-- 4. ANALISIS DE CODIGOS LOGISTICOS
-- ============================================================================

SELECT '=== ANALISIS DE CODIGOS LOGISTICOS ===' as Seccion;

-- Codigos en masters
SELECT 
    'Codigos logisticos en masters' as Metrica,
    COUNT(*) as Cantidad,
    'Base actual de codigos en masters' as Nota
FROM LogisticCode
WHERE CustomerLocationId IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
  AND (Deleted IS NULL OR Deleted = 0);

-- Codigos en duplicados
SELECT 
    'Codigos logisticos en duplicados' as Metrica,
    COUNT(*) as Cantidad,
    'Se intentaran mover al master (o marcar deleted si duplicados)' as Nota
FROM LogisticCode
WHERE CustomerLocationId IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
  AND (Deleted IS NULL OR Deleted = 0);

-- Detectar conflictos potenciales de codigos
-- (mismo distributor + code en master y duplicado)
SELECT 
    'Codigos duplicados que generaran conflictos' as Metrica,
    COUNT(*) as Cantidad,
    'Estos se marcaran como deleted automaticamente' as Nota
FROM LogisticCode lc_dup
WHERE lc_dup.CustomerLocationId IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
  AND (lc_dup.Deleted IS NULL OR lc_dup.Deleted = 0)
  AND EXISTS (
    SELECT 1 FROM LogisticCode lc_master
    WHERE lc_master.CustomerLocationId IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
      AND lc_master.MarketplaceDistributorId = lc_dup.MarketplaceDistributorId
      AND lc_master.Code = lc_dup.Code
      AND (lc_master.Deleted IS NULL OR lc_master.Deleted = 0)
  );

-- ============================================================================
-- 5. VERIFICACION DE INTEGRIDAD REFERENCIAL
-- ============================================================================

SELECT '=== INTEGRIDAD REFERENCIAL ===' as Seccion;

-- Verificar que no hay referencias circulares o problemas
SELECT 
    'Locations que son master Y duplicado' as Problema,
    COUNT(*) as Cantidad,
    'Esperado: 0 - CRITICO si > 0' as Nota
FROM (
    SELECT ID FROM CustomerLocation WHERE ID IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
    INTERSECT
    SELECT ID FROM CustomerLocation WHERE ID IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
) conflictos;

-- ============================================================================
-- 6. ANALISIS DE IMPACTO
-- ============================================================================

SELECT '=== IMPACTO DE LA CONSOLIDACION ===' as Seccion;

-- Resumen de impacto
SELECT 
    'Locations activas ANTES' as Metrica,
    COUNT(*) as Cantidad
FROM CustomerLocation
WHERE Deleted IS NULL OR Deleted = 0
UNION ALL
SELECT 
    'Locations que se marcaran deleted',
    @duplicados_count
UNION ALL
SELECT 
    'Locations activas DESPUES (estimado)',
    COUNT(*) - @duplicados_count
FROM CustomerLocation
WHERE Deleted IS NULL OR Deleted = 0
UNION ALL
SELECT 
    'Reduccion en locations',
    @duplicados_count
UNION ALL
SELECT 
    'Porcentaje de reduccion',
    ROUND((@duplicados_count * 100.0 / COUNT(*)), 2)
FROM CustomerLocation
WHERE Deleted IS NULL OR Deleted = 0;

-- ============================================================================
-- 7. VERIFICACION DE TABLAS DE BACKUP
-- ============================================================================

SELECT '=== VERIFICACION DE ESPACIO Y BACKUPS ===' as Seccion;

-- Verificar que no existan backups previos (evitar conflictos)
SELECT 
    'Tabla' as Tabla,
    CASE 
        WHEN COUNT(*) > 0 THEN 'YA EXISTE - Renombrar o eliminar antes de ejecutar'
        ELSE 'OK - No existe'
    END as Estado
FROM information_schema.tables
WHERE table_name = 'CustomerLocation_Backup_20260302'
UNION ALL
SELECT 
    'orders_Backup',
    CASE 
        WHEN COUNT(*) > 0 THEN 'YA EXISTE - Renombrar o eliminar antes de ejecutar'
        ELSE 'OK - No existe'
    END
FROM information_schema.tables
WHERE table_name = 'orders_Backup_20260302'
UNION ALL
SELECT 
    'LogisticCode_Backup',
    CASE 
        WHEN COUNT(*) > 0 THEN 'YA EXISTE - Renombrar o eliminar antes de ejecutar'
        ELSE 'OK - No existe'
    END
FROM information_schema.tables
WHERE table_name = 'LogisticCode_Backup_20260302';

-- ============================================================================
-- 8. CHECKLIST FINAL
-- ============================================================================

SELECT '=== CHECKLIST FINAL ===' as Seccion;

SELECT 
    'Checklist Item' as Item,
    'Estado' as Estado,
    'Accion Requerida' as Accion
UNION ALL
SELECT 
    '1. Todos los masters existen y estan activos',
    CASE 
        WHEN COUNT(*) = @masters_count THEN 'OK'
        ELSE 'ERROR'
    END,
    CASE 
        WHEN COUNT(*) = @masters_count THEN 'Ninguna'
        ELSE 'Verificar masters faltantes o deleted'
    END
FROM CustomerLocation
WHERE ID IN (5157,440,4299,1656,5190,3237,2162,2776,3831,4826,1860,16,2267,4601,1065,2352,2585,2540,2769,2662,2777,3810,2684,3615,3213,1944,5214,776,2305,2607,4044,4010,1909,1955,2737,1858,3931,2841,2917,4063,3770,3429,5053,2438,2651,2228,1926,2181,2749,3150,3589,2947,3587,1949,3021,2445,2445,3706,3252,3999,1963,3181,2276,3114,3019,3284,3163,2676,2621,5025,3302,3487,3404,122,2220,3813,3599,3308,3573,3289,3187,3329,2583,2134,3917,5171,3744,2611,2611,3898,3971,3875,1129,3186,2224,5185,81714,1969,2252,1363)
  AND (Deleted IS NULL OR Deleted = 0)
UNION ALL
SELECT 
    '2. Todos los duplicados existen y estan activos',
    CASE 
        WHEN COUNT(*) = @duplicados_count THEN 'OK'
        ELSE 'REVISAR'
    END,
    CASE 
        WHEN COUNT(*) = @duplicados_count THEN 'Ninguna'
        ELSE 'Algunos duplicados ya fueron deleted - revisar'
    END
FROM CustomerLocation
WHERE ID IN (10023,5274,102041,9422,6570,103285,10302,8464,6768,7907,8850,9909,6792,80,7448,9611,6181,102647,7342,7534,7745,7895,7528,7902,8831,7951,8602,8448,6875,10059,5967,102319,7338,7554,9174,9176,6873,7010,7876,6796,8761,7816,8239,9156,8945,8728,10163,7681,7561,7407,7211,7020,7984,8047,8570,7776,8588,7016,8216,7696,7696,8540,8442,9012,7126,8031,7459,8493,8200,8351,8056,7941,7578,10176,8483,8746,8338,70,93,7397,8848,8596,8387,8564,8350,8416,8489,7869,2922,7936,7387,8798,10047,8954,7552,7552,8764,9228,9000,6097)
  AND (Deleted IS NULL OR Deleted = 0)
UNION ALL
SELECT 
    '3. No hay pedidos huerfanos',
    CASE 
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    CASE 
        WHEN COUNT(*) = 0 THEN 'Ninguna'
        ELSE 'Corregir integridad referencial antes de continuar'
    END
FROM orders o
LEFT JOIN CustomerLocation cl ON o.CustomerLocationId = cl.ID
WHERE cl.ID IS NULL
  AND (o.Deleted IS NULL OR o.Deleted = 0)
UNION ALL
SELECT 
    '4. Tablas de backup no existen',
    CASE 
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ADVERTENCIA'
    END,
    CASE 
        WHEN COUNT(*) = 0 THEN 'Ninguna'
        ELSE 'Renombrar o eliminar backups existentes'
    END
FROM information_schema.tables
WHERE table_name IN ('CustomerLocation_Backup_20260302', 'orders_Backup_20260302', 'LogisticCode_Backup_20260302');

-- ============================================================================
-- FIN DEL SCRIPT DE VALIDACION
-- ============================================================================
--
-- IMPORTANTE: Revisar todos los resultados antes de ejecutar el script
-- de consolidacion. Si hay errores o advertencias, corregirlos primero.
--
-- Si todos los checks muestran 'OK', es seguro proceder con:
-- 01_consolidar_alta_confianza_YYYYMMDD_HHMMSS.sql
-- ============================================================================
