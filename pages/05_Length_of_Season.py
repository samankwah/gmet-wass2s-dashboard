import streamlit as st
from pathlib import Path
import xarray as xr
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Length of Season", page_icon=":calendar:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data" / "length_of_season"

st.title("Length of Growing Season Forecast")
st.markdown("Predicted duration (days) from rainfall onset to cessation — determines the available growing window.")

nc_det = DATA_DIR / "forecast_det.nc"
nc_prob = DATA_DIR / "forecast_prob.nc"

forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

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
                colorscale="Greens", colorbar=dict(title="Days"), hoverongaps=False,
            ))
            fig.update_layout(
                title="Length of Growing Season (Days)",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")

            col1, col2, col3 = st.columns(3)
            valid = data.values[~np.isnan(data.values)]
            if len(valid) > 0:
                col1.metric("Shortest Season", f"{int(np.nanmin(valid))} days")
                col2.metric("Mean Season", f"{int(np.nanmean(valid))} days")
                col3.metric("Longest Season", f"{int(np.nanmax(valid))} days")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        img = DATA_DIR / "consolidated_forecast.png"
        if img.exists():
            st.image(str(img), caption="Length of Season Forecast", width="stretch")
        else:
            st.info("No length-of-season data available yet. This is derived from onset and cessation forecasts.")
            st.markdown("""
            **How it works:**
            - Length of Season = Cessation Date - Onset Date
            - Requires both onset and cessation forecast pipelines to have run
            - Categorized as: Short / Normal / Long season
            """)
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
                title=f"Length of Season Probability - {selected}",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")
            ds.close()
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.info("No probabilistic length-of-season data available yet.")
