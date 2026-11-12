# Dataset Decision Memo

**Project:** Customer Churn Intelligence — Zorvio  
**Stage:** 0  
**Date:** 2026-09-28  
**Decision:** Use a fully **synthetic dataset** (see Recommendation section)

---

## 1. Requirements for This Project

To answer all 12 business questions — especially Q2 (trend), Q4 (cohort/tenure), Q6 (leading indicators from activity history), and Q10 (temporal feature windows) — the dataset must have:

| Requirement | Priority |
|---|---|
| R1 — Customer-level churn label (binary, with date) | **Must-have** |
| R2 — Time dimension: dated transactions or activity rows | **Must-have** |
| R3 — Revenue / subscription amount per customer | **Must-have** |
| R4 — Acquisition channel or source dimension | **Must-have** |
| R5 — At least one behavioral/usage dimension | **Must-have** |
| R6 — Geographic or segment dimension | **Nice-to-have** |
| R7 — Support interaction data | **Nice-to-have** |
| R8 — Voluntary vs involuntary churn distinction | **Must-have** |
| R9 — Free licence for portfolio use (public, no PII) | **Must-have** |

---

## 2. Real Dataset Candidates Evaluated

### Candidate A — IBM Telco Churn Dataset
- **Source:** Kaggle / IBM Watson Analytics sample  
- **Licence:** Publicly posted; no explicit open licence; widely used for portfolios  
- **Description:** ~7,000 rows, one row per customer, binary churn label, telecom plan features  
- **Scoring:**

| Requirement | Met? | Notes |
|---|---|---|
| R1 — Churn label | ✓ | Present |
| R2 — Time dimension | ✗ | **Cross-sectional snapshot; no dates** |
| R3 — Revenue | ✓ (partial) | Monthly charges and total charges present |
| R4 — Acquisition channel | ✗ | Not present |
| R5 — Behavioral/usage | ✓ (weak) | Service counts, not usage logs |
| R6 — Geography | ✗ | Not present |
| R7 — Support data | ✗ | Not present |
| R8 — Voluntary vs involuntary | ✗ | Single binary label |
| R9 — Licence | ✓ (de facto) | Widely used in portfolios |

- **Score: 3/8 must-haves.** Fails R2 (no time dimension), R4, and R8. Cannot support trend, cohort, leading-indicator, or channel analysis. **Rejected.**

---

### Candidate B — Kaggle Bank Customer Churn (various versions)
- **Source:** Multiple Kaggle datasets (BankChurners, etc.)  
- **Licence:** CC0 or unspecified  
- **Description:** 10,000–16,000 rows, binary churn, banking product features, demographics  
- **Scoring:**

| Requirement | Met? | Notes |
|---|---|---|
| R1 — Churn label | ✓ | Present |
| R2 — Time dimension | ✗ | **Cross-sectional; no transaction dates** |
| R3 — Revenue | ✓ (partial) | Credit limit / utilization; no MRR |
| R4 — Acquisition channel | ✗ | Not present |
| R5 — Behavioral/usage | ✓ (weak) | Transaction count; no usage log |
| R6 — Geography | ✗ | Country only (mostly USA) |
| R7 — Support data | ✗ | Not present |
| R8 — Voluntary vs involuntary | ✗ | Single label |
| R9 — Licence | ✓ | CC0 |

- **Score: 2/8 must-haves.** Fails R2, R4, R8. Also: banking, not SaaS; not India-relevant. **Rejected.**

---

### Candidate C — KKBOX Music Streaming Churn (KDD Cup 2015)
- **Source:** Kaggle / KDD Cup 2015  
- **Licence:** Competition dataset; Kaggle terms; portfolio use generally accepted  
- **Description:** Millions of rows, churn per 30-day window, listening logs, transaction history, member info  
- **Scoring:**

| Requirement | Met? | Notes |
|---|---|---|
| R1 — Churn label | ✓ | Window-based binary label |
| R2 — Time dimension | ✓ | Daily listening logs with dates |
| R3 — Revenue | ✓ (partial) | Subscription price present |
| R4 — Acquisition channel | ✗ | Not explicitly present |
| R5 — Behavioral/usage | ✓ | Rich listening log |
| R6 — Geography | ✗ | Taiwan-based; not India-relevant |
| R7 — Support data | ✗ | Not present |
| R8 — Voluntary vs involuntary | ✗ | Cannot separate cleanly |
| R9 — Licence | ✓ (de facto) | Kaggle competition |

- **Score: 4/8 must-haves.** Better than A and B (has time dimension and rich behavior), but: no acquisition channel, no voluntary/involuntary split, Taiwan streaming market (not relatable to target Indian SaaS audience), and files exceed 25 MB. Nearest match to requirements, but still fails R4 and R8 and is domain-irrelevant. **Rejected.**

---

### Candidate D — Recurly / ProfitWell / Baremetrics Open Datasets
- **Source:** Various SaaS analytics vendors have published aggregate benchmark reports  
- **Licence:** Aggregated benchmarks (not customer-level data) — **cannot be used as a dataset**  
- **Notes:** These are summary statistics (average churn rates by industry), not row-level data. **Not applicable.**

---

## 3. Verdict

**No public dataset meets the minimum requirements (R1 + R2 + R4 + R8) with a clearly acceptable licence.**

The core blocker is **R2 (time dimension)**: the most famous public churn datasets are all cross-sectional snapshots. Without dated activity or transactions, it is impossible to:
- Compute monthly churn trend (Q2)
- Build customer cohorts and retention curves (Q4)
- Construct snapshot-based leading indicators (Q6, Q10)
- Measure feature usage evolution (Q5)

Candidate C comes closest but is domain-irrelevant, missing acquisition channel, and oversized for this project's constraints.

---

## 4. Recommendation: Synthetic Dataset

**Build a deterministic synthetic dataset** representing ~24 months of the fictional Indian SaaS company **Zorvio**.

**Why synthetic is the right call for this project:**
1. We get exactly the structure we need: all eight requirements, all six tables, all 12 questions answerable.
2. We control realism: planted effects (moderate, not obvious), injected data-quality issues, confounders, red herrings, voluntary and involuntary churn as distinct mechanisms.
3. We can prove methodological rigor through **synthetic validation** (Stage 6): the analysis either recovers the planted effects or we honestly report what it missed.
4. The project demonstrates **analytical method**, not dataset selection. A portfolio project built on a public dataset that everyone uses is less differentiating.
5. Clearly labelled as synthetic throughout — no deception risk.

**Key generator design decisions** (documented in `_ground_truth/GENERATOR_SPEC.md`):
- Seeded (seed = 42) for full reproducibility
- ~30,000 customers, January 2024 – December 2025
- Six tables: `customers`, `subscriptions`, `payments`, `usage_daily`, `support_tickets`, `marketing_spend`
- Injected quality issues, confounders, and red herrings (see `_ground_truth/injected_issues.json`)
- ⚠️ **Do not open `_ground_truth/` until Stage 6**

---

**Decision logged in `docs/decision_log.md` as DEC-001.**  
**Approved by student: 2026-09-28**
