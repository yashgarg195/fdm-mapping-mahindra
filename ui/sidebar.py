"""
Sidebar Module — File uploaders, type assignment, and filter controls.
"""
import streamlit as st
from config.constants import BRAND_RED, ZONE_STATE_MAP


def render_sidebar():
    """Render the sidebar with file uploaders, type assignments, and filters.
    Returns dict with uploaded_files, file_assignments, filters, and run_pipeline flag.
    """
    result = {
        "uploaded_files": [],
        "file_assignments": {},
        "filters": {},
        "run_pipeline": False,
    }

    st.sidebar.markdown(
        f"<h2 style='color:{BRAND_RED}; font-weight:800; text-transform:uppercase;'>"
        "MAHINDRA & MAHINDRA TRACTORS</h2>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── File Upload Section ─────────────────────────────────────────────────
    st.sidebar.markdown("### 📁 Upload Data Files")
    file_types = ["Manpower Roster", "Training Data", "Additional Training Data", "Other"]

    for i in range(1, 5):
        label = f"File {i}" if i > 2 else ("Manpower Roster" if i == 1 else "Training Data")
        uploaded = st.sidebar.file_uploader(
            f"Upload {label}",
            type=["xlsx", "csv"],
            key=f"file_upload_{i}",
        )
        if uploaded:
            result["uploaded_files"].append(uploaded)
            assigned_type = st.sidebar.selectbox(
                f"Assign type for: {uploaded.name}",
                file_types,
                index=0 if i == 1 else (1 if i == 2 else 2),
                key=f"file_type_{i}",
            )
            result["file_assignments"][uploaded.name] = assigned_type

    st.sidebar.markdown("---")

    # ── Run Pipeline Button ─────────────────────────────────────────────────
    if result["uploaded_files"]:
        result["run_pipeline"] = st.sidebar.button(
            "🔴 Run Pipeline",
            type="primary",
        )

    # ── Filter Controls (only shown after pipeline runs) ────────────────────
    if st.session_state.get("pipeline_complete", False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Filters")

        unified_df = st.session_state.get("unified_df")
        if unified_df is not None and not unified_df.empty:
            filters = {}

            # Zone filter
            if "Zone" in unified_df.columns:
                zones = sorted(unified_df["Zone"].dropna().unique())
                filters["Zone"] = st.sidebar.multiselect("Zone", zones, default=zones, key="filter_zone")

            # State filter (filtered by zone)
            if "State" in unified_df.columns:
                if filters.get("Zone"):
                    available_states = sorted(
                        unified_df[unified_df["Zone"].isin(filters["Zone"])]["State"].dropna().unique()
                    )
                else:
                    available_states = sorted(unified_df["State"].dropna().unique())
                filters["State"] = st.sidebar.multiselect("State", available_states, default=available_states, key="filter_state")

            # Designation filter
            if "Designation" in unified_df.columns:
                desigs = sorted(unified_df["Designation"].dropna().unique())
                filters["Designation"] = st.sidebar.multiselect("Designation", desigs, default=desigs, key="filter_desig")

            # Dealer filter
            if "Dealer Name" in unified_df.columns:
                dealers = sorted(unified_df["Dealer Name"].dropna().unique())
                filters["Dealer Name"] = st.sidebar.multiselect("Dealer Name", dealers, default=[], key="filter_dealer")

            # Training year filter
            if "Training year" in unified_df.columns:
                fys = sorted(unified_df["Training year"].dropna().unique())
                filters["Training year"] = st.sidebar.multiselect("Training Year", fys, default=fys, key="filter_fy")

            # Skill level filter
            if "SKILL LEVEL - POST" in unified_df.columns:
                skills = sorted(unified_df["SKILL LEVEL - POST"].dropna().unique())
                filters["SKILL LEVEL - POST"] = st.sidebar.multiselect("Skill Level (Post)", skills, default=skills, key="filter_skill")

            result["filters"] = filters

    return result


def apply_filters(df, filters):
    """Apply sidebar filter selections to a DataFrame.
    Returns filtered DataFrame. Never mutates the original.
    """
    if df is None or df.empty or not filters:
        return df

    filtered = df.copy()
    for col, values in filters.items():
        if col in filtered.columns and values:
            filtered = filtered[filtered[col].isin(values)]
    return filtered
