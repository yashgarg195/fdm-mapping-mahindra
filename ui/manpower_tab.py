"""
Manpower Tab — State/zone manpower tables, unique headcount, unresolved count.
"""
import io
import streamlit as st
import plotly.express as px
from config.constants import BRAND_CHARCOAL
from utils.formatting_utils import style_kpi_card, format_count, style_section_header
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
        st.markdown(style_kpi_card("UNIQUE MANPOWER", format_count(total), "VERIFIED EMPLOYEES", "#1A1A2E"), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card("UNRESOLVED IDENTITIES", format_count(unresolved), "EXCLUDED FROM COUNTS", "#78909C"), unsafe_allow_html=True)

    # ── State Table ─────────────────────────────────────────────────────────
    st.markdown(style_section_header("State-wise Manpower Breakdown", ""), unsafe_allow_html=True)
    state_df = state_manpower_table(unified_df)
    if not state_df.empty:
        state_sorted = state_df.sort_values("Total_Employees", ascending=False)
        s_label, s_btn = st.columns([6, 2])
        with s_label:
            st.markdown(f"**{len(state_sorted)} states**")
        with s_btn:
            _buf = io.BytesIO()
            state_sorted.to_excel(_buf, index=False, engine="xlsxwriter")
            _buf.seek(0)
            st.download_button(
                "↓ Export Table", _buf,
                file_name="MAHINDRA_STATE_MANPOWER.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="manpower_state_export",
            )
        st.dataframe(state_sorted, height=400, use_container_width=True)
    else:
        st.info("No state-level data available.")

    # ── Zone Chart ──────────────────────────────────────────────────────────
    st.markdown(style_section_header("Zone Manpower Distribution", ""), unsafe_allow_html=True)
    zone_df = zone_manpower_table(unified_df)
    if not zone_df.empty:
        fig = px.bar(
            zone_df, x="Zone", y=["Trained_Count", "Untrained_Count"],
            barmode="stack",
            color_discrete_map={"Trained_Count": "#1A1A2E", "Untrained_Count": "#E0E0E0"},
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20), yaxis_title="Employees", legend_title="")
        st.plotly_chart(fig, key="zone_manpower_chart", use_container_width=True)

        # Zone data table with export
        with st.expander("Zone-wise Data Table", expanded=False):
            z_label, z_btn = st.columns([6, 2])
            with z_btn:
                _buf2 = io.BytesIO()
                zone_df.to_excel(_buf2, index=False, engine="xlsxwriter")
                _buf2.seek(0)
                st.download_button(
                    "↓ Export Table", _buf2,
                    file_name="MAHINDRA_ZONE_MANPOWER.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="manpower_zone_export",
                )
            st.dataframe(zone_df, use_container_width=True)
    else:
        st.info("No zone-level data available.")


