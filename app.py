import streamlit as st
import pandas as pd

from tabs.entender import mostrar as mostrarTabEntender
from tabs.limpiar import mostrar as mostrarTabLimpiar
from tabs.descriptiva import mostrar as mostrarTabDescriptiva
from tabs.predictiva import mostrar as mostrarTabPredictiva
from tabs.prescriptiva import mostrar as mostrarTabPrescriptiva
from tabs.decisiones import mostrar as mostrarTabDecisiones
from tabs.decisiones_modificada import mostrar as mostrarTabDecisionesMod


# ----------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------

st.set_page_config(
    page_title="Bank Analytics",
    page_icon="🏦",
    layout="wide"
)


# ----------------------------------
# TÍTULO DE LA APLICACIÓN
# ----------------------------------

st.title("🏦 Bank Analytics")

st.markdown("""
Aplicación para encontrar clientes potenciales para contratrar un depósito a plazo.
""")


# ----------------------------------
# CARGAR DATASET
# ----------------------------------

df = pd.read_csv("data/bank_espanol_comas.csv")

# ----------------------------------
# CREAR PESTAÑAS
# ----------------------------------

tabEntender, tabLimpiar, tabDescriptiva, tabPredictiva, tabPrescriptiva, tabDecisiones, tabDecisionesMod = st.tabs([
    "1. Entender los datos",
    "2. Limpiar los datos",
    "3. Estadística descriptiva",
    "4. Estadística predictiva",
    "5. Estadística prescriptiva",
    "6. Toma de decisiones",
    "6. Toma de decisiones - modificada"
])


# ----------------------------------
# 1. ENTENDER LOS DATOS
# ----------------------------------

with tabEntender:
    mostrarTabEntender(df)


# ----------------------------------
# 2. LIMPIAR LOS DATOS
# ----------------------------------

with tabLimpiar:
    dfLimpio = mostrarTabLimpiar(df)


# ----------------------------------
# 3. ESTADÍSTICA DESCRIPTIVA
# ----------------------------------

with tabDescriptiva:
    mostrarTabDescriptiva(dfLimpio)


# ----------------------------------
# 4. ESTADÍSTICA PREDICTIVA
# ----------------------------------

with tabPredictiva:
    resultado = mostrarTabPredictiva(dfLimpio)


# ----------------------------------
# 5. ESTADÍSTICA PRESCRIPTIVA
# ----------------------------------

with tabPrescriptiva:
    pruebas, cortes = mostrarTabPrescriptiva(resultado)


# ----------------------------------
# 6. TOMA DE DECISIONES
# ----------------------------------

with tabDecisiones:
    mostrarTabDecisiones(pruebas, cortes)


# ----------------------------------
# 6. TOMA DE DECISIONES - MODIFICADA
# ----------------------------------

with tabDecisionesMod:
    mostrarTabDecisionesMod(pruebas, cortes)
