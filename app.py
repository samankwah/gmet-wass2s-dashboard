import streamlit as st
from pathlib import Path
import sys

st.set_page_config(
    page_title="GMet WASS2S Forecast Dashboard",
    page_icon=":partly_sunny:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure utils is importable
sys.path.insert(0, str(Path(__file__).parent))
from utils import inject_css, sidebar_branding, page_header, info_bar, section_heading, status_badge, footer
from utils.data_loader import get_metadata, find_forecast_file, load_netcdf
from utils.charts import forecast_heatmap
from utils.product_config import get_product

inject_css()
sidebar_branding()

# --- Hero banner ---
page_header(
    title="WASS2S Agrometeorological Forecast Dashboard",
    subtitle="Ghana Meteorological Agency (GMet) — Sub-Seasonal to Seasonal Forecasts",
    accent="#1B5E20",
)

# --- How to use ---
with st.expander("How to use this dashboard"):
    st.markdown("""
1. **Select a product** from the sidebar — expand any category to see sub-items
2. **Choose your season** and initialization month on the product page
3. **Explore the map** — hover for grid-cell values, zoom into your region
4. **Download data** — use the export buttons on each product page
    """)

# --- Info bar ---
meta = get_metadata()
if meta:
    info_bar([
        ("Forecast Year", str(meta.get("forecast_year", "—"))),
        ("Initialization", str(meta.get("initialization", "—"))),
    ])
else:
    st.info("No forecast data found. Ensure an Agro_PRESAGG_YYYY_ic_N/ directory exists.")

# --- Reference tables ---
col1, col2 = st.columns(2)

with col1:
    section_heading("Agronomic Indices")
    st.caption("Key parameters for planting decisions")
    st.markdown("""
| Product | What it tells you |
|---------|-------------------|
| **Onset** | Planting window |
| **1st Dry Spell** | First dry period risk |
| **Late Dry Spell** | Late-season drought risk |
| **Cessation** | When rains end |
| **Season Length** | Growing window |
""")

with col2:
    section_heading("Seasonal Forecasts")
    st.caption("3-month outlook products")
    st.markdown("""
| Season | Months | Products |
|--------|--------|----------|
| **MAM** | Mar–May | PRCP & TEMP |
| **JJA** | Jun–Aug | PRCP & TEMP |
| **SON** | Sep–Nov | PRCP & TEMP |
""")
    with st.expander("All seasons"):
        st.markdown("""
| Season | Months | Products |
|--------|--------|----------|
| **AMJ** | Apr–Jun | PRCP & TEMP |
| **MJJ** | May–Jul | PRCP & TEMP |
| **JAS** | Jul–Sep | PRCP & TEMP |
| **DJF** | Dec–Feb | PRCP & TEMP |
""")

# --- Consolidated forecasts ---
st.markdown("---")
badge = status_badge("Updated Jan 2026")
st.markdown(f'<div class="section-heading">Latest Consolidated Forecasts {badge}</div>', unsafe_allow_html=True)

tab_onset, tab_dryspell = st.tabs(["Onset", "Dry Spell"])

for tab, product_key, label in [(tab_onset, "onset", "Onset"), (tab_dryspell, "dry_spell", "Dry Spell")]:
    with tab:
        P = get_product(product_key)
        data_file = find_forecast_file(product_key, "det")
        if data_file:
            data, lat, lon, ds = load_netcdf(str(data_file), deterministic=True)
            if data is not None:
                fig = forecast_heatmap(
                    data.values, lon, lat, P["colorscale"], P["colorbar_title"],
                    f"Consolidated {label} Forecast",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No consolidated {label.lower()} forecast data found.")
        else:
            # Fallback to static image
            img_file = find_forecast_file(product_key, "image")
            if img_file:
                _, c, _ = st.columns([1, 2, 1])
                c.image(str(img_file), caption=f"Consolidated {label} Forecast", use_container_width=True)
            else:
                st.info(f"No consolidated {label.lower()} forecast found.")

footer()
