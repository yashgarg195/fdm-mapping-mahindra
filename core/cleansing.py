"""
Cleansing Module — Name normalization, contact cleaning, Aadhar parsing,
abbreviation expansion. All functions are null-safe.
"""
import re
import numpy as np
import pandas as pd
from config.constants import NAME_ABBREVIATIONS


def normalize_name(name):
    """Standardize a name string for matching.
    Steps: uppercase, remove titles, remove non-alphanumeric except spaces,
    collapse whitespace, expand abbreviations, strip.
    Returns original value if None/empty.
    """
    if name is None or (isinstance(name, float) and np.isnan(name)):
        return None
    try:
        s = str(name).strip()
        if not s or s.upper() in ("NAN", "NONE", ""):
            return None
        # Uppercase
        s = s.upper()
        # Remove common titles
        s = re.sub(
            r"\b(MR|MRS|MS|MISS|SHRI|SMT|DR|PROF|SH)\b\.?\s*",
            " ", s
        )
        # Remove non-alphanumeric except spaces
        s = re.sub(r"[^A-Z0-9\s]", " ", s)
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip()
        # Expand abbreviations
        s = expand_abbreviations(s, NAME_ABBREVIATIONS)
        return s if s else None
    except Exception:
        return str(name).strip().upper() if name else None


def normalize_contact(contact):
    """Normalize a contact number to a 10-digit string.
    Strips .0 suffix, extracts digits, validates length.
    Returns None if invalid.
    """
    if contact is None or (isinstance(contact, float) and np.isnan(contact)):
        return None
    try:
        s = str(contact).strip()
        # Remove .0 suffix from float representation
        if s.endswith(".0"):
            s = s[:-2]
        # Extract digits only
        digits = re.sub(r"[^0-9]", "", s)
        # Remove leading country code (91) if 12 digits
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        if len(digits) == 10:
            return digits
        return None
    except Exception:
        return None


def normalize_dealership(name):
    """Clean a dealership name. Uppercase, strip, collapse spaces."""
    if name is None or (isinstance(name, float) and np.isnan(name)):
        return None
    try:
        s = str(name).strip().upper()
        s = re.sub(r"\s+", " ", s)
        return s if s and s not in ("NAN", "NONE") else None
    except Exception:
        return None


def normalize_aadhar(val):
    """Parse an Aadhar number to a 12-digit string.
    Handles scientific notation (e.g. 9.51881e+11), floats, ints.
    Returns None if not exactly 12 digits.
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        s = str(val).strip()
        if not s or s.upper() in ("NAN", "NONE", ""):
            return None
        # Handle scientific notation by converting to int first
        if "e" in s.lower() or "E" in s:
            s = str(int(float(s)))
        # Remove .0 suffix
        if s.endswith(".0"):
            s = s[:-2]
        # Extract digits
        digits = re.sub(r"[^0-9]", "", s)
        if len(digits) == 12:
            return digits
        return None
    except Exception:
        return None


def normalize_dealer_code(code):
    """Clean a dealer code. Uppercase, strip."""
    if code is None or (isinstance(code, float) and np.isnan(code)):
        return None
    try:
        s = str(code).strip().upper()
        return s if s and s not in ("NAN", "NONE") else None
    except Exception:
        return None


def expand_abbreviations(text, abbrev_dict):
    """Expand abbreviations in text using a word-by-word dictionary lookup.
    Returns expanded text. Null-safe.
    """
    if not text or not abbrev_dict:
        return text
    try:
        words = str(text).split()
        expanded = []
        for word in words:
            replacement = abbrev_dict.get(word, word)
            if replacement:  # Skip empty replacements (titles stripped)
                expanded.append(replacement)
        return " ".join(expanded)
    except Exception:
        return text


def clean_star_id(val):
    """Parse a Star ID to integer. Returns None if invalid."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        s = str(val).strip()
        if s.endswith(".0"):
            s = s[:-2]
        s = re.sub(r"[^0-9]", "", s)
        if s:
            return int(s)
        return None
    except Exception:
        return None
