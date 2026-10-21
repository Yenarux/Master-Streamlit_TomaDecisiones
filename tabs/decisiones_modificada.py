import streamlit as st

from banco import TARGET, POLICY

ORDEN = ["Alta", "Media", "Baja"]
CORTE_CLASIFICACION = 0.5


def mostrar(pruebas, cortes):

    tasa_general = (pruebas[TARGET] == "Sí").mean()

    # ----------------------------------
    # ENCABEZADO E INTRODUCCIÓN
    # ----------------------------------

    st.header("6. Toma de decisiones - modificada")

    st.markdown("""
    ### Retomando la pregunta inicial

    **¿Qué clientes tienen mayor probabilidad de contratar un depósito a plazo?**
    """)

    st.markdown(f"""
    Un depósito a plazo es un producto de ahorro: la persona deja su dinero en el banco por un tiempo
    acordado a cambio de un rendimiento. El banco no puede ni conviene contactar a todos sus clientes con la
    misma insistencia, así que la idea es **decidir antes de iniciar una nueva campaña** a quién conviene
    acercarse primero y con qué mensaje.

    En las pestañas anteriores revisamos los datos, los limpiamos, los describimos y construimos un modelo
    que estima, para cada cliente, qué tan probable es que contrate. Aquí damos el último paso: convertir
    esa estimación en una **acción concreta**. Para tener una referencia, en los casos de prueba contrató
    cerca de **{tasa_general:.1%}** de las personas (aproximadamente 1 de cada {round(1 / tasa_general)}).
    """)

    # ----------------------------------
    # QUÉ ES LA PRIORIDAD
    # ----------------------------------

    st.subheader("¿Qué es la «prioridad»?")

    st.markdown(f"""
    La **prioridad** indica qué tan pronto y con qué intensidad conviene acercarse a un cliente. Se asigna
    únicamente a partir de la probabilidad que estimó el modelo, nunca con el resultado real:

    + **Alta:** probabilidad estimada desde {cortes['alto']:.0%}.
    + **Media:** desde {cortes['medio']:.0%} y menos de {cortes['alto']:.0%}.
    + **Baja:** menos de {cortes['medio']:.0%}.
    """)

    with st.expander("¿Cómo se eligieron estos cortes?"):
        st.markdown(f"""
        Los cortes son **supuestos operativos ilustrativos**, no el resultado de una optimización:

        + Se tomaron como referencia la tasa general (alrededor de {tasa_general:.0%}): **{cortes['medio']:.0%}**
          marca a quienes están cerca o por encima del promedio y **{cortes['alto']:.0%}** a quienes tienen
          una probabilidad claramente mayor que el promedio.
        + No se calcularon con costos, capacidad del equipo de contacto ni rentabilidad.
        + Pueden ajustarse en la pestaña 5. Si se cambian muchas veces mirando los mismos datos de prueba,
          esos datos dejan de servir como validación independiente de la política elegida.
        """)

    # ----------------------------------
    # QUÉ SIGNIFICA LA PREDICCIÓN DEL 50%
    # ----------------------------------

    st.subheader("¿Qué significa la predicción Sí/No con 50%?")

    predicho_si = pruebas[pruebas["Probabilidad estimada"] >= CORTE_CLASIFICACION]
    aciertos = int((predicho_si[TARGET] == "Sí").sum())
    reales_si = int((pruebas[TARGET] == "Sí").sum())

    st.markdown(f"""
    El modelo no responde «sí» o «no» directamente: calcula una **probabilidad** para cada persona, por
    ejemplo 8% o 62%. Para evaluar si acierta, se necesita una regla simple: si la probabilidad llega
    al **50%** o más, se anota una predicción de **«Sí contratará»**; si es menor, **«No contratará»**.
    Es como decir «más de la mitad de posibilidades».
    """)

    st.info(
        f"Con esta regla, el modelo anunció «Sí» para {len(predicho_si)} personas de la prueba y acertó en "
        f"{aciertos}. Sin embargo, hubo {reales_si} contrataciones reales, es decir, dejó pasar a muchas "
        "personas que sí contrataron porque su probabilidad estimada era menor al 50%."
    )

    st.markdown(f"""
    **¿Por qué importa?** La mayoría de las personas tiene una probabilidad baja (la tasa general es
    de {tasa_general:.0%}), así que pocas llegan al 50%. Por eso el 50% sirve para **medir** al modelo, pero no
    para decidir a quién contactar: para eso usamos los cortes de prioridad de arriba, que son más
    sensibles ({cortes['medio']:.0%} y {cortes['alto']:.0%}).
    """)

    # ----------------------------------
    # SELECTOR DE PRIORIDAD
    # ----------------------------------

    st.subheader("Explorar una prioridad")

    prioridad = st.selectbox("Selecciona una prioridad:", ORDEN, key="prioridad_decisiones_mod")

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

    prob_media = grupo["Probabilidad estimada"].mean()
    tasa_grupo = (grupo[TARGET] == "Sí").mean()

    # ----------------------------------
    # EVIDENCIA
    # ----------------------------------

    st.subheader("Evidencia")

    col1, col2, col3 = st.columns(3)
    col1.metric("Casos", len(grupo))
    col2.metric("Probabilidad media estimada", f"{prob_media:.1%}")
    col3.metric("Tasa observada", f"{tasa_grupo:.1%}")

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
        f"Su probabilidad media estimada es {prob_media:.1%} y la tasa "
        f"observada fue {tasa_grupo:.1%}, frente a una tasa general de "
        f"{tasa_general:.1%} en la prueba."
    )

    st.markdown("**En palabras sencillas**")

    por_cada = 100
    contrataron_grupo = round(tasa_grupo * por_cada)
    contrataron_general = round(tasa_general * por_cada)

    if tasa_grupo > tasa_general * 1.2:
        lectura = "Es un grupo donde contratar es **más común** que en el resto, por eso conviene atenderlo primero."
    elif tasa_grupo < tasa_general * 0.8:
        lectura = ("Es un grupo donde contratar es **menos común** que en el resto, por eso conviene no insistir "
                   "y dejar la información disponible.")
    else:
        lectura = "Es un grupo **parecido al promedio**, por eso se propone un acercamiento informativo y moderado."

    st.success(
        f"De cada {por_cada} personas de este grupo, unas **{contrataron_grupo}** terminaron contratando. "
        f"En el total de la prueba, lo hicieron unas **{contrataron_general}** de cada {por_cada}. "
        f"{lectura} Esto no significa que el contacto cause la contratación: solo muestra con quién "
        "ha sido más frecuente en los datos."
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
