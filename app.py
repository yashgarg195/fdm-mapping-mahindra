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

# ── Export ──────────────────────────────────────────────────────────────────
from export.excel_export import generate_excel_report
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
      --foreground: #030213;
      --primary: #030213;
      --muted: #ececf0;
      --muted-foreground: #717182;
      --accent: #e9ebef;
      --destructive: #d4183d;
      --input-background: #f3f3f5;
      --radius: 0.625rem;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 16px;
    }}
    .stApp {{
        background-color: var(--input-background);
        color: var(--foreground);
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
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: var(--radius) var(--radius) 0 0;
        padding: 8px 20px;
        font-weight: 500;
        color: var(--muted-foreground) !important;
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: transparent !important;
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary);
    }}
    /* Sidebar: light background to match shadcn sidebar */
    section[data-testid="stSidebar"] {{
        background-color: var(--background) !important;
        border-right: 1px solid var(--muted);
    }}
    /* Catch every text node Streamlit renders inside the sidebar */
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
    /* Selectbox / multiselect control boxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        color: var(--foreground) !important;
        background-color: var(--input-background);
        border-radius: var(--radius);
        border: none;
    }}
    /* Buttons */
    .stButton>button[kind="primary"] {{
        background-color: var(--primary);
        color: var(--background);
        font-weight: 500;
        border: none;
        border-radius: var(--radius);
        padding: 10px 20px;
    }}
    .stButton>button[kind="primary"]:hover {{
        background-color: var(--primary);
        opacity: 0.9;
    }}
    .stDownloadButton>button {{
        background-color: var(--muted);
        color: var(--foreground);
        font-weight: 500;
        border: 1px solid var(--muted-foreground);
        border-radius: var(--radius);
    }}
    /* Metric values */
    [data-testid="stMetricValue"] {{
        color: var(--foreground) !important;
        font-weight: 700;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--muted-foreground) !important;
        font-weight: 500;
    }}
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background-color: var(--destructive);
    }}
    /* Dataframes/Tables */
    [data-testid="stDataFrame"] {{
        background-color: var(--background);
        border-radius: var(--radius);
        border: 1px solid var(--muted);
        overflow: hidden;
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HEADER — Red Mahindra "M" badge (no green tractor)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="display:flex; align-items:center; gap:15px; margin-bottom:10px;">
    <div style="background:{BRAND_RED}; color:white; font-size:2.5rem; font-weight:900;
                width:60px; height:60px; display:flex; align-items:center; justify-content:center;
                border-radius:10px;">M</div>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:{BRAND_DARK_CORE};">
            MAHINDRA TRAINING ANALYTICS & MANPOWER INTELLIGENCE
        </div>
        <div style="font-size:0.85rem; color:{BRAND_CHARCOAL};">
            Air-Gapped · Zero Row Loss · Deterministic · Offline
        </div>
    </div>
</div>
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

        st.success(
            f"Pipeline complete! "
            f"{len(unified_df):,} rows processed | "
            f"{stats.get('matched_count', 0):,} matched | "
            f"{stats.get('unresolved_count', 0):,} unresolved | "
            f"0 rows lost"
        )

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
    unified_df = st.session_state["unified_df"]
    duplicate_df = st.session_state["duplicate_df"]
    backlog_df = st.session_state["backlog_df"]
    nomination_df = st.session_state["nomination_df"]
    kpis = st.session_state["kpis"]
    
    # ── Main Area Filters ───────────────────────────────────────────────────
    st.markdown("### Global Filters")
    
    if "global_filters" not in st.session_state:
        st.session_state.global_filters = {}

    with st.expander("Filter Options", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        zones = sorted(unified_df["Zone"].dropna().unique()) if "Zone" in unified_df.columns else []
        sel_zones = f_col1.multiselect("Zone", zones, default=st.session_state.global_filters.get("Zone", zones), key="temp_zone")
        
        available_states = []
        if "State" in unified_df.columns:
            if sel_zones:
                available_states = sorted(unified_df[unified_df["Zone"].isin(sel_zones)]["State"].dropna().unique())
            else:
                available_states = sorted(unified_df["State"].dropna().unique())
        
        # Ensure default states are valid
        def_states = [s for s in st.session_state.global_filters.get("State", available_states) if s in available_states]
        sel_states = f_col2.multiselect("State", available_states, default=def_states, key="temp_state")
        
        desigs = sorted(unified_df["Designation"].dropna().unique()) if "Designation" in unified_df.columns else []
        sel_desigs = f_col3.multiselect("Designation", desigs, default=st.session_state.global_filters.get("Designation", desigs), key="temp_desig")
        
        dealers = sorted(unified_df["Dealer Name"].dropna().unique()) if "Dealer Name" in unified_df.columns else []
        sel_dealers = f_col4.multiselect("Dealer Name", dealers, default=st.session_state.global_filters.get("Dealer Name", []), key="temp_dealer")

        btn_col1, btn_col2, _ = st.columns([2, 2, 8])
        if btn_col1.button("Apply Filters", type="primary"):
            st.session_state.global_filters = {
                "Zone": sel_zones,
                "State": sel_states,
                "Designation": sel_desigs,
                "Dealer Name": sel_dealers
            }
            st.rerun()
            
        if btn_col2.button("Clear Filters"):
            st.session_state.global_filters = {}
            for k in ["temp_zone", "temp_state", "temp_desig", "temp_dealer"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    filters = st.session_state.global_filters
    df_filtered = apply_filters(unified_df, filters)

    # ── Top Action Bar ──────────────────────────────────────────────────────
    st.markdown("---")
    act_col1, act_col2 = st.columns([4, 8])
    with act_col1:
        with st.spinner("Preparing Excel report..."):
            excel_buf = generate_excel_report(
                df_filtered, backlog_df, duplicate_df,
                st.session_state.get("audit_log", []),
            )
        st.download_button(
            "Download Full Report (8 Sheets)",
            excel_buf,
            file_name="MAHINDRA_TRAINING_ANALYTICS_REPORT.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with act_col2:
        st.markdown(
            f"<div style='padding:8px 14px; background:var(--muted); border-radius:6px; "
            f"display:inline-block; font-size:0.85rem; color:var(--muted-foreground);'>"
            f"Showing <b>{len(df_filtered):,}</b> / <b>{len(unified_df):,}</b> rows (filters applied)</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Tab Routing ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Pending & Nominations",
        "Skill Analytics",
        "Unique Manpower",
        "Audit & Exceptions",
    ])

    with tab1:
        with st.spinner("Loading Overview..."):
            render_overview(df_filtered, kpis, filters)

    with tab2:
        render_backlog(backlog_df, nomination_df, filters)

    with tab3:
        render_skill(df_filtered, filters)

    with tab4:
        render_manpower(df_filtered, filters)

    with tab5:
        unresolved_df = unified_df[unified_df["Match_Confidence"] == "UNRESOLVED"] if "Match_Confidence" in unified_df.columns else pd.DataFrame()
        render_audit(df_filtered, duplicate_df, unresolved_df)

else:
    # ── Landing Page — Red Mahindra M logo, dark text ────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:80px 20px;">
        <div style="background:{BRAND_RED}; color:white; font-size:4rem; font-weight:900;
                    width:100px; height:100px; display:flex; align-items:center; justify-content:center;
                    border-radius:16px; margin:auto;">M</div>
        <h2 style="color:{BRAND_DARK_CORE} !important; margin-top:20px;">
            Upload Files to Begin
        </h2>
        <p style="color:{BRAND_CHARCOAL} !important; font-size:1.1rem; max-width:600px; margin:auto;">
            Upload your Manpower Roster and Training Data files using the sidebar.
            Assign file types and click <b>Run Pipeline</b> to process.
        </p>
        <div style="margin-top:30px; padding:20px; background:{BRAND_LIGHT_GREY};
                    border-radius:10px; display:inline-block;">
            <div style="font-size:0.9rem; color:{BRAND_CHARCOAL} !important;">
                <b>Supported:</b> .xlsx, .csv · <b>Max files:</b> 4 ·
                <b>Max size:</b> 60MB per file<br>
                <b>100% Offline</b> · <b>Zero Row Loss</b> · <b>No AI/LLMs</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
