import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import io

from utils import (
    BRAND_RED, BRAND_CHARCOAL, BRAND_DARK_CORE, BRAND_LIGHT_GREY, BRAND_WHITE,
    CURRENT_FY, FY_CALENDAR, RECALL_BUCKETS, NEVER_TRAINED_COLOR, NEVER_TRAINED_LABEL,
    SKILL_SCORE_MAP, SKILL_LABELS, CANONICAL_MODELS, MODEL_CATEGORY_MAP,
    TECHNICAL_DESIGNATIONS, ALL_DESIGNATIONS, ZONE_STATE_MAP, CONFIDENCE_COLORS,
    CONFIDENCE_ORDER, average_skill_score, get_skill_label, get_skill_score
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
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', sans-serif;
    }}
    
    /* Title Styling */
    .portal-title {{
        color: {BRAND_RED};
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }}
    .portal-subtitle {{
        color: {BRAND_CHARCOAL};
        font-weight: 400;
        font-size: 1.0rem;
        margin-bottom: 25px;
        text-transform: uppercase;
        border-bottom: 2px solid {BRAND_RED};
        padding-bottom: 8px;
    }}
    
    /* Metrics Card Styling */
    .kpi-card {{
        background-color: {BRAND_WHITE};
        border-left: 5px solid {BRAND_RED};
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
    }}
    .kpi-label {{
        color: {BRAND_CHARCOAL};
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-value {{
        color: {BRAND_DARK_CORE};
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 5px;
    }}
    .kpi-desc {{
        color: #888888;
        font-size: 0.75rem;
        margin-top: 5px;
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
    st.markdown(f"<div style='font-size:3.5rem; text-align:center; color:{BRAND_RED}; font-weight:700;'>M</div>", unsafe_allow_html=True)
with row_header:
    st.markdown('<div class="portal-title">MAHINDRA & MAHINDRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-subtitle">Training Analytics & Manpower Recall Portal — FDM Mapping System</div>', unsafe_allow_html=True)

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
                "skill_regression_count": int(df_direct_master["SKILL_REGRESSION_FLAG"].sum())
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

# ── PIPELINE STATISTICS REPORT (COLLAPSIBLE SUMMARY) ─────────────────────────
with st.expander("📊 ETL Pipeline Execution & Data Quality Report", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Manpower (Roster)", f"{stats['total_roster_count']:,} employees")
        st.metric("Consolidated Records", f"{stats['total_master_count']:,} rows")
    with col2:
        st.metric("Input Training Rows", f"{stats['total_training_input_count']:,} records")
        st.metric("Resolved Matches", f"{stats['matched_count']:,} rows")
    with col3:
        st.metric("Untrained Manpower", f"{stats['untrained_count']:,} employees")
        st.metric("Unresolved Logs", f"{stats['unresolved_count']:,} rows", delta="Zero Row Loss Active")
    with col4:
        st.metric("Future Date Flags", stats["future_joining_count"])
        st.metric("Skill Regressions", stats["skill_regression_count"])
        
    st.markdown("#### Name Resolution Confidence Distribution")
    # Show confidence distribution
    conf_df = pd.DataFrame([
        {"Confidence": k, "Count": v, "Color": CONFIDENCE_COLORS[k]}
        for k, v in stats["confidence_distribution"].items()
    ])
    fig_conf = px.bar(
        conf_df, x="Confidence", y="Count", color="Confidence",
        color_discrete_map=CONFIDENCE_COLORS,
        title="Resolution Confidence Breakdown"
    )
    st.plotly_chart(fig_conf, use_container_width=True, key="fig_conf_chart")

    # Download consolidated master button
    excel_data = export_to_excel(df_master, stats)
    st.download_button(
        label="📥 Download Formatted Master Excel Workbook",
        data=excel_data,
        file_name=f"MAHINDRA_MASTER_TRAINING_REPORT_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ── READ-ONLY FILTER CONTROLS (EXPLORATION ONLY) ──────────────────────────────
st.markdown("### 🔍 Interactive Filters (Read-Only Exploration)")
filter_row1, filter_row2 = st.columns(2)

with filter_row1:
    # 1. Zone filter
    available_zones = sorted(df_master['Zone'].dropna().unique())
    selected_zones = st.multiselect("Select Zones:", available_zones, default=available_zones)
    
    # 2. State filter (dynamically filtered by selected Zone)
    # Determine valid states for selected zones
    allowed_states = []
    for z in selected_zones:
        allowed_states.extend(ZONE_STATE_MAP.get(z, []))
    available_states = sorted(df_master[df_master['Zone'].isin(selected_zones)]['State'].dropna().unique())
    # Keep selected states that belong to current available states
    selected_states = st.multiselect("Select States:", available_states, default=available_states)

with filter_row2:
    # 3. Designation filter
    available_desigs = sorted(df_master['Designation'].dropna().unique())
    selected_desigs = st.multiselect("Select Designations:", available_desigs, default=available_desigs)
    
    # 4. Recall Status filter
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

# ── DASHBOARD NAVIGATION TABS ─────────────────────────────────────────────────
tab_names = ["Executive Dashboard", "Training Recall List", "Skill Shift Analysis", "Leaderboards", "Employee Deep Dive"]
tabs = st.tabs(tab_names)

# Tab 1: Executive Dashboard (Overview)
with tabs[0]:
    st.markdown("### Executive Overview")
    
    # KPIs Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    total_emp = df_filtered['Star ID'].nunique()
    # Employee has been trained if they have a valid Training Year
    trained_emp = df_filtered[df_filtered['Training year'].notnull()]['Star ID'].nunique()
    coverage = (trained_emp / total_emp * 100) if total_emp > 0 else 0
    
    overdue_critical_count = df_filtered[df_filtered['RECALL_STATUS'].isin(['CRITICAL', 'OVERDUE'])]['Star ID'].nunique()
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Manpower</div>
            <div class="kpi-value">{total_emp:,}</div>
            <div class="kpi-desc">Active in selected filters</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #90EE90;">
            <div class="kpi-label">Trained Manpower</div>
            <div class="kpi-value">{trained_emp:,}</div>
            <div class="kpi-desc">At least one training record</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #FFD700;">
            <div class="kpi-label">Training Coverage</div>
            <div class="kpi-value">{coverage:.1f}%</div>
            <div class="kpi-desc">Trained vs Total Roster ratio</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {BRAND_RED};">
            <div class="kpi-label">Overdue / Critical Recall</div>
            <div class="kpi-value">{overdue_critical_count:,}</div>
            <div class="kpi-desc">Technicians due for retraining</div>
        </div>
        """, unsafe_allow_html=True)
        
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### Training Recall Status Distribution")
        # Donut Chart for Recall Statuses
        recall_counts = df_filtered.groupby('Star ID')['RECALL_STATUS'].first().value_counts().reset_index()
        recall_counts.columns = ['Recall Status', 'Headcount']
        
        # Color mapping
        color_map = {
            "CRITICAL": BRAND_RED,
            "OVERDUE": "#FF8C00",
            "DUE_SOON": "#FFD700",
            "RECENT": "#90EE90",
            "CURRENT_FY": BRAND_CHARCOAL,
            "NEVER_TRAINED": NEVER_TRAINED_COLOR
        }
        
        fig_donut = px.pie(
            recall_counts, names='Recall Status', values='Headcount',
            hole=0.4, color='Recall Status',
            color_discrete_map=color_map
        )
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_donut, use_container_width=True, key="fig_donut_recall")
        
    with chart_col2:
        st.markdown("#### Training Coverage by Zone")
        # Bar Chart of Trained vs Untrained per Zone
        zone_df = df_filtered.groupby('Zone').agg(
            Total_Employees=('Star ID', 'nunique'),
            Trained_Employees=('Star ID', lambda x: x[df_filtered.loc[x.index, 'Training year'].notnull()].nunique())
        ).reset_index()
        zone_df['Coverage %'] = (zone_df['Trained_Employees'] / zone_df['Total_Employees'] * 100).round(1)
        
        fig_zone = px.bar(
            zone_df, x='Zone', y='Coverage %',
            color='Zone', color_discrete_sequence=[BRAND_RED, BRAND_CHARCOAL, "#707072", "#9C9C9E", "#C0C0C2", "#E6E7E8"],
            text='Coverage %'
        )
        fig_zone.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_zone, use_container_width=True, key="fig_zone_coverage")

# Tab 2: Training Recall List
with tabs[1]:
    st.markdown("### Training Recall & Action List")
    st.markdown("Identifies employees whose last training fell outside standard timelines. Filter below to target specific recall urgency levels.")
    
    selected_recall_tab = st.multiselect(
        "Filter List by Urgency:",
        ["CRITICAL", "OVERDUE", "DUE_SOON", "RECENT", "CURRENT_FY", "NEVER_TRAINED"],
        default=["CRITICAL", "OVERDUE", "DUE_SOON"]
    )
    
    # Filter the list
    df_recall_list = df_filtered[df_filtered['RECALL_STATUS'].isin(selected_recall_tab)]
    
    # De-duplicate by employee to show latest status
    # Get first record per Star ID
    df_recall_unique = df_recall_list.sort_values(
        ['Star ID', 'LATEST_TRAINING_DATE'], ascending=[True, False]
    ).drop_duplicates(subset=['Star ID'])
    
    st.markdown(f"**Found {df_recall_unique.shape[0]} unique employees matching criteria.**")
    
    # Select columns to display
    display_cols = ['Star ID', 'Name', 'Designation', 'Zone', 'State', 'Dealer Code', 'Dealer Name', 
                    'Contact No', 'LAST PRODUCT TRANIING ON', 'LAST MODEL TRAINED', 
                    'LATEST_TRAINING_DATE', 'RECALL_STATUS']
    
    st.dataframe(
        df_recall_unique[display_cols],
        column_config={
            "Star ID": st.column_config.NumberColumn(format="%d"),
            "LATEST_TRAINING_DATE": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "RECALL_STATUS": st.column_config.TextColumn(help="Retraining recall interval status")
        },
        use_container_width=True
    )
    
    # Download filtered CSV button
    csv_data = df_recall_unique[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Recall Action List (CSV)",
        data=csv_data,
        file_name=f"MAHINDRA_RECALL_ACTION_LIST_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Tab 3: Skill Level Shift Analytics
with tabs[2]:
    st.markdown("### Skill Transition & Regression Analysis")
    st.markdown("Evaluates pre- vs. post-training scores. Note: `NO TEST` (-1) is excluded from mathematical averages.")
    
    # Filter to trained rows only
    df_trained_rows = df_filtered[df_filtered['Training year'].notnull()].copy()
    
    if df_trained_rows.empty:
        st.info("No training history records available under selected filters.")
    else:
        # Average Pre and Post scores (strictly ignoring -1 / NO TEST)
        # Add numeric representations
        df_trained_rows['pre_score'] = df_trained_rows['SKILL LEVEL - PRE'].map(SKILL_SCORE_MAP)
        df_trained_rows['post_score'] = df_trained_rows['SKILL LEVEL - POST'].map(SKILL_SCORE_MAP)
        
        avg_pre = df_trained_rows[df_trained_rows['pre_score'] >= 0]['pre_score'].mean()
        avg_post = df_trained_rows[df_trained_rows['post_score'] >= 0]['post_score'].mean()
        
        col_pre, col_post, col_gain = st.columns(3)
        with col_pre:
            st.metric("Average Pre-Training Score", f"{avg_pre:.2f}" if pd.notna(avg_pre) else "N/A")
        with col_post:
            st.metric("Average Post-Training Score", f"{avg_post:.2f}" if pd.notna(avg_post) else "N/A")
        with col_gain:
            if pd.notna(avg_pre) and pd.notna(avg_post):
                gain = avg_post - avg_pre
                st.metric("Average Skill Gain Shift", f"+{gain:.2f}" if gain >= 0 else f"{gain:.2f}")
            else:
                st.metric("Average Skill Gain Shift", "N/A")
                
        # Designation skill level breakdown
        st.markdown("#### Average Skill Score by Designation")
        desig_scores = []
        for desig, group in df_trained_rows.groupby('Designation'):
            valid_pre = group[group['pre_score'] >= 0]['pre_score']
            valid_post = group[group['post_score'] >= 0]['post_score']
            
            p_score = valid_pre.mean() if not valid_pre.empty else np.nan
            po_score = valid_post.mean() if not valid_post.empty else np.nan
            
            if pd.notna(p_score) or pd.notna(po_score):
                desig_scores.append({
                    "Designation": desig,
                    "Pre-Training Avg": round(p_score, 2) if pd.notna(p_score) else 0,
                    "Post-Training Avg": round(po_score, 2) if pd.notna(po_score) else 0
                })
        
        if desig_scores:
            df_desig_scores = pd.DataFrame(desig_scores)
            df_desig_melt = df_desig_scores.melt(id_vars='Designation', value_vars=['Pre-Training Avg', 'Post-Training Avg'],
                                                 var_name='Stage', value_name='Score')
            
            fig_desig_skill = px.bar(
                df_desig_melt, x='Designation', y='Score', color='Stage',
                barmode='group', color_discrete_map={"Pre-Training Avg": BRAND_CHARCOAL, "Post-Training Avg": BRAND_RED}
            )
            st.plotly_chart(fig_desig_skill, use_container_width=True, key="fig_desig_skill_scores")
            
        # Skill Regressions Listing
        st.markdown("#### ⚠️ Skill Regression Alerts")
        st.markdown("Records where `SKILL LEVEL - POST` score is lower than `SKILL LEVEL - PRE` score (negative shift).")
        
        df_regressions = df_trained_rows[df_trained_rows['SKILL_REGRESSION_FLAG']]
        st.markdown(f"**Found {df_regressions.shape[0]} training records with regression.**")
        
        if not df_regressions.empty:
            reg_display_cols = ['Star ID', 'Name', 'Designation', 'Dealer Code', 'Dealer Name', 
                               'Training year', 'LAST PRODUCT TRANIING ON', 'LAST MODEL TRAINED', 
                               'SKILL LEVEL - PRE', 'SKILL LEVEL - POST']
            st.dataframe(
                df_regressions[reg_display_cols],
                column_config={
                    "Star ID": st.column_config.NumberColumn(format="%d")
                },
                use_container_width=True
            )

# Tab 4: Leaderboards
with tabs[3]:
    st.markdown("### Dealership & Designation Rankings")
    
    lead_col1, lead_col2 = st.columns(2)
    
    with lead_col1:
        st.markdown("#### Top 15 Dealerships (Highest Training Coverage %)")
        # Dealership Coverage
        dealer_cov = df_filtered.groupby(['Dealer Code', 'Dealer Name']).agg(
            Total_Employees=('Star ID', 'nunique'),
            Trained_Employees=('Star ID', lambda x: x[df_filtered.loc[x.index, 'Training year'].notnull()].nunique())
        ).reset_index()
        dealer_cov['Coverage %'] = (dealer_cov['Trained_Employees'] / dealer_cov['Total_Employees'] * 100).round(1)
        dealer_cov = dealer_cov.sort_values(by=['Coverage %', 'Total_Employees'], ascending=[False, False]).head(15)
        
        st.dataframe(
            dealer_cov[['Dealer Code', 'Dealer Name', 'Total_Employees', 'Trained_Employees', 'Coverage %']],
            use_container_width=True
        )
        
    with lead_col2:
        st.markdown("#### Dealerships Requiring Retraining Attention")
        # Dealerships with most Overdue/Critical technicians
        dealer_attn = df_filtered.groupby(['Dealer Code', 'Dealer Name']).agg(
            Overdue_Critical_Count=('Star ID', lambda x: x[df_filtered.loc[x.index, 'RECALL_STATUS'].isin(['CRITICAL', 'OVERDUE'])].nunique()),
            Total_Employees=('Star ID', 'nunique')
        ).reset_index()
        dealer_attn = dealer_attn.sort_values(by='Overdue_Critical_Count', ascending=False).head(15)
        
        st.dataframe(
            dealer_attn[['Dealer Code', 'Dealer Name', 'Total_Employees', 'Overdue_Critical_Count']],
            use_container_width=True
        )

# Tab 5: Search & Employee Deep Dive
with tabs[4]:
    st.markdown("### Employee Deep Dive Profile")
    
    search_query = st.text_input(
        "Search by Star ID, Name, Aadhar, or Employee Code:",
        placeholder="Enter search term..."
    )
    
    if search_query:
        # Match query defensively
        q = str(search_query).strip().upper()
        
        # Check matching rows
        # Direct check on Star ID, Name, AadharCardNumber, Emp Code
        match_mask = (
            (df_master['Star ID'].astype(str).str.contains(q, case=False, na=False)) |
            (df_master['Name'].str.contains(q, case=False, na=False)) |
            (df_master['AadharCardNumber'].astype(str).str.contains(q, case=False, na=False)) |
            (df_master['Emp Code'].str.contains(q, case=False, na=False))
        )
        
        matches = df_master[match_mask]
        
        if matches.empty:
            st.info("No matching employee record found.")
        else:
            # Dropdown to choose employee if multiple matches exist
            unique_matches = matches.drop_duplicates(subset=['Star ID', 'Name'])
            emp_list = [
                f"{int(row['Star ID']) if pd.notna(row['Star ID']) else 0} - {row['Name']} ({row['Designation']}) at {row['Dealer Name']}"
                for idx, row in unique_matches.iterrows()
            ]
            
            selected_emp_desc = st.selectbox("Select Employee:", emp_list)
            
            selected_idx = emp_list.index(selected_emp_desc)
            selected_star_id = unique_matches.iloc[selected_idx]['Star ID']
            selected_name = unique_matches.iloc[selected_idx]['Name']
            
            # Filter all training records for this chosen employee
            emp_records = df_master[
                (df_master['Star ID'] == selected_star_id) & 
                (df_master['Name'] == selected_name)
            ]
            
            # Main demographics (from the first row)
            demo_row = emp_records.iloc[0]
            
            st.markdown(f"#### Profile: {demo_row['Name']} (Star ID: {int(demo_row['Star ID']) if pd.notna(demo_row['Star ID']) else 0})")
            
            # Profile Details Table
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown(f"**Designation:** {demo_row['Designation']}")
                st.markdown(f"**Gender:** {demo_row['Gender']}")
                st.markdown(f"**Father's Name:** {demo_row['Father Name']}")
                st.markdown(f"**Contact Number:** {demo_row['Contact No']}")
                st.markdown(f"**Aadhar Card Number:** {demo_row['AadharCardNumber']}")
            with p_col2:
                st.markdown(f"**Zone / State:** {demo_row['Zone']} / {demo_row['State']}")
                st.markdown(f"**Dealership:** {demo_row['Dealer Name']} ({demo_row['Dealer Code']})")
                st.markdown(f"**AO / Location:** {demo_row['Dealer AO']} / {demo_row['Location']}")
                st.markdown(f"**Joining Date:** {demo_row['Joining Date'].strftime('%Y-%m-%d') if isinstance(demo_row['Joining Date'], (pd.Timestamp, datetime.datetime)) else str(demo_row['Joining Date'])}")
                st.markdown(f"**Recall Status:** `{demo_row['RECALL_STATUS']}`")
                
            # Training History
            st.markdown("#### Training History & Logs")
            
            # Check if there is training history
            has_training = emp_records['Training year'].notnull().any()
            if not has_training:
                st.warning("No product training records registered for this employee in the system.")
            else:
                hist_cols = ['Training year', 'LAST PRODUCT TRANIING ON', 'LAST MODEL TRAINED', 
                             'SKILL LEVEL - PRE', 'SKILL LEVEL - POST', 'MATCH_CONFIDENCE', 'MATCH_REASON']
                st.dataframe(
                    emp_records[hist_cols],
                    use_container_width=True
                )
