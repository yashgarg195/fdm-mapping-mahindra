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
    return f"""<div style="
background-color: var(--background);
border: 1px solid var(--muted);
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
<div style="color: var(--muted-foreground); font-size: 10.5px; font-weight: 600;
text-transform: uppercase; letter-spacing: 0.5px;">
{label}
</div>
<div style="color: var(--foreground); font-size: 22px; font-weight: 800;
margin-top: 3px; line-height: 1.2;">
{value}
</div>
<div style="color: var(--muted-foreground); font-size: 10px; font-weight: 500; margin-top: 1px;">
{desc}
</div>
</div>
</div>"""


def style_section_header(title, subtitle=""):
    return (
        f'<div style="margin-bottom: 14px;">'
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 3px;">'
        f'<div style="width: 3px; height: 16px; background: #D2232A; border-radius: 2px; flex-shrink: 0;"></div>'
        f'<span style="font-size: 14px; font-weight: 700; color: var(--foreground);">{title}</span>'
        f'</div>'
        f'<div style="font-size: 11px; color: var(--muted-foreground); padding-left: 11px;">{subtitle}</div>'
        f'</div>'
    )


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
    return f"""<span style="
background: {bg};
color: {fg} !important;
border-radius: 4px;
padding: 2px 8px;
font-size: 10px;
font-weight: 700;
display: inline-block;
">{status}</span>"""


# Shared user-friendly column config mapping for Streamlit tables
COLUMN_CONFIGS = {
    # Unique/Manpower/Roster standard columns
    "Star ID": "Star ID",
    "Name": "Name",
    "Designation": "Designation",
    "Dealer Code": "Dealer Code",
    "Dealer Name": "Dealer Name",
    "Zone": "Zone",
    "State": "State",
    "Dealer AO": "Dealer AO",
    "Dealer Operational Status": "Operational Status",
    "Location": "Location",
    "Emp Code": "Employee Code",
    "Joining Date": "Joining Date",
    "Contact No": "Contact Number",
    "Gender": "Gender",
    "Father Name": "Father Name",
    "DOB": "Date of Birth",
    "Residence Location": "Residence Location",
    "Age": "Age",
    "AadharCardNumber": "Aadhar Card Number",
    "Training year": "Training Year",
    "SKILL LEVEL - PRE": "Pre-Training Skill Level",
    "SKILL LEVEL - POST": "Post-Training Skill Level",
    "LAST PRODUCT TRANIING ON": "Last Product Training",
    "LAST MODEL TRAINED": "Last Model Trained",

    # Priority / Backlog specific columns
    "Nomination_Rank": "Nomination Rank",
    "Pending_Age_Months": "Pending Age (Months)",
    "Training_Priority_Score": "Training Priority Score",
    "Training_Status": "Training Status",
    "Trained_Count": "Trained Count",
    "Untrained_Count": "Untrained Count",
    "Total_Employees": "Total Employees",
    "Pending_Count": "Pending Count",
    "Trained_Pct": "Trained %",
    "Pending_Pct": "Pending %",
    
    # Audit / Matching / Exception specific columns
    "Match_Confidence": "Match Confidence",
    "CROSS_ID_DUPLICATE_SUSPECT": "Cross-ID Suspect",
    "Match_Method": "Match Method",
    "Fuzzy_Score": "Fuzzy Score",
    "Phonetic_Score": "Phonetic Score",
    "Confidence": "Confidence Level",
    "Count": "Count",
    "Pct": "Percentage (%)",
    "Status": "Status",
    "DATA_QUALITY_STATUS": "Quality Status",
    "DATA_QUALITY_REASON": "Quality Reason",
    "CROSS_ID_DUPLICATE_NOTE": "Duplicate Notes",
    "Suspected_Match_StarID": "Suspected Match Star ID",
    "Suspected_Match_Name": "Suspected Match Name",
    "Suspected_Match_Dealer_Code": "Suspected Match Dealer Code",
    "Suspected_Match_Dealer_Name": "Suspected Match Dealer Name",
    "Issue_Type": "Issue Type",
    "Issue_Description": "Issue Description",
    "Dealer_Code": "Dealer Code",
    "Dealer_Name": "Dealer Name",
    "Coverage_Pct": "Coverage %",

    # Skill / Uplift specific columns
    "FY": "Financial Year",
    "Avg_Pre": "Avg Pre Score",
    "Avg_Post": "Avg Post Score",
    "Avg_Uplift": "Avg Uplift",
    "Skill_Level": "Skill Level",
    
    # Count totals
    "Trained": "Trained Count",
    "Untrained": "Untrained Count",
    "Pending": "Pending Count",
    "Total": "Total Count",
}

