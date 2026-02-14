import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Station Data", page_icon=":round_pushpin:", layout="wide")

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
OBS_DIR = Path("Agro_PRESAGG_2026_ic_1/Observation")

st.title("Station-Level Predictions & Observations")
st.markdown("Point forecasts and historical data for 34 synoptic stations across Ghana.")

# --- Product selector ---
product = st.selectbox("Select Product", [
    "Onset", "1st Dry Spell", "Late Dry Spell", "Cessation",
    "Seasonal PRCP (MAM)", "Seasonal PRCP (AMJ)", "Seasonal PRCP (MJJ)",
    "Seasonal PRCP (JJA)", "Seasonal PRCP (JAS)", "Seasonal PRCP (SON)",
    "Seasonal PRCP (DJF)",
])

# --- Try to load station CSV data ---
# Map product names to likely CSV filenames
csv_map = {
    "Onset": ["Onset_2025.csv", "onset_stations.csv"],
    "1st Dry Spell": ["1st_Dry_Spell_2025.csv", "dry_spell_stations.csv"],
    "Late Dry Spell": ["late_dry_spell_stations.csv"],
    "Cessation": ["cessation_stations.csv"],
    "Seasonal PRCP (MAM)": ["MAM_1981-2025.csv", "MAM_stations.csv"],
    "Seasonal PRCP (AMJ)": ["AMJ_1981-2025.csv", "AMJ_stations.csv"],
    "Seasonal PRCP (MJJ)": ["MJJ_stations.csv"],
    "Seasonal PRCP (JJA)": ["JJA_stations.csv"],
    "Seasonal PRCP (JAS)": ["JAS_stations.csv"],
    "Seasonal PRCP (SON)": ["SON_stations.csv"],
    "Seasonal PRCP (DJF)": ["DJF_stations.csv"],
}

csv_loaded = False
df = None

for csv_name in csv_map.get(product, []):
    # Check multiple locations
    for search_dir in [DATA_DIR, OBS_DIR, Path("Agro_PRESAGG_2026_ic_1")]:
        csv_path = search_dir / csv_name
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                st.success(f"Loaded: {csv_path.name}")
                csv_loaded = True
                break
            except Exception as e:
                st.error(f"Error reading {csv_path}: {e}")
    if csv_loaded:
        break

if csv_loaded and df is not None:
    # Replace -999 with NaN
    df = df.replace(-999, pd.NA)

    st.subheader("Station Data Table")
    st.dataframe(df, use_container_width=True, height=500)

    # Download button
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"{product.replace(' ', '_').lower()}_stations.csv",
        mime="text/csv",
    )

    # Try to plot if there are numeric columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        st.subheader("Historical Time Series")
        # Assume first column is station name or ID
        id_col = df.columns[0]
        stations = df[id_col].unique()

        if len(stations) > 0 and len(stations) <= 50:
            selected_station = st.selectbox("Select Station", stations)
            station_data = df[df[id_col] == selected_station]

            if len(station_data) > 0:
                # Try to plot years vs values
                year_cols = [c for c in numeric_cols if str(c).isdigit() or "year" in str(c).lower()]
                if year_cols:
                    vals = station_data[year_cols].iloc[0].dropna()
                    fig = px.line(x=vals.index, y=vals.values,
                                 title=f"{selected_station} — {product}",
                                 labels={"x": "Year", "y": product})
                    st.plotly_chart(fig, width="stretch")
        else:
            # Plot latest column as bar chart across stations
            if len(numeric_cols) > 0:
                latest_col = numeric_cols[-1]
                fig = px.bar(df, x=id_col, y=latest_col,
                             title=f"{product} — {latest_col}",
                             labels={id_col: "Station", latest_col: product})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")
else:
    st.info(f"No station data found for '{product}'. Run the pipeline to generate station-level predictions.")
    st.markdown("""
    **Expected data format:**
    - CSV with stations as rows and years as columns
    - First column: station name/ID
    - Values: day-of-year (for indices) or mm (for rainfall)
    - Missing values coded as -999
    """)

st.markdown("---")
st.caption("Data source: Ghana Meteorological Agency — 34 synoptic stations")
