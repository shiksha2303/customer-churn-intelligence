# Executive Business Report: "Why Are We Losing Customers?"

**Company:** Zorvio SaaS (Fictional Indian B2B/B2C Productivity & Collaboration Platform)  
**Author:** [Student Name] | Final-Year B.Tech Computer Science  
**Target Roles:** Data Analyst · Business Analyst  
**Period Analyzed:** January 2024 – December 2025 (~24 Months, 30,000 Customers)  
**Deliverable Status:** Final Analysis & Synthesis (Reconciled Out-of-Time Validation)  

> ⚠️ **SYNTHETIC DATA NOTICE:** All data in this report is entirely computer-generated and describes fictional SaaS company Zorvio. It demonstrates analytical methodology, leakage-free feature design, person-time hazard rates, and business problem-solving. Findings do not reflect any real entity.

---

## 1. Executive Summary

Zorvio operates a three-tier subscription SaaS model in India (Starter ₹499/mo, Growth ₹1,499/mo, Scale ₹3,999/mo). Across 24 months of customer history, the company reached **₹15,903,978.51 in active Monthly Recurring Revenue (MRR)** across **13,020 active customer accounts** as of December 31, 2025.

Key empirical findings from the investigation:
- **Baseline Monthly Churn:** Under steady-state conditions, monthly total churn averages **6.67%** (voluntary: **5.52%**, involuntary: **1.15%**). The latest full month (December 2025) recorded a **6.31% monthly churn rate** (voluntary: **5.10%**). Across the entire 2-year cumulative cohort, **56.58% of accounts have ever churned** (strictly a cumulative cohort total, not a monthly rate).
- **The Outage Shock:** In October 2025, voluntary churn surged to a peak of **11.18%** (**12.44% total churn**) following an infrastructure outage, returning to baseline within 60 days.
- **Tenure Mortality Cliff:** Churn hazard per customer-month is concentrated in early tenure: **46.5% per customer-month in Months 0–3**, dropping to **13.9% in Months 4–6**, **6.0% in Months 7–12**, and **2.2% beyond Month 13**.
- **Billing Frequency at Equal Tenure:** Annual contracts exhibit lower churn hazard across every tenure band (0–3m: 45.0% vs 47.1%; 4–6m: 12.2% vs 14.6%; 7–12m: 4.9% vs 6.5%; 13+m: 1.9% vs 2.3%; overall 6.07% vs 7.86% per customer-month).
- **Out-of-Time Leading Indicators (2025 Holdout):**
  - **30-Day Inactivity:** Zero sessions in 30 days is associated with an **89.47% prospective churn rate** vs **14.05%** for active accounts (Relative Risk: **6.37x**). *(Note: evaluated on $n=95$ inactive accounts with 85 churners; below the 200-account sample floor, providing strong directional evidence).*
  - **Collaboration Adoption:** Team collaboration feature adoption is associated with half the churn hazard: **12.37%** vs **24.67%** for non-users (Relative Risk: **1.99x**, $n=3,563$, 879 events).
- **Revenue Concentration:** While Starter accounts comprise 54.1% of accounts, **Scale accounts concentrate 41.2% of active MRR (₹6.55M)**.
- **Three Dimensions of Revenue at Risk:**
  1. *Realized Churned MRR:* **₹21,003,006.85** cumulative revenue lost over 24 months (peaked at ₹2.29M in Oct 2025).
  2. *Exposed MRR:* **₹520,212.02** in Medium/High risk tiers in the instrumented cohort (~₹3.84M scaled across total active base).
  3. *Expected MRR at Risk (60-day Estimate):* **₹411,711.58** [95% Wilson range: **₹391,612 – ₹432,158**].

---

## 2. Answers to the 12 Core Business Questions

| # | Business Question | Empirical Finding & Evidence | Business Implication | Finding ID |
|---|---|---|---|---|
| **Q1** | *What is the current churn rate?* | Latest monthly churn rate (Dec 2025) is **6.31% total** (5.10% voluntary, 1.21% involuntary). Baseline mean monthly churn is **6.67% total** (5.52% voluntary). Cumulative ever-churned cohort share is **56.58%**. | Current monthly attrition is stable under normal operations. Cumulative attrition requires continuous customer acquisition. | `F001` |
| **Q2** | *Is churn increasing or decreasing?* | Monthly churn remained stable (~5.0%–5.5% voluntary), spiking to **12.44% total / 11.18% voluntary in October 2025** after an infrastructure outage, returning to 6.31% within 60 days. | Churn is event-sensitive rather than structurally deteriorating. Infrastructure uptime directly protects revenue. | `F002` |
| **Q3** | *Which customer segments churn the most?* | Churn hazard per customer-month is nearly identical across plans: Growth (7.41%), Scale (7.39%), Starter (7.35%). However, **Annual billing exhibits lower churn per customer-month across all tenure bands (6.07% vs 7.86%)**. | Plan tier does not shield against churn; contract duration correlates with improved retention. | `F005`, `F006` |
| **Q4** | *Are new customers more likely to churn than existing ones?* | Yes. Churn hazard per customer-month is **46.5% in Months 0–3**, dropping to **2.2% beyond Month 13** (a 20x drop). Churned customer average tenure is **6.0 months** vs **12.8 months** for active accounts. | Steep early mortality cliff. Onboarding interventions must concentrate on Days 1–45. | `F003`, `F004` |
| **Q5** | *Does product/feature usage affect churn?* | In out-of-time validation (2025), accounts using collaboration features churn at **12.37%**, compared to **24.67%** for non-users (Relative Risk: **1.99x**; $n=3,563$, 879 events). | Multi-user team workflows correlate with a 2x retention moat. | `F008` |
| **Q6** | *Does inactivity predict churn?* | Zero sessions over 30 days yields an **89.47% prospective churn rate** vs **14.05%** for active accounts (Relative Risk: **6.37x**; $n=95$, 85 churners). | Inactivity is the strongest observable precursor to cancellation. Automated re-engagement must trigger before Day 14. | `F007` |
| **Q7** | *Which acquisition channels produce higher-churn customers?* | When controlling for plan and tenure, channel hazard is uniform: App Store Starter (7.74%), Growth (8.15%), Scale (7.84%) vs Organic Starter (7.22%), Growth (7.24%), Scale (7.57%). | App Store's raw lifetime churn elevation is driven by an 82.1% Starter plan skew rather than channel deficiency. | `F009` |
| **Q8** | *Which customer types generate the most revenue?* | **Scale accounts generate 41.2% of active MRR (₹6,553,481)** from only 13.3% of accounts (1,735 accounts, avg MRR ₹3,777). Starter accounts generate 21.1% of MRR from 54.1% of accounts. | Revenue is heavily concentrated in mid-sized teams. High-touch retention must prioritize Scale accounts. | `F010` |
| **Q9** | *Where is the greatest revenue at risk?* | Three measures: (1) Realized churned MRR = **₹21.00M cumulative**; (2) Exposed active MRR in Medium/High tiers = **₹520K instrumented / ₹3.84M scaled**; (3) Expected MRR at risk = **₹411,712** [Wilson range: **₹391,612 – ₹432,158**]. | Aligning operational interventions with expected loss protects capital where exposure is highest. | `F011` |
| **Q10** | *What are the strongest observable leading indicators of churn?* | (1) 30-day inactivity ($RR=6.37\times$), (2) Non-adoption of collaboration tools ($RR=1.99\times$), (3) Open support ticket friction. | Composite additive scoring provides transparent operational triggers for Customer Success. | `F007`, `F008` |
| **Q11** | *Can we identify high-risk customer groups?* | Out-of-time validation across 2025 monthly snapshots confirms strict monotonicity: **Low: 12.41% $\rightarrow$ Medium: 22.28% $\rightarrow$ High: 68.46% $\rightarrow$ Critical: 100.0%**. | Monotonic risk tiers allow defensible routing for customer success queues. | `F012` |
| **Q12** | *What should the business do?* | Execute the **5-Play Churn Playbook**: Scale account concierge, collaboration onboarding loops, support de-escalation, annual billing incentives, and mobile onboarding optimization. | Actionable operational plays with clear hypotheses, owners, and A/B test designs. | `Playbook` |

---

## 3. Financial Impact & Revenue Analysis

### Active MRR Breakdown by Plan Tier (as of 2025-12-31)
```
+---------------+----------------+---------------+--------------------+----------------+
| Plan Tier     | Monthly Price  | Active Users  | Active MRR (INR)   | Share of MRR   |
+---------------+----------------+---------------+--------------------+----------------+
| Scale         | INR 3,999      | 1,735         | INR 6,553,481.22   | 41.2%          |
| Growth        | INR 1,499      | 4,239         | INR 5,999,537.64   | 37.7%          |
| Starter       | INR 499        | 7,046         | INR 3,350,959.65   | 21.1%          |
+---------------+----------------+---------------+--------------------+----------------+
| Total         |                | 13,020        | INR 15,903,978.51  | 100.0%         |
+---------------+----------------+---------------+--------------------+----------------+
```

### Three Measures of Revenue at Risk
1. **Realized Churned MRR:** **₹21,003,006.85** cumulative revenue permanently lost across 2024–2025 (peaked at ₹2,291,426 in Oct 2025; ₹1,089,780 in Dec 2025).
2. **Exposed MRR:** Active MRR of accounts currently classified in elevated risk tiers (Medium, High, or Critical): **₹520,212.02** in the instrumented cohort (~**₹3,840,000** scaled across total active base).
3. **Expected MRR at Risk (60-day Estimate):** Statistical expected loss computed as tier MRR multiplied by observed out-of-time tier churn rates: **₹411,711.58** [95% Wilson range: **₹391,611.97 – ₹432,157.75**].

---

## 4. Methodological Defense & Statistical Rigor

1. **Person-Time Hazard Rates over Lifetime Averages:**
   Lifetime churn rates confuse duration with risk. Evaluating events per customer-month at risk proves that underlying hazard is identical across plan tiers (~7.4% per customer-month) and drops 20x from Month 0–3 to Month 13+.
2. **Multi-Snapshot Out-of-Time Validation (DEC-016):**
   Evaluating 34,450 observations across 22 monthly snapshots prevents single-date sampling bias. Thresholds selected on 2024 discovery snapshots were strictly validated on 2025 holdout snapshots.
3. **Statistical Sample Size Floor ($n \ge 200, \text{events} \ge 30$):**
   Small cohorts (such as the 95 inactive accounts or 130 High-risk accounts) are transparently labeled as having sample sizes below the certainty floor, avoiding false precision while reporting strong directional indicators.
4. **Simpson's Paradox & Confounder Control:**
   Controlling for plan tier revealed that App Store accounts have identical hazard per customer-month to other channels, debunking the surface hypothesis that App Store traffic was defective.
