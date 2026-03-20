# 🏥 HSE Hospital Waiting List Analysis (2019–2026)

**Python · SQL · Streamlit · Power BI**  
**End-to-End Analytics | 8 Years of Real Government Data | 50+ Hospitals**

---

## Why I Built This

Ireland spent **€437 million in 2024** to reduce hospital waiting lists.

**The result? The waiting list still grew by ~40,000 patients.**

This project answers a critical question:

> **Why is the system failing despite increased funding — and what actually needs to change?**

Using 8 years of official NTPF data (2019–2026), I built a full analytics pipeline to identify:
- Where the bottlenecks actually are
- Which hospitals are improving vs failing
- Why the system structurally cannot reduce waiting lists
- What interventions would realistically fix the problem

---

## 🎯 Key Insight (TL;DR)

> **Ireland doesn’t have a funding problem — it has a throughput problem.**

Patients are entering the system faster than they are being treated.

Until that imbalance is fixed, **waiting lists will continue to grow regardless of spending.**

---

## Dashboard Screenshots

**Overview and KPIs**
![Overview](screenshots/Screenshot1.png)

**National Waiting List Trend (2019–2026)**
![National Trend](screenshots/Screenshot2.png)

**Hospital Performance — Volume and Long Wait %**
![Hospital Performance](screenshots/Screenshot3.png)

**Specialty Analysis — Orthopaedics, Dermatology, ENT Lead**
![Specialty Analysis](screenshots/Screenshot4.png)

**Sláintecare Target Tracker**
![Slaintecare](screenshots/Screenshot5.png)

**Browse All Data — Searchable by Hospital and Specialty**
![Browse Data](screenshots/Screenshot6.png)

---

## Project Pipeline

```
NTPF Open Data (ntpf.ie)
        ↓
Python Downloader   →   30+ CSV files (2019–2026)
        ↓
Python Cleaning     →   3 unified analytical tables
        ↓
SQLite Database     →   17 analytical SQL queries
        ↓
Streamlit Dashboard + Power BI
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python (requests, pandas)** | Downloaded 30+ CSVs from NTPF, handled inconsistent column names across 8 years, merged into 3 clean tables |
| **SQLite** | Stored cleaned data, wrote 17 queries using window functions, CTEs, year-on-year comparisons |
| **Streamlit + Plotly** | Interactive dashboard with hospital/year filters, trend charts, wait band analysis, Sláintecare tracker |
| **Power BI** | Secondary executive-style dashboard |

---

## Data Source

Official Irish government open data published monthly by the National Treatment Purchase Fund (NTPF).

- Source: [ntpf.ie/waiting-list-data/open-data](https://www.ntpf.ie/waiting-list-data/open-data/)
- Updated on the third Friday of every month
- Covers all public hospitals in Ireland
- Free to use and download

---

## Key Findings

## 🔍 Key Findings & Business Implications

### 1. The System Is Mathematically Failing

- In 2024, **new patients added > patients treated**
- Even with €437M funding, backlog increased

👉 **Conclusion:**
This is a **capacity imbalance**, not a budget issue.

👉 **What decision-makers should do:**
- Track **monthly inflow vs outflow ratio** as a core KPI
- Shift focus from “total waiting list” → **system throughput efficiency**

---

### 2. COVID Didn’t Improve the System — It Hid the Problem

- Waiting lists dropped in 2020–21
- But this was due to **collapse in referrals**, not better performance
- Post-COVID → demand surged + backlog exploded

👉 **Conclusion:**
The system never improved — it was temporarily suppressed.

👉 **What decision-makers should do:**
- Avoid interpreting short-term improvements without **contextual drivers**
- Build forecasting models based on **demand shocks**

---

### 3. 4 Specialties Drive the Entire Crisis

- Orthopaedics, Ophthalmology, ENT, Dermatology dominate waiting lists
- These are **high-volume, non-emergency procedures**

👉 **Conclusion:**
The “national crisis” is actually a **targetable bottleneck in 4 areas**

👉 **What decision-makers should do:**
- Allocate **specialty-specific budgets**, not general funding
- Expand capacity specifically in these 4 specialties
- Measure **wait time per specialty**, not just total volume

---

### 4. Funding Alone Has Diminishing Returns

- €437M investment did not reduce backlog
- Indicates inefficiency in **how resources are deployed**

👉 **Conclusion:**
Adding money to a constrained system ≠ improved output

👉 **What decision-makers should do:**
- Track **cost per treated patient**
- Optimize **existing infrastructure before increasing funding**
- Audit underutilised operating capacity

---

### 5. Hospital Performance Variation Is Massive

- Some hospitals reduced long-wait cohorts
- Others worsened despite similar constraints

👉 **Conclusion:**
Performance differences are driven by **operations, not size or funding**

👉 **What decision-makers should do:**
- Create **hospital-level performance benchmarks**
- Replicate high-performing hospital strategies
- Introduce accountability using **ranked performance dashboards**

---

### 6. Sláintecare Targets Were Never Realistic

- Majority of patients consistently exceed target wait times
- No year shows alignment with policy targets

👉 **Conclusion:**
Targets were set without matching system capacity

👉 **What decision-makers should do:**
- Redefine targets based on **real throughput capacity**
- Introduce phased targets instead of fixed unrealistic benchmarks

---

## 🔮 Predictive Insights

Based on 8 years of trend data:

- If current inflow/outflow imbalance continues,
  👉 Waiting lists will **continue growing year-on-year**

- Even with increased funding,
  👉 Backlog reduction will remain minimal without structural changes

- High-volume specialties will continue to dominate,
  👉 Unless targeted interventions are implemented

👉 **Prediction:**
Without intervention, the system will remain in a **permanent backlog state**


## What Could Actually Fix This (Data-Driven Recommendations)
 

### 1. Fix Throughput First
- Increase treatment capacity before increasing funding
- Track **patients treated per month per hospital**

---

### 2. Specialisation Strategy
- Build dedicated surgical pipelines for:
  - Orthopaedics
  - Ophthalmology
  - ENT
- These 3–4 areas will deliver the highest ROI

---

### 3. Control Demand at Entry Point
- Strengthen GP triage
- Reduce unnecessary referrals into hospital system

---

### 4. Maximise Existing Infrastructure
- Extend operating hours (evenings + weekends)
- Increase utilisation of existing theatres

---

### 5. Introduce Performance Accountability
- Rank hospitals by:
  - Wait time reduction
  - Long-wait cohort change
- Use data to drive operational improvements
---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Ishankasare/HSE-Hospital-Wait-Times-Analysis

# Install dependencies
pip install -r requirements.txt

# Step 1 — Download all NTPF data files
python src/download_data.py

# Step 2 — Clean and merge
python src/clean_data.py

# Step 3 — Launch dashboard
streamlit run src/dashboard.py
```

For SQL analysis — open DB Browser for SQLite (free), connect to `data/hse_waits.db`, run queries from `sql/analysis_queries.sql`.

---

## Project Structure

```
HSE-Hospital-Wait-Times-Analysis/
├── README.md
├── INSIGHTS.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── download_data.py      ← downloads all NTPF CSVs (2019–2026)
│   ├── clean_data.py         ← cleans, merges, saves to SQLite + CSV
│   └── dashboard.py          ← Streamlit interactive dashboard
├── sql/
│   └── analysis_queries.sql  ← 17 analytical queries
├── data/
│   ├── raw/                  ← downloaded NTPF CSVs (gitignored)
│   └── processed/            ← cleaned tables (committed)
├── dashboard/
│   └── HSE-WaitTimes.pbix    ← Power BI dashboard
└── screenshots/
```

---

## What I Learned

- Ability to work with **messy, real-world government datasets**
- - Handling 8 years of inconsistently formatted CSVs with changing column names and restructured hospital names
- Building **end-to-end data pipelines** (ETL → SQL → Dashboard)
- Translating data into **clear business decisions**
- Identifying **system bottlenecks and inefficiencies**
- Communicating insights to **non-technical stakeholders**


---

*Data: National Treatment Purchase Fund (NTPF) · ntpf.ie · Official Irish Government Open Data · Updated monthly*
