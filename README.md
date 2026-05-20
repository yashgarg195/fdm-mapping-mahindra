# Mahindra & Mahindra Tractors — Training Analytics & Manpower Intelligence Platform

An enterprise-grade, 100% offline, air-gapped manpower identity resolution and training governance portal. Automates monthly data-crunching, name-matching, and business-intelligence workloads into a single button click.

---

## 🚀 Active Local Deployment

* **Local:** [http://localhost:8501](http://localhost:8501)
* **Network:** [http://10.212.61.157:8501](http://10.212.61.157:8501)
* **External:** [http://106.216.244.170:8501](http://106.216.244.170:8501)

*Last verified:* **2026-05-20 16:45 IST**

---

## 🛠️ Setup

```bash
cd "C:\Users\Anumay Pandey\Desktop\FDM mapping Mahindra"
pip install -r requirements.txt
streamlit run app.py
```

**Requirements:** Python 3.10+, streamlit, pandas, numpy, plotly, xlsxwriter, openpyxl, rapidfuzz, jellyfish, recordlinkage, symspellpy

---

## 📁 Project Structure

```
├── app.py                          # Streamlit entry point (no business logic)
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
| 4 | Dealer-Transfer-Aware (global name) | LOW |
| 5 | Phonetic (Metaphone + Soundex) | LOW |
| 6 | Weighted Probabilistic Composite | Varies |
| 7 | Unresolved → PENDING_MAPPING_REVIEW | UNRESOLVED |

---

## 📊 Dashboard Tabs

1. **Overview** — KPI cards, FY trend line, MoM bar chart
2. **Pending & Nominations** — Rolling backlog, priority ranking, aging distribution
3. **Skill Analytics** — Distribution, regression cases, uplift heatmap
4. **Product Penetration** — Zone gauges, dealership readiness, specialist density
5. **Unique Manpower** — State/zone tables, unresolved identity count
6. **Audit & Exceptions** — Confidence distribution, duplicate log, data quality issues

---

## 📥 Excel Output — 8 Sheets

1. Unified_Master — all rows, mapped Star IDs, confidence-colored
2. Pending_Backlog — rolling backlog with priority scores
3. Duplicate_Log — flagged duplicates (never deleted)
4. Mapping_Confidence — every match method and score
5. Data_Quality_Report — future dates, missing names, anomalies
6. Skill_Analytics — pre/post/delta by employee
7. Recall_Action_List — sorted nomination list
8. Audit_Log — processing events with timestamps

---

## 🔒 Hard Constraints

- **100% Offline** — no API calls, no cloud, no internet at runtime
- **Zero Row Loss** — every uploaded row appears in output
- **No AI/LLMs** — only classical algorithms (fuzzy, phonetic, rule-based)
- **Deterministic** — same input always produces same output
- **Read-Only Dashboard** — no in-UI data editing
- **No Disk Writes** — all exports via io.BytesIO