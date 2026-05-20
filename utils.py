import datetime
import re
import pandas as pd
import numpy as np

# ── OFFICIAL BRAND CORPORATE COLOR PALETTE ────────────────────────────────────
BRAND_RED       = "#E31837" # Primary Accent / Call-to-actions / Critical highlights
BRAND_CHARCOAL  = "#4D4D4F" # Dark Neutral / Sub-headers / Body text elements
BRAND_DARK_CORE = "#231F20" # Primary Dark Accent / Dynamic structural elements
BRAND_LIGHT_GREY= "#E6E7E8" # Light Background Tint / Structural block surfaces
BRAND_WHITE     = "#FFFFFF" # Pure Neutral

# ── FISCAL CALENDAR BOUNDARIES ────────────────────────────────────────────────
CURRENT_FY = "F-26"
FY_CALENDAR = {
    "F-23": {"start": datetime.date(2022, 4, 1), "end": datetime.date(2023, 3, 31)},
    "F-24": {"start": datetime.date(2023, 4, 1), "end": datetime.date(2024, 3, 31)},
    "F-25": {"start": datetime.date(2024, 4, 1), "end": datetime.date(2025, 3, 31)},
    "F-26": {"start": datetime.date(2025, 4, 1), "end": datetime.date(2026, 3, 31)},
}

# ── RETRAINING RECALL INTERVAL BUCKETS ───────────────────────────────────────
# (label, min_months_elapsed, hex_color, tracking_description)
RECALL_BUCKETS = [
    ("CRITICAL",   36, BRAND_RED,       "Critical — 3+ years since last training"),
    ("OVERDUE",    24, "#FF8C00",       "Overdue — 2–3 years since last training"),
    ("DUE_SOON",   18, "#FFD700",       "Due Soon — 18–24 months since last training"),
    ("RECENT",      6, "#90EE90",       "Recent — 6–18 months since last training"),
    ("CURRENT_FY",  0, BRAND_CHARCOAL,  "Current FY — trained this financial year"),
]
NEVER_TRAINED_COLOR  = BRAND_LIGHT_GREY
NEVER_TRAINED_LABEL  = "NEVER_TRAINED"

# ── MATRICES FOR SKILL SCORING ────────────────────────────────────────────────
# 'NO TEST' maps strictly to -1 (never assessed) and must never be averaged with 0.
SKILL_SCORE_MAP = {
    0: 0, "0": 0, 0.0: 0, "0.0": 0,
    "L1": 1, "L2": 2, "L3": 3, "L4": 4,
    "NO TEST": -1,
}
SKILL_LABELS = {-1: "NO TEST", 0: "0", 1: "L1", 2: "L2", 3: "L3", 4: "L4"}

# ── PRODUCTION MODEL TEXT STANDARDIZATION MAP ────────────────────────────────
MODEL_NORMALISATION_MAP = {
    "INSTALATION":       "INSTALLATION",
    "L1-L2 TRAINING":    "L1 L2 TRAINING",
    "M LIFT HYDRAULIC":  "M-LIFT HYDRAULICS",
    "FARM MACHNINERY":   "FARM MACHINERY",
    "FARM MACHINERY":    "FARM MACHINERY",
    "YUVO HYDRAULICS":   "YUVO HYDRAULICS",
}

# Canonical model names list after cleanup layer
CANONICAL_MODELS = [
    "H1 R", "YT+", "TREM IV", "OJA", "ENGINE SETTINGS", "SALES MAN TRAINING",
    "TREM IV REFRESH", "H1 TRACTOR", "YUVO HYDRAULICS", "H1 R INSTALLATION",
    "NOVO", "MS PTO", "HYDRAULICS", "ROTAVATOR", "OJA REFRESHER", "KRISH E KIT",
    "ASK PORTAL", "L1 L2 TRAINING", "DSQI", "FARM MACHINERY", "INSTALLATION",
    "SST - AWARENESS", "HY TECH HYDRAULIC", "FLA PRODUCT TRAINING", "XP PLUS",
    "THRESHER", "STRAW REAPER", "PARIVARTAN KIT", "WET CLUTCH", "WARRANTY MODULE",
    "ELECTRICALS", "LOADER", "M-LIFT HYDRAULICS", "SP PLUS", "ARJUN", "JIVO",
    "NEW DEALER INDUCTION", "LASER LEVELER", "MSDC - TRAINING", "YUVO TRACTOR", "N - PAGE",
]

# ── MACHINE MODEL CATEGORIZATION MATRICES ─────────────────────────────────────
MODEL_CATEGORY_MAP = {
    "H1 R": "TECHNICAL", "H1 TRACTOR": "TECHNICAL", "H1 R INSTALLATION": "TECHNICAL",
    "TREM IV": "TECHNICAL", "TREM IV REFRESH": "TECHNICAL", "OJA": "TECHNICAL", 
    "OJA REFRESHER": "TECHNICAL", "NOVO": "TECHNICAL", "YT+": "TECHNICAL", 
    "SP PLUS": "TECHNICAL", "XP PLUS": "TECHNICAL", "ARJUN": "TECHNICAL", 
    "JIVO": "TECHNICAL", "YUVO TRACTOR": "TECHNICAL", "ENGINE SETTINGS": "TECHNICAL",
    "HYDRAULICS": "TECHNICAL", "YUVO HYDRAULICS": "TECHNICAL", "HY TECH HYDRAULIC": "TECHNICAL", 
    "M-LIFT HYDRAULICS": "TECHNICAL", "MS PTO": "TECHNICAL", "WET CLUTCH": "TECHNICAL", 
    "ELECTRICALS": "TECHNICAL", "DSQI": "TECHNICAL", 
    "ROTAVATOR": "PRODUCT", "THRESHER": "PRODUCT", "STRAW REAPER": "PRODUCT", 
    "LOADER": "PRODUCT", "LASER LEVELER": "PRODUCT", "KRISH E KIT": "PRODUCT", 
    "PARIVARTAN KIT": "PRODUCT", "INSTALLATION": "PRODUCT", "FARM MACHINERY": "PRODUCT", 
    "SALES MAN TRAINING": "PROCESS", "ASK PORTAL": "PROCESS", "NEW DEALER INDUCTION": "PROCESS", 
    "WARRANTY MODULE": "PROCESS", "SST - AWARENESS": "PROCESS", "FLA PRODUCT TRAINING": "PROCESS", 
    "MSDC - TRAINING": "PROCESS", "L1 L2 TRAINING": "PROCESS", "N - PAGE": "PROCESS"
}

TECHNICAL_DESIGNATIONS = ["Technician", "Installer", "Service Advisor (FLA)", "Techguru", "Electrician"]
ALL_DESIGNATIONS = TECHNICAL_DESIGNATIONS + ["Salesman", "Sales Manager", "Works Manager", "Branch Manager", "General Manager", "Team Leader"]

ZONE_STATE_MAP = {
    "Zone1": ["Haryana", "Punjab", "Rajasthan East", "Rajasthan West"],
    "Zone2": ["UP Central", "UP East", "UP West"],
    "Zone3": ["Bihar", "Jharkhand", "North East", "West Bengal"],
    "Zone4": ["Chhattisgarh", "Madhya Pradesh East", "Madhya Pradesh West", "Odisha"],
    "Zone5": ["Gujarat", "Karnataka", "Maharashtra East", "Maharashtra West"],
    "Zone6": ["Andhra Pradesh", "Tamil Nadu", "Telangana"],
}

CONFIDENCE_ORDER = ["HIGH", "MEDIUM", "LOW", "FUZZY", "UNRESOLVED"]
CONFIDENCE_COLORS = {
    "HIGH":       "#CCFFCC",  # light green
    "MEDIUM":     "#CCFFFF",  # light cyan
    "LOW":        "#FFE0A0",  # amber
    "FUZZY":      "#FFD0FF",  # light purple (needs manual review)
    "UNRESOLVED": "#FFCCCC",  # light red
}

# Algorithmic Threshold Caps
FUZZY_PRIMARY_THRESHOLD   = 88
FUZZY_SECONDARY_THRESHOLD = 75
RECORDLINKAGE_SCORE_HIGH  = 4.0
RECORDLINKAGE_SCORE_FUZZY = 2.5


def clean_string(val):
    """Clean and normalize string values for exact/fuzzy comparisons."""
    if pd.isna(val) or val is None:
        return ""
    # Convert to uppercase string, strip leading/trailing spaces, replace inner multi-spaces
    s = str(val).upper().strip()
    return re.sub(r'\s+', ' ', s)


def clean_name(name):
    """Clean name specifically by removing titles, special chars, keeping alphabet/spaces."""
    if pd.isna(name) or name is None:
        return ""
    name_str = str(name).lower().strip()
    # Remove common prefixes
    prefixes = [r"^mr\.\s+", r"^ms\.\s+", r"^m/s\s+", r"^dr\.\s+", r"^shri\s+", r"^sh\.\s+", r"^smt\.\s+"]
    for p in prefixes:
        name_str = re.sub(p, "", name_str)
    # Remove non-alphanumeric except spaces
    name_str = re.sub(r'[^a-zA-Z0-9\s]', '', name_str)
    # Clean inner whitespaces
    name_str = re.sub(r'\s+', ' ', name_str).strip()
    return name_str.upper()


def clean_dealer_code(code):
    """Normalize dealer code to be uniform."""
    return clean_string(code)


def clean_aadhar(val):
    """Clean Aadhar numbers to 12 digits, handling floats or scientific notation."""
    if pd.isna(val) or val is None:
        return ""
    # Convert to string and remove spaces/dashes
    s = str(val).strip()
    # Handle float representation (like 1.23456789012e+11 or 123456789012.0)
    if '.0' in s:
        s = s.split('.0')[0]
    s = re.sub(r'\D', '', s)  # extract digits only
    if len(s) == 12:
        return s
    return ""


def clean_contact(val):
    """Clean contact number and return as a string without decimal part."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    if '.0' in s:
        s = s.split('.0')[0]
    s = re.sub(r'\D', '', s)
    return s


def calculate_recall_bucket(last_training_date, base_date=None):
    """
    Calculate the recall bucket based on the elapsed months since last training.
    Recall intervals:
    - CRITICAL: >= 36 months
    - OVERDUE: 24 - 35 months
    - DUE_SOON: 18 - 23 months
    - RECENT: 6 - 17 months
    - CURRENT_FY: < 6 months or trained in current fiscal year (start of current FY till base_date)
    """
    if pd.isna(last_training_date) or last_training_date is None:
        return NEVER_TRAINED_LABEL, NEVER_TRAINED_COLOR, "Never Trained"
        
    if isinstance(last_training_date, str):
        try:
            last_training_date = pd.to_datetime(last_training_date).date()
        except:
            return NEVER_TRAINED_LABEL, NEVER_TRAINED_COLOR, "Never Trained"
    elif isinstance(last_training_date, (pd.Timestamp, datetime.datetime)):
        last_training_date = last_training_date.date()

    if base_date is None:
        base_date = datetime.date.today()
    elif isinstance(base_date, (pd.Timestamp, datetime.datetime)):
        base_date = base_date.date()
        
    # Calculate difference in months
    diff_days = (base_date - last_training_date).days
    elapsed_months = diff_days / 30.4375  # average days per month
    
    # Check current fiscal year status
    # Get current FY start date
    curr_fy_details = FY_CALENDAR[CURRENT_FY]
    fy_start = curr_fy_details["start"]
    fy_end = curr_fy_details["end"]
    
    if last_training_date >= fy_start:
        # Trained in the current fiscal year
        return "CURRENT_FY", BRAND_CHARCOAL, "Current FY — trained this financial year"

    for bucket_name, min_months, color, desc in RECALL_BUCKETS:
        if elapsed_months >= min_months:
            return bucket_name, color, desc
            
    # Default fallback
    return "CURRENT_FY", BRAND_CHARCOAL, "Current FY — trained this financial year"


def get_skill_score(level):
    """Map skill level string to numeric score."""
    if pd.isna(level) or level is None:
        return -1
    val = str(level).strip().upper()
    return SKILL_SCORE_MAP.get(val, -1)


def get_skill_label(score):
    """Map numeric score back to label string."""
    return SKILL_LABELS.get(score, "NO TEST")


def average_skill_score(scores):
    """
    Calculate the average skill score, strictly ignoring 'NO TEST' (-1).
    Returns -1 if there are no valid scores.
    """
    valid_scores = [s for s in scores if s >= 0]
    if not valid_scores:
        return -1
    return np.mean(valid_scores)
