"""Página 5 — Bias Explorer: explicaciones expandibles con indicadores de riesgo."""
import streamlit as st
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L

st.set_page_config(page_title="Bias Explorer · HRIA", page_icon="🛡️", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

L.page_header("Bias Explorer",
              "Lo que los datos NO dicen — y cómo lo mitigamos",
              "Conocer las limitaciones no debilita el análisis: lo hace defendible.")

risk_color = {"Alto": L.CORAL, "Medio": L.GOLD, "Bajo": L.GREEN}

# risk summary row
n_alto = sum(1 for b in L.BIASES if b["riesgo"] == "Alto")
n_medio = sum(1 for b in L.BIASES if b["riesgo"] == "Medio")
n_bajo = sum(1 for b in L.BIASES if b["riesgo"] == "Bajo")
c1, c2, c3 = st.columns(3)
c1.metric("Riesgo alto", n_alto, "requieren mitigación activa", delta_color="off")
c2.metric("Riesgo medio", n_medio, "vigilar", delta_color="off")
c3.metric("Riesgo bajo / resuelto", n_bajo, "ya mitigados", delta_color="off")

st.markdown("---")
st.markdown("##### Los 8 sesgos del análisis")

for b in L.BIASES:
    rc = risk_color[b["riesgo"]]
    with st.expander(f"#{b['n']} · {b['sesgo']}  —  {b['dato']}"):
        st.markdown(
            f"<span style='background:{rc};color:white;padding:2px 10px;border-radius:12px;"
            f"font-size:0.75rem;font-weight:700'>RIESGO {b['riesgo'].upper()}</span>",
            unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        cc1.markdown(f"**Implicación**  \n{b['implicacion']}")
        cc2.markdown(f"**Mitigación**  \n{b['mitigacion']}")

st.markdown(" ")
L.dark_panel("Conclusión",
    "Los sesgos no invalidan el análisis — lo contextualizan. Sabemos qué preguntas puede "
    "responder este dataset y cuáles no. Los dos de mayor riesgo (geográfico y salarial) se "
    "gestionan con el ajuste salarial de la barra lateral y el cruce con datos de España.")
