"""Página 1 — Simulador de Carrera: ROI dinámico, break-even, comparación de roles."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import lib as L
import data_loader as DL

st.set_page_config(page_title="Simulador de Carrera · HRIA", page_icon="📈", layout="wide")
L.inject_css(); L.init_state(); S = L.sidebar_controls()

L.page_header("Simulador de Carrera",
              "¿Qué retorno obtiene un alumno — y en cuánto tiempo?",
              "Ajuste coste y mercado en la barra lateral. Compare los tres roles en tiempo real.")

# ── Live KPIs for the selected role ──────────────────────────────────
role = S["target_role"]
roi = L.compute_roi(role, S["program_cost"], S["salary_adj"])
k1, k2, k3, k4 = st.columns(4)
k1.metric("Salario alcanzable", f"€{roi['salary_eur']:,.0f}".replace(",", "."))
k2.metric("Ganancia anual", f"€{roi['annual_gain']:,.0f}".replace(",", "."))
k3.metric("ROI", f"{roi['multiple']:.1f}×")
k4.metric("Break-even", L.fmt_payback(roi['payback_months']))

st.markdown("---")
df_mkt, src = DL.load_market_data()
st.caption(f"Datos de mercado: **{src}**" +
           (" · sube tu dataset real en cualquier página para cálculo sobre datos reales"
            if src == "sintético" else ""))
tab1, tab2, tab3, tab4 = st.tabs(
    ["⚖️ Comparar roles", "⏱️ Curva de break-even", "🎚️ Sensibilidad al precio",
     "📊 Salario real por industria"])

# TAB 1 — comparación de los tres roles bajo el escenario actual
with tab1:
    roles = list(L.ROLES.keys())
    rows = []
    for r in roles:
        rr = L.compute_roi(r, S["program_cost"], S["salary_adj"])
        rows.append((r, rr["salary_eur"], rr["annual_gain"], rr["multiple"], rr["payback_months"]))
    colA, colB = st.columns([1.1, 1])
    with colA:
        fig = go.Figure()
        fig.add_bar(name="Ganancia anual (€)", x=roles,
                    y=[x[2] for x in rows],
                    marker_color=[L.ROLES[r]["color"] for r in roles],
                    text=[f"€{x[2]:,.0f}".replace(",", ".") for x in rows], textposition="outside")
        fig.add_hline(y=S["program_cost"], line_dash="dash", line_color=L.CORAL,
                      annotation_text="Coste del programa")
        fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=10, r=10, t=30, b=10),
                          font=dict(family="Inter", color=L.INK),
                          yaxis=dict(title="€/año", gridcolor="#EEF1F7"))
        st.plotly_chart(fig, width='stretch')
    with colB:
        st.markdown("##### Tabla del escenario")
        import pandas as pd
        df = pd.DataFrame(rows, columns=["Rol", "Salario €", "Ganancia €", "ROI ×", "Payback meses"])
        df["Salario €"] = df["Salario €"].map(lambda v: f"{v:,.0f}".replace(",", "."))
        df["Ganancia €"] = df["Ganancia €"].map(lambda v: f"{v:,.0f}".replace(",", "."))
        df["ROI ×"] = df["ROI ×"].map(lambda v: f"{v:.1f}×")
        df["Payback meses"] = df["Payback meses"].map(lambda v: L.fmt_payback(v))
        st.dataframe(df, hide_index=True, width='stretch')
        best = max(rows, key=lambda x: x[3])
        L.insight_card("Mejor ROI del escenario", f"<b>{best[0]}</b> con {best[3]:.1f}× "
                       f"de retorno y recuperación en {L.fmt_payback(best[4])}.", L.GREEN)

# TAB 2 — break-even curve over months
with tab2:
    st.markdown("##### ¿Cuándo recupera el alumno la inversión?")
    months = np.arange(0, 25)
    fig = go.Figure()
    non_recoverable = []
    for r in roles:
        rr = L.compute_roi(r, S["program_cost"], S["salary_adj"])
        monthly_gain = rr["annual_gain"] / 12
        cumulative = monthly_gain * months - S["program_cost"]
        fig.add_trace(go.Scatter(x=months, y=cumulative, mode="lines",
                                 name=r, line=dict(color=L.ROLES[r]["color"], width=3)))
        if rr["annual_gain"] <= 0:
            non_recoverable.append(r)
    fig.add_hline(y=0, line_dash="dash", line_color=L.SLATE,
                  annotation_text="Punto de equilibrio")
    fig.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=10, r=10, t=20, b=10), font=dict(family="Inter", color=L.INK),
                      xaxis=dict(title="Meses desde la graduación", gridcolor="#EEF1F7"),
                      yaxis=dict(title="Beneficio neto acumulado (€)", gridcolor="#EEF1F7"))
    st.plotly_chart(fig, width='stretch')
    if non_recoverable:
        st.warning(f"⚠️ {', '.join(non_recoverable)}: con este ajuste salarial la ganancia es "
                   "negativa — el programa no se recupera. Sube el ajuste salarial o reduce el coste.")
    st.caption("Cruce con la línea de equilibrio = momento en que el alumno recupera el coste del programa.")

# TAB 3 — price sensitivity for the selected role
with tab3:
    st.markdown(f"##### Sensibilidad del payback al precio — {role}")
    costs = np.arange(2000, 10001, 500)
    paybacks_raw = [L.compute_roi(role, c, S["salary_adj"])["payback_months"] for c in costs]
    # filter out inf/nan for plotly (non-recoverable scenarios)
    costs_plot = [c for c, p in zip(costs, paybacks_raw) if p != float("inf") and p == p]
    paybacks = [p for p in paybacks_raw if p != float("inf") and p == p]
    if not paybacks:
        st.warning("Con el ajuste salarial actual el programa no se recupera en ningún escenario de precio.")
        st.stop()
    fig = go.Figure(go.Scatter(x=costs_plot, y=paybacks, mode="lines+markers",
                               line=dict(color=L.GOLD, width=3), marker=dict(size=7)))
    fig.add_vline(x=S["program_cost"], line_dash="dash", line_color=L.NAVY2,
                  annotation_text="Precio actual")
    fig.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=10, r=10, t=20, b=10), font=dict(family="Inter", color=L.INK),
                      xaxis=dict(title="Precio del programa (€)", gridcolor="#EEF1F7"),
                      yaxis=dict(title="Break-even (meses)", gridcolor="#EEF1F7"))
    st.plotly_chart(fig, width='stretch')
    L.insight_card("Lectura comercial",
                   f"A €{S['program_cost']:,.0f}".replace(",", ".") +
                   f", el alumno de {role} recupera en {L.fmt_payback(roi['payback_months'])}. "
                   "El margen para subir precio es amplio sin romper la propuesta de valor.", L.GOLD)

# TAB 4 — salario real calculado en vivo, filtrado por la industria del sidebar
with tab4:
    st.markdown(f"##### Salario mediano real por rol — {S['industry']}")
    si = DL.salary_by_role_industry(df_mkt, S["industry"])
    glob = DL.salary_by_role(df_mkt)
    if si.empty:
        st.info("No hay suficientes ofertas de esa industria en el dataset actual. "
                "Mostrando el agregado global.")
        si = glob.rename(columns={"mediana": "mediana"})[["rol", "mediana", "n"]]
    order = ["Data Analyst", "Data Engineer", "Data Scientist"]
    si["rol"] = si["rol"].astype("category")
    si = si.set_index("rol").reindex([r for r in order if r in si["rol"].values
                                      or r in si.index]).dropna().reset_index()
    colA, colB = st.columns([1.2, 1])
    with colA:
        fig = go.Figure()
        fig.add_bar(name=f"{S['industry']} (USD)", x=si["rol"], y=si["mediana"],
                    marker_color=[L.ROLES.get(r, {}).get("color", L.GOLD) for r in si["rol"]],
                    text=[f"${v:,.0f}".replace(",", ".") for v in si["mediana"]],
                    textposition="outside")
        # overlay global medians as reference markers
        gm = glob.set_index("rol")["mediana"]
        fig.add_trace(go.Scatter(
            x=si["rol"], y=[gm.get(r, None) for r in si["rol"]],
            mode="markers", name="Mediana global", marker=dict(
                symbol="line-ew", size=26, color=L.NAVY2, line=dict(width=3, color=L.NAVY2))))
        fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=10, r=10, t=30, b=10),
                          font=dict(family="Inter", color=L.INK),
                          yaxis=dict(title="Salario mediano (USD)", gridcolor="#EEF1F7"),
                          legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, width='stretch')
    with colB:
        st.markdown("**Cómo leerlo**")
        st.markdown(
            f"Estas medianas se **calculan en vivo** sobre el dataset ({src}), filtrando "
            f"las ofertas de *{S['industry']}*. Las marcas azules son la mediana global de "
            "cada rol: si la barra queda por debajo, esa industria paga menos que la media; "
            "por encima, paga una prima.")
        st.dataframe(
            si.assign(mediana=si["mediana"].map(lambda v: f"${v:,.0f}".replace(",", ".")),
                      n=si["n"].astype(int))
              .rename(columns={"rol": "Rol", "mediana": "Mediana", "n": "Ofertas"}),
            hide_index=True, width='stretch')

L.recommendation_strip("Recomendación.",
    "Fijar el precio sobre el rol de entrada (Data Analyst) manteniendo el payback por debajo "
    "de 12 meses: es el umbral psicológico que hace el programa una decisión fácil para el alumno.")
