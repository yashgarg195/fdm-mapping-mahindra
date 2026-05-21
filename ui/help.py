import streamlit as st

def render_help():
    st.markdown("### Help & Guide")
    st.markdown("""
**How to use this dashboard:**

1. **Upload Files** — Use the file uploaders in the sidebar to upload your Manpower Roster and Training Data Excel files.
2. **Assign Types** — Files are automatically assigned the correct type based on the dropzone you use.
3. **Run Pipeline** — Click **Run Pipeline** to process the data through the 7-pass identity resolution engine.
4. **Apply Filters** — Use the Global Filters panel on the main screen to narrow down by Zone, State, Designation, or Dealer.
5. **Explore Tabs** — Navigate across tabs to view analytics.
6. **Export** — Go to the **Exports** tab to download individual or combined reports.

---

**Tabs at a Glance:**

| Tab | Purpose |
|-----|---------|
| Overview | National KPIs + All-India graphical dashboard |
| Pending & Nominations | Backlog priority list |
| Skill Analytics | Pre/post training skill scores (1–10 scale) |
| Unique Manpower | State/zone headcount breakdown |
| Audit & Exceptions | Duplicate log, unresolved queue, data quality |
| Exports | Download all reports |
| Help & Guide | This instruction manual |

---

**Confidence Tiers:**

- 🟢 **HIGH** — Exact ID match with matching name
- 🟡 **MEDIUM** — Strong match with minor name variation
- 🟠 **LOW** — Weak match — requires supervisor review
- 🟣 **POSSIBLE** — Similar name at same dealership (Possible Match)
- ⬛ **UNRESOLVED** — Could not be matched — excluded from KPIs

---

**Skill Scale (1–10):**

| Score | Level | Meaning |
|-------|-------|---------|
| 2 | Beginner | Untested / No training |
| 4 | Basic | Completed L1 |
| 6 | Intermediate | Completed L2 |
| 8 | Advanced | Completed L3 |
| 10 | Expert | Completed L4 |
""")
