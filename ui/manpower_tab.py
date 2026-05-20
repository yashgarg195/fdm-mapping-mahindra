"""
Manpower Tab — State/zone manpower tables, unique headcount, unresolved count.
"""
import streamlit as st
import plotly.express as px
from config.constants import BRAND_RED, BRAND_CHARCOAL
from utils.formatting_utils import style_kpi_card, format_count
from analytics.manpower import state_manpower_table, zone_manpower_table, unique_manpower_count


def render_manpower(unified_df, filters):
    """Render the Unique Manpower tab."""
    if unified_df is None or unified_df.empty:
        st.info("No data available for manpower analysis.")
        return

    # ── In-Tab Filters ──────────────────────────────────────────────────────
    st.markdown("#### Manpower Filters")
    col1, col2, col3 = st.columns(3)
    with col1:
        zones = ["All"] + sorted([str(z) for z in unified_df.get("Zone", pd.Series()).unique() if pd.notna(z) and str(z).strip()])
        sel_zone = st.selectbox("Location (Zone)", zones, key="mp_zone")
    with col2:
        roles = ["All"] + sorted([str(r) for r in unified_df.get("Designation", pd.Series()).unique() if pd.notna(r) and str(r).strip()])
        sel_role = st.selectbox("Role (Designation)", roles, key="mp_role")
    with col3:
        if "Training_Status" in unified_df.columns:
            statuses = ["All"] + sorted([str(s) for s in unified_df["Training_Status"].unique() if pd.notna(s) and str(s).strip()])
            sel_status = st.selectbox("Training Status", statuses, key="mp_status")
        else:
            sel_status = "All"
            st.selectbox("Training Status", ["All"], key="mp_status", disabled=True)

    # Apply in-tab filters
    filtered_df = unified_df.copy()
    if sel_zone != "All":
        filtered_df = filtered_df[filtered_df["Zone"] == sel_zone]
    if sel_role != "All":
        filtered_df = filtered_df[filtered_df["Designation"] == sel_role]
    if sel_status != "All" and "Training_Status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Training_Status"] == sel_status]

    if filtered_df.empty:
        st.warning("No records match the selected manpower filters.")
        return

    # ── KPI Cards ───────────────────────────────────────────────────────────
    total = unique_manpower_count(filtered_df)
    unresolved = (filtered_df.get("Match_Confidence", "") == "UNRESOLVED").sum() if "Match_Confidence" in filtered_df.columns else 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(style_kpi_card("UNIQUE MANPOWER", format_count(total), "VERIFIED EMPLOYEES", BRAND_RED), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card("UNRESOLVED IDENTITIES", format_count(unresolved), "EXCLUDED FROM COUNTS", BRAND_CHARCOAL), unsafe_allow_html=True)

    # ── State Table ─────────────────────────────────────────────────────────
    st.markdown("#### State-wise Manpower Breakdown")
    state_df = state_manpower_table(filtered_df)
    if not state_df.empty:
        st.dataframe(state_df.sort_values("Total_Employees", ascending=False), height=400)
    else:
        st.info("No state-level data available.")

    # ── Zone Chart ──────────────────────────────────────────────────────────
    st.markdown("#### Zone Manpower Distribution")
    zone_df = zone_manpower_table(filtered_df)
    if not zone_df.empty:
        fig = px.bar(
            zone_df, x="Zone", y=["Trained_Count", "Untrained_Count"],
            barmode="stack",
            color_discrete_map={"Trained_Count": BRAND_RED, "Untrained_Count": "#E6E7E8"},
        )
        fig.update_layout(plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20), yaxis_title="Employees", legend_title="")
        st.plotly_chart(fig, key="zone_manpower_chart")
    else:
        st.info("No zone-level data available.")
