import streamlit as st

from banco import TARGET, POLICY

ORDEN = ["Alta", "Media", "Baja"]


def mostrar(pruebas, cortes):

    # ----------------------------------
    # ENCABEZADO
    # ----------------------------------

    st.header("6. Toma de decisiones")
    st.markdown("**¿Qué hacemos y qué mensaje proponemos?**")

    # ----------------------------------
    # SELECTOR DE PRIORIDAD
    # ----------------------------------

    prioridad = st.selectbox("Selecciona una prioridad:", ORDEN, key="prioridad_decisiones")

    grupo = pruebas[pruebas["Prioridad"] == prioridad]
    politica = POLICY[prioridad]

    if prioridad == "Alta":
        rango = f"probabilidad estimada desde {cortes['alto']:.0%}"
    elif prioridad == "Media":
        rango = f"probabilidad estimada desde {cortes['medio']:.0%} y menos de {cortes['alto']:.0%}"
    else:
        rango = f"probabilidad estimada menor a {cortes['medio']:.0%}"

    st.caption(f"Prioridad {prioridad}: {rango}.")

    if grupo.empty:
        st.info("No hay casos de prueba con esta prioridad con los cortes actuales; no se muestran métricas.")
        return

    # ----------------------------------
    # EVIDENCIA
    # ----------------------------------

    st.subheader("Evidencia")

    col1, col2, col3 = st.columns(3)
    col1.metric("Casos", len(grupo))
    col2.metric("Probabilidad media estimada", f"{grupo['Probabilidad estimada'].mean():.1%}")
    col3.metric("Tasa observada", f"{(grupo[TARGET] == 'Sí').mean():.1%}")

    # ----------------------------------
    # ACCIÓN Y MENSAJE
    # ----------------------------------

    st.subheader("Acción y mensaje propuestos")

    st.markdown(f"**Acción:** {politica['accion']}")
    st.info(f"**Mensaje inicial:** {politica['mensaje']}")

    # ----------------------------------
    # JUSTIFICACIÓN
    # ----------------------------------

    st.subheader("Justificación")

    total = len(pruebas)
    st.markdown(
        f"Este grupo reúne {len(grupo)} de {total} casos de prueba ({len(grupo) / total:.1%}). "
        f"Su probabilidad media estimada es {grupo['Probabilidad estimada'].mean():.1%} y la tasa "
        f"observada fue {(grupo[TARGET] == 'Sí').mean():.1%}, frente a una tasa general de "
        f"{(pruebas[TARGET] == 'Sí').mean():.1%} en la prueba."
    )

    # ----------------------------------
    # LÍMITES
    # ----------------------------------

    st.subheader("Límites y validación futura")

    st.warning("""
    + Los datos son de una campaña en Portugal (2008–2010); no representan clientes actuales.
    + Una mayor propensión histórica no equivale a un mayor efecto de contactar.
    + Los mensajes son propuestas para un piloto: el dataset no prueba que funcionen.
    + Los cortes no se optimizaron con costos ni capacidad; falta validación independiente y calibración.
    + Revisar sesgos por edad, educación, estado civil y ocupación. Una prioridad baja no debe restringir
      el acceso al producto o a asesoría; respetar autorizaciones y solicitudes de no contacto.
    """)
