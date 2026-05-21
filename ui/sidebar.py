"""
Sidebar Module — File uploaders and type assignment.
"""
import streamlit as st
from config.constants import BRAND_CHARCOAL


def render_sidebar():
    """Render the sidebar with file uploaders and type assignments.
    Returns dict with uploaded_files, file_assignments, and run_pipeline flag.
    """
    result = {
        "uploaded_files": [],
        "file_assignments": {},
        "run_pipeline": False,
    }

    st.sidebar.markdown(
        f"<h2 style='color:{BRAND_CHARCOAL}; font-size:14px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px; margin-top:-16px;'>"
        "MAHINDRA TRACTORS</h2>",
        unsafe_allow_html=True,
    )

    # ── File Upload Section ─────────────────────────────────────────────────
    st.sidebar.markdown("### Upload Data Files")

    roster_files = st.sidebar.file_uploader(
        "Upload Manpower Roster",
        type=["xlsx", "csv"],
        key="file_upload_roster",
        accept_multiple_files=True,
    )
    if roster_files:
        for f in roster_files:
            result["uploaded_files"].append(f)
            result["file_assignments"][f.name] = "Manpower Roster"

    training_files = st.sidebar.file_uploader(
        "Upload Training Data",
        type=["xlsx", "csv"],
        key="file_upload_training",
        accept_multiple_files=True,
    )
    if training_files:
        for f in training_files:
            result["uploaded_files"].append(f)
            result["file_assignments"][f.name] = "Training Data"



    # ── Run Pipeline Button ─────────────────────────────────────────────────
    if len(result["uploaded_files"]) >= 2:
        result["run_pipeline"] = st.sidebar.button(
            "Run Pipeline",
            type="primary",
        )
    elif result["uploaded_files"]:
        st.sidebar.button(
            "Run Pipeline",
            type="primary",
            disabled=True,
            help="Please upload at least 2 files (Roster and Training Data) to run the pipeline."
        )


    return result



def apply_filters(df, filters):
    """Apply filter selections to a DataFrame.

    Rules:
    - An empty ``filters`` dict (or None) → return full DataFrame (no filter).
    - An empty list for a dimension → no filter on that dimension (show all).
    - A non-empty list for a dimension → keep only matching rows.

    Returns filtered DataFrame. Never mutates the original.
    """
    if df is None or df.empty or not filters:
        return df

    filtered = df.copy()
    for col, values in filters.items():
        # Skip dimensions where nothing was selected (empty list = no filter).
        if col in filtered.columns and values:
            filtered = filtered[filtered[col].isin(values)]
    return filtered
