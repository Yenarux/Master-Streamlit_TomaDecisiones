import streamlit as st
import pandas as pd

from banco import (
    TARGET, NUM_FEATURES, CAT_FEATURES, EXCLUDED, DURACION, DESCONOCIDO,
    DIAS_PREVIO, TUVO_CONTACTO,
)

# Qué significa cada variable y qué papel cumple en el análisis.
DICCIONARIO = {
    "Edad": "Edad del cliente en años.",
    "Ocupación": "Tipo de trabajo del cliente.",
    "Estado civil": "Estado civil del cliente.",
    "Nivel educativo": "Nivel de estudios alcanzado.",
    "Crédito en incumplimiento de pago": "Si tiene un crédito en incumplimiento.",
    "Saldo promedio anual en euros": "Saldo promedio anual; puede ser negativo.",
    "Préstamo para vivienda": "Si tiene un préstamo para vivienda.",
    "Préstamo personal": "Si tiene un préstamo personal.",
    "Medio de contacto": "Medio usado en el último contacto.",
    "Día del último contacto": "Día del mes del último contacto.",
    "Mes del último contacto": "Mes del último contacto.",
    "Duración del último contacto en segundos": "Duración de la llamada; solo se conoce después de ella.",
    "Contactos durante la campaña actual": "Número de contactos en la campaña actual.",
    "Días desde el contacto de una campaña anterior": "-1 significa que no hubo contacto anterior.",
    "Contactos anteriores a la campaña actual": "Contactos realizados antes de esta campaña.",
    "Resultado de la campaña anterior": "Resultado de la campaña previa; Desconocido si no aplica o no se conoce.",
    "Contrató el depósito a plazo": "Resultado a estudiar: Sí o No.",
}


def _rol(variable):
    if variable == TARGET:
        return "Resultado"
    if variable == DURACION:
        return "Solo exploración (se conoce después de la llamada)"
    if variable in EXCLUDED:
        return "Excluida (corresponde a la campaña actual)"
    if variable in NUM_FEATURES or variable in CAT_FEATURES:
        return "Predictor"
    return "Otro"


def mostrar(df):

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("1. Entender los datos")

    st.markdown("""
    ### Pregunta inicial

    **¿Qué clientes tienen mayor probabilidad de contratar un depósito a plazo?**

    La decisión se plantea **antes de iniciar una nueva campaña**, con las características del cliente
    y el historial anterior que se supone disponible.
    """)

    st.info(
        "Fuente: Bank Marketing (UCI), campañas telefónicas de un banco de Portugal. "
        "Es una muestra de 4,521 registros del conjunto completo de 45,211 (2008–2010), "
        "traducida al español. No representa clientes actuales de México. "
        "Cada fila es un registro de campaña, no necesariamente una persona única."
    )

    # ----------------------------------
    # DIMENSIONES DEL DATASET
    # ----------------------------------

    contrataron = (df[TARGET] == "Sí").sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de registros", f"{len(df):,}")

    with col2:
        st.metric("Número de variables", len(df.columns))

    with col3:
        st.metric("Contrataron el depósito", f"{contrataron:,} ({contrataron / len(df):.1%})")

    # ----------------------------------
    # VISTA PREVIA
    # ----------------------------------

    st.subheader("Vista previa del dataset")
    st.dataframe(df.head(10), width='stretch')

    # ----------------------------------
    # DICCIONARIO
    # ----------------------------------

    st.subheader("Diccionario de variables")

    diccionario = pd.DataFrame({
        "Variable": df.columns,
        "Descripción": [DICCIONARIO.get(c, "") for c in df.columns],
        "Uso en el análisis": [_rol(c) for c in df.columns],
    })
    st.dataframe(diccionario, width='stretch', hide_index=True)

    # ----------------------------------
    # DIAGNÓSTICO
    # ----------------------------------

    st.subheader("Diagnóstico del dataset")

    diagnostico = pd.DataFrame({
        "Variable": df.columns,
        "Tipo": df.dtypes.astype(str).values,
        "Valores únicos": df.nunique().values,
        "Valores faltantes": df.isnull().sum().values,
        "Porcentaje faltante": (df.isnull().mean() * 100).round(2).values
    })

    st.dataframe(
        diagnostico,
        width='stretch',
        hide_index=True,
        column_config={"Porcentaje faltante": st.column_config.NumberColumn(format="%.2f%%")}
    )

    # ----------------------------------
    # PROBLEMAS POTENCIALES
    # ----------------------------------

    st.subheader("Problemas potenciales")

    duplicados = df.duplicated().sum()
    desconocidos = int((df == DESCONOCIDO).sum().sum())
    sin_contacto = int((df[DIAS_PREVIO] == -1).sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Registros duplicados", duplicados)
    col2.metric("Celdas con «Desconocido»", f"{desconocidos:,}")
    col3.metric("Registros con días = -1", f"{sin_contacto:,}")

    st.markdown("""
    No todo lo que parece raro es un error:

    + **Desconocido** es información no disponible, no un «No» ni un fracaso.
    + **Días = -1** significa que no hubo contacto en una campaña anterior; no es un intervalo real.
    + **Saldos negativos** son posibles y no se consideran errores.
    + **Duración** se conoce después de la llamada, por eso no sirve para decidir a quién llamar.
    """)

    # ----------------------------------
    # EXPLORADOR DE VARIABLES
    # ----------------------------------

    st.subheader("Explorar una variable")

    variable = st.selectbox(
        "Selecciona una variable:",
        df.columns,
        key="variable_entender"
    )

    st.caption(DICCIONARIO.get(variable, ""))

    # Cuando es una variable numérica
    if pd.api.types.is_numeric_dtype(df[variable]):
        st.write("**Tipo:** Variable numérica")

        st.dataframe(df[variable].describe(), width='stretch')

    # Cuando es una variable categórica
    else:
        st.write("**Tipo:** Variable categórica")

        frecuencias = (
            df[variable]
            .value_counts(dropna=False)
            .reset_index()
        )

        frecuencias.columns = ["Valor", "Frecuencia"]
        frecuencias["Porcentaje"] = (frecuencias["Frecuencia"] / len(df) * 100).round(2)

        st.dataframe(frecuencias, width='stretch', hide_index=True)
