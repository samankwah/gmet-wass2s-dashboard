import streamlit as st
from pathlib import Path
import json

st.set_page_config(
    page_title="GMet WASS2S Forecast Dashboard",
    page_icon=":partly_sunny:",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"
DATA_DIR = APP_DIR / "data"

# --- Sidebar branding ---
with st.sidebar:
    logo_path = ASSETS_DIR / "smart_logo_GMet.png"
    cilss_path = ASSETS_DIR / "cilss.png"
    if logo_path.exists():
        st.image(str(logo_path), width=180)
    if cilss_path.exists():
        st.image(str(cilss_path), width=120)
    st.markdown("---")
    st.markdown("**Ghana Meteorological Agency**")
    st.markdown("Sub-Seasonal to Seasonal Forecasts")

# --- Main page ---
st.title("WASS2S Agrometeorological Forecast Dashboard")
st.markdown("### Ghana Meteorological Agency (GMet)")

# Load metadata if available
metadata_path = DATA_DIR / "metadata.json"
if metadata_path.exists():
    with open(metadata_path) as f:
        meta = json.load(f)
    col1, col2, col3 = st.columns(3)
    col1.metric("Forecast Year", meta.get("forecast_year", "—"))
    col2.metric("Initialization", meta.get("initialization", "—"))
    col3.metric("Last Updated", meta.get("last_updated", "—"))
else:
    st.info("No forecast data loaded yet. Run the pipeline to generate forecasts.")

st.markdown("---")

# --- Product overview ---
st.subheader("Available Forecast Products")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Agronomic Indices")
    st.markdown("""
    | Product | Description |
    |---------|-------------|
    | **Onset** | Rainfall onset date — planting guidance |
    | **1st Dry Spell** | First dry spell after onset |
    | **2nd/Late Dry Spell** | Second or late-season dry spell |
    | **Cessation** | Rainfall cessation date (end of season) |
    | **Length of Season** | Duration from onset to cessation |
    """)

with col2:
    st.markdown("#### Seasonal Forecasts")
    st.markdown("""
    | Season | Months | Products |
    |--------|--------|----------|
    | **MAM** | Mar–May | PRCP & TEMP |
    | **AMJ** | Apr–Jun | PRCP & TEMP |
    | **MJJ** | May–Jul | PRCP & TEMP |
    | **JJA** | Jun–Aug | PRCP & TEMP |
    | **JAS** | Jul–Sep | PRCP & TEMP |
    | **SON** | Sep–Nov | PRCP & TEMP |
    | **DJF** | Dec–Feb | PRCP & TEMP |
    """)

st.markdown("---")

# --- Quick links to consolidated forecast images ---
st.subheader("Latest Consolidated Forecasts")

FORECAST_DIR = Path("Agro_PRESAGG_2026_ic_1/forecasts")

tab_onset, tab_dryspell = st.tabs(["Onset", "Dry Spell"])

with tab_onset:
    onset_img = FORECAST_DIR / "Consolidated Forecast Onset-2025.png"
    if onset_img.exists():
        st.image(str(onset_img), caption="Consolidated Onset Forecast", width="stretch")
    else:
        # Try data dir
        data_img = DATA_DIR / "onset" / "consolidated_forecast.png"
        if data_img.exists():
            st.image(str(data_img), caption="Consolidated Onset Forecast", width="stretch")
        else:
            st.info("Run the pipeline to generate onset forecast maps.")

with tab_dryspell:
    ds_img = FORECAST_DIR / "Consolidated Forecast dryspellonset-2025.png"
    if ds_img.exists():
        st.image(str(ds_img), caption="Consolidated Dry Spell Onset Forecast", width="stretch")
    else:
        data_img = DATA_DIR / "dry_spell" / "consolidated_forecast.png"
        if data_img.exists():
            st.image(str(data_img), caption="Consolidated Dry Spell Onset Forecast", width="stretch")
        else:
            st.info("Run the pipeline to generate dry spell forecast maps.")

st.markdown("---")
st.caption("Powered by WASS2S | CILSS/AGRHYMET RCC | Ghana Meteorological Agency")
