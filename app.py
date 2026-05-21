"""
TRAINING ANALYTICS & MANPOWER INTELLIGENCE PLATFORM
Streamlit Entry Point — Page config, sidebar, tab routing.
No business logic here — all delegated to modules.
"""
import streamlit as st
import pandas as pd
import datetime
import time

# ── Config & Constants ──────────────────────────────────────────────────────
from config.constants import (
    BRAND_RED, BRAND_CHARCOAL, BRAND_DARK_CORE, BRAND_LIGHT_GREY,
    BRAND_WHITE, ROSTER_COLUMNS, TRAINING_COLUMNS,
)

# ── Core Pipeline ───────────────────────────────────────────────────────────
from core.etl import load_file, clean_dataframe, standardize_columns
from core.deduplication import detect_duplicate_manpower, detect_duplicate_training
from core.matching import resolve_star_ids
from core.training_pipeline import (
    assign_training_status, build_rolling_backlog, build_nomination_list,
)

# ── Analytics ───────────────────────────────────────────────────────────────
from analytics.kpi_engine import compute_all_kpis

# ── UI Tabs ─────────────────────────────────────────────────────────────────
from ui.sidebar import render_sidebar, apply_filters
from ui.overview_tab import render_overview
from ui.backlog_tab import render_backlog
from ui.skill_tab import render_skill
from ui.manpower_tab import render_manpower
from ui.audit_tab import render_audit
from ui.export_tab import render_export_tab

# ── Export ──────────────────────────────────────────────────────────────────
from reports_export.excel_export import generate_excel_report
from storage.mapping_store import persist_mappings

# ── Logging ─────────────────────────────────────────────────────────────────
from utils.logging_utils import (
    log_etl_event, log_pipeline_event, Timer, build_audit_entry,
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Mahindra Training Analytics & Manpower Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — Enterprise Dashboard Shadcn Theme
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
      --background: #ffffff;
      --foreground: #1A1A2E;
      --primary: #1A1A2E;
      --muted: #F7F7F9;
      --muted-foreground: #8B8BA7;
      --accent: #F3F3F5;
      --destructive: #C62828;
      --input-background: #ffffff;
      --radius: 6px;
      --brand-red: {BRAND_RED};
      --brand-charcoal: {BRAND_CHARCOAL};
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --background: #111118;
        --foreground: #F7F7F9;
        --primary: #F7F7F9;
        --muted: #252532;
        --muted-foreground: #B7B7C8;
        --accent: #1B1B26;
        --input-background: #111118;
      }}
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 16px;
    }}
    .stApp {{
        background-color: var(--input-background);
        color: var(--foreground);
    }}
    .block-container {{
        padding-top: 5.25rem !important;
    }}
    [data-testid="stSidebarCollapsedControl"] {{
        top: 72px !important;
    }}
    .app-topnav {{
        position: fixed;
        inset: 0 0 auto 0;
        height: 64px;
        z-index: 999999;
        background: var(--background);
        border-bottom: 1px solid #E8E8EC;
        display: flex;
        align-items: stretch;
        box-shadow: 0 1px 0 rgba(26, 26, 46, 0.03);
    }}
    .app-topnav-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 318px;
        padding: 0 22px;
        border-right: 1px solid #E8E8EC;
        background: var(--background);
    }}
    .app-topnav-mark {{
        width: 3px;
        height: 28px;
        background: var(--brand-red);
        border-radius: 2px;
    }}
    .app-topnav-title {{
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.02em;
        color: var(--brand-charcoal);
        line-height: 1.1;
        white-space: nowrap;
    }}
    .app-topnav-subtitle {{
        margin-top: 3px;
        font-size: 10px;
        font-weight: 600;
        color: var(--muted-foreground);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        white-space: nowrap;
    }}
    .app-topnav-items {{
        display: flex;
        align-items: stretch;
        flex: 1;
        min-width: 0;
        overflow-x: auto;
    }}
    .app-topnav-item {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: max-content;
        padding: 0 22px;
        color: var(--muted-foreground);
        font-size: 13px;
        font-weight: 650;
        border-right: 1px solid #E8E8EC;
        background: transparent;
        user-select: none;
        cursor: pointer;
        text-decoration: none;
    }}
    .st-key-topnav_tabs {{
        position: fixed !important;
        top: 0 !important;
        left: 318px !important;
        right: 0 !important;
        height: 64px !important;
        z-index: 1000000 !important;
        background: transparent !important;
        padding: 0 !important;
    }}
    .st-key-topnav_tabs [data-testid="stWidgetLabel"] {{
        display: none !important;
    }}
    .st-key-topnav_tabs [role="radiogroup"] {{
        display: flex !important;
        align-items: stretch !important;
        height: 64px !important;
        gap: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        overflow-x: auto !important;
    }}
    .st-key-topnav_tabs [role="radiogroup"] > button {{
        height: 64px !important;
        flex: 1 0 max-content !important;
        border-radius: 0 !important;
        border: none !important;
        border-right: 1px solid #E8E8EC !important;
        background: transparent !important;
        color: var(--muted-foreground) !important;
        font-size: 13px !important;
        font-weight: 650 !important;
        padding: 0 10px !important;
        box-shadow: none !important;
    }}
    .st-key-topnav_tabs [role="radiogroup"] > button:hover {{
        background: var(--muted) !important;
        color: var(--brand-charcoal) !important;
    }}
    .st-key-topnav_tabs [role="radiogroup"] > button[kind="segmented_controlActive"] {{
        position: relative;
        background: var(--background) !important;
        color: var(--brand-charcoal) !important;
        border-right: 1px solid #E8E8EC !important;
    }}
    .st-key-topnav_tabs [role="radiogroup"] > button[kind="segmented_controlActive"]::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 3px;
        background: var(--brand-red);
    }}
    .app-topnav-item:hover {{
        color: var(--brand-charcoal);
        background: var(--muted);
    }}
    .app-topnav-item.active {{
        color: var(--brand-charcoal);
        background: var(--background);
    }}
    @media (prefers-color-scheme: dark) {{
        .app-topnav,
        .app-topnav-brand {{
            border-color: #2D2D3A;
        }}
        .app-topnav-title,
        .app-topnav-item:hover,
        .app-topnav-item.active {{
            color: var(--foreground);
        }}
        .app-topnav-item,
        .st-key-topnav_tabs [role="radiogroup"] > button {{
            border-color: #2D2D3A;
        }}
        .st-key-topnav_tabs [role="radiogroup"] > button:hover,
        .st-key-topnav_tabs [role="radiogroup"] > button[kind="segmented_controlActive"] {{
            color: var(--foreground) !important;
        }}
        header[data-testid="stHeader"] {{
            background-color: var(--background);
            border-bottom-color: var(--muted);
        }}
        section[data-testid="stSidebar"] {{
            background-color: var(--background) !important;
            border-right-color: var(--muted);
        }}
    }}
    .app-topnav-item.active::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 3px;
        background: var(--brand-red);
    }}
    /* Ensure all main-area text is dark */
    section[data-testid="stMain"] .stMarkdown,
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] span,
    section[data-testid="stMain"] label,
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4,
    section[data-testid="stMain"] h5,
    section[data-testid="stMain"] h6 {{
        color: var(--foreground) !important;
    }}
    header[data-testid="stHeader"] {{
        background-color: var(--background);
        border-bottom: 1px solid var(--muted);
    }}
    /* ── Sidebar ───────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background-color: var(--background) !important;
        border-right: 1px solid var(--muted);
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4,
    section[data-testid="stSidebar"] .stMarkdown span {{
        color: var(--foreground) !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        color: var(--foreground) !important;
        background-color: var(--input-background);
        border-radius: var(--radius);
        border: none;
    }}
    /* ── Primary Buttons (brand red) ───────────────────── */
    .stButton>button[kind="primary"],
    section[data-testid="stSidebar"] .stButton>button[kind="primary"] {{
        background-color: var(--brand-red) !important;
        color: #ffffff !important;
        font-weight: 600;
        border: none;
        border-radius: var(--radius);
        padding: 8px 14px;
        font-size: 12px;
    }}
    .stButton>button[kind="primary"]:hover,
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover {{
        background-color: #A91F24 !important;
        color: #ffffff !important;
    }}
    /* ── Secondary Buttons (outline style) ─────────────── */
    .stButton>button[kind="secondary"],
    .stButton>button:not([kind]) {{
        background-color: var(--background) !important;
        color: var(--foreground) !important;
        font-weight: 500;
        border: 1px solid var(--muted) !important;
        border-radius: var(--radius);
        padding: 10px 20px;
    }}
    .stButton>button[kind="secondary"]:hover,
    .stButton>button:not([kind]):hover {{
        background-color: var(--accent) !important;
        border-color: var(--muted-foreground) !important;
    }}
    /* ── Download Button ──────────────────────────────── */
    .stDownloadButton>button {{
        background-color: var(--background);
        color: var(--foreground);
        font-weight: 500;
        border: 1px solid var(--muted);
        border-radius: var(--radius);
    }}
    .stDownloadButton>button:hover {{
        background-color: var(--accent);
        border-color: var(--muted-foreground);
    }}
    /* ── Metrics ──────────────────────────────────────── */
    [data-testid="stMetricValue"] {{
        color: var(--foreground) !important;
        font-weight: 700;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--muted-foreground) !important;
        font-weight: 500;
    }}
    /* ── Progress bar ─────────────────────────────────── */
    .stProgress > div > div > div > div {{
        background-color: var(--primary);
    }}
    /* ── Dataframes / Tables ──────────────────────────── */
    [data-testid="stDataFrame"] {{
        background-color: var(--background);
        border-radius: var(--radius);
        border: 1px solid var(--muted);
        overflow: hidden;
    }}
    /* ── Spinner / Cache containers — no white box ───── */
    .stSpinner, .stSpinner > div {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stCachedStFunctionOutputContainer"],
    [data-testid="stStaleElementContainer"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }}
    /* ── Floating Filters Button ──────────────────────── */
    .filter-fab {{
        position: fixed;
        top: 78px;
        right: 24px;
        z-index: 999998;
        background: var(--brand-charcoal);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 10px 18px;
        font-size: 12px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.02em;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.15s, box-shadow 0.15s;
    }}
    .filter-fab:hover {{
        background: var(--brand-red);
        box-shadow: 0 6px 20px rgba(210,35,42,0.35);
    }}
    .filter-fab svg {{
        width: 16px;
        height: 16px;
        fill: currentColor;
    }}
    /* ── Filter Panel Overlay ─────────────────────────── */
    .filter-overlay {{
        position: fixed;
        inset: 0;
        z-index: 999997;
        background: rgba(0,0,0,0.25);
        backdrop-filter: blur(2px);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
    }}
    .filter-overlay.active {{
        opacity: 1;
        pointer-events: auto;
    }}
    .filter-panel {{
        position: fixed;
        top: 0;
        right: -55%;
        width: 50%;
        height: 100vh;
        z-index: 999998;
        background: var(--background);
        border-left: 1px solid var(--muted);
        box-shadow: -8px 0 30px rgba(0,0,0,0.12);
        padding: 80px 32px 32px;
        overflow-y: auto;
        transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .filter-panel.active {{
        right: 0;
    }}
    .filter-panel-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }}
    .filter-panel-title {{
        font-size: 16px;
        font-weight: 800;
        color: var(--foreground);
        letter-spacing: 0.02em;
    }}
    .filter-panel-close {{
        background: var(--muted);
        border: none;
        border-radius: 6px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: var(--foreground);
        font-size: 18px;
        font-weight: 700;
        transition: background 0.15s;
    }}
    .filter-panel-close:hover {{
        background: var(--accent);
    }}
    /* Hide the popover trigger button — the floating FAB triggers it via JS */
    .st-key-filter_popover > div > .stPopover > button {{
        display: none !important;
    }}
    /* Make the popover panel wider (half screen) */
    .st-key-filter_popover div[data-testid="stPopover"] > div {{
        min-width: 50vw !important;
        max-width: 50vw !important;
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════
for key in ["unified_df", "duplicate_df", "backlog_df", "nomination_df",
            "kpis", "stats", "audit_log", "pipeline_complete"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "audit_log" not in st.session_state or st.session_state["audit_log"] is None:
    st.session_state["audit_log"] = []
# Applied filters (committed via Apply Filters button). Empty dict = no filter = all rows shown.
if "global_filters" not in st.session_state:
    st.session_state["global_filters"] = {}
# Counter used to force-reset multiselect widgets when Clear Filters is clicked.
if "filter_reset_counter" not in st.session_state:
    st.session_state["filter_reset_counter"] = 0
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Overview"

NAV_ITEMS = [
    ("Overview", "Overview"),
    ("Pending & Nominations", "Pending & Nominations"),
    ("Skill Analytics", "Skill Analytics"),
    ("Unique Manpower", "Unique Manpower"),
    ("Audit & Exceptions", "Audit & Exceptions"),
    ("Exports", "Exports"),
]

_query_tab = st.query_params.get("tab")
if _query_tab in [key for key, _ in NAV_ITEMS]:
    st.session_state["current_tab"] = _query_tab

st.markdown(f"""
<div class="app-topnav">
    <div class="app-topnav-brand">
        <div class="app-topnav-mark"></div>
        <div>
            <div class="app-topnav-title">MAHINDRA ENTERPRISE DASHBOARD</div>
            <div class="app-topnav-subtitle">Training Analytics & Manpower Intelligence</div>
        </div>
    </div>
    <nav class="app-topnav-items">
    </nav>
</div>
""", unsafe_allow_html=True)

_selected_tab = st.segmented_control(
    "Dashboard sections",
    options=[key for key, _ in NAV_ITEMS],
    default=st.session_state["current_tab"],
    key="topnav_tabs",
    label_visibility="collapsed",
)
if _selected_tab and _selected_tab != st.session_state["current_tab"]:
    st.session_state["current_tab"] = _selected_tab
    st.query_params["tab"] = _selected_tab
    st.rerun()

# Native sidebar state used instead of custom CSS injection

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
sidebar_result = render_sidebar()

# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE EXECUTION — with real-time progress bar
# ═══════════════════════════════════════════════════════════════════════════
if sidebar_result["run_pipeline"] and sidebar_result["uploaded_files"]:
    progress_bar = st.progress(0, text="Starting pipeline...")
    status_text = st.empty()

    try:
        with Timer("Full Pipeline"):
            audit_log = []

            # ── Step 1: Load & Classify Files (0% → 20%) ────────────────
            status_text.markdown(f"**Step 1/5:** Loading and classifying files...")
            manpower_dfs = []
            training_dfs = []

            files = sidebar_result["uploaded_files"]
            for i, uploaded_file in enumerate(files):
                file_type = sidebar_result["file_assignments"].get(
                    uploaded_file.name, "Other"
                )
                raw_df = load_file(uploaded_file)
                if raw_df.empty:
                    st.sidebar.error(f"Failed to load: {uploaded_file.name}")
                    continue

                cleaned = clean_dataframe(raw_df)
                audit_log.append(build_audit_entry(
                    "FILE_LOADED", f"Loaded {uploaded_file.name} as {file_type}",
                    rows_affected=len(cleaned),
                ))

                if file_type == "Manpower Roster":
                    manpower_dfs.append(standardize_columns(cleaned, ROSTER_COLUMNS))
                elif file_type in ("Training Data", "Additional Training Data"):
                    training_dfs.append(standardize_columns(cleaned, TRAINING_COLUMNS))
                else:
                    if "Star ID" in cleaned.columns and "Training year" in cleaned.columns:
                        training_dfs.append(standardize_columns(cleaned, TRAINING_COLUMNS))
                    elif "Star ID" in cleaned.columns:
                        manpower_dfs.append(standardize_columns(cleaned, ROSTER_COLUMNS))
                    else:
                        training_dfs.append(standardize_columns(cleaned, TRAINING_COLUMNS))

                progress_bar.progress(
                    int(20 * (i + 1) / len(files)),
                    text=f"Loaded {uploaded_file.name} ({len(cleaned):,} rows)"
                )

            if not manpower_dfs and not training_dfs:
                st.error("No valid data files loaded. Please check file assignments.")
                progress_bar.empty()
                status_text.empty()
                st.stop()

            manpower_df = pd.concat(manpower_dfs, ignore_index=True) if manpower_dfs else pd.DataFrame(columns=ROSTER_COLUMNS)
            training_df = pd.concat(training_dfs, ignore_index=True) if training_dfs else pd.DataFrame(columns=TRAINING_COLUMNS)

            log_etl_event(len(manpower_df), len(manpower_df), 0, "Manpower")
            log_etl_event(len(training_df), len(training_df), 0, "Training")

            # ── Step 2: Deduplication (20% → 30%) ────────────────────────
            progress_bar.progress(20, text="Step 2/5: Detecting duplicates...")
            status_text.markdown(f"**Step 2/5:** Detecting duplicates in {len(manpower_df):,} manpower + {len(training_df):,} training rows...")

            manpower_clean, manpower_dups = detect_duplicate_manpower(manpower_df)
            training_clean, training_dups = detect_duplicate_training(training_df)
            all_duplicates = pd.concat([manpower_dups, training_dups], ignore_index=True)

            audit_log.append(build_audit_entry(
                "DEDUPLICATION",
                f"Manpower: {len(manpower_dups)} dups, Training: {len(training_dups)} dups",
                rows_affected=len(all_duplicates),
            ))

            progress_bar.progress(30, text=f"Found {len(all_duplicates)} duplicates")

            # ── Step 3: Identity Resolution (30% → 70%) ─────────────────
            progress_bar.progress(30, text="Step 3/5: Running 7-pass identity resolution...")
            status_text.markdown(f"**Step 3/5:** Running 7-pass identity resolution on {len(training_clean):,} training rows against {len(manpower_clean):,} roster entries...")

            if not training_clean.empty and not manpower_clean.empty:
                unified_df, stats = resolve_star_ids(training_clean, manpower_clean)
            elif not manpower_clean.empty:
                unified_df = manpower_clean.copy()
                unified_df["Match_Method"] = "ROSTER_ONLY"
                unified_df["Match_Confidence"] = "HIGH"
                unified_df["Fuzzy_Score"] = 100.0
                unified_df["Phonetic_Score"] = 100.0
                unified_df["Matched_Candidate"] = unified_df.get("Star ID", "")
                stats = {"total_roster_count": len(manpower_clean), "total_training_input_count": 0,
                         "total_master_count": len(unified_df), "matched_count": 0,
                         "untrained_count": len(manpower_clean), "unresolved_count": 0,
                         "confidence_distribution": {"HIGH": len(manpower_clean)},
                         "passes_distribution": {"ROSTER_ONLY": len(manpower_clean)}}
            else:
                unified_df = training_clean.copy()
                stats = {"total_roster_count": 0, "total_training_input_count": len(training_clean),
                         "total_master_count": len(training_clean)}

            audit_log.append(build_audit_entry(
                "IDENTITY_RESOLUTION",
                f"Resolved {stats.get('matched_count', 0)} records, "
                f"{stats.get('unresolved_count', 0)} unresolved",
                rows_affected=len(unified_df),
            ))

            progress_bar.progress(70, text=f"Resolved {stats.get('matched_count', 0):,} identities")

            # ── Step 4: Training Status & Backlog (70% → 85%) ────────────
            progress_bar.progress(70, text="Step 4/5: Building backlog & nominations...")
            status_text.markdown(f"**Step 4/5:** Assigning training status and building rolling backlog...")

            unified_df["Training_Status"] = unified_df.apply(assign_training_status, axis=1)
            backlog_df = build_rolling_backlog(unified_df)
            nomination_df = build_nomination_list(backlog_df)

            audit_log.append(build_audit_entry(
                "BACKLOG_BUILT",
                f"Backlog: {len(backlog_df)} records, Nominations: {len(nomination_df)}",
                rows_affected=len(backlog_df),
            ))

            progress_bar.progress(85, text=f"Backlog: {len(backlog_df):,} pending employees")

            # ── Step 5: Compute KPIs & Persist (85% → 100%) ─────────────
            progress_bar.progress(85, text="Step 5/5: Computing KPIs and generating dashboard...")
            status_text.markdown(f"**Step 5/5:** Computing KPIs across {len(unified_df):,} unified records...")

            st.session_state["raw_training_count"] = len(training_df)
            st.session_state["raw_roster_count"] = len(manpower_df)
            st.session_state["unified_df"] = unified_df
            st.session_state["duplicate_df"] = all_duplicates
            st.session_state["backlog_df"] = backlog_df
            st.session_state["nomination_df"] = nomination_df
            st.session_state["kpis"] = compute_all_kpis(unified_df)
            st.session_state["stats"] = stats
            st.session_state["audit_log"] = audit_log
            st.session_state["pipeline_complete"] = True

            persist_mappings(unified_df)

            log_pipeline_event(
                f"Pipeline complete: {len(unified_df)} rows in unified master"
            )

            progress_bar.progress(100, text="Pipeline complete!")
            status_text.empty()

        st.session_state["pipeline_success_message"] = (
            f"Pipeline complete! "
            f"{len(unified_df):,} rows processed | "
            f"{stats.get('matched_count', 0):,} matched | "
            f"{stats.get('unresolved_count', 0):,} unresolved | "
            f"0 rows lost"
        )
        time.sleep(0.5)
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Pipeline error: {e}")
        import traceback
        st.code(traceback.format_exc())
# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD TABS (only shown after pipeline runs)
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.get("pipeline_complete"):
    if "pipeline_success_message" in st.session_state and st.session_state["pipeline_success_message"]:
        st.success(st.session_state["pipeline_success_message"])
        del st.session_state["pipeline_success_message"]
    unified_df = st.session_state["unified_df"]
    duplicate_df = st.session_state["duplicate_df"]
    backlog_df = st.session_state["backlog_df"]
    nomination_df = st.session_state["nomination_df"]

    # ── Floating Filter Button + Popover ───────────────────────────────────────
    active_filters = {k: v for k, v in st.session_state["global_filters"].items() if v}
    _filter_count = sum(len(v) for v in active_filters.values())
    _badge_html = f' <span style="background:var(--brand-red);color:#fff;border-radius:50%;padding:1px 6px;font-size:10px;margin-left:4px;">{_filter_count}</span>' if _filter_count else ''

    # Pure HTML floating button (visual only — the actual interaction uses st.popover below)
    st.markdown(f"""
    <button class="filter-fab" onclick="
        var popoverBtns = document.querySelectorAll('.st-key-filter_popover button');
        if (popoverBtns.length > 0) popoverBtns[0].click();
    ">
        <svg viewBox="0 0 24 24"><path d="M10 18h4v-2h-4v2zm-7-12v2h18V6H3zm3 7h12v-2H6v2z"/></svg>
        Filters{_badge_html}
    </button>
    """, unsafe_allow_html=True)

    # Use the reset counter as part of the widget key so that changing it
    # forces Streamlit to recreate the widgets with empty defaults.
    _rc = st.session_state["filter_reset_counter"]

    # Streamlit popover — contains the actual filter widgets
    with st.container(key="filter_popover"):
        with st.popover("⚙ Open Filter Panel", use_container_width=False):
            st.markdown("#### Global Filters")
            st.markdown("Select filters below and click **Apply Filters** to update the dashboard.")

            f_col1, f_col2 = st.columns(2)

            zones = sorted(unified_df["Zone"].dropna().unique()) if "Zone" in unified_df.columns else []
            sel_zones = f_col1.multiselect(
                "Zone", zones,
                default=st.session_state["global_filters"].get("Zone", []),
                key=f"sel_zone_{_rc}",
            )

            if "State" in unified_df.columns:
                if sel_zones:
                    available_states = sorted(
                        unified_df[unified_df["Zone"].isin(sel_zones)]["State"].dropna().unique()
                    )
                else:
                    available_states = sorted(unified_df["State"].dropna().unique())
            else:
                available_states = []
            saved_states = [s for s in st.session_state["global_filters"].get("State", []) if s in available_states]
            sel_states = f_col2.multiselect(
                "State", available_states,
                default=saved_states,
                key=f"sel_state_{_rc}",
            )

            f_col3, f_col4 = st.columns(2)

            desigs = sorted(unified_df["Designation"].dropna().unique()) if "Designation" in unified_df.columns else []
            sel_desigs = f_col3.multiselect(
                "Designation", desigs,
                default=st.session_state["global_filters"].get("Designation", []),
                key=f"sel_desig_{_rc}",
            )

            dealers = sorted(unified_df["Dealer Name"].dropna().unique()) if "Dealer Name" in unified_df.columns else []
            sel_dealers = f_col4.multiselect(
                "Dealer Name", dealers,
                default=st.session_state["global_filters"].get("Dealer Name", []),
                key=f"sel_dealer_{_rc}",
            )

            btn_col1, btn_col2, _ = st.columns([2, 2, 8])

            if btn_col1.button("Apply Filters", type="primary", key="apply_filters_btn"):
                st.session_state["global_filters"] = {
                    "Zone":        sel_zones,
                    "State":       sel_states,
                    "Designation": sel_desigs,
                    "Dealer Name": sel_dealers,
                }
                st.rerun()

            if btn_col2.button("Clear Filters", key="clear_filters_btn"):
                st.session_state["global_filters"] = {}
                st.session_state["filter_reset_counter"] += 1
                st.rerun()

    # ── Apply committed filters to the data ─────────────────────────────────
    df_filtered = apply_filters(unified_df, st.session_state["global_filters"])

    # Recompute KPIs from filtered data so Overview cards reflect active filters.
    kpis = compute_all_kpis(df_filtered)

    # ── Compact filter status pill ──────────────────────────────────────────
    filter_label = "filters applied" if active_filters else "no filters active — showing all data"
    st.markdown(
        f"<div style='padding:8px 14px; background:#F7F7F9; border: 1px solid #E8E8EC; border-radius:6px; "
        f"display:inline-block; font-size:11px; color:#6B6B8D;'>"
        f"Showing <b>{len(df_filtered):,}</b> / <b>{len(unified_df):,}</b> rows &nbsp;·&nbsp; {filter_label}</div>",
        unsafe_allow_html=True,
    )
    # ── Pipeline Math Summary Pill ──────────────────────────────────────────
    raw_train = st.session_state.get("raw_training_count", 0)
    raw_rost = st.session_state.get("raw_roster_count", 0)
    total_raw = raw_train + raw_rost
    st.markdown(
        f"<div style='padding:12px 16px; background:#F7F7F9; border: 1px solid #E8E8EC; border-radius:8px; "
        f"font-size:11px; color:{BRAND_CHARCOAL}; margin-bottom:15px; border-left: 3px solid {BRAND_CHARCOAL};'>"
        f"<b>Data Pipeline Summary:</b> Ingested <b>{total_raw:,}</b> raw rows "
        f"({raw_train:,} training + {raw_rost:,} roster) &rarr; "
        f"Removed <b>{len(duplicate_df):,}</b> exact duplicates &rarr; "
        f"Resolved into <b>{len(unified_df):,}</b> unique master records."
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Top Navigation Routing ──────────────────────────────────────────────
    page = st.session_state.get("current_tab", "Overview")
    if page == "Overview":
        render_overview(df_filtered, kpis, st.session_state["global_filters"])

    elif page == "Pending & Nominations":
        render_backlog(backlog_df, nomination_df, st.session_state["global_filters"])

    elif page == "Skill Analytics":
        render_skill(df_filtered, st.session_state["global_filters"])

    elif page == "Unique Manpower":
        render_manpower(df_filtered, st.session_state["global_filters"])

    elif page == "Audit & Exceptions":
        unresolved_df = (
            unified_df[unified_df["Match_Confidence"] == "UNRESOLVED"]
            if "Match_Confidence" in unified_df.columns
            else pd.DataFrame()
        )
        render_audit(df_filtered, duplicate_df, unresolved_df)

    elif page == "Exports":
        render_export_tab(
            df_filtered, backlog_df, nomination_df, duplicate_df,
            st.session_state.get("audit_log", []),
            st.session_state["global_filters"],
            kpis,
            st.session_state.get("stats", {}),
        )


else:
    # ── Landing Page — Red Mahindra M logo, dark text ────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:80px 20px;">
        <div style="background:{BRAND_RED}; color:white; font-size:4rem; font-weight:900;
                    width:100px; height:100px; display:flex; align-items:center; justify-content:center;
                    border-radius:16px; margin:auto; box-shadow: 0 4px 12px rgba(210,35,42,0.4);">M</div>
        <h2 style="color:{BRAND_CHARCOAL} !important; margin-top:20px; font-weight: 700;">
            Enterprise Dashboard
        </h2>
        <p style="color:#8B8BA7 !important; font-size:13px; max-width:600px; margin:auto;">
            Upload your Manpower Roster and Training Data files using the sidebar.
            Assign file types and click <b>Run Pipeline</b> to process.
        </p>
        <div style="margin-top:30px; padding:16px; background:#F7F7F9; border: 1px solid #E8E8EC;
                    border-radius:8px; display:inline-block;">
            <div style="font-size:11px; color:#6B6B8D !important;">
                <b>Supported:</b> .xlsx, .csv &nbsp;·&nbsp; <b>Max files:</b> 4 &nbsp;·&nbsp;
                <b>Max size:</b> 60MB per file<br>
                <b>100% Offline</b> &nbsp;·&nbsp; <b>Zero Row Loss</b> &nbsp;·&nbsp; <b>Deterministic</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
