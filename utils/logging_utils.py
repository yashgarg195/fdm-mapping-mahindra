"""
Logging Utilities — Structured logging for ETL, matching, and export events.
All logs go to Python's standard logging module for traceability.
"""
import logging
import time
from datetime import datetime


def get_logger(name):
    """Get or create a named logger with a standard format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# Module-level loggers
_etl_logger = get_logger("ETL")
_match_logger = get_logger("MATCHING")
_export_logger = get_logger("EXPORT")
_pipeline_logger = get_logger("PIPELINE")


def log_etl_event(rows_in, rows_out, duration_seconds, source=""):
    """Log an ETL processing event with row counts and timing."""
    _etl_logger.info(
        "ETL [%s] | Rows In: %d | Rows Out: %d | Duration: %.2fs | Row Loss: %d",
        source, rows_in, rows_out, duration_seconds, rows_in - rows_out,
    )
    if rows_in != rows_out:
        _etl_logger.warning(
            "ROW MISMATCH DETECTED: %d rows lost during ETL for source '%s'",
            rows_in - rows_out, source,
        )


def log_match_event(method, count, avg_score=0.0):
    """Log a matching pass result."""
    _match_logger.info(
        "Match Pass [%s] | Matched: %d | Avg Score: %.1f",
        method, count, avg_score,
    )


def log_export_event(sheets, row_counts):
    """Log an Excel export event.
    
    Args:
        sheets: list of sheet names
        row_counts: dict of {sheet_name: row_count}
    """
    total = sum(row_counts.values())
    _export_logger.info(
        "Excel Export | Sheets: %d | Total Rows: %d | Sheets: %s",
        len(sheets), total, ", ".join(sheets),
    )


def log_pipeline_event(message, level="info"):
    """Log a generic pipeline event."""
    getattr(_pipeline_logger, level, _pipeline_logger.info)(message)


class Timer:
    """Context manager for timing code blocks.
    
    Usage:
        with Timer("ETL processing") as t:
            do_work()
        print(t.elapsed)  # seconds as float
    """

    def __init__(self, label=""):
        self.label = label
        self.elapsed = 0.0
        self._start = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self._start
        if self.label:
            _pipeline_logger.info("%s completed in %.2fs", self.label, self.elapsed)


def build_audit_entry(event_type, description, rows_affected=0, details=None):
    """Create a standardized audit log entry dict.
    
    Returns dict with: timestamp, event_type, description, rows_affected, details
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "description": description,
        "rows_affected": rows_affected,
        "details": str(details) if details else "",
    }
