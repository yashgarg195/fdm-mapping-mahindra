"""
Overview Tab — KPI summary cards + All-India graphical dashboard.
Includes: national KPIs, trained/untrained/pending stacked bar, FY trend,
L1-L4 stacked bar, top-10 states by coverage, zone-wise breakdown.
"""
import io
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.constants import BRAND_CHARCOAL
from utils.formatting_utils import style_kpi_card, format_count, format_pct, style_section_header, COLUMN_CONFIGS
from analytics.overview import (
    national_summary, fy_trend, l_level_breakdown, zone_breakdown, state_coverage_top,
)

# Colour palette used across all charts in this tab
# Colour palette used across all charts in this tab
_L_COLORS = {
    "L1": "#FF7043",
    "L2": "#FFCA28",
    "L3": "#66BB6A",
    "L4": "#42A5F5",
    "Untrained": "#E0E0E0",
    "Trained": "#455A64",
    "Pending": "#F57C00",
}

_CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", size=12),
    margin=dict(t=30, b=20, l=20, r=20),
)


def _section(title, subtitle=""):
    st.markdown(style_section_header(title, subtitle), unsafe_allow_html=True)


def render_overview(unified_df, kpis, filters):
    """Render the Overview tab with KPI cards and All-India graphical dashboard."""

    # ── Section A: KPI Summary Cards ─────────────────────────────────────────
    _section("National KPI Summary", "National KPIs · Training coverage · Zone and state summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(style_kpi_card(
            "TOTAL MANPOWER", format_count(kpis.get("total_manpower", 0)),
            "UNIQUE EMPLOYEES", "#1A1A2E",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card(
            "TRAINING COVERAGE", format_pct(kpis.get("coverage_pct", 0)),
            "HIGH + MEDIUM CONFIDENCE", "#2E7D32",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(style_kpi_card(
            "PENDING / ELIGIBLE", format_count(kpis.get("pending_count", 0)),
            "AWAITING TRAINING", "#F57C00",
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(style_kpi_card(
            "L3/L4 SPECIALISTS", format_count(kpis.get("l3_l4_specialist_count", 0)),
            "ADVANCED TECHNICIANS", "#1976D2",
        ), unsafe_allow_html=True)

    # Second KPI row
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(style_kpi_card(
            "TRAINED MANPOWER", format_count(kpis.get("unique_trained_manpower", 0)),
            "UNIQUE EMPLOYEES TRAINED", "#2E7D32",
        ), unsafe_allow_html=True)
    with c6:
        untrained = kpis.get("total_manpower", 0) - kpis.get("unique_trained_manpower", 0)
        st.markdown(style_kpi_card(
            "UNTRAINED MANPOWER", format_count(max(untrained, 0)),
            "NEVER TRAINED", "#C62828",
        ), unsafe_allow_html=True)
    with c7:
        st.markdown(style_kpi_card(
            "UNRESOLVED IDENTITIES", format_count(kpis.get("unresolved_mapping_count", 0)),
            "EXCLUDED FROM KPIs", "#78909C",
        ), unsafe_allow_html=True)
    with c8:
        st.markdown(style_kpi_card(
            "DATA QUALITY FLAGS", format_count(
                kpis.get("regression_count", 0) + kpis.get("future_date_flag_count", 0)
            ),
            "REGRESSIONS + FUTURE DATES", "#F57C00",
        ), unsafe_allow_html=True)

    if unified_df is None or unified_df.empty:
        st.info("Run the pipeline to view graphical analytics.")
        return

    # ── Section B: Trained / Untrained / Pending Stacked Bar ─────────────────
    _section("All-India Manpower Status")

    nat = national_summary(unified_df)
    total_emp = nat.get("total_employees", 0)
    trained_emp = nat.get("total_trained", 0)
    untrained_emp = nat.get("total_untrained", 0)
    pending_emp = nat.get("total_pending", 0)

    bar_col, stat_col = st.columns([1, 1])

    with bar_col:
        if total_emp > 0:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Trained", x=[trained_emp], y=["Status"], orientation='h', marker_color="#2E7D32"))
            fig_bar.add_trace(go.Bar(name="Pending", x=[pending_emp], y=["Status"], orientation='h', marker_color="#F57C00"))
            fig_bar.add_trace(go.Bar(name="Untrained", x=[max(untrained_emp - pending_emp, 0)], y=["Status"], orientation='h', marker_color="#E0E0E0"))
            fig_bar.update_layout(
                **_CHART_LAYOUT,
                barmode="stack",
                showlegend=True,
                legend=dict(orientation="h", y=-0.2),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=180,
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="manpower_stacked_bar")
        else:
            st.info("No manpower data to display.")

    with stat_col:
        st.markdown("<br>", unsafe_allow_html=True)
        metrics = [
            ("Total Employees", total_emp, "#1A1A2E"),
            ("Trained", trained_emp, "#2E7D32"),
            ("Untrained", untrained_emp, "#C62828"),
            ("Pending / Eligible", pending_emp, "#F57C00"),
            ("Total Dealers", nat.get("total_dealers", 0), "#4A4A6A"),
            ("States Covered", nat.get("total_states", 0), "#4A4A6A"),
            ("Zones", nat.get("total_zones", 0), "#4A4A6A"),
        ]
        for label, val, color in metrics:
            st.markdown(
                f"<div style='display:flex; justify-content:space-between; "
                f"padding:7px 12px; margin-bottom:4px; border-radius:6px; "
                f"background:#F7F7F9; border: 1px solid #E8E8EC;'>"
                f"<span style='color:#6B6B8D; font-size:0.85rem;'>{label}</span>"
                f"<span style='color:{color}; font-weight:700; font-size:0.95rem;'>{val:,}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Section C: FY Training Trend ─────────────────────────────────────────
    _section("Year-wise Training Trend")

    fy_df = fy_trend(unified_df)
    if not fy_df.empty:
        fig_fy = go.Figure()
        fig_fy.add_trace(go.Bar(
            x=fy_df["FY"], y=fy_df["Trained_Count"],
            name="Training Records",
            marker_color="#455A64",
            opacity=0.85,
        ))
        fig_fy.update_layout(
            **_CHART_LAYOUT,
            xaxis_title="Financial Year",
            yaxis=dict(title="Training Records", showgrid=True, gridcolor="#ececf0"),
            legend=dict(orientation="h", y=1.1),
            barmode="group",
        )
        st.plotly_chart(fig_fy, use_container_width=True, key="fy_trend_chart")
    else:
        st.info("No FY training data available.")

    # ── Section D: L1-L4 Skill Breakdown by FY ───────────────────────────────
    _section("L1–L4 Skill Level Breakdown by Financial Year")

    ll_df = l_level_breakdown(unified_df)
    if not ll_df.empty:
        fig_ll = go.Figure()
        for level, color in [("L1", _L_COLORS["L1"]), ("L2", _L_COLORS["L2"]),
                              ("L3", _L_COLORS["L3"]), ("L4", _L_COLORS["L4"]),
                              ("Untrained", _L_COLORS["Untrained"])]:
            if level in ll_df.columns:
                fig_ll.add_trace(go.Bar(
                    name=level, x=ll_df["FY"], y=ll_df[level],
                    marker_color=color,
                ))
        fig_ll.update_layout(
            **_CHART_LAYOUT,
            barmode="stack",
            xaxis_title="Financial Year",
            yaxis=dict(title="Employee Count", showgrid=True, gridcolor="#ececf0"),
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig_ll, use_container_width=True, key="l_level_chart")
    else:
        st.info("No skill level data available by FY.")

    # ── Section E: Zone-wise Breakdown ───────────────────────────────────────
    _section("Zone-wise Manpower Breakdown")

    zone_df = zone_breakdown(unified_df)
    if not zone_df.empty:
        zcol1, zcol2 = st.columns(2)

        with zcol1:
            # Stacked trained/untrained bar
            fig_zone_main = go.Figure()
            fig_zone_main.add_trace(go.Bar(
                name="Trained", x=zone_df["Zone"], y=zone_df["Trained"],
                marker_color="#455A64",
            ))
            fig_zone_main.add_trace(go.Bar(
                name="Untrained", x=zone_df["Zone"], y=zone_df["Untrained"],
                marker_color="#E0E0E0",
            ))
            fig_zone_main.add_trace(go.Bar(
                name="Pending", x=zone_df["Zone"], y=zone_df["Pending"],
                marker_color="#F57C00",
            ))
            fig_zone_main.update_layout(
                **_CHART_LAYOUT,
                barmode="stack",
                title="Trained vs Untrained by Zone",
                yaxis=dict(title="Employees", showgrid=True, gridcolor="#ececf0"),
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig_zone_main, use_container_width=True, key="zone_main_chart")

        with zcol2:
            # L1-L4 breakdown per zone
            fig_zone_ll = go.Figure()
            for level, color in [("L1", _L_COLORS["L1"]), ("L2", _L_COLORS["L2"]),
                                  ("L3", _L_COLORS["L3"]), ("L4", _L_COLORS["L4"])]:
                if level in zone_df.columns:
                    fig_zone_ll.add_trace(go.Bar(
                        name=level, x=zone_df["Zone"], y=zone_df[level],
                        marker_color=color,
                    ))
            fig_zone_ll.update_layout(
                **_CHART_LAYOUT,
                barmode="stack",
                title="L1–L4 Skill Distribution by Zone",
                yaxis=dict(title="Employee Count", showgrid=True, gridcolor="#ececf0"),
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig_zone_ll, use_container_width=True, key="zone_ll_chart")

        # Zone tabular summary
        with st.expander("Zone-wise Data Table", expanded=False):
            _z_label, _z_btn = st.columns([6, 2])
            with _z_btn:
                _buf_z = io.BytesIO()
                zone_df.to_excel(_buf_z, index=False, engine="xlsxwriter")
                _buf_z.seek(0)
                st.download_button(
                    "Export Table", _buf_z,
                    file_name="MAHINDRA_OVERVIEW_ZONE_DATA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="overview_zone_export",
                )
            st.dataframe(zone_df, use_container_width=True, column_config=COLUMN_CONFIGS)
    else:
        st.info("No zone-level data available (Zone column missing in dataset).")

    # ── Section F: Top 10 States by Coverage ─────────────────────────────────
    _section("Top 10 States by Training Coverage")

    state_df = state_coverage_top(unified_df, n=10)
    if not state_df.empty:
        scol1, scol2 = st.columns([2, 1])
        with scol1:
            fig_states = px.bar(
                state_df.sort_values("Coverage_Pct"),
                x="Coverage_Pct", y="State", orientation="h",
                color="Coverage_Pct",
                color_continuous_scale=[[0, "#E0E0E0"], [1.0, "#455A64"]],
                labels={"Coverage_Pct": "Coverage %", "State": ""},
                text="Coverage_Pct",
            )
            fig_states.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_states.update_layout(
                **_CHART_LAYOUT,
                coloraxis_showscale=False,
                xaxis=dict(title="Coverage %", range=[0, 110], showgrid=True, gridcolor="#ececf0"),
            )
            st.plotly_chart(fig_states, use_container_width=True, key="state_coverage_chart")
        with scol2:
            _st_label, _st_btn = st.columns([3, 2])
            with _st_btn:
                _buf_st = io.BytesIO()
                state_df.to_excel(_buf_st, index=False, engine="xlsxwriter")
                _buf_st.seek(0)
                st.download_button(
                    "Export Table", _buf_st,
                    file_name="MAHINDRA_OVERVIEW_STATE_COVERAGE.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="overview_state_export",
                )
            st.dataframe(
                state_df,
                use_container_width=True, height=320,
                column_config=COLUMN_CONFIGS,
            )
    else:
        st.info("No state-level data available.")
