import streamlit as st
import sys
from pathlib import Path

_logo_path = Path(__file__).parent.parent / "assets" / "smart_logo_GMet.png"
st.set_page_config(page_title="Agronomic Forecasts", page_icon=str(_logo_path) if _logo_path.exists() else None, layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import inject_css, sidebar_branding, metric_cards, footer, disclaimer
from utils.product_config import get_product
from utils.charts import forecast_heatmap, dominant_tercile_map
from utils.data_loader import (
    find_forecast_file, find_forecast_files, load_netcdf,
    load_probabilistic, compute_stats, format_metric, get_data_dirs,
    get_metadata, pdf_to_image,
)

AGRO_KEYS = ["onset", "dry_spell", "late_dry_spell", "cessation", "length_of_season"]

inject_css()
sidebar_branding(page_id="agronomic")

qp = st.query_params.get("product", "onset")
product_key = qp if qp in AGRO_KEYS else "onset"
P = get_product(product_key)

# ─── Consolidated Forecast ───
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
                forecast_year=forecast_year,
                use_week_labels=P.get("use_week_labels", False),
            )
            st.plotly_chart(fig, use_container_width=True)
            stats = compute_stats(data)
            if stats[0] is not None:
                metric_cards(
                    [(lbl, format_metric(P["metric_fmt"], v, forecast_year=forecast_year))
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
                category_labels=P.get("category_labels"),
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
from utils import section_heading
section_heading("Individual Model Forecasts", caption="Browse outputs from each contributing climate model")

pdf_files = find_forecast_files(product_key, "pdf")
if pdf_files:
    model_names = [f.stem for f in pdf_files]
    col_select, col_dl = st.columns([3, 1], vertical_alignment="bottom")
    with col_select:
        selected_model = st.selectbox("Select Model", model_names, label_visibility="collapsed")
    selected_pdf = pdf_files[model_names.index(selected_model)]
    with col_dl:
        with open(selected_pdf, "rb") as f:
            st.download_button(
                "Download PDF", f.read(), f"{selected_model}.pdf",
                "application/pdf", use_container_width=True,
            )
    # Render selected PDF as image
    png_bytes = pdf_to_image(str(selected_pdf))
    if png_bytes:
        _, img_col, _ = st.columns([1, 2, 1])
        img_col.image(png_bytes, caption=f"{selected_model}", use_container_width=True)
else:
    st.info(f"No individual model PDFs found for {P['short']}.")

disclaimer(P["description"], P["farmer_guidance"])
footer()
