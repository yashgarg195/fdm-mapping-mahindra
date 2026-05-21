# Mahindra & Mahindra Tractors — Training Analytics & Manpower Intelligence Platform

An enterprise-grade, offline-capable identity resolution and training governance portal.

---

## 🌐 Dashboard Access

* **Live Web Portal:** [https://mec-training-analysis.streamlit.app/](https://mec-training-analysis.streamlit.app/)
* **Local Server:** `http://localhost:8501`

To run locally, double-click [start_dashboard.bat](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/start_dashboard.bat) or run:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Core Project Files

* [app.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/app.py) — Streamlit Web Portal entry point
* [config/constants.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/config/constants.py) — Mappings and configurations
* [core/matching.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/core/matching.py) — 7-Pass Identity Resolution Engine
* [core/training_pipeline.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/core/training_pipeline.py) — Backlog & Nomination Engine
* [core/deduplication.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/core/deduplication.py) — Exact & Fuzzy deduplication logic
* [analytics/kpi_engine.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/analytics/kpi_engine.py) — KPI computations
* [ui/audit_tab.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/ui/audit_tab.py) — Audit & Exception Queue tab UI
* [export/excel_export.py](file:///C:/Users/Anumay%20Pandey/Desktop/FDM%20mapping%20Mahindra/export/excel_export.py) — 8-sheet styled Excel report builder

---

## 📥 Web Portal File Processing Pipeline

When Excel files are uploaded:

1. **Alignment**: Automatically maps variable column headers (e.g. `STARID` $\rightarrow$ `Star ID`).
2. **Cleansing**: Standardizes names, strips titles, and normalizes phone/Aadhar strings.
3. **Deduplication**: Automatically flags duplicate IDs and fuzzy name duplicates under different IDs.
4. **Resolution**: Matches training records to the master roster through 7 progressive fuzzy/phonetic passes.
5. **Backlog & Nomination**: Groups workers by eligibility status and ranks priority candidates for upcoming training.
6. **Reporting**: Displays real-time dashboards (Overview, Penetration, Skills, Manpower, Audits) and generates a downloadable 8-sheet Excel master file.
