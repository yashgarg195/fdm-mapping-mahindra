"""
Fuzzy Matching Module — String similarity scoring using rapidfuzz and jellyfish.
All functions return 0 on None/empty input. Never raises.
"""
from rapidfuzz import fuzz
import jellyfish
from config.settings import COMPOSITE_WEIGHT_FUZZY, COMPOSITE_WEIGHT_PHONETIC


def fuzzy_name_match(name_a, name_b):
    """Compute fuzzy string match score between two names.
    Uses rapidfuzz: token_sort_ratio (weight 0.6) + partial_ratio (weight 0.4).
    Returns float score 0-100. Returns 0 if either name is None/empty.
    """
    if not name_a or not name_b:
        return 0.0
    try:
        a = str(name_a).strip().upper()
        b = str(name_b).strip().upper()
        if not a or not b:
            return 0.0
        token_sort = fuzz.token_sort_ratio(a, b)
        partial = fuzz.partial_ratio(a, b)
        return round(token_sort * 0.6 + partial * 0.4, 2)
    except Exception:
        return 0.0


def phonetic_match(name_a, name_b):
    """Compute phonetic similarity score between two names.
    Uses jellyfish: metaphone (50pts) + soundex (30pts) + jaro_winkler (20pts).
    Returns float score 0-100. Returns 0 if either name is None/empty.
    """
    if not name_a or not name_b:
        return 0.0
    try:
        a = str(name_a).strip().upper()
        b = str(name_b).strip().upper()
        if not a or not b:
            return 0.0

        score = 0.0

        # Metaphone comparison (50 points if match)
        try:
            meta_a = jellyfish.metaphone(a)
            meta_b = jellyfish.metaphone(b)
            if meta_a and meta_b and meta_a == meta_b:
                score += 50.0
        except Exception:
            pass

        # Soundex comparison (30 points if match)
        try:
            sx_a = jellyfish.soundex(a)
            sx_b = jellyfish.soundex(b)
            if sx_a and sx_b and sx_a == sx_b:
                score += 30.0
        except Exception:
            pass

        # Jaro-Winkler similarity (up to 20 points)
        try:
            jw = jellyfish.jaro_winkler_similarity(a, b)
            score += jw * 20.0
        except Exception:
            pass

        return round(min(score, 100.0), 2)
    except Exception:
        return 0.0


def composite_score(fuzzy_score, phonetic_score, weights=None):
    """Compute weighted composite score from fuzzy and phonetic scores.
    Uses COMPOSITE_WEIGHT_FUZZY and COMPOSITE_WEIGHT_PHONETIC from settings
    unless custom weights are provided.
    Returns float 0-100.
    """
    try:
        f = float(fuzzy_score) if fuzzy_score else 0.0
        p = float(phonetic_score) if phonetic_score else 0.0
        if weights:
            w_f = weights.get("fuzzy", COMPOSITE_WEIGHT_FUZZY)
            w_p = weights.get("phonetic", COMPOSITE_WEIGHT_PHONETIC)
        else:
            w_f = COMPOSITE_WEIGHT_FUZZY
            w_p = COMPOSITE_WEIGHT_PHONETIC
        result = f * w_f + p * w_p
        return round(min(max(result, 0.0), 100.0), 2)
    except Exception:
        return 0.0
