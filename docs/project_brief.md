# Project Brief: Customer Churn Intelligence

**Project title:** Customer Churn Intelligence — "Why Are We Losing Customers?"  
**Company (fictional):** Zorvio  
**Author:** [Student Name], Final-Year B.Tech Computer Science  
**Document status:** Approved — Stage 0  
**Last updated:** 2026-09-28

---

## 1. Business Problem

Zorvio is a subscription SaaS product for individuals and small teams in India. It offers three plans (Starter ₹499/mo, Growth ₹1,499/mo, Scale ₹3,999/mo) on monthly or annual billing. Customers acquire the product through multiple channels: organic search, paid social, referral, app store, and campus/partnership programmes.

Like most SaaS businesses, Zorvio loses a share of its paying customers every month. Customer acquisition is expensive. Retaining an existing customer is substantially cheaper than replacing one. The business therefore needs to understand **not just that customers are leaving, but why, which ones, and when** — so that specific actions can be targeted at the right customer groups at the right time.

**This project does not build a churn-prediction model.** It performs a complete, defensible business analysis and delivers a Churn Playbook: a set of evidence-based, prioritised signals and recommended actions that the Customer Success, Product, and Billing teams can act on.

---

## 2. The 12 Business Questions

| # | Question |
|---|---|
| Q1 | What is the current churn rate? |
| Q2 | Is churn increasing or decreasing? |
| Q3 | Which customer segments churn the most? |
| Q4 | Are new customers more likely to churn than existing ones? |
| Q5 | Does product/feature usage affect churn? |
| Q6 | Does inactivity predict churn? |
| Q7 | Which acquisition channels produce higher-churn customers? |
| Q8 | Which customer types generate the most revenue? |
| Q9 | Where is the greatest revenue at risk? |
| Q10 | What are the strongest observable leading indicators of churn? |
| Q11 | Can we identify high-risk customer groups? |
| Q12 | What should the business do? |

Each question must be answered by the end of the project, or explicitly marked **"cannot be answered from this data because…"** in `docs/question_traceability.md`.

---

## 3. Scope

**In scope:**
- Synthetic data generation representing ~24 months of Zorvio history (25,000–40,000 customers)
- SQL analysis (SQLite): quality audit, cleaning, metric calculation, segmentation, cohort analysis
- Python EDA: distributions, visualisations, statistical testing (Wilson CIs, relative risk, stratification)
- Behavioral leading indicators: snapshot-based, leakage-free, time-validated
- Revenue at risk: three distinct measures (realized, exposed, estimated)
- Power BI package: star-schema export, DAX measures, build guide, wireframes, theme
- Churn Playbook: evidence-based, hypothesis-framed, with test designs
- Documentation: data dictionary, metric definitions, business report, interview prep, demo script

**Out of scope (unless explicitly approved):**
- Machine learning (except optional logistic regression extension at Stage 5, with approval)
- Real-time or streaming data
- Cloud infrastructure, Docker, Airflow, dbt
- Benchmarking against real industry churn rates (data is synthetic)
- Any claim that findings generalise beyond the simulated company

---

## 4. Non-Goals

- **Not a churn prediction tool.** The risk framework is transparent rules, not a trained model.
- **Not a real business case.** All findings describe the synthetic Zorvio dataset only.
- **Not a data engineering project.** The pipeline is a clean Python + SQLite script, not a production ETL.
- **Not an ML portfolio piece.** The value lies in analytical rigor, business framing, and communication.

---

## 5. Fictional Company: Zorvio

| Attribute | Detail |
|---|---|
| Product | Subscription SaaS — productivity and collaboration for individuals and SMBs |
| Geography | Indian cities, grouped into Tier 1 / Tier 2 / Tier 3 |
| Plans | Starter (₹499/mo), Growth (₹1,499/mo), Scale (₹3,999/mo) |
| Billing cycles | Monthly, Annual |
| Acquisition channels | Organic Search, Paid Social, Referral, App Store, Campus/Partnership |
| Customer types | Individual, Small Team (2–10), Mid Team (11–50) |
| Data period | ~24 months (approx. Jan 2024 – Dec 2025) |
| Customer count | ~30,000 (target; exact count determined by generator) |

---

## 6. Deliverables Summary

1. Synthetic dataset (generator script + data)
2. SQLite database (`db/churn.db`)
3. SQL analysis scripts (`sql/`)
4. Jupyter notebooks with full EDA (`notebooks/`)
5. Findings register (`outputs/findings_register.csv`)
6. Churn Playbook (`playbook/churn_playbook.md` + `.csv`)
7. Power BI package (`powerbi/`)
8. Business report (`docs/business_report.md`)
9. Interview prep guide (`docs/interview_prep.md`)
10. Full documentation suite (`docs/`)

---

## 7. Key Constraints

- **Reproducibility:** generator uses a fixed seed; pipeline re-run produces identical results
- **File size limit:** no committed file exceeds 25 MB
- **No leakage:** all indicator analysis uses snapshot-based features; enforced by tests
- **Statistical honesty:** Wilson CIs on every rate; minimum segment sizes; stratification
- **No causal claims:** all language is associational unless from a randomised experiment
- **Synthetic-data notice:** visible in README (line 1), data dictionary, dashboard, and business report
