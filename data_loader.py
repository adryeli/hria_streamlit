"""
Cargador del dataset de mercado (Fase 2).

Estrategia de 3 niveles:
  1. CSV real en data/data_roles_completo.csv  ->  cálculo en vivo sobre datos reales
  2. CSV subido por el usuario en la app (uploader)  ->  se guarda en session_state
  3. Muestra sintética calibrada  ->  reproduce los agregados conocidos del análisis
     (salario mediano por rol, r≈0.857 vistas-applies, distribución por experiencia)

Esquema de columnas esperado (igual que los notebooks):
  job_id, salary_annual, views, applies,
  formatted_experience_level, formatted_work_type,
  job_industries_list, job_skills_list, comp_country, data_role
"""
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA = Path(__file__).parent / "data"
REAL_CSV = DATA / "data_roles_completo.csv"

# Mapeo flexible: nombres alternativos -> nombre canónico
COLUMN_ALIASES = {
    "salary_annual": ["salary_annual", "salary", "med_salary", "normalized_salary"],
    "views": ["views"],
    "applies": ["applies", "applications"],
    "formatted_experience_level": ["formatted_experience_level", "experience_level", "exp_level"],
    "formatted_work_type": ["formatted_work_type", "work_type", "contract_type"],
    "job_industries_list": ["job_industries_list", "industries", "industry"],
    "job_skills_list": ["job_skills_list", "skills"],
    "comp_country": ["comp_country", "country"],
    "data_role": ["data_role", "role", "job_role", "title_role"],
}

# Cifras objetivo del análisis (para calibrar la muestra sintética)
ROLE_TARGETS = {
    "Data Analyst":   {"median": 103000, "n": 1649, "pct_entry": 38.5},
    "Data Engineer":  {"median": 140000, "n": 3266, "pct_entry": 18.0},
    "Data Scientist": {"median": 145150, "n": 292,  "pct_entry": 22.0},
}
EXP_LEVELS = ["Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
EXP_WEIGHTS = [0.18, 0.10, 0.62, 0.07, 0.03]
EXP_SALARY = {"Entry level": 104767, "Associate": 105743, "Mid-Senior level": 138529,
              "Director": 209560, "Executive": 176583}
INDUSTRIES_SYN = {
    "IT Services & IT Consulting": 3189, "Financial Services": 1669,
    "Software Development": 1608, "Staffing & Recruiting": 1136,
    "Hospitals & Health Care": 831, "Technology": 749, "Manufacturing": 678,
    "Defense & Space": 657, "Civil Engineering": 570, "Banking": 547,
}
WORK_TYPES = {"Full-time": 0.797, "Contract": 0.166, "Part-time": 0.020,
              "Internship": 0.009, "Temporary": 0.004, "Other": 0.004}


def _canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas a los nombres canónicos según los alias detectados."""
    rename = {}
    lower = {c.lower(): c for c in df.columns}
    for canon, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a.lower() in lower:
                rename[lower[a.lower()]] = canon
                break
    return df.rename(columns=rename)


def _infer_role(df: pd.DataFrame) -> pd.DataFrame:
    """Si no hay columna data_role, intenta inferirla del título de la oferta."""
    if "data_role" in df.columns:
        return df
    title_col = next((c for c in df.columns if c.lower() in
                      ("title", "job_title", "normalized_title")), None)
    if title_col:
        t = df[title_col].astype(str).str.lower()
        role = np.select(
            [t.str.contains("engineer"), t.str.contains("scientist"), t.str.contains("analyst")],
            ["Data Engineer", "Data Scientist", "Data Analyst"], default="Data Analyst")
        df["data_role"] = role
    return df


@st.cache_data(show_spinner=False)
def _make_synthetic(seed: int = 42) -> pd.DataFrame:
    """Genera una muestra calibrada a las cifras reales del análisis."""
    rng = np.random.default_rng(seed)
    frames = []
    for role, t in ROLE_TARGETS.items():
        n = t["n"]
        # salario lognormal centrado en la mediana objetivo
        sigma = 0.42
        sal = rng.lognormal(mean=np.log(t["median"]), sigma=sigma, size=n)
        sal = np.clip(sal, 28000, 290000)
        # nivel de experiencia: ajustar % entry al objetivo del rol
        pe = t["pct_entry"] / 100
        rest = 1 - pe
        w = [pe, rest * 0.16, rest * 0.66, rest * 0.12, rest * 0.06]
        levels = rng.choice(EXP_LEVELS, size=n, p=np.array(w) / sum(w))
        # vistas y solicitudes con correlación ~0.857
        views = rng.gamma(2.0, 18, size=n).clip(2, 110)
        applies = (0.135 * views + 3.4 + rng.normal(0, 2.5, size=n)).clip(2, 30)
        # industria y tipo de contrato
        ind = rng.choice(list(INDUSTRIES_SYN), size=n,
                         p=np.array(list(INDUSTRIES_SYN.values())) / sum(INDUSTRIES_SYN.values()))
        wt = rng.choice(list(WORK_TYPES), size=n, p=list(WORK_TYPES.values()))
        frames.append(pd.DataFrame({
            "job_id": [f"{role[:2]}{i}" for i in range(n)],
            "data_role": role,
            "salary_annual": sal.round(0),
            "formatted_experience_level": levels,
            "views": views.round(0).astype(int),
            "applies": applies.round(0).astype(int),
            "job_industries_list": ind,
            "formatted_work_type": wt,
            "comp_country": "US",
        }))
    df = pd.concat(frames, ignore_index=True)
    return df


@st.cache_data(show_spinner=False)
def _read_uploaded(file_bytes: bytes) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(file_bytes), low_memory=False)
    return _infer_role(_canonical(df))


@st.cache_data(show_spinner=False)
def _read_real() -> pd.DataFrame:
    df = pd.read_csv(REAL_CSV, low_memory=False)
    return _infer_role(_canonical(df))


def load_market_data() -> tuple[pd.DataFrame, str]:
    """
    Devuelve (dataframe, fuente). fuente ∈ {'subido', 'real', 'sintético'}.
    Prioridad: CSV subido en la app > CSV real en data/ > muestra sintética.
    """
    up = st.session_state.get("uploaded_market_csv")
    if up is not None:
        try:
            up.seek(0)
            return _read_uploaded(up.getvalue()), "subido"
        except Exception:
            pass
    if REAL_CSV.exists():
        try:
            return _read_real(), "real"
        except Exception:
            pass
    return _make_synthetic(), "sintético"


def from_upload(file) -> pd.DataFrame:
    """Procesa un CSV subido por el usuario en la app."""
    df = pd.read_csv(file, low_memory=False)
    return _infer_role(_canonical(df))


# ── Agregaciones reutilizables (cacheadas por contenido) ─────────────
@st.cache_data(show_spinner=False)
def salary_by_role(df: pd.DataFrame) -> pd.DataFrame:
    g = df.dropna(subset=["salary_annual"]).groupby("data_role")["salary_annual"]
    return pd.DataFrame({
        "rol": g.median().index,
        "mediana": g.median().values,
        "q1": g.quantile(0.25).values,
        "q3": g.quantile(0.75).values,
        "n": g.size().values,
    })


@st.cache_data(show_spinner=False)
def salary_by_role_industry(df: pd.DataFrame, industry: str) -> pd.DataFrame:
    """Salario mediano por rol filtrado a una industria (cálculo en vivo)."""
    sub = df.copy()
    if "job_industries_list" in sub.columns:
        sub = sub[sub["job_industries_list"].astype(str).str.contains(industry, case=False, na=False)]
    if sub.empty or "salary_annual" not in sub.columns:
        return pd.DataFrame(columns=["rol", "mediana", "n"])
    g = sub.dropna(subset=["salary_annual"]).groupby("data_role")["salary_annual"]
    return pd.DataFrame({"rol": g.median().index, "mediana": g.median().values, "n": g.size().values})


@st.cache_data(show_spinner=False)
def scatter_data(df: pd.DataFrame, role: str | None = None) -> tuple[pd.DataFrame, float]:
    """Datos del scatter vistas-solicitudes (filtros del notebook) + r de Pearson."""
    if not {"views", "applies"}.issubset(df.columns):
        return pd.DataFrame(columns=["views", "applies"]), float("nan")
    sub = df.dropna(subset=["views", "applies"])
    if role and "data_role" in sub.columns:
        sub = sub[sub["data_role"] == role]
    sub = sub[(sub["views"] > 1) & (sub["applies"] > 1)]
    if len(sub) < 3:
        return sub[["views", "applies"]], float("nan")
    p95v, p95a = sub["views"].quantile(0.95), sub["applies"].quantile(0.95)
    sub = sub[(sub["views"] <= p95v) & (sub["applies"] <= p95a)]
    r = float(np.corrcoef(sub["views"], sub["applies"])[0, 1]) if len(sub) > 2 else float("nan")
    return sub[["views", "applies"]], r
