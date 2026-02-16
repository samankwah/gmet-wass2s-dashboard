import streamlit as st
import sys
from pathlib import Path

_logo_path = Path(__file__).parent.parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(page_title="Forecast Skill", page_icon=str(_logo_path) if _logo_path.exists() else None, layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, metric_cards, footer, disclaimer
from utils.product_config import get_product
from utils.charts import forecast_heatmap
from utils.data_loader import load_netcdf, compute_stats, get_data_dirs

P = get_product("skill_scores")
inject_css()
sidebar_branding(page_id="skill")

st.markdown("### Forecast Skill Scores")

data_root, _, score_dir, _ = get_data_dirs()

col1, col2 = st.columns(2)
with col1:
    product = st.selectbox("Forecast Product", [
        "Onset", "Dry Spell Onset", "Late Dry Spell",
        "Cessation", "Length of Season",
        "Seasonal PRCP", "Seasonal TEMP"
    ])
with col2:
    _metric_options = ["GROC", "Pearson", "MAE", "RPSS"]
    _metric_param = st.query_params.get("metric")
    _metric_idx = _metric_options.index(_metric_param) if _metric_param in _metric_options else 0
    metric = st.selectbox("Skill Metric", _metric_options, index=_metric_idx)

# Sync selectbox value back to query params so sidebar checkmark updates
st.query_params["metric"] = metric

with st.expander("Metric Descriptions", expanded=False):
    st.markdown("""
| Metric | Description | Range | Good values |
|--------|-------------|-------|-------------|
| **GROC** | Generalized ROC area | 0.5 \u2013 1.0 | > 0.6 |
| **Pearson** | Temporal correlation | -1 \u2013 1 | > 0.3 |
| **MAE** | Mean Absolute Error (days) | 0 \u2013 \u221E | Lower is better |
| **RPSS** | Ranked Probability Skill Score | -\u221E \u2013 1 | > 0 |
""")

st.markdown("---")

# Ensemble skill map
st.markdown("#### Ensemble Skill Map")

_SKILL_BOUNDS = {
    "GROC":    {"zmin": 0.0, "zmax": 1.0, "colorscale": "RdBu_r"},
    "Pearson": {"zmin": -1.0, "zmax": 1.0, "colorscale": "RdBu_r"},
    "MAE":     {"zmin": 0.0, "zmax": 50.0, "colorscale": "Viridis"},
    "RPSS":    {"zmin": -1.5, "zmax": 1.0, "colorscale": "RdBu_r"},
}

equaly_file = data_root / f"equaly_{metric}.nc" if data_root else None
if equaly_file and equaly_file.exists():
    data, lat, lon, ds = load_netcdf(str(equaly_file), deterministic=True)
    if data is not None:
        bounds = _SKILL_BOUNDS.get(metric, {"zmin": None, "zmax": None, "colorscale": "RdYlGn"})
        fig = forecast_heatmap(data.values, lon, lat, bounds["colorscale"], metric,
                               f"Equal-Weighted Ensemble \u2014 {metric}",
                               zmin=bounds["zmin"], zmax=bounds["zmax"])
        st.plotly_chart(fig, use_container_width=True)
        stats = compute_stats(data)
        if stats[0] is not None:
            metric_cards(
                [("Min", f"{stats[0]:.3f}"), ("Mean", f"{stats[1]:.3f}"), ("Max", f"{stats[2]:.3f}")],
                P["accent"], P["light_bg"],
            )
else:
    st.info(f"No consolidated {metric} score file found.")

# Individual model scores
st.markdown("---")
st.markdown("#### Individual Model Scores")

if score_dir and score_dir.exists():
    score_images = sorted(score_dir.glob(f"*_{metric}.png"))
    if score_images:
        model_names = [f.stem.replace(f"_{metric}", "") for f in score_images]
        selected = st.selectbox("Select Model", model_names)
        idx = model_names.index(selected)
        _, col_img, _ = st.columns([1, 2, 1])
        with col_img:
            st.image(str(score_images[idx]), caption=f"{selected} \u2014 {metric}", use_container_width=True)

        with st.expander("View All Models"):
            cols = st.columns(3)
            for i, (img, name) in enumerate(zip(score_images, model_names)):
                with cols[i % 3]:
                    st.image(str(img), caption=name, use_container_width=True)
    else:
        st.info(f"No {metric} score images found.")
else:
    st.info("Score directory not found.")

disclaimer(P["description"], P["farmer_guidance"])
footer()
