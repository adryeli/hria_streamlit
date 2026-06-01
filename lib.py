"""
HRIA · DataTalent Solutions — Talent Intelligence Platform
Core library: design system, cached data, shared business logic.
"""
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# PALETTE — "Midnight Executive" (consistente con el deliverable)
# ════════════════════════════════════════════════════════════════════
NAVY   = "#0F1A33"
NAVY2  = "#16213E"
NAVY3  = "#1E2C4F"
INK    = "#1A2540"
SLATE  = "#5B6B8C"
SLATE2 = "#8593AD"
GOLD   = "#C9A24B"
GOLDLT = "#E6CE8E"
ICE    = "#DCE6F7"
LIGHT  = "#F4F6FB"
TEAL   = "#2E8B8B"
CORAL  = "#C0504D"
GREEN  = "#2E9E6B"

ASSETS = Path(__file__).parent / "assets"
DATA   = Path(__file__).parent / "data"

# ════════════════════════════════════════════════════════════════════
# PROJECT DATA (verified from the HRIA analysis — LinkedIn USA + OrientaHub ES)
# ════════════════════════════════════════════════════════════════════
EUR_PER_USD = 0.92
SMI_ES = 17094  # salario mínimo anual de referencia, €

# Roles: salario mediano (USD, LinkedIn), % ofertas entry-level, n ofertas,
# vacantes reales España (OrientaHub Dic25-Abr26)
ROLES = {
    "Data Analyst":   {"salary_usd": 103000, "pct_entry": 38.5, "n": 1649,
                       "es_vacancies": 2573, "color": TEAL,
                       "blurb": "Puerta de entrada más accesible para juniors."},
    "Data Engineer":  {"salary_usd": 140000, "pct_entry": 18.0, "n": 3266,
                       "es_vacancies": 1888, "color": GOLD,
                       "blurb": "Rol de evolución con fuerte demanda técnica en España."},
    "Data Scientist": {"salary_usd": 145150, "pct_entry": 22.0, "n": 292,
                       "es_vacancies": None, "color": CORAL,
                       "blurb": "Mejor pagado, pero menor acceso junior y más incertidumbre."},
}

# Salario medio por nivel de experiencia (USD) + IC aproximado
EXPERIENCE = pd.DataFrame([
    {"nivel": "Entry level",      "salario": 104767, "n": 1222, "err": 2500},
    {"nivel": "Associate",        "salario": 105743, "n": 687,  "err": 3000},
    {"nivel": "Mid-Senior level", "salario": 138529, "n": 4051, "err": 1800},
    {"nivel": "Director",         "salario": 209560, "n": 86,   "err": 10000},
    {"nivel": "Executive",        "salario": 176583, "n": 14,   "err": 42000},
])

# Industrias (LinkedIn) + clasificación de saturación para la lógica de nicho
INDUSTRIES = pd.DataFrame([
    {"industria": "IT Services & IT Consulting", "ofertas": 3189, "tipo": "Alto volumen", "saturacion": "Alta"},
    {"industria": "Financial Services",          "ofertas": 1669, "tipo": "Alto volumen", "saturacion": "Alta"},
    {"industria": "Software Development",         "ofertas": 1608, "tipo": "Alto volumen", "saturacion": "Alta"},
    {"industria": "Staffing & Recruiting",        "ofertas": 1136, "tipo": "Intermediario", "saturacion": "Media"},
    {"industria": "Hospitals & Health Care",      "ofertas": 831,  "tipo": "Nicho",        "saturacion": "Baja"},
    {"industria": "Technology",                   "ofertas": 749,  "tipo": "Alto volumen", "saturacion": "Media"},
    {"industria": "Manufacturing",                "ofertas": 678,  "tipo": "Nicho",        "saturacion": "Baja"},
    {"industria": "Defense & Space",              "ofertas": 657,  "tipo": "Nicho",        "saturacion": "Baja"},
    {"industria": "Civil Engineering",            "ofertas": 570,  "tipo": "Nicho",        "saturacion": "Baja"},
    {"industria": "Banking",                      "ofertas": 547,  "tipo": "Alto volumen", "saturacion": "Media"},
])

INDUSTRY_RECOS = {
    "Hospitals & Health Care": "Sector en digitalización acelerada. Menos competencia que IT. "
        "Enfatizar privacidad de datos (RGPD sanitario) y analítica clínica.",
    "Manufacturing": "Industria 4.0 e IoT impulsan la demanda. Perfil Data Engineer con foco "
        "en datos de sensores y mantenimiento predictivo. Baja saturación de candidatos.",
    "Defense & Space": "Alta barrera de entrada (seguridad), pero salarios y estabilidad superiores. "
        "Vía premium para alumnos avanzados.",
    "IT Services & IT Consulting": "Mayor volumen absoluto pero máxima competencia. Bueno para "
        "primera colocación rápida; diferenciarse es difícil.",
    "Financial Services": "Alta demanda y buenos salarios. Valora certificaciones cloud y "
        "cumplimiento normativo. Competencia alta.",
}

# 8 sesgos del análisis
BIASES = [
    {"n": 1, "sesgo": "MNAR Salarial", "dato": "68% sin salario publicado",
     "implicacion": "Sobreestima los salarios reales del mercado.",
     "mitigacion": "Usar mediana + cruzar con Infojobs/SEPE.", "riesgo": "Alto"},
    {"n": 2, "sesgo": "Geográfico", "dato": "87% de ofertas en EE.UU.",
     "implicacion": "Los benchmarks salariales no aplican a España.",
     "mitigacion": "Cruzar con datos del mercado español (OrientaHub).", "riesgo": "Alto"},
    {"n": 3, "sesgo": "Selección (LinkedIn)", "dato": "Solo grandes empresas con marca",
     "implicacion": "Infravalora PYMEs y sector público.",
     "mitigacion": "Diversificar fuentes de datos.", "riesgo": "Medio"},
    {"n": 4, "sesgo": "Ausencia de género", "dato": "0% de cobertura de género",
     "implicacion": "Brecha salarial indetectable; riesgo legal AI Act.",
     "mitigacion": "Stack Overflow Developer Survey.", "riesgo": "Medio"},
    {"n": 5, "sesgo": "Temporal", "dato": "Datos de ~abril 2024",
     "implicacion": "Skills emergentes subrepresentadas.",
     "mitigacion": "Incorporar series 2022–2024.", "riesgo": "Medio"},
    {"n": 6, "sesgo": "Agregación de skills", "dato": "35 categorías para 213k relaciones",
     "implicacion": "Currículo de reskilling demasiado genérico.",
     "mitigacion": "NLP en descripciones + OrientaHub (resuelto).", "riesgo": "Bajo"},
    {"n": 7, "sesgo": "Supervivencia", "dato": "99%+ sin fecha de cierre",
     "implicacion": "Mercado oculto (60–80%) invisible.",
     "mitigacion": "Encuestas a candidatos y empresas.", "riesgo": "Medio"},
    {"n": 8, "sesgo": "Applies subestimadas", "dato": "Solo 39% con datos de solicitudes",
     "implicacion": "Métricas de competencia sesgadas.",
     "mitigacion": "Usar vistas como proxy universal (r=0.86).", "riesgo": "Bajo"},
]

CORE_CURRICULUM_CATS = ("Cloud", "Programming")  # núcleo del temario


@st.cache_data
def load_skills():
    df = pd.read_csv(DATA / "skills_spain.csv")
    return df.sort_values("menciones", ascending=False).reset_index(drop=True)


@st.cache_data
def roles_df():
    rows = []
    for name, d in ROLES.items():
        rows.append({"rol": name, **d})
    return pd.DataFrame(rows)


# ════════════════════════════════════════════════════════════════════
# BUSINESS LOGIC
# ════════════════════════════════════════════════════════════════════
def adjusted_salary_eur(role: str, salary_adj_pct: float) -> float:
    """Salario anual en EUR ajustado por el slider de mercado."""
    usd = ROLES[role]["salary_usd"]
    eur = usd * EUR_PER_USD
    return eur * (1 + salary_adj_pct / 100)


def compute_roi(role: str, program_cost: float, salary_adj_pct: float) -> dict:
    """
    ROI para el candidato: ganancia anual = salario alcanzable - salario base (SMI ES).
    Devuelve ganancia, múltiplo sobre coste y payback en meses.
    """
    salary = adjusted_salary_eur(role, salary_adj_pct)
    annual_gain = salary - SMI_ES
    multiple = annual_gain / program_cost if program_cost else 0
    payback_months = (program_cost / annual_gain * 12) if annual_gain > 0 else float("inf")
    return {
        "salary_eur": salary,
        "annual_gain": annual_gain,
        "multiple": multiple,
        "payback_months": payback_months,
    }

# Ejemplo: Entry Level €35.000 → Data Analyst €94.760 · ganancia €59.760 · payback = 6000/(59760/12) = 1.2 meses

def fmt_payback(months: float) -> str:
    """Formatea el payback de forma legible, manejando infinito y valores > 12 meses."""
    if months == float("inf") or months != months:  # inf o NaN
        return "No recuperable"
    if months < 1:
        return f"{months * 30:.0f} días"
    if months < 12:
        return f"{months:.1f} meses"
    years = int(months // 12)
    remaining = months % 12
    if remaining < 0.5:
        return f"{years} año{'s' if years > 1 else ''}"
    return f"{years} año{'s' if years > 1 else ''} {remaining:.0f} m"

def competitiveness(views: int, applies_known: int | None = None) -> dict:
    """
    Estima competitividad usando vistas como proxy (r=0.857 vistas->solicitudes).
    Modelo lineal simple derivado del análisis: applies ≈ 0.135*views + 3.4
    """
    est_applies = 0.135 * views + 3.4
    applies = applies_known if applies_known else est_applies
    # índice 0-100: normalizado contra un máximo de referencia (~25 applies)
    idx = min(100, (applies / 25) * 100)
    if idx < 33:
        label, color = "Baja competencia", GREEN
    elif idx < 66:
        label, color = "Competencia media", GOLD
    else:
        label, color = "Alta competencia", CORAL
    return {"est_applies": est_applies, "index": idx, "label": label, "color": color}


# ════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    .stApp {{ background: {LIGHT}; }}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Lora', serif !important; color: {INK}; letter-spacing:-0.01em; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background: {NAVY}; }}
    section[data-testid="stSidebar"] * {{ color: {ICE}; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: #fff !important; }}
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {{ color: {GOLDLT} !important; font-weight:600; }}

    /* KPI / metric cards */
    div[data-testid="stMetric"] {{
        background:#fff; border:1px solid #E3E9F4; border-radius:14px;
        padding:18px 20px; box-shadow:0 2px 10px rgba(15,26,51,0.06);
        border-top:4px solid {GOLD};
    }}
    div[data-testid="stMetric"] label {{ color:{SLATE}; font-weight:600; font-size:0.8rem; }}
    div[data-testid="stMetricValue"] {{ color:{INK}; font-family:'Lora',serif; }}

    /* Tabs */
    button[data-baseweb="tab"] {{ font-weight:600; color:{SLATE}; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color:{NAVY2}; }}
    div[data-baseweb="tab-highlight"] {{ background:{GOLD}; }}

    /* Expanders */
    details {{ border:1px solid #E3E9F4 !important; border-radius:10px !important; background:#fff; }}
    summary {{ font-weight:600; color:{INK}; }}

    /* Buttons */
    .stButton button {{
        background:{NAVY2}; color:#fff; border:none; border-radius:8px;
        font-weight:600; padding:0.5rem 1.2rem;
    }}
    .stButton button:hover {{ background:{GOLD}; color:{NAVY}; }}

    .block-container {{ padding-top:2.2rem; max-width:1280px; }}
    </style>
    """, unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(
        f"<div style='font-size:0.78rem;font-weight:700;letter-spacing:2px;"
        f"color:{GOLD};margin-bottom:2px'>{kicker.upper()}</div>"
        f"<h1 style='margin:0 0 6px 0;font-size:2.0rem'>{title}</h1>"
        + (f"<p style='color:{SLATE};font-size:1.02rem;margin:0 0 8px 0'>{subtitle}</p>" if subtitle else ""),
        unsafe_allow_html=True,
    )
    st.markdown(f"<hr style='border:none;border-top:2px solid {GOLD};width:54px;margin:6px 0 22px 0'>",
                unsafe_allow_html=True)


def insight_card(title, body, accent=GOLD, icon="◆"):
    st.markdown(
        f"<div style='background:#fff;border:1px solid #E3E9F4;border-left:4px solid {accent};"
        f"border-radius:10px;padding:16px 18px;margin-bottom:12px;box-shadow:0 2px 8px rgba(15,26,51,0.05)'>"
        f"<div style='font-weight:700;color:{INK};margin-bottom:4px'>{icon} {title}</div>"
        f"<div style='color:{SLATE};font-size:0.93rem;line-height:1.5'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def dark_panel(title, body, accent=GOLDLT):
    st.markdown(
        f"<div style='background:{NAVY2};border-radius:12px;padding:18px 22px;margin-bottom:12px'>"
        f"<div style='font-weight:700;color:{accent};letter-spacing:1px;font-size:0.8rem;"
        f"margin-bottom:6px'>{title.upper()}</div>"
        f"<div style='color:{ICE};font-size:0.95rem;line-height:1.55'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def recommendation_strip(headline, body):
    st.markdown(
        f"<div style='background:{NAVY2};border-left:6px solid {GOLD};border-radius:10px;"
        f"padding:16px 20px;margin-top:8px'>"
        f"<span style='color:{GOLDLT};font-weight:700'>↳ {headline} </span>"
        f"<span style='color:{ICE}'>{body}</span></div>",
        unsafe_allow_html=True,
    )


def init_state():
    """Valores por defecto de los controles globales (session_state)."""
    defaults = {
        "program_cost": 6000,
        "salary_adj": 0,
        "target_role": "Data Analyst",
        "industry": "IT Services & IT Consulting",
        "selected_skills": [],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def sidebar_controls():
    """Render de los controles globales. Devuelve el dict de estado actual."""
    import streamlit as st
    with st.sidebar:
        logo = ASSETS / "logo_hria.png"
        if logo.exists():
            st.image(str(logo))
        st.markdown(f"<div style='color:{GOLDLT};font-weight:700;letter-spacing:1px;"
                    f"font-size:0.85rem;margin-bottom:2px'>TALENT INTELLIGENCE</div>"
                    f"<div style='color:{SLATE2};font-size:0.78rem;margin-bottom:14px'>"
                    f"DataTalent Solutions · HRIA</div>", unsafe_allow_html=True)

        st.markdown("### Escenario")
        st.session_state.program_cost = st.slider(
            "Coste del programa (€)", 2000, 10000, st.session_state.program_cost, step=250,
            help="Precio del bootcamp por alumno. Afecta al ROI y al payback en todas las páginas.")
        st.session_state.salary_adj = st.slider(
            "Ajuste salarial (%)", -20, 20, st.session_state.salary_adj, step=1,
            help="Corrige el sesgo USA. Recomendado: negativo para aproximar al mercado español real.")
        st.session_state.target_role = st.selectbox(
            "Rol objetivo", list(ROLES.keys()),
            index=list(ROLES.keys()).index(st.session_state.target_role))
        st.session_state.industry = st.selectbox(
            "Industria", INDUSTRIES["industria"].tolist(),
            index=INDUSTRIES["industria"].tolist().index(st.session_state.industry))
    return st.session_state
      
