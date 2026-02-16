"""Cached NetCDF/CSV loading with auto-detection of Agro_PRESAGG data directories."""

import re
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import streamlit as st
import xarray as xr
import numpy as np
import requests

APP_DIR = Path(__file__).parent.parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = Path("/tmp/wass2s_data")  # Writable on Streamlit Cloud

GITHUB_REPO = "samankwah/gmet-wass2s-dashboard"
RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

_AGRO_PATTERN = re.compile(r"Agro_PRESAGG_(\d+)_ic_(\d+)")


def detect_data_dir() -> Optional[Path]:
    """Scan search paths for Agro_PRESAGG_*_ic_*/ and return the latest match."""
    candidates = []
    for search_root in [PROJECT_ROOT, DATA_DIR]:
        if not search_root.exists():
            continue
        for d in search_root.iterdir():
            if d.is_dir():
                m = _AGRO_PATTERN.match(d.name)
                if m:
                    candidates.append((int(m.group(1)), int(m.group(2)), d))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return candidates[0][2]


def _download_release_data():
    """Download data from GitHub Releases if no local data directory exists."""
    if detect_data_dir() is not None:
        return

    try:
        resp = requests.get(RELEASE_API_URL, timeout=30)
        resp.raise_for_status()
        release = resp.json()

        # Find the first .zip asset
        zip_url = None
        for asset in release.get("assets", []):
            if asset["name"].endswith(".zip"):
                zip_url = asset["browser_download_url"]
                break

        if zip_url is None:
            st.error("No data zip found in latest GitHub release.")
            return

        # Download the zip to a temp file (avoids loading 200MB+ into RAM)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False, dir="/tmp") as tmp:
            tmp_path = tmp.name
            with requests.get(zip_url, timeout=600, stream=True) as dl:
                dl.raise_for_status()
                for chunk in dl.iter_content(chunk_size=8 * 1024 * 1024):
                    tmp.write(chunk)

        # Extract and clean up
        with zipfile.ZipFile(tmp_path) as zf:
            zf.extractall(DATA_DIR)
        Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        st.error(f"Could not download data: {e}")


@st.cache_resource
def get_data_dirs():
    """Return cached (data_root, forecast_dir, score_dir, obs_dir) paths."""
    if detect_data_dir() is None:
        with st.spinner("Downloading forecast data (first run only)..."):
            _download_release_data()
    root = detect_data_dir()
    if root is None:
        return None, None, None, None
    return root, root / "forecasts", root / "scores", root / "Observation"


def get_metadata() -> dict:
    """Parse year and initialization from the detected directory name."""
    root = get_data_dirs()[0]
    if root is None:
        return {}
    m = re.match(r"Agro_PRESAGG_(\d+)_ic_(\d+)", root.name)
    if not m:
        return {}
    months = {
        "1": "January", "2": "February", "3": "March", "4": "April",
        "5": "May", "6": "June", "7": "July", "8": "August",
        "9": "September", "10": "October", "11": "November", "12": "December",
    }
    return {
        "forecast_year": int(m.group(1)),
        "initialization": months.get(m.group(2), f"ic_{m.group(2)}"),
    }


def find_forecast_file(product_key: str, forecast_type: str) -> Optional[Path]:
    """Find a forecast NC file using product config glob patterns.

    Args:
        product_key: key in PRODUCTS dict (e.g. "onset")
        forecast_type: "det", "prob", "image", or "pdf"
    Returns:
        Path to the first matching file, or None
    """
    from .product_config import get_product
    p = get_product(product_key)
    _, forecast_dir, _, _ = get_data_dirs()
    if forecast_dir is None or not forecast_dir.exists():
        return None

    pattern_key = f"{forecast_type}_pattern"
    pattern = p.get(pattern_key)
    if not pattern:
        return None

    matches = sorted(forecast_dir.glob(pattern))
    return matches[0] if matches else None


def find_forecast_files(product_key: str, forecast_type: str) -> list[Path]:
    """Find all matching forecast files for a product (e.g. all PDFs)."""
    from .product_config import get_product
    p = get_product(product_key)
    _, forecast_dir, _, _ = get_data_dirs()
    if forecast_dir is None or not forecast_dir.exists():
        return []

    pattern_key = f"{forecast_type}_pattern"
    pattern = p.get(pattern_key)
    if not pattern:
        return []

    return sorted(forecast_dir.glob(pattern))


def _resolve_dims(data):
    """Extract lat/lon dimension names from an xarray DataArray."""
    lat_name = next((d for d in data.dims if d.startswith("lat") or d == "Y"), None)
    lon_name = next((d for d in data.dims if d.startswith("lon") or d == "X"), None)
    return lat_name, lon_name


def _collapse_time(data):
    """Collapse time-like dimensions (time, T, forecast_time)."""
    for tname in ("time", "T", "forecast_time"):
        if tname in data.dims:
            data = data.isel({tname: 0})
    return data


@st.cache_data(ttl=3600)
def load_netcdf(file_path: str, deterministic: bool = True):
    """Load a deterministic NetCDF file, return (data_2d, lat_values, lon_values, ds).

    Returns None tuple if file doesn't exist or fails.
    """
    fp = Path(file_path)
    if not fp.exists():
        return None, None, None, None

    try:
        ds = xr.open_dataset(fp)
        var_name = list(ds.data_vars)[0]
        data = ds[var_name]

        if deterministic:
            data = _collapse_time(data)
            if "member" in data.dims:
                data = data.mean(dim="member")

        lat_name, lon_name = _resolve_dims(data)
        if lat_name is None or lon_name is None:
            ds.close()
            return None, None, None, None

        return data, ds[lat_name].values, ds[lon_name].values, ds
    except Exception:
        return None, None, None, None


# Category labels for probabilistic forecasts
PROB_LABELS = {
    "PB": "Below Normal",
    "PN": "Near Normal",
    "PA": "Above Normal",
}


@st.cache_data(ttl=3600)
def load_probabilistic(file_path: str):
    """Load a probabilistic NetCDF file.

    Returns (categories_dict, lat, lon) where categories_dict maps
    category labels to 2D numpy arrays, or (None, None, None) on failure.

    Handles two formats:
      1. Single variable with 'probability' dimension (PB/PN/PA)
      2. Multiple data variables (one per category)
    """

    fp = Path(file_path)
    if not fp.exists():
        return None, None, None

    try:
        ds = xr.open_dataset(fp)
        var_names = list(ds.data_vars)

        if len(var_names) == 1 and "probability" in ds[var_names[0]].dims:
            data = ds[var_names[0]]
            data = _collapse_time(data)
            lat_name, lon_name = _resolve_dims(data)
            if lat_name is None or lon_name is None:
                ds.close()
                return None, None, None

            prob_coords = data["probability"].values
            categories = {}
            for i, pval in enumerate(prob_coords):
                label = PROB_LABELS.get(str(pval), str(pval))
                categories[label] = data.isel(probability=i).values

            return categories, ds[lat_name].values, ds[lon_name].values

        else:
            first_var = ds[var_names[0]]
            first_var = _collapse_time(first_var)
            lat_name, lon_name = _resolve_dims(first_var)
            if lat_name is None or lon_name is None:
                ds.close()
                return None, None, None

            categories = {}
            for vn in var_names:
                d = _collapse_time(ds[vn])
                label = PROB_LABELS.get(vn, vn)
                categories[label] = d.values

            return categories, ds[lat_name].values, ds[lon_name].values

    except Exception:
        return None, None, None


@st.cache_data(ttl=3600)
def pdf_to_image(file_path: str) -> bytes | None:
    """Render the first page of a PDF as a PNG image (bytes)."""
    try:
        import fitz
        doc = fitz.open(file_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        png_bytes = pix.tobytes("png")
        doc.close()
        return png_bytes
    except Exception:
        return None


def compute_stats(data) -> list[float]:
    """Return [min, mean, max] of non-NaN values."""
    vals = data.values if hasattr(data, "values") else np.asarray(data)
    valid = vals[~np.isnan(vals)]
    if len(valid) == 0:
        return [None, None, None]
    return [float(np.nanmin(valid)), float(np.nanmean(valid)), float(np.nanmax(valid))]


def format_metric(fmt: str, value: float, forecast_year: int = None) -> str:
    """Format a metric value using the product's format string.

    When fmt == "week", converts a day-of-year value to 'Wk2 May' format.
    """
    if value is None:
        return "\u2014"
    if fmt == "week":
        from datetime import date, timedelta
        year = forecast_year or 2026
        d = date(year, 1, 1) + timedelta(days=int(value) - 1)
        week_num = (d.day - 1) // 7 + 1
        return f"Wk{week_num} {d.strftime('%b')}"
    if "{:.0f}" in fmt or "{:.1f}" in fmt:
        return fmt.format(value)
    return fmt.format(int(value))
