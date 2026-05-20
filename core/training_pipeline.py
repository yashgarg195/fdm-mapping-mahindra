"""
Training Pipeline Module — Training status assignment, rolling backlog
computation, and nomination list generation.
"""
import datetime
import pandas as pd
import numpy as np
from config.constants import TRAINING_STATUSES, CURRENT_FY, SKILL_SCORE_MAP
from config.settings import (
    DEFAULT_NOMINATION_TOP_N,
    PENDING_AGE_CRITICAL_MONTHS,
    PENDING_AGE_WARNING_MONTHS,
)
from core.scoring import compute_skill_score, compute_training_priority_score
from utils.date_utils import months_since, fy_end_date, parse_date_safe


def assign_training_status(row):
    """Assign a training status to an employee row.
    Returns one of TRAINING_STATUSES values.
    Logic:
      - COMPLETED: training in current FY with positive post-score
      - ATTENDED: training in current FY but no skill improvement
      - PENDING: had training in prior FY, not yet in current
      - ELIGIBLE: no training history at all
      - NOT_ELIGIBLE: non-technical roles with no requirements
    """
    try:
        fy = str(row.get("Training year", "")).strip()
        post = compute_skill_score(row.get("SKILL LEVEL - POST", row.get("post_score")))
        pre = compute_skill_score(row.get("SKILL LEVEL - PRE", row.get("pre_score")))
        match_method = str(row.get("Match_Method", "")).strip()

        # Roster-only (never trained)
        if match_method == "ROSTER_ONLY" or not fy or fy in ("nan", "None", "NAN"):
            return "ELIGIBLE"

        # Current FY with skill gain
        if fy == CURRENT_FY:
            if post > 0 and (pre < 0 or post > pre):
                return "COMPLETED"
            elif post >= 0:
                return "ATTENDED"
            else:
                return "ATTENDED"

        # Has historical training but not in current FY
        return "PENDING"

    except Exception:
        return "ELIGIBLE"


def compute_pending_age(row, reference_date=None):
    """Compute how many months an employee has been pending training.
    Uses last training date if available, else joining date.
    Returns 0 if no date available.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    try:
        # Try latest training date first
        ltd = row.get("LATEST_TRAINING_DATE")
        if ltd is not None and not (isinstance(ltd, float) and np.isnan(ltd)):
            dt = parse_date_safe(ltd)
            if dt:
                result = months_since(dt, reference_date)
                return result if result is not None else 0

        # Try training year FY end date
        fy = str(row.get("Training year", "")).strip()
        if fy and fy not in ("nan", "None", "NAN"):
            fy_end = fy_end_date(fy)
            if fy_end:
                result = months_since(fy_end, reference_date)
                return result if result is not None else 0

        # Fall back to joining date
        jd = row.get("Joining Date")
        if jd is not None:
            dt = parse_date_safe(jd)
            if dt:
                result = months_since(dt, reference_date)
                return result if result is not None else 0

        return 0
    except Exception:
        return 0


def build_rolling_backlog(unified_df, reference_date=None):
    """Build a rolling backlog DataFrame from the unified master.
    Filters to PENDING, ELIGIBLE, and DEFERRED employees.
    Computes Pending_Age_Months and Training_Priority_Score.
    Sorts by priority and adds Backlog_Rank.
    
    Returns backlog DataFrame.
    """
    if unified_df is None or unified_df.empty:
        return pd.DataFrame()

    if reference_date is None:
        reference_date = datetime.date.today()

    df = unified_df.copy()

    # Assign training status if not present
    if "Training_Status" not in df.columns:
        df["Training_Status"] = df.apply(assign_training_status, axis=1)

    # Filter to backlog-eligible statuses
    backlog_statuses = ["PENDING", "ELIGIBLE", "DEFERRED"]
    backlog = df[df["Training_Status"].isin(backlog_statuses)].copy()

    if backlog.empty:
        return pd.DataFrame()

    # De-duplicate by Star ID (keep earliest/most stale record)
    if "Star ID" in backlog.columns:
        backlog = backlog.sort_values(
            "LATEST_TRAINING_DATE", ascending=True, na_position="first"
        ).drop_duplicates(subset=["Star ID"], keep="first")

    # Compute pending age
    backlog["Pending_Age_Months"] = backlog.apply(
        lambda row: compute_pending_age(row, reference_date), axis=1
    )

    # Compute priority score
    backlog["Training_Priority_Score"] = backlog.apply(
        compute_training_priority_score, axis=1
    )

    # Sort: oldest pending first, then highest priority
    backlog = backlog.sort_values(
        ["Pending_Age_Months", "Training_Priority_Score"],
        ascending=[False, False],
    ).reset_index(drop=True)

    # Add rank
    backlog["Backlog_Rank"] = range(1, len(backlog) + 1)

    # Categorize pending age
    backlog["Pending_Category"] = backlog["Pending_Age_Months"].apply(
        lambda m: "CRITICAL" if m >= PENDING_AGE_CRITICAL_MONTHS
        else ("WARNING" if m >= PENDING_AGE_WARNING_MONTHS else "NORMAL")
    )

    return backlog


def build_nomination_list(backlog_df, top_n=None):
    """Extract the top-N priority nominations from the backlog.
    Returns nomination DataFrame with Nomination_Rank column.
    """
    if backlog_df is None or backlog_df.empty:
        return pd.DataFrame()

    if top_n is None:
        top_n = DEFAULT_NOMINATION_TOP_N

    nomination = backlog_df.head(top_n).copy()
    nomination["Nomination_Rank"] = range(1, len(nomination) + 1)
    return nomination
