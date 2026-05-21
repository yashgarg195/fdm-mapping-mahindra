"""
Sidebar Module — File uploaders and type assignment.
"""
import streamlit as st
from config.constants import BRAND_RED, BRAND_CHARCOAL


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
        f"<h2 style='color:{BRAND_CHARCOAL}; font-size:14px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:0;'>"
        "MAHINDRA TRACTORS</h2>",
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

    # ── Help & Guide ────────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    with st.sidebar.expander("Help & Guide", expanded=False):
        st.markdown("""
**How to use this dashboard:**

1. **Upload Files** — Use the file uploaders above to upload your Manpower Roster and Training Data Excel files.
2. **Assign Types** — Set the correct type for each file (Manpower Roster or Training Data).
3. **Run Pipeline** — Click **Run Pipeline** to process the data through the 7-pass identity resolution engine.
4. **Apply Filters** — Use the Global Filters panel on the main screen to narrow down by Zone, State, Designation, or Dealer.
5. **Explore Tabs** — Navigate across tabs to view analytics.
6. **Export** — Go to the **Exports** tab to download individual or combined reports.

---

**Tabs at a Glance:**

| Tab | Purpose |
|-----|---------|
| Overview | National KPIs + All-India graphical dashboard |
| Pending & Nominations | Backlog priority list |
| Skill Analytics | Pre/post training skill scores (1–10 scale) |
| Unique Manpower | State/zone headcount breakdown |
| Audit & Exceptions | Duplicate log, unresolved queue, data quality |
| Exports | Download all reports |

---

**Confidence Tiers:**

- 🟢 **HIGH** — Exact ID match with matching name
- 🟡 **MEDIUM** — Strong match with minor name variation
- 🟠 **LOW** — Weak match — requires supervisor review
- 🟣 **POSSIBLE** — Similar name at same dealership (Possible Match)
- ⬛ **UNRESOLVED** — Could not be matched — excluded from KPIs

---

**Skill Scale (1–10):**

| Score | Level | Meaning |
|-------|-------|---------|
| 2 | Beginner | Untested / No training |
| 4 | Basic | Completed L1 |
| 6 | Intermediate | Completed L2 |
| 8 | Advanced | Completed L3 |
| 10 | Expert | Completed L4 |
""")

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
