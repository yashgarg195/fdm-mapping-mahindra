"""
Audit Tab — Mapping confidence, duplicate log, unresolved queue, data quality.
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
            st.plotly_chart(fig, key="conf_pie", use_container_width=True)

        with chart2:
            st.dataframe(conf_counts, use_container_width=True, height=200)
    else:
        st.info("No confidence data available.")

    # ── Duplicate Log ───────────────────────────────────────────────────────
    st.markdown("#### Duplicate Log")
    if duplicate_df is not None and not duplicate_df.empty:
        st.markdown(f"**{len(duplicate_df)} duplicate records detected** (flagged, not deleted)")
        display_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name",
                        "DATA_QUALITY_STATUS", "DATA_QUALITY_REASON"] if c in duplicate_df.columns]
        st.dataframe(duplicate_df[display_cols] if display_cols else duplicate_df, use_container_width=True, height=300)
    else:
        st.success("No duplicate records detected.")

    # ── Unresolved Queue ────────────────────────────────────────────────────
    st.markdown("#### Unresolved Identity Queue (PENDING_MAPPING_REVIEW)")
    if unresolved_df is not None and not unresolved_df.empty:
        st.markdown(f"**{len(unresolved_df)} unresolved records** — excluded from official KPIs")
        display_cols = [c for c in ["Star ID", "Name", "Designation", "Dealer Code",
                        "Dealer Name", "Match_Method", "Fuzzy_Score", "Phonetic_Score"]
                        if c in unresolved_df.columns]
        st.dataframe(unresolved_df[display_cols] if display_cols else unresolved_df, use_container_width=True, height=300)
    else:
        st.success("No unresolved records. All identities mapped.")

    # ── Data Quality Issues ─────────────────────────────────────────────────
    st.markdown("#### Data Quality Issues")
    if unified_df is not None and not unified_df.empty:
        issues = []

        # Future dates
        if "FUTURE_JOINING_FLAG" in unified_df.columns:
            future = unified_df[unified_df["FUTURE_JOINING_FLAG"] == True]
            for _, row in future.iterrows():
                issues.append({
                    "Star ID": row.get("Star ID", ""),
                    "Name": row.get("Name", ""),
                    "Dealer Code": row.get("Dealer Code", ""),
                    "Issue_Type": "FUTURE_DATE",
                    "Issue_Description": f"Joining Date in future: {row.get('Joining Date', '')}",
                })

        # Skill regressions
        if "SKILL_REGRESSION_FLAG" in unified_df.columns:
            regressions = unified_df[unified_df["SKILL_REGRESSION_FLAG"] == True]
            for _, row in regressions.iterrows():
                issues.append({
                    "Star ID": row.get("Star ID", ""),
                    "Name": row.get("Name", ""),
                    "Dealer Code": row.get("Dealer Code", ""),
                    "Issue_Type": "SKILL_REGRESSION",
                    "Issue_Description": f"Post ({row.get('SKILL LEVEL - POST', '')}) < Pre ({row.get('SKILL LEVEL - PRE', '')})",
                })

        # Missing names
        missing_name = unified_df[unified_df["Name"].isna() | (unified_df["Name"].astype(str).str.strip() == "")]
        for _, row in missing_name.head(50).iterrows():
            issues.append({
                "Star ID": row.get("Star ID", ""),
                "Name": "",
                "Dealer Code": row.get("Dealer Code", ""),
                "Issue_Type": "MISSING_NAME",
                "Issue_Description": "Employee name is missing",
            })

        if issues:
            issues_df = pd.DataFrame(issues)
            st.markdown(f"**{len(issues_df)} data quality issues found**")
            st.dataframe(issues_df, use_container_width=True, height=300)
        else:
            st.success("No data quality issues detected.")
    else:
        st.info("No data loaded.")
