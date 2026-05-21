"""
Formatting Utilities — Display formatting for percentages, scores,
and Streamlit-compatible CSS styling.
"""
from config.constants import CONFIDENCE_COLORS, BRAND_CHARCOAL, COLOR_CRITICAL, COLOR_WARNING, COLOR_SUCCESS


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
    return f"background-color: {COLOR_CRITICAL}; color: white; font-weight: bold"


def highlight_pending(months):
    """Return a CSS style based on pending age months."""
    try:
        m = int(months)
        if m >= 12:
            return f"background-color: {COLOR_CRITICAL}; color: white"
        elif m >= 6:
            return f"background-color: {COLOR_WARNING}; color: white"
        elif m >= 3:
            return "background-color: #FFD700; color: black"
        else:
            return ""
    except (TypeError, ValueError):
        return ""


def style_kpi_card(label, value, desc="", border_color=None):
    """Generate HTML for a styled KPI card."""
    bc = border_color or BRAND_CHARCOAL
    return f"""
    <div style="
        background-color: #FFFFFF;
        border: 1px solid #E8E8EC;
        border-radius: 8px;
        padding: 14px 16px;
        min-height: 90px;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    ">
        <div style="
            position: absolute;
            left: 0;
            top: 14px;
            width: 3px;
            height: 32px;
            background-color: {bc};
            border-radius: 0 2px 2px 0;
        "></div>
        <div style="padding-left: 8px;">
            <div style="color: #8B8BA7; font-size: 10.5px; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.5px;">
                {label}
            </div>
            <div style="color: #1A1A2E; font-size: 22px; font-weight: 800;
                        margin-top: 3px; line-height: 1.2;">
                {value}
            </div>
            <div style="color: #8B8BA7; font-size: 10px; font-weight: 500; margin-top: 1px;">
                {desc}
            </div>
        </div>
    </div>
    """


def style_section_header(title, subtitle=""):
    return f"""
    <div style="margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 3px;">
            <div style="width: 3px; height: 16px; background: #D2232A; border-radius: 2px; flex-shrink: 0;"></div>
            <span style="font-size: 14px; font-weight: 700; color: #1A1A2E;">{title}</span>
        </div>
        <div style="font-size: 11px; color: #8B8BA7; padding-left: 11px;">
            {subtitle}
        </div>
    </div>
    """


def style_filter_toolbar():
    return """
    <div style="
        background: #F7F7F9;
        border: 1px solid #E8E8EC;
        border-radius: 8px;
        padding: 10px 14px;
        display: flex;
        gap: 10px;
        align-items: center;
        margin-bottom: 14px;
    ">
    """


def style_status_badge(status):
    """Return styled HTML for training status badges."""
    colors = {
        "COMPLETED": ("rgba(46,125,50,0.08)", "#2E7D32"),
        "ATTENDED": ("rgba(120,144,156,0.1)", "#546E7A"),
        "PENDING": ("rgba(245,124,0,0.1)", "#F57C00"),
        "ELIGIBLE": ("rgba(33,150,243,0.1)", "#1976D2"),
        "NOT_TRAINED": ("rgba(0,0,0,0.05)", "#9E9E9E")
    }
    bg, fg = colors.get(str(status).upper(), ("rgba(0,0,0,0.05)", "#9E9E9E"))
    return f"""
    <span style="
        background: {bg};
        color: {fg};
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
    ">{status}</span>
    """
