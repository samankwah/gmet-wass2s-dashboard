import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

_logo_path = Path(__file__).parent.parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(page_title="Station Data", page_icon=str(_logo_path) if _logo_path.exists() else None, layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, footer, disclaimer
from utils.product_config import get_product
from utils.charts import station_map
from utils.data_loader import get_data_dirs

P = get_product("station_data")
inject_css()
sidebar_branding(page_id="station")

data_root, _, _, obs_dir = get_data_dirs()

# Map query-param value → (display name, CSV candidates)
PRODUCT_MAP = {
    "onset":          ("Onset",               ["Onset_2025.csv", "onset_stations.csv"]),
    "dry_spell":      ("1st Dry Spell",       ["1st_Dry_Spell_2025.csv", "dry_spell_stations.csv"]),
    "late_dry_spell": ("Late Dry Spell",      ["late_dry_spell_stations.csv"]),
    "cessation":      ("Cessation",           ["cessation_stations.csv"]),
    "MAM":            ("Seasonal PRCP (MAM)", ["MAM_1981-2025.csv", "MAM_stations.csv"]),
    "AMJ":            ("Seasonal PRCP (AMJ)", ["AMJ_1981-2025.csv", "AMJ_stations.csv"]),
    "MJJ":            ("Seasonal PRCP (MJJ)", ["MJJ_stations.csv"]),
    "JJA":            ("Seasonal PRCP (JJA)", ["JJA_stations.csv"]),
    "JAS":            ("Seasonal PRCP (JAS)", ["JAS_stations.csv"]),
    "SON":            ("Seasonal PRCP (SON)", ["SON_stations.csv"]),
    "DJF":            ("Seasonal PRCP (DJF)", ["DJF_stations.csv"]),
}

# Read product from query params (default to onset)
product_key = st.query_params.get("product", "onset")
if product_key not in PRODUCT_MAP:
    product_key = "onset"
st.query_params["product"] = product_key

product, csv_candidates = PRODUCT_MAP[product_key]

st.markdown(f"### Station-Level Predictions — {product}")

csv_loaded = False
df = None

# Build search directories from auto-detected data root + project root
project_root = Path(__file__).parent.parent.parent
search_dirs = []
if obs_dir:
    search_dirs.append(obs_dir)
if data_root:
    search_dirs.append(data_root)
search_dirs.append(project_root)

for csv_name in csv_candidates:
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
    # --- Extract station info from CSV header rows ---
    # Row 0: STATION, name1, name2, ...
    # Row 1: LAT, lat1, lat2, ...
    # Row 2: LON, lon1, lon2, ...
    # Rows 3+: year data
    first_col = df.columns[0]
    station_cols = df.columns[1:]  # station names from header

    # Check if the CSV has LAT/LON metadata rows
    has_meta = (
        len(df) >= 2
        and str(df.iloc[0][first_col]).strip().upper() == "LAT"
        and str(df.iloc[1][first_col]).strip().upper() == "LON"
    )

    if has_meta:
        station_names = list(station_cols)
        lats = pd.to_numeric(df.iloc[0][station_cols], errors="coerce").tolist()
        lons = pd.to_numeric(df.iloc[1][station_cols], errors="coerce").tolist()

        # Data rows start at index 2
        data_df = df.iloc[2:].copy()
        data_df[first_col] = pd.to_numeric(data_df[first_col], errors="coerce")
        for col in station_cols:
            data_df[col] = pd.to_numeric(data_df[col], errors="coerce")

        # Determine which stations have valid data in the latest year
        if len(data_df) > 0:
            latest_row = data_df.iloc[-1]
            has_data = [
                pd.notna(latest_row[col]) and float(latest_row[col]) != -999
                for col in station_cols
            ]
        else:
            has_data = [False] * len(station_names)

        # --- Station Map ---
        fig = station_map(station_names, lats, lons, has_data, product)
        st.plotly_chart(fig, use_container_width=True)

        # Replace -999 with NA for display
        display_df = data_df.replace(-999, pd.NA)

    else:
        # No LAT/LON metadata — skip map, use original df
        display_df = df.replace(-999, pd.NA)

    # --- Station Data Table (in expander) ---
    with st.expander("Station Data Table", expanded=False):
        st.dataframe(display_df, use_container_width=True, height=500)

    # --- Download ---
    with st.expander("Download", expanded=False):
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{product.replace(' ', '_').lower()}_stations.csv",
            mime="text/csv",
        )

    # --- Time Series Chart (in expander) ---
    numeric_cols = display_df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        with st.expander("Historical Time Series", expanded=False):
            id_col = display_df.columns[0]
            if has_meta:
                # Stations are columns — let user pick a station column
                selected_station = st.selectbox("Select Station", list(station_cols))
                vals = display_df[[id_col, selected_station]].dropna()
                if len(vals) > 0:
                    fig = px.line(
                        x=vals[id_col], y=vals[selected_station],
                        title=f"{selected_station} — {product}",
                        labels={"x": "Year", "y": product},
                    )
                    fig.update_layout(
                        title=dict(x=0.5, xanchor="center"),
                        margin=dict(l=60, r=20, t=50, b=50),
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                stations = display_df[id_col].unique()
                if len(stations) > 0 and len(stations) <= 50:
                    selected_station = st.selectbox("Select Station", stations)
                    station_data = display_df[display_df[id_col] == selected_station]
                    if len(station_data) > 0:
                        year_cols = [c for c in numeric_cols if str(c).isdigit() or "year" in str(c).lower()]
                        if year_cols:
                            vals = station_data[year_cols].iloc[0].dropna()
                            fig = px.line(
                                x=vals.index, y=vals.values,
                                title=f"{selected_station} — {product}",
                                labels={"x": "Year", "y": product},
                            )
                            fig.update_layout(
                                title=dict(x=0.5, xanchor="center"),
                                margin=dict(l=60, r=20, t=50, b=50),
                            )
                            st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No station data found for '{product}'.")
    st.markdown("""
**Expected data format:**
- CSV with stations as columns and years as rows
- Row 1: Station names, Row 2: LAT, Row 3: LON
- Values: day-of-year (for indices) or mm (for rainfall)
- Missing values coded as -999
""")

disclaimer(P["description"], P["farmer_guidance"])
footer()
