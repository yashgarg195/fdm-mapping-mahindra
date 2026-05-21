"""
Audit Tab — Mapping confidence, duplicate log, unresolved queue,
cross-ID suspects, data quality issues.
FIXED: Shows cross-ID duplicate suspects, training status breakdown,
vectorized operations for speed.
"""
import io
import streamlit as st
import plotly.express as px
import pandas as pd
from config.constants import CONFIDENCE_ORDER
from ui.theme import CHART_COLORS, CHART_LAYOUT, NEUTRAL, callout, section_header


def render_audit(unified_df, duplicate_df, unresolved_df):
    """Render the Audit & Exceptions tab."""
    # ── Mapping Confidence Distribution ─────────────────────────────────────
    st.markdown(
        section_header(
            "Mapping Confidence Distribution",
            "Exception-summary view of identity resolution confidence across the filtered data.",
        ),
        unsafe_allow_html=True,
    )

    if unified_df is not None and not unified_df.empty and "Match_Confidence" in unified_df.columns:
        conf_counts = unified_df["Match_Confidence"].value_counts().reindex(CONFIDENCE_ORDER, fill_value=0).reset_index()
        conf_counts.columns = ["Confidence", "Count"]
        conf_counts["Display_Confidence"] = conf_counts["Confidence"].replace({"FUZZY": "POSSIBLE MATCH"})
        conf_counts["Pct"] = (conf_counts["Count"] / max(conf_counts["Count"].sum(), 1) * 100).round(1)

        chart1, chart2 = st.columns(2)
        with chart1:
            neutral_conf_colors = {
                "HIGH": CHART_COLORS["high"],
                "MEDIUM": CHART_COLORS["medium"],
                "LOW": CHART_COLORS["low"],
                "POSSIBLE MATCH": "#f59e0b",
                "UNRESOLVED": CHART_COLORS["unresolved"],
            }
            fig = px.pie(
                conf_counts,
                names="Display_Confidence",
                values="Count",
                color="Display_Confidence",
                color_discrete_map=neutral_conf_colors,
                hole=0.48,
            )
            fig.update_layout(
                **CHART_LAYOUT,
                legend=dict(orientation="h", y=-0.05),
            )
            st.plotly_chart(fig, use_container_width=True, key="conf_pie")

        with chart2:
            c2_label, c2_btn = st.columns([3, 2])
            with c2_btn:
                _buf_conf = io.BytesIO()
                conf_counts.drop(columns=["Confidence"]).rename(
                    columns={"Display_Confidence": "Confidence"}
                ).to_excel(_buf_conf, index=False, engine="xlsxwriter")
                _buf_conf.seek(0)
                st.download_button(
                    "Export Table", _buf_conf,
                    file_name="MAHINDRA_CONFIDENCE_DISTRIBUTION.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="audit_conf_export",
                )
            st.dataframe(
                conf_counts.drop(columns=["Confidence"]).rename(columns={"Display_Confidence": "Confidence"}),
                height=200,
            )

        # Training Status Breakdown
        if "Training_Status" in unified_df.columns:
            st.markdown(
                section_header("Training Status Breakdown", "Current status mix for the filtered master data."),
                unsafe_allow_html=True,
            )
            status_counts = unified_df["Training_Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            status_counts["Pct"] = (status_counts["Count"] / max(status_counts["Count"].sum(), 1) * 100).round(1)
            ts_label, ts_btn = st.columns([6, 2])
            with ts_btn:
                _buf_ts = io.BytesIO()
                status_counts.to_excel(_buf_ts, index=False, engine="xlsxwriter")
                _buf_ts.seek(0)
                st.download_button(
                    "Export Table", _buf_ts,
                    file_name="MAHINDRA_TRAINING_STATUS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="audit_ts_export",
                )
            st.dataframe(status_counts, height=200)
    else:
        st.info("No confidence data available.")

    # ── Duplicate Log ───────────────────────────────────────────────────────
    st.markdown(section_header("Duplicate Log"), unsafe_allow_html=True)
    if duplicate_df is not None and not duplicate_df.empty:
        dup_label, dup_btn = st.columns([6, 2])
        with dup_label:
            st.markdown(f"**{len(duplicate_df)} duplicate records detected** (flagged, not deleted)")
        display_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name",
                        "DATA_QUALITY_STATUS", "DATA_QUALITY_REASON"] if c in duplicate_df.columns]
        dup_display = duplicate_df[display_cols] if display_cols else duplicate_df
        with dup_btn:
            _buf_dup = io.BytesIO()
            dup_display.to_excel(_buf_dup, index=False, engine="xlsxwriter")
            _buf_dup.seek(0)
            st.download_button(
                "Export Table", _buf_dup,
                file_name="MAHINDRA_DUPLICATE_LOG.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="audit_dup_export",
            )
        st.dataframe(dup_display, height=300, use_container_width=True)
    else:
        st.success("No exact duplicate records detected.")

    # ── Suspect Duplicates (Possible Matches) ───────────────────────────────
    st.markdown(section_header("Possible Match Queue"), unsafe_allow_html=True)
    st.markdown(
        callout(
            "What is a Possible Match?",
            "A Possible Match means two records may belong to the same person based on similar names, dealer/location, or other identity signals. These records need human review before confirmation.",
            "warning",
        ),
        unsafe_allow_html=True,
    )
    if unified_df is not None and not unified_df.empty:
        suspect_col = None
        if "DATA_QUALITY_STATUS" in unified_df.columns:
            suspects = unified_df[unified_df["DATA_QUALITY_STATUS"] == "SUSPECT_DUPLICATE"]
            suspect_col = "DATA_QUALITY_STATUS"
        else:
            suspects = pd.DataFrame()

        # Also check cross-ID suspects from matching engine
        if "CROSS_ID_DUPLICATE_SUSPECT" in unified_df.columns:
            cross_suspects = unified_df[unified_df["CROSS_ID_DUPLICATE_SUSPECT"] == True]
            if not cross_suspects.empty:
                if suspects.empty:
                    suspects = cross_suspects
                else:
                    suspects = pd.concat([suspects, cross_suspects]).drop_duplicates()

        if not suspects.empty:
            st.markdown(f"**{len(suspects)} possible match records** require review.")

            # ── Enrich with suspected match's identity ───────────────────────
            # CROSS_ID_DUPLICATE_NOTE contains a candidate Star ID and score.
            # Parse the suspected Star ID and look up their details in unified_df.
            if "CROSS_ID_DUPLICATE_NOTE" in suspects.columns and "Star ID" in unified_df.columns:
                import re

                def _extract_sid(note):
                    """Extract the first Star ID mentioned in the note string."""
                    if not note or pd.isna(note):
                        return None
                    m = re.search(r"Similar to Star ID\s+(\S+)", str(note))
                    return m.group(1).strip(";, ") if m else None

                # Build lookup: Star ID → (Name, Dealer Code, Dealer Name) from unified_df
                _lookup_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name"]
                                if c in unified_df.columns]
                _lookup = (
                    unified_df[_lookup_cols]
                    .drop_duplicates(subset=["Star ID"])
                    .set_index("Star ID")
                )

                suspects = suspects.copy()
                suspects["_match_sid"] = suspects["CROSS_ID_DUPLICATE_NOTE"].apply(_extract_sid)

                suspects["Suspected_Match_StarID"] = suspects["_match_sid"]
                suspects["Suspected_Match_Name"] = suspects["_match_sid"].map(
                    _lookup["Name"] if "Name" in _lookup.columns else pd.Series(dtype=str)
                )
                if "Dealer Code" in _lookup.columns:
                    suspects["Suspected_Match_Dealer_Code"] = suspects["_match_sid"].map(_lookup["Dealer Code"])
                if "Dealer Name" in _lookup.columns:
                    suspects["Suspected_Match_Dealer_Name"] = suspects["_match_sid"].map(_lookup["Dealer Name"])

                suspects.drop(columns=["_match_sid"], inplace=True)

            display_cols = [c for c in [
                "Star ID", "Name", "Dealer Code", "Dealer Name",
                "DATA_QUALITY_STATUS", "CROSS_ID_DUPLICATE_NOTE",
                "Suspected_Match_StarID", "Suspected_Match_Name",
                "Suspected_Match_Dealer_Code", "Suspected_Match_Dealer_Name",
            ] if c in suspects.columns]
            suspects_display = suspects[display_cols] if display_cols else suspects
            suspects_display = suspects_display.rename(
                columns={"CROSS_ID_DUPLICATE_NOTE": "Possible_Match_Note"}
            )

            sus_label, sus_btn = st.columns([6, 2])
            with sus_btn:
                _buf_sus = io.BytesIO()
                suspects_display.to_excel(_buf_sus, index=False, engine="xlsxwriter")
                _buf_sus.seek(0)
                st.download_button(
                    "Export Table", _buf_sus,
                    file_name="MAHINDRA_SUSPECT_DUPLICATES.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="audit_suspect_export",
                )
            st.dataframe(suspects_display, height=350, use_container_width=True)

        else:
            st.success("No possible matches detected.")
    else:
        st.info("No data loaded.")

    # ── Unresolved Queue ────────────────────────────────────────────────────
    st.markdown(section_header("Unresolved Identity Queue", "Records excluded from official KPIs until mapping review is complete."), unsafe_allow_html=True)
    if unresolved_df is not None and not unresolved_df.empty:
        ur_label, ur_btn = st.columns([6, 2])
        with ur_label:
            st.markdown(f"**{len(unresolved_df)} unresolved records** — excluded from official KPIs")
        display_cols = [c for c in ["Star ID", "Name", "Designation", "Dealer Code",
                        "Dealer Name", "Match_Method", "Fuzzy_Score", "Phonetic_Score"]
                        if c in unresolved_df.columns]
        ur_display = unresolved_df[display_cols] if display_cols else unresolved_df
        ur_display = ur_display.rename(columns={"Fuzzy_Score": "Similarity_Score"})
        with ur_btn:
            _buf_ur = io.BytesIO()
            ur_display.to_excel(_buf_ur, index=False, engine="xlsxwriter")
            _buf_ur.seek(0)
            st.download_button(
                "Export Table", _buf_ur,
                file_name="MAHINDRA_UNRESOLVED_QUEUE.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="audit_unresolved_export",
            )
        st.dataframe(ur_display, height=300, use_container_width=True)
    else:
        st.success("No unresolved records. All identities mapped.")

    # ── Data Quality Issues (with local filters) ─────────────────────────────
    st.markdown(section_header("Data Quality Issues"), unsafe_allow_html=True)
    if unified_df is not None and not unified_df.empty:
        # Base columns to pull from each flagged subset — include Zone & State if present
        _base_cols = [c for c in ["Star ID", "Name", "Zone", "State", "Dealer Code"]
                      if c in unified_df.columns]

        issues_frames = []

        # Future dates
        if "FUTURE_JOINING_FLAG" in unified_df.columns:
            future = unified_df[unified_df["FUTURE_JOINING_FLAG"] == True]
            if not future.empty:
                f_df = future[_base_cols].copy()
                f_df["Issue_Type"] = "FUTURE_DATE"
                f_df["Issue_Description"] = "Joining Date is in the future"
                issues_frames.append(f_df)

        # Skill regressions
        if "SKILL_REGRESSION_FLAG" in unified_df.columns:
            regressions = unified_df[unified_df["SKILL_REGRESSION_FLAG"] == True]
            if not regressions.empty:
                r_df = regressions[_base_cols].copy()
                r_df["Issue_Type"] = "SKILL_REGRESSION"
                if "SKILL LEVEL - PRE" in regressions.columns and "SKILL LEVEL - POST" in regressions.columns:
                    r_df["Issue_Description"] = (
                        "Post (" + regressions["SKILL LEVEL - POST"].astype(str) +
                        ") < Pre (" + regressions["SKILL LEVEL - PRE"].astype(str) + ")"
                    ).values
                else:
                    r_df["Issue_Description"] = "Post-training skill lower than pre-training"
                issues_frames.append(r_df)

        # Missing names
        if "Name" in unified_df.columns:
            missing_name = unified_df[
                unified_df["Name"].isna() | (unified_df["Name"].astype(str).str.strip() == "")
            ]
            if not missing_name.empty:
                m_df = missing_name[_base_cols].head(50).copy()
                m_df["Issue_Type"] = "MISSING_NAME"
                m_df["Issue_Description"] = "Employee name is missing"
                issues_frames.append(m_df)

        # Missing prerequisite (L4 without L1-L3 progression)
        if "MISSING_PREREQUISITE_FLAG" in unified_df.columns:
            prereq = unified_df[unified_df["MISSING_PREREQUISITE_FLAG"] == True]
            if not prereq.empty:
                p_df = prereq[_base_cols].head(100).copy()
                p_df["Issue_Type"] = "MISSING_PREREQUISITE"
                p_df["Issue_Description"] = "Skill level progression has gaps (e.g., L4 without L2)"
                issues_frames.append(p_df)

        # Name mismatches (Pass 1 matched by ID but names don't match)
        if "Match_Method" in unified_df.columns:
            name_conflicts = unified_df[unified_df["Match_Method"].str.contains("NAME_CONFLICT|NAME_MISMATCH", na=False)]
            if not name_conflicts.empty:
                n_df = name_conflicts[_base_cols].head(100).copy()
                n_df["Issue_Type"] = "NAME_MISMATCH"
                n_df["Issue_Description"] = "Star ID matched but names differ between training and roster"
                issues_frames.append(n_df)

        if issues_frames:
            issues_df = pd.concat(issues_frames, ignore_index=True)

            # ── Local filters ────────────────────────────────────────────────
            st.markdown(
                "<div style='background:#f3f3f5; border-radius:8px; padding:12px 16px; margin-bottom:12px;'>"
                "<span style='font-size:0.82rem; font-weight:600; color:#717182;'>FILTER DATA QUALITY TABLE</span>"
                "</div>",
                unsafe_allow_html=True,
            )

            # Row 1: Issue Type | Zone | State
            dq_r1c1, dq_r1c2, dq_r1c3 = st.columns(3)

            all_issue_types = sorted(issues_df["Issue_Type"].unique().tolist())
            sel_issue_types = dq_r1c1.multiselect(
                "Issue Type", all_issue_types, default=[], key="dq_filter_issue_type"
            )

            all_zones = sorted(issues_df["Zone"].dropna().unique().tolist()) \
                if "Zone" in issues_df.columns else []
            sel_zones_dq = dq_r1c2.multiselect(
                "Zone", all_zones, default=[], key="dq_filter_zone"
            )

            # States cascade from selected zones if any
            if sel_zones_dq and "Zone" in issues_df.columns and "State" in issues_df.columns:
                available_states = sorted(
                    issues_df[issues_df["Zone"].isin(sel_zones_dq)]["State"].dropna().unique().tolist()
                )
            else:
                available_states = sorted(issues_df["State"].dropna().unique().tolist()) \
                    if "State" in issues_df.columns else []
            sel_states_dq = dq_r1c3.multiselect(
                "State", available_states, default=[], key="dq_filter_state"
            )

            # Row 2: Dealer Code | Name search
            dq_r2c1, dq_r2c2, _ = st.columns([2, 3, 2])

            all_dealers = sorted(issues_df["Dealer Code"].dropna().unique().tolist()) \
                if "Dealer Code" in issues_df.columns else []
            sel_dealers_dq = dq_r2c1.multiselect(
                "Dealer Code", all_dealers, default=[], key="dq_filter_dealer"
            )

            name_search = dq_r2c2.text_input(
                "Search by Name", value="", placeholder="Type a name to filter...",
                key="dq_filter_name"
            )

            # Apply local filters
            filtered_issues = issues_df.copy()
            if sel_issue_types:
                filtered_issues = filtered_issues[filtered_issues["Issue_Type"].isin(sel_issue_types)]
            if sel_zones_dq and "Zone" in filtered_issues.columns:
                filtered_issues = filtered_issues[filtered_issues["Zone"].isin(sel_zones_dq)]
            if sel_states_dq and "State" in filtered_issues.columns:
                filtered_issues = filtered_issues[filtered_issues["State"].isin(sel_states_dq)]
            if sel_dealers_dq and "Dealer Code" in filtered_issues.columns:
                filtered_issues = filtered_issues[filtered_issues["Dealer Code"].isin(sel_dealers_dq)]
            if name_search.strip():
                filtered_issues = filtered_issues[
                    filtered_issues["Name"].astype(str).str.contains(
                        name_search.strip(), case=False, na=False
                    )
                ]

            any_filter_active = bool(
                sel_issue_types or sel_zones_dq or sel_states_dq or sel_dealers_dq or name_search.strip()
            )
            total_issues = len(issues_df)
            shown_issues = len(filtered_issues)

            count_col, export_col = st.columns([6, 2])
            with count_col:
                st.markdown(
                    f"**{shown_issues:,}** of **{total_issues:,}** data quality issues shown"
                    + (f" &nbsp;·&nbsp; <span style='color:{NEUTRAL['danger']};'>filters active</span>"
                       if any_filter_active else ""),
                    unsafe_allow_html=True,
                )
            with export_col:
                _buf = io.BytesIO()
                filtered_issues.to_excel(_buf, index=False, engine="xlsxwriter")
                _buf.seek(0)
                st.download_button(
                    "Export Table",
                    data=_buf,
                    file_name="MAHINDRA_DATA_QUALITY_ISSUES.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dq_export_btn",
                )

            st.dataframe(filtered_issues, height=350, use_container_width=True)
        else:
            st.success("No data quality issues detected.")
    else:
        st.info("No data loaded.")



