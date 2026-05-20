"""
Deduplication Module — Detect duplicate records in manpower and training data.
FIXED: Added fuzzy name-based duplicate detection within dealer groups.
Never deletes rows. Always returns both clean and duplicate tables.
"""
import pandas as pd
import numpy as np
from core.cleansing import normalize_name, normalize_dealer_code


def _fuzzy_name_dedup_within_dealers(df):
    """Scan each dealer group for employees with very similar names but
    different Star IDs. Flags them as SUSPECT_DUPLICATE.
    This catches the same person registered twice with different IDs.
    """
    if "Star ID" not in df.columns or "Dealer Code" not in df.columns:
        return df

    try:
        from rapidfuzz import fuzz
    except ImportError:
        return df

    df["_name_dedup"] = df["Name"].apply(normalize_name)
    df["_dealer_dedup"] = df["Dealer Code"].apply(normalize_dealer_code)

    suspect_indices = set()
    suspect_notes = {}

    # Group by dealer code for efficient comparison
    grouped = df.groupby("_dealer_dedup")
    for dealer_code, group in grouped:
        if len(group) < 2 or not dealer_code:
            continue

        names = group["_name_dedup"].tolist()
        sids = group["Star ID"].tolist()
        idxs = group.index.tolist()

        for i in range(len(names)):
            if not names[i]:
                continue
            for j in range(i + 1, len(names)):
                if not names[j]:
                    continue
                # Skip if same Star ID (already caught by exact dedup)
                if str(sids[i]).strip() == str(sids[j]).strip():
                    continue
                score = fuzz.token_sort_ratio(names[i], names[j])
                if score >= 92:
                    suspect_indices.add(idxs[i])
                    suspect_indices.add(idxs[j])
                    note_i = f"Fuzzy name match ({score}%) with Star ID {sids[j]}"
                    note_j = f"Fuzzy name match ({score}%) with Star ID {sids[i]}"
                    suspect_notes[idxs[i]] = suspect_notes.get(idxs[i], "") + ("; " if suspect_notes.get(idxs[i]) else "") + note_i
                    suspect_notes[idxs[j]] = suspect_notes.get(idxs[j], "") + ("; " if suspect_notes.get(idxs[j]) else "") + note_j

    # Apply flags (these stay in the CLEAN set, just flagged)
    for idx in suspect_indices:
        if df.loc[idx, "DATA_QUALITY_STATUS"] == "CLEAN":
            df.loc[idx, "DATA_QUALITY_STATUS"] = "SUSPECT_DUPLICATE"
        df.loc[idx, "DATA_QUALITY_REASON"] = suspect_notes.get(idx, "Suspect duplicate")

    # Clean up temp columns
    df.drop(columns=["_name_dedup", "_dealer_dedup"], inplace=True, errors="ignore")

    return df


def detect_duplicate_manpower(df):
    """Detect duplicate manpower records.
    Pass 1: Exact Star ID duplicates.
    Pass 2: Fuzzy name duplicates within same dealer (different Star IDs).
    First occurrence is CLEAN, subsequent exact dupes are DUPLICATE.
    Fuzzy suspects stay in clean set but are flagged.
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

    # Pass 1: Exact Star ID duplicates
    dup_mask = df.duplicated(subset=["Star ID"], keep="first")
    df.loc[dup_mask, "DATA_QUALITY_STATUS"] = "DUPLICATE"
    df.loc[dup_mask, "DATA_QUALITY_REASON"] = df.loc[dup_mask, "Star ID"].apply(
        lambda x: f"Duplicate Star ID: {x}"
    )

    clean_df = df[~dup_mask].copy()
    duplicate_df = df[dup_mask].copy()

    # Pass 2: Fuzzy name duplicates within dealer groups (on clean set only)
    clean_df = _fuzzy_name_dedup_within_dealers(clean_df)

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
