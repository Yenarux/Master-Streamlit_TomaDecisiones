# Campañas bancarias: de los datos a la decisión

Aplicación académica de Streamlit con seis pasos (siete pestañas, ver más abajo), basada en Bank Marketing de UCI. Usa una traducción al español de la muestra de 4,521 registros.

Para entender las decisiones de diseño, consulta la [guía de replicación y decisiones de desarrollo](GUIA_REPLICACION.md).

**Pregunta guía:** ¿Qué clientes tienen mayor probabilidad de contratar un depósito a plazo y qué prioridad de contacto y mensaje inicial conviene asignarles?

**Momento de la decisión:** antes de iniciar una nueva campaña, utilizando características del cliente e historial anterior que se supone disponible y actualizado.

## Datos

La carpeta `data/` se incluye en el repositorio:

```text
data/bank_espanol_comas.csv    Archivo que lee la app (separador coma)
data/bank_espanol.csv          Misma traducción con separador punto y coma (;)
```

- Fuente original: [Bank Marketing, UCI](https://archive.ics.uci.edu/dataset/222/bank+marketing) (archivo `bank.csv`, 4,521 registros), de uso público.
- La app solo lee `bank_espanol_comas.csv`, en español, con estas 17 columnas exactamente: Edad, Ocupación, Estado civil, Nivel educativo, Crédito en incumplimiento de pago, Saldo promedio anual en euros, Préstamo para vivienda, Préstamo personal, Medio de contacto, Día del último contacto, Mes del último contacto, Duración del último contacto en segundos, Contactos durante la campaña actual, Días desde el contacto de una campaña anterior, Contactos anteriores a la campaña actual, Resultado de la campaña anterior y Contrató el depósito a plazo.
- Las categorías también están traducidas (por ejemplo, `Sí`/`No`, `Desconocido`, `Teléfono celular`). La app no incluye un traductor: si usas el original en inglés, debes traducir encabezados y categorías.

## Abrir la aplicación

Desde PowerShell, **dentro de esta carpeta** (la app lee `data/...` con ruta relativa):

```powershell
python -m venv bank_stream
.\bank_stream\Scripts\python.exe -m pip install -r requirements.txt
.\bank_stream\Scripts\python.exe -m streamlit run app.py
```

Si el entorno ya existe, basta con la última línea. Abre la dirección local que muestre la terminal, normalmente http://localhost:8501. No hace falta una llave API ni un servicio externo.

Versiones con las que se desarrolló: Python 3.14, Streamlit 1.66.0, pandas 3.0.6, NumPy 2.5.4 y scikit-learn 1.9.1.

## Estructura

```text
app.py                         Interfaz: configura la página y llama a cada pestaña
banco.py                       Limpieza, validaciones, modelo y política de prioridad
requirements.txt               Dependencias
tabs/
├── entender.py                1. Entender los datos
├── limpiar.py                 2. Limpiar los datos
├── descriptiva.py             3. Estadística descriptiva
├── predictiva.py              4. Estadística predictiva
├── prescriptiva.py            5. Estadística prescriptiva
├── decisiones.py              6. Toma de decisiones
└── decisiones_modificada.py   6. Toma de decisiones - modificada (con explicaciones para público no técnico)
data/                          Datos de entrada (CSV en español)
```

Cada pestaña es un archivo con una función `mostrar(...)`; `app.py` solo las invoca y pasa los resultados de una a otra (limpieza → descriptiva y predictiva → prescriptiva → decisiones).

## Las pestañas

| Pestaña | Pregunta | Contenido |
|---|---|---|
| 1. Entender | ¿Qué sabemos de estos casos? | Contexto, fuente, vista previa, diccionario con el uso de cada variable, diagnóstico y explorador de variables. |
| 2. Limpiar | ¿Qué tan confiables son los datos? | Validaciones, vacíos, desconocidos, decisiones de limpieza, antes/después y descargas. |
| 3. Describir | ¿Cómo cambia la contratación por segmento? | Tasa general, ocupación, grupos de edad y selector de otros segmentos, siempre con tamaño de grupo. |
| 4. Predecir | ¿Podemos estimar quién contratará? | Regresión logística, prueba reservada, referencia «siempre No», métricas, matriz de confusión y coeficientes. |
| 5. Prescribir | ¿Qué acción proponer para cada nivel? | Cortes de prioridad ajustables, tabla de acciones, resultados por prioridad y descarga. |
| 6. Decidir | ¿Qué hacemos y qué mensaje proponemos? | Selector de prioridad, evidencia, acción, mensaje, justificación y límites. |
| 6. Decidir (modificada) | Igual, explicada para quien no conoce estadística | Añade introducción, qué es la prioridad y cómo se eligieron los cortes, qué significa el 50% y una justificación en palabras sencillas. |

## Reglas de limpieza

- **Desconocido:** se conserva como categoría; no equivale a No ni a fracaso.
- **Días = -1:** significa que no hubo contacto anterior. Se cambia a un vacío y se crea el indicador «Tuvo contacto en una campaña anterior». En el modelo ese vacío se representa con 0 acompañado del indicador.
- **Saldo negativo:** se conserva; no es un error por sí mismo.
- **Filas idénticas:** se cuentan y conservan; no hay identificador único para tratarlas como personas duplicadas.
- **Duración:** se conserva para describir y se excluye del modelo (se conoce después de la llamada). También se excluyen medio, día, mes y contactos de la campaña actual.
- **Validación:** columnas, tipos, categorías Sí/No y rangos básicos. Si falla alguna, la pestaña 2 detiene la app para revisión; no se eliminan filas automáticamente.

## Modelo y evaluación

Regresión logística sin balanceo artificial de clases. La prueba reservada (~20%, semilla 42) se obtiene con `StratifiedGroupKFold` de cinco grupos, usando solo la primera partición; las filas idénticas quedan del mismo lado. El escalado y la codificación se ajustan solo con entrenamiento.

Las métricas de prueba se comparan con una referencia que siempre predice No. La clasificación Sí/No usa un corte fijo de 50% para **evaluar**; los cortes de prioridad (10% y 25% por defecto) son supuestos operativos ilustrativos, sin optimizar con costos ni capacidad. Los coeficientes son asociaciones, no causas.

## Fuente y límites

Moro, S., Laureano, R. y Cortez, P. (2011). Using Data Mining for Bank Direct Marketing: An Application of the CRISP-DM Methodology. En Proceedings of ESM'2011, pp. 117–121. EUROSIS.

La muestra corresponde a campañas de un banco portugués (el conjunto completo abarca de mayo de 2008 a noviembre de 2010). No representa clientes actuales de México. No permite probar qué mensaje funciona, estimar rentabilidad ni demostrar el efecto causal de contactar: los mensajes de la app son propuestas informativas para un piloto.
