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


def l_level_breakdown(unified_df):
    """Return stacked L-level counts per FY for All-India chart.
    Columns: FY, L1, L2, L3, L4, Untrained.
    """
    cols = ["FY", "L1", "L2", "L3", "L4", "Untrained"]
    if unified_df is None or unified_df.empty or "Training year" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df.copy()
    has_post = "SKILL LEVEL - POST" in df.columns
    has_sid = "Star ID" in df.columns
    rows = []
    for fy, group in df.groupby("Training year"):
        if not has_post:
            rows.append({"FY": fy, "L1": 0, "L2": 0, "L3": 0, "L4": 0, "Untrained": len(group)})
            continue
        counts = group["SKILL LEVEL - POST"].value_counts().to_dict()
        rows.append({
            "FY": fy,
            "L1": counts.get("L1", 0),
            "L2": counts.get("L2", 0),
            "L3": counts.get("L3", 0),
            "L4": counts.get("L4", 0),
            "Untrained": counts.get("NO TEST", 0) + counts.get("0", 0),
        })
    result = pd.DataFrame(rows, columns=cols)
    return result.sort_values("FY")


def zone_breakdown(unified_df):
    """Zone-wise breakdown: trained, untrained, pending, and L1-L4 counts."""
    cols = ["Zone", "Total", "Trained", "Untrained", "Pending", "L1", "L2", "L3", "L4"]
    if unified_df is None or unified_df.empty or "Zone" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df.copy()
    has_sid = "Star ID" in df.columns
    has_post = "SKILL LEVEL - POST" in df.columns
    has_status = "Training_Status" in df.columns
    rows = []
    for zone, group in df.groupby("Zone"):
        total = group["Star ID"].nunique() if has_sid else len(group)
        trained = group[group["Training year"].notna()]["Star ID"].nunique() \
            if has_sid and "Training year" in group.columns else 0
        untrained = total - trained
        pending = group[group["Training_Status"].isin(["PENDING", "ELIGIBLE"])]["Star ID"].nunique() \
            if has_sid and has_status else 0
        level_counts = group["SKILL LEVEL - POST"].value_counts().to_dict() if has_post else {}
        rows.append({
            "Zone": zone, "Total": total, "Trained": trained, "Untrained": untrained, "Pending": pending,
            "L1": level_counts.get("L1", 0), "L2": level_counts.get("L2", 0),
            "L3": level_counts.get("L3", 0), "L4": level_counts.get("L4", 0),
        })
    return pd.DataFrame(rows, columns=cols)


def state_coverage_top(unified_df, n=10):
    """Top N states by training coverage percentage."""
    cols = ["State", "Total", "Trained", "Coverage_Pct"]
    if unified_df is None or unified_df.empty or "State" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df.copy()
    has_sid = "Star ID" in df.columns
    rows = []
    for state, group in df.groupby("State"):
        total = group["Star ID"].nunique() if has_sid else len(group)
        trained = group[group["Training year"].notna()]["Star ID"].nunique() \
            if has_sid and "Training year" in group.columns else 0
        pct = round(trained / max(total, 1) * 100, 1)
        rows.append({"State": state, "Total": total, "Trained": trained, "Coverage_Pct": pct})
    result = pd.DataFrame(rows, columns=cols)
    return result.sort_values("Coverage_Pct", ascending=False).head(n)
