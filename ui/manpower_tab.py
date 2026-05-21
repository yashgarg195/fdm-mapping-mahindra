"""
Manpower Tab — State/zone manpower tables, unique headcount, unresolved count.
"""
import streamlit as st
import plotly.express as px
from config.constants import BRAND_RED, BRAND_CHARCOAL
from utils.formatting_utils import style_kpi_card, format_count
from analytics.manpower import state_manpower_table, zone_manpower_table, unique_manpower_count


def render_manpower(unified_df, filters):
    """Render the Unique Manpower tab.

    ``unified_df`` is already filtered by the global filters in app.py —
    no additional in-tab filtering is needed.
    """
    if unified_df is None or unified_df.empty:
        st.info("No data available for manpower analysis.")
        return

    # ── KPI Cards ───────────────────────────────────────────────────────────
    total = unique_manpower_count(unified_df)
    unresolved = (
        (unified_df["Match_Confidence"] == "UNRESOLVED").sum()
        if "Match_Confidence" in unified_df.columns else 0
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(style_kpi_card("UNIQUE MANPOWER", format_count(total), "VERIFIED EMPLOYEES", BRAND_RED), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card("UNRESOLVED IDENTITIES", format_count(unresolved), "EXCLUDED FROM COUNTS", BRAND_CHARCOAL), unsafe_allow_html=True)

    # ── State Table ─────────────────────────────────────────────────────────
    st.markdown("#### State-wise Manpower Breakdown")
    state_df = state_manpower_table(unified_df)
    if not state_df.empty:
        st.dataframe(state_df.sort_values("Total_Employees", ascending=False), height=400)
    else:
        st.info("No state-level data available.")

    # ── Zone Chart ──────────────────────────────────────────────────────────
    st.markdown("#### Zone Manpower Distribution")
    zone_df = zone_manpower_table(unified_df)
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

