import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

_logo_path = Path(__file__).parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(
    page_title="GMet WASS2S Forecast Dashboard",
    page_icon=str(_logo_path) if _logo_path.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure utils is importable
sys.path.insert(0, str(Path(__file__).parent))
from utils import inject_css, sidebar_branding, info_bar, section_heading, status_badge, footer, disclaimer
from utils.data_loader import get_metadata, find_forecast_file, load_netcdf
from utils.charts import forecast_heatmap
from utils.product_config import get_product

inject_css()
sidebar_branding(page_id="dashboard")

# --- About this dashboard ---
with st.expander("About This Dashboard"):
    st.markdown("""
This dashboard presents sub-seasonal to seasonal agrometeorological forecast products
for Ghana, produced by the WASS2S system in collaboration with CILSS/AGRHYMET Regional
Climate Centre. Use the sidebar to navigate forecast products.
    """)

# --- Info bar ---
meta = get_metadata()
if meta:
    info_bar([
        ("Issued By", "Ghana Meteorological Agency"),
        ("Issue Date", datetime.now().strftime("%d %B %Y")),
        ("Forecast Year", str(meta.get("forecast_year", "\u2014"))),
        ("Initialization", str(meta.get("initialization", "\u2014"))),
    ])
else:
    st.info("No forecast data found. Ensure an Agro_PRESAGG_YYYY_ic_N/ directory exists.")

# --- Reference tables ---
col1, col2 = st.columns(2)

with col1:
    section_heading("Agronomic Indices", caption="Key parameters for planting decisions")
    _agro_indices = [
        ("Onset", "Planting window start date"),
        ("1st Dry Spell", "First dry period risk"),
        ("Late Dry Spell", "Late-season drought risk"),
        ("Cessation", "When rains end"),
        ("Season Length", "Total growing window"),
    ]
    _cards_html = "".join(
        f'<div class="summary-card">'
        f'<div class="sc-name">{name}</div>'
        f'<div class="sc-desc">{desc}</div>'
        f'</div>'
        for name, desc in _agro_indices
    )
    st.html(_cards_html)

with col2:
    section_heading("Seasonal Forecasts", caption="3-month outlook products")
    _season_groups = [
        ("Major Season (South)", [("MAM", "Mar\u2013May"), ("AMJ", "Apr\u2013Jun"), ("MJJ", "May\u2013Jul")]),
        ("Major Season (North)", [("MJJ", "May\u2013Jul"), ("JJA", "Jun\u2013Aug"), ("JAS", "Jul\u2013Sep")]),
        ("Minor Season", [("SON", "Sep\u2013Nov")]),
        ("Dry Season", [("DJF", "Dec\u2013Feb")]),
    ]
    _seasons_html = ""
    for group_label, seasons in _season_groups:
        _seasons_html += f'<div class="season-group-label">{group_label}</div>'
        _seasons_html += '<div class="season-chips">'
        for code, months in seasons:
            _seasons_html += (
                f'<span class="season-chip">'
                f'<span class="sc-code">{code}</span>'
                f'<span class="sc-months">{months}</span>'
                f'</span>'
            )
        _seasons_html += '</div>'
    st.html(_seasons_html)

# --- Consolidated forecasts ---
st.markdown("---")
st.html('<div class="section-heading">Latest Consolidated Forecasts \u2014 Updated January 2026</div>')

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
                    use_week_labels=P.get("use_week_labels", False),
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

st.markdown("<br>", unsafe_allow_html=True)
disclaimer()
footer()
