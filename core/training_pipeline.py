"""
Training Pipeline Module — Training status assignment, rolling backlog,
and nomination list generation.
FIXED: Smart status logic, proper pending age, realistic backlog sizing.
"""
import datetime
import pandas as pd
import numpy as np
from config.constants import TRAINING_STATUSES, CURRENT_FY, SKILL_SCORE_MAP, TECHNICAL_DESIGNATIONS
from config.settings import (
    DEFAULT_NOMINATION_TOP_N,
    PENDING_AGE_CRITICAL_MONTHS,
    PENDING_AGE_WARNING_MONTHS,
)
from core.scoring import compute_skill_score, compute_training_priority_score
from utils.date_utils import months_since, fy_end_date, parse_date_safe


def assign_training_status(row):
    """Assign a training status to an employee row.
    FIXED: Proper separation of trained/untrained/pending/not-eligible.

    Logic:
      - COMPLETED: trained in current FY AND post-score improved over pre-score
      - ATTENDED: trained in current FY but no measurable skill improvement
      - PENDING: trained in a PRIOR FY but not in current FY → needs refresher
      - ELIGIBLE: never trained BUT is in a TECHNICAL_DESIGNATION → should be trained
      - NOT_TRAINED: never trained and not in a technical role → informational only
      - NOT_ELIGIBLE: explicit non-training role (e.g., admin, manager with no tech duties)
    """
    try:
        fy = str(row.get("Training year", "")).strip()
        post = compute_skill_score(row.get("SKILL LEVEL - POST", row.get("post_score")))
        pre = compute_skill_score(row.get("SKILL LEVEL - PRE", row.get("pre_score")))
        match_method = str(row.get("Match_Method", "")).strip()
        designation = str(row.get("Designation", "")).strip()

        has_training = fy and fy not in ("nan", "None", "NAN", "")

        # ── Roster-only (never appeared in any training file) ────────────
        if match_method == "ROSTER_ONLY" or not has_training:
            # Check if this is a technical role that SHOULD be trained
            if designation in TECHNICAL_DESIGNATIONS:
                return "ELIGIBLE"
            else:
                return "NOT_TRAINED"

        # ── Has training in current FY ───────────────────────────────────
        if fy == CURRENT_FY:
            if post > 0 and pre >= 0 and post > pre:
                return "COMPLETED"
            elif post >= 0:
                return "ATTENDED"
            else:
                return "ATTENDED"

        # ── Has training in a prior FY (but not current) ─────────────────
        # This employee was trained before but has not been re-trained this year
        return "PENDING"

    except Exception:
        return "NOT_TRAINED"


def compute_pending_age(row, reference_date=None):
    """Compute how many months an employee has been pending training.
    FIXED: Actually produces real month values from FY end dates and joining dates.

    For PENDING employees: months since their last training FY ended
    For ELIGIBLE employees: months since their Joining Date
    For others: 0
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    try:
        status = str(row.get("Training_Status", "")).strip()

        # For PENDING: use last training FY end date
        if status == "PENDING":
            fy = str(row.get("Training year", "")).strip()
            if fy and fy not in ("nan", "None", "NAN", ""):
                fy_end = fy_end_date(fy)
                if fy_end:
                    if isinstance(fy_end, str):
                        try:
                            fy_end = datetime.datetime.strptime(fy_end, "%Y-%m-%d").date()
                        except Exception:
                            try:
                                fy_end = pd.to_datetime(fy_end).date()
                            except Exception:
                                pass
                    if isinstance(fy_end, (datetime.date, datetime.datetime)):
                        if isinstance(fy_end, datetime.datetime):
                            fy_end = fy_end.date()
                        delta_days = (reference_date - fy_end).days
                        if delta_days > 0:
                            return max(1, delta_days // 30)
                        return 0

        # For ELIGIBLE: use joining date
        if status == "ELIGIBLE":
            jd = row.get("Joining Date")
            if jd is not None:
                dt = parse_date_safe(jd)
                if dt:
                    if isinstance(dt, datetime.datetime):
                        dt = dt.date()
                    delta_days = (reference_date - dt).days
                    if delta_days > 0:
                        return max(1, delta_days // 30)

            # Fallback: if no joining date, assume 6 months pending
            return 6

        # For COMPLETED/ATTENDED: not pending
        return 0

    except Exception:
        return 0


def build_rolling_backlog(unified_df, reference_date=None):
    """Build a rolling backlog DataFrame from the unified master.
    FIXED: Only includes PENDING (needs refresher) and ELIGIBLE (technical, never trained).
    Excludes NOT_TRAINED, NOT_ELIGIBLE, COMPLETED, ATTENDED.
    """
    if unified_df is None or unified_df.empty:
        return pd.DataFrame()

    if reference_date is None:
        reference_date = datetime.date.today()

    df = unified_df.copy()

    # Assign training status if not present
    if "Training_Status" not in df.columns:
        df["Training_Status"] = df.apply(assign_training_status, axis=1)

    # Only include employees who actually need training
    backlog_statuses = ["PENDING", "ELIGIBLE"]
    backlog = df[df["Training_Status"].isin(backlog_statuses)].copy()

    if backlog.empty:
        return pd.DataFrame()

    # De-duplicate by Star ID (keep the record with the oldest/most stale training)
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
