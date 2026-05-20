"""
Skill Tab — Skill distribution, regression table, uplift heatmap.
"""
import streamlit as st
import pandas as pd
from config.constants import BRAND_RED, BRAND_CHARCOAL, SKILL_SCORE_MAP
from utils.formatting_utils import style_kpi_card
from analytics.skill_analytics import regression_cases

def render_skill(unified_df, filters):
    """Render the Skill Analytics tab."""
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

    # Compute scores if not present
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

    # ── Skill Score Explanation ──────────────────────────────────────────────
    st.markdown("""
    ### ℹ️ About Skill Scoring
    The Skill Score measures the technical proficiency of our manpower on a **0 to 5 scale**:
    * **0**: Unrated / Entry Level
    * **1-2 (L1/L2)**: Basic to Intermediate
    * **3-4 (L3/L4)**: Advanced Specialist
    * **5 (L5)**: Master / Expert
    
    **Formula:** The uplift is calculated as the simple average of `Post-Training Score - Pre-Training Score` for all *trained* individuals. Untrained individuals are excluded from these metrics.
    """)

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
