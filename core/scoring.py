"""
Scoring Module — Skill scoring, training effectiveness, priority scoring,
and dealership readiness computation.
"""
import pandas as pd
import numpy as np
from config.constants import SKILL_SCORE_MAP, CURRENT_FY, TECHNICAL_DESIGNATIONS
from config.settings import (
    PRIORITY_WEIGHT_PENDING_AGE, PRIORITY_WEIGHT_SKILL_GAP,
    PRIORITY_WEIGHT_PRODUCT_CRIT, PRIORITY_WEIGHT_DESIGNATION,
    PRIORITY_WEIGHT_DEALER_SHORTAGE, MIN_L3_L4_PER_DEALERSHIP,
    PENDING_AGE_CRITICAL_MONTHS,
)


def compute_skill_score(skill_level):
    """Map a skill level string to a numeric score.
    Returns -1 for unknown/unmapped values.
    """
    if skill_level is None:
        return -1
    return SKILL_SCORE_MAP.get(skill_level, SKILL_SCORE_MAP.get(str(skill_level).strip(), -1))


def compute_training_effectiveness(pre, post):
    """Compute training effectiveness as post - pre skill delta.
    Returns None if either is -1 (NO TEST) or None.
    """
    pre_s = compute_skill_score(pre)
    post_s = compute_skill_score(post)
    if pre_s < 0 or post_s < 0:
        return None
    return post_s - pre_s


def compute_training_priority_score(row):
    """Compute a priority score (0-100) for a training candidate.
    Higher = more urgent need for training.

    Inputs from row:
      - Pending_Age_Months (int)
      - post_score or SKILL LEVEL - POST
      - Designation
      - Dealer_Shortage_Flag (bool, optional)
      - Product_Criticality_Flag (bool, optional)
    """
    try:
        score = 0.0

        # 1. Pending age component (0-100, scaled)
        pending_age = int(row.get("Pending_Age_Months", 0) or 0)
        age_score = min(pending_age / PENDING_AGE_CRITICAL_MONTHS * 100, 100)
        score += age_score * PRIORITY_WEIGHT_PENDING_AGE

        # 2. Skill gap component (lower skill = higher priority)
        post = compute_skill_score(row.get("SKILL LEVEL - POST", row.get("post_score")))
        if post < 0:
            post = 0
        skill_gap_score = max(0, (4 - post) / 4 * 100)
        score += skill_gap_score * PRIORITY_WEIGHT_SKILL_GAP

        # 3. Product criticality (flag-based)
        prod_flag = bool(row.get("Product_Criticality_Flag", False))
        score += (100 if prod_flag else 0) * PRIORITY_WEIGHT_PRODUCT_CRIT

        # 4. Designation priority (technical roles score higher)
        desig = str(row.get("Designation", "")).strip()
        is_technical = desig in TECHNICAL_DESIGNATIONS
        score += (100 if is_technical else 30) * PRIORITY_WEIGHT_DESIGNATION

        # 5. Dealer shortage
        shortage = bool(row.get("Dealer_Shortage_Flag", False))
        score += (100 if shortage else 0) * PRIORITY_WEIGHT_DEALER_SHORTAGE

        return round(min(max(score, 0), 100), 2)
    except Exception:
        return 0.0


def compute_dealership_readiness(dealer_df):
    """Compute a readiness score (0-100) for a dealership.
    Based on:
      - % of technicians at L3+ (weight 40%)
      - % trained in current FY (weight 35%)
      - specialist count vs minimum threshold (weight 25%)
    """
    try:
        if dealer_df is None or dealer_df.empty:
            return 0.0

        total = len(dealer_df)
        if total == 0:
            return 0.0

        # L3+ specialist percentage
        if "post_score" in dealer_df.columns:
            l3_plus = (dealer_df["post_score"].astype(int, errors="ignore") >= 3).sum()
        elif "SKILL LEVEL - POST" in dealer_df.columns:
            l3_plus = dealer_df["SKILL LEVEL - POST"].isin(["L3", "L4"]).sum()
        else:
            l3_plus = 0
        l3_pct = min(l3_plus / total * 100, 100)

        # Current FY training percentage
        if "Training year" in dealer_df.columns:
            current_fy_count = (dealer_df["Training year"] == CURRENT_FY).sum()
        else:
            current_fy_count = 0
        fy_pct = min(current_fy_count / total * 100, 100)

        # Specialist sufficiency
        spec_score = min(l3_plus / MIN_L3_L4_PER_DEALERSHIP * 100, 100)

        readiness = (l3_pct * 0.40) + (fy_pct * 0.35) + (spec_score * 0.25)
        return round(min(max(readiness, 0), 100), 2)
    except Exception:
        return 0.0
