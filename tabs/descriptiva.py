import pandas as pd
import streamlit as st

from banco import (
    TARGET, OCUPACION, SALDO, EDAD, GRUPO_EDAD, ESTADO_CIVIL, EDUCACION,
    VIVIENDA, PERSONAL, RESULTADO_PREVIO, TUVO_CONTACTO, MIN_GRUPO, grupo_edad,
)

SEGMENTOS = [VIVIENDA, PERSONAL, RESULTADO_PREVIO, TUVO_CONTACTO, ESTADO_CIVIL, EDUCACION]


def _tasa_por_grupo(df, columna):
    """Casos, contrataciones y tasa por categoría, siempre con su denominador."""
    tabla = (
        df.assign(_si=(df[TARGET] == "Sí"))
        .groupby(columna, observed=True)["_si"]
        .agg(Casos="count", Contrataciones="sum")
        .reset_index()
    )
    tabla["Tasa de contratación"] = tabla["Contrataciones"] / tabla["Casos"]
    return tabla


def _comentario(tabla, columna):
    """Comenta el grupo con mayor tasa considerando solo grupos de tamaño suficiente."""
    validos = tabla[tabla["Casos"] >= MIN_GRUPO]
    if validos.empty:
        st.caption(f"Ningún grupo tiene al menos {MIN_GRUPO} casos; no se comenta.")
        return
    mejor = validos.sort_values("Tasa de contratación", ascending=False).iloc[0]
    st.markdown(
        f"**Lectura:** entre los grupos con al menos {MIN_GRUPO} casos, «{mejor[columna]}» "
        f"tiene la mayor tasa ({mejor['Tasa de contratación']:.1%}, {int(mejor['Casos'])} casos). "
        "Es una asociación observada, no una causa."
    )


def _mostrar_grupo(df, columna, orden=None):
    tabla = _tasa_por_grupo(df, columna)
    if orden is not None:
        tabla[columna] = pd.Categorical(tabla[columna], categories=orden, ordered=True)
        tabla = tabla.sort_values(columna)
    else:
        tabla = tabla.sort_values("Tasa de contratación", ascending=False)

    st.bar_chart(tabla.set_index(columna)["Tasa de contratación"], y_label="Tasa de contratación")
    st.dataframe(
        tabla,
        width='stretch',
        hide_index=True,
        column_config={"Tasa de contratación": st.column_config.NumberColumn(format="percent")},
    )
    _comentario(tabla, columna)


def mostrar(dfLimpio):

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("3. Estadística descriptiva")
    st.markdown("**¿Cómo cambia la contratación por segmento?**")

    df = dfLimpio.copy()
    df[GRUPO_EDAD] = grupo_edad(df[EDAD])

    # ----------------------------------
    # INDICADORES GENERALES
    # ----------------------------------

    contrataron = int((df[TARGET] == "Sí").sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasa general de contratación", f"{contrataron / len(df):.2%}")
    col2.metric("Contrataciones", f"{contrataron:,} de {len(df):,}")
    col3.metric("Mediana del saldo (€)", f"{df[SALDO].median():,.0f}")

    # ----------------------------------
    # POR OCUPACIÓN
    # ----------------------------------

    st.subheader("Por ocupación")
    _mostrar_grupo(df, OCUPACION)

    # ----------------------------------
    # POR EDAD
    # ----------------------------------

    st.subheader("Por grupo de edad")
    _mostrar_grupo(df, GRUPO_EDAD, orden=["18–29", "30–44", "45–59", "60 o más"])

    # ----------------------------------
    # OTRO SEGMENTO
    # ----------------------------------

    st.subheader("Explorar otro segmento")

    segmento = st.selectbox(
        "Selecciona un segmento:",
        SEGMENTOS,
        key="segmento_descriptiva",
    )
    _mostrar_grupo(df, segmento)

    st.caption(
        "Estos filtros solo describen los datos; no modifican el entrenamiento del modelo. "
        f"El mínimo de {MIN_GRUPO} casos es una regla de prudencia, no una garantía de significancia."
    )
