"""Página 3 — Industry Explorer: tabs por tipo de industria y recomendaciones."""
import streamlit as st
import plotly.graph_objects as go
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L

st.set_page_config(page_title="Industry Explorer · HRIA", page_icon="🏢", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

L.page_header("Industry Explorer",
              "¿Dónde colocar a los alumnos? Volumen frente a competencia",
              "El volumen de ofertas no lo es todo: el nicho reduce la saturación de candidatos.")

ind = L.INDUSTRIES.copy()

# ── Overview chart colored by saturation ─────────────────────────────
sat_color = {"Alta": L.CORAL, "Media": L.GOLD, "Baja": L.GREEN}
fig = go.Figure(go.Bar(
    x=ind["industria"], y=ind["ofertas"],
    marker_color=[sat_color[s] for s in ind["saturacion"]],
    text=[f"{v:,}".replace(",", ".") for v in ind["ofertas"]], textposition="outside"))
fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                  margin=dict(l=10, r=10, t=20, b=10), font=dict(family="Inter", color=L.INK),
                  yaxis=dict(title="Nº de ofertas", gridcolor="#EEF1F7"),
                  xaxis=dict(tickangle=-30))
st.plotly_chart(fig, width='stretch')
st.caption("Color = saturación de candidatos · 🟥 Alta  🟨 Media  🟩 Baja. "
           "Los sectores verdes ofrecen mejor tasa de colocación por alumno.")

st.markdown("---")

# ── Tabs by saturation tier ──────────────────────────────────────────
t1, t2, t3 = st.tabs(["🟩 Nicho (baja competencia)", "🟨 Intermedio", "🟥 Alto volumen"])

def render_tier(tier):
    sub = ind[ind["saturacion"] == tier]
    for _, row in sub.iterrows():
        with st.expander(f"{row['industria']}  ·  {row['ofertas']:,} ofertas".replace(",", "."),
                         expanded=(row["industria"] == S["industry"])):
            reco = L.INDUSTRY_RECOS.get(row["industria"],
                                        "Sector con demanda de perfiles de datos. "
                                        "Evaluar saturación antes de priorizar.")
            cc1, cc2 = st.columns([1, 2])
            cc1.metric("Ofertas", f"{row['ofertas']:,}".replace(",", "."))
            cc1.metric("Saturación", row["saturacion"])
            cc2.markdown(f"**Recomendación de colocación**  \n{reco}")

with t1: render_tier("Baja")
with t2: render_tier("Media")
with t3: render_tier("Alta")

st.markdown(" ")
L.recommendation_strip("Recomendación.",
    "Dirigir el grueso a IT/Financial por <b>volumen</b>, y abrir una <b>vía premium de "
    "especialización en Healthcare y Manufacturing</b>: demanda real, menos competencia y "
    "diferenciación frente a otros bootcamps.")
