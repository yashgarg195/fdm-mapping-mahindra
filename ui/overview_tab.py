"""
Overview Tab — neutral KPI summary and bar-based national dashboard.
"""
import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.overview import national_summary, state_coverage_top, zone_breakdown
from ui.theme import CHART_COLORS, CHART_LAYOUT, NEUTRAL, kpi_card, label_value, section_header
from utils.formatting_utils import format_count, format_pct


def _show_download(df, filename, key):
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="xlsxwriter")
    buf.seek(0)
    st.download_button(
        "Export Table",
        buf,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
    )


def _clean_status_value(value):
    return 0 if value is None or pd.isna(value) else max(int(value), 0)


def render_overview(unified_df, kpis, filters):
    """Render the Overview tab with KPI cards and bar/stacked-bar analytics."""

    st.markdown(
        section_header(
            "National KPI Summary",
            "Filtered executive view of manpower, training status, identity resolution, and quality flags.",
        ),
        unsafe_allow_html=True,
    )

    total_manpower = kpis.get("total_manpower", 0)
    trained = kpis.get("unique_trained_manpower", 0)
    untrained = max(total_manpower - trained, 0)

    row1 = st.columns(4)
    cards = [
        ("Total Manpower", format_count(total_manpower), "Unique employees in current view", "accent"),
        ("Training Coverage", format_pct(kpis.get("coverage_pct", 0)), "Trained manpower percentage", "info"),
        ("Pending / Eligible", format_count(kpis.get("pending_count", 0)), "Awaiting training action", "warning"),
        ("L3/L4 Specialists", format_count(kpis.get("l3_l4_specialist_count", 0)), "Advanced trained technicians", "success"),
    ]
    for col, card in zip(row1, cards):
        with col:
            st.markdown(kpi_card(*card), unsafe_allow_html=True)

    row2 = st.columns(4)
    cards = [
        ("Trained Manpower", format_count(trained), "Unique employees trained", "trained"),
        ("Untrained Manpower", format_count(untrained), "No valid training record", "untrained"),
        ("Unresolved Identities", format_count(kpis.get("unresolved_mapping_count", 0)), "Excluded from official KPIs", "danger"),
        (
            "Data Quality Flags",
            format_count(kpis.get("regression_count", 0) + kpis.get("future_date_flag_count", 0)),
            "Regressions + future dates",
            "warning",
        ),
    ]
    for col, card in zip(row2, cards):
        with col:
            st.markdown(kpi_card(*card), unsafe_allow_html=True)

    if unified_df is None or unified_df.empty:
        st.info("Run the pipeline to view graphical analytics.")
        return

    nat = national_summary(unified_df)
    total_emp = _clean_status_value(nat.get("total_employees", 0))
    trained_emp = _clean_status_value(nat.get("total_trained", 0))
    pending_emp = _clean_status_value(nat.get("total_pending", 0))
    untrained_emp = _clean_status_value(nat.get("total_untrained", 0))
    not_pending_untrained = max(untrained_emp - pending_emp, 0)

    st.markdown(
        section_header(
            "All-India Manpower Status",
            "Stacked status view of trained, untrained, and pending manpower.",
        ),
        unsafe_allow_html=True,
    )

    status_col, stat_col = st.columns([1.65, 1])
    with status_col:
        if total_emp > 0:
            fig_status = go.Figure()
            status_parts = [
                ("Trained", trained_emp, CHART_COLORS["trained"]),
                ("Untrained", not_pending_untrained, CHART_COLORS["untrained"]),
                ("Pending / Eligible", pending_emp, CHART_COLORS["pending"]),
            ]
            for name, value, color in status_parts:
                fig_status.add_trace(
                    go.Bar(
                        name=name,
                        x=[value],
                        y=["All India"],
                        orientation="h",
                        marker_color=color,
                        text=[f"{value:,}"],
                        textposition="inside",
                    )
                )
            fig_status.update_layout(
                **CHART_LAYOUT,
                barmode="stack",
                height=230,
                xaxis=dict(title="Employees", showgrid=True, gridcolor=NEUTRAL["line"]),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=1.14),
            )
            st.plotly_chart(fig_status, use_container_width=True, key="overview_status_stack")
        else:
            st.info("No manpower data to display.")

    with stat_col:
        for label, value, tone in [
            ("Total Employees", total_emp, "accent"),
            ("Trained", trained_emp, "trained"),
            ("Untrained", untrained_emp, "untrained"),
            ("Pending / Eligible", pending_emp, "warning"),
            ("Total Dealers", nat.get("total_dealers", 0), "accent"),
            ("States Covered", nat.get("total_states", 0), "accent"),
            ("Zones", nat.get("total_zones", 0), "accent"),
        ]:
            st.markdown(label_value(label, f"{int(value):,}", tone), unsafe_allow_html=True)

    st.markdown(
        section_header(
            "Zone-wise Manpower Breakdown",
            "Operational view of trained, untrained, pending, and skill-level distribution by zone.",
        ),
        unsafe_allow_html=True,
    )

    zone_df = zone_breakdown(unified_df)
    if not zone_df.empty:
        zcol1, zcol2 = st.columns(2)
        with zcol1:
            fig_zone_main = go.Figure()
            for name, col_name, color in [
                ("Trained", "Trained", CHART_COLORS["trained"]),
                ("Untrained", "Untrained", CHART_COLORS["untrained"]),
                ("Pending", "Pending", CHART_COLORS["pending"]),
            ]:
                if col_name in zone_df.columns:
                    fig_zone_main.add_trace(
                        go.Bar(name=name, x=zone_df["Zone"], y=zone_df[col_name], marker_color=color)
                    )
            fig_zone_main.update_layout(
                **CHART_LAYOUT,
                barmode="stack",
                title="Training Status by Zone",
                yaxis=dict(title="Employees", showgrid=True, gridcolor=NEUTRAL["line"]),
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig_zone_main, use_container_width=True, key="zone_status_bar")

        with zcol2:
            fig_zone_levels = go.Figure()
            for level, color in [
                ("L1", CHART_COLORS["l1"]),
                ("L2", CHART_COLORS["l2"]),
                ("L3", CHART_COLORS["l3"]),
                ("L4", CHART_COLORS["l4"]),
            ]:
                if level in zone_df.columns:
                    fig_zone_levels.add_trace(
                        go.Bar(name=level, x=zone_df["Zone"], y=zone_df[level], marker_color=color)
                    )
            fig_zone_levels.update_layout(
                **CHART_LAYOUT,
                barmode="stack",
                title="Skill Level Mix by Zone",
                yaxis=dict(title="Employees", showgrid=True, gridcolor=NEUTRAL["line"]),
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig_zone_levels, use_container_width=True, key="zone_skill_bar")

        with st.expander("Zone-wise Data Table", expanded=False):
            _, export_col = st.columns([6, 2])
            with export_col:
                _show_download(zone_df, "MAHINDRA_OVERVIEW_ZONE_DATA.xlsx", "overview_zone_export")
            st.dataframe(zone_df, use_container_width=True)
    else:
        st.info("No zone-level data available.")

    st.markdown(
        section_header(
            "Top States by Training Coverage",
            "Highest-coverage states with a companion table for cross-checking.",
        ),
        unsafe_allow_html=True,
    )

    state_df = state_coverage_top(unified_df, n=10)
    if not state_df.empty:
        state_df = state_df.sort_values("Coverage_Pct")
        scol1, scol2 = st.columns([1.7, 1])
        with scol1:
            fig_states = px.bar(
                state_df,
                x="Coverage_Pct",
                y="State",
                orientation="h",
                text="Coverage_Pct",
                color="Coverage_Pct",
                color_continuous_scale=[
                    [0, "#cbd5e1"],
                    [0.55, "#60a5fa"],
                    [1.0, "#2563eb"],
                ],
                labels={"Coverage_Pct": "Coverage %", "State": ""},
            )
            fig_states.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_states.update_layout(
                **CHART_LAYOUT,
                coloraxis_showscale=False,
                xaxis=dict(title="Coverage %", range=[0, 110], showgrid=True, gridcolor=NEUTRAL["line"]),
            )
            st.plotly_chart(fig_states, use_container_width=True, key="state_coverage_bar")
        with scol2:
            _, export_col = st.columns([3, 2])
            with export_col:
                _show_download(state_df, "MAHINDRA_OVERVIEW_STATE_COVERAGE.xlsx", "overview_state_export")
            st.dataframe(
                state_df.rename(columns={"Coverage_Pct": "Coverage %"}),
                use_container_width=True,
                height=330,
            )
    else:
        st.info("No state-level data available.")
