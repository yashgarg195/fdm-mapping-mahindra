"""
Audit Tab — Mapping confidence, duplicate log, unresolved queue,
cross-ID suspects, data quality issues.
FIXED: Shows cross-ID duplicate suspects, training status breakdown,
vectorized operations for speed.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from config.constants import BRAND_RED, BRAND_CHARCOAL, CONFIDENCE_ORDER, CONFIDENCE_COLORS


def render_audit(unified_df, duplicate_df, unresolved_df):
    """Render the Audit & Exceptions tab."""
    # ── Mapping Confidence Distribution ─────────────────────────────────────
    st.markdown("#### Mapping Confidence Distribution")

    if unified_df is not None and not unified_df.empty and "Match_Confidence" in unified_df.columns:
        conf_counts = unified_df["Match_Confidence"].value_counts().reindex(CONFIDENCE_ORDER, fill_value=0).reset_index()
        conf_counts.columns = ["Confidence", "Count"]
        conf_counts["Pct"] = (conf_counts["Count"] / max(conf_counts["Count"].sum(), 1) * 100).round(1)

        chart1, chart2 = st.columns(2)
        with chart1:
            fig = px.pie(
                conf_counts, names="Confidence", values="Count",
                color="Confidence",
                color_discrete_map=CONFIDENCE_COLORS,
                hole=0.4,
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, key="conf_pie")

        with chart2:
            st.dataframe(conf_counts, height=200)

        # Training Status Breakdown
        if "Training_Status" in unified_df.columns:
            st.markdown("#### Training Status Breakdown")
            status_counts = unified_df["Training_Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            status_counts["Pct"] = (status_counts["Count"] / max(status_counts["Count"].sum(), 1) * 100).round(1)
            st.dataframe(status_counts, height=200)
    else:
        st.info("No confidence data available.")

    # ── Duplicate Log ───────────────────────────────────────────────────────
    st.markdown("#### Duplicate Log")
    if duplicate_df is not None and not duplicate_df.empty:
        st.markdown(f"**{len(duplicate_df)} duplicate records detected** (flagged, not deleted)")
        display_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name",
                        "DATA_QUALITY_STATUS", "DATA_QUALITY_REASON"] if c in duplicate_df.columns]
        st.dataframe(duplicate_df[display_cols] if display_cols else duplicate_df, height=300)
    else:
        st.success("No exact duplicate records detected.")

    # ── Suspect Duplicates (Possible Matches) ───────────────────────────────
    st.markdown("#### Suspect Duplicates (Possible Matches)")
    st.markdown(
        "<div style='font-size:0.9rem; color:#555; margin-bottom:15px;'>"
        "<b>What is a Possible Match?</b> A Possible Match occurs when the system identifies two records with different IDs but very similar names (e.g., 'Amit Kumar' and 'Ameet Kumar') working at the same location. These are flagged for your review to ensure they aren't the same person entered twice."
        "</div>", 
        unsafe_allow_html=True
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
            st.markdown(f"**{len(suspects)} suspect duplicate records** — different Star IDs, very similar names at same dealer")
            display_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name",
                            "DATA_QUALITY_STATUS", "DATA_QUALITY_REASON",
                            "CROSS_ID_DUPLICATE_NOTE"] if c in suspects.columns]
            st.dataframe(suspects[display_cols] if display_cols else suspects, height=300)
        else:
            st.success("No possible matches detected.")
    else:
        st.info("No data loaded.")

    # ── Unresolved Queue ────────────────────────────────────────────────────
    st.markdown("#### Unresolved Identity Queue (PENDING_MAPPING_REVIEW)")
    if unresolved_df is not None and not unresolved_df.empty:
        st.markdown(f"**{len(unresolved_df)} unresolved records** — excluded from official KPIs")
        display_cols = [c for c in ["Star ID", "Name", "Designation", "Dealer Code",
                        "Dealer Name", "Match_Method", "Fuzzy_Score", "Phonetic_Score"]
                        if c in unresolved_df.columns]
        st.dataframe(unresolved_df[display_cols] if display_cols else unresolved_df, height=300)
    else:
        st.success("No unresolved records. All identities mapped.")

    # ── Data Quality Issues (with local filters) ─────────────────────────────
    st.markdown("#### Data Quality Issues")
    if unified_df is not None and not unified_df.empty:
        issues_frames = []

        # Future dates
        if "FUTURE_JOINING_FLAG" in unified_df.columns:
            future = unified_df[unified_df["FUTURE_JOINING_FLAG"] == True]
            if not future.empty:
                f_df = future[["Star ID", "Name", "Dealer Code"]].copy()
                f_df["Issue_Type"] = "FUTURE_DATE"
                f_df["Issue_Description"] = "Joining Date is in the future"
                issues_frames.append(f_df)

        # Skill regressions
        if "SKILL_REGRESSION_FLAG" in unified_df.columns:
            regressions = unified_df[unified_df["SKILL_REGRESSION_FLAG"] == True]
            if not regressions.empty:
                r_df = regressions[["Star ID", "Name", "Dealer Code"]].copy()
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
                m_df = missing_name[["Star ID", "Name", "Dealer Code"]].head(50).copy()
                m_df["Issue_Type"] = "MISSING_NAME"
                m_df["Issue_Description"] = "Employee name is missing"
                issues_frames.append(m_df)

        # Missing prerequisite (L4 without L1-L3 progression)
        if "MISSING_PREREQUISITE_FLAG" in unified_df.columns:
            prereq = unified_df[unified_df["MISSING_PREREQUISITE_FLAG"] == True]
            if not prereq.empty:
                p_df = prereq[["Star ID", "Name", "Dealer Code"]].head(100).copy()
                p_df["Issue_Type"] = "MISSING_PREREQUISITE"
                p_df["Issue_Description"] = "Skill level progression has gaps (e.g., L4 without L2)"
                issues_frames.append(p_df)

        # Name mismatches (Pass 1 matched by ID but names don't match)
        if "Match_Method" in unified_df.columns:
            name_conflicts = unified_df[unified_df["Match_Method"].str.contains("NAME_CONFLICT|NAME_MISMATCH", na=False)]
            if not name_conflicts.empty:
                n_df = name_conflicts[["Star ID", "Name", "Dealer Code"]].head(100).copy()
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
            dq_f1, dq_f2, dq_f3 = st.columns([2, 2, 3])

            all_issue_types = sorted(issues_df["Issue_Type"].unique().tolist())
            sel_issue_types = dq_f1.multiselect(
                "Issue Type", all_issue_types, default=[], key="dq_filter_issue_type"
            )

            all_dealers = sorted(issues_df["Dealer Code"].dropna().unique().tolist()) \
                if "Dealer Code" in issues_df.columns else []
            sel_dealers_dq = dq_f2.multiselect(
                "Dealer Code", all_dealers, default=[], key="dq_filter_dealer"
            )

            name_search = dq_f3.text_input(
                "Search by Name", value="", placeholder="Type a name to filter...",
                key="dq_filter_name"
            )

            # Apply local filters
            filtered_issues = issues_df.copy()
            if sel_issue_types:
                filtered_issues = filtered_issues[filtered_issues["Issue_Type"].isin(sel_issue_types)]
            if sel_dealers_dq:
                filtered_issues = filtered_issues[filtered_issues["Dealer Code"].isin(sel_dealers_dq)]
            if name_search.strip():
                filtered_issues = filtered_issues[
                    filtered_issues["Name"].astype(str).str.contains(
                        name_search.strip(), case=False, na=False
                    )
                ]

            total_issues = len(issues_df)
            shown_issues = len(filtered_issues)
            st.markdown(
                f"**{shown_issues:,}** of **{total_issues:,}** data quality issues shown"
                + (" &nbsp;·&nbsp; <span style='color:#d4183d;'>filters active</span>" if (sel_issue_types or sel_dealers_dq or name_search.strip()) else ""),
                unsafe_allow_html=True,
            )
            st.dataframe(filtered_issues, height=350, use_container_width=True)
        else:
            st.success("No data quality issues detected.")
    else:
        st.info("No data loaded.")

