import pandas as pd
import streamlit as st

from banco import (
    TARGET, POLICY, CORTE_MEDIO, CORTE_ALTO, assign_priority,
)

ORDEN = ["Alta", "Media", "Baja"]


def resumen_prioridades(pruebas):
    """Casos, contrataciones y probabilidad media por prioridad (incluye grupos vacíos)."""
    filas = []
    for p in ORDEN:
        g = pruebas[pruebas["Prioridad"] == p]
        filas.append({
            "Prioridad": p,
            "Casos": len(g),
            "Contrataciones observadas": int((g[TARGET] == "Sí").sum()),
            "Probabilidad media estimada": g["Probabilidad estimada"].mean() if len(g) else None,
            "Tasa observada": (g[TARGET] == "Sí").mean() if len(g) else None,
        })
    return pd.DataFrame(filas)


def mostrar(resultado):
    """Asigna prioridades a los casos de prueba y devuelve (pruebas, cortes) para la pestaña 6."""

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("5. Estadística prescriptiva")
    st.markdown("**¿Qué acción proponer para cada nivel de probabilidad?**")

    # ----------------------------------
    # CORTES AJUSTABLES
    # ----------------------------------

    st.subheader("Cortes de prioridad")

    col1, col2 = st.columns(2)
    with col1:
        corte_medio = st.slider("Prioridad media desde (%)", 1, 99, int(CORTE_MEDIO * 100),
                                key="corte_medio") / 100
    with col2:
        corte_alto = st.slider("Prioridad alta desde (%)", 1, 99, int(CORTE_ALTO * 100),
                               key="corte_alto") / 100

    if corte_alto < corte_medio:
        st.warning("El corte alto no puede ser menor que el medio; se usa el valor del corte medio.")
        corte_alto = corte_medio
    elif corte_alto == corte_medio:
        st.info("Los cortes son iguales: la prioridad Media quedará vacía.")

    st.caption(
        "Los cortes iniciales (10% y 25%) son supuestos operativos ilustrativos, distintos del corte de "
        "50% de la evaluación. Si los ajustas repetidamente mirando esta prueba, ya no es una "
        "validación independiente de la política elegida."
    )

    # ----------------------------------
    # ASIGNACIÓN (solo con la probabilidad estimada)
    # ----------------------------------

    pruebas = resultado["pruebas"].copy()
    pruebas["Prioridad"] = assign_priority(pruebas["Probabilidad estimada"], corte_medio, corte_alto)

    # ----------------------------------
    # TABLA DE ACCIONES
    # ----------------------------------

    st.subheader("Acciones propuestas")

    limites = {
        "Alta": f"Desde {corte_alto:.0%}",
        "Media": f"Desde {corte_medio:.0%} y menos de {corte_alto:.0%}",
        "Baja": f"Menos de {corte_medio:.0%}",
    }
    acciones = pd.DataFrame([
        {"Prioridad": p, "Probabilidad estimada": limites[p], "Acción propuesta": POLICY[p]["accion"]}
        for p in ORDEN
    ])
    st.dataframe(acciones, width='stretch', hide_index=True)

    # ----------------------------------
    # RESULTADOS POR PRIORIDAD
    # ----------------------------------

    st.subheader("Resultados por prioridad en la prueba")

    resumen = resumen_prioridades(pruebas)
    st.dataframe(
        resumen,
        width='stretch',
        hide_index=True,
        column_config={
            "Probabilidad media estimada": st.column_config.NumberColumn(format="percent"),
            "Tasa observada": st.column_config.NumberColumn(format="percent"),
        },
    )

    vacias = resumen.loc[resumen["Casos"] == 0, "Prioridad"].tolist()
    if vacias:
        st.info(f"Sin casos en prioridad: {', '.join(vacias)}. No se calculan métricas para esos grupos.")

    st.caption("La prioridad se asigna solo con la probabilidad; el resultado real se muestra para evaluar "
               "retrospectivamente cada grupo, no para decidirlo.")

    # ----------------------------------
    # DESCARGA
    # ----------------------------------

    st.download_button(
        "Descargar prioridades de los casos de prueba (CSV)",
        pruebas.to_csv(index=False).encode("utf-8-sig"),
        file_name="prioridades_prueba.csv",
        mime="text/csv",
    )
    st.caption("«Fila del CSV» señala la posición para inspección (cuenta el encabezado); no identifica a una persona.")

    return pruebas, {"medio": corte_medio, "alto": corte_alto}
