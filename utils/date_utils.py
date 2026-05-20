"""
Date Utilities — Safe date parsing, fiscal year computation, elapsed months.
All functions are null-safe and never raise on bad input.
"""
import datetime
import pandas as pd
from config.constants import FY_CALENDAR


def parse_date_safe(value):
    """Parse a value into a datetime.date. Returns None on failure."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, pd.Timestamp):
        return value.date()
    try:
        s = str(value).strip()
        if not s or s.upper() in ("NAT", "NAN", "NONE", ""):
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
                    "%m/%d/%Y", "%d-%b-%Y", "%d %b %Y"):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return pd.to_datetime(s, errors="coerce").date()
    except Exception:
        return None


def get_financial_year(dt):
    """Return fiscal year string like 'FY2023-24' from a date.
    Indian fiscal year: April 1 → March 31.
    Returns None if dt is None.
    """
    if dt is None:
        return None
    if isinstance(dt, (pd.Timestamp, datetime.datetime)):
        dt = dt.date()
    if not isinstance(dt, datetime.date):
        dt = parse_date_safe(dt)
        if dt is None:
            return None
    if dt.month >= 4:
        start_year = dt.year
    else:
        start_year = dt.year - 1
    return f"FY{start_year}-{str(start_year + 1)[-2:]}"


def get_fy_short(dt):
    """Return short fiscal year string like 'F-25' from a date.
    Matches the format used in training data.
    Returns None if dt is None.
    """
    if dt is None:
        return None
    if isinstance(dt, (pd.Timestamp, datetime.datetime)):
        dt = dt.date()
    if not isinstance(dt, datetime.date):
        dt = parse_date_safe(dt)
        if dt is None:
            return None
    if dt.month >= 4:
        end_year = dt.year + 1
    else:
        end_year = dt.year
    return f"F-{str(end_year)[-2:]}"


def months_since(dt, reference=None):
    """Compute months elapsed between dt and reference date.
    Returns integer months. Returns None if dt is None.
    Uses 30.4375 days per month for consistency.
    """
    if dt is None:
        return None
    if reference is None:
        reference = datetime.date.today()
    if isinstance(dt, (pd.Timestamp, datetime.datetime)):
        dt = dt.date()
    if isinstance(reference, (pd.Timestamp, datetime.datetime)):
        reference = reference.date()
    if not isinstance(dt, datetime.date):
        dt = parse_date_safe(dt)
        if dt is None:
            return None
    delta = reference - dt
    return max(0, int(delta.days / 30.4375))


def fy_end_date(fy_label):
    """Given a fiscal year label like 'F-25', return the end date.
    Returns None if not found in FY_CALENDAR.
    """
    if fy_label is None:
        return None
    fy_label = str(fy_label).strip()
    entry = FY_CALENDAR.get(fy_label)
    if entry:
        return entry["end"]
    return None
