"""
Backlog Analytics — Aging reports and dealership backlog ranking.
"""
import pandas as pd


def backlog_aging_report(backlog_df):
    """Categorize backlog by aging buckets."""
    cols = ["Aging_Bucket", "Count", "Pct"]
    if backlog_df is None or backlog_df.empty or "Pending_Age_Months" not in backlog_df.columns:
        return pd.DataFrame(columns=cols)
    df = backlog_df.copy()
    m = df["Pending_Age_Months"].astype(int, errors="ignore")

    buckets = [
        ("0-3 months", (m >= 0) & (m < 3)),
        ("3-6 months", (m >= 3) & (m < 6)),
        ("6-12 months", (m >= 6) & (m < 12)),
        ("12+ months", m >= 12),
    ]
    rows = []
    total = len(df)
    for label, mask in buckets:
        count = mask.sum()
        pct = round(count / max(total, 1) * 100, 1)
        rows.append({"Aging_Bucket": label, "Count": int(count), "Pct": pct})
    return pd.DataFrame(rows)


def dealership_backlog_rank(backlog_df):
    """Rank dealerships by backlog size."""
    cols = ["Dealer_Code", "Dealer_Name", "Backlog_Count", "Avg_Pending_Age", "Max_Pending_Age"]
    if backlog_df is None or backlog_df.empty or "Dealer Code" not in backlog_df.columns:
        return pd.DataFrame(columns=cols)
    df = backlog_df.copy()
    grouped = df.groupby("Dealer Code").agg(
        Backlog_Count=("Star ID", "nunique") if "Star ID" in df.columns else ("Dealer Code", "count"),
        Avg_Pending_Age=("Pending_Age_Months", "mean"),
        Max_Pending_Age=("Pending_Age_Months", "max"),
    ).reset_index()
    grouped.rename(columns={"Dealer Code": "Dealer_Code"}, inplace=True)
    grouped["Avg_Pending_Age"] = grouped["Avg_Pending_Age"].round(1)
    # Add dealer name
    if "Dealer Name" in df.columns:
        dn = df[["Dealer Code", "Dealer Name"]].drop_duplicates()
        dn.rename(columns={"Dealer Code": "Dealer_Code", "Dealer Name": "Dealer_Name"}, inplace=True)
        grouped = grouped.merge(dn, on="Dealer_Code", how="left")
    else:
        grouped["Dealer_Name"] = ""
    return grouped.sort_values("Backlog_Count", ascending=False)[cols].reset_index(drop=True)
