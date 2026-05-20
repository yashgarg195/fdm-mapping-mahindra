"""
Deduplication Module — Detect duplicate records in manpower and training data.
Never deletes rows. Always returns both clean and duplicate tables.
"""
import pandas as pd
import numpy as np


def detect_duplicate_manpower(df):
    """Detect duplicate manpower records by Star ID.
    First occurrence is CLEAN, subsequent are DUPLICATE.
    Returns (clean_df, duplicate_df).
    Combined row count always equals input row count.
    """
    if df is None or df.empty:
        empty = pd.DataFrame(columns=list(df.columns) + ["DATA_QUALITY_STATUS", "DATA_QUALITY_REASON"])
        return empty.copy(), empty.copy()

    df = df.copy()
    df["DATA_QUALITY_STATUS"] = "CLEAN"
    df["DATA_QUALITY_REASON"] = ""

    if "Star ID" not in df.columns:
        return df, pd.DataFrame(columns=df.columns)

    # Identify duplicates (keep first)
    dup_mask = df.duplicated(subset=["Star ID"], keep="first")

    # Mark duplicates
    df.loc[dup_mask, "DATA_QUALITY_STATUS"] = "DUPLICATE"
    df.loc[dup_mask, "DATA_QUALITY_REASON"] = df.loc[dup_mask, "Star ID"].apply(
        lambda x: f"Duplicate Star ID: {x}"
    )

    clean_df = df[~dup_mask].copy()
    duplicate_df = df[dup_mask].copy()

    assert len(clean_df) + len(duplicate_df) == len(df), \
        "Row count mismatch in deduplication!"

    return clean_df, duplicate_df


def detect_duplicate_training(df):
    """Detect duplicate training records.
    Duplicate = same Star ID + Training year + LAST MODEL TRAINED.
    First occurrence is CLEAN, subsequent are DUPLICATE.
    Returns (clean_df, duplicate_df).
    Combined row count always equals input row count.
    """
    if df is None or df.empty:
        empty = pd.DataFrame(columns=list(df.columns) + ["DATA_QUALITY_STATUS", "DATA_QUALITY_REASON"])
        return empty.copy(), empty.copy()

    df = df.copy()
    df["DATA_QUALITY_STATUS"] = "CLEAN"
    df["DATA_QUALITY_REASON"] = ""

    # Build subset for deduplication (only use columns that exist)
    dedup_cols = []
    for col in ["Star ID", "Training year", "LAST MODEL TRAINED"]:
        if col in df.columns:
            dedup_cols.append(col)

    if not dedup_cols:
        return df, pd.DataFrame(columns=df.columns)

    # Identify duplicates
    dup_mask = df.duplicated(subset=dedup_cols, keep="first")

    df.loc[dup_mask, "DATA_QUALITY_STATUS"] = "DUPLICATE"
    df.loc[dup_mask, "DATA_QUALITY_REASON"] = "Duplicate training record"

    clean_df = df[~dup_mask].copy()
    duplicate_df = df[dup_mask].copy()

    assert len(clean_df) + len(duplicate_df) == len(df), \
        "Row count mismatch in training deduplication!"

    return clean_df, duplicate_df
