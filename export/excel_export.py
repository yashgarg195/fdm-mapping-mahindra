"""
Excel Export Module — Generates 8-sheet styled Excel workbook via BytesIO.
Never writes to disk. Uses XlsxWriter engine.
"""
import io
import datetime
import pandas as pd
import numpy as np
from config.constants import BRAND_RED, CONFIDENCE_ORDER, CONFIDENCE_COLORS


def _safe_val(val):
    """Convert a value to an Excel-safe type."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    if isinstance(val, (pd.Timestamp, datetime.datetime)):
        return val.strftime("%Y-%m-%d") if not pd.isna(val) else ""
    if isinstance(val, datetime.date):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, bool):
        return "YES" if val else "NO"
    return val


def generate_excel_report(unified_df, backlog_df=None, duplicate_df=None, audit_log=None):
    """Generate an 8-sheet Excel workbook and return as io.BytesIO.
    Never writes to disk.
    """
    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book

        # ── Formats ─────────────────────────────────────────────────────────
        header_fmt = wb.add_format({
            "bold": True, "font_color": "#FFFFFF", "bg_color": BRAND_RED,
            "font_name": "Calibri", "font_size": 11, "border": 1,
            "text_wrap": True, "valign": "vcenter",
        })
        cell_fmt = wb.add_format({"font_name": "Calibri", "font_size": 10, "border": 1})
        int_fmt = wb.add_format({"font_name": "Calibri", "font_size": 10, "num_format": "#,##0", "border": 1})
        date_fmt = wb.add_format({"font_name": "Calibri", "font_size": 10, "num_format": "yyyy-mm-dd", "border": 1})
        red_fill = wb.add_format({"bg_color": "#FFCCCC", "font_name": "Calibri", "font_size": 10, "border": 1})
        amber_fill = wb.add_format({"bg_color": "#FFE0A0", "font_name": "Calibri", "font_size": 10, "border": 1})
        red_text = wb.add_format({"font_color": "#CC0000", "font_name": "Calibri", "font_size": 10, "bold": True, "border": 1})

        conf_fmts = {}
        for level, color in CONFIDENCE_COLORS.items():
            conf_fmts[level] = wb.add_format({"bg_color": color, "font_name": "Calibri", "font_size": 10, "border": 1})

        date_cols = {"Joining Date", "DOB", "LATEST_TRAINING_DATE"}
        int_cols = {"Star ID", "Age", "pre_score", "post_score", "Backlog_Rank", "Nomination_Rank"}

        def _write_sheet(df, sheet_name, tab_color=None, conf_col=None, pending_col=None):
            """Write a DataFrame to a sheet with formatting."""
            if df is None or df.empty:
                ws = wb.add_worksheet(sheet_name)
                if tab_color:
                    ws.set_tab_color(tab_color)
                ws.write(0, 0, "No data available", cell_fmt)
                return

            df_out = df.copy()
            df_out.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
            ws = writer.sheets[sheet_name]
            if tab_color:
                ws.set_tab_color(tab_color)

            # Write headers
            for col_idx, col_name in enumerate(df_out.columns):
                ws.write(0, col_idx, str(col_name), header_fmt)

            # Write data with formatting
            for row_idx in range(len(df_out)):
                for col_idx, col_name in enumerate(df_out.columns):
                    val = _safe_val(df_out.iloc[row_idx, col_idx])
                    fmt = cell_fmt

                    if col_name in date_cols:
                        fmt = date_fmt
                    elif col_name in int_cols:
                        fmt = int_fmt
                        try:
                            val = int(float(val)) if val != "" else ""
                        except (ValueError, TypeError):
                            pass
                    elif conf_col and col_name == conf_col:
                        fmt = conf_fmts.get(str(val).strip(), cell_fmt)
                    elif pending_col and col_name == pending_col:
                        try:
                            months = int(float(val))
                            if months >= 12:
                                fmt = red_fill
                            elif months >= 6:
                                fmt = amber_fill
                        except (ValueError, TypeError):
                            pass

                    ws.write(row_idx + 1, col_idx, val, fmt)

            # Auto-fit columns (approximate)
            for col_idx, col_name in enumerate(df_out.columns):
                max_len = max(
                    len(str(col_name)),
                    df_out.iloc[:, col_idx].astype(str).str.len().max() if len(df_out) > 0 else 0
                )
                ws.set_column(col_idx, col_idx, min(max_len + 2, 40))

            # Freeze top row & autofilter
            ws.freeze_panes(1, 0)
            if len(df_out.columns) > 0:
                ws.autofilter(0, 0, len(df_out), len(df_out.columns) - 1)

        # ── Sheet 1: Unified_Master ─────────────────────────────────────────
        _write_sheet(unified_df, "Unified_Master", tab_color=BRAND_RED, conf_col="Match_Confidence")

        # ── Sheet 2: Pending_Backlog ────────────────────────────────────────
        if backlog_df is not None and not backlog_df.empty:
            bl = backlog_df.sort_values("Backlog_Rank") if "Backlog_Rank" in backlog_df.columns else backlog_df
        else:
            bl = pd.DataFrame()
        _write_sheet(bl, "Pending_Backlog", tab_color="#FF8C00", pending_col="Pending_Age_Months")

        # ── Sheet 3: Duplicate_Log ──────────────────────────────────────────
        _write_sheet(duplicate_df, "Duplicate_Log", tab_color="#FFD700")

        # ── Sheet 4: Mapping_Confidence ─────────────────────────────────────
        if unified_df is not None and not unified_df.empty:
            mc_cols = [c for c in ["Star ID", "Name", "Dealer Code", "Dealer Name",
                       "Match_Method", "Match_Confidence", "Fuzzy_Score",
                       "Phonetic_Score", "Matched_Candidate"] if c in unified_df.columns]
            mc_df = unified_df[mc_cols] if mc_cols else pd.DataFrame()
        else:
            mc_df = pd.DataFrame()
        _write_sheet(mc_df, "Mapping_Confidence", tab_color="#4D4D4F", conf_col="Match_Confidence")

        # ── Sheet 5: Data_Quality_Report ────────────────────────────────────
        dq_rows = []
        if unified_df is not None and not unified_df.empty:
            if "FUTURE_JOINING_FLAG" in unified_df.columns:
                for _, row in unified_df[unified_df["FUTURE_JOINING_FLAG"] == True].iterrows():
                    dq_rows.append({"Star ID": row.get("Star ID"), "Name": row.get("Name"),
                                    "Dealer Code": row.get("Dealer Code"), "Issue_Type": "FUTURE_DATE",
                                    "Issue_Description": f"Joining Date: {row.get('Joining Date')}"})
            if "SKILL_REGRESSION_FLAG" in unified_df.columns:
                for _, row in unified_df[unified_df["SKILL_REGRESSION_FLAG"] == True].iterrows():
                    dq_rows.append({"Star ID": row.get("Star ID"), "Name": row.get("Name"),
                                    "Dealer Code": row.get("Dealer Code"), "Issue_Type": "SKILL_REGRESSION",
                                    "Issue_Description": f"Post < Pre"})
            missing = unified_df[unified_df["Name"].isna() | (unified_df["Name"].astype(str).str.strip() == "")]
            for _, row in missing.head(100).iterrows():
                dq_rows.append({"Star ID": row.get("Star ID"), "Name": "",
                                "Dealer Code": row.get("Dealer Code"), "Issue_Type": "MISSING_NAME",
                                "Issue_Description": "Employee name missing"})
        dq_df = pd.DataFrame(dq_rows) if dq_rows else pd.DataFrame()
        _write_sheet(dq_df, "Data_Quality_Report", tab_color="#4D4D4F")

        # ── Sheet 6: Skill_Analytics ────────────────────────────────────────
        if unified_df is not None and not unified_df.empty and "Training year" in unified_df.columns:
            sk = unified_df[unified_df["Training year"].notna()].copy()
            sk_cols = [c for c in ["Star ID", "Name", "Designation", "Dealer Name",
                       "Training year", "SKILL LEVEL - PRE", "SKILL LEVEL - POST",
                       "pre_score", "post_score", "VALIDATED_SKILL_LEVEL"] if c in sk.columns]
            if "pre_score" in sk.columns and "post_score" in sk.columns:
                sk["Skill_Delta"] = sk["post_score"] - sk["pre_score"]
                sk_cols.append("Skill_Delta")
            sk_df = sk[sk_cols] if sk_cols else pd.DataFrame()
        else:
            sk_df = pd.DataFrame()
        _write_sheet(sk_df, "Skill_Analytics", tab_color="#4D4D4F")

        # ── Sheet 7: Recall_Action_List ─────────────────────────────────────
        if backlog_df is not None and not backlog_df.empty:
            ral = backlog_df.sort_values("Training_Priority_Score", ascending=False) if "Training_Priority_Score" in backlog_df.columns else backlog_df
            ral_cols = [c for c in ["Nomination_Rank", "Star ID", "Name", "Designation",
                        "Dealer Code", "Dealer Name", "Zone", "State",
                        "Pending_Age_Months", "Training_Priority_Score", "Training_Status"]
                        if c in ral.columns]
            ral_df = ral[ral_cols] if ral_cols else ral
        else:
            ral_df = pd.DataFrame()
        _write_sheet(ral_df, "Recall_Action_List", tab_color="#4D4D4F")

        # ── Sheet 8: Audit_Log ──────────────────────────────────────────────
        if audit_log:
            if isinstance(audit_log, list):
                al_df = pd.DataFrame(audit_log)
            elif isinstance(audit_log, pd.DataFrame):
                al_df = audit_log
            else:
                al_df = pd.DataFrame([{"timestamp": datetime.datetime.now().isoformat(),
                                       "event_type": "INFO", "description": "No audit events recorded",
                                       "rows_affected": 0, "details": ""}])
        else:
            al_df = pd.DataFrame([{"timestamp": datetime.datetime.now().isoformat(),
                                   "event_type": "INFO", "description": "No audit events recorded",
                                   "rows_affected": 0, "details": ""}])
        _write_sheet(al_df, "Audit_Log", tab_color="#4D4D4F")

    buf.seek(0)
    return buf
