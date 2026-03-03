# Pipeline de Consolidación de Customer Locations
## Proyecto Unilever CompraBeauty - Fase 2

---

## 📋 Descripción del Proyecto

Este pipeline automatiza la consolidación de **Customer Locations duplicados** en la plataforma Tracy (CompraBeauty), provenientes de la migración del sistema Elvis. El objetivo es identificar y consolidar registros duplicados basándose en:

- **Dominios corporativos** de email
- **Códigos logísticos** compartidos
- **Proximidad geográfica** (< 50 metros)
- **Similitud de Tax IDs**

El resultado es un conjunto de scripts SQL listos para ejecutar la consolidación en base de datos, con validaciones y respaldos automáticos.

---

## 🗂️ Estructura del Proyecto

```
Unilever_Comprabeauty_Fase2/
├── scripts/                      # Scripts Python del pipeline
│   ├── 01_extraer_clientes_elvis.py
│   ├── 02_extraer_pedidos_elvis_por_trimestre.py
│   ├── 03_generar_mapeo_droguerias.py
│   ├── 04_analizar_compatibilidad_campos.py
│   ├── 05_transformar_elvis_a_tracy.py
│   ├── 06_consolidacion_customer_locations.py
│   ├── 07_generar_reporte_dominios_detallado.py
│   ├── 08_generar_reporte_geo_detallado.py
│   ├── 09_analisis_erps_con_arrays.py
│   ├── 10_analisis_erps_corregido.py
│   ├── 11_generar_comparacion_erps_actuales.py
│   ├── 12_generar_reporte_detallado.py
│   └── 14_generar_06_update_FINAL.py
├── 13_generar_sql_validacion.py  # Script en raíz del proyecto
├── Csvs/                         # Archivos CSV de entrada
│   ├── CustomerLocation.csv
│   ├── EcommerceUsers.csv
│   ├── LogisticCode.csv
│   ├── MarketplaceDistributors.csv
│   ├── orders.csv
│   └── SalesRepCustomerLocations.csv
├── datos_generados/              # Salidas del pipeline
│   ├── consolidacion_completa.csv
│   ├── estadisticas_por_grupo.csv
│   ├── 03_reporte_consolidacion_detallado.csv / .xlsx
│   ├── 00_validacion_previa_consolidacion_*.sql
│   ├── 01_consolidar_alta_confianza_*.sql
│   └── 02_rollback_consolidacion_*.sql
├── historicos/                   # Datos históricos de Elvis
│   └── Historico_Elvis_fragmented_by_Q/
└── backups/                      # Scripts antiguos

```

---

## 🚀 Pipeline Completo

El pipeline se divide en **3 fases principales** que deben ejecutarse en orden:

---

### **FASE 1: Extracción y Transformación (Elvis → Tracy)**

Convierte datos del sistema legacy Elvis al formato Tracy.

#### **1️⃣ Script: `01_extraer_clientes_elvis.py`**
**Propósito:** Extrae la solapa "fichero" del Excel de Elvis y exporta los clientes a CSV.

**Entrada:**
- Archivo Excel de Elvis con solapa "Fichero"

**Salida:**
- `clientes.elvis.csv` - Base de datos de clientes de Elvis

**Ejecución:**
```bash
cd scripts
python 01_extraer_clientes_elvis.py [archivo_elvis.xlsx]
```

---

#### **2️⃣ Script: `02_extraer_pedidos_elvis_por_trimestre.py`**
**Propósito:** Divide el histórico de pedidos de Elvis en archivos trimestrales para facilitar el procesamiento.

**Entrada:**
- Excel con histórico completo de pedidos Elvis

**Salida:**
- `historicos/Historico_Elvis_fragmented_by_Q/pedidos.elvis.YYYY.QX.csv`

**Ejecución:**
```bash
python 02_extraer_pedidos_elvis_por_trimestre.py
```

---

#### **3️⃣ Script: `03_generar_mapeo_droguerias.py`**
**Propósito:** Genera el mapeo entre códigos de droguerías de Elvis y Tracy.

**Entrada:**
- Archivo de configuración con mapeos

**Salida:**
- Archivo Excel con mapeo Elvis → Tracy

**Ejecución:**
```bash
python 03_generar_mapeo_droguerias.py
```

---

#### **4️⃣ Script: `04_analizar_compatibilidad_campos.py`**
**Propósito:** Analiza compatibilidad de campos entre Elvis y Tracy, detectando diferencias de formato.

**Entrada:**
- CSVs de Elvis y Tracy

**Salida:**
- Reporte de compatibilidad de campos

**Ejecución:**
```bash
python 04_analizar_compatibilidad_campos.py
```

---

#### **5️⃣ Script: `05_transformar_elvis_a_tracy.py`**
**Propósito:** Transforma pedidos de Elvis a formato Tracy aplicando todos los mapeos.

**Mapeos aplicados:**
- `PEDIDO` → `ORDER ERP ID`
- `CONTACTO ID` → `CUSTOMER LOCATION - ERP ID` (con prefijo `phxId:`)
- Estados: Validado → FINALIZADO, Pendiente → ENVIADO
- Droguerías según mapeo generado en script 03

**Entrada:**
- `pedidos.elvis.YYYY.QX.csv` (trimestral)
- Mapeo de droguerías

**Salida:**
- Archivos Tracy por trimestre listos para importar

**Ejecución:**
```bash
python 05_transformar_elvis_a_tracy.py
```

---

### **FASE 2: Consolidación de Customer Locations**

Identifica y agrupa Customer Locations duplicados.

#### **6️⃣ Script: `06_consolidacion_customer_locations.py`**
**Propósito:** Script principal que identifica grupos de customer locations duplicados.

**Criterios de consolidación:**
1. **Dominios corporativos:** Locations con mismo dominio no genérico (excluye gmail.com, hotmail.com, etc.)
2. **Códigos logísticos:** Locations que comparten código logístico y distribuidor
3. **Proximidad geográfica:** Locations a < 50 metros de distancia
4. **Tax ID similar:** Similitud Levenshtein > 0.8

**Configuración:**
```python
GENERIC_DOMAINS = {
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'live.com', 'icloud.com', 'protonmail.com', 'aol.com'
}
GEO_DISTANCE_THRESHOLD_METERS = 50
TAXID_SIMILARITY_THRESHOLD = 0.8
```

**Entrada:**
- `Csvs/CustomerLocation.csv`
- `Csvs/EcommerceUsers.csv`
- `Csvs/LogisticCode.csv`
- `Csvs/MarketplaceDistributors.csv`
- `Csvs/orders.csv`
- `Csvs/SalesRepCustomerLocations.csv`

**Salida:**
- `datos_generados/consolidacion_completa.csv` - Todos los grupos identificados
- `datos_generados/estadisticas_por_grupo.csv` - Métricas por grupo
- `datos_generados/reporte_grupos_alta_confianza.csv` - Grupos con nivel de confianza ALTA
- `datos_generados/reporte_grupos_revision.csv` - Grupos que requieren revisión manual

**Niveles de confianza:**
- **ALTA:** Múltiples señales (dominio + código logístico + geo)
- **MEDIA:** Al menos 2 señales concordantes
- **BAJA:** Solo 1 señal o señales débiles

**Ejecución:**
```bash
python 06_consolidacion_customer_locations.py
```

---

#### **7️⃣ Script: `07_generar_reporte_dominios_detallado.py`**
**Propósito:** Genera reporte detallado de consolidación por dominios corporativos.

**Salida:**
- `datos_generados/fase1_consolidacion_dominios_corporativos.csv`

**Ejecución:**
```bash
python 07_generar_reporte_dominios_detallado.py
```

---

#### **8️⃣ Script: `08_generar_reporte_geo_detallado.py`**
**Propósito:** Genera reporte detallado de consolidación por proximidad geográfica.

**Salida:**
- `datos_generados/fase2_consolidacion_geo_proximidad.csv`

**Ejecución:**
```bash
python 08_generar_reporte_geo_detallado.py
```

---

### **FASE 3: Análisis y Generación de Scripts SQL**

Analiza ERPs, genera reportes enriquecidos y crea scripts SQL para ejecutar la consolidación.

#### **9️⃣ Script: `09_analisis_erps_con_arrays.py`**
**Propósito:** Analiza los arrays de ERPIds en customer locations, identificando cuáles están siendo usados en Tracy.

**Entrada:**
- `06 update phxId customer location.xlsx`
- `Tracy 2025 FINAL.xlsx`

**Salida:**
- Reporte de ERPIds en uso vs no usados

**Ejecución:**
```bash
python 09_analisis_erps_con_arrays.py
```

---

#### **🔟 Script: `10_analisis_erps_corregido.py`**
**Propósito:** Versión corregida del análisis de ERPIds, maneja casos especiales.

**Entrada:**
- `06 update phxId customer location.xlsx`
- `Tracy 2025 FINAL.xlsx`

**Salida:**
- Análisis refinado de ERPIds

**Ejecución:**
```bash
python 10_analisis_erps_corregido.py
```

---

#### **1️⃣1️⃣ Script: `11_generar_comparacion_erps_actuales.py`**
**Propósito:** Genera comparación entre ERPIds actuales y propuestos.

**Salida:**
- `COMPARACION_ERPS_ACTUALES_VS_PROPUESTOS.xlsx`

**Ejecución:**
```bash
python 11_generar_comparacion_erps_actuales.py
```

---

#### **1️⃣2️⃣ Script: `12_generar_reporte_detallado.py`**
**Propósito:** Enriquece los resultados de consolidación con información detallada de cada location para revisión manual.

**Información incluida:**
- Datos de location (nombre, dirección, coordenadas, Tax ID)
- Usuarios asociados (emails)
- Códigos logísticos
- Distribuidores
- Cantidad de pedidos
- Representantes de ventas

**Entrada:**
- `datos_generados/consolidacion_completa.csv`
- Todos los CSVs en `Csvs/`

**Salida:**
- `datos_generados/03_reporte_consolidacion_detallado.csv` (y `.xlsx`)
- `datos_generados/reporte_consolidacion_detallado.csv`

**Ejecución:**
```bash
cd scripts
python 12_generar_reporte_detallado.py
```

---

#### **1️⃣3️⃣ Script: `13_generar_sql_validacion.py`** ⚠️ (Raíz del proyecto)
**Propósito:** Genera script SQL de validación previa para verificar el estado de la BD antes de ejecutar la consolidación.

**Validaciones incluidas:**
1. Estado actual de la BD (locations, pedidos, códigos logísticos)
2. Verificación de locations master y duplicados
3. Análisis de pedidos (cuántos se van a mover)
4. Análisis de códigos logísticos (conflictos potenciales)
5. Verificación de integridad referencial
6. Análisis de impacto (cuántas locations se eliminarán)
7. Verificación de tablas de backup
8. **Checklist final con GO/NO-GO**

**Entrada:**
- `datos_generados/revision_grupos_alta_confianza_completo.xlsx`

**Salida:**
- `datos_generados/00_validacion_previa_consolidacion_YYYYMMDD_HHMMSS.sql`

**Ejecución:**
```bash
python 13_generar_sql_validacion.py
```

**⚠️ CRÍTICO:** Este script debe ejecutarse en la BD ANTES del script de consolidación.

---

#### **1️⃣4️⃣ Script: `14_generar_06_update_FINAL.py`**
**Propósito:** Genera archivo final consolidado actualizando ERPIds de customer locations.

**Entrada:**
- `06 update phxId customer location.xlsx`
- `UPDATE_CUSTOMER_LOCATION_ERPIDS_PISADOS.xlsx`
- `Tracy 2025 FINAL.xlsx`

**Salida:**
- `06 update phxId customer location FINAL.xlsx` - Archivo consolidado final

**Ejecución:**
```bash
python 14_generar_06_update_FINAL.py
```

---

## 📊 Archivos Generados

### **Reportes CSV/Excel**
| Archivo | Descripción |
|---------|-------------|
| `consolidacion_completa.csv` | Todos los grupos de consolidación identificados |
| `estadisticas_por_grupo.csv` | Métricas agregadas por grupo |
| `reporte_grupos_alta_confianza.csv` | Grupos listos para consolidar automáticamente |
| `reporte_grupos_revision.csv` | Grupos que requieren revisión manual |
| `03_reporte_consolidacion_detallado.csv/.xlsx` | Reporte enriquecido con toda la información |

### **Scripts SQL**
| Archivo | Descripción |
|---------|-------------|
| `00_validacion_previa_consolidacion_*.sql` | ⚠️ **Ejecutar PRIMERO** - Validaciones previas |
| `01_consolidar_alta_confianza_*.sql` | Script de consolidación principal |
| `02_rollback_consolidacion_*.sql` | Script de rollback en caso de problemas |

---

## ⚙️ Requisitos

### **Python 3.7+**

### **Librerías:**
```bash
pip install pandas numpy openpyxl xlsxwriter
```

### **Archivos de entrada requeridos:**
- Excel de Elvis con solapa "Fichero"
- CSVs de Tracy en `Csvs/`:
  - `CustomerLocation.csv`
  - `EcommerceUsers.csv`
  - `LogisticCode.csv`
  - `MarketplaceDistributors.csv`
  - `orders.csv`
  - `SalesRepCustomerLocations.csv`

---

## 🎯 Ejecución Completa del Pipeline

### **Paso 1: Extracción y Transformación**
```bash
cd scripts

# 1. Extraer clientes de Elvis
python 01_extraer_clientes_elvis.py elvis_data.xlsx

# 2. Dividir pedidos por trimestre
python 02_extraer_pedidos_elvis_por_trimestre.py

# 3. Generar mapeo de droguerías
python 03_generar_mapeo_droguerias.py

# 4. Analizar compatibilidad de campos
python 04_analizar_compatibilidad_campos.py

# 5. Transformar pedidos Elvis → Tracy
python 05_transformar_elvis_a_tracy.py
```

### **Paso 2: Consolidación**
```bash
# 6. Ejecutar consolidación principal
python 06_consolidacion_customer_locations.py

# 7-8. Generar reportes detallados
python 07_generar_reporte_dominios_detallado.py
python 08_generar_reporte_geo_detallado.py
```

### **Paso 3: Análisis y SQL**
```bash
# 9-11. Análisis de ERPs
python 09_analisis_erps_con_arrays.py
python 10_analisis_erps_corregido.py
python 11_generar_comparacion_erps_actuales.py

# 12. Generar reporte detallado final
python 12_generar_reporte_detallado.py

# 13. Generar script de validación SQL
cd ..
python 13_generar_sql_validacion.py

# 14. Generar archivo final
cd scripts
python 14_generar_06_update_FINAL.py
```

### **Paso 4: Ejecución en Base de Datos** ⚠️
```sql
-- 1. PRIMERO: Ejecutar validación
\. datos_generados/00_validacion_previa_consolidacion_YYYYMMDD_HHMMSS.sql

-- 2. Revisar resultados del checklist
--    Si todos los checks son OK, continuar

-- 3. Ejecutar consolidación
\. datos_generados/01_consolidar_alta_confianza_YYYYMMDD_HHMMSS.sql

-- 4. (Solo si hay problemas) Ejecutar rollback
\. datos_generados/02_rollback_consolidacion_YYYYMMDD_HHMMSS.sql
```

---

## 🔍 Algoritmo de Consolidación

### **1. Identificación de Grupos por Dominio Corporativo**
```python
Para cada dominio corporativo:
    Agrupar locations con mismo dominio
    Excluir dominios genéricos (gmail, hotmail, etc.)
```

### **2. Identificación por Código Logístico**
```python
Para cada par (Distribuidor, Código):
    Agrupar locations que comparten el mismo código
```

### **3. Identificación por Proximidad Geográfica**
```python
Para cada location con coordenadas:
    Buscar locations a < 50 metros (Haversine)
    Si Tax ID tiene similitud > 0.8 (Levenshtein):
        Agrupar locations
```

### **4. Fusión de Grupos**
```python
Unir grupos que comparten al menos 1 location
Resultado: Componentes conectados del grafo de duplicados
```

### **5. Selección de Master**
```python
Para cada grupo:
    Seleccionar master basándose en:
        1. Mayor cantidad de pedidos
        2. Mayor cantidad de códigos logísticos
        3. Tiene Tax ID completo
        4. ID más bajo (desempate)
```

### **6. Asignación de Nivel de Confianza**
```python
Si grupo tiene >= 3 señales concordantes: ALTA
Si grupo tiene 2 señales concordantes: MEDIA
Caso contrario: BAJA
```

---

## 📈 Métricas del Pipeline

Después de ejecutar el pipeline, revisa estas métricas en `estadisticas_por_grupo.csv`:

- **Total de grupos identificados**
- **Locations master seleccionados**
- **Locations duplicados a consolidar**
- **Grupos por nivel de confianza** (ALTA/MEDIA/BAJA)
- **Pedidos que se redistribuirán**
- **Códigos logísticos afectados**

---

## ⚠️ Notas Importantes

1. **Siempre ejecutar script de validación (00) antes de consolidar**
2. Los scripts están numerados en orden de ejecución
3. El script 13 está en la raíz del proyecto, no en `scripts/`
4. Hacer backup de la BD antes de ejecutar consolidación
5. Los scripts SQL incluyen respaldos automáticos de tablas
6. En caso de error, usar script de rollback (02)
7. Grupos con confianza BAJA requieren revisión manual

---

## 🛡️ Seguridad y Respaldos

Los scripts SQL generados incluyen:
- **Creación de tablas de backup** antes de modificar datos
- **Transacciones** para garantizar atomicidad
- **Validaciones** de integridad referencial
- **Scripts de rollback** automáticos

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar logs de ejecución de cada script
2. Verificar archivos en `datos_generados/`
3. Consultar script de validación SQL para diagnóstico

---

## 📝 Changelog

- **Fase 2 (2026-03):** Pipeline de consolidación de customer locations
- **Fase 1 (2025):** Migración Elvis → Tracy

---

**Última actualización:** 2026-03-03
