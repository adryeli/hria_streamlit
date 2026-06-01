"""Página 2 — Constructor de Skills: selección interactiva, currículo y cobertura de demanda."""
import streamlit as st
import plotly.graph_objects as go
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L

st.set_page_config(page_title="Constructor de Skills · HRIA", page_icon="🧩", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

skills = L.load_skills()
total_demand = skills["menciones"].sum()

L.page_header("Constructor de Skills",
              "Diseñe el temario y mida su cobertura del mercado español",
              "Datos OrientaHub (Fundación Telefónica) · tecnologías reales, Dic 2025–Abr 2026.")

# ── Curriculum builder: pick skills, see coverage live ───────────────
colL, colR = st.columns([1, 1.15])

with colL:
    st.markdown("##### 1 · Seleccione las skills del programa")
    # quick presets
    cpre1, cpre2, cpre3 = st.columns(3)
    if cpre1.button("Núcleo recomendado"):
        st.session_state.selected_skills = ["Cloud computing", "Python", "Git",
                                            "Microsoft Azure", "Scrum"]
    if cpre2.button("Vía Data Engineer"):
        st.session_state.selected_skills = ["Cloud computing", "Python", "Git", "Docker",
                                            "Kubernetes", "Amazon Web Services (AWS)", "Terraform"]
    if cpre3.button("Limpiar"):
        st.session_state.selected_skills = []

    chosen = st.multiselect(
        "Skills incluidas en el currículo",
        skills["skill"].tolist(),
        key="selected_skills")

with colR:
    st.markdown("##### 2 · Cobertura de la demanda")
    if chosen:
        covered = skills[skills["skill"].isin(chosen)]["menciones"].sum()
        coverage = covered / total_demand * 100
        core_hit = skills[(skills["skill"].isin(chosen)) &
                          (skills["categoria"].isin(L.CORE_CURRICULUM_CATS))]["menciones"].sum()
        core_total = skills[skills["categoria"].isin(L.CORE_CURRICULUM_CATS)]["menciones"].sum()
        core_cov = core_hit / core_total * 100 if core_total else 0
    else:
        coverage = core_cov = 0

    m1, m2 = st.columns(2)
    m1.metric("Cobertura total de demanda", f"{coverage:.1f}%",
              f"{len(chosen)} skills seleccionadas")
    m2.metric("Cobertura del núcleo (Cloud+Prog)", f"{core_cov:.1f}%",
              "lo que el mercado más pide")

    # gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=coverage,
        number={"suffix": "%", "font": {"family": "Lora"}},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": L.GOLD},
               "steps": [{"range": [0, 40], "color": "#F3E7CC"},
                         {"range": [40, 70], "color": "#E9D49A"},
                         {"range": [70, 100], "color": "#D9BE72"}],
               "threshold": {"line": {"color": L.CORAL, "width": 3},
                             "value": 60}}))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=10, b=10),
                      paper_bgcolor="white", font=dict(color=L.INK))
    st.plotly_chart(fig, width='stretch')
    if coverage >= 60:
        st.success("✓ El temario cubre la mayor parte de la demanda técnica española.")
    elif coverage > 0:
        st.warning("Cobertura baja. Añada skills de Cloud y Programación, que son el núcleo del mercado.")
    else:
        st.info("Seleccione skills o use un preset para empezar.")

st.markdown("---")

# ── Demand chart with selected skills highlighted ────────────────────
st.markdown("##### Skills más demandadas en España (selección resaltada)")
top = skills.head(15).iloc[::-1]
colors = [L.GOLD if s in chosen else "#C9CFDC" for s in top["skill"]]
fig = go.Figure(go.Bar(
    x=top["menciones"], y=top["skill"], orientation="h",
    marker_color=colors,
    text=[f"{v:,}".replace(",", ".") for v in top["menciones"]], textposition="outside"))
fig.update_layout(height=520, plot_bgcolor="white", paper_bgcolor="white",
                  margin=dict(l=10, r=40, t=10, b=10), font=dict(family="Inter", color=L.INK),
                  xaxis=dict(title="Menciones en ofertas", gridcolor="#EEF1F7"))
st.plotly_chart(fig, width='stretch')

# ── Curriculum recommendation ────────────────────────────────────────
st.markdown("##### 3 · Currículo recomendado, derivado de la demanda")
rc = st.columns(4)
modules = [
    ("Fundamentos", "Python · Scripting", L.TEAL),
    ("Cloud", "Cloud computing · Azure · AWS", L.GOLD),
    ("Ingeniería / DevOps", "Git · Docker · Kubernetes", L.NAVY2),
    ("Empleabilidad", "Scrum · JIRA + negocio", L.CORAL),
]
for col, (t, b, c) in zip(rc, modules):
    col.markdown(
        f"<div style='background:#fff;border-top:4px solid {c};border:1px solid #E3E9F4;"
        f"border-radius:10px;padding:14px;height:120px'>"
        f"<div style='font-weight:700;color:{L.INK}'>{t}</div>"
        f"<div style='color:{L.SLATE};font-size:0.85rem;margin-top:6px'>{b}</div></div>",
        unsafe_allow_html=True)

L.recommendation_strip("Recomendación.",
    "Construir el temario sobre <b>Cloud + un lenguaje base (Python/Java) + Git + metodología "
    "ágil</b>, con una capa diferencial de negocio. Currículo derivado de la demanda española real, "
    "no del dato USA — cierra el sesgo de agregación de skills del análisis.")
