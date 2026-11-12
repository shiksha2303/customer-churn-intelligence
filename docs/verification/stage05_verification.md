# Stage 5 Verification Report

**Stage:** 5 (Customer Segmentation & Acquisition Channel Analysis — Q3 & Q7)  
**Date:** 2026-10-02 (Updated 2026-10-11)  
**Status:** ✅ Passed

## 1. What Was Executed
1. Computed person-time hazard rates (churn events per customer-month at risk) across plans, billing frequencies, tenure buckets, and acquisition channels.
2. Evaluated billing frequency comparison (Monthly vs. Annual) at equal tenure bands to control for customer maturation.
3. Stratified acquisition channel performance across plan tiers to test for Simpson's Paradox and confounders.
4. Extracted findings F005, F006, and F009 to `outputs/findings_register.csv`.

---

## 2. Actual Empirical Outputs: Person-Time Hazard & Segmentation

### Table 1: Churn Hazard per Customer-Month by Plan Tier (F005)
| Plan | Total Accounts | Churn Events | Customer-Months at Risk | Churn / Cust-Month % | Lifetime Ever-Churned % |
|---|---|---|---|---|---|
| **Growth** | 9,719 | 5,480 | 73,954 | **7.41%** | 56.38% |
| **Scale** | 4,008 | 2,273 | 30,758 | **7.39%** | 56.71% |
| **Starter** | 16,273 | 9,227 | 125,537 | **7.35%** | 56.70% |

*Key Finding (F005):* When accounting for exposure time, churn hazard is virtually identical across plan tiers (~7.4% per customer-month).

---

### Table 2: Monthly vs. Annual Billing at Equal Tenure Bands (F006)
| Tenure Band | Billing Cycle | Total Accounts | Churn Events | Cust-Months at Risk | Churn / Cust-Month % |
|---|---|---|---|---|---|
| **0–3 Months** | **Annual** | 1,963 | 1,326 | 2,945 | **45.02%** |
| | **Monthly** | 6,473 | 4,506 | 9,571 | **47.08%** |
| **4–6 Months** | **Annual** | 1,593 | 938 | 7,663 | **12.24%** |
| | **Monthly** | 4,775 | 3,346 | 22,933 | **14.59%** |
| **7–12 Months** | **Annual** | 2,095 | 967 | 19,654 | **4.92%** |
| | **Monthly** | 6,037 | 3,668 | 56,868 | **6.45%** |
| **13+ Months** | **Annual** | 2,060 | 577 | 29,890 | **1.93%** |
| | **Monthly** | 5,004 | 1,652 | 72,776 | **2.27%** |
| **Overall** | **Annual** | 7,711 | 3,808 | 62,732 | **6.07%** |
| | **Monthly** | 22,289 | 13,172 | 167,516 | **7.86%** |

*Key Finding (F006):* Annual billing is associated with lower churn hazard per customer-month across every tenure band. Early-tenure hazard is ~46% per customer-month, falling to ~2% after Month 13.

---

### Table 3: Acquisition Channel Stratification by Plan Tier (F009)
| Channel | Plan Tier | Accounts | Churn Events | Cust-Months | Churn / Cust-Month % |
|---|---|---|---|---|---|
| **App Store** | Starter | 3,540 | 2,058 | 26,589 | **7.74%** |
| | Growth | 659 | 382 | 4,687 | **8.15%** |
| | Scale | 213 | 157 | 2,003 | **7.84%** |
| **Organic Search** | Starter | 5,796 | 3,246 | 44,959 | **7.22%** |
| | Growth | 4,247 | 2,382 | 32,900 | **7.24%** |
| | Scale | 1,742 | 982 | 12,972 | **7.57%** |
| **Paid Social** | Starter | 3,702 | 2,074 | 29,211 | **7.10%** |
| | Growth | 2,550 | 1,466 | 18,892 | **7.76%** |
| | Scale | 1,083 | 593 | 8,520 | **6.96%** |
| **Referral** | Starter | 2,223 | 1,281 | 17,194 | **7.45%** |
| | Growth | 1,547 | 871 | 12,302 | **7.08%** |
| | Scale | 674 | 345 | 4,612 | **7.48%** |

*Key Finding (F009):* Within each plan tier, churn hazard across channels is uniform (7.0%–8.1% per customer-month). App Store's raw lifetime churn elevation is driven by 82.1% Starter plan concentration.
