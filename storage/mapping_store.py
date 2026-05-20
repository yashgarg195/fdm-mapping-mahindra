"""
Mapping Store — In-memory SQLite persistence for resolved identity mappings.
Survives Streamlit tab switches within a single session.
"""
import sqlite3
import hashlib
import datetime
import pandas as pd
import streamlit as st


_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS resolved_mappings (
    training_row_hash TEXT PRIMARY KEY,
    star_id TEXT,
    match_method TEXT,
    match_confidence TEXT,
    fuzzy_score REAL,
    phonetic_score REAL,
    matched_candidate TEXT,
    resolved_at TEXT
)
"""

_COLUMNS = [
    "training_row_hash", "star_id", "match_method", "match_confidence",
    "fuzzy_score", "phonetic_score", "matched_candidate", "resolved_at",
]


@st.cache_resource
def get_connection():
    """Get or create the in-memory SQLite connection.
    Cached so it persists across reruns within the same session.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute(_TABLE_SCHEMA)
    conn.commit()
    return conn


def _row_hash(row_dict):
    """Generate a deterministic hash for a training row."""
    key_parts = [
        str(row_dict.get("Name", "")),
        str(row_dict.get("Dealer Code", "")),
        str(row_dict.get("Training year", "")),
        str(row_dict.get("LAST MODEL TRAINED", "")),
    ]
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()


def persist_mappings(mapping_df):
    """Upsert resolved mappings into the SQLite store.
    
    Args:
        mapping_df: DataFrame with columns matching the schema.
    """
    if mapping_df is None or mapping_df.empty:
        return

    conn = get_connection()
    now = datetime.datetime.now().isoformat()

    for _, row in mapping_df.iterrows():
        row_hash = _row_hash(row.to_dict())
        conn.execute(
            "INSERT OR REPLACE INTO resolved_mappings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row_hash,
                str(row.get("Star ID", row.get("Matched_Candidate", ""))),
                str(row.get("Match_Method", "")),
                str(row.get("Match_Confidence", "")),
                float(row.get("Fuzzy_Score", 0)),
                float(row.get("Phonetic_Score", 0)),
                str(row.get("Matched_Candidate", "")),
                now,
            ),
        )
    conn.commit()


def load_mappings():
    """Load all resolved mappings from the SQLite store.
    Returns DataFrame with standard columns.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM resolved_mappings", conn)
        if df.empty:
            return pd.DataFrame(columns=_COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=_COLUMNS)


def clear_mappings():
    """Delete all resolved mappings from the store."""
    conn = get_connection()
    conn.execute("DELETE FROM resolved_mappings")
    conn.commit()


def get_mapping_count():
    """Return count of resolved mappings in the store."""
    conn = get_connection()
    try:
        result = conn.execute("SELECT COUNT(*) FROM resolved_mappings").fetchone()
        return result[0] if result else 0
    except Exception:
        return 0
