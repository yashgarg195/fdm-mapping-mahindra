"""
Overview Analytics — National summary, FY trends, month-on-month trends.
"""
import pandas as pd
import numpy as np


def national_summary(unified_df):
    """Compute national-level summary statistics."""
    result = {
        "total_employees": 0, "total_trained": 0, "total_untrained": 0,
        "total_pending": 0, "total_dealers": 0, "total_states": 0, "total_zones": 0,
    }
    if unified_df is None or unified_df.empty:
        return result
    df = unified_df
    if "Star ID" in df.columns:
        result["total_employees"] = df["Star ID"].nunique()
    if "Training year" in df.columns:
        trained_ids = df[df["Training year"].notna()]["Star ID"].unique() if "Star ID" in df.columns else []
        result["total_trained"] = len(trained_ids)
    result["total_untrained"] = result["total_employees"] - result["total_trained"]
    if "Training_Status" in df.columns:
        result["total_pending"] = df[df["Training_Status"].isin(["PENDING", "ELIGIBLE"])]["Star ID"].nunique() if "Star ID" in df.columns else 0
    if "Dealer Code" in df.columns:
        result["total_dealers"] = df["Dealer Code"].nunique()
    if "State" in df.columns:
        result["total_states"] = df["State"].nunique()
    if "Zone" in df.columns:
        result["total_zones"] = df["Zone"].nunique()
    return result


def fy_trend(unified_df):
    """Training trend by financial year."""
    if unified_df is None or unified_df.empty or "Training year" not in unified_df.columns:
        return pd.DataFrame(columns=["FY", "Trained_Count", "Unique_Employees", "Coverage_Pct"])
    df = unified_df[unified_df["Training year"].notna()].copy()
    if df.empty:
        return pd.DataFrame(columns=["FY", "Trained_Count", "Unique_Employees", "Coverage_Pct"])
    total_emp = unified_df["Star ID"].nunique() if "Star ID" in unified_df.columns else len(unified_df)
    grouped = df.groupby("Training year").agg(
        Trained_Count=("Star ID", "count"),
        Unique_Employees=("Star ID", "nunique") if "Star ID" in df.columns else ("Star ID", "count"),
    ).reset_index().rename(columns={"Training year": "FY"})
    grouped["Coverage_Pct"] = (grouped["Unique_Employees"] / max(total_emp, 1) * 100).round(1)
    return grouped.sort_values("FY")


def mom_trend(unified_df):
    """Month-on-month training count trend."""
    if unified_df is None or unified_df.empty:
        return pd.DataFrame(columns=["Month", "Training_Count"])
    col = "LAST PRODUCT TRANIING ON"
    if col not in unified_df.columns:
        return pd.DataFrame(columns=["Month", "Training_Count"])
    df = unified_df[unified_df[col].notna()].copy()
    if df.empty:
        return pd.DataFrame(columns=["Month", "Training_Count"])
    try:
        dates = pd.to_datetime(df[col], errors="coerce")
        df["_month"] = dates.dt.to_period("M").astype(str)
        grouped = df.groupby("_month").size().reset_index(name="Training_Count")
        grouped.rename(columns={"_month": "Month"}, inplace=True)
        return grouped.sort_values("Month")
    except Exception:
        return pd.DataFrame(columns=["Month", "Training_Count"])
