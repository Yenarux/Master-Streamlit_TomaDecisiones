"""Lógica compartida por las pestañas: limpieza, modelo y política de prioridad.

Las pestañas (carpeta tabs/) solo se encargan de la interfaz.
"""

import numpy as np
import pandas as pd
import streamlit as st

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ----------------------------------
# NOMBRES DE COLUMNAS
# ----------------------------------

TARGET = "Contrató el depósito a plazo"

EDAD = "Edad"
OCUPACION = "Ocupación"
ESTADO_CIVIL = "Estado civil"
EDUCACION = "Nivel educativo"
INCUMPLIMIENTO = "Crédito en incumplimiento de pago"
SALDO = "Saldo promedio anual en euros"
VIVIENDA = "Préstamo para vivienda"
PERSONAL = "Préstamo personal"
MEDIO = "Medio de contacto"
DIA = "Día del último contacto"
MES = "Mes del último contacto"
DURACION = "Duración del último contacto en segundos"
CONTACTOS_ACTUAL = "Contactos durante la campaña actual"
DIAS_PREVIO = "Días desde el contacto de una campaña anterior"
CONTACTOS_PREVIOS = "Contactos anteriores a la campaña actual"
RESULTADO_PREVIO = "Resultado de la campaña anterior"
TUVO_CONTACTO = "Tuvo contacto en una campaña anterior"
GRUPO_EDAD = "Grupo de edad"

DESCONOCIDO = "Desconocido"

NUM_FEATURES = [EDAD, SALDO, DIAS_PREVIO, CONTACTOS_PREVIOS]
CAT_FEATURES = [
    OCUPACION, ESTADO_CIVIL, EDUCACION, INCUMPLIMIENTO,
    VIVIENDA, PERSONAL, RESULTADO_PREVIO, TUVO_CONTACTO,
]
# Se conocen durante o después de la campaña actual; no se usan para predecir.
EXCLUDED = [DURACION, MEDIO, DIA, MES, CONTACTOS_ACTUAL]

MIN_GRUPO = 30  # casos mínimos para comentar un grupo en las descripciones


# ----------------------------------
# VALIDACIÓN Y LIMPIEZA
# ----------------------------------

def validar(df):
    """Devuelve una lista de (regla, cumple, detalle). No modifica los datos."""
    resultados = []

    faltantes = [c for c in NUM_FEATURES + CAT_FEATURES + EXCLUDED + [TARGET]
                 if c not in df.columns and c != TUVO_CONTACTO]
    resultados.append(("Columnas esperadas presentes", not faltantes,
                       ", ".join(faltantes) if faltantes else "17 columnas originales"))
    if faltantes:
        return resultados

    numericas = [EDAD, SALDO, DIA, DURACION, CONTACTOS_ACTUAL, DIAS_PREVIO, CONTACTOS_PREVIOS]
    num = df[numericas].apply(pd.to_numeric, errors="coerce")
    resultados.append(("Columnas numéricas completas e interpretables",
                       bool(num.notna().all().all()),
                       f"{int(num.isna().sum().sum())} valores no interpretables"))

    resultados.append(("Resultado únicamente Sí/No",
                       bool(df[TARGET].isin(["Sí", "No"]).all()), TARGET))
    resultados.append(("Indicadores de crédito y préstamos Sí/No",
                       bool(df[[INCUMPLIMIENTO, VIVIENDA, PERSONAL]].isin(["Sí", "No"]).all().all()),
                       "Incumplimiento, vivienda y personal"))
    resultados.append(("Edad entre 18 y 120", bool(num[EDAD].between(18, 120).all()), EDAD))
    resultados.append(("Día del mes entre 1 y 31", bool(num[DIA].between(1, 31).all()), DIA))
    resultados.append(("Al menos un contacto en la campaña actual",
                       bool((num[CONTACTOS_ACTUAL] >= 1).all()), CONTACTOS_ACTUAL))
    resultados.append(("Duración y contactos anteriores no negativos",
                       bool((num[DURACION] >= 0).all() and (num[CONTACTOS_PREVIOS] >= 0).all()),
                       f"{DURACION}; {CONTACTOS_PREVIOS}"))
    resultados.append(("Días desde contacto previo no menores que -1",
                       bool((num[DIAS_PREVIO] >= -1).all()), DIAS_PREVIO))
    return resultados


def clean_data(df):
    """Limpia una copia del original; no elimina filas.

    Devuelve (df_limpio, transformaciones) con una tabla que documenta cada cambio.
    """
    limpio = df.copy()

    # Texto: sin espacios exteriores y vacíos como datos ausentes.
    for col in limpio.columns:
        if not pd.api.types.is_numeric_dtype(limpio[col]):
            limpio[col] = limpio[col].astype("object").map(
                lambda v: v.strip() if isinstance(v, str) else v
            ).replace("", np.nan)

    # Numéricas: conversión explícita.
    for col in [EDAD, SALDO, DIA, DURACION, CONTACTOS_ACTUAL, DIAS_PREVIO, CONTACTOS_PREVIOS]:
        limpio[col] = pd.to_numeric(limpio[col], errors="coerce")

    # Vacíos categóricos de predictores -> Desconocido.
    categoricas = [c for c in CAT_FEATURES if c != TUVO_CONTACTO]
    vacios_cat = int(limpio[categoricas].isna().sum().sum())
    limpio[categoricas] = limpio[categoricas].fillna(DESCONOCIDO)

    # Días = -1 -> vacío estructural + indicador.
    sin_contacto = int((limpio[DIAS_PREVIO] == -1).sum())
    limpio[TUVO_CONTACTO] = np.where(limpio[DIAS_PREVIO] == -1, "No", "Sí")
    limpio.loc[limpio[DIAS_PREVIO] == -1, DIAS_PREVIO] = np.nan

    transformaciones = pd.DataFrame([
        {"Tratamiento": "Texto normalizado",
         "Regla": "Se quitan espacios exteriores; las cadenas vacías pasan a ausentes.",
         "Registros afectados": 0,
         "Justificación": "Evita categorías duplicadas por formato."},
        {"Tratamiento": "Desconocido conservado",
         "Regla": "Se mantiene como categoría; los vacíos categóricos de predictores se rellenan con Desconocido.",
         "Registros afectados": vacios_cat,
         "Justificación": "Desconocido es información no disponible; no equivale a No ni a fracaso."},
        {"Tratamiento": "Días = -1 → vacío estructural",
         "Regla": f"Se reemplaza -1 en «{DIAS_PREVIO}» por un vacío y se crea «{TUVO_CONTACTO}».",
         "Registros afectados": sin_contacto,
         "Justificación": "-1 significa que no hubo contacto anterior; no es un intervalo real."},
        {"Tratamiento": "Saldos negativos conservados",
         "Regla": "No se modifican ni se eliminan.",
         "Registros afectados": int((limpio[SALDO] < 0).sum()),
         "Justificación": "Un saldo negativo no es un error por sí mismo."},
        {"Tratamiento": "Filas idénticas conservadas",
         "Regla": "Se cuentan pero no se eliminan.",
         "Registros afectados": int(df.duplicated().sum()),
         "Justificación": "Sin identificador único no se pueden tratar como personas duplicadas."},
        {"Tratamiento": "Duración excluida del modelo",
         "Regla": "Se conserva para describir; no entra como predictor.",
         "Registros afectados": len(limpio),
         "Justificación": "Se conoce después de la llamada, no antes de decidir."},
    ])
    return limpio, transformaciones


def diagnostico_calidad(df, limpio):
    """Tabla por variable con vacíos, Desconocido y valores especiales."""
    filas = []
    for col in df.columns:
        filas.append({
            "Variable": col,
            "Vacíos originales": int(df[col].isna().sum()),
            "Desconocido": int((df[col] == DESCONOCIDO).sum()),
            "Valores -1": int((df[col] == -1).sum()) if pd.api.types.is_numeric_dtype(df[col]) else 0,
            "Vacíos tras limpiar": int(limpio[col].isna().sum()),
        })
    return pd.DataFrame(filas)


def grupo_edad(edad):
    return pd.cut(edad, bins=[17, 29, 44, 59, 200],
                  labels=["18–29", "30–44", "45–59", "60 o más"])


# ----------------------------------
# MODELO
# ----------------------------------

def _construir_pipeline():
    numerico = Pipeline([
        ("imputar", SimpleImputer(strategy="constant", fill_value=0)),
        ("escalar", StandardScaler()),
    ])
    categorico = Pipeline([
        ("imputar", SimpleImputer(strategy="constant", fill_value=DESCONOCIDO)),
        ("codificar", OneHotEncoder(handle_unknown="ignore", drop="first")),
    ])
    prep = ColumnTransformer([
        ("num", numerico, NUM_FEATURES),
        ("cat", categorico, CAT_FEATURES),
    ])
    return Pipeline([
        ("prep", prep),
        ("modelo", LogisticRegression(max_iter=2000, random_state=42)),
    ])


def _metricas(y, prob, corte=0.5):
    pred = (prob >= corte).astype(int)
    return {
        "Exactitud": accuracy_score(y, pred),
        "Precisión de Sí": precision_score(y, pred, zero_division=0),
        "Sensibilidad de Sí": recall_score(y, pred, zero_division=0),
        "F1 de Sí": f1_score(y, pred, zero_division=0),
        "ROC AUC": roc_auc_score(y, prob),
        "Precisión promedio (AP)": average_precision_score(y, prob),
    }


@st.cache_resource(show_spinner="Entrenando el modelo...")
def entrenar(limpio):
    """Entrena la regresión logística y evalúa en una prueba reservada (~20%)."""
    y = (limpio[TARGET] == "Sí").astype(int).to_numpy()
    X = limpio[NUM_FEATURES + CAT_FEATURES]

    # Las filas completamente idénticas quedan del mismo lado de la separación.
    grupos = pd.util.hash_pandas_object(limpio.drop(columns=[GRUPO_EDAD], errors="ignore"),
                                        index=False).to_numpy()
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    idx_train, idx_test = next(splitter.split(X, y, grupos))

    pipe = _construir_pipeline().fit(X.iloc[idx_train], y[idx_train])
    prob = pipe.predict_proba(X.iloc[idx_test])[:, 1]
    y_test = y[idx_test]

    prevalencia = y[idx_train].mean()
    base_prob = np.full(len(y_test), prevalencia)
    base = _metricas(y_test, base_prob, corte=0.5)

    nombres = pipe.named_steps["prep"].get_feature_names_out()
    coef = pd.DataFrame({
        "Variable": [n.split("__", 1)[1] for n in nombres],
        "Coeficiente": pipe.named_steps["modelo"].coef_[0],
    })
    coef["Magnitud"] = coef["Coeficiente"].abs()
    coef = coef.sort_values("Magnitud", ascending=False).drop(columns="Magnitud")

    pruebas = limpio.iloc[idx_test].copy()
    pruebas["Probabilidad estimada"] = prob
    pruebas["Fila del CSV"] = idx_test + 2  # cuenta el encabezado

    return {
        "n_train": len(idx_train),
        "n_test": len(idx_test),
        "metricas": _metricas(y_test, prob),
        "referencia": base,
        "matriz": confusion_matrix(y_test, (prob >= 0.5).astype(int), labels=[0, 1]),
        "coeficientes": coef,
        "pruebas": pruebas,
    }


# ----------------------------------
# POLÍTICA DE PRIORIDAD
# ----------------------------------

CORTE_MEDIO = 0.10
CORTE_ALTO = 0.25

POLICY = {
    "Alta": {
        "accion": "Priorizar una invitación informativa y ofrecer asesoría si la persona acepta.",
        "mensaje": "Tenemos una opción de ahorro a plazo que podría ajustarse a tus metas. "
                   "¿Te gustaría conocer los detalles con una persona asesora?",
    },
    "Media": {
        "accion": "Enviar información educativa y dar seguimiento con autorización.",
        "mensaje": "Te compartimos información sobre cómo funciona un depósito a plazo, "
                   "por si te resulta útil para planear tu ahorro.",
    },
    "Baja": {
        "accion": "Mantener la información disponible a solicitud, evitando contactos insistentes.",
        "mensaje": "Si en algún momento deseas conocer opciones de ahorro a plazo, "
                   "aquí tienes dónde consultarlas.",
    },
}


def assign_priority(prob, corte_medio=CORTE_MEDIO, corte_alto=CORTE_ALTO):
    """Asigna prioridad solo con la probabilidad estimada, nunca con el resultado real."""
    prob = np.asarray(prob)
    return np.where(prob >= corte_alto, "Alta",
                    np.where(prob >= corte_medio, "Media", "Baja"))
