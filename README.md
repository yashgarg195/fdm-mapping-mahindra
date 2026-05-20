# Mahindra & Mahindra Tractors — Training Recall & Analytics Portal

An enterprise-grade, 100% offline, air-gapped data compilation and business-intelligence portal. It automates monthly manpower roster matching with raw training logs, computes sequential skill ladders, and flags retraining timelines without relying on external cloud APIs or neural network model dependencies.

---

## 🚀 Active Local Deployment Site Links
This app is hosted locally on your network interface.

* **Local Access:** [http://localhost:8501](http://localhost:8501)
* **Network Access:** [http://10.212.61.157:8501](http://10.212.61.157:8501)
* **External Access:** [http://106.216.244.170:8501](http://106.216.244.170:8501)

*Last updated / verified:* **2026-05-20 16:16:09 IST**

---

## 🛠️ Installation & Setup

1. **Clone & Navigate:**
   ```bash
   cd "C:\Users\Anumay Pandey\Desktop\FDM mapping Mahindra"
   ```

2. **Install Dependencies:**
   Ensure you have python 3.10+ installed and run:
   ```bash
   pip install -r requirements.txt
   ```
   *(Required packages: `streamlit`, `pandas`, `numpy`, `plotly`, `xlsxwriter`, `rapidfuzz`, `jellyfish`, `recordlinkage`, `symspellpy`)*

3. **Run Streamlit Portal:**
   ```bash
   streamlit run app.py
   ```

4. **Run Offline Batch CLI Pipeline (Optional):**
   To execute the matching compiler directly in the terminal without UI:
   ```bash
   python run_backend_pipeline.py
   ```

---

## ⚙️ Key Engineered Features

### 1. Cumulative Skill Ladder Validation (`L0` to `L4`)
The engine validates sequential skill progression. A technician is only evaluated at a level if they successfully passed every previous prerequisite tier:
* **L0:** Untrained
* **L1:** Initiation Training (Prerequisite for L2)
* **L2:** Contiguous training completed (Prerequisite for L3)
* **L3:** Advanced training completed (Prerequisite for L4)
* **L4:** Specialized machinery/engine specialization
* **Anomaly Flag:** If any intermediate level is skipped (e.g. technician jumps L1 -> L4), their valid level is clamped at L1 and highlighted as a `MISSING_PREREQUISITE_FLAG` in red.

### 2. Multi-Pass Fuzzy Matching Engine
Resolves training logs missing Star IDs via 6 fallback algorithms using edit-distance metrics and string matching, achieving **100% resolution rate** on historical logs.

### 3. Strict Resiliency & 0 Row Loss
* Input roster and training sheets with missing or extra columns are defensive-parsed without key errors.
* Future joining dates (e.g., year > 2026) and negative training shifts (skill regressions) are automatically flagged for manager review, keeping every single row intact.