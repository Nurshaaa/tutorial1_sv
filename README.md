# 📊 Scientific Visualization: Socioeconomic and Demographic Analysis of Malaysia

This repository contains the source code and datasets for a multi-page interactive Streamlit dashboard developed for scientific visualization assignments. The project integrates multiple open-source datasets from the Department of Statistics Malaysia (DOSM) to analyze socioeconomic and demographic trends across states in Malaysia.

## 👥 Author
* **Name:** Siti Nurul Nurshafika Binti Azman
* **Repository:** `tutorial1_sv`

---

## 📂 Project Structure
```text
tutorial1_sv/
│
├── app.py                      # Homepage of the Streamlit application
├── pages/                      # Directory containing multi-page views
│   ├── 1_Income_and_Births.py      # Page 1: Household Income + Annual Live Births
│   ├── 2_Marriages_and_Births.py   # Page 2: Annual Marriages + Annual Live Births
│   └── 3_Income_and_Marriages.py   # Page 3: Household Income + Annual Marriages
│
├── birth_state (1).csv         # Dataset 1: Annual Live Births by State
├── marriages_state.csv         # Dataset 2: Annual Marriages by State
├── hh_income_state.csv         # Dataset 3: Household Income by State
└── requirements.txt            # Python package dependencies
