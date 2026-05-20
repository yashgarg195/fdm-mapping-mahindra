# Mahindra & Mahindra Tractors — Training Analytics & Manpower Intelligence Platform

An enterprise-grade, 100% offline, air-gapped manpower identity resolution and training governance portal. Automates monthly data-crunching, name-matching, and business-intelligence workloads into a single button click.

---

## 🚀 Access the Dashboard

* **Local:** [http://localhost:8501](http://localhost:8501)
* **Network (LAN):** `http://<your-ip>:8501`

To start the dashboard, run:
```bash
streamlit run app.py
```

Or double-click `start_dashboard.bat` for one-click launch (includes optional global tunnel).

---

## 🛠️ Setup

```bash
cd "C:\Users\Anumay Pandey\Desktop\FDM mapping Mahindra"
pip install -r requirements.txt
streamlit run app.py
```

**Requirements:** Python 3.10+, streamlit, pandas, numpy, plotly, xlsxwriter, openpyxl, rapidfuzz, jellyfish

---

## 📁 Project Structure

```
├── app.py                          # Streamlit entry point (no business logic)
├── start_dashboard.bat             # One-click launcher with optional tunnel
├── config/
│   ├── constants.py                # All constants, mappings, column aliases
│   └── settings.py                 # Tunable thresholds and weights
├── core/
│   ├── etl.py                      # File loading and DataFrame cleaning
│   ├── cleansing.py                # Name/contact/Aadhar normalization
│   ├── deduplication.py            # Duplicate detection (never deletes)
│   ├── fuzzy_matching.py           # rapidfuzz + jellyfish scoring
│   ├── matching.py                 # 7-pass identity resolution engine
│   ├── scoring.py                  # Skill/priority/readiness scoring
│   └── training_pipeline.py        # Rolling backlog and nomination engine
├── analytics/
│   ├── kpi_engine.py               # All KPI computations
│   ├── overview.py                 # National summary, FY/MoM trends
│   ├── manpower.py                 # State/zone manpower tables
│   ├── penetration.py              # Dealership penetration metrics
│   ├── skill_analytics.py          # Skill distribution and regression
│   └── backlog_analytics.py        # Aging reports and dealer rankings
├── ui/
│   ├── sidebar.py                  # File upload, type assignment, filters
│   ├── overview_tab.py             # Tab 1: KPIs and trends
│   ├── backlog_tab.py              # Tab 2: Pending & nominations
│   ├── skill_tab.py                # Tab 3: Skill analytics
│   ├── penetration_tab.py          # Tab 4: Product penetration
│   ├── manpower_tab.py             # Tab 5: Unique manpower
│   └── audit_tab.py                # Tab 6: Audit & exceptions
├── export/
│   └── excel_export.py             # 8-sheet styled Excel via BytesIO
├── storage/
│   └── mapping_store.py            # In-memory SQLite mapping cache
├── utils/
│   ├── date_utils.py               # Date parsing, FY computation
│   ├── formatting_utils.py         # Display formatting and KPI cards
│   └── logging_utils.py            # Structured ETL/matching logging
├── requirements.txt
└── README.md
```

---

## ⚙️ Identity Resolution — 7-Pass Engine

| Pass | Strategy | Confidence |
|------|----------|------------|
| 1 | Exact Star ID / Aadhar / Emp Code | HIGH |
| 2 | Exact Name + Dealer + Contact | HIGH/MEDIUM |
| 3 | Fuzzy Name + Same Dealer | MEDIUM/LOW |
| 4 | Dealer-Transfer-Aware (global name via rapidfuzz C++) | LOW |
| 5 | Phonetic (Metaphone + Soundex + Jaro-Winkler) | LOW |
| 6 | Weighted Probabilistic Composite | Varies |
| 7 | Unresolved → PENDING_MAPPING_REVIEW | UNRESOLVED |

---

## 📊 Dashboard Tabs — Detailed Use Cases

### Tab 1: 📊 Overview
**Use Case:** Executive-level snapshot of the entire training program.
- **KPI Cards:** Total Manpower, Training Coverage %, Pending/Eligible count, L3/L4 Specialist count.
- **FY Trend Line:** Shows how training coverage has progressed year-over-year. Use this to demonstrate ROI to management.
- **Monthly Bar Chart:** Identifies seasonal peaks/dips in training activity. Use this to plan batch scheduling.

### Tab 2: 📋 Pending & Nominations
**Use Case:** Operational planning — *who* to train next and *where*.
- **Rolling Backlog:** Every employee pending training, ranked by a weighted priority score (pending age, skill gap, dealer shortage, designation).
- **Nomination List:** The top-N highest-priority candidates auto-extracted from the backlog. Download as Excel to send directly to training coordinators.
- **Dealership Backlog Ranking:** Which dealerships have the most untrained employees? Focus resources there first.
- **Aging Distribution:** How long have employees been waiting? 12+ months = Critical (red), 6-12 = Warning (amber).

### Tab 3: 🎯 Skill Analytics
**Use Case:** Measure training *effectiveness* — not just attendance.
- **Pre vs Post Scores:** Are employees actually improving after training? Shows average skill uplift.
- **Skill Distribution:** How many employees are at each level (L0-L4)? L0=untrained, L4=specialist.
- **Regression Cases:** Employees whose post-skill is *lower* than pre-skill (data quality flag or retest needed).
- **Uplift Heatmap:** Which dealers × FY combinations show the best/worst skill improvement?

### Tab 4: 🏢 Product Penetration
**Use Case:** Assess *geographic* and *product* training coverage gaps.
- **Zone Gauges:** Visual gauge per zone showing what % of manpower has been trained. Red zone = under 50%.
- **Dealership Penetration Table:** Per-dealer metrics — total employees, trained count, penetration %, L3/L4 count, readiness score.
- **Product Readiness:** Which tractor models have been covered in training, how many unique employees, across how many states?
- **L3/L4 Specialist Density:** State-level bar chart showing specialist distribution. Identify states with zero specialists.

### Tab 5: 👥 Unique Manpower
**Use Case:** HR-level headcount validation and identity audit.
- **Unique Employee Count:** De-duplicated headcount (by Star ID) across all uploaded files.
- **Unresolved Identities:** Employees the system could not match — excluded from official KPIs to prevent double-counting.
- **State-wise Table:** Sortable table with trained/untrained/pending breakdown per state.
- **Zone Stacked Bar:** Visual comparison of trained vs untrained manpower by zone.

### Tab 6: 🔍 Audit & Exceptions
**Use Case:** Data governance and quality assurance.
- **Confidence Pie Chart:** What % of matches are HIGH vs MEDIUM vs LOW vs UNRESOLVED? Target: >90% HIGH.
- **Duplicate Log:** All flagged duplicate records (never deleted, always preserved for audit).
- **Unresolved Queue:** Records tagged PENDING_MAPPING_REVIEW — need manual verification.
- **Data Quality Issues:** Future joining dates, skill regressions, missing employee names — all auto-detected.

---

## 📥 Excel Output — 8 Sheets

1. **Unified_Master** — all rows, mapped Star IDs, confidence-colored
2. **Pending_Backlog** — rolling backlog with priority scores
3. **Duplicate_Log** — flagged duplicates (never deleted)
4. **Mapping_Confidence** — every match method and score
5. **Data_Quality_Report** — future dates, missing names, anomalies
6. **Skill_Analytics** — pre/post/delta by employee
7. **Recall_Action_List** — sorted nomination list
8. **Audit_Log** — processing events with timestamps

---

## 🔒 Hard Constraints

- **100% Offline** — no API calls, no cloud, no internet at runtime
- **Zero Row Loss** — every uploaded row appears in output
- **No AI/LLMs** — only classical algorithms (fuzzy, phonetic, rule-based)
- **Deterministic** — same input always produces same output
- **Read-Only Dashboard** — no in-UI data editing
- **No Disk Writes** — all exports via io.BytesIO