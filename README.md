# ⚠️ SYNTHETIC DATA NOTICE
> **All data in this project is entirely synthetic and computer-generated.**
> It represents a fictional Indian SaaS company called **Zorvio**.
> No finding describes any real company, industry, or customer population.
> This project demonstrates analytical method, not real-world churn dynamics.

---

# Customer Churn Intelligence: "Why Are We Losing Customers?"

*A complete business analysis portfolio project — SQL · Python · Power BI · Churn Playbook*

**Built by:** [Student Name] | Final-Year B.Tech Computer Science  
**Target roles:** Data Analyst · Business Analyst  
**Status:** ✅ Complete — Stages 1–8 Fully Implemented  

---

## Key Findings

All findings trace directly to [`outputs/findings_register.csv`](outputs/findings_register.csv) and empirical SQL/Python pipeline outputs:

| Finding ID | Business Area | Core Finding | Key Metric / Evidence | Source |
|---|---|---|---|---|
| **F001** | Headline Churn (Q1) | Current monthly churn rate is steady at ~6.3% under normal operations; cumulative lifetime cohort share is 56.6%. | Latest full-month (Dec 2025): **6.31% total** (5.10% voluntary). Baseline mean: **6.67%**. | [`03_historical_churn_Q1_Q2.sql`](sql/03_historical_churn_Q1_Q2.sql) |
| **F002** | Churn Trend (Q2) | Churn is event-driven; transient infrastructure outage in late 2025 doubled voluntary cancellations before recovering. | Outage peak (Oct 2025): **12.44% total** (11.18% voluntary) vs baseline **5.52%**. | [`03_historical_churn_Q1_Q2.sql`](sql/03_historical_churn_Q1_Q2.sql) |
| **F003/F004** | Cohorts & Tenure (Q3/Q4) | Steep early mortality cliff in first 90 days; hazard rate drops 20x for mature accounts. Churned tenure averages 6 months. | Hazard per customer-month: M0–3 **46.5%** $\rightarrow$ M13+ **2.2%**. Churned avg tenure: **6.0 months**. | [`04_cohort_retention_Q3_Q4.sql`](sql/04_cohort_retention_Q3_Q4.sql) |
| **F005** | Plan Hazard (Q3) | Churn hazard per customer-month is invariant across plan tiers when accounting for time at risk. | Growth: **7.41%**, Scale: **7.39%**, Starter: **7.35%** per customer-month. | [`05_segmentation.sql`](sql/05_segmentation.sql) |
| **F006** | Billing Frequency (Q3) | Annual billing contracts exhibit lower churn hazard across all tenure bands (commitment effect). | Annual: **6.07%** vs Monthly: **7.86%** per customer-month (M0–3: 45.0% vs 47.1%). | [`05_segmentation.sql`](sql/05_segmentation.sql) |
| **F007** | Inactivity Signal (Q6/Q10) | 30-day platform inactivity is the strongest observable prospective leading indicator of cancellation. | Inactive: **89.47% churn** vs Active: **14.05%** ($RR = 6.37\times$, $n=95 < 200$ floor). | [`07_feature_usage.sql`](sql/07_feature_usage.sql) |
| **F008** | Product Stickiness (Q5) | Accounts adopting multi-user team collaboration features exhibit half the churn hazard (2x moat). | Collaboration users: **12.37% churn** vs Non-users: **24.67%** ($RR = 1.99\times$, $n=3,563$). | [`07_feature_usage.sql`](sql/07_feature_usage.sql) |
| **F009** | Channel Quality (Q7) | App Store's raw lifetime churn elevation is driven by 82.1% Starter plan skew rather than channel deficiency. | Hazard per customer-month: App Store Starter **7.74%** vs Organic Starter **7.22%**. | [`06_channel_and_tenure.sql`](sql/06_channel_and_tenure.sql) |
| **F010** | Revenue Concentration (Q8) | Scale accounts represent the highest financial exposure; 1 Scale account equals 8 Starter accounts in MRR. | Active MRR: **INR 15.90M**; Scale holds **INR 6.55M (41.2%)** across only 1,735 accounts. | [`08_revenue_and_risk.sql`](sql/08_revenue_and_risk.sql) |
| **F011** | Revenue at Risk (Q9) | Three distinct measures quantify historical loss, current exposure, and prospective expected downside. | Realized: **INR 21.00M**; Exposed: **INR 520K (inst.) / INR 3.84M (tot.)**; Expected: **INR 411,712** [Wilson CI: INR 391K–432K]. | [`08_revenue_and_risk.sql`](sql/08_revenue_and_risk.sql) |
| **F012** | Risk Monotonicity (Q11) | Rule-based risk framework validates strictly monotonically in out-of-time prospective testing (2025). | Low: **12.41%** $\rightarrow$ Med: **22.28%** $\rightarrow$ High: **68.46%** $\rightarrow$ Critical: **100.0%**. | [`09_high_value_churn.sql`](sql/09_high_value_churn.sql) |

---

## Power BI Dashboard & Action Artifacts

- **Executive Report:** [`docs/business_report.md`](docs/business_report.md) — complete synthesis answering all 12 business questions.
- **Power BI Package:** [`powerbi/`](powerbi/) — build guide, star-schema data model, production DAX formulas, UI wireframes, and custom theme.
- **Churn Playbook:** [`playbook/churn_playbook.md`](playbook/churn_playbook.md) — 5 prioritised, hypothesis-driven operational retention plays for CS, Product, Support, and Growth teams.
- **Interview Prep:** [`docs/interview_prep.md`](docs/interview_prep.md) — elevator pitch, technical methodology defense, and STAR stories.

---

## Project Workflow

```
Business Problem → Data Generation → SQL Analysis → Data Cleaning → EDA
    → Segmentation → Root-Cause Analysis → Leading Indicators
        → Revenue at Risk → Power BI Dashboard → Churn Playbook
```

---

## Methodology Highlights

| Principle | How it is implemented |
|---|---|
| Churn definition | Stated precisely in `docs/metric_definitions.md`; never changed silently |
| Leakage prevention | Snapshot-based features; post-churn fields excluded; enforced by tests |
| Time-based validation | Risk framework thresholds set on earlier months; evaluated on later months |
| Statistical honesty | Wilson CIs on every rate; sample-size floor; stratified checks for confounding |
| Honest null results | Non-effects and reversals reported in findings register |
| Causal language | "Associated with" / "may indicate" — no causal claims without an experiment |

---

## Skills Demonstrated

| Skill | Where to look |
|---|---|
| SQL (CTEs, window functions, cohorts) | `sql/` directory |
| Python EDA (pandas, seaborn, scipy) | `notebooks/` directory |
| Data cleaning & quality audit | `notebooks/01_data_understanding_and_quality.ipynb` |
| Segmentation & behavioral analysis | `notebooks/03_segmentation_and_tenure.ipynb` |
| Leading indicators & risk framework | `notebooks/06_leading_indicators.ipynb` |
| Revenue analysis | `notebooks/08_revenue_at_risk_and_synthesis.ipynb` |
| Power BI (data model + DAX) | `powerbi/` directory |
| Business storytelling | `playbook/churn_playbook.md`, `docs/business_report.md` |

---

## How to Reproduce

```bash
# 1. Clone the repo
git clone <repo-url>
cd customer-churn-intelligence

# 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 3. Run the full pipeline (generate → clean → load DB → export)
python run_pipeline.py

# 4. Run tests
pytest tests/ -v

# 5. Launch notebooks
jupyter notebook notebooks/
```

*Expected full pipeline runtime: < 5 minutes on a standard laptop.*

---

## Repository Tour

```
customer-churn-intelligence/
├── _ground_truth/        ← DO NOT OPEN until Stage 6 (generator spec + injected issues)
├── synthetic_data/       ← Deterministic data generator (seeded)
├── data/                 ← raw → staging → clean → exports (for Power BI)
├── db/                   ← SQLite database (churn.db)
├── sql/                  ← 11 analysis scripts
├── notebooks/            ← 8 Jupyter notebooks (EDA → synthesis)
├── src/                  ← Reusable Python functions (cleaning, metrics, CIs)
├── tests/                ← pytest: leakage, reconciliation, row-count tests
├── outputs/              ← figures/, tables/, findings_register.csv
├── powerbi/              ← Build guide, DAX measures, data model, theme, wireframes
├── playbook/             ← churn_playbook.md + .csv
└── docs/                 ← All documentation (brief, dictionary, report, interview prep)
```

---

## Limitations and Honest Caveats

- **Synthetic data:** findings describe only this simulated dataset. Do not generalise.
- **Correlation, not causation:** all findings are associational unless a randomised test is run.
- **Right-censoring:** active customers at the data end-date have unresolved outcomes; handled explicitly in cohort analyses.
- **Single simulated company:** segment effects are designed to be plausible but not calibrated to any real SaaS benchmark.
- **How I would approach this with real company data:** documented in `docs/assumptions_and_limitations.md`.

---

## Optional Demo Video

> *(Link added after recording. See `docs/demo_script.md` for the walkthrough script.)*
