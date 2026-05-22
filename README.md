# Mahindra & Mahindra Tractors — Training Analytics & Manpower Intelligence Platform

An enterprise-grade, offline-capable identity resolution and training governance portal built to unify, clean, and analyze highly fragmented workforce data.

---

## 🌐 Dashboard Access

* **Live Web Portal:** [https://mec-data-mapping.streamlit.app/](https://mec-data-mapping.streamlit.app/)
* **Local Server:** `http://localhost:8501`

To run locally, double-click `start_dashboard.bat` or run the following in your terminal:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Overview

This application bridges the gap between disparate data systems by merging Manpower Rosters and Training History logs into a single, cohesive source of truth. Designed to handle messy data, misspellings, missing IDs, and conflicting records, the platform provides actionable insights into technical training coverage across the nation.

### Key Features
* **Zero Data Loss Pipeline:** Ensures every record from both Roster and Training files is captured, audited, and accounted for.
* **Intelligent Deduplication:** Identifies exact duplicate rows and uses fuzzy logic to flag suspect "cross-ID" duplicates (e.g., the same person logged under two different Star IDs at the same dealership).
* **Automated Training Status & Backlog:** Dynamically calculates whether technicians are `COMPLETED`, `PENDING` (needs refresher), `ATTENDED` (no skill improvement), or `ELIGIBLE` based on the current financial year and technical designation requirements.
* **Comprehensive Excel Export:** Generates a 9-sheet master report detailing unified records, duplicates, unmatched entities, raw data, and summary matrices.

---

## 🧠 The 7-Pass Identity Resolution Engine

The core of the application is a custom identity resolution algorithm (`core/matching.py`) that progressively merges datasets using deterministic and probabilistic matching:

### Workflow
1. **Alignment**: Automatically maps variable column headers (e.g. `STARID` $\rightarrow$ `Star ID`).
2. **Cleansing**: Standardizes names, strips titles, and normalizes phone/Aadhar strings.
3. **Deduplication**: Automatically flags duplicate IDs and fuzzy name duplicates under different IDs.
4. **Resolution**: Matches training records to the master roster through 7 progressive fuzzy/phonetic passes.
5. **Backlog & Nomination**: Groups workers by eligibility status and ranks priority candidates for upcoming training.
6. **Reporting**: Displays real-time dashboards (Overview, Penetration, Skills, Manpower, Audits) and generates a downloadable 8-sheet Excel master file.

### Resolution Passes
1. **Pass 1: Exact Star ID** (with fuzzy name validation to catch ID clashes)
2. **Pass 2: Exact Aadhar Card** (with fuzzy name validation)
3. **Pass 3: Exact Mobile Number** (with fuzzy name validation)
4. **Pass 4: Name + Dealer Code** (Fuzzy Phonetic Matching `>88%`)
5. **Pass 5: Name + Location/State** (Fuzzy Phonetic Matching `>92%`)
6. **Pass 6: Name Only Global** (Fuzzy Phonetic Matching `>95%` — High threshold for safety)
7. **Pass 7: Unresolved / Roster-Only** (Captures all remainders for the audit queue)

---

## 🗂️ Project Architecture

```text
├── app.py                      # Main Streamlit web portal entry point
├── config/
│   ├── constants.py            # Global mappings, thresholds, and brand colors
│   └── settings.py             # Feature flags and system toggles
├── core/
│   ├── etl.py                  # Ingestion, validation, and schema mapping
│   ├── cleansing.py            # Data normalization (text, dates, phones)
│   ├── deduplication.py        # Exact and fuzzy duplicate detection
│   ├── matching.py             # 7-pass identity resolution engine
│   └── training_pipeline.py    # Backlog generation and nomination logic
├── analytics/
│   ├── kpi_engine.py           # Core calculations for national coverage
│   └── overview.py             # Specialized aggregations
├── reports_export/
│   └── excel_export.py         # Advanced XlsxWriter engine (9-sheet generation)
└── ui/
    ├── overview_tab.py         # National KPIs & Charts
    ├── backlog_tab.py          # Pending nominations and aging analysis
    ├── skill_tab.py            # L1-L4 proficiency and regression tracking
    ├── manpower_tab.py         # Attrition, retention, and dealer mapping
    ├── audit_tab.py            # Data quality exceptions and suspect duplicates
    └── export_tab.py           # Download center
```

---

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit (Custom HTML/CSS injections for enterprise Shadcn-like aesthetics)
* **Data Processing:** Pandas, NumPy
* **Fuzzy Matching:** RapidFuzz (Jaro-Winkler, Levenshtein, Phonetic algorithms)
* **Visualizations:** Plotly Express & Plotly Graph Objects
* **Reporting:** XlsxWriter (In-memory `BytesIO` buffers for high-performance offline generation)

---

## 🚀 How to Use

1. **Upload Data:** Navigate to the sidebar and upload your `Manpower Roster` and `Training History` Excel files.
2. **Wait for Processing:** The platform will instantly execute deduplication, cleansing, and the 7-pass match.
3. **Explore Tabs:**
    * **Overview:** Check high-level national training penetration.
    * **Backlog Manager:** Identify who is pending training and filter by designation.
    * **Data Quality Audit:** Review the `Audit Tab` to resolve unmapped individuals, name mismatches, and suspected duplicates.
4. **Export:** Go to the Export tab to download the fully reconciled Master Excel File.

---
*Built for Mahindra & Mahindra Tractors.*
