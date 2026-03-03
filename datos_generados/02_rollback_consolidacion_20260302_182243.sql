-- ============================================================================
-- SCRIPT DE ROLLBACK - REVERTIR CONSOLIDACION
-- Generado: 2026-03-02 18:22:43
-- ============================================================================
-- USAR SOLO SI ES NECESARIO REVERTIR LA CONSOLIDACION
-- ============================================================================

-- Restaurar orders desde backup
TRUNCATE TABLE orders;
INSERT INTO orders SELECT * FROM orders_Backup_20260302;

-- Restaurar LogisticCode desde backup
TRUNCATE TABLE LogisticCode;
INSERT INTO LogisticCode SELECT * FROM LogisticCode_Backup_20260302;

-- Restaurar CustomerLocation desde backup
TRUNCATE TABLE CustomerLocation;
INSERT INTO CustomerLocation SELECT * FROM CustomerLocation_Backup_20260302;

-- Eliminar tabla de mapeo
DROP TABLE IF EXISTS ConsolidacionMapping;

-- Verificar restauracion
SELECT 'Locations activas restauradas' as Metrica, COUNT(*) as Cantidad
FROM CustomerLocation WHERE Deleted IS NULL OR Deleted = 0;

