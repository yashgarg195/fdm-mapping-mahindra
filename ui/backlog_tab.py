"""
Backlog Tab — eligibility filter, nomination table, and backlog charts.
"""
import io

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.backlog_analytics import backlog_aging_report, dealership_backlog_rank
from ui.theme import CHART_LAYOUT, NEUTRAL, callout, kpi_card, section_header
from utils.formatting_utils import format_count


def _export_table(df, filename, key):
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="xlsxwriter")
    buf.seek(0)
    st.download_button(
        "Download Excel",
        buf,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
    )


def _filter_by_timeframe(backlog_df, timeframe):
    if "Pending_Age_Months" not in backlog_df.columns or timeframe == "All":
        return backlog_df.copy()
    thresholds = {
        ">= 1 month": 1,
        ">= 3 months": 3,
        ">= 6 months": 6,
        ">= 1 year": 12,
    }
    return backlog_df[backlog_df["Pending_Age_Months"] >= thresholds.get(timeframe, 0)].copy()


def render_backlog(backlog_df, nomination_df, filters):
    """Render the Pending & Nominations tab."""
    st.markdown(
        section_header(
            "Pending & Nominations",
            "Eligibility-based backlog review and downloadable nomination list.",
        ),
        unsafe_allow_html=True,
    )

    if backlog_df is None or backlog_df.empty:
        st.info("No backlog data available. Run the pipeline first.")
        return

    st.markdown(
        callout(
            "Eligibility timeframe",
            "Filter employees by how long they have been pending training, then export the currently filtered backlog for action.",
            "info",
        ),
        unsafe_allow_html=True,
    )

    col_filter, col_export = st.columns([1.2, 2.8])
    with col_filter:
        timeframe = st.selectbox(
            "Eligibility Timeframe",
            options=["All", ">= 1 month", ">= 3 months", ">= 6 months", ">= 1 year"],
            index=0,
        )

    filtered_backlog = _filter_by_timeframe(backlog_df, timeframe)
    if filtered_backlog.empty:
        st.warning("No records match the selected eligibility timeframe.")
        return

    display_cols = [
        c for c in [
            "Nomination_Rank", "Star ID", "Name", "Designation",
            "Dealer Code", "Dealer Name", "Zone", "State",
            "Pending_Age_Months", "Training_Priority_Score", "Training_Status",
        ] if c in filtered_backlog.columns
    ]
    export_df = filtered_backlog[display_cols] if display_cols else filtered_backlog
    with col_export:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        _export_table(export_df, "MAHINDRA_FILTERED_BACKLOG.xlsx", "backlog_filtered_export")

    total_backlog = len(filtered_backlog)
    critical_count = (
        (filtered_backlog.get("Pending_Category", pd.Series(dtype=str)) == "CRITICAL").sum()
    )
    avg_age = (
        filtered_backlog["Pending_Age_Months"].mean()
        if "Pending_Age_Months" in filtered_backlog.columns else 0
    )
    nomination_count = len(nomination_df) if nomination_df is not None else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Backlog", format_count(total_backlog), "Pending employees", "accent"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Critical 12+ Mo", format_count(critical_count), "Immediate attention", "warning"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Avg Pending Age", f"{avg_age:.1f} mo", "Months waiting", "info"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Nominations", format_count(nomination_count), "Generated priority list", "success"), unsafe_allow_html=True)

    st.markdown(
        section_header("Filtered Backlog & Nomination List", f"{len(export_df):,} rows in current view."),
        unsafe_allow_html=True,
    )
    st.dataframe(export_df, height=420, use_container_width=True)

    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown(section_header("Dealership Backlog Ranking"), unsafe_allow_html=True)
        dr = dealership_backlog_rank(filtered_backlog)
        if not dr.empty:
            top15 = dr.head(15).sort_values("Backlog_Count")
            fig = px.bar(
                top15,
                y="Dealer_Name",
                x="Backlog_Count",
                orientation="h",
                color_discrete_sequence=["#475569"],
                labels={"Backlog_Count": "Backlog", "Dealer_Name": ""},
            )
            fig.update_layout(
                **CHART_LAYOUT,
                xaxis=dict(title="Backlog", showgrid=True, gridcolor=NEUTRAL["line"]),
                yaxis=dict(title=""),
            )
            st.plotly_chart(fig, use_container_width=True, key="dealer_backlog_chart")
        else:
            st.info("No dealership backlog data.")

    with chart2:
        st.markdown(section_header("Pending Aging Distribution"), unsafe_allow_html=True)
        aging = backlog_aging_report(filtered_backlog)
        if not aging.empty:
            fig = px.bar(
                aging,
                x="Aging_Bucket",
                y="Count",
                color="Aging_Bucket",
                color_discrete_map={
                    "0-3 months": "#cbd5e1",
                    "3-6 months": "#93c5fd",
                    "6-12 months": "#f59e0b",
                    "12+ months": "#b91c1c",
                },
            )
            fig.update_layout(
                **CHART_LAYOUT,
                showlegend=False,
                yaxis=dict(title="Employees", showgrid=True, gridcolor=NEUTRAL["line"]),
                xaxis=dict(title=""),
            )
            st.plotly_chart(fig, use_container_width=True, key="aging_chart")
        else:
            st.info("No aging data.")
