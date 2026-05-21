"""
Skill Tab — Skill distribution, regression table, uplift heatmap.
Scores displayed on company-standard 1–5 scale with visual legend.
"""
import streamlit as st
import pandas as pd
from config.constants import (
    BRAND_RED, BRAND_CHARCOAL, SKILL_SCORE_MAP,
    COMPANY_SCALE_MAP, COMPANY_SCALE_LABELS, COMPANY_SCALE_COLORS,
)
from utils.formatting_utils import style_kpi_card
from analytics.skill_analytics import regression_cases


def _to_company(internal_score):
    """Convert internal 0-4 score to company 1-5 scale."""
    return COMPANY_SCALE_MAP.get(int(internal_score), None) if pd.notna(internal_score) and internal_score >= 0 else None


def _fmt_company(val):
    """Format a company-scale value as a 1-10 display string.
    The underlying company scale is 1-5; we simply double for display only.
    """
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val * 2:.1f} / 10"


def _render_scale_legend():
    """Render the skill scale visual legend. Displayed on a 1-10 scale
    (values 2, 4, 6, 8, 10) by doubling the internal 1-5 company scale.
    """
    return """
    <div style="display:flex; border-radius:8px; overflow:hidden;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); margin:12px 0 18px 0;">
        <div style="flex:1; text-align:center; padding:6px 4px; background:#FF6B6B;
                    color:#231F20; font-size:0.72rem; line-height:1.3;
                    border-right:2px solid white;">
            <div style="font-weight:800; font-size:1.1rem;">2</div>
            <div style="font-weight:700;">Beginner</div>
            <div style="font-size:0.65rem; opacity:0.85;">No formal training or untested — needs onboarding</div>
        </div>
        <div style="flex:1; text-align:center; padding:6px 4px; background:#FFA94D;
                    color:#231F20; font-size:0.72rem; line-height:1.3;
                    border-right:2px solid white;">
            <div style="font-weight:800; font-size:1.1rem;">4</div>
            <div style="font-weight:700;">Basic</div>
            <div style="font-size:0.65rem; opacity:0.85;">Completed L1 — can assist under supervision</div>
        </div>
        <div style="flex:1; text-align:center; padding:6px 4px; background:#FFD43B;
                    color:#231F20; font-size:0.72rem; line-height:1.3;
                    border-right:2px solid white;">
            <div style="font-weight:800; font-size:1.1rem;">6</div>
            <div style="font-weight:700;">Intermediate</div>
            <div style="font-size:0.65rem; opacity:0.85;">Completed L2 — can handle routine tasks independently</div>
        </div>
        <div style="flex:1; text-align:center; padding:6px 4px; background:#69DB7C;
                    color:#231F20; font-size:0.72rem; line-height:1.3;
                    border-right:2px solid white;">
            <div style="font-weight:800; font-size:1.1rem;">8</div>
            <div style="font-weight:700;">Advanced</div>
            <div style="font-size:0.65rem; opacity:0.85;">Completed L3 — can troubleshoot and mentor juniors</div>
        </div>
        <div style="flex:1; text-align:center; padding:6px 4px; background:#228BE6;
                    color:#231F20; font-size:0.72rem; line-height:1.3;">
            <div style="font-weight:800; font-size:1.1rem;">10</div>
            <div style="font-weight:700;">Expert</div>
            <div style="font-size:0.65rem; opacity:0.85;">Completed L4 — certified specialist, can lead audits</div>
        </div>
    </div>"""


def render_skill(unified_df, filters):
    """Render the Skill Analytics tab with company 1-5 scale."""
    if unified_df is None or unified_df.empty:
        st.info("No data available for skill analytics.")
        return

    df = unified_df.copy()

    # Exclude untrained individuals from skill calculations
    if "Training_Status" in df.columns:
        df = df[~df["Training_Status"].isin(["NOT_TRAINED", "ELIGIBLE"])]

    if df.empty:
        st.info("No trained manpower data available for skill analytics.")
        return

    # Compute internal scores if not present
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

    # Convert to company 1-5 scale
    df["pre_company"] = df["pre_score"].apply(_to_company)
    df["post_company"] = df["post_score"].apply(_to_company)

    # ── Scale Legend ─────────────────────────────────────────────────────────
    st.markdown("#### Mahindra Skill Rating Scale (1–10)")
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
            "COMPANY SCALE (1-10)",
            BRAND_CHARCOAL,
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(style_kpi_card(
            "AVG POST-TRAINING",
            _fmt_company(avg_post),
            "COMPANY SCALE (1-10)",
            BRAND_RED,
        ), unsafe_allow_html=True)
    with c3:
        # Uplift is also doubled for display consistency
        gain = avg_post - avg_pre if avg_pre and avg_post else 0
        gain_display = gain * 2
        sign = "+" if gain_display >= 0 else ""
        st.markdown(style_kpi_card(
            "SKILL UPLIFT",
            f"{sign}{gain_display:.2f}",
            "POINTS ON 1-10 SCALE",
            "#69DB7C" if gain_display >= 0 else "#FF8C00",
        ), unsafe_allow_html=True)

    # ── Regression Table ────────────────────────────────────────────────────
    st.markdown("#### Skill Regression Cases")
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
