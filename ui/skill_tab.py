"""
Skill Tab — Skill distribution, regression table, uplift heatmap.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config.constants import BRAND_RED, BRAND_CHARCOAL, SKILL_SCORE_MAP
from utils.formatting_utils import style_kpi_card
from analytics.skill_analytics import skill_distribution, regression_cases, skill_uplift_report


def render_skill(unified_df, filters):
    """Render the Skill Analytics tab."""
    if unified_df is None or unified_df.empty:
        st.info("No data available for skill analytics.")
        return

    df = unified_df.copy()

    # Compute scores if not present
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

    # ── KPI Cards ───────────────────────────────────────────────────────────
    valid_pre = df[df["pre_score"] >= 0]["pre_score"]
    valid_post = df[df["post_score"] >= 0]["post_score"]
    avg_pre = valid_pre.mean() if not valid_pre.empty else 0
    avg_post = valid_post.mean() if not valid_post.empty else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(style_kpi_card("AVG PRE-TRAINING", f"{avg_pre:.2f}", "SKILL SCORE", BRAND_CHARCOAL), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card("AVG POST-TRAINING", f"{avg_post:.2f}", "SKILL SCORE", BRAND_RED), unsafe_allow_html=True)
    with c3:
        gain = avg_post - avg_pre
        sign = "+" if gain >= 0 else ""
        st.markdown(style_kpi_card("SKILL UPLIFT", f"{sign}{gain:.2f}", "AVG DELTA", "#90EE90" if gain >= 0 else "#FF8C00"), unsafe_allow_html=True)

    # ── Skill Distribution Chart ────────────────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Skill Level Distribution")
        dist = skill_distribution(df)
        if not dist.empty:
            fig = px.bar(
                dist, x="Skill_Level", y="Count",
                color="Skill_Level",
                color_discrete_sequence=[BRAND_CHARCOAL, "#90EE90", "#FFD700", "#FF8C00", BRAND_RED, "#E6E7E8"],
            )
            fig.update_layout(plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig, key="skill_dist_chart")
        else:
            st.info("No skill distribution data.")

    with chart2:
        st.markdown("#### Skill Uplift Heatmap (Dealer × FY)")
        uplift = skill_uplift_report(df)
        if not uplift.empty and len(uplift) > 1:
            try:
                pivot = uplift.pivot_table(index="Dealer_Name", columns="FY", values="Avg_Uplift", aggfunc="mean").fillna(0)
                if not pivot.empty:
                    fig = px.imshow(
                        pivot.values, x=list(pivot.columns), y=list(pivot.index),
                        color_continuous_scale=["#FFCCCC", "#FFFFFF", "#CCFFCC"],
                        aspect="auto",
                    )
                    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig, key="uplift_heatmap")
                else:
                    st.info("Not enough data for heatmap.")
            except Exception:
                st.info("Unable to generate heatmap.")
        else:
            st.info("Not enough data for heatmap.")

    # ── Regression Table ────────────────────────────────────────────────────
    st.markdown("#### ⚠️ Skill Regression Cases")
    reg = regression_cases(df)
    if not reg.empty:
        st.markdown(f"**{len(reg)} records** where post-skill < pre-skill")
        st.dataframe(reg, height=300)
    else:
        st.success("No skill regressions detected.")

    # ── Non-improving count ─────────────────────────────────────────────────
    trained = df[df.get("Training year", pd.Series()).notna()]
    non_improving = trained[(trained["pre_score"] >= 0) & (trained["post_score"] >= 0) & (trained["post_score"] == trained["pre_score"])]
    st.markdown(f"**Non-improving manpower:** {len(non_improving)} employees attended training with no skill change.")
