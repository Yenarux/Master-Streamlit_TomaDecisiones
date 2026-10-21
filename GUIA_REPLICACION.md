# Guía de replicación y decisiones de desarrollo

**Proyecto:** Campañas bancarias: de los datos a la decisión  
**Documentación de la versión revisada:** 18 de octubre de 2026  
**Tecnología:** Python y Streamlit  
**Dataset:** Bank Marketing, UCI; muestra de 4,521 registros traducida al español.

Este documento explica cómo reproducir la aplicación, cómo se prepararon los datos, por qué se tomaron las decisiones del análisis y qué comprobar al modificar el proyecto. Describe la implementación existente en `app.py` y `banco.py`; los resultados numéricos se recalcularon para documentar esta versión.

> **Nota sobre el estado actual del repositorio.** Esta guía documenta el diseño y las decisiones del análisis. La implementación publicada difiere en lo siguiente; para ejecutar la app, sigue el [README](README.md):
>
> - La lógica está en `banco.py` y cada pestaña en su propio archivo dentro de `tabs/`; `app.py` solo las invoca. Hay una séptima pestaña, «6. Toma de decisiones - modificada».
> - La app lee `data/bank_espanol_comas.csv` (separador coma), no `bank_espanol.csv`. Ambos CSV se incluyen en `data/`; `bank-names.txt` no está en esta carpeta.
> - **No incluidos** en este repositorio: `preparar_datos.py`, `requirements-lock.txt`, `output/`, `evidencias/` y `tests/`. Las secciones 4.3, 4.4, 12, 16 y 18 que los mencionan describen una versión planeada.
> - El entorno virtual se llama `bank_stream`, no `.venv`. El desarrollo usó Python 3.14.8 y pandas 3.0.6 (las versiones de la sección 4.2 corresponden a la versión planeada).
> - La limpieza se calcula desde el CSV original en la pestaña 2 y se ofrecen descargas desde la app.

## 1. Propósito y alcance

La pregunta guía es:

> ¿Qué clientes tienen mayor probabilidad de contratar un depósito a plazo y qué prioridad de contacto y mensaje inicial conviene asignarles?

La decisión se sitúa **antes de iniciar una nueva campaña**. Se supone que las características del cliente y el historial de campañas anteriores están disponibles y actualizados. Esta definición determina qué variables pueden entrar al modelo.

El recorrido es:

```text
Entender → Limpiar → Describir → Predecir → Prescribir → Decidir
```

El proyecto comenzó explorando abandono escolar, pero la elección final fue Bank Marketing. Los archivos escolares que pudieran permanecer en la carpeta raíz no forman parte del procesamiento de esta app.

La aplicación es un ejercicio académico de apoyo a decisiones. No ejecuta contactos, envía mensajes ni se conecta a clientes reales. Tampoco prueba que una acción o mensaje aumente la contratación.

## 2. Origen, traducción y archivo de entrada

Según `data/bank-names.txt`, los datos corresponden a campañas telefónicas de un banco de Portugal. El archivo `bank.csv` es una muestra de 4,521 registros seleccionados aleatoriamente del conjunto completo de 45,211. La documentación sitúa el conjunto completo entre mayo de 2008 y noviembre de 2010.

El archivo original tiene 16 variables explicativas y una de resultado. Se tradujeron los encabezados y las categorías al español, conservando números, orden de registros y valores especiales. La traducción no convierte el dataset en información de México.

La aplicación consume únicamente:

```text
data/bank_espanol.csv
```

Características de lectura:

| Elemento | Configuración |
|---|---|
| Separador | Punto y coma: `;` |
| Codificación | `utf-8-sig`, compatible con UTF-8 con marca BOM |
| Encabezados | Nombres descriptivos en español |
| Resultado | `Contrató el depósito a plazo`, con valores `Sí` y `No` |
| Unidad de análisis | Registro de campaña asociado a un cliente; no hay un identificador único de persona |

Si existe una variante `bank_espanol_comas.csv`, no debe copiarse a la ruta de entrada sin adaptar también la lectura. El archivo limpio tampoco reemplaza al original: ya contiene transformaciones y vacíos estructurales que la validación de entrada trata de forma diferente.

Para reproducir exactamente esta versión, conserva el CSV traducido incluido en `data/`, además del código. Descargar nuevamente la fuente en inglés requiere repetir el mapeo de encabezados y categorías; la app no incluye un traductor automático.

Huella SHA-256 del CSV de entrada revisado:

```text
c91b23aadb3b69d0628aa47435454552bc38858c769f3bdd3fb122148fb0df4b
```

Compruébala en PowerShell, desde la carpeta del proyecto:

```powershell
Get-FileHash -LiteralPath .\data\bank_espanol.csv -Algorithm SHA256
```

Una huella distinta indica que los bytes cambiaron; revisa si se modificó solo el formato o también el contenido antes de comparar resultados.

## 3. Archivos y responsabilidades

```text
carpeta_del_proyecto/
├── app.py
├── banco.py
├── preparar_datos.py
├── requirements.txt
├── requirements-lock.txt
├── README.md
├── GUIA_REPLICACION.md
├── .gitignore
├── data/
│   ├── bank_espanol.csv
│   └── bank-names.txt
├── output/
│   ├── bank_limpio.csv
│   ├── diagnostico_calidad.csv
│   └── transformaciones.csv
├── evidencias/
│   └── GUIA.md
└── tests/
    └── test_framework.py
```

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Interfaz, seis pestañas, gráficas, métricas, controles, descargas y recordatorios de evidencias. |
| `banco.py` | Diccionario, lectura, limpieza, resúmenes, entrenamiento, evaluación y política de prioridad. |
| `preparar_datos.py` | Exportar la copia limpia y los diagnósticos a `output/`. |
| `requirements.txt` | Rangos de dependencias permitidas para una instalación compatible. |
| `requirements-lock.txt` | Versiones exactas instaladas al desarrollar esta versión, incluidas dependencias indirectas. |
| `tests/test_framework.py` | Verificación de reglas de datos, separación de prueba e interacciones. |
| `evidencias/GUIA.md` | Relación entre el proyecto y los siete momentos de la tarea. |

Separar interfaz y análisis permite cambiar textos o diseño sin reescribir el modelo y verificar las reglas de datos sin abrir el navegador.

## 4. Replicación en otro equipo

### 4.1 Preparación

1. Copia o descarga los archivos del proyecto conservando su estructura.
2. Abre PowerShell en esa carpeta.
3. Comprueba Python con `python --version` o `py --version`.
4. Para aproximarte al entorno original, utiliza **Python 3.12**. La ejecución documentada utilizó **Python 3.12.13** en Windows.

No copies la carpeta `.venv` entre equipos: contiene rutas y componentes propios de la instalación. Créala de nuevo. La instalación de dependencias requiere acceso a internet; ejecutar el análisis con el CSV local no necesita servicios externos ni llaves API.

### 4.2 Crear el entorno e instalar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Si el comando disponible es `py`, utiliza `py -3.12 -m venv .venv` en el primer paso.

Las versiones principales de la ejecución revisada fueron:

| Paquete | Versión |
|---|---|
| Streamlit | 1.66.0 |
| pandas | 2.3.3 |
| NumPy | 2.5.4 |
| scikit-learn | 1.9.1 |

Si las versiones fijadas no están disponibles para tu plataforma o necesitas adaptar dependencias, instala los rangos de `requirements.txt` y vuelve a ejecutar las verificaciones. Eso crea una variante del entorno, por lo que podrían cambiar algunos resultados. No se comprobó esta versión en otros sistemas operativos.

### 4.3 Generar archivos de limpieza

```powershell
.\.venv\Scripts\python.exe preparar_datos.py
```

Se generan o sobrescriben los archivos derivados de `output/`. No se sobrescribe el CSV de entrada.

### 4.4 Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

El resultado esperado para el dataset incluido es **seis pruebas correctas** y el mensaje final `OK`.

### 4.5 Abrir Streamlit

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre la dirección que indique la terminal, normalmente `http://localhost:8501`. Mantén esa terminal abierta mientras usas la app. Para detenerla, pulsa `Ctrl+C` en esa terminal.

Opcionalmente puedes activar el entorno para que su nombre aparezca en la terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

La ejecución directa mediante `.venv\Scripts\python.exe` evita depender de la activación si PowerShell restringe scripts. Para la evidencia académica del entorno activo, utiliza una activación permitida por la configuración de tu equipo.

## 5. Diagnóstico del dataset revisado

| Comprobación | Resultado |
|---|---:|
| Registros originales | 4,521 |
| Columnas originales | 17 |
| Columnas después de limpiar | 18 |
| Resultado Sí | 521 (11.52%) |
| Resultado No | 4,000 (88.48%) |
| Celdas vacías originales | 0 |
| Celdas con Desconocido | 5,254 |
| Filas idénticas adicionales | 0 |
| Saldos negativos | 366 |
| Registros con días = -1 | 3,705 |

Distribución de información desconocida:

| Variable | Registros con Desconocido |
|---|---:|
| Ocupación | 38 |
| Nivel educativo | 187 |
| Medio de contacto | 1,324 |
| Resultado de la campaña anterior | 3,705 |

Estos conteos describen el archivo revisado. No deben imponerse como resultados esperados si sustituyes el dataset por otra muestra.

## 6. Decisiones de limpieza y su justificación

### 6.1 Preservar el original

`clean_data()` trabaja sobre una copia. No elimina filas ni modifica el DataFrame original. Las transformaciones permiten conservar trazabilidad y comparar antes y después.

Las cadenas se normalizan quitando espacios exteriores. Las cadenas vacías se representan como datos ausentes. Las columnas numéricas se convierten explícitamente y los valores no interpretables detienen la preparación para revisión.

### 6.2 Desconocido no significa No

Se conserva como categoría explícita: representa información no disponible. No se transforma en una respuesta negativa ni en fracaso, y no se eliminan todas las filas que la contienen. Los vacíos de las variables categóricas utilizadas por el modelo también se completan con `Desconocido`.

Eliminar automáticamente esos registros reduciría la muestra y podría cambiar su composición. Conservar la categoría permite observar la ausencia de información, aunque no resuelve sus posibles sesgos.

### 6.3 Días = -1 es un caso de no aplicación

La fuente define `-1` como ausencia de contacto en una campaña anterior. Por ello:

1. Se crea `Tuvo contacto en una campaña anterior`, con valor Sí o No.
2. El `-1` se sustituye por un vacío estructural en la columna de días.
3. Ese vacío permanece vacío en la exportación limpia.
4. Solo al preparar el modelo se usa un marcador numérico 0, acompañado por el indicador de contacto.

El marcador no afirma que una persona sin contacto haya sido contactada hace cero días. El indicador permite distinguirla de un caso con contacto previo y cero días reales. Tampoco se calcula una media de días que mezcle el `-1` con intervalos válidos.

### 6.4 Los saldos negativos se conservan

Un saldo negativo es un valor posible. No existe una justificación para sustituirlo por cero o eliminar su registro solo por el signo. La limpieza tampoco recorta automáticamente valores extremos.

### 6.5 Las filas idénticas se revisan antes de eliminar

Sin un identificador único, dos filas iguales podrían representar casos distintos con las mismas características. La versión actual no contiene filas idénticas, pero el código las cuenta y las conservaría.

Al separar entrenamiento y prueba, las filas completamente idénticas se agrupan para que queden en el mismo lado. Esto no controla todas las apariciones posibles de una misma persona: para eso harían falta identificadores adecuados.

### 6.6 La duración se conserva para describir y se excluye para predecir

La duración se conoce después de la llamada. Utilizarla para elegir a quién llamar incorporaría información que todavía no está disponible al decidir.

También se excluyen el medio, día y mes del último contacto y los contactos de la campaña actual, porque el escenario elegido es anterior al inicio de esa campaña. Estas son decisiones de selección de predictores, no correcciones de datos sucios.

### 6.7 Validaciones implementadas

Se comprueba la presencia de las columnas esperadas, valores numéricos finitos, ausencia de vacíos en las columnas numéricas originales y resultado Sí/No. También se revisan las categorías Sí/No de los tres indicadores de crédito y préstamo.

Se validan edades entre 18 y 120, días del mes entre 1 y 31, al menos un contacto de campaña actual, duración y contactos anteriores no negativos y días desde contacto no menores que -1. Son controles básicos de esta implementación, no una auditoría exhaustiva de todas las relaciones entre variables. Por ejemplo, no se implementó una validación completa de coherencia entre días, número de contactos y resultado anterior.

## 7. Qué construye cada pestaña

| Pestaña | Propósito y componentes | Consideración principal |
|---|---|---|
| 1. Entender | Pregunta, contexto, fuente, filas y columnas, contrataciones, vista previa y diccionario con función de cada variable. | Una fila no equivale necesariamente a una persona única. |
| 2. Limpiar | Conteos de vacíos, desconocidos y duplicados; decisiones, transformaciones, antes/después y descargas. | Los vacíos estructurales no son errores de captura. |
| 3. Describir | Tasa general, contrataciones, mediana del saldo, gráficas por ocupación y edad y selector de otros segmentos. | Mostrar denominadores y separar asociación de causalidad. |
| 4. Predecir | Regresión logística, predictores, exclusiones, partición de datos, métricas, referencia, matriz de confusión y coeficientes. | Evaluar con datos que el modelo no utilizó para aprender. |
| 5. Prescribir | Cortes ajustables, tabla de acciones, resumen de prioridades y descarga de casos de prueba. | Los cortes son supuestos operativos ilustrativos. |
| 6. Decidir | Selector de prioridad, acción, mensaje, tamaño del grupo, probabilidades, resultados observados, justificación y límites. | La eficacia de los mensajes aún debe probarse. |

Los grupos de edad son 18–29, 30–44, 45–59 y 60 o más. Los comentarios automáticos sobre el grupo con mayor tasa consideran solo grupos con al menos 30 casos. Ese mínimo es una regla descriptiva de prudencia, no una garantía de significancia estadística.

Los filtros descriptivos no modifican el entrenamiento. Las pestañas 5 y 6 comparten los cortes elegidos y las mismas probabilidades reservadas.

## 8. Entrenamiento y prevención de filtración de información

### 8.1 Variables del modelo

Predictores numéricos:

- Edad.
- Saldo promedio anual en euros.
- Días desde el contacto de una campaña anterior.
- Contactos anteriores a la campaña actual.

Predictores categóricos:

- Ocupación.
- Estado civil.
- Nivel educativo.
- Crédito en incumplimiento de pago.
- Préstamo para vivienda.
- Préstamo personal.
- Resultado de la campaña anterior.
- Tuvo contacto en una campaña anterior.

El resultado se transforma a 1 para Sí y 0 para No. Nunca se incluye entre los predictores. Las variables demográficas se utilizan en el ejercicio, pero su necesidad y sus posibles sesgos deben revisarse antes de un uso real.

### 8.2 Separación de entrenamiento y prueba

Se usa `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` y se toma **solo la primera partición**. No se promedian resultados de las cinco particiones: la implementación usa esta herramienta para crear una prueba reservada de aproximadamente 20%, manteniendo grupos de filas idénticas y buscando conservar las proporciones Sí/No.

En esta versión quedaron:

| Conjunto | Registros |
|---|---:|
| Entrenamiento | 3,617 |
| Prueba | 904 |

El agrupamiento identifica filas completas iguales mediante un hash. Es una protección contra duplicados exactos, no una identificación de clientes. Si cambia el archivo, su orden o las versiones de las librerías, revisa nuevamente la partición y los resultados.

### 8.3 Preparación dentro del modelo

Un `ColumnTransformer` y un `Pipeline` mantienen juntas las transformaciones y la regresión:

1. Marcador constante 0 para vacíos numéricos estructurales.
2. Escalado numérico con `StandardScaler`.
3. Codificación categórica con `OneHotEncoder(handle_unknown="ignore", drop="first")`.
4. Regresión logística con `max_iter=2000` y `random_state=42`; los demás parámetros usan los valores predeterminados de la versión instalada.

El escalado y la codificación se ajustan únicamente con entrenamiento. La limpieza previa aplica reglas fijas del significado de los datos y no aprende medias o frecuencias de toda la muestra. Así se evita que estadísticas de prueba entren a la preparación aprendida.

No se aplicaron sobremuestreo ni ponderación de clases. Se conservó una primera referencia sencilla y se hizo visible la dificultad de identificar la clase minoritaria. Esta decisión no garantiza probabilidades bien calibradas ni que sea el mejor modelo posible.

### 8.4 Referencia y corte de clasificación

El modelo se compara con una referencia que predice siempre No. Para las métricas basadas en probabilidades, esa referencia asigna la frecuencia de Sí del entrenamiento como probabilidad constante.

La clasificación Sí/No de la evaluación utiliza un corte fijo de **50%**. Los cortes operativos de **10% y 25%** de la pestaña 5 tienen otro propósito: organizar prioridades. No hay que confundirlos.

## 9. Resultados de referencia y su interpretación

Resultados recalculados con el CSV y entorno documentados:

| Métrica en prueba | Regresión logística | Referencia: siempre No |
|---|---:|---:|
| Exactitud | 89.49% | 88.50% |
| Precisión de Sí | 68.00% | 0.00% |
| Sensibilidad de Sí | 16.35% | 0.00% |
| F1 de Sí | 0.2636 | 0.0000 |
| ROC AUC | 0.7044 | 0.5000 |
| Precisión promedio (AP) | 0.3456 | 0.1150 |

La precisión de la referencia se reporta como cero por la convención `zero_division=0`: nunca predice Sí.

Matriz de confusión con corte de 50%:

| Resultado real | Predicho No | Predicho Sí |
|---|---:|---:|
| No | 792 | 8 |
| Sí | 87 | 17 |

El modelo identificó 17 de los 104 Sí reales de prueba y omitió 87. Una exactitud cercana al 89% no significa que detecte al 89% de quienes contratarán. La mejora de exactitud respecto de siempre No es pequeña y debe interpretarse junto con sensibilidad, precisión y métricas de ordenación.

Los coeficientes describen asociaciones condicionadas. Los numéricos están escalados y las categorías se comparan con una referencia omitida. Sus magnitudes no son efectos causales ni una medida universal de importancia.

## 10. De probabilidades a prioridades y mensajes

La regla inicial es:

| Prioridad | Probabilidad estimada | Acción propuesta |
|---|---|---|
| Baja | Menos de 10% | Información disponible a solicitud, evitando contactos insistentes. |
| Media | Desde 10% y menos de 25% | Información educativa y seguimiento con autorización. |
| Alta | Desde 25% | Priorizar una invitación informativa y ofrecer asesoría si la persona acepta. |

Los mensajes están definidos en `POLICY`, dentro de `banco.py`. Son propuestas redactadas para el ejercicio; el dataset no contiene evidencia de que esos textos funcionen mejor.

Con los cortes predeterminados, el resumen de prueba fue:

| Prioridad | Casos | Contrataciones observadas | Probabilidad media estimada | Tasa observada |
|---|---:|---:|---:|---:|
| Alta | 47 | 26 | 47.95% | 55.32% |
| Media | 343 | 44 | 14.23% | 12.83% |
| Baja | 514 | 34 | 6.99% | 6.61% |

La prioridad se asigna únicamente con la probabilidad. El resultado real aparece para evaluar retrospectivamente el grupo, pero no se usa para decidir su prioridad. La columna `Fila del CSV` señala la posición para inspección, contando el encabezado; no identifica una persona.

Los cortes no se optimizaron con costos, capacidad ni rentabilidad. Si se ajustan repetidamente mirando esta prueba, ya no se puede afirmar que ella valida de forma independiente la política elegida. Para optimizar, separa entrenamiento, validación y una prueba final nueva.

## 11. Descargas, caché y comportamiento de ejecución

La app calcula la limpieza desde el original y genera descargas en memoria. `preparar_datos.py` permite guardar archivos derivados en disco. Las prioridades se descargan desde la pestaña 5 y corresponden solo a los casos de prueba; no se guardan automáticamente en `output/`.

`prepare()` usa `st.cache_data` para reutilizar los datos preparados y `train()` usa `st.cache_resource` para reutilizar el resultado del entrenamiento. Al cambiar controles, la interfaz se vuelve a ejecutar, pero no necesita entrenar el modelo en cada interacción.

**Si sustituyes el CSV mientras la app está abierta, detén y reinicia Streamlit.** La función de carga está cacheada sin un argumento de fecha o huella del archivo; reemplazar el contenido por sí solo puede no invalidar esa caché. También reinicia tras cambios importantes en la lógica y revisa los resultados antes de tomar capturas.

El modelo no se exporta a un archivo persistente ni hay un formulario para puntuar clientes nuevos. Al iniciar una sesión nueva del servidor, puede volver a entrenarse. Esas funciones serían extensiones futuras.

## 12. Verificaciones realizadas

Las seis pruebas automatizadas cubren:

1. Conservación del original, número de registros, resultado y valores especiales; duración fuera de los predictores.
2. Filas idénticas en un único lado de la separación, usando duplicados añadidos expresamente a la prueba.
3. Entrenamiento y prueba sin índices compartidos, probabilidades entre 0 y 1 y matriz de confusión con el total correcto.
4. Fronteras de prioridad y asignación independiente del resultado real.
5. Rechazo de ejemplos con edad inválida o resultado desconocido.
6. Ejecución de las seis pestañas con `AppTest`, cambios de selectores y cortes, incluidos cortes iguales.

Durante el desarrollo, la creación del entorno requirió resolver un permiso de acceso temporal y la instalación de dependencias requirió acceso a red. Las primeras ejecuciones de Streamlit y `AppTest` se bloquearon dentro del entorno restringido de la herramienta porque necesitan conexiones locales internas. Al ejecutarlas con autorización fuera de esa restricción, las seis pruebas terminaron correctamente. Esto describe el entorno de desarrollo, no un error del CSV.

No se realizó una validación con clientes actuales, calibración independiente ni experimento comercial. Las pruebas automatizadas comprueban comportamientos del código; no demuestran que el modelo sea adecuado para producción.

## 13. Problemas frecuentes al replicar

| Problema | Qué revisar |
|---|---|
| Python no se reconoce | Comprueba la instalación y prueba `py --version`; para esta réplica usa Python 3.12. |
| No se puede activar el entorno | Usa directamente `.\.venv\Scripts\python.exe`; no necesitas modificar la política global para ejecutar. |
| Falla la instalación | Revisa red, permisos y disponibilidad de las versiones para tu plataforma. Conserva el mensaje antes de cambiar dependencias. |
| No encuentra el CSV | Comprueba `data/bank_espanol.csv` dentro del proyecto. La ruta de lectura se calcula desde `banco.py`. |
| Faltan columnas o todo aparece en una columna | Comprueba que sea la versión española y que utilice `;`. |
| Datos numéricos vacíos después de reemplazar la entrada | Verifica que no estés usando `bank_limpio.csv` como original: sus días vacíos son una transformación posterior. |
| La app muestra datos anteriores | Reinicia el servidor para invalidar la carga cacheada. |
| El puerto está ocupado | Abre la instancia existente o ejecuta `python -m streamlit run app.py --server.port 8502` desde el entorno. |
| El navegador no conecta | Mantén la terminal abierta y utiliza la URL que realmente muestra; revisa las restricciones locales de conexiones. |
| Una prioridad queda vacía | Es posible con ciertos cortes; la app lo indica y no inventa métricas para ese grupo. |
| Las pruebas fallan con otro dataset | Algunas verifican los 4,521 registros y 521 Sí de la muestra original. Adáptalas al nuevo contrato de datos y vuelve a validar la partición. |

## 14. Cómo adaptar el framework

Para otro dataset, sigue este orden:

1. Define la unidad de análisis, resultado y momento exacto de la decisión.
2. Documenta procedencia, categorías, valores especiales y datos disponibles antes del resultado.
3. Adapta `load_data()`, `MEANINGS`, `TARGET` y las listas de variables.
4. Reescribe las reglas de `clean_data()` según el nuevo significado; no heredes automáticamente las de este banco.
5. Ajusta la separación: por persona, grupo o periodo si esos identificadores existen.
6. Revisa gráficas, métricas, desbalance, calibración y disponibilidad temporal de los predictores.
7. Define acciones y cortes en función de una decisión real; prueba los mensajes por separado.
8. Actualiza pruebas, documentación, versiones y evidencias.

Cambios frecuentes en este proyecto:

| Quieres modificar… | Ubicación |
|---|---|
| Títulos, pregunta y explicaciones | `app.py` |
| Reglas de limpieza | `clean_data()` en `banco.py` |
| Variables del modelo | `NUM_FEATURES`, `CAT_FEATURES` y `EXCLUDED` en `banco.py`; mantener consistencia con la interfaz |
| Modelo o evaluación | `fit_model()` en `banco.py` |
| Acciones y mensajes | `POLICY` en `banco.py` |
| Cortes iniciales de la app | Valor inicial del slider en `app.py`; alinear también valores predeterminados de `assign_priority()` y documentación |
| Exportación a disco | `preparar_datos.py` |

## 15. Límites y validación futura

Antes de un uso real haría falta atender al menos estos puntos:

- **Actualidad y contexto:** validar con datos recientes del banco y una separación temporal. Portugal en 2008–2010 no representa automáticamente otro país o periodo.
- **Información de cliente:** comprobar que los atributos supuestamente disponibles antes de la campaña realmente lo estén y estén actualizados.
- **Identidad de casos:** utilizar identificadores seudónimos para controlar múltiples registros de una misma persona.
- **Sesgos:** evaluar errores y resultados por grupo y revisar la necesidad de edad, educación, estado civil y ocupación.
- **Calibración y política:** validar probabilidades y elegir cortes con datos independientes, costos y capacidad operativa.
- **Eficacia de acciones:** diseñar un piloto o experimento; una mayor propensión histórica no equivale a un mayor efecto de contactar.
- **Privacidad y preferencias:** minimizar datos, limitar accesos y respetar autorizaciones y solicitudes de no contacto. Una prioridad baja no debe restringir el acceso al producto o a asesoría.

## 16. Evidencias y entrega académica

La app ayuda a documentar siete momentos: entorno, primera ejecución, comprensión, error o decisión técnica, limpieza y descripción, conexión con la decisión y reflexión final. Consulta `evidencias/GUIA.md` para la captura y las preguntas de cada momento.

Cada explicación debe tener 80 a 120 palabras y acompañar una captura real y verificable. La decisión de excluir duración puede servir para el momento 4 sin inventar errores. Si utilizaste IA para generar código, indícalo y explica qué comprobaste.

La entrega solicita un PDF con portada y nombre completo, contexto en una línea, los siete momentos en orden y enlace al repositorio público. También pide una revisión de la última pestaña por un compañero y un cambio documentado a partir de su comentario.

El PDF final, las capturas personales, la revisión del compañero y la publicación del repositorio son actividades pendientes de la entrega; esta guía no afirma que ya se hayan realizado.

Para compartir la réplica, incluye código, dependencias, CSV y documentación. `.gitignore` excluye `.venv`, archivos temporales, cachés y secretos habituales. Si publicas el proyecto, revisa los archivos que realmente vas a incluir; no copies credenciales ni datos personales.

## 17. Referencias y materiales del proyecto

- [Dataset Bank Marketing en UCI](https://archive.ics.uci.edu/dataset/222/bank+marketing).
- Documentación de la fuente incluida: `data/bank-names.txt`.
- Moro, S., Laureano, R. y Cortez, P. (2011). *Using Data Mining for Bank Direct Marketing: An Application of the CRISP-DM Methodology*. Proceedings of ESM’2011, pp. 117–121. EUROSIS.
- [Guía breve del proyecto](README.md).
- [Guía para las evidencias](evidencias/GUIA.md).

## 18. Lista final para comprobar una réplica

- [ ] El CSV de entrada y sus categorías corresponden a esta versión.
- [ ] El entorno se creó en el equipo destino y se registraron sus versiones.
- [ ] Se ejecutó `preparar_datos.py` y se conserva el original.
- [ ] El limpio tiene 4,521 filas y 18 columnas con esta muestra.
- [ ] Las seis pruebas terminan correctamente.
- [ ] Las seis pestañas abren y los controles responden.
- [ ] La evaluación usa 3,617 casos de entrenamiento y 904 de prueba con esta configuración.
- [ ] Se distingue el corte de clasificación del 50% de los cortes operativos del 10% y 25%.
- [ ] Se interpretan la baja sensibilidad, los tamaños de grupo y los límites del análisis.
- [ ] Las evidencias y reflexiones de la entrega proceden de una ejecución real.
