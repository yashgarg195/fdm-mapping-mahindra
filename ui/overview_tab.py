"""
Overview Tab — KPI cards, FY trend line, MoM bar chart.
"""
import streamlit as st
import plotly.express as px
from config.constants import BRAND_RED, BRAND_CHARCOAL, BRAND_DARK_CORE
from utils.formatting_utils import style_kpi_card, format_count, format_pct
from analytics.overview import fy_trend, mom_trend


def render_overview(unified_df, kpis, filters):
    """Render the Overview tab."""
    # ── KPI Cards ───────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(style_kpi_card(
            "TOTAL MANPOWER", format_count(kpis.get("total_manpower", 0)),
            "UNIQUE EMPLOYEES", BRAND_RED
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card(
            "TRAINING COVERAGE", format_pct(kpis.get("coverage_pct", 0)),
            "HIGH + MEDIUM CONFIDENCE", BRAND_CHARCOAL
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(style_kpi_card(
            "PENDING / ELIGIBLE", format_count(kpis.get("pending_count", 0)),
            "AWAITING TRAINING", "#FF8C00"
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(style_kpi_card(
            "L3/L4 SPECIALISTS", format_count(kpis.get("l3_l4_specialist_count", 0)),
            "ADVANCED TECHNICIANS", BRAND_DARK_CORE
        ), unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### FY Training Trend")
        fy_data = fy_trend(unified_df)
        if not fy_data.empty:
            fig = px.line(
                fy_data, x="FY", y="Unique_Employees",
                markers=True,
                color_discrete_sequence=[BRAND_RED],
            )
            fig.update_layout(
                plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20),
                yaxis_title="Unique Employees Trained",
            )
            st.plotly_chart(fig, key="fy_trend_chart")
        else:
            st.info("No FY trend data available.")

    with chart2:
        st.markdown("#### Monthly Training Volume")
        mom_data = mom_trend(unified_df)
        if not mom_data.empty:
            fig = px.bar(
                mom_data, x="Month", y="Training_Count",
                color_discrete_sequence=[BRAND_CHARCOAL],
            )
            fig.update_layout(
                plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20),
                yaxis_title="Training Count",
            )
            st.plotly_chart(fig, key="mom_trend_chart")
        else:
            st.info("No monthly trend data available.")
