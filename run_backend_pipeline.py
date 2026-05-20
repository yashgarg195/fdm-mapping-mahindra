import os
import sys
import pandas as pd
import datetime

# Add dashboard folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matching_engine import run_matching_pipeline
from excel_exporter import export_to_excel

def main():
    print("=== STARTING MAHINDRA TRAINING ANALYTICS BACKEND PIPELINE ===")
    
    d = r'C:\Users\Anumay Pandey\Desktop\FDM mapping Mahindra'
    input_file = os.path.join(d, 'ANALYTICS.xlsx')
    output_file = os.path.join(d, 'CONSOLIDATED_MASTER.xlsx')
    
    print(f"Loading input data from: {input_file}")
    df_raw = pd.read_excel(input_file, sheet_name='Working file')
    print(f"Loaded raw data: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    
    # 1. Build Active Roster
    demographic_cols = [
        'Star ID', 'Zone', 'State', 'Dealer AO', 'Dealer Code', 'Dealer Name', 
        'Dealer Operational Status', 'Location', 'Emp Code', 'Name', 
        'Designation', 'Joining Date', 'Contact No', 'AadharCardNumber', 
        'Gender', 'Father Name', 'DOB', 'Residence Location', 'Age'
    ]
    df_roster = df_raw[demographic_cols].drop_duplicates(subset=['Star ID']).copy()
    print(f"Extracted Active Roster: {df_roster.shape[0]} unique employees")
    
    # 2. Build Training Logs
    # Extract rows where Training year is not null (has some training record)
    training_cols = [
        'Star ID', 'Name', 'Dealer Code', 'Dealer AO', 'Designation', 'Emp Code', 'AadharCardNumber',
        'Training year', 'SKILL LEVEL - PRE', 'SKILL LEVEL - POST', 
        'LAST PRODUCT TRANIING ON', 'LAST MODEL TRAINED'
    ]
    df_training = df_raw[df_raw['Training year'].notnull()][training_cols].copy()
    print(f"Extracted Training Logs: {df_training.shape[0]} records")
    
    # 3. Run Matching Pipeline
    print("\nRunning multi-pass matching engine...")
    base_date = datetime.date(2026, 5, 20)
    df_master, stats = run_matching_pipeline(df_roster, df_training, base_date)
    
    print("\n=== PIPELINE RESULTS ===")
    print(f"Total Consolidated Master Rows: {df_master.shape[0]}")
    print(f"Successfully Matched: {stats['matched_count']}")
    print(f"Unresolved Logs: {stats['unresolved_count']}")
    print(f"Confidence distribution: {stats['confidence_distribution']}")
    print(f"Passes breakdown:")
    for k, v in stats['passes_distribution'].items():
        if v > 0:
            print(f"  - {k}: {v}")
            
    print(f"Future Joining Dates: {stats['future_joining_count']}")
    print(f"Skill Regressions: {stats['skill_regression_count']}")
    
    # 4. Export formatted Excel sheet
    print(f"\nExporting beautifully styled Excel sheet to: {output_file}")
    excel_bin = export_to_excel(df_master, stats)
    
    with open(output_file, 'wb') as f:
        f.write(excel_bin)
        
    print(f"Successfully wrote {len(excel_bin)} bytes to Excel.")
    print("=== BACKEND PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
