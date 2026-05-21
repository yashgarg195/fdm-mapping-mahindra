"""
Sidebar Module — File uploaders and type assignment.
"""
import streamlit as st
from config.constants import BRAND_RED


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
        f"<h2 style='color:{BRAND_RED}; font-weight:800; text-transform:uppercase;'>"
        "MAHINDRA & MAHINDRA TRACTORS</h2>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── File Upload Section ─────────────────────────────────────────────────
    st.sidebar.markdown("### Upload Data Files")
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
            "Run Pipeline",
            type="primary",
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
