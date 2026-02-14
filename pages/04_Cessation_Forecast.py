import streamlit as st
from pathlib import Path
import xarray as xr
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Cessation Forecast", page_icon=":fallen_leaf:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data" / "cessation"

st.title("Rainfall Cessation Forecast")
st.markdown("Predicted date when the rainy season ends — important for harvest timing and post-season planning.")

forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

nc_det = DATA_DIR / "forecast_det.nc"
nc_prob = DATA_DIR / "forecast_prob.nc"

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
                colorscale="RdYlBu_r", colorbar=dict(title="Day of Year"), hoverongaps=False,
            ))
            fig.update_layout(
                title="Deterministic Cessation Forecast (Day of Year)",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")

            col1, col2, col3 = st.columns(3)
            valid = data.values[~np.isnan(data.values)]
            if len(valid) > 0:
                col1.metric("Earliest Cessation", f"Day {int(np.nanmin(valid))}")
                col2.metric("Mean Cessation", f"Day {int(np.nanmean(valid))}")
                col3.metric("Latest Cessation", f"Day {int(np.nanmax(valid))}")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        img = DATA_DIR / "consolidated_forecast.png"
        if img.exists():
            st.image(str(img), caption="Cessation Forecast", width="stretch")
        else:
            st.info("No cessation forecast data available yet. Run the pipeline to generate.")
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
                colorscale="RdYlGn", colorbar=dict(title="Probability"),
                zmin=0, zmax=1, hoverongaps=False,
            ))
            fig.update_layout(
                title=f"Probabilistic Cessation - {selected}",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.info("No probabilistic cessation forecast data available yet.")
