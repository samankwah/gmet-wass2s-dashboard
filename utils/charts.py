"""Plotly chart factory with Ghana outline overlay and consistent formatting."""

import json
from datetime import date, timedelta
from pathlib import Path
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import shape
from shapely.ops import unary_union

ASSETS_DIR = Path(__file__).parent.parent / "assets"
_ghana_geo = None
_ghana_union = None
_mask_cache = {}

# 34 southern-Ghana GMet synoptic stations {name: (lat, lon)}
GMET_STATIONS = {
    "Abetifi": (6.67, -0.75), "Aburi": (5.8667, -0.1667), "Accra": (5.6, -0.17),
    "Ada": (5.78, 0.63), "Akatsi": (6.12, 0.8), "Akim Oda": (6.12, -0.8),
    "Akuse": (6.1, 0.12), "Asamankese": (5.8667, -0.6667), "Atebubu": (7.75, -0.98),
    "Axim": (4.87, -2.23), "Bechem": (7.08, -2.03), "Bogoso": (5.4, -2.03),
    "Cape Coast": (5.13, -1.25), "Dormaa": (7.28, -2.88), "Dunkwa": (5.9667, -1.7833),
    "Ejura": (7.3833, -1.3667), "Goaso": (6.8, -2.5167), "Half Assini": (5.05, -2.88),
    "Ho": (6.6, 0.47), "Kete Krachi": (7.82, -0.03), "Kade": (6.1, -0.8333),
    "Kintampo": (8.05, -1.72), "Koforidua": (6.08, -0.25), "Kpando": (7.0, 0.2833),
    "Kumasi": (6.72, -1.6), "Prang": (7.98, -0.88), "Saltpond": (5.2, -1.07),
    "Sefwi Bekwai": (6.2, -2.33), "Sunyani": (7.33, -2.33), "Takoradi": (4.88, -1.77),
    "Tarkwa": (5.3, -1.98), "Tema": (5.62, 0.0), "Wenchi": (7.75, -2.1),
    "Mim": (6.9, -2.55),
}


def _load_ghana_boundary():
    """Load Ghana regions GeoJSON (cached in module)."""
    global _ghana_geo
    if _ghana_geo is not None:
        return _ghana_geo
    geo_path = ASSETS_DIR / "ghana_regions.geojson"
    if geo_path.exists():
        with open(geo_path) as f:
            _ghana_geo = json.load(f)
    return _ghana_geo


def _get_ghana_union():
    """Return the union of all Ghana region polygons (cached)."""
    global _ghana_union
    if _ghana_union is not None:
        return _ghana_union
    geo = _load_ghana_boundary()
    if geo is None:
        return None
    polys = [shape(f["geometry"]) for f in geo["features"]]
    _ghana_union = unary_union(polys)
    return _ghana_union


def _ghana_mask(lon, lat):
    """Return a boolean 2-D mask (lat x lon): True = inside Ghana."""
    key = (lon.tobytes(), lat.tobytes())
    if key in _mask_cache:
        return _mask_cache[key]
    poly = _get_ghana_union()
    if poly is None:
        return np.ones((len(lat), len(lon)), dtype=bool)
    from shapely.geometry import Point
    mask = np.zeros((len(lat), len(lon)), dtype=bool)
    for i, la in enumerate(lat):
        for j, lo in enumerate(lon):
            mask[i, j] = poly.contains(Point(lo, la))
    _mask_cache[key] = mask
    return mask


def _apply_ghana_mask(z, lon, lat):
    """Set z values outside Ghana to NaN."""
    mask = _ghana_mask(lon, lat)
    z = z.astype(float).copy()
    z[~mask] = np.nan
    return z


def _add_station_labels(fig):
    """Add GMet station markers with name labels to the figure."""
    lats = [v[0] for v in GMET_STATIONS.values()]
    lons = [v[1] for v in GMET_STATIONS.values()]
    names = list(GMET_STATIONS.keys())
    fig.add_trace(go.Scatter(
        x=lons, y=lats,
        mode="markers+text",
        marker=dict(size=7, color="black"),
        text=names,
        textfont=dict(size=10, color="black"),
        textposition="top center",
        hoverinfo="text",
        hovertext=[f"{n} ({la:.2f}\u00b0N, {lo:.2f}\u00b0E)" for n, la, lo in zip(names, lats, lons)],
        showlegend=False,
    ))


def _add_ghana_outline(fig):
    """Add Ghana regional boundaries as line traces on the figure."""
    geo = _load_ghana_boundary()
    if geo is None:
        return

    for feature in geo.get("features", []):
        geom = feature.get("geometry", {})
        coords_list = geom.get("coordinates", [])
        geom_type = geom.get("type", "")

        if geom_type == "Polygon":
            coords_list = [coords_list]
        elif geom_type != "MultiPolygon":
            continue

        for polygon in coords_list:
            for ring in polygon:
                lons = [c[0] for c in ring]
                lats = [c[1] for c in ring]
                fig.add_trace(go.Scatter(
                    x=lons, y=lats,
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0.4)", width=1),
                    hoverinfo="skip",
                    showlegend=False,
                ))


def _doy_to_week_label(doy, year=2026):
    """Convert day-of-year to 'Wk1 May' format (week within the month)."""
    d = date(year, 1, 1) + timedelta(days=int(doy) - 1)
    week_num = (d.day - 1) // 7 + 1
    return f"Wk{week_num} {d.strftime('%b')}"


def forecast_heatmap(
    z: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    colorscale: str,
    colorbar_title: str,
    title: str,
    zmin=None,
    zmax=None,
    height: int = 900,
    width: int = 1000,
    valid_period: str = None,
    forecast_year: int = None,
    use_week_labels: bool = False,
) -> go.Figure:
    """Create a styled heatmap with Ghana outline overlay."""
    z = _apply_ghana_mask(z, x, y)

    year = forecast_year or 2026

    # Build colorbar kwargs
    cb_kwargs = dict(
        title=dict(text=colorbar_title, side="right"),
        thickness=15,
        len=0.75,
    )

    # Use integer format for Day of Year values
    z_fmt = ":.0f" if colorbar_title == "Day of Year" else ":.2f"
    hover_kwargs = dict(
        hovertemplate=f"Longitude: %{{x:.2f}}<br>Latitude: %{{y:.2f}}<br>Value: %{{z{z_fmt}}}<extra></extra>",
    )

    if use_week_labels:
        # Compute week-boundary tick values spanning the data range
        valid = z[~np.isnan(z)]
        if len(valid) > 0:
            dmin, dmax = int(np.nanmin(valid)), int(np.nanmax(valid))
            # Start at the first day-1 of each week boundary (every 7 days)
            first_tick = (dmin // 7) * 7 + 1
            tickvals = list(range(first_tick, dmax + 1, 7))
            ticktext = [_doy_to_week_label(v, year) for v in tickvals]
            cb_kwargs["tickvals"] = tickvals
            cb_kwargs["ticktext"] = ticktext

        # Build hover text matrix with week labels
        hover_text = np.empty(z.shape, dtype=object)
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                if np.isnan(z[i, j]):
                    hover_text[i, j] = ""
                else:
                    hover_text[i, j] = _doy_to_week_label(z[i, j], year)
        hover_kwargs = dict(
            hovertext=hover_text,
            hovertemplate="Longitude: %{x:.2f}<br>Latitude: %{y:.2f}<br>%{hovertext}<extra></extra>",
        )

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=colorscale,
        colorbar=cb_kwargs,
        zmin=zmin,
        zmax=zmax,
        hoverongaps=False,
        **hover_kwargs,
    ))

    _add_ghana_outline(fig)
    _add_station_labels(fig)

    display_title = title
    if valid_period:
        display_title += f"<br><span style='font-size:14px;'>Valid: {valid_period}</span>"

    fig.update_layout(
        title=dict(text=display_title, x=0.5, xanchor="center", font=dict(size=20)),
        xaxis_title="Longitude (\u00b0E)",
        yaxis_title="Latitude (\u00b0N)",
        height=height,
        width=width,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=60, r=20, t=70, b=90),
        plot_bgcolor="#fafafa",
        font=dict(size=14),
    )

    return fig


# Original wass2s color palettes for probabilistic tercile maps
_GREEN = ["#e5f5f9", "#ccece6", "#99d8c9", "#66c2a4", "#41ae76", "#238b45", "#006d2c", "#00441b"]
_GRAY = ["#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252"]
_ORANGE = ["#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#993404", "#662506"]


def _build_tercile_colorscale(reverse_cmap: bool):
    """Build a 3-segment Plotly colorscale matching the original wass2s palettes.

    The z-value encodes category + probability:
      BN -> 0..100, NN -> 100..200, AN -> 200..300
    Each segment maps linearly across its palette.

    reverse_cmap=True  (onset, dry spells): BN=Green, NN=Gray, AN=Orange
    reverse_cmap=False (rainfall, temp):    BN=Orange, NN=Gray, AN=Green
    """
    if reverse_cmap:
        bn_colors, nn_colors, an_colors = _GREEN, _GRAY, _ORANGE
    else:
        bn_colors, nn_colors, an_colors = _ORANGE, _GRAY, _GREEN

    cs = []
    # BN segment: z 0..100 -> normalized 0..1/3
    for i, c in enumerate(bn_colors):
        pos = (i / (len(bn_colors) - 1)) / 3.0
        cs.append([pos, c])
    # NN segment: z 100..200 -> normalized 1/3..2/3
    for i, c in enumerate(nn_colors):
        pos = 1.0 / 3.0 + (i / (len(nn_colors) - 1)) / 3.0
        cs.append([pos, c])
    # AN segment: z 200..300 -> normalized 2/3..1
    for i, c in enumerate(an_colors):
        pos = 2.0 / 3.0 + (i / (len(an_colors) - 1)) / 3.0
        cs.append([pos, c])

    return cs


def dominant_tercile_map(
    categories: dict,
    lon: np.ndarray,
    lat: np.ndarray,
    title: str,
    reverse_cmap: bool = False,
    height: int = 900,
    width: int = 1000,
    valid_period: str = None,
    category_labels: list = None,
) -> go.Figure:
    """Create a dominant tercile map with continuous color gradients.

    Each grid cell shows the dominant category colored by probability intensity,
    matching the original wass2s output style (green/gray/orange palettes).

    z encoding: BN prob -> 0+prob*100, NN -> 100+prob*100, AN -> 200+prob*100
    """
    cat_names = list(categories.keys())  # ["Below Normal", "Near Normal", "Above Normal"]
    display_names = category_labels if category_labels else cat_names
    arrays = [categories[c] for c in cat_names]
    stacked = np.stack(arrays, axis=0)  # (3, lat, lon)

    dominant_idx = np.argmax(stacked, axis=0)  # 0, 1, or 2
    max_prob = np.max(stacked, axis=0)

    all_nan = np.all(np.isnan(stacked), axis=0)

    # BN vmin/vmax = 35-85%, NN = 35-65%, AN = 35-85%
    vmin = np.array([35.0, 35.0, 35.0])
    vmax = np.array([85.0, 65.0, 85.0])

    # Encode category + intensity into single z value
    z = np.full(dominant_idx.shape, np.nan)
    for i in range(dominant_idx.shape[0]):
        for j in range(dominant_idx.shape[1]):
            if all_nan[i, j]:
                continue
            idx = dominant_idx[i, j]
            prob_pct = max_prob[i, j] * 100.0
            # Clamp to [vmin, vmax] then normalize to [0, 100]
            clamped = np.clip(prob_pct, vmin[idx], vmax[idx])
            norm = (clamped - vmin[idx]) / (vmax[idx] - vmin[idx]) * 100.0
            z[i, j] = idx * 100.0 + norm

    # Mask to Ghana boundary
    mask = _ghana_mask(lon, lat)
    z[~mask] = np.nan

    colorscale = _build_tercile_colorscale(reverse_cmap)

    # Hover text
    hover_text = np.empty(dominant_idx.shape, dtype=object)
    for i in range(dominant_idx.shape[0]):
        for j in range(dominant_idx.shape[1]):
            if all_nan[i, j]:
                hover_text[i, j] = ""
            else:
                idx = dominant_idx[i, j]
                hover_text[i, j] = (
                    f"Category: {display_names[idx]}<br>"
                    f"Probability: {max_prob[i, j]:.0%}"
                )

    # Build percentage tick labels for the colorbar
    tickvals = []
    ticktext = []
    # BN: 35-85% in 10% steps (z range 0-100)
    for pct in range(35, 86, 10):
        tickvals.append((pct - 35) / (85 - 35) * 100)
        ticktext.append(f"{pct}%")
    # NN: 35-65% in 10% steps (z range 100-200)
    for pct in range(35, 66, 10):
        tickvals.append(100 + (pct - 35) / (65 - 35) * 100)
        ticktext.append(f"{pct}%")
    # AN: 35-85% in 10% steps (z range 200-300)
    for pct in range(35, 86, 10):
        tickvals.append(200 + (pct - 35) / (85 - 35) * 100)
        ticktext.append(f"{pct}%")

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=lon,
        y=lat,
        colorscale=colorscale,
        zmin=0,
        zmax=300,
        hoverongaps=False,
        hovertext=hover_text,
        hovertemplate="Longitude: %{x:.2f}<br>Latitude: %{y:.2f}<br>%{hovertext}<extra></extra>",
        colorbar=dict(
            title=dict(text="Probability (%)", side="right"),
            thickness=15,
            len=0.75,
            tickvals=tickvals,
            ticktext=ticktext,
            tickfont=dict(size=10),
        ),
    ))

    # Add category labels to the right of the colorbar via annotations
    # Colorbar spans y 0.125 to 0.875 (len=0.75 centered), each segment is 1/3 of that
    cb_bottom = 0.125
    cb_height = 0.75
    seg_height = cb_height / 3.0
    for i, name in enumerate(display_names):
        mid_y = cb_bottom + (i + 0.5) * seg_height
        fig.add_annotation(
            x=1.22,
            y=mid_y,
            xref="paper",
            yref="paper",
            text=f"<b>{name}<br>(%)</b>",
            showarrow=False,
            font=dict(size=11),
            textangle=-90,
        )

    _add_ghana_outline(fig)
    _add_station_labels(fig)

    display_title = title
    if valid_period:
        display_title += f"<br><span style='font-size:14px;'>Valid: {valid_period}</span>"

    fig.update_layout(
        title=dict(text=display_title, x=0.5, xanchor="center", font=dict(size=20)),
        xaxis_title="Longitude (\u00b0E)",
        yaxis_title="Latitude (\u00b0N)",
        height=height,
        width=width,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=60, r=140, t=70, b=90),
        plot_bgcolor="#fafafa",
        font=dict(size=14),
    )

    return fig


def station_map(
    station_names: list,
    lats: list,
    lons: list,
    has_data: list,
    title: str,
    height: int = 700,
    width: int = 900,
) -> go.Figure:
    """Create a scatter map of station locations on the Ghana outline.

    Parameters
    ----------
    station_names : list of str
    lats, lons : list of float
    has_data : list of bool – True if the station has valid data
    title : str – displayed above the map
    """
    fig = go.Figure()
    _add_ghana_outline(fig)

    colors = ["#2ca02c" if hd else "#d62728" for hd in has_data]
    labels = ["Has data" if hd else "No data" for hd in has_data]

    fig.add_trace(go.Scatter(
        x=lons,
        y=lats,
        mode="markers+text",
        marker=dict(size=9, color=colors, line=dict(width=0.5, color="black")),
        text=station_names,
        textfont=dict(size=9, color="black"),
        textposition="top center",
        hoverinfo="text",
        hovertext=[
            f"{n} ({la:.2f}\u00b0N, {lo:.2f}\u00b0E)<br>{lbl}"
            for n, la, lo, lbl in zip(station_names, lats, lons, labels)
        ],
        showlegend=False,
    ))

    n_with = sum(has_data)
    n_total = len(has_data)
    display_title = f"{title} \u2014 {n_with} of {n_total} stations with data"

    fig.update_layout(
        title=dict(text=display_title, x=0.5, xanchor="center", font=dict(size=18)),
        xaxis_title="Longitude (\u00b0E)",
        yaxis_title="Latitude (\u00b0N)",
        height=height,
        width=width,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=60, r=20, t=70, b=90),
        plot_bgcolor="#fafafa",
        font=dict(size=14),
    )

    return fig
