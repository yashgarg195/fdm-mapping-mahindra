"""
Penetration Analytics — Dealership penetration and product readiness.
"""
import pandas as pd
from core.scoring import compute_dealership_readiness


def dealership_penetration(unified_df):
    """Compute training penetration per dealership."""
    cols = ["Dealer_Code", "Dealer_Name", "Zone", "State", "Total_Employees",
            "Trained_Count", "Penetration_Pct", "L3_L4_Count", "Readiness_Score"]
    if unified_df is None or unified_df.empty or "Dealer Code" not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    rows = []
    for dc, group in unified_df.groupby("Dealer Code"):
        total = group["Star ID"].nunique() if "Star ID" in group.columns else len(group)
        trained = group[group["Training year"].notna()]["Star ID"].nunique() if "Star ID" in group.columns and "Training year" in group.columns else 0
        pct = round(trained / max(total, 1) * 100, 1)
        l3_l4 = 0
        if "SKILL LEVEL - POST" in group.columns:
            l3_l4 = group[group["SKILL LEVEL - POST"].isin(["L3", "L4"])]["Star ID"].nunique() if "Star ID" in group.columns else 0
        readiness = compute_dealership_readiness(group)
        rows.append({
            "Dealer_Code": dc,
            "Dealer_Name": group["Dealer Name"].iloc[0] if "Dealer Name" in group.columns else "",
            "Zone": group["Zone"].iloc[0] if "Zone" in group.columns else "",
            "State": group["State"].iloc[0] if "State" in group.columns else "",
            "Total_Employees": total,
            "Trained_Count": trained,
            "Penetration_Pct": pct,
            "L3_L4_Count": l3_l4,
            "Readiness_Score": readiness,
        })
    return pd.DataFrame(rows).sort_values("Penetration_Pct", ascending=False)


def product_readiness(unified_df, product_col="LAST MODEL TRAINED"):
    """Product training readiness report."""
    cols = ["Product", "Trained_Count", "Unique_Employees", "States_Covered"]
    if unified_df is None or unified_df.empty or product_col not in unified_df.columns:
        return pd.DataFrame(columns=cols)
    df = unified_df[unified_df[product_col].notna()].copy()
    if df.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    for product, group in df.groupby(product_col):
        rows.append({
            "Product": product,
            "Trained_Count": len(group),
            "Unique_Employees": group["Star ID"].nunique() if "Star ID" in group.columns else len(group),
            "States_Covered": group["State"].nunique() if "State" in group.columns else 0,
        })
    return pd.DataFrame(rows).sort_values("Trained_Count", ascending=False)
