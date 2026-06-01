"""
HRIA · Talent Intelligence Platform — Executive Summary (entry page)
Run with:  streamlit run app.py
"""
import streamlit as st
import plotly.graph_objects as go
import lib as L

st.set_page_config(page_title="HRIA · Talent Intelligence",
                   page_icon="assets/logo_hria.png", layout="wide",
                   initial_sidebar_state="expanded")

L.inject_css()
L.init_state()
S = L.sidebar_controls()

L.page_header(
    "Resumen ejecutivo",
    "DataTalent · Talent Intelligence Platform",
    "Explore escenarios de reskilling con datos reales del mercado. "
    "Los controles de la barra lateral recalculan toda la plataforma.")

# ── Live KPI row (reaccionan a los controles globales) ───────────────
role = S["target_role"]
roi = L.compute_roi(role, S["program_cost"], S["salary_adj"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rol objetivo", role, L.ROLES[role]["blurb"][:22] + "…", delta_color="off")
c2.metric("Salario alcanzable (€)", f"{roi['salary_eur']:,.0f}".replace(",", "."),
          f"{S['salary_adj']:+d}% ajuste" if S["salary_adj"] else "sin ajuste", delta_color="off")
c3.metric("ROI vs coste", f"{roi['multiple']:.1f}×",
          f"coste €{S['program_cost']:,.0f}".replace(",", "."), delta_color="inverse")
c4.metric("Payback", L.fmt_payback(roi['payback_months']),
          "recuperación de la inversión", delta_color="normal")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Two columns: insights + a live comparison chart ──────────────────
left, right = st.columns([1.05, 1])

with left:
    st.markdown("##### Hallazgos que definen la estrategia")
    L.insight_card("66% del mercado es Mid-Senior",
                   "El segmento más relevante. El reskilling debe apuntar al salto "
                   "Entry → Mid-Senior, que vale +35% de salario.", L.GOLD)
    L.insight_card("Data Analyst es la puerta de entrada",
                   "38,5% de sus ofertas aceptan juniors — casi el doble que cualquier "
                   "otro rol. Y lidera en vacantes reales en España (2.573).", L.TEAL)
    L.insight_card("El programa se amortiza en < 1 año",
                   "Incluso con un ajuste prudente sobre los salarios USA, el retorno para "
                   "el candidato multiplica el coste del programa.", L.GREEN)
    L.insight_card("Honestidad analítica",
                   "El 87% de los datos son de EE.UU. Por eso cruzamos con OrientaHub "
                   "(España real) y ofrecemos el ajuste salarial como control explícito.",
                   L.CORAL)

with right:
    st.markdown("##### Comparativa de roles en el escenario actual")
    roles = list(L.ROLES.keys())
    gains = [L.compute_roi(r, S["program_cost"], S["salary_adj"])["annual_gain"] for r in roles]
    colors = [L.ROLES[r]["color"] for r in roles]
    fig = go.Figure(go.Bar(
        x=roles, y=gains, marker_color=colors,
        text=[f"€{g:,.0f}".replace(",", ".") for g in gains], textposition="outside"))
    fig.add_hline(y=S["program_cost"], line_dash="dash", line_color=L.CORAL,
                  annotation_text=f"Coste €{S['program_cost']:,.0f}".replace(",", "."),
                  annotation_position="top left")
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="Ganancia anual (€)", font=dict(family="Inter", color=L.INK),
        yaxis=dict(gridcolor="#EEF1F7"))
    st.plotly_chart(fig, width='stretch')
    st.caption("Ganancia anual estimada = salario alcanzable − salario de referencia (SMI). "
               "Línea roja = coste del programa.")

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
L.recommendation_strip(
    "Navegación.",
    "Use el <b>Simulador de Carrera</b> para el caso de negocio, el <b>Constructor de "
    "Skills</b> para el temario, y el <b>Motor de Recomendación</b> para una ruta personalizada. "
    "Los controles de la izquierda son globales: cambian el escenario en todas las páginas.")
