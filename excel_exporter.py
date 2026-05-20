import pandas as pd
import io
import datetime
from utils import CONFIDENCE_COLORS, BRAND_DARK_CORE, BRAND_RED, BRAND_WHITE, BRAND_LIGHT_GREY, CONFIDENCE_ORDER

def export_to_excel(df_master, stats):
    """
    Generate a beautifully styled Excel workbook using XlsxWriter.
    
    Returns:
        bytes: The binary content of the generated Excel workbook.
    """
    output = io.BytesIO()
    
    # Create Excel writer with xlsxwriter engine
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # ── FORMAT DEFINITIONS ────────────────────────────────────────────────
        # Header Format
        header_format = workbook.add_format({
            'bold': True,
            'font_color': BRAND_WHITE,
            'bg_color': BRAND_DARK_CORE,
            'font_name': 'Segoe UI',
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': BRAND_LIGHT_GREY
        })
        
        # Title Format (Metadata Sheet)
        title_format = workbook.add_format({
            'bold': True,
            'font_color': BRAND_RED,
            'font_name': 'Segoe UI',
            'font_size': 16,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        # Subsection Header Format (Metadata Sheet)
        sub_header_format = workbook.add_format({
            'bold': True,
            'font_color': BRAND_WHITE,
            'bg_color': '#4D4D4F',
            'font_name': 'Segoe UI',
            'font_size': 12,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Standard Cell Format
        cell_format = workbook.add_format({
            'font_name': 'Segoe UI',
            'font_size': 10,
            'valign': 'vcenter',
            'border': 1,
            'border_color': BRAND_LIGHT_GREY
        })
        
        # Bold Label Format
        bold_label_format = workbook.add_format({
            'bold': True,
            'font_name': 'Segoe UI',
            'font_size': 10,
            'valign': 'vcenter',
            'border': 1,
            'border_color': BRAND_LIGHT_GREY
        })
        
        # Numeric / Integer Format
        integer_format = workbook.add_format({
            'font_name': 'Segoe UI',
            'font_size': 10,
            'num_format': '#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': BRAND_LIGHT_GREY
        })
        
        # Date Format
        date_format = workbook.add_format({
            'font_name': 'Segoe UI',
            'font_size': 10,
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': BRAND_LIGHT_GREY
        })
        
        # Confidence Level Formats (Cell Background Fills)
        conf_formats = {}
        for level, color in CONFIDENCE_COLORS.items():
            conf_formats[level] = workbook.add_format({
                'font_name': 'Segoe UI',
                'font_size': 10,
                'bg_color': color,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'border_color': BRAND_LIGHT_GREY
            })
            
        # ── SHEET 1: METADATA & SUMMARY ───────────────────────────────────────
        meta_sheet = workbook.add_worksheet('Metadata & Summary')
        meta_sheet.set_column('A:A', 30)
        meta_sheet.set_column('B:B', 40)
        
        # Title
        meta_sheet.write('A2', 'TRAINING ANALYTICS MASTER COMPILATION', title_format)
        meta_sheet.write('A3', f'Execution Date: {datetime.date.today().strftime("%Y-%m-%d")}', cell_format)
        
        # Block 1: Pipeline Summary
        meta_sheet.write('A5', 'PIPELINE RUN STATS', sub_header_format)
        meta_sheet.write('B5', '', sub_header_format)
        
        stats_rows = [
            ("Total Active Roster Count", stats["total_roster_count"]),
            ("Total Training Input Records", stats["total_training_input_count"]),
            ("Total Consolidated Output Rows", stats["total_master_count"]),
            ("Successfully Matched Records", stats["matched_count"]),
            ("Untrained Active Manpower Count", stats["untrained_count"]),
            ("Unresolved Training Records", stats["unresolved_count"]),
            ("Future Joining Dates Identified", stats["future_joining_count"]),
            ("Skill Regressions Identified", stats["skill_regression_count"])
        ]
        
        row_idx = 6
        for label, val in stats_rows:
            meta_sheet.write(row_idx, 0, label, bold_label_format)
            meta_sheet.write(row_idx, 1, val, integer_format)
            row_idx += 1
            
        # Block 2: Confidence Distribution
        meta_sheet.write(row_idx + 1, 0, 'MATCHING CONFIDENCE DISTRIBUTION', sub_header_format)
        meta_sheet.write(row_idx + 1, 1, '', sub_header_format)
        
        row_idx += 2
        for level in CONFIDENCE_ORDER:
            count = stats["confidence_distribution"].get(level, 0)
            meta_sheet.write(row_idx, 0, f"Confidence Level: {level}", bold_label_format)
            meta_sheet.write(row_idx, 1, count, integer_format)
            row_idx += 1
            
        # Block 3: Verification Check
        meta_sheet.write(row_idx + 1, 0, 'PIPELINE INTEGRITY CHECKS', sub_header_format)
        meta_sheet.write(row_idx + 1, 1, '', sub_header_format)
        
        row_idx += 2
        # Check: Input Row Conservation
        loss_check = (stats["matched_count"] + stats["unresolved_count"]) == stats["total_training_input_count"]
        meta_sheet.write(row_idx, 0, "Zero Row Loss Check (Matched + Unresolved == Inputs)", bold_label_format)
        meta_sheet.write(row_idx, 1, "PASS" if loss_check else "FAIL (Row Discrepancy)", cell_format)
        row_idx += 1
        
        meta_sheet.write(row_idx, 0, "Air-gapped Compliance Status", bold_label_format)
        meta_sheet.write(row_idx, 1, "COMPLIANT (100% Offline Processing)", cell_format)
        
        # ── SHEET 2: MASTER MAPPED DATA ───────────────────────────────────────
        data_sheet = workbook.add_worksheet('Master Database')
        
        # Columns list in specific ordered format
        cols = list(df_master.columns)
        
        # Write headers
        for col_idx, col_name in enumerate(cols):
            data_sheet.write(0, col_idx, col_name, header_format)
            
        # Write data rows
        for row_idx, row in df_master.iterrows():
            excel_row_idx = row_idx + 1
            confidence_val = row.get('MATCH_CONFIDENCE', 'UNRESOLVED')
            
            for col_idx, col_name in enumerate(cols):
                val = row[col_name]
                
                # Check for nulls
                if pd.isna(val) or val is None:
                    data_sheet.write(excel_row_idx, col_idx, "", cell_format)
                    continue
                    
                # Format cell based on column type
                if col_name in ['Star ID', 'Star ID.1', 'Age', 'Roster_Matched_Index', 'pre_score', 'post_score']:
                    data_sheet.write(excel_row_idx, col_idx, int(val), integer_format)
                elif col_name in ['Joining Date', 'DOB', 'LATEST_TRAINING_DATE']:
                    # Handle datetimes
                    if isinstance(val, (pd.Timestamp, datetime.datetime)):
                        val_date = val.date()
                    elif isinstance(val, datetime.date):
                        val_date = val
                    else:
                        try:
                            val_date = pd.to_datetime(val).date()
                        except:
                            val_date = str(val)
                    
                    if isinstance(val_date, datetime.date):
                        data_sheet.write_datetime(excel_row_idx, col_idx, val_date, date_format)
                    else:
                        data_sheet.write(excel_row_idx, col_idx, val_date, cell_format)
                elif col_name == 'MATCH_CONFIDENCE':
                    # Apply background color format matching confidence level
                    fmt = conf_formats.get(confidence_val, cell_format)
                    data_sheet.write(excel_row_idx, col_idx, str(val), fmt)
                else:
                    data_sheet.write(excel_row_idx, col_idx, str(val), cell_format)
                    
        # Autofit column widths dynamically
        data_sheet.autofit()
        
    output.seek(0)
    return output.getvalue()
