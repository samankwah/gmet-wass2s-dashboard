import streamlit as st
from pathlib import Path
import xarray as xr
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="1st Dry Spell Forecast", page_icon=":sun_with_face:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data" / "dry_spell"
FORECAST_DIR = Path("Agro_PRESAGG_2026_ic_1/forecasts")

st.title("1st Dry Spell Onset Forecast")
st.markdown("Predicted date of the first extended dry period after rainfall onset.")

forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

if forecast_type == "Deterministic":
    nc_file = DATA_DIR / "forecast_det.nc"
    fallback_nc = FORECAST_DIR / "Forecast_Det_PRCPdryspellonset_2025.nc"
    data_file = nc_file if nc_file.exists() else (fallback_nc if fallback_nc.exists() else None)

    if data_file:
        try:
            ds = xr.open_dataset(data_file)
            st.success(f"Loaded: {data_file.name}")
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
                colorscale="YlOrRd", colorbar=dict(title="Day of Year"), hoverongaps=False,
            ))
            fig.update_layout(
                title="Deterministic 1st Dry Spell Onset (Day of Year)",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")

            col1, col2, col3 = st.columns(3)
            valid = data.values[~np.isnan(data.values)]
            if len(valid) > 0:
                col1.metric("Earliest", f"Day {int(np.nanmin(valid))}")
                col2.metric("Mean", f"Day {int(np.nanmean(valid))}")
                col3.metric("Latest", f"Day {int(np.nanmax(valid))}")
            ds.close()
        except Exception as e:
            st.error(f"Error loading NetCDF: {e}")
    else:
        img_path = FORECAST_DIR / "Consolidated Forecast dryspellonset-2025.png"
        if img_path.exists():
            st.image(str(img_path), caption="Consolidated Dry Spell Forecast", width="stretch")
        else:
            st.warning("No dry spell forecast data found. Run the pipeline first.")

else:
    nc_file = DATA_DIR / "forecast_prob.nc"
    fallback_nc = FORECAST_DIR / "Forecast_Prob_PRCPdryspellonset_2025.nc"
    data_file = nc_file if nc_file.exists() else (fallback_nc if fallback_nc.exists() else None)

    if data_file:
        try:
            ds = xr.open_dataset(data_file)
            st.success(f"Loaded: {data_file.name}")
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
                title=f"Probabilistic Forecast — {selected}",
                xaxis_title="Longitude", yaxis_title="Latitude", height=600,
                yaxis=dict(scaleanchor="x", scaleratio=1),
            )
            st.plotly_chart(fig, width="stretch")
            ds.close()
        except Exception as e:
            st.error(f"Error loading NetCDF: {e}")
    else:
        st.warning("No probabilistic forecast data found. Run the pipeline first.")

st.markdown("---")
st.subheader("Individual Model Forecasts")
pdf_files = sorted(FORECAST_DIR.glob("*dryspell*.pdf")) if FORECAST_DIR.exists() else []
if pdf_files:
    model_names = [f.stem for f in pdf_files]
    selected_model = st.selectbox("Select Model", model_names)
    selected_pdf = pdf_files[model_names.index(selected_model)]
    with open(selected_pdf, "rb") as f:
        st.download_button(f"Download {selected_model}.pdf", f.read(), f"{selected_model}.pdf", "application/pdf")
else:
    st.info("No individual model PDFs found.")
