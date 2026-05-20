import pandas as pd
import numpy as np
import datetime
from rapidfuzz import fuzz
import jellyfish
from recordlinkage import Index
import recordlinkage

from utils import (
    clean_name, clean_string, clean_dealer_code, clean_aadhar, clean_contact,
    get_skill_score, get_skill_label, calculate_recall_bucket,
    MODEL_NORMALISATION_MAP, CANONICAL_MODELS, MODEL_CATEGORY_MAP,
    CONFIDENCE_ORDER, FUZZY_PRIMARY_THRESHOLD, FUZZY_SECONDARY_THRESHOLD,
    RECORDLINKAGE_SCORE_HIGH, RECORDLINKAGE_SCORE_FUZZY, FY_CALENDAR
)

def run_matching_pipeline(df_roster_raw, df_training_raw, base_date=datetime.date(2026, 5, 20)):
    """
    Run the zero-loss ETL pipeline and multi-pass fuzzy matching engine.
    
    Inputs:
        df_roster_raw: DataFrame of active employees (Active Roster).
        df_training_raw: DataFrame of training logs.
        base_date: Date to calculate recall status relative to.
        
    Outputs:
        df_master: The fully mapped Master DataFrame (Roster left join Matched Training + Unresolved Training).
        stats: Dictionary containing matching metrics and execution summary.
    """
    # 1. Defensive Copies
    roster = df_roster_raw.copy()
    training = df_training_raw.copy()
    
    # Drop Star ID.1 duplicate columns immediately from both dataframes
    if 'Star ID.1' in roster.columns:
        roster.drop(columns=['Star ID.1'], inplace=True)
    if 'Star ID.1' in training.columns:
        training.drop(columns=['Star ID.1'], inplace=True)

    # Ensure required columns are present in roster
    roster_cols = ['Star ID', 'Zone', 'State', 'Dealer AO', 'Dealer Code', 'Dealer Name', 
                   'Dealer Operational Status', 'Location', 'Emp Code', 'Name', 
                   'Designation', 'Joining Date', 'Contact No', 'AadharCardNumber', 
                   'Gender', 'Father Name', 'DOB', 'Residence Location', 'Age']
    
    for col in roster_cols:
        if col not in roster.columns:
            roster[col] = np.nan

    # 2. Pre-process Roster to build indexes for fast matching
    roster['clean_Name'] = roster['Name'].apply(clean_name)
    roster['clean_Dealer_Code'] = roster['Dealer Code'].apply(clean_dealer_code)
    roster['clean_Emp_Code'] = roster['Emp Code'].apply(clean_string)
    roster['clean_Aadhar'] = roster['AadharCardNumber'].apply(clean_aadhar)
    roster['clean_Contact'] = roster['Contact No'].apply(clean_contact)
    
    # Cast Joining Date to datetime defensively
    roster['Joining Date'] = pd.to_datetime(roster['Joining Date'], errors='coerce')
    roster['DOB'] = pd.to_datetime(roster['DOB'], errors='coerce')
    
    # Indexes
    star_id_map = {}
    aadhar_map = {}
    emp_code_map = {}
    dealer_group = {}  # clean_dealer_code -> list of roster dictionaries
    roster_records = []
    
    for idx, row in roster.iterrows():
        r_dict = row.to_dict()
        r_dict['original_index'] = idx
        roster_records.append(r_dict)
        
        star_id = row['Star ID']
        if pd.notna(star_id):
            star_id_map[int(star_id)] = r_dict
            
        aadhar = row['clean_Aadhar']
        if aadhar:
            aadhar_map[aadhar] = r_dict
            
        emp_code = row['clean_Emp_Code']
        if emp_code:
            emp_code_map[emp_code] = r_dict
            
        dealer = row['clean_Dealer_Code']
        if dealer:
            if dealer not in dealer_group:
                dealer_group[dealer] = []
            dealer_group[dealer].append(r_dict)

    # 3. Match each training record
    matched_records = []
    
    # For stats tracking
    passes_count = {
        "Direct Star ID Match": 0,
        "Aadhar Card Match": 0,
        "Exact Emp Code Match": 0,
        "Exact Name & Dealer Match (Same Designation)": 0,
        "Exact Name & Dealer Match (Designation Differs)": 0,
        "Fuzzy Name & Dealer Match (Primary)": 0,
        "Fuzzy Name & Dealer Match (Secondary)": 0,
        "Phonetic Name & Dealer Match": 0,
        "Record Linkage / AO Match": 0,
        "Unresolved": 0
    }
    
    confidence_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "FUZZY": 0,
        "UNRESOLVED": 0
    }

    for idx, t_row in training.iterrows():
        matched_roster = None
        confidence = "UNRESOLVED"
        reason = "No match found in roster"
        
        # Extract keys
        raw_star_id = t_row.get('Star ID')
        raw_aadhar = t_row.get('AadharCardNumber')
        raw_emp_code = t_row.get('Emp Code')
        raw_name = t_row.get('Name')
        raw_dealer_code = t_row.get('Dealer Code')
        raw_dealer_ao = t_row.get('Dealer AO')
        raw_designation = t_row.get('Designation')
        
        clean_t_name = clean_name(raw_name)
        clean_t_dealer = clean_dealer_code(raw_dealer_code)
        clean_t_aadhar = clean_aadhar(raw_aadhar)
        clean_t_emp_code = clean_string(raw_emp_code)
        
        # ── PASS 1: DIRECT IDENTIFIER MATCH ───────────────────────────────────
        # A. Star ID lookup
        if pd.notna(raw_star_id):
            try:
                star_val = int(float(raw_star_id))
                if star_val in star_id_map:
                    matched_roster = star_id_map[star_val]
                    confidence = "HIGH"
                    reason = "Direct Star ID Match"
                    passes_count[reason] += 1
            except ValueError:
                pass
                
        # B. Aadhar Card lookup (if not matched)
        if matched_roster is None and clean_t_aadhar:
            if clean_t_aadhar in aadhar_map:
                matched_roster = aadhar_map[clean_t_aadhar]
                confidence = "HIGH"
                reason = "Aadhar Card Match"
                passes_count[reason] += 1
                
        # C. Emp Code lookup (if not matched)
        if matched_roster is None and clean_t_emp_code:
            if clean_t_emp_code in emp_code_map:
                matched_roster = emp_code_map[clean_t_emp_code]
                confidence = "HIGH"
                reason = "Exact Emp Code Match"
                passes_count[reason] += 1

        # ── PASS 2: EXACT NAME & DEALER CODE ──────────────────────────────────
        if matched_roster is None and clean_t_name and clean_t_dealer:
            candidates = dealer_group.get(clean_t_dealer, [])
            # Try to match name exactly
            exact_name_candidates = [c for c in candidates if c['clean_Name'] == clean_t_name]
            if exact_name_candidates:
                # Resolve designation if multiple exist
                match_cand = None
                if len(exact_name_candidates) == 1:
                    match_cand = exact_name_candidates[0]
                else:
                    # Match designation
                    t_desig = clean_string(raw_designation)
                    for ec in exact_name_candidates:
                        if clean_string(ec['Designation']) == t_desig:
                            match_cand = ec
                            break
                    if match_cand is None:
                        match_cand = exact_name_candidates[0] # Default fallback
                
                matched_roster = match_cand
                t_desig = clean_string(raw_designation)
                m_desig = clean_string(match_cand['Designation'])
                if t_desig == m_desig:
                    confidence = "HIGH"
                    reason = "Exact Name & Dealer Match (Same Designation)"
                else:
                    confidence = "MEDIUM"
                    reason = "Exact Name & Dealer Match (Designation Differs)"
                passes_count[reason] += 1

        # ── PASS 3: FUZZY NAME & DEALER CODE ──────────────────────────────────
        if matched_roster is None and clean_t_name and clean_t_dealer and len(clean_t_name) > 2:
            candidates = dealer_group.get(clean_t_dealer, [])
            best_score = 0
            best_cand = None
            for c in candidates:
                if len(c['clean_Name']) > 2:
                    score = fuzz.ratio(clean_t_name, c['clean_Name'])
                    if score > best_score:
                        best_score = score
                        best_cand = c
                        
            if best_cand is not None:
                if best_score >= FUZZY_PRIMARY_THRESHOLD:
                    matched_roster = best_cand
                    confidence = "MEDIUM"
                    reason = "Fuzzy Name & Dealer Match (Primary)"
                    passes_count[reason] += 1
                elif best_score >= FUZZY_SECONDARY_THRESHOLD:
                    matched_roster = best_cand
                    confidence = "LOW"
                    reason = "Fuzzy Name & Dealer Match (Secondary)"
                    passes_count[reason] += 1

        # ── PASS 4: PHONETIC & DEALER CODE ───────────────────────────────────
        if matched_roster is None and clean_t_name and clean_t_dealer and len(clean_t_name) > 2:
            candidates = dealer_group.get(clean_t_dealer, [])
            best_jw = 0.0
            best_cand = None
            for c in candidates:
                if len(c['clean_Name']) > 2:
                    jw_score = jellyfish.jaro_winkler_similarity(clean_t_name, c['clean_Name'])
                    if jw_score > best_jw:
                        best_jw = jw_score
                        best_cand = c
            
            if best_cand is not None and best_jw >= 0.85:
                matched_roster = best_cand
                confidence = "LOW"
                reason = "Phonetic Name & Dealer Match"
                passes_count[reason] += 1

        # ── PASS 5: RECORD LINKAGE fallback (Same Area Office, Name Fuzzy) ─────
        if matched_roster is None and clean_t_name and len(clean_t_name) > 2:
            # Let's search inside the same Area Office (Dealer AO)
            clean_ao = clean_string(raw_dealer_ao)
            ao_candidates = []
            if clean_ao:
                # Find roster employees in the same Dealer AO
                ao_candidates = [r_dict for r_dict in roster_records 
                                 if clean_string(r_dict['Dealer AO']) == clean_ao]
            
            best_score = 0
            best_cand = None
            for c in ao_candidates:
                c_clean_name = c['clean_Name']
                if len(c_clean_name) > 2:
                    score = fuzz.ratio(clean_t_name, c_clean_name)
                    if score > best_score:
                        best_score = score
                        best_cand = c
                        
            if best_cand is not None and best_score >= 85:
                matched_roster = best_cand
                confidence = "FUZZY"
                reason = "Record Linkage / AO Match"
                passes_count[reason] += 1
            else:
                # Fallback: Record Linkage across the entire database for name matching
                # Check if we have a very strong name match (>=90)
                best_global_score = 0
                best_global_cand = None
                for r_dict in roster_records:
                    rc_clean_name = r_dict['clean_Name']
                    if len(rc_clean_name) > 2:
                        score = fuzz.ratio(clean_t_name, rc_clean_name)
                        if score > best_global_score:
                            best_global_score = score
                            best_global_cand = r_dict
                if best_global_cand is not None and best_global_score >= 90:
                    matched_roster = best_global_cand
                    confidence = "FUZZY"
                    reason = "Record Linkage / AO Match"
                    passes_count[reason] += 1

        # ── PASS 6: UNRESOLVED ────────────────────────────────────────────────
        if matched_roster is None:
            passes_count["Unresolved"] += 1
            confidence = "UNRESOLVED"
            reason = "No match found in roster"
            
        confidence_counts[confidence] += 1
        
        # Build training info
        t_info = {
            "Training year": clean_string(t_row.get("Training year")),
            "SKILL LEVEL - PRE": clean_string(t_row.get("SKILL LEVEL - PRE", "NO TEST")),
            "SKILL LEVEL - POST": clean_string(t_row.get("SKILL LEVEL - POST", "NO TEST")),
            "LAST PRODUCT TRANIING ON": clean_string(t_row.get("LAST PRODUCT TRANIING ON")),
            "LAST MODEL TRAINED": clean_string(t_row.get("LAST MODEL TRAINED")),
            "MATCH_CONFIDENCE": confidence,
            "MATCH_REASON": reason
        }
        
        # Normalise Model Name and Product
        prod_val = t_info["LAST PRODUCT TRANIING ON"]
        model_val = t_info["LAST MODEL TRAINED"]
        
        # Map normalization
        if prod_val in MODEL_NORMALISATION_MAP:
            prod_val = MODEL_NORMALISATION_MAP[prod_val]
        if model_val in MODEL_NORMALISATION_MAP:
            model_val = MODEL_NORMALISATION_MAP[model_val]
            
        # Ensure it maps to canonical name
        for can in CANONICAL_MODELS:
            if prod_val.upper() == can.upper():
                prod_val = can
            if model_val.upper() == can.upper():
                model_val = can
                
        t_info["LAST PRODUCT TRANIING ON"] = prod_val
        t_info["LAST MODEL TRAINED"] = model_val
        
        # Compute skill score pre and post
        t_info["pre_score"] = get_skill_score(t_info["SKILL LEVEL - PRE"])
        t_info["post_score"] = get_skill_score(t_info["SKILL LEVEL - POST"])
        
        # Detect skill regressions (strictly lower post than pre, ignoring -1 / NO TEST)
        if t_info["pre_score"] >= 0 and t_info["post_score"] >= 0 and t_info["post_score"] < t_info["pre_score"]:
            t_info["SKILL_REGRESSION_FLAG"] = True
        else:
            t_info["SKILL_REGRESSION_FLAG"] = False

        # Build output record
        out_rec = {}
        if matched_roster:
            # Demographics from Roster (Source of truth)
            for k in roster_cols:
                out_rec[k] = matched_roster.get(k)
            out_rec["Roster_Matched_Index"] = matched_roster["original_index"]
        else:
            # Unresolved record: demographic information from the training log file is preserved
            for k in roster_cols:
                out_rec[k] = t_row.get(k)
            # Default Star ID to 0 or original Star ID
            out_rec["Star ID"] = int(float(raw_star_id)) if pd.notna(raw_star_id) else 0
            out_rec["Roster_Matched_Index"] = -1
            
        # Merge training info
        out_rec.update(t_info)
        matched_records.append(out_rec)

    # 4. Construct the output matched training dataset
    df_matched_training = pd.DataFrame(matched_records)
    
    # Convert dates to datetime objects defensively
    df_matched_training['Joining Date'] = pd.to_datetime(df_matched_training['Joining Date'], errors='coerce')
    df_matched_training['DOB'] = pd.to_datetime(df_matched_training['DOB'], errors='coerce')

    # Detect future joining dates (> current date or standard boundary of current FY end)
    # Flag future joining dates (year > 2026) but preserve the row
    df_matched_training["FUTURE_JOINING_FLAG"] = df_matched_training["Joining Date"].dt.year > 2026
    
    # 5. Create Master Output Sheet (Active Roster Left Join Training Logs + Unresolved)
    # We want to represent EVERY active employee from the roster.
    # For employees who have been matched to training logs: they will have their training records.
    # For employees who have NOT been matched to training logs: they will have 1 row with empty/NaN training records.
    # PLUS: Include the Unresolved training logs (to prevent row loss).
    
    # Find active employees who were NOT matched to any training record
    matched_roster_indices = set(df_matched_training[df_matched_training["Roster_Matched_Index"] != -1]["Roster_Matched_Index"].unique())
    untrained_employees = []
    
    for idx, r_row in roster.iterrows():
        if idx not in matched_roster_indices:
            # Create a row for this untrained employee
            emp_rec = {k: r_row[k] for k in roster_cols}
            emp_rec["Roster_Matched_Index"] = idx
            
            # Empty training fields
            emp_rec.update({
                "Training year": np.nan,
                "SKILL LEVEL - PRE": "NO TEST",
                "SKILL LEVEL - POST": "NO TEST",
                "LAST PRODUCT TRANIING ON": np.nan,
                "LAST MODEL TRAINED": np.nan,
                "pre_score": -1,
                "post_score": -1,
                "MATCH_CONFIDENCE": "HIGH", # demographic detail is high confidence as it's from roster
                "MATCH_REASON": "No Training History (Active Roster)",
                "SKILL_REGRESSION_FLAG": False,
            })
            untrained_employees.append(emp_rec)
            
    df_untrained = pd.DataFrame(untrained_employees)
    if not df_untrained.empty:
        df_untrained['Joining Date'] = pd.to_datetime(df_untrained['Joining Date'], errors='coerce')
        df_untrained['DOB'] = pd.to_datetime(df_untrained['DOB'], errors='coerce')
        df_untrained["FUTURE_JOINING_FLAG"] = df_untrained["Joining Date"].dt.year > 2026
    
    # Combine everything to form the Master Database
    # We concatenate:
    # 1. Matched Training Logs (which include matched roster demographics)
    # 2. Untrained Active Employees (demographics from roster, empty training fields)
    # 3. Unresolved Training Logs (demographics from training files, training fields intact, MATCH_CONFIDENCE = UNRESOLVED)
    
    dfs_to_concat = []
    if not df_matched_training.empty:
        dfs_to_concat.append(df_matched_training)
    if not df_untrained.empty:
        dfs_to_concat.append(df_untrained)
        
    df_master = pd.concat(dfs_to_concat, ignore_index=True)
    
    # Clean contact no representations (e.g. convert float representation 9999.0 to 9999)
    df_master['Contact No'] = df_master['Contact No'].apply(clean_contact)
    
    # 6. Calculate Recall Statuses on df_master
    # For each row, find the latest training date for that employee.
    # Wait, how to find training date for recall calculation?
    # Roster does not have "Last Training Date" column directly. But wait, we can map:
    # We find the latest training year for each Star ID.
    # Let's map Training year to the end date of that Fiscal Year or the center date:
    # FY_CALENDAR start/end.
    # To be conservative, let's map training year to the end date of that fiscal year (e.g. F-25 -> March 31, 2025).
    # Then calculate the elapsed months between that date and the base_date.
    
    # Find latest training date for each unique employee
    # Let's define the mapping:
    # F-23 -> March 31, 2023
    # F-24 -> March 31, 2024
    # F-25 -> March 31, 2025
    # F-26 -> March 31, 2026
    # Let's write a small helper for this mapping
    def fy_to_date(fy_str):
        if pd.isna(fy_str) or not isinstance(fy_str, str):
            return None
        fy_str = fy_str.strip().upper()
        if fy_str in FY_CALENDAR:
            return FY_CALENDAR[fy_str]["end"] # Use end date of fiscal year
        return None
        
    df_master['Training_End_Date'] = df_master['Training year'].apply(fy_to_date)
    
    # For each Star ID (if not 0), find the latest Training_End_Date
    # If Star ID is 0 or unresolved, we use its own Training_End_Date
    # Let's group by Star ID and find the max Training_End_Date
    latest_training_dates = {}
    
    # Fill latest training dates dictionary
    for star_id, group in df_master.groupby('Star ID'):
        if star_id != 0:
            valid_dates = group['Training_End_Date'].dropna()
            if not valid_dates.empty:
                latest_training_dates[star_id] = max(valid_dates)
                
    def get_latest_training_date(row):
        star_id = row['Star ID']
        if star_id != 0 and star_id in latest_training_dates:
            return latest_training_dates[star_id]
        return row['Training_End_Date'] # fallback for unresolved or Star ID 0
        
    df_master['LATEST_TRAINING_DATE'] = df_master.apply(get_latest_training_date, axis=1)
    
    # Apply recall status calculations
    recall_results = df_master['LATEST_TRAINING_DATE'].apply(lambda d: calculate_recall_bucket(d, base_date))
    df_master['RECALL_STATUS'] = [r[0] for r in recall_results]
    df_master['RECALL_COLOR'] = [r[1] for r in recall_results]
    df_master['RECALL_DESCRIPTION'] = [r[2] for r in recall_results]
    
    # Clean up temporary columns
    df_master.drop(columns=['Training_End_Date'], inplace=True, errors='ignore')
    
    # 7. Summary Stats
    total_training_rows = len(df_training_raw)
    total_master_rows = len(df_master)
    
    stats = {
        "total_roster_count": len(roster),
        "total_training_input_count": total_training_rows,
        "total_master_count": total_master_rows,
        "matched_count": len(df_matched_training),
        "untrained_count": len(df_untrained),
        "unresolved_count": confidence_counts["UNRESOLVED"],
        "confidence_distribution": confidence_counts,
        "passes_distribution": passes_count,
        "future_joining_count": int(df_master["FUTURE_JOINING_FLAG"].sum()),
        "skill_regression_count": int(df_master["SKILL_REGRESSION_FLAG"].sum())
    }
    
    return df_master, stats
