"""
Overview Tab — KPI cards.
"""
import streamlit as st
import plotly.express as px
from config.constants import BRAND_RED, BRAND_CHARCOAL, BRAND_DARK_CORE
from utils.formatting_utils import style_kpi_card, format_count, format_pct

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

