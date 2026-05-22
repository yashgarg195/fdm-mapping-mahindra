"""
Identity Resolution Module — 7-Pass multi-strategy matching engine.
FIXED: Pass 1 now validates names to produce real fuzzy/phonetic scores.
Cross-ID duplicate detection. Training orphan detection.
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

        sid = clean_star_id(rec.get("Star ID"))
        if sid:
            rec["_star_id_clean"] = sid
            star_id_map[sid] = rec

        aadhar = normalize_aadhar(rec.get("AadharCardNumber"))
        if aadhar:
            rec["_aadhar_clean"] = aadhar
            aadhar_map[aadhar] = rec

        emp = str(rec.get("Emp Code", "")).strip().upper()
        if emp and emp not in ("NAN", "NONE", ""):
            rec["_emp_code_clean"] = emp
            emp_code_map[emp] = rec

        rec["_name_clean"] = normalize_name(rec.get("Name"))

        contact = normalize_contact(rec.get("Contact No"))
        if contact:
            rec["_contact_clean"] = contact
            contact_map[contact] = rec

        dc = normalize_dealer_code(rec.get("Dealer Code"))
        if dc:
            rec["_dealer_clean"] = dc
            dealer_group[dc].append(rec)

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
        "global_name_to_rec": {rec["_name_clean"]: rec for rec in roster_records if rec.get("_name_clean")},
    }


def _match_row(t_row, indexes):
    """Run the 7-pass resolution pipeline on a single training row.
    FIXED: Pass 1 now validates name similarity for real confidence scoring.
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

    # ── PASS 1: Exact Identifier Match WITH Name Validation ──────────────
    matched_rec = None
    match_id_method = None

    if t_sid and t_sid in indexes["star_id_map"]:
        matched_rec = indexes["star_id_map"][t_sid]
        match_id_method = "PASS1_EXACT_STAR_ID"
    elif t_aadhar and t_aadhar in indexes["aadhar_map"]:
        matched_rec = indexes["aadhar_map"][t_aadhar]
        match_id_method = "PASS1_EXACT_AADHAR"
    elif t_emp and t_emp not in ("NAN", "NONE", "") and t_emp in indexes["emp_code_map"]:
        matched_rec = indexes["emp_code_map"][t_emp]
        match_id_method = "PASS1_EXACT_EMP_CODE"

    if matched_rec:
        r_name = matched_rec.get("_name_clean", "")
        # Compute REAL fuzzy and phonetic scores between the two names
        if t_name and r_name:
            real_fuzzy = fuzzy_name_match(t_name, r_name)
            real_phonetic = phonetic_match(t_name, r_name)
        elif not t_name and not r_name:
            real_fuzzy = 100.0  # both empty = trivial match
            real_phonetic = 100.0
        else:
            real_fuzzy = 0.0  # one has name, other doesn't
            real_phonetic = 0.0

        # Determine confidence based on name validation
        if real_fuzzy >= 88:
            confidence = "HIGH"
        elif real_fuzzy >= 60:
            confidence = "MEDIUM"
            match_id_method += "_NAME_MISMATCH"
        elif real_fuzzy >= 30:
            confidence = "LOW"
            match_id_method += "_NAME_CONFLICT"
        else:
            confidence = "LOW"
            match_id_method += "_NAME_CONFLICT"

        result.update({
            "Match_Method": match_id_method,
            "Match_Confidence": confidence,
            "Fuzzy_Score": round(real_fuzzy, 2),
            "Phonetic_Score": round(real_phonetic, 2),
            "Matched_Candidate": str(matched_rec.get("_star_id_clean", t_sid or "")),
            "_matched_rec": matched_rec,
        })
        return result

    # ── PASS 2: Exact Composite Key (name + dealer + contact) ───────────
    if t_name and t_dealer:
        candidates = indexes["dealer_group"].get(t_dealer, [])
        for rec in candidates:
            r_name = rec.get("_name_clean")
            if r_name and r_name == t_name:
                real_fuzzy = 100.0
                real_phonetic = phonetic_match(t_name, r_name) if t_name else 100.0
                conf = "HIGH"
                if t_contact and rec.get("_contact_clean"):
                    if t_contact != rec.get("_contact_clean"):
                        conf = "MEDIUM"
                result.update({
                    "Match_Method": "PASS2_EXACT_NAME_DEALER",
                    "Match_Confidence": conf,
                    "Fuzzy_Score": real_fuzzy,
                    "Phonetic_Score": round(real_phonetic, 2),
                    "Matched_Candidate": str(rec.get("_star_id_clean", "")),
                    "_matched_rec": rec,
                })
                return result

    # ── PASS 3: Fuzzy Name + Same Dealer ────────────────────────────────
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
                "Fuzzy_Score": round(best_score, 2),
                "Phonetic_Score": round(phonetic_match(t_name, best_rec.get("_name_clean", "")), 2),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result
        elif best_rec and best_score >= FUZZY_SECONDARY_THRESHOLD:
            result.update({
                "Match_Method": "PASS3_FUZZY_NAME_DEALER_LOW",
                "Match_Confidence": "LOW",
                "Fuzzy_Score": round(best_score, 2),
                "Phonetic_Score": round(phonetic_match(t_name, best_rec.get("_name_clean", "")), 2),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 4: Dealer-Transfer-Aware (global rapidfuzz) ────────────────
    if t_name and ENABLE_GLOBAL_FUZZY_PASS:
        try:
            from rapidfuzz import process, fuzz
            match = process.extractOne(
                t_name,
                indexes.get("global_names", []),
                scorer=fuzz.token_sort_ratio,
                score_cutoff=FUZZY_GLOBAL_THRESHOLD,
            )
            if match:
                matched_name, best_score, _ = match
                best_rec = indexes["global_name_to_rec"].get(matched_name)
                if best_rec:
                    result.update({
                        "Match_Method": "PASS4_TRANSFER_MATCH",
                        "Match_Confidence": "LOW",
                        "Fuzzy_Score": round(best_score, 2),
                        "Phonetic_Score": round(phonetic_match(t_name, best_rec.get("_name_clean", "")), 2),
                        "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                        "_matched_rec": best_rec,
                    })
                    return result
        except Exception:
            pass

    # ── PASS 5: Phonetic Matching (same dealer) ────────────────────────
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
            result.update({
                "Match_Method": "PASS5_PHONETIC",
                "Match_Confidence": "LOW",
                "Fuzzy_Score": round(fuzzy_name_match(t_name, best_rec.get("_name_clean", "")), 2),
                "Phonetic_Score": round(phonetic_match(t_name, best_rec.get("_name_clean", "")), 2),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 6: Probabilistic Composite (AO-level, then limited global) ──
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
                conf = "POSSIBLE MATCH"
            result.update({
                "Match_Method": "PASS6_PROBABILISTIC",
                "Match_Confidence": conf,
                "Fuzzy_Score": round(best_fz, 2),
                "Phonetic_Score": round(best_ph, 2),
                "Matched_Candidate": str(best_rec.get("_star_id_clean", "")),
                "_matched_rec": best_rec,
            })
            return result

    # ── PASS 7: Unresolved ──────────────────────────────────────────────
    return result


def _normalize_model_name(model):
    """Normalize a training model name using the standardization map."""
    if not model or str(model).strip().upper() in ("NAN", "NONE", ""):
        return None
    m = str(model).strip().upper()
    m = MODEL_NORMALISATION_MAP.get(m, m)
    return m


def _detect_cross_id_duplicates(unified_df):
    """Detect potential cross-ID duplicates: different Star IDs with very
    similar names at the same dealer. Flags them in-place."""
    if "Star ID" not in unified_df.columns or "Dealer Code" not in unified_df.columns:
        unified_df["CROSS_ID_DUPLICATE_SUSPECT"] = False
        return unified_df

    unified_df["CROSS_ID_DUPLICATE_SUSPECT"] = False
    unified_df["CROSS_ID_DUPLICATE_NOTE"] = ""

    try:
        from rapidfuzz import fuzz

        # Group by dealer, check for similar names with different Star IDs
        if "Dealer Code" in unified_df.columns:
            # Get unique employee per dealer (Star ID + Name + Dealer Code)
            uniq = unified_df.drop_duplicates(subset=["Star ID", "Dealer Code"])[
                ["Star ID", "Name", "Dealer Code"]
            ].copy()
            uniq["_name_clean"] = uniq["Name"].apply(normalize_name)

            flagged_pairs = set()
            for dealer_code, group in uniq.groupby("Dealer Code"):
                if len(group) < 2:
                    continue
                names = group["_name_clean"].tolist()
                sids = group["Star ID"].tolist()
                for i in range(len(names)):
                    if not names[i]:
                        continue
                    for j in range(i + 1, len(names)):
                        if not names[j]:
                            continue
                        if sids[i] == sids[j]:
                            continue
                        score = fuzz.token_sort_ratio(names[i], names[j])
                        if score >= 92:
                            flagged_pairs.add((sids[i], sids[j], score))
                            flagged_pairs.add((sids[j], sids[i], score))

            if flagged_pairs:
                for sid1, sid2, score in flagged_pairs:
                    mask = unified_df["Star ID"] == sid1
                    unified_df.loc[mask, "CROSS_ID_DUPLICATE_SUSPECT"] = True
                    existing = unified_df.loc[mask, "CROSS_ID_DUPLICATE_NOTE"].iloc[0] if mask.any() else ""
                    note = f"Similar to Star ID {sid2} (possible match={score}%)"
                    if existing and note not in existing:
                        note = existing + "; " + note
                    unified_df.loc[mask, "CROSS_ID_DUPLICATE_NOTE"] = note

    except Exception:
        pass

    return unified_df


def resolve_star_ids(training_df, manpower_df):
    """Run the full 7-pass identity resolution pipeline.
    FIXED: Real name validation on exact matches, cross-ID duplicate detection,
    training orphan detection.
    """
    with Timer("Identity Resolution Pipeline"):
        indexes = _build_indexes(manpower_df)
        roster_star_ids = set(indexes["star_id_map"].keys())

        log_pipeline_event(
            f"Built indexes: {len(indexes['star_id_map'])} Star IDs, "
            f"{len(indexes['dealer_group'])} dealer groups, "
            f"{len(indexes['roster_records'])} roster records"
        )

        matched_roster_ids = set()
        matched_results = []
        pass_counts = defaultdict(int)
        confidence_counts = defaultdict(int)

        total = len(training_df)
        for idx, row in training_df.iterrows():
            t_dict = row.to_dict()
            match = _match_row(t_dict, indexes)

            merged = dict(t_dict)
            if match["_matched_rec"]:
                rec = match["_matched_rec"]
                for col in ROSTER_COLUMNS:
                    if col not in merged or pd.isna(merged.get(col)):
                        merged[col] = rec.get(col)
                matched_roster_ids.add(rec.get("_star_id_clean"))
                if not merged.get("Star ID") or str(merged.get("Star ID")).strip() in ("", "nan"):
                    merged["Star ID"] = rec.get("Star ID")
            else:
                # Training orphan: Star ID in training but NOT in roster
                t_sid = clean_star_id(t_dict.get("Star ID"))
                if t_sid and t_sid not in roster_star_ids:
                    match["Match_Method"] = "PASS7_NO_ROSTER_MATCH"
                    match["Match_Confidence"] = "UNRESOLVED"
                    match["Matched_Candidate"] = "TRAINING_ORPHAN"

            merged["Match_Method"] = match["Match_Method"]
            merged["Match_Confidence"] = match["Match_Confidence"]
            merged["Fuzzy_Score"] = match["Fuzzy_Score"]
            merged["Phonetic_Score"] = match["Phonetic_Score"]
            merged["Matched_Candidate"] = match["Matched_Candidate"]

            merged["LAST MODEL TRAINED"] = _normalize_model_name(
                merged.get("LAST MODEL TRAINED")
            )

            matched_results.append(merged)
            pass_counts[match["Match_Method"]] += 1
            confidence_counts[match["Match_Confidence"]] += 1

        for method, count in pass_counts.items():
            log_match_event(method, count)

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

        if not df_unmatched.empty:
            unified_df = pd.concat([df_matched, df_unmatched], ignore_index=True)
        else:
            unified_df = df_matched.copy()

        # ── Post-processing ──────────────────────────────────────────────
        unified_df["pre_score"] = unified_df.get("SKILL LEVEL - PRE", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)
        unified_df["post_score"] = unified_df.get("SKILL LEVEL - POST", pd.Series(dtype="object")).map(SKILL_SCORE_MAP).fillna(-1).astype(int)

        unified_df["SKILL_REGRESSION_FLAG"] = (
            (unified_df["pre_score"] >= 0) &
            (unified_df["post_score"] >= 0) &
            (unified_df["post_score"] < unified_df["pre_score"])
        )

        if "Joining Date" in unified_df.columns:
            try:
                jd = pd.to_datetime(unified_df["Joining Date"], errors="coerce")
                unified_df["FUTURE_JOINING_FLAG"] = jd.dt.year > 2026
            except Exception:
                unified_df["FUTURE_JOINING_FLAG"] = False
        else:
            unified_df["FUTURE_JOINING_FLAG"] = False

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

        # ── Technician Enrichment Columns ─────────────────────────────────
        # Age from DOB
        if "DOB" in unified_df.columns:
            try:
                dob_series = pd.to_datetime(unified_df["DOB"], errors="coerce")
                today = pd.Timestamp("today").normalize()
                unified_df["Age"] = ((today - dob_series).dt.days / 365.25).round(0).astype("Int64")
            except Exception:
                unified_df["Age"] = pd.NA

        # Modules trained and training history count per Star ID
        if "Star ID" in unified_df.columns:
            product_col = next(
                (c for c in ["PRODUCT TRAINED ON", "Product Trained On", "PRODUCT_TRAINED_ON"]
                 if c in unified_df.columns),
                None,
            )
            grouped_sid = unified_df.groupby("Star ID")

            # Modules: unique non-null product values joined as a string
            if product_col:
                modules_map = grouped_sid[product_col].apply(
                    lambda s: ", ".join(sorted(s.dropna().astype(str).unique()))
                )
                unified_df["Modules_Trained"] = unified_df["Star ID"].map(modules_map)
            else:
                unified_df["Modules_Trained"] = ""

            # Training history count: rows with a Training year value per Star ID
            if "Training year" in unified_df.columns:
                history_map = (
                    unified_df[unified_df["Training year"].notna()]
                    .groupby("Star ID")["Training year"]
                    .count()
                )
                unified_df["Training_History_Count"] = (
                    unified_df["Star ID"].map(history_map).fillna(0).astype(int)
                )
            else:
                unified_df["Training_History_Count"] = 0

        # ── Cross-ID Duplicate Detection ─────────────────────────────────
        unified_df = _detect_cross_id_duplicates(unified_df)

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
            "cross_id_duplicate_count": int(unified_df["CROSS_ID_DUPLICATE_SUSPECT"].sum()),
        }

        log_pipeline_event(
            f"Pipeline complete: {stats['total_master_count']} rows, "
            f"{stats['matched_count']} matched, "
            f"{stats['unresolved_count']} unresolved"
        )

        return unified_df, stats
