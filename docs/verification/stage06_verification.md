# Stage 6 Verification Report

**Stage:** 6 (Feature Usage, Stickiness & Leading Indicators — Q5, Q6 & Q10)  
**Date:** 2026-10-04 (Updated 2026-10-11 per DEC-016)  
**Status:** ✅ Passed

## 1. What Was Executed
1. Expanded single-date snapshot evaluation to **22 monthly rolling snapshots** (`2024-01-31` to `2025-10-31`), producing 34,450 observation records.
2. Formulated feature thresholds on earlier discovery snapshots (2024, 12,645 records) and strictly validated out-of-time on later holdout snapshots (2025, 21,805 records).
3. Applied the statistical sample size floor ($n \ge 200$, events $\ge 30$).
4. Evaluated Relative Risk (RR), capture share, and Wilson 95% confidence intervals.
5. Automated test suite verified zero temporal leakage across all feature columns.

---

## 2. Cohort Definition & Instrumentation Clarification
- **Why only 2,249 of 13,020 active accounts were in the single 2025-11-01 snapshot:**
  1. *Usage Sampling:* In `generator.py`, detailed daily usage logs were generated for a 5,000-customer sample to keep file sizes within the 25 MB limit. 25,000 accounts did not have daily instrumentation.
  2. *Prior Churn Exclusion:* Of the 5,000 instrumented customers, 2,318 churned prior to `2025-11-01` and were strictly excluded to eliminate retrospective survival bias.
  3. *Result:* Exactly 2,249 instrumented accounts were active on `2025-11-01`.
  4. *DEC-016 Enhancement:* Monthly rolling snapshots across 22 months expanded the evaluated pool to **34,450 observations**, resolving single-snapshot sparsity.

---

## 3. Empirical Outputs: Out-of-Time Monthly Validation (2025 Holdout)

### Table 1: Inactivity Signal (F007)
| Inactivity Group | Evaluated ($n$) | Churned (60d) | Churn % | Relative Risk | Capture Share | Sample Floor Valid? |
|---|---|---|---|---|---|---|
| **Inactive (0 sessions in 30d)** | 95 | 85 | **89.47%** | **6.37x** | 2.71% | **False** ($n=95 < 200$) |
| **Active (1+ sessions in 30d)** | 21,710 | 3,050 | **14.05%** | *Baseline* | 97.29% | **True** |

*Takeaway:* Inactivity is the strongest predictive leading indicator ($RR=6.37\times$), but due to $n=95$, it is transparently categorized as strong directional evidence below the 200-account certainty floor.

---

### Table 2: Collaboration Adoption Signal (F008)
| Feature Group | Evaluated ($n$) | Churned (60d) | Churn % | Relative Risk | Capture Share | Sample Floor Valid? |
|---|---|---|---|---|---|---|
| **No Collaboration Use** | 3,563 | 879 | **24.67%** | **1.99x** | 28.04% | **True** ($n=3,563 \ge 200$) |
| **Uses Collaboration** | 18,242 | 2,256 | **12.37%** | *Baseline* | 71.96% | **True** |

*Takeaway:* Accounts adopting team collaboration features exhibit half the prospective churn hazard (**12.37% vs 24.67%**, $RR=1.99\times$). Fully clears sample size floor.

---

## 4. Automated Leakage Prevention Status
- `test_no_feature_timestamp_after_reference_date`: **PASSED** (all timestamps $< \text{OBSERVATION\_DATE}$).
- `test_no_post_churn_fields_in_indicator_table`: **PASSED** (zero forbidden post-churn columns in `customer_behavioral_snapshot`).
