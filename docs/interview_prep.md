# Interview Preparation Guide: Customer Churn Intelligence

> **Role Focus:** Data Analyst · Business Analyst · Analytics Engineer  
> **Project:** Zorvio Customer Churn Intelligence

---

## 1. The 60-Second Elevator Pitch

> *"In this project, I answered the core executive question: **'Why are we losing customers?'** for Zorvio, a subscription SaaS company in India. Rather than training an opaque machine learning model, I built a complete end-to-end analytical solution using SQL, Python, and Power BI.*
>
> *I designed a deterministic 30,000-customer dataset, audited data quality with automated row-conservation tests, and engineered a leakage-free prospective observation pipeline. My analysis uncovered that a 30-day inactivity window increases churn risk by **6.37x (89.47% vs. 14.05%)**, while adopting team collaboration features drops churn from **24.67% down to 12.37% (a 1.99x retention moat)**.*
>
> *I discovered that **41.2% of active MRR is concentrated in the top Scale plan (₹6.55M)**, and built an interactive dashboard on a clean star schema with a prioritized triage queue for Customer Success. Finally, I delivered a 5-play, hypothesis-driven Churn Playbook with clear A/B test designs to protect over ₹1M in exposed MRR."*

---

## 2. Technical Q&A & Deep-Dive Defenses

### Q1: Why didn't you just train a Random Forest or XGBoost model to predict churn?
**Answer:**
> *"In a business context, executive teams and Customer Success managers don't need a black-box probability; they need transparent, actionable levers. A machine learning model that predicts churn with 92% accuracy doesn't tell a product manager what feature to fix or tell a CS rep why an account is unhappy.
>
> Instead, I built a transparent, rule-based risk framework based on empirical leading indicators (activity decay, support friction, and collaboration adoption). When evaluated prospectively out-of-time across 2025 monthly snapshots, our tiers proved strictly monotonic across populated tiers: churn increased from 12.41% in Low up to 22.28% in Medium, 68.46% in High, and 100.0% in Critical. This gave the CS team immediate confidence because every risk score directly mapped to an actionable retention play in our playbook."*

### Q2: How did you ensure your analysis didn't have data leakage?
**Answer:**
> *"Data leakage is the single most common pitfall in churn analytics. In my initial design (v1), I had anchored the 30-day feature window on each customer's own cancellation date for churned users. That meant I was measuring inactivity in the 30 days right before they left — capturing the consequence of churn rather than a predictor, which produced artificially high numbers.
>
> I recognized this flaw and refactored the entire pipeline to v2:
> 1. Selected ONE fixed observation date (`2025-11-01`, 60 days before the study end).
> 2. Computed all behavioral features strictly in the 30 days prior to that date (`2025-10-02` to `2025-10-31`).
> 3. Defined the churn label prospectively: did the customer cancel within the 60 days *after* `2025-11-01`?
> 4. Excluded customers who had already churned before `2025-11-01` (2,318 accounts) or had no usage logs.
>
> I then wrote automated pytest assertions in `tests/test_leakage_and_reconciliation.py` to programmatically verify that no feature used data on or after the observation date and no already-churned accounts entered the scored population."*

### Q3: Why did you use Wilson score confidence intervals instead of normal approximations?
**Answer:**
> *"The standard Wald normal approximation (`p ± 1.96 * sqrt(p(1-p)/n)`) performs notoriously poorly when proportions are close to 0 or 1, or when sample sizes are small — it can even produce confidence intervals that extend below 0% or above 100%.
>
> Because our churn rates ranged from 10% to over 90% across various sub-segments, I implemented Wilson score intervals. Wilson intervals maintain nominal 95% coverage, handle extreme proportions gracefully, and provide statistically honest bounds that prevent executives from overreacting to noisy small-sample variations."*

### Q4: Explain your Power BI Star Schema and why you didn't just load one flat denormalized CSV.
**Answer:**
> *"Loading a single large flat table in Power BI leads to bloated memory usage, severe DAX performance degradation, and misleading aggregations — especially when computing ARPU or customer counts across many-to-many subscription records.
>
> I architected a clean Star Schema:
> - **Dimension Tables:** `dim_customer`, `dim_plan`, `dim_date`.
> - **Fact Tables:** `fact_subscriptions`, `fact_monthly_churn`, `fact_cohort_retention`, `fact_customer_risk`, and `fact_high_risk_active`.
> 
> All relationships have 1-to-many cardinality with single-direction filtering. This guarantees high compression in the VertiPaq engine, makes DAX measures simple and intuitive, and allows global date and plan slicers to filter all report pages seamlessly."*

### Q5: How did you handle confounding variables (e.g. Simpson's Paradox)?
**Answer:**
> *"When analyzing acquisition channels, the raw data showed that App Store had the highest churn rate (58.86%) while Referral had the lowest (55.56%). Rather than immediately advising marketing to kill mobile ads, I performed a stratified cross-tabulation by plan tier.
> 
> I discovered that App Store users heavily skewed toward the Starter plan (individual mobile users), which naturally had lower initial onboarding completion. When controlling for plan tier, the channel difference was partially mitigated. Documenting this in our findings register (`F009`) prevented the company from making a misinformed marketing budget cut."*

---

## 3. High-Value Behavioral Scenarios (STAR Method)

### Scenario 1: "Tell me about a time you caught data leakage or a methodological flaw in your work and resolved it."
- **Situation:** While evaluating leading indicators in v1, my model showed that inactive customers had a 100% churn rate and the Critical risk tier had near-perfect separation.
- **Task:** I audited the underlying SQL and realized the 30-day feature window was anchored on each customer's own churn date. I was measuring inactivity right as customers were cancelling — a severe temporal leakage bug that made churn an input to the feature rather than a prospective outcome.
- **Action:** I restructured the analytical framework: I locked a single fixed observation date (`2025-11-01`), filtered for accounts active at that moment, measured features strictly in the 30 days prior, and evaluated churn prospectively over the subsequent 60 days. I added automated pytest assertions to guarantee no future data leaked into features.
- **Result:** The corrected results were realistic and defensible: inactivity proved to be a powerful prospective signal with a **6.37x relative risk** (89.47% vs 14.05%), collaboration adoption showed a **1.99x retention moat** (24.67% vs 12.37%), and the risk tiers remained strictly monotone (Critical 100.0% > High 68.46% > Med 22.28% > Low 12.41%). Being upfront about the leakage and resolving it added immense credibility to the analysis.

### Scenario 2: "Tell me about a time you found an unexpected anomaly in data."
- **Situation:** While evaluating monthly churn trends for Zorvio, I noticed voluntary churn doubled from a steady 5.5% baseline to an alarming 11.18% (12.44% total churn) in October 2025.
- **Task:** I needed to diagnose whether this was a seasonal pattern, a data tracking bug, or an operational incident.
- **Action:** I queried support ticket volumes and daily usage logs for that month. I discovered an unprecedented cluster of "failed action" logs and severe technical support tickets centered on an infrastructure outage.
- **Result:** I verified this was an acute platform outage. By isolating the outage months in my SQL queries, I prevented executive reporting from misinterpreting a one-time reliability event as structural product churn, and quantified the peak outage revenue impact at ₹2.29M realized churned MRR.

### Scenario 3: "How do you translate technical data findings into executive business actions?"
- **Situation:** Many data analysts stop after presenting charts and correlation coefficients.
- **Task:** I wanted to bridge the gap between SQL metrics and departmental execution.
- **Action:** I authored an operational Churn Playbook (`churn_playbook.md`). For each major finding, I defined: (1) an observable trigger signal, (2) an owning department (Product, CS, Support, or Growth), (3) a concrete workflow action, and (4) an A/B test design with primary and guardrail metrics.
- **Result:** Instead of handing leadership a passive dashboard, I delivered an actionable priority queue (`fact_high_risk_active`) that allowed the Customer Success team to immediately triage high-MRR accounts and protect over ₹1.2M in exposed revenue.
