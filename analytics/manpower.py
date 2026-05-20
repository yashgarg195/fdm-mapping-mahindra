"""
Manpower Analytics — State/zone/region manpower tables and unique counts.
"""
import pandas as pd


def state_manpower_table(unified_df):
    """State-wise manpower breakdown table."""
    cols = ["State", "Total_Employees", "Trained_Count", "Untrained_Count", "Trained_Pct", "Pending_Count"]
    if unified_df is None or unified_df.empty or "State" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df
    has_sid = "Star ID" in df.columns
    rows = []
    for state, group in df.groupby("State"):
        total = group["Star ID"].nunique() if has_sid else len(group)
        trained = group[group.get("Training year", pd.Series()).notna()]["Star ID"].nunique() if has_sid and "Training year" in group.columns else 0
        untrained = total - trained
        pct = round(trained / max(total, 1) * 100, 1)
        pending = group[group.get("Training_Status", pd.Series(dtype=str)).isin(["PENDING", "ELIGIBLE"])]["Star ID"].nunique() if has_sid and "Training_Status" in group.columns else 0
        rows.append({"State": state, "Total_Employees": total, "Trained_Count": trained, "Untrained_Count": untrained, "Trained_Pct": pct, "Pending_Count": pending})
    return pd.DataFrame(rows)


def zone_manpower_table(unified_df):
    """Zone-wise manpower breakdown table."""
    cols = ["Zone", "Total_Employees", "Trained_Count", "Untrained_Count", "Trained_Pct", "Pending_Count"]
    if unified_df is None or unified_df.empty or "Zone" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df
    has_sid = "Star ID" in df.columns
    rows = []
    for zone, group in df.groupby("Zone"):
        total = group["Star ID"].nunique() if has_sid else len(group)
        trained = group[group.get("Training year", pd.Series()).notna()]["Star ID"].nunique() if has_sid and "Training year" in group.columns else 0
        untrained = total - trained
        pct = round(trained / max(total, 1) * 100, 1)
        pending = group[group.get("Training_Status", pd.Series(dtype=str)).isin(["PENDING", "ELIGIBLE"])]["Star ID"].nunique() if has_sid and "Training_Status" in group.columns else 0
        rows.append({"Zone": zone, "Total_Employees": total, "Trained_Count": trained, "Untrained_Count": untrained, "Trained_Pct": pct, "Pending_Count": pending})
    return pd.DataFrame(rows)


def unique_manpower_count(unified_df):
    """Count of unique employees (unique Star IDs)."""
    if unified_df is None or unified_df.empty:
        return 0
    if "Star ID" in unified_df.columns:
        return unified_df["Star ID"].nunique()
    return len(unified_df)
