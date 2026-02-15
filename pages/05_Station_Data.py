import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Station Data", page_icon="\U0001F4CD", layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, page_header, about_product, footer
from utils.product_config import get_product
from utils.data_loader import get_data_dirs

P = get_product("station_data")
inject_css()
sidebar_branding()

page_header(P["title"], "Point forecasts and historical data for 34 synoptic stations", P["accent"], P["icon"])
about_product(P["description"], P["farmer_guidance"])

data_root, _, _, obs_dir = get_data_dirs()

product = st.selectbox("Select Product", [
    "Onset", "1st Dry Spell", "Late Dry Spell", "Cessation",
    "Seasonal PRCP (MAM)", "Seasonal PRCP (AMJ)", "Seasonal PRCP (MJJ)",
    "Seasonal PRCP (JJA)", "Seasonal PRCP (JAS)", "Seasonal PRCP (SON)",
    "Seasonal PRCP (DJF)",
])

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

# Build search directories from auto-detected data root
search_dirs = []
if obs_dir:
    search_dirs.append(obs_dir)
if data_root:
    search_dirs.append(data_root)

for csv_name in csv_map.get(product, []):
    for search_dir in search_dirs:
        csv_path = search_dir / csv_name
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                csv_loaded = True
                break
            except Exception as e:
                st.error(f"Error reading {csv_path}: {e}")
    if csv_loaded:
        break

if csv_loaded and df is not None:
    df = df.replace(-999, pd.NA)

    st.markdown("#### Station Data Table")
    st.dataframe(df, use_container_width=True, height=500)

    csv_data = df.to_csv(index=False)
    st.download_button(
        label="\U0001F4E5 Download CSV",
        data=csv_data,
        file_name=f"{product.replace(' ', '_').lower()}_stations.csv",
        mime="text/csv",
    )

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        st.markdown("#### Historical Time Series")
        id_col = df.columns[0]
        stations = df[id_col].unique()

        if len(stations) > 0 and len(stations) <= 50:
            selected_station = st.selectbox("Select Station", stations)
            station_data = df[df[id_col] == selected_station]

            if len(station_data) > 0:
                year_cols = [c for c in numeric_cols if str(c).isdigit() or "year" in str(c).lower()]
                if year_cols:
                    vals = station_data[year_cols].iloc[0].dropna()
                    fig = px.line(x=vals.index, y=vals.values,
                                 title=f"{selected_station} \u2014 {product}",
                                 labels={"x": "Year", "y": product})
                    fig.update_layout(
                        title=dict(x=0.5, xanchor="center"),
                        margin=dict(l=60, r=20, t=50, b=50),
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            if len(numeric_cols) > 0:
                latest_col = numeric_cols[-1]
                fig = px.bar(df, x=id_col, y=latest_col,
                             title=f"{product} \u2014 {latest_col}",
                             labels={id_col: "Station", latest_col: product})
                fig.update_layout(
                    xaxis_tickangle=-45,
                    title=dict(x=0.5, xanchor="center"),
                    margin=dict(l=60, r=20, t=50, b=50),
                )
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No station data found for '{product}'.")
    st.markdown("""
**Expected data format:**
- CSV with stations as rows and years as columns
- First column: station name/ID
- Values: day-of-year (for indices) or mm (for rainfall)
- Missing values coded as -999
""")

footer()
