"""Página 6 — Recommendation Engine: ruta personalizada + recomendaciones de negocio."""
import streamlit as st
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L

st.set_page_config(page_title="Motor de Recomendación · HRIA", page_icon="🧭", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

L.page_header("Motor de Recomendación",
              "Una ruta personalizada a partir de su escenario",
              "Sintetiza todos los controles en un plan accionable para alumno y negocio.")

role = S["target_role"]
roi = L.compute_roi(role, S["program_cost"], S["salary_adj"])
skills = L.load_skills()

# ── Personalized learning path ───────────────────────────────────────
st.markdown("##### Ruta de aprendizaje recomendada")

# Decide entry role logic: Analyst is the recommended door unless user insists
entry = "Data Analyst"
target = role
path = [entry] if target == entry else [entry, target]
core = skills[skills["categoria"].isin(L.CORE_CURRICULUM_CATS)].head(5)["skill"].tolist()

steps = []
steps.append(("1 · Entrada", f"{entry}",
              "Rol más colocable (38,5% de ofertas junior). Primer empleo en el sector."))
if target != entry:
    steps.append(("2 · Evolución", f"{target}",
                  f"Tras 1–2 años, salto a {target}. Salario alcanzable: "
                  f"€{roi['salary_eur']:,.0f}".replace(",", ".") + "."))
steps.append((f"{'3' if target!=entry else '2'} · Núcleo de skills",
              ", ".join(core[:3]),
              "Base técnica que cubre la mayor parte de la demanda española."))
steps.append((f"{'4' if target!=entry else '3'} · Colocación",
              S["industry"],
              L.INDUSTRY_RECOS.get(S["industry"], "Sector con demanda de perfiles de datos.")[:90] + "…"))

cols = st.columns(len(steps))
for col, (head, big, body) in zip(cols, steps):
    col.markdown(
        f"<div style='background:#fff;border:1px solid #E3E9F4;border-top:4px solid {L.GOLD};"
        f"border-radius:10px;padding:14px;height:180px'>"
        f"<div style='color:{L.GOLD};font-weight:700;font-size:0.78rem'>{head.upper()}</div>"
        f"<div style='font-family:Lora;font-weight:700;color:{L.INK};font-size:1.05rem;margin:6px 0'>{big}</div>"
        f"<div style='color:{L.SLATE};font-size:0.83rem;line-height:1.4'>{body}</div></div>",
        unsafe_allow_html=True)

st.markdown("---")

# ── Scenario summary KPIs ────────────────────────────────────────────
st.markdown("##### Resumen del escenario configurado")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Ruta", f"{entry}" + (f" → {target}" if target != entry else ""))
k2.metric("Inversión", f"€{S['program_cost']:,.0f}".replace(",", "."))
k3.metric("ROI", f"{roi['multiple']:.1f}×")
k4.metric("Break-even", f"{roi['payback_months']:.1f} meses")

st.markdown("---")
st.caption(
    f"ℹ️ Break-even calculado como diferencia entre salario alcanzable y SMI español (Salario referencia USA, ajustar a mercado español)"
    f"(€{L.SMI_ES:,.0f}/año). Es el argumento comercial máximo, no el payback desde un salario previo real.")
st.info("💡 Escenario mínimo real (España): SMI €17.094 → Entry Level datos €35.000 "
        f"· ganancia €{35000-17094:,.0f}/año · payback {L.fmt_payback(6000/((35000-17094)/12))}")
# ── Business recommendations (the 5, tied to questions) ──────────────
st.markdown("##### Recomendaciones de negocio para DataTalent")
recos = [
    ("Priorizar Data Analyst como entrada", "Mayor tasa de colocación en el primer empleo.", "Pregunta 1", L.TEAL),
    ("Itinerario en dos velocidades", "Vendemos una carrera, no un curso suelto.", "Pregunta 1", L.GOLD),
    ("Comunicar el ROI < 1 año", "Argumento de venta y precio defendible.", "Pregunta 2", L.GREEN),
    ("Currículo con módulo de negocio", "Perfil que coloca en España, no solo técnica.", "Pregunta 3", L.NAVY2),
    ("Vía de especialización sectorial", "Diferenciación frente a otros bootcamps.", "Pregunta 4", L.CORAL),
    ("Inteligencia de competencia (vistas)", "Servicio nuevo para candidatos y empresas.", "Pregunta 5", L.SLATE),
]
g = st.columns(2)
for i, (t, b, q, c) in enumerate(recos):
    with g[i % 2]:
        st.markdown(
            f"<div style='background:#fff;border:1px solid #E3E9F4;border-left:5px solid {c};"
            f"border-radius:10px;padding:14px 16px;margin-bottom:10px'>"
            f"<div style='display:flex;justify-content:space-between'>"
            f"<span style='font-weight:700;color:{L.INK}'>{t}</span>"
            f"<span style='font-size:0.72rem;color:{L.NAVY2};border:1px solid {L.GOLD};"
            f"border-radius:10px;padding:1px 8px'>{q}</span></div>"
            f"<div style='color:{L.SLATE};font-size:0.86rem;margin-top:4px'>"
            f"<b>Impacto:</b> {b}</div></div>",
            unsafe_allow_html=True)

# ── Export the scenario ──────────────────────────────────────────────
import pandas as pd
summary = pd.DataFrame([{
    "rol_entrada": entry, "rol_objetivo": target,
    "coste_programa_eur": S["program_cost"], "ajuste_salarial_pct": S["salary_adj"],
    "salario_alcanzable_eur": round(roi["salary_eur"]),
    "ganancia_anual_eur": round(roi["annual_gain"]),
    "roi_multiplo": round(roi["multiple"], 2),
    "payback_meses": round(roi["payback_months"], 1),
    "industria": S["industry"],
}])
st.download_button("⬇️ Exportar escenario (CSV)",
                   summary.to_csv(index=False).encode("utf-8"),
                   "escenario_datatalent.csv", "text/csv")

L.recommendation_strip("En una frase.",
    "Data Analyst como puerta de entrada y el salto a Mid-Senior es el camino de mayor retorno "
    "y menor riesgo. El programa se amortiza en menos de un año.")
