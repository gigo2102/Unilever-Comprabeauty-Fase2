# Análisis básico estadístico de datos Básicos Customer Location

---

## 1. Análisis básico estadístico

Fuente: *Question · Metabase*

### Conteos básicos

| Categoría | Métrica | Valor |
|---|---|---:|
| 01 - CONTEOS_BASICOS | registros_completos_coord_taxid | 3120 |
| 01 - CONTEOS_BASICOS | registros_con_coordenadas_validas | 3133 |
| 01 - CONTEOS_BASICOS | registros_con_taxid_valido | 9711 |
| 01 - CONTEOS_BASICOS | total_registros | 9724 |

### Calidad de datos

| Categoría | Métrica | Valor |
|---|---|---:|
| 02 - CALIDAD_DATOS | latitude_null_count | 3765 |
| 02 - CALIDAD_DATOS | latitude_zero_count | 2823 |
| 02 - CALIDAD_DATOS | longitude_null_count | 3765 |
| 02 - CALIDAD_DATOS | longitude_zero_count | 2826 |
| 02 - CALIDAD_DATOS | taxid_empty_or_zero | 13 |
| 02 - CALIDAD_DATOS | taxid_null_count | 0 |

### Estadísticas de Latitud

| Métrica | Valor |
|---|---:|
| avg | -32.777107 |
| max | -22.1031772 |
| min | -41.32994679999999 |
| stddev | 2.964347 |

### Estadísticas de Longitud

| Métrica | Valor |
|---|---:|
| avg | -61.153539 |
| max | -55.8765162 |
| min | -71.07528529999999 |
| stddev | 3.480455 |

### Patrones de TaxID

| Métrica | Valor |
|---|---:|
| taxid_length_avg | 11.00 |
| taxid_length_max | 11 |
| taxid_length_min | 11 |

### Percentiles de Latitud

| Percentil | Valor |
|---|---:|
| 25 | -34.652051 |
| 50 (mediana) | -32.957692 |
| 75 | -31.462270 |

### Distribución geográfica

| Métrica | Valor |
|---|---:|
| coordenadas_argentina_aprox | 3133 |
| coordenadas_fuera_argentina | 0 |

### Duplicados

| Métrica | Valor |
|---|---:|
| locations_duplicadas_exactas | 87 |
| taxid_duplicados | 1833 |

---

## 2. Grupos por dominio de e‑mail

Caso testigo: un **PDV** con **58 logistic codes activos en 2025**, de **3 distribuidores distintos**, realizó **199 pedidos con artículos** (no borrador).

- Total métricas observadas:
  - **199** orders
  - **58** logistic codes
  - **1** usuario
  - **3** distribuidores
  - **1** location

Resultado visible en Metabase:
- **44 usuarios** con dominio `puntodesalud`

Listado de usuarios (ejemplo):
- PUNTO DE SALUD MALVINAS DANIELA
- PUNTO DE SALUD AVELLANEDA
- PUNTO DE SALUD GUERNICA
- PUNTO DE SALUD JUNCAL
- … (44 en total)

---

## 3. Análisis de combinaciones (órdenes y códigos)

Observaciones:

- En Metabase se ve que son **478 orders**, pero **1 sola cuenta** hizo casi **200** de esos pedidos.
- **58** códigos logísticos en esa cuenta.
- En todo el grupo:
  - **95** combinaciones de droguería + código logístico distintas
  - **188** combinaciones totales distintas en base de datos (mismo distri/código usado por distintos usuarios)

Resumen:

- **44 usuarios**
- **44 customer locations** (sin analizar duplicados internos)
- **95** combinaciones únicas droguería + código logístico
- **188** combinaciones totales usadas
- Droguería con más códigos operativos en 2025: **22 códigos**, lo que coincide con **22 sucursales** (validado por web)

👉 Se propone hacer **análisis por dominios no genéricos**.

---

## 4. Dominios no genéricos

Resultados:

- **85 grupos** de dominios **no genéricos**
- Facilitan la unificación de **470 usuarios** dentro de esos grupos

Ejemplos de dominios:

| Dominio | user_count |
|---|---:|
| puntodarma.com | 29 |
| gdpsalud.com.ar | 28 |
| puntodesalud.com.ar | 23 |
| paradinerofarmacias.com.ar | 18 |
| farmaciasvilera.com.ar | 16 |
| farmavidam.com | 15 |
| jerarquicos.com | 15 |
| onativia.com.ar | 14 |

---

## 5. Grupos por Lat/Long y similitud de TaxID

### Escenario A

- Tolerancia: **200 metros**
- Sin usar similitud de TaxID

Resultado:
- **712 únicos** sin repetidos
- **1066** registros totales

### Escenario B

- Tolerancia: **< 50 metros**
- Similitud de TaxID **> 0.6**

Resultado:
- **166 unificados** de **176** registros

---

## 6. Análisis por Logistic Codes con pedidos

Resultados globales:

- **2772 usuarios**
- **2998 customer locations** (sin analizar duplicados internos)
- **3748** combinaciones distintas de droguería + código logístico
- **4377** combinaciones totales usadas

👉 **Potencial de deduplicación: 529 registros**

---

## 7. Ejemplo detallado (cadena Punto de Salud)

Usuarios con historial de pedidos y códigos logísticos:

- javier almaras – dominio puntodesalud – múltiples códigos
- seba alonso – dominio puntodesalud
- avellaneda – dominio puntodesalud
- asistenteperfu – dominio puntodesalud
- leo messi – dominio gmail (INACTIVO)

---

## 8. Propuesta de consolidación

### PASO 1 – Seguro

Armar **grupos de consolidación** por:

1. Dominio no genérico
2. Uso de misma combinación droguería + código logístico

Luego:
- Regla: **CUIT no puede usarse en más de una cuenta grupal**

### PASO 2 – Unificar PDVs

#### 2.1 PDVs migrados

- **Paso 2.1.1 (probable, según Unilever)**
  - Expandir PDVs con pedidos en más de un domicilio
  - Unificar PDVs repetidos
  - ⚠️ Requiere **intervención de comercios** (configurar correctamente códigos logísticos)

- **Paso 2.1.2 (nice to have)**
  - Limpiar historiales de pedidos de PDVs unificados
  - Regla futura: combinación droguería + código logístico no puede usarse en más de un domicilio

#### 2.2 Freeze de PDVs viejos

- Todo PDV con pedidos con **más de un código logístico para la misma droguería**:
  - Pasa a PDV **freezado** (solo lectura)
- Luego:
  - Regla sistémica: droguería + código logístico no se repite en más de un domicilio

