import pandas as pd
import streamlit as st

from banco import entrenar, NUM_FEATURES, CAT_FEATURES, EXCLUDED


def mostrar(dfLimpio):
    """Entrena el modelo, muestra su evaluación y devuelve el resultado para las pestañas 5 y 6."""

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("4. Estadística predictiva")
    st.markdown("**¿Podemos estimar quién contratará?**")

    resultado = entrenar(dfLimpio)

    # ----------------------------------
    # CONFIGURACIÓN DEL MODELO
    # ----------------------------------

    st.subheader("Cómo se construyó")

    st.markdown(f"""
    + **Modelo:** regresión logística, sin balanceo artificial de clases.
    + **Partición:** {resultado['n_train']:,} registros de entrenamiento y {resultado['n_test']:,} de prueba (~20%),
      estratificada y manteniendo juntas las filas idénticas.
    + **Preparación:** escalado y codificación ajustados solo con entrenamiento.
    + **Corte de clasificación:** 50% (fijo; no se elige mirando la prueba).
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Predictores usados**")
        st.write(", ".join(NUM_FEATURES + CAT_FEATURES))
    with col2:
        st.markdown("**Excluidos (no disponibles antes de la campaña)**")
        st.write(", ".join(EXCLUDED))

    # ----------------------------------
    # MÉTRICAS
    # ----------------------------------

    st.subheader("Resultados en la prueba")

    metricas = pd.DataFrame({
        "Regresión logística": resultado["metricas"],
        "Referencia: siempre No": resultado["referencia"],
    })
    st.dataframe(
        metricas,
        width='stretch',
        column_config={
            "Regresión logística": st.column_config.NumberColumn(format="%.4f"),
            "Referencia: siempre No": st.column_config.NumberColumn(format="%.4f"),
        },
    )

    # ----------------------------------
    # MATRIZ DE CONFUSIÓN
    # ----------------------------------

    st.subheader("Matriz de confusión (corte 50%)")

    m = resultado["matriz"]
    matriz = pd.DataFrame(
        m,
        index=["Real: No", "Real: Sí"],
        columns=["Predicho: No", "Predicho: Sí"],
    )
    st.dataframe(matriz, width='stretch')

    reales_si = int(m[1].sum())
    st.warning(
        f"El modelo identificó {int(m[1, 1])} de {reales_si} contrataciones reales de la prueba "
        f"y omitió {int(m[1, 0])}. Una exactitud cercana a la de la referencia no significa que "
        "detecte a quienes contratarán: hay que leerla junto con la sensibilidad y las métricas de ordenación."
    )

    # ----------------------------------
    # COEFICIENTES
    # ----------------------------------

    st.subheader("Coeficientes")

    cuantos = st.slider("Variables a mostrar", 5, len(resultado["coeficientes"]), 15,
                        key="coef_predictiva")
    st.dataframe(resultado["coeficientes"].head(cuantos), width='stretch', hide_index=True)

    st.caption(
        "Los coeficientes son asociaciones condicionadas: las variables numéricas están escaladas "
        "y cada categoría se compara con una referencia omitida. No demuestran causalidad. "
        "Edad, educación, estado civil y ocupación requieren revisión de sesgos antes de un uso real."
    )

    return resultado
