"""
Exports Tab — Centralised download hub for all reports.
All download buttons are consolidated here. Individual section exports
and the combined 9-sheet full report are available.
"""
import datetime
import streamlit as st
import pandas as pd
from config.constants import BRAND_CHARCOAL
from utils.formatting_utils import style_section_header
from reports_export.excel_export import (
    generate_excel_report,
    export_skill_report,
    export_manpower_summary,
    export_backlog,
    export_audit_quality,
    export_india_dashboard,
)


def _download_row(label, buf, filename, description=""):
    """Render a single styled download row."""
    col_desc, col_btn = st.columns([5, 2])
    with col_desc:
        st.markdown(
            f"<div style='padding:10px 0 2px 0;'>"
            f"<span style='font-weight:600; color:#1A1A2E; font-size:0.95rem;'>{label}</span>"
            + (f"<br><span style='color:#717182; font-size:0.8rem;'>{description}</span>" if description else "")
            + "</div>",
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown("<div style='padding-top:8px;'>", unsafe_allow_html=True)
        st.download_button(
            "↓ Download",
            data=buf,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{filename}",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border-bottom:1px solid #ececf0; margin:4px 0 8px 0;'></div>",
        unsafe_allow_html=True,
    )


def _section_header(title, subtitle=""):
    st.markdown(style_section_header(title, subtitle), unsafe_allow_html=True)


def render_export_tab(unified_df, backlog_df, nomination_df, duplicate_df, audit_log, filters, kpis, stats):
    """Render the Exports tab with all download buttons."""

    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    row_count = len(unified_df) if unified_df is not None else 0
    active_filters = {k: v for k, v in filters.items() if v}

    # ── Pipeline metadata banner ──────────────────────────────────────────────
    st.markdown(
        f"<div style='background:#F7F7F9; border-radius:8px; padding:12px 18px; border: 1px solid #E8E8EC; "
        f"display:flex; gap:32px; flex-wrap:wrap; margin-bottom:20px;'>"
        f"<div><span style='color:#6B6B8D; font-size:0.78rem;'>REPORT GENERATED</span><br>"
        f"<span style='font-weight:700; font-size:0.92rem;'>{now}</span></div>"
        f"<div><span style='color:#6B6B8D; font-size:0.78rem;'>TOTAL RECORDS</span><br>"
        f"<span style='font-weight:700; font-size:0.92rem;'>{row_count:,}</span></div>"
        f"<div><span style='color:#6B6B8D; font-size:0.78rem;'>FILTERS APPLIED</span><br>"
        f"<span style='font-weight:700; font-size:0.92rem; color:{BRAND_CHARCOAL};'>"
        f"{'Yes — ' + ', '.join(active_filters.keys()) if active_filters else 'None (all data)'}</span></div>"
        f"<div><span style='color:#6B6B8D; font-size:0.78rem;'>UNIQUE MANPOWER</span><br>"
        f"<span style='font-weight:700; font-size:0.92rem;'>{kpis.get('total_manpower', 0):,}</span></div>"
        f"<div><span style='color:#6B6B8D; font-size:0.78rem;'>MATCHED RECORDS</span><br>"
        f"<span style='font-weight:700; font-size:0.92rem;'>{stats.get('matched_count', 0):,}</span></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if unified_df is None or unified_df.empty:
        st.info("Run the pipeline first to enable downloads.")
        return

    # ── Section A: Combined Full Report ──────────────────────────────────────
    _section_header(
        "Combined Full Report (9 Sheets)",
        "All tabs and data quality information in a single Excel workbook.",
    )

    @st.cache_data(show_spinner=False)
    def _full_report(filter_key, _udf, _bdf, _ddf, _alog):
        return generate_excel_report(_udf, _bdf, _ddf, _alog)

    filter_key = str(sorted(filters.items()))
    full_buf = _full_report(filter_key, unified_df, backlog_df, duplicate_df, audit_log)

    _download_row(
        "Full Analytics Report",
        full_buf,
        "MAHINDRA_TRAINING_ANALYTICS_REPORT.xlsx",
        "Unified Master · Backlog · Duplicates · Confidence · Data Quality · Skill · Nominations · Audit · Technician Profile",
    )

    # ── Section B: Per-Dashboard Downloads ───────────────────────────────────
    _section_header(
        "Individual Section Downloads",
        "Download a focused export for each dashboard section.",
    )

    @st.cache_data(show_spinner=False)
    def _cache(fn_name, filter_key, _df, _df2=None):
        from reports_export.excel_export import (
            export_skill_report, export_manpower_summary,
            export_backlog, export_audit_quality, export_india_dashboard,
        )
        if fn_name == "skill":
            return export_skill_report(_df)
        if fn_name == "manpower":
            return export_manpower_summary(_df)
        if fn_name == "backlog":
            return export_backlog(_df, _df2)
        if fn_name == "audit":
            return export_audit_quality(_df)
        if fn_name == "india":
            return export_india_dashboard(_df)
        return None

    _download_row(
        "Overview — India Dashboard",
        _cache("india", filter_key, unified_df),
        "MAHINDRA_INDIA_DASHBOARD.xlsx",
        "National summary · FY trend · Zone breakdown · State coverage",
    )
    _download_row(
        "Skill Analytics",
        _cache("skill", filter_key, unified_df),
        "MAHINDRA_SKILL_ANALYTICS.xlsx",
        "Pre/post scores · Skill delta · Regression flags · Validated skill level",
    )
    _download_row(
        "Manpower Summary",
        _cache("manpower", filter_key, unified_df),
        "MAHINDRA_MANPOWER_SUMMARY.xlsx",
        "State-wise and zone-wise headcount breakdown",
    )
    _download_row(
        "Pending Backlog & Nominations",
        _cache("backlog", filter_key, backlog_df, nomination_df),
        "MAHINDRA_BACKLOG_NOMINATIONS.xlsx",
        "Priority-ranked pending employees and nomination list",
    )
    _download_row(
        "Data Quality Report",
        _cache("audit", filter_key, unified_df),
        "MAHINDRA_DATA_QUALITY.xlsx",
        "Future dates · Skill regressions · Missing names · Prerequisite gaps",
    )
