"""
Audit Tab — Mapping confidence, duplicate log, unresolved queue, data quality.
Fixed: Vectorized operations instead of row-by-row iteration for speed.
Accurate data quality detection for future dates, regressions, and missing names.
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
        st.success("No duplicate records detected.")

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

    # ── Data Quality Issues (VECTORIZED — no row iteration) ─────────────────
    st.markdown("#### Data Quality Issues")
    if unified_df is not None and not unified_df.empty:
        issues_frames = []

        # Future dates — vectorized
        if "FUTURE_JOINING_FLAG" in unified_df.columns:
            future = unified_df[unified_df["FUTURE_JOINING_FLAG"] == True]
            if not future.empty:
                f_df = future[["Star ID", "Name", "Dealer Code"]].copy()
                f_df["Issue_Type"] = "FUTURE_DATE"
                f_df["Issue_Description"] = "Joining Date is in the future"
                issues_frames.append(f_df)

        # Skill regressions — vectorized
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

        # Missing names — vectorized
        if "Name" in unified_df.columns:
            missing_name = unified_df[
                unified_df["Name"].isna() | (unified_df["Name"].astype(str).str.strip() == "")
            ]
            if not missing_name.empty:
                m_df = missing_name[["Star ID", "Name", "Dealer Code"]].head(50).copy()
                m_df["Issue_Type"] = "MISSING_NAME"
                m_df["Issue_Description"] = "Employee name is missing"
                issues_frames.append(m_df)

        if issues_frames:
            issues_df = pd.concat(issues_frames, ignore_index=True)
            st.markdown(f"**{len(issues_df)} data quality issues found**")
            st.dataframe(issues_df, height=300)
        else:
            st.success("No data quality issues detected.")
    else:
        st.info("No data loaded.")
