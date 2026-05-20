# Technology Stack

## Core Languages
- **Python:** Primary language for the application backend, data processing pipelines, and the Streamlit interface.
- **TypeScript & JavaScript:** Used for the React-based Enterprise Dashboard UI.

## Application Frameworks
- **Streamlit:** The main framework for the web portal, providing the UI for data upload, processing, and visualization.
- **React (with Vite):** Framework for the standalone Enterprise Dashboard UI.

## Data Processing & Identity Resolution
- **pandas & numpy:** Core libraries for data manipulation and numerical operations.
- **Identity Resolution Suite:** Leveraging `rapidfuzz`, `recordlinkage`, `symspellpy`, and `jellyfish` for advanced fuzzy matching, phonetic resolution, and deduplication.

## Visualization & Reporting
- **Plotly:** Used for generating interactive charts and dashboards within Streamlit.
- **Excel Export:** `XlsxWriter` and `openpyxl` are used for building complex, styled multi-sheet Excel reports.

## Frontend Styles & UI Components
- **Tailwind CSS:** For utility-first styling in the React dashboard.
- **Radix UI & Shadcn:** Headless and styled UI components for the React dashboard.
- **Material UI (MUI):** Additional component library used in the dashboard UI.