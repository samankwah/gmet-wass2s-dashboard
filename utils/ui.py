"""Shared UI components — CSS injection, page headers, metric cards, about sections, footer."""

import streamlit as st
from pathlib import Path
from datetime import datetime
from PIL import Image


def inject_css():
    """Inject global CSS for professional styling."""
    st.markdown("""
    <style>
    /* Sidebar — clean light theme */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E8E8E8;
    }
    section[data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #EEEEEE !important;
    }

    /* Hide Streamlit's default page nav */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar section headers (small caps) */
    .sidebar-section {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #999 !important;
        padding: 1rem 0 0.4rem 0.5rem;
        margin: 0;
    }

    /* Style st.page_link items in sidebar */
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] > a {
        font-size: 0.88rem;
        padding: 0.45rem 0.7rem;
        border-radius: 6px;
        color: #555 !important;
        transition: background 0.15s;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] > a:hover {
        background: #F0F0F0;
        color: #1B5E20 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] > a[aria-current="page"] {
        background: #E8F5E9;
        color: #1B5E20 !important;
        font-weight: 600;
    }

    /* ===== Sidebar expanders — borderless flat nav ===== */
    section[data-testid="stSidebar"] [data-testid="stExpander"],
    section[data-testid="stSidebar"] [data-testid="stExpander"] > *,
    section[data-testid="stSidebar"] [data-testid="stExpander"] details,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: 0.88rem;
        padding: 0.45rem 0.7rem;
        border-radius: 6px;
        color: #555 !important;
        transition: background 0.15s;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        background: #F0F0F0;
        color: #1B5E20 !important;
    }
    /* Expander content — indented */
    section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 0 !important;
        margin-left: 1.2rem !important;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .page-banner { padding: 1rem !important; }
        .page-banner h1 { font-size: 1.3rem !important; }
        .metric-card { min-width: 100% !important; }
        .product-card { min-width: 100% !important; }
    }

    /* Metric cards */
    .metric-card {
        border-left: 4px solid var(--accent);
        background: var(--light-bg);
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent);
        line-height: 1.2;
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.2rem;
    }

    /* Info bar — compact horizontal metadata strip */
    .info-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        background: #F5F5F5;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        align-items: center;
    }
    .info-bar .info-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .info-bar .info-label {
        font-size: 0.78rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .info-bar .info-value {
        font-size: 0.88rem;
        font-weight: 700;
        color: #1B5E20;
    }

    /* Section heading */
    .section-heading {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
        border-bottom: 2px solid #1B5E20;
        padding-bottom: 0.35rem;
        margin-bottom: 0.2rem;
    }
    .section-caption {
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 0.8rem;
    }

    /* Status badge pill */
    .status-badge {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        letter-spacing: 0.02em;
        vertical-align: middle;
    }

    /* Product cards — clickable, horizontal layout */
    .product-card {
        border-radius: 10px;
        padding: 1.2rem;
        text-align: left;
        transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        cursor: pointer;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        margin-bottom: 0.6rem;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #1B5E20;
    }
    .product-card .icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
    .product-card .name { font-weight: 600; font-size: 0.92rem; color: #333; }
    .product-card .desc { font-size: 0.75rem; color: #888; margin-top: 0.2rem; }

    /* Page-link card styling in main content only (not sidebar) */
    .main div[data-testid="stPageLink"] > a {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        transition: border-color 0.15s, box-shadow 0.15s;
        display: block;
    }
    .main div[data-testid="stPageLink"] > a:hover {
        border-color: #1B5E20;
        box-shadow: 0 2px 8px rgba(27,94,32,0.1);
    }

    /* Ensure sidebar page links have NO border at all */
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] > a {
        border: none !important;
        box-shadow: none !important;
    }

    /* Farmer guidance box */
    .farmer-tip {
        background: #FFF8E1;
        border-left: 4px solid #F9A825;
        padding: 0.8rem 1rem;
        border-radius: 0 6px 6px 0;
        margin-top: 0.5rem;
    }
    .farmer-tip strong { color: #E65100; }

    /* Push main content up so footer doesn't overlap */
    .main .block-container {
        padding-bottom: 2.5rem;
    }

    /* Footer — pinned to bottom of viewport, outside page body */
    .app-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 0.3rem 0;
        color: #AAA;
        font-size: 0.65rem;
        background: #FAFAFA;
        border-top: 1px solid #E8E8E8;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_branding():
    """Render sidebar with structured navigation and branding."""
    with st.sidebar:
        assets = Path(__file__).parent.parent / "assets"
        logo = assets / "smart_logo_GMet.png"
        st.caption("WASS2S Forecast Dashboard")

        # MAIN MENU section
        st.markdown('<p class="sidebar-section">Main Menu</p>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard", icon="\U0001F4CA")

        with st.expander("\U0001F331 Agronomic Forecasts"):
            st.page_link("pages/01_Agronomic_Forecasts.py", label="\u25AA Onset", query_params={"product": "onset"})
            st.page_link("pages/01_Agronomic_Forecasts.py", label="\u25AA 1st Dry Spell", query_params={"product": "dry_spell"})
            st.page_link("pages/01_Agronomic_Forecasts.py", label="\u25AA Late Dry Spell", query_params={"product": "late_dry_spell"})
            st.page_link("pages/01_Agronomic_Forecasts.py", label="\u25AA Cessation", query_params={"product": "cessation"})
            st.page_link("pages/01_Agronomic_Forecasts.py", label="\u25AA Season Length", query_params={"product": "length_of_season"})

        with st.expander("\U0001F327\uFE0F Rainfall Outlook"):
            st.caption("Major Season (South)")
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA MAM", query_params={"product": "MAM"})
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA AMJ", query_params={"product": "AMJ"})
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA MJJ", query_params={"product": "MJJ"})
            st.caption("Major Season (North)")
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA MJJ", query_params={"product": "MJJ"})
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA JJA", query_params={"product": "JJA"})
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA JAS", query_params={"product": "JAS"})
            st.caption("Minor Season (South)")
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA SON", query_params={"product": "SON"})
            st.caption("Dry Season (All)")
            st.page_link("pages/02_Rainfall_Outlook.py", label="\u25AA NDJ", query_params={"product": "NDJ"})

        with st.expander("\U0001F321\uFE0F Temperature Outlook"):
            st.caption("Major Season (South)")
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA MAM", query_params={"product": "MAM"})
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA AMJ", query_params={"product": "AMJ"})
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA MJJ", query_params={"product": "MJJ"})
            st.caption("Major Season (North)")
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA MJJ", query_params={"product": "MJJ"})
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA JJA", query_params={"product": "JJA"})
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA JAS", query_params={"product": "JAS"})
            st.caption("Minor Season (South)")
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA SON", query_params={"product": "SON"})
            st.caption("Dry Season (All)")
            st.page_link("pages/03_Temperature_Outlook.py", label="\u25AA NDJ", query_params={"product": "NDJ"})

        # ANALYSIS section
        st.markdown('<p class="sidebar-section">Analysis</p>', unsafe_allow_html=True)

        with st.expander("\U0001F4C8 Forecast Skill"):
            st.page_link("pages/04_Forecast_Skill.py", label="\u25AA GROC", query_params={"product": "GROC"})
            st.page_link("pages/04_Forecast_Skill.py", label="\u25AA Pearson", query_params={"product": "Pearson"})
            st.page_link("pages/04_Forecast_Skill.py", label="\u25AA MAE", query_params={"product": "MAE"})
            st.page_link("pages/04_Forecast_Skill.py", label="\u25AA RPSS", query_params={"product": "RPSS"})

        with st.expander("\U0001F4CD Station Data"):
            st.page_link("pages/05_Station_Data.py", label="\u25AA Onset", query_params={"product": "onset"})
            st.page_link("pages/05_Station_Data.py", label="\u25AA Dry Spell", query_params={"product": "dry_spell"})
            st.page_link("pages/05_Station_Data.py", label="\u25AA Seasonal PRCP", query_params={"product": "seasonal_prcp"})

        # HELP section
        st.markdown('<p class="sidebar-section">Help</p>', unsafe_allow_html=True)
        with st.expander("Glossary"):
            st.markdown("""
**Initialization** — month when models were run
**Skill Score** — forecast reliability (1993–2016)
**Onset** — start of rainy season
**Cessation** — end of rainy season
**PRCP** — precipitation (rainfall)
            """)

        # GMet logo pinned to sidebar bottom corner
        if logo.exists():
            import base64
            logo_bytes = logo.read_bytes()
            b64 = base64.b64encode(logo_bytes).decode()
            st.markdown(f"""
            <div style="position:fixed; bottom:0.8rem; left:0.8rem; z-index:50;
                        max-width:calc(var(--sidebar-width, 21rem) - 1.6rem);">
                <hr style="border:none; border-top:1px solid #EEE; margin-bottom:0.5rem;">
                <img src="data:image/png;base64,{b64}" width="70">
            </div>
            """, unsafe_allow_html=True)


def info_bar(items, accent="#1B5E20"):
    """Compact horizontal metadata bar. items is a list of (label, value) tuples."""
    inner = "".join(
        f'<div class="info-item">'
        f'<span class="info-label">{label}:</span>'
        f'<span class="info-value" style="color:{accent};">{value}</span>'
        f'</div>'
        for label, value in items
    )
    st.markdown(f'<div class="info-bar">{inner}</div>', unsafe_allow_html=True)


def section_heading(title, caption=None):
    """Styled section heading with optional caption."""
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)


def status_badge(text):
    """Return HTML for an inline status pill."""
    return f'<span class="status-badge">{text}</span>'


def page_header(title: str, subtitle: str, accent: str, icon: str = ""):
    """Render a gradient banner at the top of a page."""
    st.markdown(f"""
    <div class="page-banner" style="
        background: linear-gradient(135deg, {accent}, {_lighten(accent, 0.3)});
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: white;
    ">
        <h1 style="margin:0; font-size:1.8rem; color:white;">
            {icon} {title}
        </h1>
        <p style="margin:0.3rem 0 0; opacity:0.9; font-size:0.95rem; color: #ffffffdd;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def metric_cards(values: list[tuple[str, str]], accent: str, light_bg: str):
    """Render styled metric cards. Each item is (label, value_str)."""
    cols = st.columns(len(values))
    for col, (label, val) in zip(cols, values):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="--accent:{accent}; --light-bg:{light_bg};
                 border-left-color:{accent}; background:{light_bg};">
                <div class="value" style="color:{accent};">{val}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def about_product(description: str, farmer_guidance: str):
    """Render expandable about section with farmer guidance."""
    with st.expander("About this product", expanded=False):
        st.markdown(description)
        if farmer_guidance:
            st.markdown(f"""
            <div class="farmer-tip">
                <strong>\U0001F33E Farmer Guidance:</strong> {farmer_guidance}
            </div>
            """, unsafe_allow_html=True)


def footer():
    """Render page footer."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="app-footer">
        Powered by <strong>WASS2S</strong> | CILSS/AGRHYMET RCC | Ghana Meteorological Agency<br>
        <span style="font-size:0.65rem;">Rendered {now} UTC</span>
    </div>
    """, unsafe_allow_html=True)


def _lighten(hex_color: str, amount: float = 0.3) -> str:
    """Lighten a hex color by blending with white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"
