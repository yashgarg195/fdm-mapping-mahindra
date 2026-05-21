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
      --foreground: #030213;
      --primary: {BRAND_RED};
      --muted: #ececf0;
      --muted-foreground: #717182;
      --accent: #e9ebef;
      --destructive: {BRAND_RED};
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
    /* ── Tabs ──────────────────────────────────────────── */
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
        color: var(--foreground) !important;
        border-bottom: 2px solid var(--primary);
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
        background-color: var(--primary) !important;
        color: #ffffff !important;
        font-weight: 600;
        border: none;
        border-radius: var(--radius);
        padding: 10px 20px;
    }}
    .stButton>button[kind="primary"]:hover,
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover {{
        background-color: #b8142f !important;
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
# Applied filters (committed via Apply Filters button). Empty dict = no filter = all rows shown.
if "global_filters" not in st.session_state:
    st.session_state["global_filters"] = {}
# Counter used to force-reset multiselect widgets when Clear Filters is clicked.
if "filter_reset_counter" not in st.session_state:
    st.session_state["filter_reset_counter"] = 0

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

    # ── Main Area Filters ───────────────────────────────────────────────────
    st.markdown("### Global Filters")

    # Use the reset counter as part of the widget key so that changing it
    # forces Streamlit to recreate the widgets with empty defaults.
    _rc = st.session_state["filter_reset_counter"]

    with st.expander("Filter Options", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        zones = sorted(unified_df["Zone"].dropna().unique()) if "Zone" in unified_df.columns else []
        # Restore previously applied filter selections (empty list = no filter selected).
        sel_zones = f_col1.multiselect(
            "Zone", zones,
            default=st.session_state["global_filters"].get("Zone", []),
            key=f"sel_zone_{_rc}",
        )

        # States cascade from selected zones (or show all if no zone selected).
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

        if btn_col1.button("Apply Filters", type="primary"):
            # Commit current widget selections as the active filter.
            # An empty list for any dimension means "no filter on that dimension".
            st.session_state["global_filters"] = {
                "Zone":        sel_zones,
                "State":       sel_states,
                "Designation": sel_desigs,
                "Dealer Name": sel_dealers,
            }
            st.rerun()

        if btn_col2.button("Clear Filters"):
            # Wipe applied filters and increment the reset counter so the
            # multiselect widgets are recreated with empty defaults.
            st.session_state["global_filters"] = {}
            st.session_state["filter_reset_counter"] += 1
            st.rerun()

    # ── Apply committed filters to the data ─────────────────────────────────
    # apply_filters already handles empty dicts/lists (returns full df).
    df_filtered = apply_filters(unified_df, st.session_state["global_filters"])

    # Recompute KPIs from filtered data so Overview cards reflect active filters.
    kpis = compute_all_kpis(df_filtered)

    # ── Top Action Bar (filter status only — downloads moved to Exports tab) ───
    st.markdown("---")
    active_filters = {k: v for k, v in st.session_state["global_filters"].items() if v}
    filter_label = "filters applied" if active_filters else "no filters active — showing all data"
    st.markdown(
        f"<div style='padding:8px 14px; background:var(--muted); border-radius:6px; "
        f"display:inline-block; font-size:0.85rem; color:var(--muted-foreground);'>"
        f"Showing <b>{len(df_filtered):,}</b> / <b>{len(unified_df):,}</b> rows &nbsp;·&nbsp; {filter_label}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    # ── Pipeline Math Summary Pill ──────────────────────────────────────────
    raw_train = st.session_state.get("raw_training_count", 0)
    raw_rost = st.session_state.get("raw_roster_count", 0)
    total_raw = raw_train + raw_rost
    st.markdown(
        f"<div style='padding:12px 16px; background:{BRAND_LIGHT_GREY}; border-radius:8px; "
        f"font-size:0.9rem; color:{BRAND_CHARCOAL}; margin-bottom:15px; border-left: 4px solid {BRAND_RED};'>"
        f"<b>Data Pipeline Summary:</b> Ingested <b>{total_raw:,}</b> raw rows "
        f"({raw_train:,} training + {raw_rost:,} roster) &rarr; "
        f"Removed <b>{len(duplicate_df):,}</b> exact duplicates &rarr; "
        f"Resolved into <b>{len(unified_df):,}</b> unique master records."
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Tab Routing ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Pending & Nominations",
        "Skill Analytics",
        "Unique Manpower",
        "Audit & Exceptions",
        "Exports",
    ])

    with tab1:
        render_overview(df_filtered, kpis, st.session_state["global_filters"])

    with tab2:
        render_backlog(backlog_df, nomination_df, st.session_state["global_filters"])

    with tab3:
        render_skill(df_filtered, st.session_state["global_filters"])

    with tab4:
        render_manpower(df_filtered, st.session_state["global_filters"])

    with tab5:
        unresolved_df = (
            unified_df[unified_df["Match_Confidence"] == "UNRESOLVED"]
            if "Match_Confidence" in unified_df.columns
            else pd.DataFrame()
        )
        render_audit(df_filtered, duplicate_df, unresolved_df)

    with tab6:
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
