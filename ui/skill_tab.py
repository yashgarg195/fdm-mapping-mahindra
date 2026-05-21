"""
Skill Tab — Skill distribution, regression table, uplift heatmap.
FIXED: Scores displayed on company-standard 1–5 scale with visual legend.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config.constants import (
    BRAND_RED, BRAND_CHARCOAL, SKILL_SCORE_MAP,
    COMPANY_SCALE_MAP, COMPANY_SCALE_LABELS, COMPANY_SCALE_COLORS,
)
from utils.formatting_utils import style_kpi_card
from analytics.skill_analytics import skill_distribution, regression_cases, skill_uplift_report


def _to_company(internal_score):
    """Convert internal 0-4 score to company 1-5 scale."""
    return COMPANY_SCALE_MAP.get(int(internal_score), None) if pd.notna(internal_score) and internal_score >= 0 else None


def _fmt_company(val):
    """Format a company-scale float to a display string like '3.2 / 5'."""
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val:.1f} / 5"


def _render_scale_legend():
    """Render the 1-5 company scale visual legend as an HTML bar."""
    cells = ""
    for score in range(1, 6):
        label, desc = COMPANY_SCALE_LABELS[score]
        color = COMPANY_SCALE_COLORS[score]
        cells += f"""
        <div style="flex:1; text-align:center; padding:6px 4px; background:{color};
                    color:#231F20; font-size:0.72rem; line-height:1.3;
                    border-right:2px solid white;">
            <div style="font-weight:800; font-size:1.1rem;">{score}</div>
            <div style="font-weight:700;">{label}</div>
            <div style="font-size:0.65rem; opacity:0.85;">{desc}</div>
        </div>"""
    return f"""
    <div style="display:flex; border-radius:8px; overflow:hidden;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); margin:12px 0 18px 0;">
        {cells}
    </div>"""


def render_skill(unified_df, filters):
    """Render the Skill Analytics tab with company 1-5 scale."""
    if unified_df is None or unified_df.empty:
        st.info("No data available for skill analytics.")
        return

    df = unified_df.copy()

    # Compute internal scores if not present
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

    # Convert to company 1-5 scale
    df["pre_company"] = df["pre_score"].apply(_to_company)
    df["post_company"] = df["post_score"].apply(_to_company)

    # ── Scale Legend ─────────────────────────────────────────────────────────
    st.markdown("#### Mahindra Skill Rating Scale (1–5)")
    st.markdown(_render_scale_legend(), unsafe_allow_html=True)

    # ── KPI Cards (company scale) ────────────────────────────────────────────
    valid_pre = df["pre_company"].dropna()
    valid_post = df["post_company"].dropna()
    avg_pre = valid_pre.mean() if not valid_pre.empty else 0
    avg_post = valid_post.mean() if not valid_post.empty else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(style_kpi_card(
            "AVG PRE-TRAINING",
            _fmt_company(avg_pre),
            "COMPANY SCALE (1-5)",
            BRAND_CHARCOAL,
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card(
            "AVG POST-TRAINING",
            _fmt_company(avg_post),
            "COMPANY SCALE (1-5)",
            BRAND_RED,
        ), unsafe_allow_html=True)
    with c3:
        gain = avg_post - avg_pre if avg_pre and avg_post else 0
        sign = "+" if gain >= 0 else ""
        st.markdown(style_kpi_card(
            "SKILL UPLIFT",
            f"{sign}{gain:.2f}",
            "POINTS ON 1-5 SCALE",
            "#69DB7C" if gain >= 0 else "#FF8C00",
        ), unsafe_allow_html=True)

    # ── Skill Distribution Chart (company labels) ───────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Post-Training Skill Distribution")
        if "SKILL LEVEL - POST" in df.columns:
            # Build distribution with company labels
            dist_data = []
            level_order = ["0", "L1", "L2", "L3", "L4", "NO TEST"]
            for level in level_order:
                count = (df["SKILL LEVEL - POST"] == level).sum()
                if count > 0:
                    internal = SKILL_SCORE_MAP.get(level, -1)
                    company = COMPANY_SCALE_MAP.get(internal, None)
                    if company:
                        label_name, _ = COMPANY_SCALE_LABELS[company]
                        dist_data.append({
                            "Rating": f"{company}/5 — {label_name}",
                            "Count": count,
                            "Sort": company,
                            "Color": COMPANY_SCALE_COLORS[company],
                        })
                    else:
                        dist_data.append({
                            "Rating": "N/A (No Test)",
                            "Count": count,
                            "Sort": 0,
                            "Color": "#CCCCCC",
                        })

            if dist_data:
                dist_df = pd.DataFrame(dist_data).sort_values("Sort")
                fig = px.bar(
                    dist_df, x="Rating", y="Count",
                    color="Rating",
                    color_discrete_map={r["Rating"]: r["Color"] for _, r in dist_df.iterrows()},
                )
                fig.update_layout(
                    plot_bgcolor="white",
                    margin=dict(t=20, b=60, l=20, r=20),
                    showlegend=False,
                    xaxis_title="Skill Rating (Company Scale)",
                    yaxis_title="Employee Count",
                )
                st.plotly_chart(fig, key="skill_dist_chart")
            else:
                st.info("No skill distribution data.")
        else:
            st.info("No skill distribution data.")

    with chart2:
        st.markdown("#### Skill Uplift Heatmap (Dealer x FY)")
        uplift = skill_uplift_report(df)
        if not uplift.empty and len(uplift) > 1:
            try:
                # Convert uplift averages to company scale
                uplift["Avg_Uplift_Company"] = uplift["Avg_Uplift"].apply(lambda x: x)  # delta stays same
                pivot = uplift.pivot_table(
                    index="Dealer_Name", columns="FY",
                    values="Avg_Uplift", aggfunc="mean"
                ).fillna(0)
                if not pivot.empty:
                    fig = px.imshow(
                        pivot.values,
                        x=list(pivot.columns),
                        y=list(pivot.index),
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
    st.markdown("#### :warning: Skill Regression Cases")
    reg = regression_cases(df)
    if not reg.empty:
        st.markdown(f"**{len(reg)} records** where post-training score dropped below pre-training score")
        st.dataframe(reg, height=300)
    else:
        st.success("No skill regressions detected.")

    # ── Non-improving count ─────────────────────────────────────────────────
    trained = df[df.get("Training year", pd.Series()).notna()]
    non_improving = trained[
        (trained["pre_score"] >= 0) &
        (trained["post_score"] >= 0) &
        (trained["post_score"] == trained["pre_score"])
    ]
    st.markdown(f"**Non-improving manpower:** {len(non_improving)} employees attended training with no skill change.")
