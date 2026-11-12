# Stage 7 Verification Report

**Stage:** 7 (Revenue at Risk & Risk Scoring Framework — Q8, Q9 & Q11)  
**Date:** 2026-10-06 (Updated 2026-10-11 per DEC-016)  
**Status:** ✅ Passed

## 1. What Was Executed
1. Quantified active MRR concentration across plans and customer segments.
2. Replaced the flawed 56.6% single-window projection with **Three Distinct Measures of Revenue at Risk**: Realized, Exposed, and Expected.
3. Evaluated the transparent rule-based risk framework out-of-time across 2025 monthly snapshots, verifying strict monotonicity and reporting Wilson 95% confidence intervals and capture shares.
4. Validated exact SQL vs. independent pandas reconciliation for headline monthly churn and MRR.

---

## 2. Actual Empirical Outputs: Three Revenue-at-Risk Measures (F011)

### Measure 1: Realized Churned MRR (Historical / Observed)
- **Cumulative Total Lost:** **₹21,003,006.85** across 2024–2025.
- **Outage Peak (Oct 2025):** **₹2,291,426.33** lost in a single month (Scale: ₹921,929; Growth: ₹849,993; Starter: ₹519,504).
- **Latest Month (Dec 2025):** **₹1,089,780.22** lost (Scale: ₹471,322; Growth: ₹394,552; Starter: ₹223,906).

---

### Measure 2: Exposed Active MRR (Current High/Medium Risk Portfolio)
- **Active MRR in Medium/High Tiers (Instrumented Cohort):** **₹520,212.02**.
- **Scaled Total Active Base Exposure:** ~**₹3,840,000.00** across the company.

---

### Measure 3: Expected MRR at Risk (60-Day Prospective Window Estimate)
Calculated as: $\sum \text{Tier Active MRR} \times \text{Observed Out-of-Time Churn Rate for Tier}$:
| Risk Tier | Accounts | Active MRR (INR) | Out-of-Time Churn Rate | Expected MRR at Risk | 95% Wilson CI Range |
|---|---|---|---|---|---|
| **High** | 17 | ₹37,029.63 | 68.46% | ₹25,350.48 | [₹22,232.12, ₹28,075.27] |
| **Medium** | 394 | ₹483,182.39 | 22.28% | ₹107,653.04 | [₹101,226.87, ₹114,369.46] |
| **Low** | 1,839 | ₹2,245,836.43 | 12.41% | ₹278,708.06 | [₹268,152.98, ₹289,713.02] |
| **Total** | **2,250** | **₹2,766,048.45** | — | **₹411,711.58** | **[₹391,611.97, ₹432,157.75]** |

*Takeaway:* Expected MRR at risk is an explicit statistical estimate, not a lifetime projection.

---

## 3. Risk Framework Out-of-Time Validation (2025 Monthly Snapshots)

| Risk Tier | Score | Observations ($n$) | Churned (60d) | Churn % | 95% Wilson CI | Relative Risk | Capture Share | Sample Floor Valid? |
|---|---|---|---|---|---|---|---|---|
| **Critical** | 3 | 1 | 1 | **100.00%** | [20.65%, 100.0%] | 8.06x | 0.03% | **False** ($n=1$) |
| **High** | 2 | 130 | 89 | **68.46%** | [60.04%, 75.82%] | 5.52x | 2.84% | **False** ($n=130 < 200$) |
| **Medium** | 1 | 3,591 | 800 | **22.28%** | [20.95%, 23.67%] | 1.80x | 25.52% | **True** |
| **Low** | 0 | 18,083 | 2,245 | **12.41%** | [11.94%, 12.90%] | 1.00x | 71.61% | **True** |

*Monotonicity:* Strict monotonic ascent is confirmed ($12.41\% \rightarrow 22.28\% \rightarrow 68.46\% \rightarrow 100.0\%$). Tiers with $n < 200$ are clearly marked.

---

## 4. Automated Reconciliation Status
- `test_sql_vs_pandas_reconciliation_headline_churn_and_mrr`: **PASSED** (all 23 months independently match to 0.01%).
- `test_risk_monotonicity`: **PASSED**.
