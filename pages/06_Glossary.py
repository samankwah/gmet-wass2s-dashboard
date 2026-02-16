import streamlit as st
import sys
from pathlib import Path

_logo_path = Path(__file__).parent.parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(page_title="Glossary", page_icon=str(_logo_path) if _logo_path.exists() else None, layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, footer

inject_css()
sidebar_branding(page_id="glossary")

st.markdown("### Glossary")
st.caption("Definitions for meteorological, agronomic, and statistical terms used across the dashboard.")

# ── Forecast Types ──────────────────────────────────────────────────
with st.expander("Forecast Types", expanded=True):
    st.markdown("""
**Deterministic Forecast** — a single best-estimate prediction (e.g. 850 mm of rainfall), as opposed to a range of outcomes.

**Probabilistic Forecast** — expresses the likelihood of different outcomes, typically as percentage chances for each tercile category.

**Tercile Categories (BN / NN / AN)** — Below Normal, Near Normal, and Above Normal. The historical record is split into three equal parts; forecasts indicate which category is most likely.

**Ensemble Forecast** — a set of model runs with slightly varied initial conditions, used to capture forecast uncertainty.

**Consolidated Forecast** — a merged product that combines multiple model outputs into a single consensus map or prediction.
""")

# ── Agronomic Parameters ────────────────────────────────────────────
with st.expander("Agronomic Parameters", expanded=True):
    st.markdown("""
**Onset** — the start date of the rainy season, defined by sustained rainfall exceeding a threshold without a subsequent dry spell.

**Cessation** — the end date of the rainy season, when soil moisture can no longer sustain rain-fed crops.

**Dry Spell** — a consecutive run of days with little or no rainfall during the rainy season (typically the first major dry spell after onset).

**Late Dry Spell** — a prolonged dry period occurring later in the season, which can damage crops during critical growth stages.

**Length of Season** — the number of days between onset and cessation, indicating the window available for crop growth.

**Day of Year (DOY)** — a calendar-independent date representation (1–365/366) used to compare onset and cessation dates across years.
""")

# ── Seasonal Climate ────────────────────────────────────────────────
with st.expander("Seasonal Climate", expanded=True):
    st.markdown("""
**PRCP (Precipitation)** — total rainfall accumulated over a defined season or period, usually measured in millimetres.

**TEMP (Temperature)** — mean air temperature over a season, typically reported in degrees Celsius.

**Season Codes** — three-letter abbreviations for overlapping 3-month seasons:
MAM (Mar–May), AMJ (Apr–Jun), MJJ (May–Jul), JJA (Jun–Aug), JAS (Jul–Sep), SON (Sep–Nov), DJF (Dec–Feb).
""")

# ── Skill Metrics ───────────────────────────────────────────────────
with st.expander("Skill Metrics", expanded=True):
    st.markdown("""
**GROC (Generalized Relative Operating Characteristic)** — measures the ability of a forecast to discriminate between events and non-events. Values above 0.5 indicate skill better than random chance.

**Pearson Correlation** — a measure of the linear relationship between forecast and observed values, ranging from −1 to +1. Higher positive values indicate stronger agreement.

**MAE (Mean Absolute Error)** — the average magnitude of forecast errors, in the same units as the variable. Lower values indicate more accurate forecasts.

**RPSS (Ranked Probability Skill Score)** — compares the probabilistic forecast against climatology. Positive values indicate the forecast is more skilful than simply using historical averages.

**Hindcast** — a retrospective forecast made using historical data (typically 1993–2016) to evaluate how well the model would have performed in the past.
""")

# ── General Terms ───────────────────────────────────────────────────
with st.expander("General Terms", expanded=True):
    st.markdown("""
**Initialization** — the month in which forecast models were run; determines which observations were available to seed the prediction.

**GMet** — Ghana Meteorological Agency, the national body responsible for weather and climate services.

**WASS2S** — West African Sub-seasonal to Seasonal forecasting system, providing climate predictions on 2-week to 6-month timescales.

**CILSS / AGRHYMET** — the Permanent Interstate Committee for Drought Control in the Sahel and its regional climate centre, which contributes forecast guidance for West Africa.

**Sub-seasonal to Seasonal (S2S)** — the time range between weather forecasts (~2 weeks) and long-range climate projections (~months), bridging the gap for decision-making.
""")

footer()
