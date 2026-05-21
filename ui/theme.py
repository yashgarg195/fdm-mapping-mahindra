"""Shared Streamlit UI helpers for the neutral enterprise dashboard theme."""
import html


NEUTRAL = {
    "ink": "#111827",
    "muted": "#64748b",
    "subtle": "#94a3b8",
    "line": "#e2e8f0",
    "panel": "#ffffff",
    "page": "#f5f7fb",
    "soft": "#f8fafc",
    "accent": "#475569",
    "accent_2": "#2563eb",
    "success": "#15803d",
    "warning": "#b45309",
    "danger": "#b91c1c",
    "info": "#0369a1",
}

CHART_COLORS = {
    "trained": "#2563eb",
    "untrained": "#cbd5e1",
    "pending": "#f59e0b",
    "high": "#16a34a",
    "medium": "#2563eb",
    "low": "#f59e0b",
    "unresolved": "#ef4444",
    "l1": "#94a3b8",
    "l2": "#60a5fa",
    "l3": "#22c55e",
    "l4": "#0f766e",
}

CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", color=NEUTRAL["ink"], size=12),
    margin=dict(t=36, b=24, l=24, r=24),
)


def section_header(title, subtitle=""):
    """Return compact section header HTML."""
    subtitle_html = ""
    if subtitle:
        subtitle_html = (
            f"<div style='color:{NEUTRAL['muted']}; font-size:0.86rem; "
            f"margin-top:3px;'>{html.escape(subtitle)}</div>"
        )
    return (
        f"<div class='dash-section-heading'>"
        f"<div class='dash-section-title'>{html.escape(title)}</div>"
        f"{subtitle_html}"
        f"</div>"
    )


def kpi_card(label, value, helper="", tone="accent"):
    """Return a neutral KPI card with optional tone accent."""
    color = NEUTRAL.get(tone, CHART_COLORS.get(tone, NEUTRAL["accent"]))
    helper_html = html.escape(str(helper)) if helper else ""
    return (
        "<div class='metric-card'>"
        f"<div class='metric-topline'><span>{html.escape(str(label))}</span>"
        f"<span style='background:{color};'></span></div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div>"
        f"<div class='metric-helper'>{helper_html}</div>"
        "</div>"
    )


def callout(title, body, tone="info"):
    """Return an understated guidance panel."""
    color = NEUTRAL.get(tone, CHART_COLORS.get(tone, NEUTRAL["info"]))
    return (
        f"<div class='dash-callout' style='border-left-color:{color};'>"
        f"<div class='dash-callout-title'>{html.escape(str(title))}</div>"
        f"<div class='dash-callout-body'>{html.escape(str(body))}</div>"
        "</div>"
    )


def label_value(label, value, tone="accent"):
    """Return a compact stat row."""
    color = NEUTRAL.get(tone, CHART_COLORS.get(tone, NEUTRAL["accent"]))
    return (
        "<div class='label-value-row'>"
        f"<span>{html.escape(str(label))}</span>"
        f"<strong style='color:{color};'>{html.escape(str(value))}</strong>"
        "</div>"
    )
