import streamlit as st
import sys
from pathlib import Path

_logo_path = Path(__file__).parent.parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(page_title="Rainfall Outlook", page_icon=str(_logo_path) if _logo_path.exists() else None, layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, metric_cards, footer, disclaimer
from utils.product_config import get_product
from utils.charts import forecast_heatmap
from utils.data_loader import load_netcdf, load_probabilistic, compute_stats, format_metric, get_data_dirs

P = get_product("seasonal_prcp")
inject_css()
sidebar_branding(page_id="rainfall")

SEASONS = {
    "MAM": "March \u2013 May",
    "AMJ": "April \u2013 June",
    "MJJ": "May \u2013 July",
    "JJA": "June \u2013 August",
    "JAS": "July \u2013 September",
    "SON": "September \u2013 November",
    "DJF": "December \u2013 February",
}

qp = st.query_params.get("product", "MAM")
season = qp if qp in SEASONS else "MAM"

st.markdown(f"### Seasonal Rainfall Forecast \u2014 {season} ({SEASONS[season]})")

forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

data_root, forecast_dir, _, _ = get_data_dirs()

# Look for season-specific NC files in forecasts dir
nc_det = None
nc_prob = None
if forecast_dir and forecast_dir.exists():
    det_matches = sorted(forecast_dir.glob(f"*Det*PRCP*{season}*.nc"))
    if det_matches:
        nc_det = det_matches[0]
    prob_matches = sorted(forecast_dir.glob(f"*Prob*PRCP*{season}*.nc"))
    if prob_matches:
        nc_prob = prob_matches[0]

if forecast_type == "Deterministic":
    if nc_det and nc_det.exists():
        data, lat, lon, ds = load_netcdf(str(nc_det), deterministic=True)
        if data is not None:
            fig = forecast_heatmap(data.values, lon, lat, P["colorscale"], P["colorbar_title"],
                                   f"Deterministic {season} Rainfall Forecast")
            st.plotly_chart(fig, use_container_width=True)
            stats = compute_stats(data)
            if stats[0] is not None:
                metric_cards(
                    [(lbl, format_metric(P["metric_fmt"], v)) for lbl, v in zip(P["metric_labels"], stats)],
                    P["accent"], P["light_bg"],
                )
    else:
        # Try to find a consolidated image
        if forecast_dir and forecast_dir.exists():
            img_matches = sorted(forecast_dir.glob(f"*{season}*PRCP*.png"))
            if img_matches:
                st.image(str(img_matches[0]), caption=f"{season} Rainfall Forecast", use_container_width=True)
            else:
                st.info(f"No {season} rainfall forecast data available.")
        else:
            st.info(f"No {season} rainfall forecast data available.")
else:
    if nc_prob and nc_prob.exists():
        categories, lat, lon = load_probabilistic(str(nc_prob))
        if categories:
            cat_names = list(categories.keys())
            selected = st.selectbox("Tercile Category", cat_names)
            fig = forecast_heatmap(categories[selected], lon, lat,
                                   "RdYlBu", "Probability", f"{season} Rainfall Probability \u2014 {selected}",
                                   zmin=0, zmax=1)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No probabilistic {season} rainfall data available.")

# All seasons overview
st.markdown("---")
st.markdown("#### All Seasons Overview")
available = []
for s in SEASONS:
    has_det = bool(forecast_dir and sorted(forecast_dir.glob(f"*Det*PRCP*{s}*.nc"))) if forecast_dir and forecast_dir.exists() else False
    has_prob = bool(forecast_dir and sorted(forecast_dir.glob(f"*Prob*PRCP*{s}*.nc"))) if forecast_dir and forecast_dir.exists() else False
    status = "Available" if (has_det or has_prob) else "Not available"
    available.append({"Season": s, "Months": SEASONS[s], "Status": status})
st.table(available)

disclaimer(P["description"], P["farmer_guidance"])
footer()
