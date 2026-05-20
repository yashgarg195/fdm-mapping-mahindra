"""
KPI Engine — Computes all key performance indicators from the unified dataset.
FIXED: Proper pending count (only PENDING+ELIGIBLE), no inflation from NOT_TRAINED.
"""
import pandas as pd
import numpy as np
from config.constants import SKILL_SCORE_MAP, CONFIDENCE_ORDER
from config.settings import (
    INCLUDE_LOW_IN_KPIS, INCLUDE_FUZZY_IN_KPIS,
    MIN_L3_L4_PER_DEALERSHIP,
)


def compute_all_kpis(unified_df):
    """Compute all KPIs from the unified master DataFrame.
    FIXED: Pending count only includes PENDING + ELIGIBLE (not NOT_TRAINED).
    """
    kpis = {
        "unique_trained_manpower": 0,
        "total_manpower": 0,
        "pending_count": 0,
        "coverage_pct": 0.0,
        "l3_l4_specialist_count": 0,
        "avg_skill_score": 0.0,
        "regression_count": 0,
        "unresolved_mapping_count": 0,
        "dealerships_at_risk_count": 0,
        "future_date_flag_count": 0,
        "total_training_records": 0,
        "confidence_distribution": {c: 0 for c in CONFIDENCE_ORDER},
        "completed_count": 0,
        "attended_count": 0,
        "not_trained_count": 0,
        "cross_id_suspect_count": 0,
    }

    if unified_df is None or unified_df.empty:
        return kpis

    df = unified_df.copy()

    # Total unique manpower
    if "Star ID" in df.columns:
        kpis["total_manpower"] = df["Star ID"].nunique()
    else:
        kpis["total_manpower"] = len(df)

    # Determine which confidence levels to include in KPIs
    included_conf = {"HIGH", "MEDIUM"}
    if INCLUDE_LOW_IN_KPIS:
        included_conf.add("LOW")
    if INCLUDE_FUZZY_IN_KPIS:
        included_conf.add("FUZZY")

    conf_col = "Match_Confidence"
    if conf_col in df.columns:
        df_kpi = df[df[conf_col].isin(included_conf)]
    else:
        df_kpi = df

    # Unique trained manpower (has a Training year value)
    has_training = df_kpi["Training year"].notna() if "Training year" in df_kpi.columns else pd.Series(False, index=df_kpi.index)
    if "Star ID" in df_kpi.columns:
        kpis["unique_trained_manpower"] = df_kpi.loc[has_training, "Star ID"].nunique()
    else:
        kpis["unique_trained_manpower"] = has_training.sum()

    # Coverage percentage
    if kpis["total_manpower"] > 0:
        kpis["coverage_pct"] = round(
            kpis["unique_trained_manpower"] / kpis["total_manpower"] * 100, 1
        )

    # Training status breakdowns (FIXED: separate counts)
    if "Training_Status" in df.columns:
        status_counts = df["Training_Status"].value_counts().to_dict()
        # Pending = only PENDING (trained before, needs refresher) + ELIGIBLE (technical, never trained)
        kpis["pending_count"] = status_counts.get("PENDING", 0) + status_counts.get("ELIGIBLE", 0)
        kpis["completed_count"] = status_counts.get("COMPLETED", 0)
        kpis["attended_count"] = status_counts.get("ATTENDED", 0)
        kpis["not_trained_count"] = status_counts.get("NOT_TRAINED", 0)
    else:
        if "Match_Method" in df.columns:
            kpis["pending_count"] = (df["Match_Method"] == "ROSTER_ONLY").sum()

    # L3/L4 specialists
    if "SKILL LEVEL - POST" in df_kpi.columns:
        kpis["l3_l4_specialist_count"] = df_kpi[
            df_kpi["SKILL LEVEL - POST"].isin(["L3", "L4"])
        ]["Star ID"].nunique() if "Star ID" in df_kpi.columns else 0

    # Average skill score (exclude NO TEST / -1)
    if "post_score" in df_kpi.columns:
        valid_scores = df_kpi["post_score"][df_kpi["post_score"] >= 0]
        if not valid_scores.empty:
            kpis["avg_skill_score"] = round(valid_scores.mean(), 2)

    # Regression count
    if "SKILL_REGRESSION_FLAG" in df.columns:
        kpis["regression_count"] = int(df["SKILL_REGRESSION_FLAG"].sum())

    # Unresolved mapping count
    if conf_col in df.columns:
        kpis["unresolved_mapping_count"] = (df[conf_col] == "UNRESOLVED").sum()

    # Dealerships at risk (fewer than MIN_L3_L4_PER_DEALERSHIP specialists)
    if "Dealer Code" in df.columns and "post_score" in df.columns:
        dealer_specs = df.groupby("Dealer Code")["post_score"].apply(
            lambda g: (g.astype(int, errors="ignore") >= 3).sum()
        )
        kpis["dealerships_at_risk_count"] = (
            dealer_specs < MIN_L3_L4_PER_DEALERSHIP
        ).sum()

    # Future date flags
    if "FUTURE_JOINING_FLAG" in df.columns:
        kpis["future_date_flag_count"] = int(df["FUTURE_JOINING_FLAG"].sum())

    # Total training records
    if "Training year" in df.columns:
        kpis["total_training_records"] = df["Training year"].notna().sum()

    # Confidence distribution
    if conf_col in df.columns:
        dist = df[conf_col].value_counts().to_dict()
        for c in CONFIDENCE_ORDER:
            kpis["confidence_distribution"][c] = dist.get(c, 0)

    # Cross-ID suspects
    if "CROSS_ID_DUPLICATE_SUSPECT" in df.columns:
        kpis["cross_id_suspect_count"] = int(df["CROSS_ID_DUPLICATE_SUSPECT"].sum())

    return kpis
