import streamlit as st
from pathlib import Path
import xarray as xr
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Skill Scores", page_icon=":chart_with_upwards_trend:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data" / "scores"
SCORE_DIR = Path("Agro_PRESAGG_2026_ic_1/scores")
EQUALY_DIR = Path("Agro_PRESAGG_2026_ic_1")

st.title("Forecast Skill Scores")
st.markdown("Hindcast validation metrics (1993-2016) showing forecast reliability.")

# --- Product and metric selectors ---
col1, col2 = st.columns(2)
with col1:
    product = st.selectbox("Forecast Product", [
        "Onset", "Dry Spell Onset", "Late Dry Spell",
        "Cessation", "Length of Season",
        "Seasonal PRCP", "Seasonal TEMP"
    ])
with col2:
    metric = st.selectbox("Skill Metric", ["GROC", "Pearson", "MAE", "RPSS"])

st.markdown(f"""
**Metric descriptions:**
- **GROC** (Generalized ROC): Area under ROC curve (0.5 = no skill, 1.0 = perfect)
- **Pearson**: Temporal correlation with observations (-1 to 1)
- **MAE**: Mean Absolute Error in days (lower is better)
- **RPSS**: Ranked Probability Skill Score (-inf to 1, >0 = skillful)
""")

st.markdown("---")

# --- Try consolidated NetCDF scores ---
st.subheader("Ensemble Skill Map")

equaly_file = EQUALY_DIR / f"equaly_{metric}.nc"
if equaly_file.exists():
    try:
        ds = xr.open_dataset(equaly_file)
        var_name = list(ds.data_vars)[0]
        data = ds[var_name]
        if "time" in data.dims:
            data = data.isel(time=0)

        lat_name = [d for d in data.dims if d.startswith("lat") or d == "Y"][0]
        lon_name = [d for d in data.dims if d.startswith("lon") or d == "X"][0]

        colorscale = "RdYlGn" if metric != "MAE" else "RdYlGn_r"

        fig = go.Figure(data=go.Heatmap(
            z=data.values, x=ds[lon_name].values, y=ds[lat_name].values,
            colorscale=colorscale, colorbar=dict(title=metric), hoverongaps=False,
        ))
        fig.update_layout(
            title=f"Equal-Weighted Ensemble — {metric}",
            xaxis_title="Longitude", yaxis_title="Latitude", height=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),
        )
        st.plotly_chart(fig, width="stretch")

        col1, col2, col3 = st.columns(3)
        valid = data.values[~np.isnan(data.values)]
        if len(valid) > 0:
            col1.metric("Min", f"{np.nanmin(valid):.3f}")
            col2.metric("Mean", f"{np.nanmean(valid):.3f}")
            col3.metric("Max", f"{np.nanmax(valid):.3f}")
        ds.close()
    except Exception as e:
        st.error(f"Error loading score data: {e}")
else:
    st.info(f"No consolidated {metric} score file found.")

# --- Individual model score images ---
st.markdown("---")
st.subheader("Individual Model Scores")

if SCORE_DIR.exists():
    score_images = sorted(SCORE_DIR.glob(f"*_{metric}.png"))
    if score_images:
        model_names = [f.stem.replace(f"_{metric}", "") for f in score_images]
        selected = st.selectbox("Select Model", model_names)
        idx = model_names.index(selected)
        st.image(str(score_images[idx]), caption=f"{selected} — {metric}", width="stretch")

        # Show grid of all models
        with st.expander("View All Models"):
            cols = st.columns(3)
            for i, (img, name) in enumerate(zip(score_images, model_names)):
                with cols[i % 3]:
                    st.image(str(img), caption=name, width="stretch")
    else:
        st.info(f"No {metric} score images found in {SCORE_DIR}")
else:
    st.info("Score directory not found. Run the pipeline to generate skill scores.")
