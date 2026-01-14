================================================================================
PROYECTO UNILEVER - COMPRA BEAUTY FASE 2
================================================================================

DESCRIPCIÓN DEL PROYECTO
================================================================================

Este proyecto realiza la migración completa de datos desde el sistema Elvis
(legacy) hacia el sistema Tracy (nuevo). Incluye la transformación de datos
de clientes y pedidos históricos, con mapeos personalizados y validaciones
de compatibilidad.

Período de datos: 2020 Q2 - 2025 Q2 (5 años de histórico)


ESTRUCTURA DEL PROYECTO
================================================================================

Unilever_Comprabeauty_Fase2/
│
├── Scripts Principales (Orden de ejecución)
│   ├── 01_extraer_clientes_elvis.py
│   ├── 02_extraer_pedidos_elvis_por_trimestre.py
│   ├── 03_generar_mapeo_droguerias.py
│   ├── 04_analizar_compatibilidad_campos.py
│   ├── 05_transformar_elvis_a_tracy.py
│   └── 06_generar_actualizacion_customer_location.py
│
├── Datos de Entrada
│   ├── Base Elvis 2025.xlsx (base completa de Elvis)
│   ├── Tracy 2025.xlsx (referencia de Tracy)
│   └── Archivos tracy*.csv (datos de referencia)
│
├── Datos Históricos
│   ├── Historico_Elvis_fragmented_by_Q/ (21 CSV por trimestre, 321 MB)
│   └── HistoricoPedidosUnileverFito/ (16 XLSX, 369 MB)
│
├── Datos de Salida (Generados)
│   ├── clientes.elvis.csv
│   ├── pedidos.elvis.YYYY.Qx.csv (21 archivos)
│   ├── mapeo_droguerias_elvis_tracy.xlsx
│   ├── Tracy 2025.xlsx (resultado final transformado)
│   └── 06 update phxId customer location.xlsx
│
├── Documentación
│   ├── README.txt (este archivo)
│   ├── MAPEO_CAMPOS.md
│   ├── documentacion_mapeo_campos.xlsx
│   ├── mapeo_droguerias_elvis_tracy.pdf
│   ├── Order History Import Guide.pdf
│   ├── INFORME_PROGRESO.docx
│   └── TODO.txt
│
├── Análisis de Clientes
│   └── CustomerLocation_Tracy_Elvis/
│       ├── 07.1 OPCION1 - Clientes para CREAR en Tracy.xlsx
│       ├── 07.2 OPCION2 - Clientes EXISTENTES en Tracy.xlsx
│       └── 07.3 OPCION3 - TODOS los clientes Elvis faltantes.xlsx
│
└── backups/ (versiones antiguas de scripts)
    ├── transform_elvis_to_tracy.py
    ├── transform_elvis_to_tracy_optimized.py
    ├── transform_elvis_to_tracy.backup.py
    └── process_tracy_files.py


REQUISITOS DEL SISTEMA
================================================================================

Software Necesario:
  - Python 3.7 o superior
  - pandas
  - openpyxl

Instalación de Dependencias:
  pip install pandas openpyxl


FLUJO DE TRABAJO COMPLETO
================================================================================

PASO 1: EXTRACCIÓN DE DATOS DE ELVIS
--------------------------------------------------------------------------------

1.1 Extraer Clientes
--------------------
Comando:
  python 01_extraer_clientes_elvis.py

¿Qué hace?
  - Lee la hoja "Fichero" de Base Elvis 2025.xlsx
  - Limpia campos de texto (elimina comas y punto y coma)
  - Reemplaza valores "nan" con cadenas vacías
  - Genera clientes.elvis.csv

Entrada: Base Elvis 2025.xlsx
Salida: clientes.elvis.csv


1.2 Extraer Pedidos por Trimestre
----------------------------------
Comando:
  python 02_extraer_pedidos_elvis_por_trimestre.py

¿Qué hace?
  - Lee las hojas "Año 2020" a "Año 2025" de Base Elvis 2025.xlsx
  - Detecta automáticamente la columna de fecha
  - Divide los datos por trimestres (Q1, Q2, Q3, Q4)
  - Limpia campos de texto
  - Genera 21 archivos CSV separados por trimestre

Entrada: Base Elvis 2025.xlsx
Salida: 21 archivos pedidos.elvis.YYYY.Qx.csv
        (ejemplo: pedidos.elvis.2020.Q2.csv)

Período cubierto: 2020 Q2 hasta 2025 Q2


PASO 2: PREPARACIÓN DE MAPEOS
--------------------------------------------------------------------------------

2.1 Generar Archivo de Mapeo de Droguerías
-------------------------------------------
Comando:
  python 03_generar_mapeo_droguerias.py

¿Qué hace?
  - Procesa los 21 CSV de pedidos + clientes.elvis.csv
  - Extrae todos los valores únicos de la columna "DROGUERIA"
  - Crea un archivo Excel con 2 columnas:
    * ELVIS: Valores originales de Elvis
    * TRACY: Columna vacía para mapeo manual

Entrada:
  - clientes.elvis.csv
  - Todos los pedidos.elvis.YYYY.Qx.csv

Salida: mapeo_droguerias_elvis_tracy.xlsx

IMPORTANTE: Después de ejecutar este script, debes:
  1. Abrir mapeo_droguerias_elvis_tracy.xlsx
  2. Llenar manualmente la columna "TRACY" con los valores correspondientes
  3. Guardar el archivo


2.2 Analizar Compatibilidad de Campos (Opcional)
-------------------------------------------------
Comando:
  python 04_analizar_compatibilidad_campos.py

¿Qué hace?
  - Compara valores entre archivos de Elvis y Tracy
  - Identifica campos que tienen valores coincidentes
  - Genera reporte de compatibilidad en consola
  - Útil para validar que los mapeos son correctos

Entrada:
  - clientes.elvis.csv
  - tracy.customer.locations.V2.csv
  - tracy.distributors.V2.csv
  - tracy.ecommerce.users.V2.csv
  - tracy.logistic.code.V2.csv

Salida: Reporte en consola con porcentajes de coincidencia


PASO 3: TRANSFORMACIÓN PRINCIPAL
--------------------------------------------------------------------------------

3.1 Transformar Datos de Elvis a Tracy
---------------------------------------
Comando:
  python 05_transformar_elvis_a_tracy.py

¿Qué hace?
Este es el script más crítico del proyecto. Realiza la transformación completa
de todos los datos:

  1. Lee todas las hojas de años de Base Elvis 2025.xlsx
  2. Aplica el mapeo de droguerías desde mapeo_droguerias_elvis_tracy.xlsx
  3. Transforma todos los campos según el mapeo definido
  4. Aplica transformaciones especiales:
     - Estados (Validado → FINALIZADO, etc.)
     - Customer Location ERP IDs (añade prefijo "phxId:")
     - Cálculo de rechazadas (P.U. - ATENDIDAS)
     - Sistema siempre a "CB PHARMEXX"
  5. Genera el archivo final para importar en Tracy

Entrada:
  - Base Elvis 2025.xlsx
  - mapeo_droguerias_elvis_tracy.xlsx (debe estar completado manualmente)

Salida: Tracy 2025.xlsx

IMPORTANTE: Este archivo es el que se usa para importar pedidos en el
sistema Tracy.


PASO 4: ACTUALIZACIÓN DE CUSTOMER LOCATION
--------------------------------------------------------------------------------

4.1 Generar Actualización de Customer Location
-----------------------------------------------
Comando:
  python 06_generar_actualizacion_customer_location.py

¿Qué hace?
  - Cruza datos de histórico de pedidos con clientes y Tracy
  - Genera dataset para actualizar Customer Location en Tracy
  - Recupera los erpIds correctos que fueron sobrescritos por error en agosto

Contexto del problema:
Los customer location erpid fueron sobrescritos por error en agosto. Este
script genera el archivo necesario para recuperar los valores correctos
antes de importar los pedidos.

Entrada:
  - Historico_Elvis_fragmented_by_Q/*.csv
  - clientes.elvis.csv
  - Tracy 2025.xlsx o tracy.customer.locations.csv

Salida: 06 update phxId customer location.xlsx

Columnas generadas:
  1. customerLocation.Id (ID de Tracy)
  2. customerLocation.erpIds (ErpIds de Tracy)
  3. user.mail (Email del cliente)
  4. clienteelvis.contactoid (ID original de Elvis)

IMPORTANTE: Este archivo debe importarse en Tracy ANTES de importar los
pedidos.


DESCRIPCIÓN DETALLADA DE LOS SCRIPTS
================================================================================

01_extraer_clientes_elvis.py
--------------------------------------------------------------------------------
Propósito:          Extrae datos de clientes desde Excel de Elvis
Hoja procesada:     "Fichero"
Formato salida:     CSV con separador ; y decimal ,
Limpieza:           Elimina comas, punto y coma, reemplaza "nan"
Líneas de código:   ~87


02_extraer_pedidos_elvis_por_trimestre.py
--------------------------------------------------------------------------------
Propósito:            Extrae y divide pedidos por trimestres
Hojas procesadas:     "Año 2020" a "Año 2025"
Detección automática: Identifica columna de fecha
División:             Por trimestre (Q1, Q2, Q3, Q4)
Archivos generados:   21 CSV (2020.Q2 a 2025.Q2)
Líneas de código:     ~181


03_generar_mapeo_droguerias.py
--------------------------------------------------------------------------------
Propósito:                Genera archivo para mapeo manual de droguerías
Archivos procesados:      22 archivos CSV (pedidos + clientes)
Salida:                   Excel con 2 columnas (ELVIS, TRACY)
Acción manual requerida:  Llenar columna TRACY
Líneas de código:         ~100


04_analizar_compatibilidad_campos.py
--------------------------------------------------------------------------------
Propósito:          Valida compatibilidad entre Elvis y Tracy
Tipo de análisis:   Comparación de valores entre campos
Salida:             Reporte en consola con % de coincidencia
Uso:                Opcional, para validación
Líneas de código:   ~179


05_transformar_elvis_a_tracy.py
--------------------------------------------------------------------------------
Propósito:          Transformación completa Elvis → Tracy
Complejidad:        Alta (script más crítico)
Dependencias:       Requiere mapeo de droguerías completo
Transformaciones:   Campos, estados, cálculos, prefijos
Salida crítica:     Tracy 2025.xlsx (archivo final)
Líneas de código:   ~226


06_generar_actualizacion_customer_location.py
--------------------------------------------------------------------------------
Propósito:               Corrige customer locations sobrescritos
Problema que resuelve:   Sobrescritura accidental de erpIds en agosto
Tipo de operación:       Cruce de datos múltiples fuentes
Importancia:             Crítico ejecutar ANTES de importar pedidos
Líneas de código:        ~199


MAPEO DE CAMPOS: ELVIS → TRACY
================================================================================

CAMPOS DIRECTOS (Sin Transformación)
--------------------------------------------------------------------------------
Campo Elvis                           Campo Tracy              Observaciones
--------------------------------------------------------------------------------
PEDIDO                                ORDER ERP ID             Directo
FECHA                                 FECHA                    Directo
EAN 13                                EAN                      Directo
CODIGO                                CODIGO CLIENTE           Directo
COMENTARIO/COMENTARIOS/OBSERVACIONES  OBSERVACIONES            Variaciones
P.U.                                  CANTIDAD                 Directo
ATENDIDAS                             ATENDIDAS                Directo
P. COSTO BRUTO                        P. COSTO BRUTO           Directo
P. DESCUENTO %                        P. DESCUENTO %           Directo
P. COSTO NETO                         P. COSTO NETO            Directo
COMBOS                                COMBOS                   Directo
P. DESCUENTO CUPON %                  P. DESCUENTO CUPON %     Directo
CODIGOCUPON                           CODIGOCUPON              Directo


CAMPOS CON TRANSFORMACIÓN
--------------------------------------------------------------------------------

CUSTOMER LOCATION - ERP ID
  Origen:         CONTACTO ID
  Transformación: Añade prefijo "phxId:"
  Ejemplo:        5118 → phxId:5118

ESTADO
  Origen:         ESTADO
  Transformación: Mapeo de valores

  Valor Elvis                    Valor Tracy
  ------------------------------------------
  Validado / Validada            FINALIZADO
  Pendiente / Pendiente de envio ENVIADO
  Cancelado / Cancelada          CANCELADO
  Borrador                       BORRADOR
  Otros / Nulo                   NUEVO

DROGUERIA
  Origen:         DROGUERIA
  Transformación: Mapeo desde mapeo_droguerias_elvis_tracy.xlsx
  Fallback:       Si no encuentra el valor, usa el valor original limpio

ORIGEN
  Origen:         SISTEMA
  Transformación: Todos los valores se convierten a "CB PHARMEXX"

RECHAZADAS (Campo Calculado)
  Fórmula:    RECHAZADAS = P.U. - ATENDIDAS
  Descripción: Calcula unidades rechazadas restando atendidas de pedidas


FORMATO DE ARCHIVOS
================================================================================

CSV Generados:
  - Separador de campos: ; (punto y coma)
  - Separador decimal: , (coma)
  - Codificación: UTF-8 con BOM
  - Línea de encabezado: Sí

Excel Generados:
  - Formato: .xlsx (Office Open XML)
  - Compatibilidad: Excel 2007 y superior


VOLUMEN DE DATOS
================================================================================

Tipo de Dato              Cantidad    Tamaño
--------------------------------------------------------------------------------
Archivos CSV históricos   21          321 MB
Archivos XLSX históricos  16          369 MB
Período de datos          5 años      2020 Q2 - 2025 Q2
Registros de pedidos      Miles       Variable por trimestre


NOTAS IMPORTANTES
================================================================================

ORDEN DE EJECUCIÓN CRÍTICO
--------------------------------------------------------------------------------
1. NUNCA ejecutar el script 05 sin completar el mapeo de droguerías del
   paso 03
2. SIEMPRE ejecutar el script 06 ANTES de importar pedidos en Tracy
3. Los scripts 01-02 pueden ejecutarse en paralelo si se desea


PROBLEMA CONOCIDO: CUSTOMER LOCATION
--------------------------------------------------------------------------------
En agosto, los customer location erpid fueron sobrescritos por error en
Tracy. Por esto:
  - El script 06 es CRÍTICO
  - Debe ejecutarse antes de la importación de pedidos
  - Recupera los valores correctos mediante cruce de datos


DEPENDENCIAS DE SCRIPTS
--------------------------------------------------------------------------------
01 ──┐
02 ──┼─→ 03 → [MAPEO MANUAL] → 05 → IMPORTAR
     └─→ 06 ─────────────────────────↑


VALIDACIÓN MANUAL REQUERIDA
--------------------------------------------------------------------------------
Después de ejecutar el script 03:
  1. Abrir mapeo_droguerias_elvis_tracy.xlsx
  2. Revisar columna ELVIS
  3. Completar columna TRACY con valores correctos
  4. Guardar y cerrar el archivo
  5. Recién entonces ejecutar el script 05


ARCHIVOS DE ENTRADA REQUERIDOS
================================================================================

Obligatorios:
  - Base Elvis 2025.xlsx - Base completa de datos de Elvis
  - mapeo_droguerias_elvis_tracy.xlsx - Mapeo completado manualmente

Opcionales (para validación):
  - tracy.customer.locations.V2.csv
  - tracy.distributors.V2.csv
  - tracy.ecommerce.users.V2.csv
  - tracy.logistic.code.V2.csv


ARCHIVOS DE SALIDA GENERADOS
================================================================================

Intermedios:
  - clientes.elvis.csv - Clientes extraídos de Elvis
  - pedidos.elvis.YYYY.Qx.csv - 21 archivos de pedidos por trimestre
  - mapeo_droguerias_elvis_tracy.xlsx - Plantilla para mapeo (requiere llenado)

Finales (Para Importar en Tracy):
  - Tracy 2025.xlsx - Pedidos transformados listos para importar
  - 06 update phxId customer location.xlsx - Actualización de customer locations


SOLUCIÓN DE PROBLEMAS
================================================================================

Error: "No se encuentra Base Elvis 2025.xlsx"
--------------------------------------------------------------------------------
Causa:    El archivo de entrada no está en el directorio
Solución: Verificar que Base Elvis 2025.xlsx esté en la carpeta raíz del
          proyecto


Error: "KeyError en columna DROGUERIA"
--------------------------------------------------------------------------------
Causa:    El mapeo de droguerías no está completo
Solución: Abrir mapeo_droguerias_elvis_tracy.xlsx y completar la columna TRACY


Error: "No se encuentra la hoja 'Año 2020'"
--------------------------------------------------------------------------------
Causa:    El archivo Excel de Elvis tiene nombres de hojas diferentes
Solución: Verificar los nombres de las hojas en el Excel y ajustar el script
          si es necesario


Advertencia: "Valores faltantes en mapeo"
--------------------------------------------------------------------------------
Causa:    Hay droguerías en los datos que no están en el archivo de mapeo
Solución: Actualizar el archivo de mapeo ejecutando nuevamente el script 03


Error de memoria al procesar
--------------------------------------------------------------------------------
Causa:    Archivos muy grandes, memoria insuficiente
Solución: Usar las versiones optimizadas en backups/ que procesan por lotes


DOCUMENTACIÓN ADICIONAL
================================================================================

  - MAPEO_CAMPOS.md - Tabla completa de mapeo de campos
  - documentacion_mapeo_campos.xlsx - Documentación en formato Excel
  - Order History Import Guide.pdf - Guía oficial de importación de Tracy
  - mapeo_droguerias_elvis_tracy.pdf - Diagrama visual del mapeo
  - INFORME_PROGRESO.docx - Reporte de avance del proyecto
  - TODO.txt - Lista de tareas pendientes


HISTORIAL DE VERSIONES
================================================================================

Versiones en backups/:
  - transform_elvis_to_tracy.py - Versión duplicada
  - transform_elvis_to_tracy_optimized.py - Versión optimizada para grandes
                                             volúmenes
  - transform_elvis_to_tracy.backup.py - Backup de seguridad
  - process_tracy_files.py - Script auxiliar de procesamiento


CONTACTO Y SOPORTE
================================================================================

Para dudas sobre el proyecto, consultar:
  - INFORME_PROGRESO.docx - Estado actual del proyecto
  - TODO.txt - Tareas pendientes identificadas


CHECKLIST DE EJECUCIÓN COMPLETA
================================================================================

 [ ] 1. Ejecutar 01_extraer_clientes_elvis.py
 [ ] 2. Ejecutar 02_extraer_pedidos_elvis_por_trimestre.py
 [ ] 3. Ejecutar 03_generar_mapeo_droguerias.py
 [ ] 4. MANUAL: Completar columna TRACY en mapeo_droguerias_elvis_tracy.xlsx
 [ ] 5. (Opcional) Ejecutar 04_analizar_compatibilidad_campos.py para validar
 [ ] 6. Ejecutar 05_transformar_elvis_a_tracy.py
 [ ] 7. Verificar que Tracy 2025.xlsx se generó correctamente
 [ ] 8. Ejecutar 06_generar_actualizacion_customer_location.py
 [ ] 9. IMPORTAR EN TRACY: Primero 06 update phxId customer location.xlsx
 [ ] 10. IMPORTAR EN TRACY: Luego Tracy 2025.xlsx

================================================================================
Proyecto: Unilever - Compra Beauty Fase 2
Sistema Origen: Elvis
Sistema Destino: Tracy
Última actualización: Enero 2026
================================================================================
