import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="Agronomic Forecasts", page_icon="\U0001F331", layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, page_header, metric_cards, about_product, footer
from utils.product_config import get_product
from utils.charts import forecast_heatmap, dominant_tercile_map
from utils.data_loader import (
    find_forecast_file, find_forecast_files, load_netcdf,
    load_probabilistic, compute_stats, format_metric, get_data_dirs,
    get_metadata, pdf_to_image,
)

# --- Product registry for this page ---
AGRO_PRODUCTS = [
    ("onset", "Onset"),
    ("dry_spell", "1st Dry Spell"),
    ("late_dry_spell", "Late Dry Spell"),
    ("cessation", "Cessation"),
    ("length_of_season", "Season Length"),
]

inject_css()
sidebar_branding()

page_header("Agronomic Forecasts", "Seasonal agronomic forecast products for Ghana", "#2E7D32", "\U0001F331")

# --- Product selector ---
product_labels = [label for _, label in AGRO_PRODUCTS]
product_keys = [key for key, _ in AGRO_PRODUCTS]

qp = st.query_params.get("product", None)
default_idx = product_keys.index(qp) if qp in product_keys else 0

selected_label = st.selectbox("Select Product", product_labels, index=default_idx,
                              label_visibility="collapsed")
product_key = AGRO_PRODUCTS[product_labels.index(selected_label)][0]
P = get_product(product_key)

# --- About this product ---
about_product(P["description"], P["farmer_guidance"])

# ─── Consolidated Forecast ───
st.markdown("---")
st.markdown("### Consolidated Forecast")

forecast_type = st.radio("Forecast Type", ["Deterministic", "Probabilistic"], horizontal=True)

# Find consolidated PDFs for download
_, forecast_dir, _, _ = get_data_dirs()
meta = get_metadata()
forecast_year = meta.get("forecast_year")

consolidated_pattern = P.get("consolidated_pdf_pattern")
det_pdf = None
prob_pdf = None
if consolidated_pattern and forecast_dir and forecast_dir.exists():
    for pdf in sorted(forecast_dir.glob(consolidated_pattern)):
        if forecast_year and str(forecast_year) in pdf.name:
            prob_pdf = pdf
        else:
            det_pdf = pdf

if forecast_type == "Deterministic":
    data_file = find_forecast_file(product_key, "det")
    if data_file:
        data, lat, lon, ds = load_netcdf(str(data_file), deterministic=True)
        if data is not None:
            fig = forecast_heatmap(
                data.values, lon, lat, P["colorscale"], P["colorbar_title"],
                f"Consolidated {P['short']} Forecast (Deterministic)",
            )
            st.plotly_chart(fig, use_container_width=True)
            stats = compute_stats(data)
            if stats[0] is not None:
                metric_cards(
                    [(lbl, format_metric(P["metric_fmt"], v))
                     for lbl, v in zip(P["metric_labels"], stats)],
                    P["accent"], P["light_bg"],
                )
    else:
        # Fallback to static image
        img_file = find_forecast_file(product_key, "image")
        if img_file:
            _, img_col, _ = st.columns([1, 2, 1])
            img_col.image(str(img_file), caption=f"Consolidated {P['short']} Forecast (Deterministic)",
                          use_container_width=True)
        else:
            st.info(f"No deterministic forecast data available for {P['short']}.")
    if det_pdf:
        with open(det_pdf, "rb") as f:
            st.download_button("Download Deterministic PDF", f.read(),
                               det_pdf.name, "application/pdf", key="dl_det_consolidated")
else:
    data_file = find_forecast_file(product_key, "prob")
    if data_file:
        categories, lat, lon = load_probabilistic(str(data_file))
        if categories:
            fig = dominant_tercile_map(
                categories, lon, lat,
                f"Consolidated {P['short']} Forecast (Probabilistic)",
                reverse_cmap=P.get("reverse_cmap", False),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to static PDF rendered as image
        if prob_pdf:
            png_bytes = pdf_to_image(str(prob_pdf))
            if png_bytes:
                _, img_col, _ = st.columns([1, 2, 1])
                img_col.image(png_bytes, caption=f"Consolidated {P['short']} Forecast (Probabilistic)",
                              use_container_width=True)
            else:
                st.warning("Could not render the probabilistic PDF as an image.")
        else:
            st.info(f"No probabilistic forecast data available for {P['short']}.")
    if prob_pdf:
        with open(prob_pdf, "rb") as f:
            st.download_button("Download Probabilistic PDF", f.read(),
                               prob_pdf.name, "application/pdf", key="dl_prob_consolidated")

# ─── Section 3: Individual Model Forecasts ───
st.markdown("---")
st.markdown("### Individual Model Forecasts")

pdf_files = find_forecast_files(product_key, "pdf")
if pdf_files:
    model_names = [f.stem for f in pdf_files]
    selected_model = st.selectbox("Select Model", model_names)
    selected_pdf = pdf_files[model_names.index(selected_model)]
    with open(selected_pdf, "rb") as f:
        st.download_button(
            f"Download {selected_model}.pdf",
            f.read(), f"{selected_model}.pdf", "application/pdf",
        )
else:
    st.info(f"No individual model PDFs found for {P['short']}.")

footer()
