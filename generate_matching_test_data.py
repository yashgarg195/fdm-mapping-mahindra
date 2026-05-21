import pandas as pd
import numpy as np
import random
import datetime

# --- Configuration & Seed Data ---
NUM_TOTAL_ROWS = 5000
random.seed(42)
np.random.seed(42)

# Load the real training data to create deterministic matches
try:
    training_df = pd.read_excel('TRAINING DATA ANALYTICS.xlsx')
except Exception as e:
    print(f"Error loading training data: {e}")
    exit(1)

# Ensure we have enough rows, sample with replacement if needed
train_sample = training_df.sample(n=2500, replace=True).copy()
train_sample = train_sample.reset_index(drop=True)

# Columns to ensure exist based on ANALYTICS.xlsx schema
roster_columns = [
    'Star ID', 'Zone', 'State', 'Dealer AO', 'Dealer Code', 'Dealer Name', 
    'Dealer Operational Status', 'Location', 'Emp Code', 'Name', 'Star ID.1', 
    'Designation', 'Joining Date', 'Contact No', 'AadharCardNumber', 'Gender', 
    'Father Name', 'DOB', 'Residence Location', 'Age'
]

# We will build a list of dictionaries for the new roster
roster_data = []

# Helper for random dates
def random_date(start_year=2015, end_year=2024):
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    return start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))

# --- SCENARIO 1: High Confidence (Exact Matches) - 1000 rows ---
# Exact Star ID, Dealer Code, and Name
for i in range(0, 1000):
    row = train_sample.iloc[i].to_dict()
    roster_data.append(row)

# --- SCENARIO 2: Medium Confidence (Aadhar / Phone Matches) - 500 rows ---
# Mess up Star ID and Name, but keep Contact No or Aadhar Exact
for i in range(1000, 1500):
    row = train_sample.iloc[i].to_dict()
    # Break Star ID
    row['Star ID'] = random.randint(900000, 999999) 
    # Break Name slightly
    row['Name'] = str(row.get('Name', '')) + " TEST"
    # Ensure one of Aadhar or Phone is valid
    if i % 2 == 0:
        row['AadharCardNumber'] = train_sample.iloc[i].get('AadharCardNumber')
        row['Contact No'] = random.randint(6000000000, 6999999999) # break phone
    else:
        row['Contact No'] = train_sample.iloc[i].get('Contact No')
        row['AadharCardNumber'] = "0000 0000 0000" # break aadhar
    roster_data.append(row)

# --- SCENARIO 3: Fuzzy Matches - 500 rows ---
# Keep Dealer Code the same, break Star ID, make Name phonetically/fuzzily similar
phonetic_map = {"a": "aa", "i": "ee", "u": "oo", "sh": "s", "v": "b"}
for i in range(1500, 2000):
    row = train_sample.iloc[i].to_dict()
    row['Star ID'] = random.randint(800000, 899999) # Break ID
    
    orig_name = str(row.get('Name', 'Unknown')).lower()
    if orig_name and orig_name != 'nan':
        # Apply some phonetic changes
        for k, v in phonetic_map.items():
            if k in orig_name:
                orig_name = orig_name.replace(k, v, 1)
        row['Name'] = orig_name.upper()
    roster_data.append(row)

# --- SCENARIO 4: Low Confidence (Emp Code + Dealer Code) - 250 rows ---
# Break Star ID, Name, Phone, Aadhar. Keep Emp Code and Dealer Code exact.
for i in range(2000, 2250):
    row = train_sample.iloc[i].to_dict()
    row['Star ID'] = random.randint(700000, 799999)
    row['Name'] = "COMPLETELY DIFFERENT NAME"
    row['Contact No'] = random.randint(6000000000, 6999999999)
    row['AadharCardNumber'] = "1111 2222 3333"
    # Ensure Emp Code exists
    if pd.isna(row.get('Emp Code')):
        row['Emp Code'] = f"EMP{random.randint(1000,9999)}"
    roster_data.append(row)

# --- SCENARIO 5: Name Mismatch (Conflict) - 250 rows ---
# Exact Star ID, but completely different Name and Dealer Code
for i in range(2250, 2500):
    row = train_sample.iloc[i].to_dict()
    row['Name'] = "WRONG PERSON " + str(random.randint(1,100))
    roster_data.append(row)


# --- SCENARIO 6: Completely Random Roster (Untrained/Backlog) - 2500+ rows ---
first_names = ["Amit", "Rahul", "Priya", "Suresh", "Ramesh", "Deepak", "Sneha", "Karan", "Vikas", "Anil"]
last_names = ["Kumar", "Singh", "Sharma", "Yadav", "Patil", "Deshmukh", "Jha", "Gupta", "Mishra", "Chauhan"]
zones = ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5']
states = ['Haryana', 'Punjab', 'Rajasthan East', 'Rajasthan West', 'UP Central']
designations = ['Technician', 'Installer', 'Service Advisor (FLA)', 'Salesman', 'Techguru']

for i in range(2500, NUM_TOTAL_ROWS):
    row = {
        'Star ID': 500000 + i,
        'Zone': random.choice(zones),
        'State': random.choice(states),
        'Dealer AO': 'MOCK AO',
        'Dealer Code': f"DL{random.randint(1000, 9999)}",
        'Dealer Name': 'MOCK DEALER',
        'Dealer Operational Status': 'Active',
        'Location': 'Mock City',
        'Emp Code': f"EMP{random.randint(10000, 99999)}",
        'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
        'Star ID.1': 500000 + i,
        'Designation': random.choice(designations),
        'Joining Date': random_date(),
        'Contact No': random.randint(7000000000, 9999999999),
        'AadharCardNumber': f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
        'Gender': 'Male',
        'DOB': random_date(1980, 2000),
        'Age': random.randint(22, 45)
    }
    roster_data.append(row)

# Convert to DataFrame
roster_df = pd.DataFrame(roster_data)

# Ensure columns match analytics.xlsx schema exactly
for col in roster_columns:
    if col not in roster_df.columns:
        roster_df[col] = np.nan

# Keep only the roster columns
roster_df = roster_df[roster_columns]

# Ensure datetime
roster_df['Joining Date'] = pd.to_datetime(roster_df['Joining Date'], errors='coerce').dt.date
roster_df['DOB'] = pd.to_datetime(roster_df['DOB'], errors='coerce').dt.date

# Save to Excel
output_path = 'MOCK_ROSTER_MATCHING_DEMO.xlsx'
roster_df.to_excel(output_path, index=False)
print(f"Successfully generated matching demo file: {output_path} with {len(roster_df)} rows.")
