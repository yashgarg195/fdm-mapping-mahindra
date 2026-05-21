"""
Skill Tab — neutral KPI and exception-table view.
"""
import io

import pandas as pd
import streamlit as st

from analytics.skill_analytics import regression_cases
from config.constants import COMPANY_SCALE_MAP, SKILL_SCORE_MAP
from ui.theme import callout, kpi_card, section_header


def _to_company(internal_score):
    """Convert internal 0-4 score to company 1-5 scale."""
    if pd.isna(internal_score) or internal_score < 0:
        return None
    return COMPANY_SCALE_MAP.get(int(internal_score), None)


def _fmt_company(val):
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val:.2f} / 5"


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


def render_skill(unified_df, filters):
    """Render the Skill Analytics tab with trained-person denominator only."""
    st.markdown(
        section_header(
            "Skill Analytics",
            "Score movement and exceptions for employees with valid training activity.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        callout(
            "Skill Score Calculation",
            "Scores are shown on a 0-5 scale. Only trained individuals are included in the score denominator; untrained employees are excluded so the average reflects actual training outcomes.",
            "info",
        ),
        unsafe_allow_html=True,
    )

    if unified_df is None or unified_df.empty:
        st.info("No data available for skill analytics.")
        return

    df = unified_df.copy()
    if "Training_Status" in df.columns:
        df = df[~df["Training_Status"].isin(["NOT_TRAINED", "ELIGIBLE"])]

    if df.empty:
        st.info("No trained manpower data available for skill analytics.")
        return

    if "pre_score" not in df.columns:
        df["pre_score"] = (
            df.get("SKILL LEVEL - PRE", pd.Series(dtype="object"))
            .map(SKILL_SCORE_MAP)
            .fillna(-1)
            .astype(int)
        )
    if "post_score" not in df.columns:
        df["post_score"] = (
            df.get("SKILL LEVEL - POST", pd.Series(dtype="object"))
            .map(SKILL_SCORE_MAP)
            .fillna(-1)
            .astype(int)
        )

    df["pre_company"] = df["pre_score"].apply(_to_company)
    df["post_company"] = df["post_score"].apply(_to_company)

    valid_pre = df["pre_company"].dropna()
    valid_post = df["post_company"].dropna()
    avg_pre = valid_pre.mean() if not valid_pre.empty else 0
    avg_post = valid_post.mean() if not valid_post.empty else 0
    gain = avg_post - avg_pre if avg_pre and avg_post else 0

    trained = df[df["Training year"].notna()] if "Training year" in df.columns else df.copy()
    non_improving = trained[
        (trained["pre_score"] >= 0)
        & (trained["post_score"] >= 0)
        & (trained["post_score"] == trained["pre_score"])
    ]
    reg = regression_cases(df)

    cols = st.columns(5)
    cards = [
        ("Trained Records", f"{len(df):,}", "Included in denominator", "accent"),
        ("Avg Pre Score", _fmt_company(avg_pre), "Before training", "info"),
        ("Avg Post Score", _fmt_company(avg_post), "After training", "trained"),
        ("Avg Improvement", f"{gain:+.2f}", "Post minus pre", "success" if gain >= 0 else "warning"),
        ("Regression Cases", f"{len(reg):,}", "Post score lower than pre", "danger" if len(reg) else "accent"),
    ]
    for col, card in zip(cols, cards):
        with col:
            st.markdown(kpi_card(*card), unsafe_allow_html=True)

    st.markdown(
        section_header(
            "Skill Regression Cases",
            "Employees whose post-training score is lower than their pre-training score.",
        ),
        unsafe_allow_html=True,
    )
    if not reg.empty:
        label_col, btn_col = st.columns([6, 2])
        with label_col:
            st.markdown(f"**{len(reg):,} records** require review.")
        with btn_col:
            _export_table(reg, "MAHINDRA_SKILL_REGRESSIONS.xlsx", "skill_reg_export")
        st.dataframe(reg, height=320, use_container_width=True)
    else:
        st.success("No skill regressions detected.")

    st.markdown(
        section_header(
            "Non-Improving Trained Manpower",
            "Employees who attended training but show no recorded score improvement.",
        ),
        unsafe_allow_html=True,
    )
    if not non_improving.empty:
        label_col, btn_col = st.columns([6, 2])
        with label_col:
            st.markdown(f"**{len(non_improving):,} employees** attended training with no skill change.")
        with btn_col:
            _export_table(non_improving, "MAHINDRA_NON_IMPROVING.xlsx", "skill_ni_export")
        st.dataframe(non_improving, height=320, use_container_width=True)
    else:
        st.success("No non-improving trained manpower detected.")
