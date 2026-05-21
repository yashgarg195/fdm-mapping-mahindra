"""
Manpower Tab — cross-check filters, manpower tables, and zone distribution.
"""
import io

import plotly.express as px
import streamlit as st

from analytics.manpower import state_manpower_table, unique_manpower_count, zone_manpower_table
from ui.theme import CHART_COLORS, CHART_LAYOUT, NEUTRAL, kpi_card, section_header
from utils.formatting_utils import format_count


def _export_table(df, filename, key):
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


def _options(df, column):
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().astype(str).unique().tolist())


def _apply_local_filters(df, selections):
    filtered = df.copy()
    for column, values in selections.items():
        if values and column in filtered.columns:
            filtered = filtered[filtered[column].astype(str).isin(values)]
    return filtered


def render_manpower(unified_df, filters):
    """Render the Unique Manpower tab."""
    st.markdown(
        section_header(
            "Unique Manpower",
            "Cross-check verified headcount by location, role, dealership, and training status.",
        ),
        unsafe_allow_html=True,
    )

    if unified_df is None or unified_df.empty:
        st.info("No data available for manpower analysis.")
        return

    st.markdown(
        "<div class='dash-callout' style='border-left-color:#475569;'>"
        "<div class='dash-callout-title'>Cross-check filters</div>"
        "<div class='dash-callout-body'>Use these local filters to validate manpower counts without changing other dashboard tabs.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns(4)
    region_col = "State" if "State" in unified_df.columns else ("Zone" if "Zone" in unified_df.columns else None)
    role_col = "Designation" if "Designation" in unified_df.columns else None
    dealer_col = "Dealer Name" if "Dealer Name" in unified_df.columns else None
    status_col = "Training_Status" if "Training_Status" in unified_df.columns else None

    selections = {}
    if region_col:
        selections[region_col] = f1.multiselect("Location / Region", _options(unified_df, region_col), key="mp_region")
    else:
        f1.info("No location column")
    if role_col:
        selections[role_col] = f2.multiselect("Role / Designation", _options(unified_df, role_col), key="mp_role")
    else:
        f2.info("No role column")
    if dealer_col:
        selections[dealer_col] = f3.multiselect("Dealership", _options(unified_df, dealer_col), key="mp_dealer")
    else:
        f3.info("No dealership column")
    if status_col:
        selections[status_col] = f4.multiselect("Training Status", _options(unified_df, status_col), key="mp_status")
    else:
        f4.info("No status column")

    local_df = _apply_local_filters(unified_df, selections)

    total = unique_manpower_count(local_df)
    unresolved = (
        (local_df["Match_Confidence"] == "UNRESOLVED").sum()
        if "Match_Confidence" in local_df.columns else 0
    )
    trained = (
        local_df[
            ~local_df["Training_Status"].astype(str).isin(["NOT_TRAINED", "ELIGIBLE", ""])
        ].shape[0]
        if "Training_Status" in local_df.columns else 0
    )
    filtered_delta = len(unified_df) - len(local_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Unique Manpower", format_count(total), "Verified employees", "accent"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Filtered Rows", f"{len(local_df):,}", f"{filtered_delta:,} rows hidden", "info"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Trained Rows", f"{trained:,}", "Rows with completed training status", "trained"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Unresolved Identities", format_count(unresolved), "Excluded from counts", "danger"), unsafe_allow_html=True)

    st.markdown(
        section_header("State-wise Manpower Breakdown", "Table view for operational validation."),
        unsafe_allow_html=True,
    )
    state_df = state_manpower_table(local_df)
    if not state_df.empty:
        state_sorted = state_df.sort_values("Total_Employees", ascending=False)
        label_col, btn_col = st.columns([6, 2])
        with label_col:
            st.markdown(f"**{len(state_sorted):,} states/regions** in current view.")
        with btn_col:
            _export_table(state_sorted, "MAHINDRA_STATE_MANPOWER.xlsx", "manpower_state_export")
        st.dataframe(state_sorted, height=400, use_container_width=True)
    else:
        st.info("No state-level data available.")

    st.markdown(
        section_header("Zone Manpower Distribution", "Stacked trained/untrained view by zone."),
        unsafe_allow_html=True,
    )
    zone_df = zone_manpower_table(local_df)
    if not zone_df.empty:
        fig = px.bar(
            zone_df,
            x="Zone",
            y=["Trained_Count", "Untrained_Count"],
            barmode="stack",
            color_discrete_map={
                "Trained_Count": CHART_COLORS["trained"],
                "Untrained_Count": CHART_COLORS["untrained"],
            },
        )
        fig.update_layout(
            **CHART_LAYOUT,
            yaxis=dict(title="Employees", showgrid=True, gridcolor=NEUTRAL["line"]),
            legend_title="",
        )
        st.plotly_chart(fig, use_container_width=True, key="zone_manpower_chart")

        with st.expander("Zone-wise Data Table", expanded=False):
            _, btn_col = st.columns([6, 2])
            with btn_col:
                _export_table(zone_df, "MAHINDRA_ZONE_MANPOWER.xlsx", "manpower_zone_export")
            st.dataframe(zone_df, use_container_width=True)
    else:
        st.info("No zone-level data available.")
