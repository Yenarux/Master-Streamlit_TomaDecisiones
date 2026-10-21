import pandas as pd
import streamlit as st

from banco import (
    clean_data, diagnostico_calidad, validar, DIAS_PREVIO, TUVO_CONTACTO, SALDO,
)


def mostrar(df):

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("2. Limpiar los datos")

    st.markdown("""
        ### Consideraciones

        + Hay elementos "Desconocido" porque es información no disponible
        + Contador de días con -1 significa que no hubo contacto en una campaña anterior
        + Originalmente tenemos la duración de la llamada como registros históricos pero no debe considerarse para la predicción
    """)

    # ----------------------------------
    # LIMPIEZA (sobre una copia; el original se conserva)
    # ----------------------------------

    dfLimpio, transformaciones = clean_data(df)

    # ----------------------------------
    # VALIDACIONES
    # ----------------------------------

    st.subheader("Validaciones")

    validaciones = validar(df)
    tabla_val = pd.DataFrame(
        [{"Regla": r, "Resultado": "✅ Cumple" if ok else "❌ Revisar", "Detalle": d}
         for r, ok, d in validaciones]
    )
    st.dataframe(tabla_val, width='stretch', hide_index=True)

    if not all(ok for _, ok, _ in validaciones):
        st.error("Hay validaciones que no se cumplen. Revisa los datos antes de continuar.")
        st.stop()

    # ----------------------------------
    # CALIDAD DE LOS DATOS
    # ----------------------------------

    st.subheader("¿Qué tan confiables son los datos?")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Celdas vacías", int(df.isna().sum().sum()))
    col2.metric("Celdas «Desconocido»", f"{int((df == 'Desconocido').sum().sum()):,}")
    col3.metric("Filas idénticas", int(df.duplicated().sum()))
    col4.metric("Saldos negativos", int((df[SALDO] < 0).sum()))

    st.dataframe(diagnostico_calidad(df, dfLimpio), width='stretch', hide_index=True)

    # ----------------------------------
    # TRATAMIENTOS
    # ----------------------------------

    st.subheader("Decisiones de limpieza")
    st.dataframe(transformaciones, width='stretch', hide_index=True)

    # ----------------------------------
    # ANTES / DESPUÉS
    # ----------------------------------

    st.subheader("Antes y después")

    col1, col2 = st.columns(2)
    col1.metric("Filas", f"{len(df):,} → {len(dfLimpio):,}")
    col2.metric("Columnas", f"{df.shape[1]} → {dfLimpio.shape[1]}")

    antes, despues = st.columns(2)

    with antes:
        st.markdown(f"**Antes:** «{DIAS_PREVIO}»")
        st.dataframe(df[DIAS_PREVIO].describe(), width='stretch')

    with despues:
        st.markdown(f"**Después:** «{DIAS_PREVIO}» (sin los -1)")
        st.dataframe(dfLimpio[DIAS_PREVIO].describe(), width='stretch')

    st.markdown(f"Nueva columna «{TUVO_CONTACTO}»:")
    st.dataframe(
        dfLimpio[TUVO_CONTACTO].value_counts().rename_axis("Valor").reset_index(name="Registros"),
        width='stretch',
        hide_index=True,
    )

    # ----------------------------------
    # DESCARGAS
    # ----------------------------------

    st.subheader("Descargas")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Datos limpios (CSV)",
            dfLimpio.to_csv(index=False).encode("utf-8-sig"),
            file_name="bank_limpio.csv",
            mime="text/csv",
        )

    with col2:
        st.download_button(
            "Diagnóstico de calidad (CSV)",
            diagnostico_calidad(df, dfLimpio).to_csv(index=False).encode("utf-8-sig"),
            file_name="diagnostico_calidad.csv",
            mime="text/csv",
        )

    with col3:
        st.download_button(
            "Transformaciones (CSV)",
            transformaciones.to_csv(index=False).encode("utf-8-sig"),
            file_name="transformaciones.csv",
            mime="text/csv",
        )

    return dfLimpio
