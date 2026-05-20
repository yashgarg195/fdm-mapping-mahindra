"""
TRAINING ANALYTICS & MANPOWER INTELLIGENCE PLATFORM
Settings — Tunable Parameters, Thresholds, Performance Flags

All configurable thresholds for fuzzy matching, scoring weights,
deduplication, and performance tuning are defined here.
"""

# ── FUZZY MATCHING THRESHOLDS ────────────────────────────────────────────────
FUZZY_PRIMARY_THRESHOLD   = 88   # token_sort_ratio minimum for PASS 3
FUZZY_SECONDARY_THRESHOLD = 75   # lower bound for PASS 3 LOW confidence
FUZZY_GLOBAL_THRESHOLD    = 90   # global name-only fallback (PASS 5B)
PHONETIC_JARO_THRESHOLD   = 0.85 # Jaro-Winkler minimum for PASS 5A
FUZZY_AO_THRESHOLD        = 85   # same-AO fuzzy match (PASS 5C)

# ── CONFIDENCE COMPOSITE SCORE THRESHOLDS ────────────────────────────────────
CONFIDENCE_THRESHOLD_HIGH   = 92
CONFIDENCE_THRESHOLD_MEDIUM = 80
CONFIDENCE_THRESHOLD_LOW    = 65
CONFIDENCE_THRESHOLD_FUZZY  = 50
# Below FUZZY threshold → UNRESOLVED

# ── SCORING WEIGHTS ──────────────────────────────────────────────────────────
COMPOSITE_WEIGHT_FUZZY    = 0.65  # weight for fuzzy string score
COMPOSITE_WEIGHT_PHONETIC = 0.35  # weight for phonetic score

# ── PRIORITY SCORING WEIGHTS (for nomination list) ──────────────────────────
PRIORITY_WEIGHT_PENDING_AGE     = 0.35
PRIORITY_WEIGHT_SKILL_GAP       = 0.25
PRIORITY_WEIGHT_PRODUCT_CRIT    = 0.20
PRIORITY_WEIGHT_DESIGNATION     = 0.10
PRIORITY_WEIGHT_DEALER_SHORTAGE = 0.10

# ── DEDUPLICATION THRESHOLDS ─────────────────────────────────────────────────
DEDUP_NAME_THRESHOLD      = 95   # fuzzy score to flag potential duplicate name
DEDUP_COMPOSITE_THRESHOLD = 90   # composite score to flag

# ── SPECIALIST SHORTAGE ──────────────────────────────────────────────────────
MIN_L3_L4_PER_DEALERSHIP = 2   # minimum L3/L4 specialists expected per dealer

# ── PERFORMANCE FLAGS ────────────────────────────────────────────────────────
ETL_TIMEOUT_SECONDS         = 30   # maximum allowed ETL duration
ENABLE_GLOBAL_FUZZY_PASS    = True # whether to enable PASS 5B (expensive)
MAX_CANDIDATES_PER_MATCH    = 10   # max candidates to evaluate in fuzzy passes
INCLUDE_LOW_IN_KPIS         = False  # include LOW confidence matches in KPIs
INCLUDE_FUZZY_IN_KPIS       = False  # include FUZZY confidence matches in KPIs

# ── BACKLOG / NOMINATION SETTINGS ────────────────────────────────────────────
DEFAULT_NOMINATION_TOP_N    = 100  # default nomination list size
PENDING_AGE_CRITICAL_MONTHS = 12   # months after which pending becomes critical
PENDING_AGE_WARNING_MONTHS  = 6    # months after which pending becomes warning

# ── RECORDLINKAGE SETTINGS ──────────────────────────────────────────────────
RECORDLINKAGE_SCORE_HIGH  = 4.0
RECORDLINKAGE_SCORE_FUZZY = 2.5
