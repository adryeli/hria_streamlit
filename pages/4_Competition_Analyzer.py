"""Página 4 — Competition Analyzer: simulador vistas vs solicitudes."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L
import data_loader as DL

st.set_page_config(page_title="Competition Analyzer · HRIA", page_icon="🎯", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

L.page_header("Competition Analyzer",
              "¿Qué tan disputada está una oferta?",
              "Las vistas predicen la competencia (r=0.86) y están en el 100% de las ofertas — "
              "no solo en el 39% que expone solicitudes.")

colL, colR = st.columns([1, 1.2])

with colL:
    st.markdown("##### Simulador")
    views = st.slider("Vistas de la oferta", 0, 110, 35, step=1,
                      help="Métrica disponible en todas las ofertas.")
    known = st.checkbox("Conozco las solicitudes reales (Easy Apply)")
    real_applies = st.number_input("Solicitudes reales", 0, 200, 8, disabled=not known) if known else None

    comp = L.competitiveness(views, real_applies if known else None)
    st.metric("Solicitudes estimadas", f"{comp['est_applies']:.0f}")
    st.markdown(
        f"<div style='background:#fff;border:1px solid #E3E9F4;border-left:5px solid {comp['color']};"
        f"border-radius:10px;padding:14px 16px;margin-top:6px'>"
        f"<div style='font-size:0.8rem;color:{L.SLATE};font-weight:600'>ÍNDICE DE COMPETENCIA</div>"
        f"<div style='font-family:Lora;font-size:2rem;color:{comp['color']};font-weight:700'>"
        f"{comp['index']:.0f}/100</div>"
        f"<div style='color:{L.INK};font-weight:600'>{comp['label']}</div></div>",
        unsafe_allow_html=True)

with colR:
    st.markdown("##### Vistas → solicitudes (datos reales + tu oferta)")
    df_mkt, src = DL.load_market_data()
    pts, r_real = DL.scatter_data(df_mkt, role=None)
    xs = np.arange(0, 111)
    ys = 0.135 * xs + 3.4
    fig = go.Figure()
    # nube de puntos reales del dataset
    if not pts.empty:
        fig.add_trace(go.Scatter(
            x=pts["views"], y=pts["applies"], mode="markers", name=f"Ofertas ({src})",
            marker=dict(size=5, color="#9DB2D6", opacity=0.35)))
    r_label = f"r={r_real:.3f}" if r_real == r_real else "r≈0.86"
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"Tendencia ({r_label})",
                             line=dict(color=L.CORAL, width=3)))
    fig.add_trace(go.Scatter(x=[views], y=[comp["est_applies"]], mode="markers",
                             name="Tu oferta", marker=dict(size=16, color=comp["color"],
                             line=dict(color="white", width=2))))
    fig.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=10, r=10, t=20, b=10), font=dict(family="Inter", color=L.INK),
                      xaxis=dict(title="Vistas", gridcolor="#EEF1F7"),
                      yaxis=dict(title="Solicitudes (estimadas)", gridcolor="#EEF1F7"),
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width='stretch')

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    L.insight_card("Para el candidato",
                   "Una oferta con muchas vistas está muy disputada: conviene aplicar rápido y "
                   "diferenciar el perfil. Pocas vistas = oportunidad menos competida.", L.TEAL)
with c2:
    L.insight_card("Para la empresa cliente",
                   "Si una vacante acumula vistas pero pocas conversiones, el problema está en la "
                   "descripción o el proceso, no en la falta de interés.", L.GOLD)

L.recommendation_strip("Recomendación.",
    "Ofrecer un <b>servicio de inteligencia de competencia basado en vistas</b>: orienta a los "
    "alumnos sobre a qué ofertas aplicar y asesora a las empresas cliente sobre cómo mejorar la "
    "conversión de sus vacantes.")
