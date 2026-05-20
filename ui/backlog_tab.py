"""
Backlog Tab — Rolling backlog table, nomination engine, aging charts.
"""
import io
import streamlit as st
import plotly.express as px
import pandas as pd
from config.constants import BRAND_RED, BRAND_CHARCOAL
from utils.formatting_utils import style_kpi_card, format_count
from analytics.backlog_analytics import backlog_aging_report, dealership_backlog_rank


def render_backlog(backlog_df, nomination_df, filters):
    """Render the Pending & Nomination Engine tab."""
    if backlog_df is None or backlog_df.empty:
        st.info("No backlog data available. Run the pipeline first.")
        return

    # ── Eligibility Timeframe Filter ────────────────────────────────────────
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        timeframe = st.selectbox(
            "Eligibility Timeframe",
            options=["All", ">= 1 month", ">= 3 months", ">= 6 months", ">= 1 year"],
            index=0
        )
    
    # Apply filter to backlog_df
    filtered_backlog = backlog_df.copy()
    if timeframe == ">= 1 month":
        filtered_backlog = filtered_backlog[filtered_backlog["Pending_Age_Months"] >= 1]
    elif timeframe == ">= 3 months":
        filtered_backlog = filtered_backlog[filtered_backlog["Pending_Age_Months"] >= 3]
    elif timeframe == ">= 6 months":
        filtered_backlog = filtered_backlog[filtered_backlog["Pending_Age_Months"] >= 6]
    elif timeframe == ">= 1 year":
        filtered_backlog = filtered_backlog[filtered_backlog["Pending_Age_Months"] >= 12]

    if filtered_backlog.empty:
        st.warning("No records match the selected eligibility timeframe.")
        return

    # ── KPI Cards ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    total_backlog = len(filtered_backlog)
    critical_count = (filtered_backlog.get("Pending_Category", pd.Series(dtype=str)) == "CRITICAL").sum()
    avg_age = filtered_backlog["Pending_Age_Months"].mean() if "Pending_Age_Months" in filtered_backlog.columns else 0

    with c1:
        st.markdown(style_kpi_card("TOTAL BACKLOG", format_count(total_backlog), "PENDING EMPLOYEES", BRAND_RED), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card("CRITICAL (12+ MO)", format_count(critical_count), "IMMEDIATE ATTENTION", "#FF8C00"), unsafe_allow_html=True)
    with c3:
        st.markdown(style_kpi_card("AVG PENDING AGE", f"{avg_age:.1f} mo", "MONTHS WAITING", BRAND_CHARCOAL), unsafe_allow_html=True)

    # ── Nomination Priority Table ───────────────────────────────────────────
    st.markdown("#### 🏆 Filtered Backlog & Nomination List")
    
    display_cols = [c for c in ["Nomination_Rank", "Star ID", "Name", "Designation",
                    "Dealer Code", "Dealer Name", "Zone", "State",
                    "Pending_Age_Months", "Training_Priority_Score", "Training_Status"]
                    if c in filtered_backlog.columns]
    
    st.dataframe(filtered_backlog[display_cols], height=400)

    # Download button for filtered backlog
    buf = io.BytesIO()
    filtered_backlog[display_cols].to_excel(buf, index=False, engine="xlsxwriter")
    buf.seek(0)
    st.download_button(
        "📥 Download Filtered Backlog (Excel)", buf,
        file_name="MAHINDRA_FILTERED_BACKLOG.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # ── Charts ──────────────────────────────────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Dealership Backlog Ranking")
        dr = dealership_backlog_rank(filtered_backlog)
        if not dr.empty:
            top15 = dr.head(15)
            fig = px.bar(
                top15, y="Dealer_Name", x="Backlog_Count", orientation="h",
                color_discrete_sequence=[BRAND_RED],
            )
            fig.update_layout(plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20), yaxis_title="")
            st.plotly_chart(fig, key="dealer_backlog_chart")
        else:
            st.info("No dealership backlog data.")

    with chart2:
        st.markdown("#### Pending Aging Distribution")
        aging = backlog_aging_report(filtered_backlog)
        if not aging.empty:
            fig = px.bar(
                aging, x="Aging_Bucket", y="Count",
                color="Aging_Bucket",
                color_discrete_map={"0-3 months": "#90EE90", "3-6 months": "#FFD700",
                                    "6-12 months": "#FF8C00", "12+ months": BRAND_RED},
            )
            fig.update_layout(plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig, key="aging_chart")
        else:
            st.info("No aging data.")
