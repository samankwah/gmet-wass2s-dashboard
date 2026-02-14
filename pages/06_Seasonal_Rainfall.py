import streamlit as st
from pathlib import Path
import xarray as xr
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Seasonal Rainfall", page_icon=":cloud_with_rain:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data" / "seasonal_prcp"

st.title("Seasonal Rainfall Forecast")
st.markdown("Seasonal precipitation outlook for Ghana — Below Normal, Near Normal, or Above Normal.")

SEASONS = {
    "MAM": "March - April - May",
    "AMJ": "April - May - June",
    "MJJ": "May - June - July",
    "JJA": "June - July - August",
    "JAS": "July - August - September",
    "SON": "September - October - November",
    "DJF": "December - January - February",
}

col1, col2 = st.columns([1, 3])
with col1:
    season = st.selectbox("Select Season", list(SEASONS.keys()), format_func=lambda s: f"{s} ({SEASONS[s]})")
with col2:
    forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

st.markdown(f"### {season} — {SEASONS[season]}")

nc_det = DATA_DIR / f"{season}_det.nc"
nc_prob = DATA_DIR / f"{season}_prob.nc"

if forecast_type == "Deterministic":
    if nc_det.exists():
        try:
            ds = xr.open_dataset(nc_det)
            var_name = list(ds.data_vars)[0]
            data = ds[var_name]
            if "time" in data.dims:
                data = data.isel(time=0)
            if "member" in data.dims:
                data = data.mean(dim="member")

            lat_name = [d for d in data.dims if d.startswith("lat") or d == "Y"][0]
            lon_name = [d for d in data.dims if d.startswith("lon") or d == "X"][0]

            fig = go.Figure(data=go.Heatmap(
                z=data.values, x=ds[lon_name].values, y=ds[lat_name].values,
                colorscale="Blues", colorbar=dict(title="Rainfall (mm)"), hoverongaps=False,
            ))
            fig.update_layout(
                title=f"Deterministic {season} Rainfall Forecast",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")

            col1, col2, col3 = st.columns(3)
            valid = data.values[~np.isnan(data.values)]
            if len(valid) > 0:
                col1.metric("Min Rainfall", f"{np.nanmin(valid):.0f} mm")
                col2.metric("Mean Rainfall", f"{np.nanmean(valid):.0f} mm")
                col3.metric("Max Rainfall", f"{np.nanmax(valid):.0f} mm")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        img = DATA_DIR / f"{season}_forecast.png"
        if img.exists():
            st.image(str(img), caption=f"{season} Rainfall Forecast", width="stretch")
        else:
            st.info(f"No {season} rainfall forecast data available. Run the seasonal PRCP pipeline.")

else:
    if nc_prob.exists():
        try:
            ds = xr.open_dataset(nc_prob)
            categories = list(ds.data_vars)
            selected = st.selectbox("Tercile Category", categories)
            data = ds[selected]
            if "time" in data.dims:
                data = data.isel(time=0)

            lat_name = [d for d in data.dims if d.startswith("lat") or d == "Y"][0]
            lon_name = [d for d in data.dims if d.startswith("lon") or d == "X"][0]

            fig = go.Figure(data=go.Heatmap(
                z=data.values, x=ds[lon_name].values, y=ds[lat_name].values,
                colorscale="RdYlBu", colorbar=dict(title="Probability"),
                zmin=0, zmax=1, hoverongaps=False,
            ))
            fig.update_layout(
                title=f"{season} Rainfall Probability - {selected}",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.info(f"No probabilistic {season} rainfall data available.")

# Show all seasons overview
st.markdown("---")
st.subheader("All Seasons Overview")
available = []
for s in SEASONS:
    det = (DATA_DIR / f"{s}_det.nc").exists()
    prob = (DATA_DIR / f"{s}_prob.nc").exists()
    img = (DATA_DIR / f"{s}_forecast.png").exists()
    status = "Available" if (det or prob or img) else "Not yet generated"
    available.append({"Season": s, "Months": SEASONS[s], "Status": status})

st.table(available)
