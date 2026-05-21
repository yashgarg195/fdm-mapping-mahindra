"""
TRAINING ANALYTICS & MANPOWER INTELLIGENCE PLATFORM
Global Constants — Single Source of Truth

All business constants, column mappings, color palettes,
skill definitions, and lookup tables are defined here.
No other module should define these values independently.
"""
import datetime

# ── OFFICIAL BRAND CORPORATE COLOR PALETTE ────────────────────────────────────
BRAND_RED        = "#d4183d"
BRAND_CHARCOAL   = "#717182"
BRAND_DARK_CORE  = "#030213"
BRAND_LIGHT_GREY = "#ececf0"
BRAND_WHITE      = "#ffffff"

# ── FISCAL CALENDAR BOUNDARIES ────────────────────────────────────────────────
CURRENT_FY = "F-26"
FY_CALENDAR = {
    "F-23": {"start": datetime.date(2022, 4, 1), "end": datetime.date(2023, 3, 31)},
    "F-24": {"start": datetime.date(2023, 4, 1), "end": datetime.date(2024, 3, 31)},
    "F-25": {"start": datetime.date(2024, 4, 1), "end": datetime.date(2025, 3, 31)},
    "F-26": {"start": datetime.date(2025, 4, 1), "end": datetime.date(2026, 3, 31)},
}

# ── SKILL LEVEL MAPPINGS ─────────────────────────────────────────────────────
SKILL_SCORE_MAP = {
    0: 0, "0": 0,
    "L1": 1, "L2": 2, "L3": 3, "L4": 4,
    "NO TEST": -1,
}
SKILL_LABELS = {-1: "NO TEST", 0: "0", 1: "L1", 2: "L2", 3: "L3", 4: "L4"}

# ── COMPANY 5-POINT SCALE (internal 0-4 → company 1-5) ──────────────────────
# Maps internal numeric skill scores to the company-standard 1-5 rating scale.
COMPANY_SCALE_MAP = {-1: None, 0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
COMPANY_SCALE_LABELS = {
    1: ("Beginner",      "No formal training or untested — needs onboarding"),
    2: ("Basic",         "Completed L1 foundations — can assist under supervision"),
    3: ("Intermediate",  "Completed L2 — can handle routine tasks independently"),
    4: ("Advanced",      "Completed L3 — can troubleshoot and mentor juniors"),
    5: ("Expert",        "Completed L4 — certified specialist, can lead audits"),
}
COMPANY_SCALE_COLORS = {
    1: "#FF6B6B",   # Red
    2: "#FFA94D",   # Orange
    3: "#FFD43B",   # Yellow
    4: "#69DB7C",   # Green
    5: "#228BE6",   # Blue
}

# ── TRAINING STATUS VALUES ───────────────────────────────────────────────────
TRAINING_STATUSES = [
    "ELIGIBLE",
    "NOMINATED",
    "PENDING",
    "ATTENDED",
    "COMPLETED",
    "DEFERRED",
    "SKIPPED",
    "NOT_ELIGIBLE",
]

# ── CONFIDENCE TIERS ─────────────────────────────────────────────────────────
CONFIDENCE_ORDER = ["HIGH", "MEDIUM", "LOW", "FUZZY", "UNRESOLVED"]
CONFIDENCE_COLORS = {
    "HIGH":       "#CCFFCC",
    "MEDIUM":     "#CCFFFF",
    "LOW":        "#FFE0A0",
    "FUZZY":      "#FFD0FF",
    "UNRESOLVED": "#FFCCCC",
}

# ── RECALL INTERVAL BUCKETS (legacy reference, replaced by rolling backlog) ──
RECALL_BUCKETS = [
    ("CRITICAL",   36, BRAND_RED,       "Critical — 3+ years since last training"),
    ("OVERDUE",    24, "#FF8C00",       "Overdue — 2–3 years since last training"),
    ("DUE_SOON",   18, "#FFD700",       "Due Soon — 18–24 months since last training"),
    ("RECENT",      6, "#90EE90",       "Recent — 6–18 months since last training"),
    ("CURRENT_FY",  0, BRAND_CHARCOAL,  "Current FY — trained this financial year"),
]
NEVER_TRAINED_COLOR = BRAND_LIGHT_GREY
NEVER_TRAINED_LABEL = "NEVER_TRAINED"

# ── PRODUCTION MODEL TEXT STANDARDIZATION MAP ────────────────────────────────
MODEL_NORMALISATION_MAP = {
    "INSTALATION":       "INSTALLATION",
    "L1-L2 TRAINING":    "L1 L2 TRAINING",
    "M LIFT HYDRAULIC":  "M-LIFT HYDRAULICS",
    "FARM MACHNINERY":   "FARM MACHINERY",
    "FARM MACHINERY":    "FARM MACHINERY",
    "YUVO HYDRAULICS":   "YUVO HYDRAULICS",
}

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
    "MSDC - TRAINING": "PROCESS", "L1 L2 TRAINING": "PROCESS", "N - PAGE": "PROCESS",
}

# ── DESIGNATION LISTS ────────────────────────────────────────────────────────
TECHNICAL_DESIGNATIONS = [
    "Technician", "Installer", "Service Advisor (FLA)", "Techguru", "Electrician",
]
ALL_DESIGNATIONS = TECHNICAL_DESIGNATIONS + [
    "Salesman", "Sales Manager", "Works Manager",
    "Branch Manager", "General Manager", "Team Leader",
]

# ── ZONE → STATE MAPPING ────────────────────────────────────────────────────
ZONE_STATE_MAP = {
    "Zone1": ["Haryana", "Punjab", "Rajasthan East", "Rajasthan West"],
    "Zone2": ["UP Central", "UP East", "UP West"],
    "Zone3": ["Bihar", "Jharkhand", "North East", "West Bengal"],
    "Zone4": ["Chhattisgarh", "Madhya Pradesh East", "Madhya Pradesh West", "Odisha"],
    "Zone5": ["Gujarat", "Karnataka", "Maharashtra East", "Maharashtra West"],
    "Zone6": ["Andhra Pradesh", "Tamil Nadu", "Telangana"],
}

# Reverse lookup: state → zone
STATE_ZONE_MAP = {}
for _zone, _states in ZONE_STATE_MAP.items():
    for _state in _states:
        STATE_ZONE_MAP[_state] = _zone

# ── COLUMN NAME ALIASES ─────────────────────────────────────────────────────
# Maps common variations in uploaded files to canonical column names.
COLUMN_ALIASES = {
    "STAR_ID":           "Star ID",
    "STAR ID":           "Star ID",
    "Star_ID":           "Star ID",
    "StarID":            "Star ID",
    "STARID":            "Star ID",
    "star id":           "Star ID",
    "EMPLOYEE_NAME":     "Name",
    "Employee_Name":     "Name",
    "Employee Name":     "Name",
    "EMP_NAME":          "Name",
    "Emp_Name":          "Name",
    "EMPNAME":           "Name",
    "NAME":              "Name",
    "DEALER_CODE":       "Dealer Code",
    "Dealer_Code":       "Dealer Code",
    "DealerCode":        "Dealer Code",
    "DEALERCODE":        "Dealer Code",
    "DEALER_NAME":       "Dealer Name",
    "Dealer_Name":       "Dealer Name",
    "DealerName":        "Dealer Name",
    "DEALERNAME":        "Dealer Name",
    "DESIGNATION":       "Designation",
    "Desig":             "Designation",
    "ZONE":              "Zone",
    "STATE":             "State",
    "REGION":            "Region",
    "CONTACT":           "Contact No",
    "Contact":           "Contact No",
    "CONTACT_NO":        "Contact No",
    "Contact_No":        "Contact No",
    "ContactNo":         "Contact No",
    "PHONE":             "Contact No",
    "Phone":             "Contact No",
    "AADHAAR":           "AadharCardNumber",
    "Aadhaar":           "AadharCardNumber",
    "AADHAR":            "AadharCardNumber",
    "Aadhar":            "AadharCardNumber",
    "AadharCard":        "AadharCardNumber",
    "AADHAR_CARD":       "AadharCardNumber",
    "EMP_CODE":          "Emp Code",
    "Emp_Code":          "Emp Code",
    "EmpCode":           "Emp Code",
    "EMPCODE":           "Emp Code",
    "Employee Code":     "Emp Code",
    "SKILL LEVEL - PRE": "SKILL LEVEL - PRE",
    "Pre_Skill":         "SKILL LEVEL - PRE",
    "PRE_SKILL":         "SKILL LEVEL - PRE",
    "SKILL LEVEL - POST":"SKILL LEVEL - POST",
    "Post_Skill":        "SKILL LEVEL - POST",
    "POST_SKILL":        "SKILL LEVEL - POST",
    "TRAINING_YEAR":     "Training year",
    "Training_Year":     "Training year",
    "TrainingYear":      "Training year",
    "FY":                "Training year",
    "TRAINING_DATE":     "LAST PRODUCT TRANIING ON",
    "Training_Date":     "LAST PRODUCT TRANIING ON",
    "TrainingDate":      "LAST PRODUCT TRANIING ON",
    "TRAINING_TYPE":     "LAST MODEL TRAINED",
    "Training_Type":     "LAST MODEL TRAINED",
    "TrainingType":      "LAST MODEL TRAINED",
    "JOINING_DATE":      "Joining Date",
    "Joining_Date":      "Joining Date",
    "JoiningDate":       "Joining Date",
    "DOB":               "DOB",
    "Date_of_Birth":     "DOB",
    "GENDER":            "Gender",
    "FATHER_NAME":       "Father Name",
    "Father_Name":       "Father Name",
    "DEALER_AO":         "Dealer AO",
    "Dealer_AO":         "Dealer AO",
    "DealerAO":          "Dealer AO",
    "LOCATION":          "Location",
    "AGE":               "Age",
}

# ── NAME ABBREVIATION EXPANSION DICTIONARY ───────────────────────────────────
NAME_ABBREVIATIONS = {
    "KR":    "KUMAR",
    "KMR":   "KUMAR",
    "KUMR":  "KUMAR",
    "SNH":   "SINGH",
    "SGH":   "SINGH",
    "SNG":   "SINGH",
    "MD":    "MOHAMMAD",
    "MHD":   "MOHAMMAD",
    "MOHD":  "MOHAMMAD",
    "CH":    "CHANDRA",
    "CHNDR": "CHANDRA",
    "RAM":   "RAM",
    "RJ":    "RAJ",
    "SK":    "SHAIKH",
    "SHK":   "SHAIKH",
    "JHA":   "JHA",
    "MR":    "",       # title, strip
    "MS":    "",       # title, strip
    "MRS":   "",       # title, strip
    "SHRI":  "",       # title, strip
    "SMT":   "",       # title, strip
    "DR":    "",       # title, strip
}

# ── STATE ABBREVIATION EXPANSION ─────────────────────────────────────────────
STATE_ABBREVIATIONS = {
    "MH":    "Maharashtra",
    "UP":    "Uttar Pradesh",
    "MP":    "Madhya Pradesh",
    "RJ":    "Rajasthan",
    "GJ":    "Gujarat",
    "KA":    "Karnataka",
    "TN":    "Tamil Nadu",
    "AP":    "Andhra Pradesh",
    "TS":    "Telangana",
    "PB":    "Punjab",
    "HR":    "Haryana",
    "BR":    "Bihar",
    "JH":    "Jharkhand",
    "WB":    "West Bengal",
    "OD":    "Odisha",
    "CG":    "Chhattisgarh",
    "NE":    "North East",
}

# ── ROSTER CANONICAL COLUMNS ─────────────────────────────────────────────────
ROSTER_COLUMNS = [
    "Star ID", "Zone", "State", "Dealer AO", "Dealer Code", "Dealer Name",
    "Dealer Operational Status", "Location", "Emp Code", "Name", "Designation",
    "Joining Date", "Contact No", "AadharCardNumber", "Gender", "Father Name",
    "DOB", "Residence Location", "Age",
]

# ── TRAINING CANONICAL COLUMNS ───────────────────────────────────────────────
TRAINING_COLUMNS = [
    "Star ID", "Name", "Dealer Code", "Dealer AO", "Designation", "Emp Code",
    "AadharCardNumber", "Training year", "SKILL LEVEL - PRE", "SKILL LEVEL - POST",
    "LAST PRODUCT TRANIING ON", "LAST MODEL TRAINED",
]

# ── COLUMNS TO DROP ON LOAD ──────────────────────────────────────────────────
DROP_COLUMNS = ["Star ID.1"]
