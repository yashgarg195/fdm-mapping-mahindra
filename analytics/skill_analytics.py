"""
Skill Analytics — Skill distribution, regression detection, uplift reporting.
"""
import pandas as pd
import numpy as np
from config.constants import SKILL_SCORE_MAP


def skill_distribution(unified_df):
    """Compute distribution of post-training skill levels."""
    cols = ["Skill_Level", "Count", "Pct"]
    if unified_df is None or unified_df.empty or "SKILL LEVEL - POST" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    dist = unified_df["SKILL LEVEL - POST"].value_counts().reset_index()
    dist.columns = ["Skill_Level", "Count"]
    total = dist["Count"].sum()
    dist["Pct"] = (dist["Count"] / max(total, 1) * 100).round(1)
    return dist.sort_values("Skill_Level")


def regression_cases(unified_df):
    """Find all training records where post-skill < pre-skill."""
    display_cols = ["Star ID", "Name", "Designation", "Dealer Name",
                    "Training year", "SKILL LEVEL - PRE", "SKILL LEVEL - POST"]
    if unified_df is None or unified_df.empty:
        return pd.DataFrame(columns=display_cols)
    df = unified_df.copy()
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1)
    mask = (df["pre_score"] >= 0) & (df["post_score"] >= 0) & (df["post_score"] < df["pre_score"])
    result = df[mask]
    valid_cols = [c for c in display_cols if c in result.columns]
    return result[valid_cols] if valid_cols else result


def skill_uplift_report(unified_df):
    """Average pre/post skill scores and uplift by dealer and FY."""
    cols = ["Dealer_Code", "Dealer_Name", "FY", "Avg_Pre", "Avg_Post", "Avg_Uplift"]
    if unified_df is None or unified_df.empty:
        return pd.DataFrame(columns=cols)
    df = unified_df.copy()
    if "pre_score" not in df.columns:
        df["pre_score"] = df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1)
    if "post_score" not in df.columns:
        df["post_score"] = df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1)
    # Filter to valid scores
    df = df[(df["pre_score"] >= 0) & (df["post_score"] >= 0)]
    if df.empty or "Dealer Code" not in df.columns or "Training year" not in df.columns:
        return pd.DataFrame(columns=cols)
    grouped = df.groupby(["Dealer Code", "Training year"]).agg(
        Avg_Pre=("pre_score", "mean"),
        Avg_Post=("post_score", "mean"),
    ).reset_index()
    grouped["Avg_Uplift"] = (grouped["Avg_Post"] - grouped["Avg_Pre"]).round(2)
    grouped["Avg_Pre"] = grouped["Avg_Pre"].round(2)
    grouped["Avg_Post"] = grouped["Avg_Post"].round(2)
    grouped.rename(columns={"Dealer Code": "Dealer_Code", "Training year": "FY"}, inplace=True)
    # Add dealer name
    if "Dealer Name" in unified_df.columns:
        dn = unified_df[["Dealer Code", "Dealer Name"]].drop_duplicates()
        dn.rename(columns={"Dealer Code": "Dealer_Code", "Dealer Name": "Dealer_Name"}, inplace=True)
        grouped = grouped.merge(dn, on="Dealer_Code", how="left")
    else:
        grouped["Dealer_Name"] = ""
    return grouped[cols]
