import pandas as pd
import numpy as np
import random
import datetime

# --- Configuration & Seed Data ---
NUM_ROWS = 5000
random.seed(42)
np.random.seed(42)

first_names = ["Amit", "Rahul", "Priya", "Suresh", "Ramesh", "Deepak", "Sneha", "Karan", "Vikas", "Anil", "Sunil", "Rajesh", "Pooja", "Vikram", "Sanjay", "Mahesh", "Neha", "Vijay", "Ashish", "Ajay"]
last_names = ["Kumar", "Singh", "Sharma", "Yadav", "Patil", "Deshmukh", "Jha", "Gupta", "Mishra", "Chauhan", "Bhatia", "Reddy", "Nair", "Rao", "Das", "Sen", "Bose", "Verma", "Pandey"]

zones = ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5']
states = ['Haryana', 'Punjab', 'Rajasthan East', 'Rajasthan West', 'UP Central', 'Maharashtra', 'Karnataka', 'Gujarat']
aos = ['KARNAL COTTONBELT', 'JAIPUR', 'MOHALI CENTRAL', 'PUNE', 'AHMEDABAD', 'BANGALORE']
dealers = ['M/S. S S TRADING CO.', 'AMIT TRACTORS', 'KISSAN TRACTOR TRADERS', 'BANI BUILDING MATERIAL', 'JAI KISAN AUTOS']
designations = ['Technician', 'Installer', 'Service Advisor (FLA)', 'Salesman', 'Techguru', 'Works Manager', 'Branch Manager']

training_years = ['F-23', 'F-24', 'F-25', 'F-26', np.nan]
skills = ['0', 'L1', 'L2', 'L3', 'L4', 'NO TEST']
models = ['H1 R', 'TREM IV', 'OJA', 'NOVO', 'FARM MACHINERY', 'INSTALLATION', 'ELECTRICALS']

def random_date(start_year=2015, end_year=2024):
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    return start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))

# --- Generate Base Data ---
data = []
star_id_start = 100000

for i in range(NUM_ROWS):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    name = f"{fn} {ln}"
    
    pre = random.choice(skills)
    post = random.choice(skills)
    
    # Ensure logical progression for normal data most of the time
    if pre in ['L3', 'L4'] and post in ['0', 'L1']:
        post = pre # Fix it for normal rows
        
    row = {
        'Star ID': star_id_start + i,
        'Zone': random.choice(zones),
        'State': random.choice(states),
        'Dealer AO': random.choice(aos),
        'Dealer Code': f"DL{random.randint(1000, 9999)}",
        'Dealer Name': random.choice(dealers),
        'Dealer Operational Status': 'Active',
        'Location': 'City ' + str(random.randint(1, 50)),
        'Emp Code': f"EMP{random.randint(10000, 99999)}",
        'Name': name,
        'Star ID.1': star_id_start + i,
        'Designation': random.choice(designations),
        'Joining Date': random_date(),
        'Contact No': random.randint(6000000000, 9999999999),
        'AadharCardNumber': f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
        'Gender': random.choice(['Male', 'Female']),
        'Father Name': f"{random.choice(first_names)} {random.choice(last_names)}",
        'DOB': random_date(1980, 2000),
        'Residence Location': 'City ' + str(random.randint(1, 50)),
        'Age': random.randint(22, 45),
        'Training year': random.choice(training_years),
        'SKILL LEVEL - PRE': pre,
        'SKILL LEVEL - POST': post,
        'LAST PRODUCT TRANIING ON': random_date(2022, 2024).strftime("%d/%m/%Y"),
        'LAST MODEL TRAINED': random.choice(models)
    }
    data.append(row)

df = pd.DataFrame(data)

# --- Inject Edge Cases ---

# 1. Missing Names (100 rows)
df.loc[0:99, 'Name'] = np.nan

# 2. Future Joining Date (100 rows)
df.loc[100:199, 'Joining Date'] = datetime.date(2030, 1, 1)

# 3. Skill Regressions (100 rows)
df.loc[200:299, 'SKILL LEVEL - PRE'] = 'L3'
df.loc[200:299, 'SKILL LEVEL - POST'] = 'L1'
df.loc[200:299, 'Training year'] = 'F-26'

# 4. Missing Prerequisite (100 rows)
df.loc[300:399, 'SKILL LEVEL - PRE'] = '0'
df.loc[300:399, 'SKILL LEVEL - POST'] = 'L4'

# 5. Suspect Duplicates (Cross-ID) - 100 pairs (rows 400-499 and 500-599)
for i in range(100):
    idx1 = 400 + i
    idx2 = 500 + i
    df.loc[idx2, 'Name'] = df.loc[idx1, 'Name']
    df.loc[idx2, 'Dealer Code'] = df.loc[idx1, 'Dealer Code']
    df.loc[idx2, 'Dealer Name'] = df.loc[idx1, 'Dealer Name']
    # Different Star IDs since they are different indices

# 6. Phonetic Duplicates - 100 pairs (rows 600-699 and 700-799)
phonetic_map = {"Amit": "Ameet", "Rahul": "Rahool", "Pooja": "Puja", "Deepak": "Dipak", "Vikas": "Bikas"}
for i in range(100):
    idx1 = 600 + i
    idx2 = 700 + i
    name_parts = df.loc[idx1, 'Name'].split()
    fn = name_parts[0]
    ln = name_parts[1] if len(name_parts) > 1 else ""
    # Alter first name phonetically if possible, else append 'h'
    new_fn = phonetic_map.get(fn, fn + "h")
    df.loc[idx2, 'Name'] = f"{new_fn} {ln}"
    df.loc[idx2, 'Dealer Code'] = df.loc[idx1, 'Dealer Code']
    df.loc[idx2, 'Dealer Name'] = df.loc[idx1, 'Dealer Name']

# 7. Fuzzy Name Match Same ID (Name Conflicts) - 100 rows (800-899 vs 900-999)
# Simulating the scenario where the same Star ID appears twice with slightly different names
for i in range(100):
    idx1 = 800 + i
    idx2 = 900 + i
    df.loc[idx2, 'Star ID'] = df.loc[idx1, 'Star ID']  # Same ID
    name1 = df.loc[idx1, 'Name']
    df.loc[idx2, 'Name'] = name1 + " KR" # Adding typical suffix variation

# 8. Exact Duplicates - 100 rows (rows 1000-1099 exact copy of 1100-1199)
for i in range(100):
    idx1 = 1000 + i
    idx2 = 1100 + i
    df.loc[idx2] = df.loc[idx1].copy()

# 9. No Training Date / Pending Aging (Rows 1200-1299)
df.loc[1200:1299, 'Training year'] = 'F-23'
df.loc[1200:1299, 'Designation'] = 'Technician'
df.loc[1200:1299, 'SKILL LEVEL - POST'] = 'L1'

# 10. Blank Star IDs (Rows 1300-1350)
df.loc[1300:1350, 'Star ID'] = np.nan

# Ensure correct data types
df['Joining Date'] = pd.to_datetime(df['Joining Date'])
df['DOB'] = pd.to_datetime(df['DOB'])

# Save to Excel
output_path = 'comprehensive_test_analytics.xlsx'
df.to_excel(output_path, index=False)
print(f"Successfully generated test file: {output_path} with {len(df)} rows.")
