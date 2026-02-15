"""Central product registry — colors, icons, descriptions, colorscales, farmer guidance, file patterns."""

PRODUCTS = {
    "onset": {
        "title": "Rainfall Onset Forecast",
        "short": "Onset",
        "icon": "\U0001F331",
        "accent": "#2E7D32",
        "light_bg": "#E8F5E9",
        "colorscale": "Viridis",
        "reverse_cmap": True,
        "colorbar_title": "Day of Year",
        "description": (
            "Predicted date of rainfall onset across Ghana. "
            "The onset marks the beginning of the rainy season and is the most critical "
            "parameter for planting decisions."
        ),
        "farmer_guidance": (
            "Wait for the predicted onset date before planting. Early planting before "
            "true onset risks seedling loss from false starts. Monitor local rainfall "
            "accumulation thresholds (20 mm over 3 days with no dry spell >7 days in the "
            "following 30 days)."
        ),
        "det_pattern": "Forecast_Det_PRCPOnset_*.nc",
        "prob_pattern": "Forecast_Prob_PRCPOnset_*.nc",
        "image_pattern": "Consolidated*Forecast Onset*.png",
        "pdf_pattern": "*_Onset-*.pdf",
        "metric_labels": ("Earliest Onset", "Mean Onset", "Latest Onset"),
        "metric_fmt": "Day {}",
        "consolidated_pdf_pattern": "Consolidated*Forecast_Onset-*.pdf",
    },
    "dry_spell": {
        "title": "1st Dry Spell Onset Forecast",
        "short": "1st Dry Spell",
        "icon": "\u2600\uFE0F",
        "accent": "#E65100",
        "light_bg": "#FFF3E0",
        "colorscale": "Viridis",
        "reverse_cmap": True,
        "colorbar_title": "Day of Year",
        "description": (
            "Predicted date of the first extended dry period after rainfall onset. "
            "A dry spell is typically defined as 7+ consecutive days with <1 mm rainfall."
        ),
        "farmer_guidance": (
            "Plan supplemental irrigation or drought-tolerant varieties if an early dry spell "
            "is predicted. Apply mulching before the expected dry spell to conserve soil moisture."
        ),
        "det_pattern": "Forecast_Det_PRCPdryspellonset_*.nc",
        "prob_pattern": "Forecast_Prob_PRCPdryspellonset_*.nc",
        "image_pattern": "Consolidated*dryspell*.png",
        "pdf_pattern": "*dryspell*.pdf",
        "metric_labels": ("Earliest", "Mean", "Latest"),
        "metric_fmt": "Day {}",
        "consolidated_pdf_pattern": "Consolidated_Forecast_dryspellonset-*.pdf",
    },
    "late_dry_spell": {
        "title": "2nd / Late Dry Spell Forecast",
        "short": "Late Dry Spell",
        "icon": "\U0001F3DC\uFE0F",
        "accent": "#D84315",
        "light_bg": "#FBE9E7",
        "colorscale": "Viridis",
        "reverse_cmap": True,
        "colorbar_title": "Day of Year",
        "description": (
            "Predicted timing of the second or late-season dry spell. "
            "This is critical for water management and late-season crop planning."
        ),
        "farmer_guidance": (
            "If a late dry spell is predicted during grain filling, consider early-maturing "
            "varieties. Schedule critical irrigation for reproductive stages."
        ),
        "det_pattern": "Forecast_Det_*late*.nc",
        "prob_pattern": "Forecast_Prob_*late*.nc",
        "image_pattern": "Consolidated*late*dry*.png",
        "pdf_pattern": "*late*.pdf",
        "metric_labels": ("Earliest", "Mean", "Latest"),
        "metric_fmt": "Day {}",
        "consolidated_pdf_pattern": "Consolidated_Forecast_latedryspell-*.pdf",
    },
    "cessation": {
        "title": "Rainfall Cessation Forecast",
        "short": "Cessation",
        "icon": "\U0001F342",
        "accent": "#1565C0",
        "light_bg": "#E3F2FD",
        "colorscale": "Viridis",
        "reverse_cmap": True,
        "colorbar_title": "Day of Year",
        "description": (
            "Predicted date when the rainy season ends. Important for harvest timing "
            "and post-season land preparation."
        ),
        "farmer_guidance": (
            "Plan harvest before cessation to avoid crop losses from terminal drought. "
            "Post-harvest drying is easier after cessation. Schedule land preparation for "
            "the next season."
        ),
        "det_pattern": "Forecast_Det_*Cessation*.nc",
        "prob_pattern": "Forecast_Prob_*Cessation*.nc",
        "image_pattern": "Consolidated*Cessation*.png",
        "pdf_pattern": "*Cessation*.pdf",
        "metric_labels": ("Earliest Cessation", "Mean Cessation", "Latest Cessation"),
        "metric_fmt": "Day {}",
        "consolidated_pdf_pattern": "Consolidated_Forecast_Cessation-*.pdf",
    },
    "length_of_season": {
        "title": "Length of Growing Season",
        "short": "Season Length",
        "icon": "\U0001F4C5",
        "accent": "#388E3C",
        "light_bg": "#E8F5E9",
        "colorscale": "Viridis",
        "reverse_cmap": True,
        "colorbar_title": "Days",
        "description": (
            "Predicted duration (days) from rainfall onset to cessation. "
            "Determines the available growing window for crop selection."
        ),
        "farmer_guidance": (
            "Match crop variety maturity to the predicted season length. "
            "Short seasons (<90 days): use early-maturing varieties. "
            "Long seasons (>150 days): consider relay cropping or double cropping."
        ),
        "det_pattern": "Forecast_Det_*Length*.nc",
        "prob_pattern": "Forecast_Prob_*Length*.nc",
        "image_pattern": "Consolidated*Length*.png",
        "pdf_pattern": "*Length*.pdf",
        "metric_labels": ("Shortest Season", "Mean Season", "Longest Season"),
        "metric_fmt": "{} days",
        "consolidated_pdf_pattern": "Consolidated_Forecast_Length-*.pdf",
    },
    "seasonal_prcp": {
        "title": "Seasonal Rainfall Forecast",
        "short": "Seasonal PRCP",
        "icon": "\U0001F327\uFE0F",
        "accent": "#0277BD",
        "light_bg": "#E1F5FE",
        "colorscale": "Viridis",
        "reverse_cmap": False,
        "colorbar_title": "Rainfall (mm)",
        "description": (
            "Seasonal precipitation outlook \u2014 Below Normal, Near Normal, or Above Normal "
            "probability for the selected 3-month season."
        ),
        "farmer_guidance": (
            "Above Normal: prepare for potential flooding, waterlogging. "
            "Below Normal: plan water harvesting, drought-tolerant crops. "
            "Near Normal: follow standard agronomic practices."
        ),
        "metric_labels": ("Min Rainfall", "Mean Rainfall", "Max Rainfall"),
        "metric_fmt": "{:.0f} mm",
    },
    "seasonal_temp": {
        "title": "Seasonal Temperature Forecast",
        "short": "Seasonal TEMP",
        "icon": "\U0001F321\uFE0F",
        "accent": "#C62828",
        "light_bg": "#FFEBEE",
        "colorscale": "Viridis",
        "reverse_cmap": False,
        "colorbar_title": "Temperature (\u00B0C)",
        "description": (
            "Seasonal temperature outlook \u2014 probability of Below Normal, Near Normal, "
            "or Above Normal temperatures for the selected 3-month season."
        ),
        "farmer_guidance": (
            "Above Normal temperatures increase evapotranspiration and crop water demand. "
            "Consider heat-tolerant varieties and adjust irrigation scheduling."
        ),
        "metric_labels": ("Min Temp", "Mean Temp", "Max Temp"),
        "metric_fmt": "{:.1f} \u00B0C",
    },
    "skill_scores": {
        "title": "Forecast Skill Scores",
        "short": "Skill Scores",
        "icon": "\U0001F4C8",
        "accent": "#4527A0",
        "light_bg": "#EDE7F6",
        "colorscale": "RdYlGn",
        "colorbar_title": "Score",
        "description": (
            "Hindcast validation metrics (1993\u20132016) showing how well the forecast system "
            "performs compared to observations."
        ),
        "farmer_guidance": (
            "Higher GROC and Pearson values indicate more reliable forecasts for your area. "
            "Check local skill before making major decisions based on seasonal forecasts."
        ),
    },
    "station_data": {
        "title": "Station-Level Predictions",
        "short": "Station Data",
        "icon": "\U0001F4CD",
        "accent": "#37474F",
        "light_bg": "#ECEFF1",
        "colorscale": None,
        "colorbar_title": None,
        "description": (
            "Point forecasts and historical observations for 34 synoptic stations across Ghana."
        ),
        "farmer_guidance": (
            "Station data provides localized information. Find the station nearest to your "
            "farm for the most relevant forecast guidance."
        ),
    },
}


def get_product(key: str) -> dict:
    """Return product config dict by key."""
    return PRODUCTS[key]
