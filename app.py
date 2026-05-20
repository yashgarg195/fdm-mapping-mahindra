import datetime
import re
import io
import warnings
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from rapidfuzz import fuzz, process as rfprocess
import jellyfish
import recordlinkage
from symspellpy import SymSpell, Verbosity
warnings.filterwarnings('ignore')

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
SKILL_SCORE_MAP = {
    0: 0, "0": 0,
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
    "HIGH":       "#CCFFCC",
    "MEDIUM":     "#CCFFFF",
    "LOW":        "#FFE0A0",
    "FUZZY":      "#FFD0FF",
    "UNRESOLVED": "#FFCCCC",
}

FUZZY_PRIMARY_THRESHOLD   = 88
FUZZY_SECONDARY_THRESHOLD = 75
RECORDLINKAGE_SCORE_HIGH  = 4.0
RECORDLINKAGE_SCORE_FUZZY = 2.5

from utils import (
    average_skill_score, get_skill_label, get_skill_score, calculate_recall_bucket
)
from matching_engine import run_matching_pipeline
from excel_exporter import export_to_excel

# Set page configuration
st.set_page_config(
    page_title="Mahindra Manpower Training Analytics & Recall Portal",
    page_icon="🟥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using HTML/CSS injection
st.markdown(f"""
<style>
    /* Title Styling */
    .portal-title {{
        color: #E31837;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0px;
        letter-spacing: -1px;
        text-transform: uppercase;
    }}
    .portal-subtitle {{
        color: #4D4D4F;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 25px;
        text-transform: uppercase;
        border-bottom: 4px solid #E31837;
        padding-bottom: 8px;
    }}
    
    /* Metrics Card Styling */
    .kpi-card {{
        background-color: #FFFFFF;
        border: 2px solid #E6E7E8;
        border-top: 6px solid #E31837;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 15px;
        text-align: center;
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
    }}
    .kpi-label {{
        color: #4D4D4F;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .kpi-value {{
        color: #231F20;
        font-size: 2.5rem;
        font-weight: 800;
        margin-top: 5px;
    }}
    .kpi-desc {{
        color: #888888;
        font-size: 0.75rem;
        margin-top: 5px;
        text-transform: uppercase;
    }}
    
    /* Custom Badge / Pill */
    .badge {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #222;
        margin-right: 5px;
    }}
    
    /* Alert / Normal Info styling */
    .custom-alert {{
        background-color: {BRAND_LIGHT_GREY};
        border-radius: 6px;
        padding: 15px;
        border-left: 4px solid {BRAND_CHARCOAL};
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# App Logo / Header Section
row_logo, row_header = st.columns([1, 11])
with row_logo:
    st.markdown(f"<div style='font-size:4rem; text-align:center; color:{BRAND_RED}; font-weight:800;'>M</div>", unsafe_allow_html=True)
with row_header:
    st.markdown('<div class="portal-title">MAHINDRA & MAHINDRA TRACTORS</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-subtitle">Heavy-Duty Training Analytics & Recall Terminal</div>', unsafe_allow_html=True)

# Initialize Session State Variables
if "df_master" not in st.session_state:
    st.session_state["df_master"] = None
if "stats" not in st.session_state:
    st.session_state["stats"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Executive Dashboard"

# Sidebar - Instructions & Mode Selector
st.sidebar.markdown(f"<h3 style='color:{BRAND_RED};'>System Settings</h3>", unsafe_allow_html=True)

input_mode = st.sidebar.radio(
    "Select Input Mode:",
    ["Upload Roster & Training Logs", "Upload Matched Master File"],
    help="Select whether you want to process raw logs against the active roster or directly load a pre-matched file."
)

base_date = st.sidebar.date_input(
    "Recall Calculation Base Date:",
    datetime.date(2026, 5, 20),
    help="The date relative to which the training elapsed months and recall buckets are calculated."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<h3 style='color:{BRAND_RED};'>Data Source Files</h3>", unsafe_allow_html=True)

df_roster_input = None
df_training_inputs = []
df_direct_master = None

if input_mode == "Upload Roster & Training Logs":
    roster_file = st.sidebar.file_uploader(
        "1. Active Manpower Roster (Excel/CSV):",
        type=["xlsx", "csv"],
        help="Upload the active employee directory containing Star IDs, designations, etc."
    )
    training_files = st.sidebar.file_uploader(
        "2. Raw Training Logs (Excel/CSV):",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload one or more files containing training logs with potentially missing Star IDs."
    )
    
    if roster_file:
        try:
            if roster_file.name.endswith(".csv"):
                df_roster_input = pd.read_csv(roster_file)
            else:
                df_roster_input = pd.read_excel(roster_file, sheet_name=0)
            st.sidebar.success(f"Loaded Roster: {df_roster_input.shape[0]} rows")
        except Exception as e:
            st.sidebar.error(f"Error loading roster: {e}")
            
    if training_files:
        for tf in training_files:
            try:
                if tf.name.endswith(".csv"):
                    df_t = pd.read_csv(tf)
                else:
                    df_t = pd.read_excel(tf, sheet_name=0)
                df_training_inputs.append(df_t)
            except Exception as e:
                st.sidebar.error(f"Error loading {tf.name}: {e}")
        if df_training_inputs:
            tot_rows = sum([df.shape[0] for df in df_training_inputs])
            st.sidebar.success(f"Loaded {len(df_training_inputs)} training file(s): {tot_rows} total rows")

    # Action Button for pipeline execution
    if df_roster_input is not None and df_training_inputs:
        if st.sidebar.button("⚡ Run Matching & Consolidation Pipeline", use_container_width=True):
            with st.spinner("Executing offline fuzzy matching pipeline..."):
                # Merge multiple training logs into one
                df_all_training = pd.concat(df_training_inputs, ignore_index=True)
                
                # Execute pipeline
                df_master, stats = run_matching_pipeline(df_roster_input, df_all_training, base_date)
                
                # Store in session state
                st.session_state["df_master"] = df_master
                st.session_state["stats"] = stats
                st.sidebar.success("Pipeline executed successfully!")
    else:
        st.sidebar.warning("Please upload the Active Roster and at least one Training Log file to execute.")
        
else: # Direct Matched Master upload
    master_file = st.sidebar.file_uploader(
        "Upload Matched Master File (Excel/CSV):",
        type=["xlsx", "csv"],
        help="Upload an already compiled master file containing all 25+ columns."
    )
    if master_file:
        try:
            if master_file.name.endswith(".csv"):
                df_direct_master = pd.read_csv(master_file)
            else:
                # Load working file sheet if present
                xl = pd.ExcelFile(master_file)
                sheet_to_load = "Working file" if "Working file" in xl.sheet_names else xl.sheet_names[0]
                df_direct_master = pd.read_excel(master_file, sheet_name=sheet_to_load)
            
            # Defensive check: Ensure required columns exist, adding them with NaNs if missing
            req_cols = ['Joining Date', 'DOB', 'Training year', 'SKILL LEVEL - PRE', 'SKILL LEVEL - POST']
            for c in req_cols:
                if c not in df_direct_master.columns:
                    df_direct_master[c] = np.nan
                    
            if 'VALIDATED_SKILL_LEVEL' not in df_direct_master.columns:
                df_direct_master['VALIDATED_SKILL_LEVEL'] = "NO TEST"
            if 'MISSING_PREREQUISITE_FLAG' not in df_direct_master.columns:
                df_direct_master['MISSING_PREREQUISITE_FLAG'] = False
                    
            # Defensive check: if Joining Date, DOB are string types, cast them
            df_direct_master['Joining Date'] = pd.to_datetime(df_direct_master['Joining Date'], errors='coerce')
            df_direct_master['DOB'] = pd.to_datetime(df_direct_master['DOB'], errors='coerce')
            
            # Recalculate recall buckets for direct upload as well to match user-selected base date
            def fy_to_date(fy_str):
                if pd.isna(fy_str) or not isinstance(fy_str, str):
                    return None
                fy_str = fy_str.strip().upper()
                if fy_str in FY_CALENDAR:
                    return FY_CALENDAR[fy_str]["end"]
                return None
                
            df_direct_master['Training_End_Date'] = df_direct_master['Training year'].apply(fy_to_date)
            latest_training_dates = {}
            for star_id, group in df_direct_master.groupby('Star ID'):
                if pd.notna(star_id) and star_id != 0:
                    valid_dates = group['Training_End_Date'].dropna()
                    if not valid_dates.empty:
                        latest_training_dates[star_id] = max(valid_dates)
                        
            def get_latest_training_date(row):
                star_id = row.get('Star ID')
                if pd.notna(star_id) and star_id != 0 and star_id in latest_training_dates:
                    return latest_training_dates[star_id]
                return row.get('Training_End_Date')
                
            df_direct_master['LATEST_TRAINING_DATE'] = df_direct_master.apply(get_latest_training_date, axis=1)
            recall_results = df_direct_master['LATEST_TRAINING_DATE'].apply(lambda d: calculate_recall_bucket(d, base_date))
            df_direct_master['RECALL_STATUS'] = [r[0] for r in recall_results]
            df_direct_master['RECALL_COLOR'] = [r[1] for r in recall_results]
            df_direct_master['RECALL_DESCRIPTION'] = [r[2] for r in recall_results]
            df_direct_master.drop(columns=['Training_End_Date'], inplace=True, errors='ignore')
            
            # Flags
            df_direct_master["FUTURE_JOINING_FLAG"] = df_direct_master["Joining Date"].dt.year > 2026
            
            # Skill regression flag
            df_direct_master["pre_score"] = df_direct_master["SKILL LEVEL - PRE"].map(SKILL_SCORE_MAP).fillna(-1).astype(int)
            df_direct_master["post_score"] = df_direct_master["SKILL LEVEL - POST"].map(SKILL_SCORE_MAP).fillna(-1).astype(int)
            df_direct_master["SKILL_REGRESSION_FLAG"] = (df_direct_master["pre_score"] >= 0) & (df_direct_master["post_score"] >= 0) & (df_direct_master["post_score"] < df_direct_master["pre_score"])
            
            # Map default confidence
            if "MATCH_CONFIDENCE" not in df_direct_master.columns:
                df_direct_master["MATCH_CONFIDENCE"] = "HIGH"
                df_direct_master["MATCH_REASON"] = "Direct master file import"
                
            # Create synthetic stats for matching metrics
            total_rows = len(df_direct_master)
            trained_mask = df_direct_master["Training year"].notnull()
            trained_count = df_direct_master[trained_mask]["Star ID"].nunique()
            total_manpower = df_direct_master["Star ID"].nunique()
            untrained_count = total_manpower - trained_count
            
            conf_counts = df_direct_master["MATCH_CONFIDENCE"].value_counts().to_dict()
            for c in CONFIDENCE_ORDER:
                if c not in conf_counts:
                    conf_counts[c] = 0
                    
            stats = {
                "total_roster_count": total_manpower,
                "total_training_input_count": int(trained_mask.sum()),
                "total_master_count": total_rows,
                "matched_count": int(trained_mask.sum()),
                "untrained_count": untrained_count,
                "unresolved_count": conf_counts.get("UNRESOLVED", 0),
                "confidence_distribution": conf_counts,
                "passes_distribution": {},
                "future_joining_count": int(df_direct_master["FUTURE_JOINING_FLAG"].sum()),
                "skill_regression_count": int(df_direct_master["SKILL_REGRESSION_FLAG"].sum()),
                "missing_prerequisite_count": int(df_direct_master["MISSING_PREREQUISITE_FLAG"].sum())
            }
            
            st.session_state["df_master"] = df_direct_master
            st.session_state["stats"] = stats
            st.sidebar.success(f"Master file loaded: {df_direct_master.shape[0]} rows")
        except Exception as e:
            st.sidebar.error(f"Error loading master: {e}")

# Check if data has been loaded
df_master = st.session_state["df_master"]
stats = st.session_state["stats"]

if df_master is None:
    # Beautiful offline portal welcome page
    st.markdown(f"""
    <div class="custom-alert" style="border-left: 5px solid {BRAND_RED};">
        <h3 style="color:{BRAND_RED}; margin-top:0;">100% Offline Air-Gapped Portal</h3>
        <p>This system operates entirely locally on your workstation. No external cloud or neural model APIs are utilized.</p>
        <p><strong>To begin:</strong> Use the sidebar controls to upload either the <strong>Active Manpower Roster</strong> and its matching <strong>Training Logs</strong>, or load a previously consolidated <strong>Master Excel File</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=600&auto=format&fit=crop", width=400, caption="Enterprise Training Analytics Portal")
    st.stop()

# ── READ-ONLY FILTER CONTROLS (EXPLORATION ONLY) ──────────────────────────────
st.markdown("### 🚜 Dashboard Filters")
filter_row1, filter_row2 = st.columns(2)

with filter_row1:
    available_zones = sorted(df_master['Zone'].dropna().unique())
    selected_zones = st.multiselect("Select Zones:", available_zones, default=available_zones)
    
    allowed_states = []
    for z in selected_zones:
        allowed_states.extend(ZONE_STATE_MAP.get(z, []))
    available_states = sorted(df_master[df_master['Zone'].isin(selected_zones)]['State'].dropna().unique())
    selected_states = st.multiselect("Select States:", available_states, default=available_states)

with filter_row2:
    available_desigs = sorted(df_master['Designation'].dropna().unique())
    selected_desigs = st.multiselect("Select Designations:", available_desigs, default=available_desigs)
    
    available_recalls = sorted(df_master['RECALL_STATUS'].dropna().unique())
    selected_recalls = st.multiselect("Select Recall Statuses:", available_recalls, default=available_recalls)

# Filter Dataframe (Exploration only, does not write back)
df_filtered = df_master[
    (df_master['Zone'].isin(selected_zones)) &
    (df_master['State'].isin(selected_states)) &
    (df_master['Designation'].isin(selected_desigs)) &
    (df_master['RECALL_STATUS'].isin(selected_recalls))
]

# Unique Dealer Filter
available_dealers = sorted(df_filtered['Dealer Name'].dropna().unique())
selected_dealers = st.sidebar.multiselect("Filter by Dealership:", available_dealers, default=[])
if selected_dealers:
    df_filtered = df_filtered[df_filtered['Dealer Name'].isin(selected_dealers)]

# ── TOP LEVEL METRICS ─────────────────────────────────────────────────────────
st.markdown("---")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

total_emp = df_filtered['Star ID'].nunique()
trained_emp = df_filtered[df_filtered['Training year'].notnull()]['Star ID'].nunique()
coverage = (trained_emp / total_emp * 100) if total_emp > 0 else 0
overdue_critical_count = df_filtered[df_filtered['RECALL_STATUS'].isin(['CRITICAL', 'OVERDUE'])]['Star ID'].nunique()
missing_pre = df_filtered[df_filtered.get('MISSING_PREREQUISITE_FLAG', False)]['Star ID'].nunique()

with kpi_col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL HEADCOUNT</div><div class="kpi-value">{total_emp:,}</div><div class="kpi-desc">ACTIVE TECHNICIANS</div></div>', unsafe_allow_html=True)
with kpi_col2:
    st.markdown(f'<div class="kpi-card" style="border-top-color:#4D4D4F;"><div class="kpi-label">TRAINING COVERAGE</div><div class="kpi-value">{coverage:.1f}%</div><div class="kpi-desc">COMPLETED AT LEAST 1 TRAINING</div></div>', unsafe_allow_html=True)
with kpi_col3:
    st.markdown(f'<div class="kpi-card" style="border-top-color:#FF8C00;"><div class="kpi-label">CRITICAL / OVERDUE</div><div class="kpi-value">{overdue_critical_count:,}</div><div class="kpi-desc">IMMEDIATE RECALL REQUIRED</div></div>', unsafe_allow_html=True)
with kpi_col4:
    st.markdown(f'<div class="kpi-card" style="border-top-color:#231F20;"><div class="kpi-label">MISSING PREREQUISITES</div><div class="kpi-value">{missing_pre:,}</div><div class="kpi-desc">SKILL LADDER ANOMALIES</div></div>', unsafe_allow_html=True)

# ── EXPORT AND DATA TABLE ─────────────────────────────────────────────────────
st.markdown("### 📊 Live Data & Exports")
col_export1, col_export2 = st.columns(2)

with col_export1:
    # Full Master Export
    excel_data_master = export_to_excel(df_master, stats)
    st.download_button(
        label="🚜 Download Full Master Database (Excel)",
        data=excel_data_master,
        file_name=f"MAHINDRA_MASTER_FULL_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_export2:
    # Filtered Export (Passing the filtered subset and raw stats to preserve summary page)
    # The stats will remain global, but the master sheet will be filtered.
    excel_data_filtered = export_to_excel(df_filtered, stats)
    st.download_button(
        label="📥 Download Current Filtered View (Excel)",
        data=excel_data_filtered,
        file_name=f"MAHINDRA_FILTERED_VIEW_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.dataframe(df_filtered, use_container_width=True, height=600)
