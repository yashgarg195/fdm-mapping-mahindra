"""
Formatting Utilities — Display formatting for percentages, scores,
and Streamlit-compatible CSS styling.
"""
from config.constants import CONFIDENCE_COLORS, BRAND_RED, BRAND_CHARCOAL


def format_pct(value, decimals=1):
    """Format a float as a percentage string. Returns 'N/A' on failure."""
    try:
        if value is None:
            return "N/A"
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_score(value):
    """Format a numeric skill score for display."""
    try:
        v = int(value)
        if v < 0:
            return "NO TEST"
        return str(v)
    except (TypeError, ValueError):
        return str(value) if value is not None else "—"


def format_count(value):
    """Format a numeric count with comma separators."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def highlight_confidence(val):
    """Return a CSS background-color style for a confidence level string.
    Used with Streamlit / pandas Styler.
    """
    color = CONFIDENCE_COLORS.get(str(val).upper().strip(), "")
    if color:
        return f"background-color: {color}"
    return ""


def highlight_critical(val):
    """Return a CSS style for critical values (red background)."""
    return f"background-color: {BRAND_RED}; color: white; font-weight: bold"


def highlight_pending(months):
    """Return a CSS style based on pending age months."""
    try:
        m = int(months)
        if m >= 12:
            return f"background-color: {BRAND_RED}; color: white"
        elif m >= 6:
            return "background-color: #FF8C00; color: white"
        elif m >= 3:
            return "background-color: #FFD700; color: black"
        else:
            return ""
    except (TypeError, ValueError):
        return ""


def style_kpi_card(label, value, desc="", border_color=None):
    """Generate HTML for a styled KPI card."""
    bc = border_color or BRAND_RED
    return f"""
    <div style="
        background-color: #FFFFFF;
        border: 2px solid #E6E7E8;
        border-top: 6px solid {bc};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 15px;
        text-align: center;
        transition: transform 0.2s ease;
    ">
        <div style="color: #4D4D4F; font-size: 0.85rem; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 1px;">
            {label}
        </div>
        <div style="color: #231F20; font-size: 2.5rem; font-weight: 800;
                    margin-top: 5px;">
            {value}
        </div>
        <div style="color: #888888; font-size: 0.75rem; margin-top: 5px;
                    text-transform: uppercase;">
            {desc}
        </div>
    </div>
    """
