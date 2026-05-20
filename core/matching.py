"""
Identity Resolution Module — 7-Pass multi-strategy matching engine.
Maps training records (potentially missing Star IDs) to manpower roster entries.
Every row gets Match_Method, Match_Confidence, Fuzzy_Score, Phonetic_Score, Matched_Candidate.
ZERO row loss guaranteed.
"""
import pandas as pd
import numpy as np
from collections import defaultdict

from core.cleansing import (
    normalize_name, normalize_contact, normalize_aadhar,
    normalize_dealer_code, clean_star_id,
)
from core.fuzzy_matching import fuzzy_name_match, phonetic_match, composite_score
from config.constants import (
    SKILL_SCORE_MAP, MODEL_NORMALISATION_MAP, CANONICAL_MODELS,
    FY_CALENDAR, ROSTER_COLUMNS, TRAINING_COLUMNS,
)
from config.settings import (
    FUZZY_PRIMARY_THRESHOLD, FUZZY_SECONDARY_THRESHOLD,
    FUZZY_GLOBAL_THRESHOLD, PHONETIC_JARO_THRESHOLD,
    FUZZY_AO_THRESHOLD, CONFIDENCE_THRESHOLD_HIGH,
    CONFIDENCE_THRESHOLD_MEDIUM, CONFIDENCE_THRESHOLD_LOW,
    CONFIDENCE_THRESHOLD_FUZZY, MAX_CANDIDATES_PER_MATCH,
    ENABLE_GLOBAL_FUZZY_PASS,
)
from utils.logging_utils import log_match_event, log_pipeline_event, Timer
from utils.date_utils import months_since, fy_end_date
import jellyfish


def _build_indexes(manpower_df):
    """Build lookup indexes from the manpower roster for fast matching."""
    star_id_map = {}
    aadhar_map = {}
    emp_code_map = {}
    dealer_group = defaultdict(list)
    ao_group = defaultdict(list)
    contact_map = {}
    roster_records = []

    for idx, row in manpower_df.iterrows():
        rec = row.to_dict()
        rec["_idx"] = idx

        # Star ID index
        sid = clean_star_id(rec.get("Star ID"))
        if sid:
            rec["_star_id_clean"] = sid
            star_id_map[sid] = rec

        # Aadhar index
        aadhar = normalize_aadhar(rec.get("AadharCardNumber"))
        if aadhar:
            rec["_aadhar_clean"] = aadhar
            aadhar_map[aadhar] = rec

        # Emp Code index
        emp = str(rec.get("Emp Code", "")).strip().upper()
        if emp and emp not in ("NAN", "NONE", ""):
            rec["_emp_code_clean"] = emp
            emp_code_map[emp] = rec

        # Name index
        rec["_name_clean"] = normalize_name(rec.get("Name"))

        # Contact index
        contact = normalize_contact(rec.get("Contact No"))
        if contact:
            rec["_contact_clean"] = contact
            contact_map[contact] = rec

        # Dealer grouping
        dc = normalize_dealer_code(rec.get("Dealer Code"))
        if dc:
            rec["_dealer_clean"] = dc
            dealer_group[dc].append(rec)

        # AO grouping
        ao = str(rec.get("Dealer AO", "")).strip().upper()
        if ao and ao not in ("NAN", "NONE"):
            rec["_ao_clean"] = ao
            ao_group[ao].append(rec)

        roster_records.append(rec)

    return {
        "star_id_map": star_id_map,
        "aadhar_map": aadhar_map,
        "emp_code_map": emp_code_map,
        "dealer_group": dict(dealer_group),
        "ao_group": dict(ao_group),
        "contact_map": contact_map,
        "roster_records": roster_records,
        "global_names": [rec["_name_clean"] for rec in roster_records if rec.get("_name_clean")],
        "global_name_to_rec": {rec["_name_clean"]: rec for rec in roster_records if rec.get("_name_clean")}
    }


def _match_row(t_row, indexes):
    """Run the 7-pass resolution pipeline on a single training row.
    Returns dict with match result fields.
    """
    result = {
        "Match_Method": "PASS7_UNRESOLVED",
        "Match_Confidence": "UNRESOLVED",
        "Fuzzy_Score": 0.0,
        "Phonetic_Score": 0.0,
        "Matched_Candidate": "PENDING_MAPPING_REVIEW",
        "_matched_rec": None,
    }

    t_name = normalize_name(t_row.get("Name"))
    t_dealer = normalize_dealer_code(t_row.get("Dealer Code"))
    t_contact = normalize_contact(t_row.get("Contact No"))
    t_aadhar = normalize_aadhar(t_row.get("AadharCardNumber"))
    t_emp = str(t_row.get("Emp Code", "")).strip().upper()
    t_sid = clean_star_id(t_row.get("Star ID"))

    # ── PASS 1: Exact Identifier Match ──────────────────────────────────────
    # 1A: Star ID
    if t_sid and t_sid in indexes["star_id_map"]:
        rec = indexes["star_id_map"][t_sid]
        result.update({
            "Match_Method": "PASS1_EXACT_STAR_ID",
            "Match_Confidence": "HIGH",
            "Fuzzy_Score": 100.0,
            "Phonetic_Score": 100.0,
            "Matched_Candidate": str(t_sid),
            "_matched_rec": rec,
        })
        return result

    # 1B: Aadhar
    if t_aadhar and t_aadhar in indexes["aadhar_map"]:
        rec = indexes["aadhar_map"][t_aadhar]
        result.update({
            "Match_Method": "PASS1_EXACT_AADHAR",
            "Match_Confidence": "HIGH",
            "Fuzzy_Score": 100.0,
            "Phonetic_Score": 100.0,
            "Matched_Candidate": str(rec.get("_star_id_clean", "")),
            "_matched_rec": rec,
        })
        return result

    # 1C: Emp Code
    if t_emp and t_emp not in ("NAN", "NONE", "") and t_emp in indexes["emp_code_map"]:
        rec = indexes["emp_code_map"][t_emp]
        result.update({
            "Match_Method": "PASS1_EXACT_EMP_CODE",
            "Match_Confidence": "HIGH",
            "Fuzzy_Score": 100.0,
            "Phonetic_Score": 100.0,
            "Matched_Candidate": str(rec.get("_star_id_clean", "")),
            "_matched_rec": rec,
        })
        return result

    # ── PASS 2: Exact Composite Key (name + dealer + contact) ───────────────
    if t_name and t_dealer:
        candidates = indexes["dealer_group"].get(t_dealer, [])
        for rec in candidates:
            r_name = rec.get("_name_clean")
            if r_name and r_name == t_name:
                # Bonus: check contact for certainty
                conf = "HIGH"
                if t_contact and rec.get("_contact_clean"):
                    if t_contact == rec.get("_contact_clean"):
                        conf = "HIGH"
                    else:
                        conf = "MEDIUM"
                result.update({
                    "Match_Method": "PASS2_EXACT_NAME_DEALER",
                    "Match_Confidence": conf,
                    "Fuzzy_Score": 100.0,
                    "Phonetic_Score": 100.0,
                    "Matched_Candidate": str(rec.get("_star_id_clean", "")),
                    "_matched_rec": rec,
                })
                return result

    # ── PASS 3: Fuzzy Name + Same Dealer ────────────────────────────────────
    if t_name and t_dealer:
        candidates = indexes["dealer_group"].get(t_dealer, [])
        best_score = 0
        best_rec = None
        for rec in candidates:
            r_name = rec.get("_name_clean")
            if not r_name:
                continue
            score = fuzzy_name_match(t_name, r_name)
            if score > best_score:
                best_score = score
                best_rec = rec
        if best_rec and best_score >= FUZZY_PRIMARY_THRESHOLD:
            result.update({
                "Match_Method": "PASS3_FUZZY_NAME_DEALER",
                "Match_Confidence": "MEDIUM",
                "Fuzzy_Score": best_score,
                "Phonetic_Score": phonetic_match(t_name, best_rec.get("_name_clean", "")),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result
        elif best_rec and best_score >= FUZZY_SECONDARY_THRESHOLD:
            result.update({
                "Match_Method": "PASS3_FUZZY_NAME_DEALER_LOW",
                "Match_Confidence": "LOW",
                "Fuzzy_Score": best_score,
                "Phonetic_Score": phonetic_match(t_name, best_rec.get("_name_clean", "")),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 4: Dealer-Transfer-Aware (name across ALL dealers) ─────────────
    if t_name and ENABLE_GLOBAL_FUZZY_PASS:
        try:
            from rapidfuzz import process, fuzz
            match = process.extractOne(
                t_name, 
                indexes.get("global_names", []), 
                scorer=fuzz.token_sort_ratio,
                score_cutoff=FUZZY_GLOBAL_THRESHOLD
            )
            if match:
                matched_name, best_score, _ = match
                best_rec = indexes["global_name_to_rec"].get(matched_name)
                if best_rec:
                    result.update({
                        "Match_Method": "PASS4_TRANSFER_MATCH",
                        "Match_Confidence": "LOW",
                        "Fuzzy_Score": round(best_score, 2),
                        "Phonetic_Score": phonetic_match(t_name, best_rec.get("_name_clean", "")),
                        "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                        "_matched_rec": best_rec,
                    })
                    return result
        except Exception:
            pass

    # ── PASS 5: Phonetic Matching (same dealer) ────────────────────────────
    if t_name and t_dealer:
        candidates = indexes["dealer_group"].get(t_dealer, [])
        best_jw = 0
        best_rec = None
        for rec in candidates:
            r_name = rec.get("_name_clean")
            if not r_name:
                continue
            try:
                jw = jellyfish.jaro_winkler_similarity(t_name, r_name)
            except Exception:
                jw = 0
            if jw > best_jw:
                best_jw = jw
                best_rec = rec
        if best_rec and best_jw >= PHONETIC_JARO_THRESHOLD:
            p_score = phonetic_match(t_name, best_rec.get("_name_clean", ""))
            result.update({
                "Match_Method": "PASS5_PHONETIC",
                "Match_Confidence": "LOW",
                "Fuzzy_Score": fuzzy_name_match(t_name, best_rec.get("_name_clean", "")),
                "Phonetic_Score": p_score,
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 6: Probabilistic Composite Scoring (AO-level, then global) ─────
    if t_name:
        t_ao = str(t_row.get("Dealer AO", "")).strip().upper()
        search_pool = []
        if t_ao and t_ao in indexes["ao_group"]:
            search_pool = indexes["ao_group"][t_ao]
        if not search_pool:
            search_pool = indexes["roster_records"][:MAX_CANDIDATES_PER_MATCH * 5]

        best_comp = 0
        best_rec = None
        best_fz = 0
        best_ph = 0
        for rec in search_pool:
            r_name = rec.get("_name_clean")
            if not r_name:
                continue
            fz = fuzzy_name_match(t_name, r_name)
            ph = phonetic_match(t_name, r_name)
            comp = composite_score(fz, ph)
            if comp > best_comp:
                best_comp = comp
                best_rec = rec
                best_fz = fz
                best_ph = ph

        if best_rec and best_comp >= CONFIDENCE_THRESHOLD_FUZZY:
            if best_comp >= CONFIDENCE_THRESHOLD_HIGH:
                conf = "HIGH"
            elif best_comp >= CONFIDENCE_THRESHOLD_MEDIUM:
                conf = "MEDIUM"
            elif best_comp >= CONFIDENCE_THRESHOLD_LOW:
                conf = "LOW"
            else:
                conf = "FUZZY"
            result.update({
                "Match_Method": "PASS6_PROBABILISTIC",
                "Match_Confidence": conf,
                "Fuzzy_Score": best_fz,
                "Phonetic_Score": best_ph,
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 7: Unresolved ──────────────────────────────────────────────────
    return result


def _normalize_model_name(model):
    """Normalize a training model name using the standardization map."""
    if not model or str(model).strip().upper() in ("NAN", "NONE", ""):
        return None
    m = str(model).strip().upper()
    m = MODEL_NORMALISATION_MAP.get(m, m)
    return m


def resolve_star_ids(training_df, manpower_df):
    """Run the full 7-pass identity resolution pipeline.
    
    Args:
        training_df: DataFrame of training records (may lack Star IDs)
        manpower_df: DataFrame of current manpower roster (has Star IDs)
    
    Returns:
        unified_df: Enriched DataFrame with all rows from both inputs.
        stats: dict with pipeline statistics.
    """
    with Timer("Identity Resolution Pipeline"):
        # Build indexes from manpower
        indexes = _build_indexes(manpower_df)
        log_pipeline_event(
            f"Built indexes: {len(indexes['star_id_map'])} Star IDs, "
            f"{len(indexes['dealer_group'])} dealer groups, "
            f"{len(indexes['roster_records'])} roster records"
        )

        # Track which roster records were matched
        matched_roster_ids = set()
        matched_results = []
        pass_counts = defaultdict(int)
        confidence_counts = defaultdict(int)

        # Process each training row
        total = len(training_df)
        for idx, row in training_df.iterrows():
            t_dict = row.to_dict()
            match = _match_row(t_dict, indexes)

            # Merge training data with matched roster demographics
            merged = dict(t_dict)
            if match["_matched_rec"]:
                rec = match["_matched_rec"]
                # Copy roster demographics into the training row
                for col in ROSTER_COLUMNS:
                    if col not in merged or pd.isna(merged.get(col)):
                        merged[col] = rec.get(col)
                matched_roster_ids.add(rec.get("_star_id_clean"))
                # Ensure Star ID is populated
                if not merged.get("Star ID") or str(merged.get("Star ID")).strip() in ("", "nan"):
                    merged["Star ID"] = rec.get("Star ID")

            # Add match metadata
            merged["Match_Method"] = match["Match_Method"]
            merged["Match_Confidence"] = match["Match_Confidence"]
            merged["Fuzzy_Score"] = match["Fuzzy_Score"]
            merged["Phonetic_Score"] = match["Phonetic_Score"]
            merged["Matched_Candidate"] = match["Matched_Candidate"]

            # Normalize model name
            merged["LAST MODEL TRAINED"] = _normalize_model_name(
                merged.get("LAST MODEL TRAINED")
            )

            matched_results.append(merged)
            pass_counts[match["Match_Method"]] += 1
            confidence_counts[match["Match_Confidence"]] += 1

        # Log matching results
        for method, count in pass_counts.items():
            log_match_event(method, count)

        # Build matched DataFrame
        df_matched = pd.DataFrame(matched_results)

        # Append unmatched roster records (employees with no training)
        unmatched_roster = []
        for rec in indexes["roster_records"]:
            sid = rec.get("_star_id_clean")
            if sid and sid not in matched_roster_ids:
                entry = {}
                for col in ROSTER_COLUMNS:
                    entry[col] = rec.get(col)
                entry["Match_Method"] = "ROSTER_ONLY"
                entry["Match_Confidence"] = "HIGH"
                entry["Fuzzy_Score"] = 100.0
                entry["Phonetic_Score"] = 100.0
                entry["Matched_Candidate"] = str(sid)
                entry["Training_Status"] = "ELIGIBLE"
                unmatched_roster.append(entry)

        df_unmatched = pd.DataFrame(unmatched_roster)

        # Combine into unified master
        if not df_unmatched.empty:
            unified_df = pd.concat([df_matched, df_unmatched], ignore_index=True)
        else:
            unified_df = df_matched.copy()

        # ── Post-processing ──────────────────────────────────────────────────
        # Compute skill scores
        unified_df["pre_score"] = unified_df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
        unified_df["post_score"] = unified_df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

        # Skill regression flag
        unified_df["SKILL_REGRESSION_FLAG"] = (
            (unified_df["pre_score"] >= 0) &
            (unified_df["post_score"] >= 0) &
            (unified_df["post_score"] < unified_df["pre_score"])
        )

        # Future joining date flag
        if "Joining Date" in unified_df.columns:
            try:
                jd = pd.to_datetime(unified_df["Joining Date"], errors="coerce")
                unified_df["FUTURE_JOINING_FLAG"] = jd.dt.year > 2026
            except Exception:
                unified_df["FUTURE_JOINING_FLAG"] = False
        else:
            unified_df["FUTURE_JOINING_FLAG"] = False

        # Latest training date per employee
        if "Training year" in unified_df.columns:
            unified_df["_fy_end"] = unified_df["Training year"].apply(fy_end_date)
            unified_df["LATEST_TRAINING_DATE"] = pd.to_datetime(
                unified_df["_fy_end"], errors="coerce"
            )
            unified_df.drop(columns=["_fy_end"], inplace=True, errors="ignore")
        else:
            unified_df["LATEST_TRAINING_DATE"] = pd.NaT

        # Validated skill level (sequential ladder)
        unified_df["VALIDATED_SKILL_LEVEL"] = 0
        unified_df["MISSING_PREREQUISITE_FLAG"] = False

        if "Star ID" in unified_df.columns:
            grouped = unified_df.groupby("Star ID")
            for sid, group in grouped:
                post_scores = set(
                    group["post_score"][group["post_score"] > 0].unique()
                )
                if not post_scores:
                    continue
                # Validate sequential progression
                validated = 0
                for level in [1, 2, 3, 4]:
                    if level in post_scores:
                        validated = level
                    else:
                        break
                max_claimed = max(post_scores)
                missing = max_claimed > validated
                mask = unified_df["Star ID"] == sid
                unified_df.loc[mask, "VALIDATED_SKILL_LEVEL"] = validated
                unified_df.loc[mask, "MISSING_PREREQUISITE_FLAG"] = missing

        # Build stats
        stats = {
            "total_roster_count": len(indexes["roster_records"]),
            "total_training_input_count": total,
            "total_master_count": len(unified_df),
            "matched_count": total - confidence_counts.get("UNRESOLVED", 0),
            "untrained_count": len(unmatched_roster),
            "unresolved_count": confidence_counts.get("UNRESOLVED", 0),
            "confidence_distribution": dict(confidence_counts),
            "passes_distribution": dict(pass_counts),
            "future_joining_count": int(unified_df["FUTURE_JOINING_FLAG"].sum()),
            "skill_regression_count": int(unified_df["SKILL_REGRESSION_FLAG"].sum()),
            "missing_prerequisite_count": int(unified_df["MISSING_PREREQUISITE_FLAG"].sum()),
        }

        log_pipeline_event(
            f"Pipeline complete: {stats['total_master_count']} rows, "
            f"{stats['matched_count']} matched, "
            f"{stats['unresolved_count']} unresolved"
        )

        return unified_df, stats
