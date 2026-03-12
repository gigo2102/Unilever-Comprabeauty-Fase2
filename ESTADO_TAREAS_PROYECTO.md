# Estado de Tareas - Proyecto Unilever CompraBeauty Fase 2

**Fecha de revisión:** 12 de Marzo 2026
**Proyecto:** Consolidación Customer Locations - Migración Elvis a Tracy

---

## 📋 Resumen Ejecutivo

| Tarea | Estado | Completitud |
|-------|--------|-------------|
| 1. Importación datos históricos pedidos (pre-2025) | 🟡 DOING | 60% |
| 2. Consolidación cuentas grupales | 🟢 DONE | 95% |
| 3. Unificación PDVs repetidos (Aylen Arcodia) | 🔴 TO DO | 0% |

---

## 📊 TAREA 1: Importar Datos Históricos de Pedidos (Pre-2025)

**Descripción:** Importar los datos históricos de pedidos faltantes, es decir previos al 1ro de enero de 2025. Estos datos son necesarios porque de este modo terminaremos de contar con los códigos de operaciones logísticas de los PDVs previamente importados.

**Esfuerzo estimado:** ~30hs

### Estado: 🟡 DOING (60% completado)

### Detalle de Avance:

| Subtarea | Script | Estado | Notas |
|----------|--------|--------|-------|
| Extracción pedidos Elvis | `02_extraer_pedidos_elvis_por_trimestre.py` | ✅ DONE | Pedidos fragmentados Q2 2020 - Q2 2025 en `/historicos/Historico_Elvis_fragmented_by_Q/` |
| Generación mapeo droguerías | `03_generar_mapeo_droguerias.py` | ✅ DONE | Archivo generado: `08_mapeo_droguerias_elvis_tracy.xlsx` |
| Análisis compatibilidad campos | `04_analizar_compatibilidad_campos.py` | ✅ DONE | Reporte generado: `09_documentacion_mapeo_campos.xlsx` |
| Transformación Elvis → Tracy | `05_transformar_elvis_a_tracy.py` | ⚠️ PARCIAL | Existe el script pero no hay evidencia de archivos Tracy generados para todos los trimestres pre-2025 |
| Importación a BD Tracy | - | 🔴 TO DO | Pendiente cargar pedidos transformados a base de datos |
| Validación códigos logísticos | - | 🔴 TO DO | Pendiente verificar que los códigos logísticos se hayan importado correctamente |

### Archivos Disponibles:

**Pedidos Elvis (fragmentados por trimestre):**
```
historicos/Historico_Elvis_fragmented_by_Q/
├── pedidos.elvis.2020.Q2.csv
├── pedidos.elvis.2020.Q3.csv
├── pedidos.elvis.2020.Q4.csv
├── pedidos.elvis.2021.Q1.csv → 2021.Q4.csv
├── pedidos.elvis.2022.Q1.csv → 2022.Q4.csv
├── pedidos.elvis.2023.Q1.csv → 2023.Q4.csv
├── pedidos.elvis.2024.Q1.csv → 2024.Q4.csv (CRÍTICO: Pre-2025)
└── pedidos.elvis.2025.Q1.csv, 2025.Q2.csv
```

**Pedidos Históricos Unilever:**
```
historicos/HistoricoPedidosUnileverFito/
├── pedidos2020_1.xlsx
├── pedidos2021_1.xlsx, pedidos2021_2.xlsx
├── pedidos2022_1.xlsx, pedidos2022_2.xlsx
├── pedidos2023_1.xlsx, pedidos2023_2.xlsx
├── pedidos2024_1.xlsx, pedidos2024_2.xlsx (CRÍTICO)
└── pedidos2025__1.xlsx, pedidos2025__2.xlsx, pedidos2025__3.xlsx
```

### Próximos Pasos:

1. ✅ **Ejecutar transformación completa:** Correr `05_transformar_elvis_a_tracy.py` para todos los trimestres pre-2025 (2020 Q2 - 2024 Q4)
2. ⏸️ **Validar archivos Tracy generados:** Verificar que los CSVs en formato Tracy se hayan creado correctamente
3. ⏸️ **Importar a BD:** Cargar los pedidos transformados a la base de datos Tracy
4. ⏸️ **Validar códigos logísticos:** Verificar que los customer locations ahora tengan sus códigos logísticos asociados

---

## 📊 TAREA 2: Consolidación de Cuentas Grupales

**Descripción:** Consolidación de cuentas grupales mediante:
1. Unificar en una cuenta grupal todos los Usuarios cuyo dominio de mail sea no genérico (no gmail, hotmail, etc), y sí sea de una marca o cadena (ejemplo puntodesalud.com.ar).
2. Además teniendo en cuenta los grupos definidos en punto 1, unificar en 2da instancia por CUIT, para sumar más miembros a dichos grupos o generar nuevos grupos.
3. Enviar a Unilever la lista de grupos borrador conseguidos con estos 2 pasos, para que confirme si proceder a Unificar como grupos. Esto está contemplado en ser realizado en 3 o 4 iteraciones, para primero probar con un número reducido de casos.

**Esfuerzo estimado:** ~140hs

### Estado: 🟢 DONE (95% completado)

### Detalle de Avance:

| Subtarea | Script | Estado | Notas |
|----------|--------|--------|-------|
| Consolidación por dominios corporativos | `06_consolidacion_customer_locations.py` | ✅ DONE | 424 grupos, 3,446 locations identificados |
| Consolidación por CUIT/Tax ID | `06_consolidacion_customer_locations.py` | ✅ DONE | Integrado en mismo script, usa similitud Levenshtein > 0.8 |
| Consolidación por geo-proximidad | `06_consolidacion_customer_locations.py` | ✅ DONE | 4,749 grupos, 10,620 locations (< 50 metros) |
| Reporte detallado dominios | `07_generar_reporte_dominios_detallado.py` | ✅ DONE | Archivo: `12_fase1_consolidacion_dominios_corporativos.csv` |
| Reporte detallado geo | `08_generar_reporte_geo_detallado.py` | ✅ DONE | Archivo: `13_fase2_consolidacion_geo_proximidad.csv` |
| Análisis ERPs | `09_analisis_erps_con_arrays.py` + `10_analisis_erps_corregido.py` | ✅ DONE | Archivos: `16_analisis_erps_completo_corregido.xlsx` |
| Comparación ERPs actuales vs propuestos | `11_generar_comparacion_erps_actuales.py` | ✅ DONE | Generado en análisis |
| Reporte consolidación detallado | `12_generar_reporte_detallado.py` | ✅ DONE | Archivo: `03_reporte_consolidacion_detallado.xlsx` |
| Scripts SQL de validación | `13_generar_sql_validacion.py` | ✅ DONE | Archivo: `00_validacion_previa_consolidacion_*.sql` |
| Scripts SQL de consolidación | `15_generar_sql_consolidacion_final.py` | ✅ DONE | Archivos: `01_consolidar_alta_confianza_*.sql`, `02_rollback_consolidacion_*.sql` |
| Archivo final consolidado | `14_generar_06_update_FINAL.py` | ✅ DONE | Archivo: `20_update_phxId_customer_location_FINAL.xlsx` |
| **Envío a Unilever (iterativo)** | - | 🔴 TO DO | Pendiente enviar reportes en 3-4 iteraciones para validación |
| Ejecución en BD (después de validación) | Scripts SQL | ⏸️ PENDING | Requiere aprobación de Unilever primero |

### Resultados de Consolidación:

#### Resumen de Grupos Identificados:

| Método | Grupos | Locations | Nivel Confianza | Acción Recomendada |
|--------|--------|-----------|-----------------|-------------------|
| **Geo-proximidad + Tax ID** | 4,749 | 10,615 | ✅ ALTA (99.95%) | Consolidar automáticamente |
| **Dominios corporativos** | 424 | 3,446 | ⚠️ MEDIA/BAJA | Revisión manual / Validación Unilever |
| **TOTAL** | 5,173 | 14,066 | - | - |

#### Archivos de Revisión Generados:

```
datos_generados/ArchivosGenerados/
├── 17_revision_grupos_alta_confianza_completo.xlsx      (10,615 locations - LISTO PARA CONSOLIDAR)
├── 18_revision_grupos_media_confianza.xlsx              (939 locations - REVISAR)
├── 19_revision_grupos_baja_confianza.xlsx               (2,512 locations - REVISAR CRÍTICO)
├── 14_reporte_grupos_dominios_detallado.xlsx            (Análisis por dominios)
└── 15_reporte_grupos_geolocalizacion_detallado.xlsx     (Análisis por proximidad)
```

### Hallazgos Clave:

1. **ALTA CONFIANZA (10,615 locations):**
   - Mismo Tax ID + ubicación < 50 metros
   - Mayoría con distancia = 0 metros (coordenadas exactas)
   - **Causa:** Múltiples registros para el mismo PDV físico
   - **Acción:** Consolidar automáticamente

2. **DOMINIOS CORPORATIVOS (3,446 locations):**
   - 424 grupos identificados
   - **Grupo más grande:** CORP_0012 (871 locations, 443 Tax IDs únicos)
   - **Patrón detectado:** Dominios compartidos por múltiples negocios independientes (SaaS, cooperativas, franquicias)
   - **Acción:** Requiere validación manual y aprobación de Unilever

### Próximos Pasos:

1. ⏸️ **Preparar lote 1 para Unilever:** Seleccionar ~50-100 grupos de ALTA confianza para validación inicial
2. ⏸️ **Enviar iteración 1:** Email con reporte y criterios de consolidación
3. ⏸️ **Recibir feedback:** Ajustar algoritmo según comentarios
4. ⏸️ **Iteraciones 2-4:** Incrementar cantidad de grupos progresivamente
5. ⏸️ **Ejecución final:** Una vez aprobado, ejecutar scripts SQL en BD

---

## 📊 TAREA 3: Unificación de PDVs Repetidos (Aylen Arcodia)

**Descripción:** Unificar los PDVs repetidos que pasa Aylen Arcodia, son aprox 370 a 400 PDVs.

**Esfuerzo estimado:** No especificado

### Estado: 🔴 TO DO (0% completado)

### Detalle de Avance:

| Subtarea | Script | Estado | Notas |
|----------|--------|--------|-------|
| Recibir archivo de Aylen | - | 🔴 TO DO | No se encontró archivo en el proyecto |
| Análisis de PDVs repetidos | - | 🔴 TO DO | Pendiente recibir listado |
| Script de unificación específico | - | 🔴 TO DO | Podría reutilizarse lógica de `06_consolidacion_customer_locations.py` |
| Validación y prueba | - | 🔴 TO DO | - |
| Ejecución en BD | - | 🔴 TO DO | - |

### Archivos Disponibles:

No se encontraron archivos relacionados con el listado de Aylen Arcodia en el proyecto.

### Próximos Pasos:

1. ⏸️ **Solicitar archivo a Aylen:** Obtener listado de 370-400 PDVs repetidos
2. ⏸️ **Analizar estructura:** Verificar qué información contiene (IDs, Tax IDs, nombres, etc.)
3. ⏸️ **Determinar criterio:** Definir cómo identificar cuáles son repetidos (puede ser un subconjunto de la consolidación ya realizada)
4. ⏸️ **Generar script específico:** Crear script de unificación o adaptar existente
5. ⏸️ **Validar y ejecutar:** Probar en ambiente de desarrollo antes de producción

---

## 📁 Estructura de Archivos del Proyecto

### Scripts Principales (Orden de Ejecución):

```
scripts/
├── 01_extraer_clientes_elvis.py                    [✅ EJECUTADO]
├── 02_extraer_pedidos_elvis_por_trimestre.py       [✅ EJECUTADO]
├── 03_generar_mapeo_droguerias.py                  [✅ EJECUTADO]
├── 04_analizar_compatibilidad_campos.py            [✅ EJECUTADO]
├── 05_transformar_elvis_a_tracy.py                 [⚠️ PARCIALMENTE EJECUTADO - Falta pre-2025]
├── 06_consolidacion_customer_locations.py          [✅ EJECUTADO]
├── 07_generar_reporte_dominios_detallado.py        [✅ EJECUTADO]
├── 08_generar_reporte_geo_detallado.py             [✅ EJECUTADO]
├── 09_analisis_erps_con_arrays.py                  [✅ EJECUTADO]
├── 10_analisis_erps_corregido.py                   [✅ EJECUTADO]
├── 11_generar_comparacion_erps_actuales.py         [✅ EJECUTADO]
├── 12_generar_reporte_detallado.py                 [✅ EJECUTADO]
├── 14_generar_06_update_FINAL.py                   [✅ EJECUTADO]
└── 15_generar_sql_consolidacion_final.py           [✅ EJECUTADO]

raíz/
└── 13_generar_sql_validacion.py                    [✅ EJECUTADO]
```

### Archivos Generados Clave:

```
datos_generados/ArchivosGenerados/
├── 00_validacion_previa_consolidacion_*.sql              [SQL - Validación pre-consolidación]
├── 01_consolidar_alta_confianza_*.sql                    [SQL - Script consolidación]
├── 01_resumen_consolidacion_*.csv                        [CSV - Resumen ejecutivo]
├── 02_rollback_consolidacion_*.sql                       [SQL - Rollback de emergencia]
├── 03_reporte_consolidacion_detallado.xlsx               [XLSX - Reporte maestro]
├── 10_consolidacion_completa.csv                         [CSV - Todos los grupos]
├── 11_estadisticas_por_grupo.csv                         [CSV - Métricas]
├── 12_fase1_consolidacion_dominios_corporativos.csv      [CSV - Resultados Fase 1]
├── 13_fase2_consolidacion_geo_proximidad.csv             [CSV - Resultados Fase 2]
├── 14_reporte_grupos_dominios_detallado.xlsx             [XLSX - Análisis dominios]
├── 15_reporte_grupos_geolocalizacion_detallado.xlsx      [XLSX - Análisis geo]
├── 16_analisis_erps_completo_corregido.xlsx              [XLSX - Análisis ERPs]
├── 17_revision_grupos_alta_confianza_completo.xlsx       [XLSX - Para consolidar]
├── 18_revision_grupos_media_confianza.xlsx               [XLSX - Para revisar]
├── 19_revision_grupos_baja_confianza.xlsx                [XLSX - Para revisar crítico]
└── 20_update_phxId_customer_location_FINAL.xlsx          [XLSX - Archivo final]
```

---

## 🎯 Próximas Acciones Prioritarias

### Corto Plazo (Esta Semana):

1. **⚠️ TAREA 1:** Ejecutar `05_transformar_elvis_a_tracy.py` para completar transformación de pedidos pre-2025
2. **🔴 TAREA 2:** Preparar primera iteración de validación con Unilever (seleccionar ~50 grupos de alta confianza)
3. **🔴 TAREA 3:** Contactar a Aylen Arcodia para obtener listado de PDVs repetidos

### Mediano Plazo (Próximas 2 Semanas):

1. **TAREA 1:** Importar pedidos históricos transformados a BD Tracy
2. **TAREA 2:** Completar proceso iterativo de validación con Unilever (3-4 rondas)
3. **TAREA 3:** Analizar y procesar listado de Aylen Arcodia

### Largo Plazo (Próximo Mes):

1. **TAREA 2:** Ejecutar consolidación en BD producción (después de aprobación)
2. **TAREA 3:** Ejecutar unificación de PDVs de Aylen
3. **General:** Validación post-consolidación y auditoría de calidad de datos

---

## 📊 Métricas del Proyecto

### Cobertura de Análisis:

- **Total Customer Locations:** 31,664
- **Locations Agrupadas:** 14,066 (44.4%)
- **Locations Sin Agrupar:** 17,598 (55.6%)
- **Grupos Identificados:** 5,173

### Calidad de Datos:

- **Locations con coordenadas válidas:** 18,900 (59.7%)
- **Locations con Tax ID válido:** 31,478 (99.4%)
- **Locations con datos completos:** 18,900 (ambos)

### Impacto Esperado de Consolidación:

- **Reducción de registros:** ~33.5% (de 31,664 a ~21,049)
- **Mejora en calidad de datos:** Alta
- **Pedidos a redistribuir:** Variable según grupo

---

## 🔗 Referencias

- **README Principal:** `README.md`
- **Resumen Consolidación:** `RESUMEN_CONSOLIDACION.md`
- **Análisis Inicial:** `analisis_consolidacion_inicial_markdown.md`
- **Documentación Pipeline:** Ver scripts individuales

---

**Última actualización:** 2026-03-12
**Responsable:** Equipo Unilever CompraBeauty
**Fase:** 2 - Consolidación
