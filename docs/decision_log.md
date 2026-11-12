# Decision Log

This document records every significant design and architectural decision made during the project. Each entry states **what was decided, what alternatives were considered, and why this choice was made.** Any change to a previously-logged decision is recorded as a new entry referencing the original.

Decisions that affect metric definitions are also reflected in `docs/metric_definitions.md`.

---

## Entry Format

**DEC-NNN** | Stage N | YYYY-MM-DD  
**Decision:** [what was decided]  
**Alternatives considered:** [what else was on the table]  
**Rationale:** [why this choice]  
**Impact:** [which files / stages are affected]

---

## DEC-001 | Stage 0 | 2026-09-28

**Decision:** Use a fully synthetic dataset rather than any real public dataset.  
**Alternatives considered:** Telco churn (IBM), bank churn (Kaggle), e-commerce datasets. See `docs/dataset_decision.md` for full scoring.  
**Rationale:** No public dataset meets the minimum requirements: customer-level churn label + dated activity/transactions + revenue + acquisition channel dimension + a time dimension sufficient for trend, cohort, and leading-indicator analysis. The most famous datasets (Telco, bank churn) are cross-sectional snapshots — they have no time dimension, so Q2 (trend), Q4 (cohort/tenure), Q6 (leading indicators), and Q10 (temporal feature windows) cannot be answered. Synthetic data allows full control of realism, planted effects, injected quality issues, and confounders — making this a richer methodological demonstration.  
**Impact:** `synthetic_data/`, `_ground_truth/`, all stages.

---

## DEC-002 | Stage 0 | 2026-09-28

**Decision:** Fictional company name is **Zorvio**. Product: SaaS productivity and collaboration for individuals and SMBs in India.  
**Alternatives considered:** Generic "TechCo", industry-specific names. Zorvio is neutral, memorable, and clearly fictional.  
**Rationale:** A named company makes the business narrative credible and the portfolio piece more engaging. "Zorvio" has no Google results, avoiding confusion with a real entity.  
**Impact:** README, all documentation, generator, data dictionary.

---

## DEC-003 | Stage 0 | 2026-09-28

**Decision:** Three pricing plans: **Starter ₹499/mo**, **Growth ₹1,499/mo**, **Scale ₹3,999/mo**. Annual billing at approximately 10-month equivalent (≈17% discount).  
**Alternatives considered:** Two-plan (free vs paid), four-plan (freemium + three tiers). Three plans are the industry norm for Indian B2B SaaS and give enough segment variation without over-complicating the analysis.  
**Rationale:** Three plans create clear MRR tiers for revenue analysis, distinct churn behaviour to detect, and a realistic up/downgrade history to track.  
**Impact:** Generator (`subscriptions` table), metric definitions (MRR, ARPU, value tiers).

---

## DEC-004 | Stage 0 | 2026-09-28

**Decision:** Acquisition channels: **Organic Search, Paid Social, Referral, App Store, Campus/Partnership**.  
**Alternatives considered:** Fewer channels (e.g., just three); adding email marketing as separate channel.  
**Rationale:** Five channels is realistic for an Indian SaaS startup and gives enough variation to answer Q7 while keeping segment sizes large enough for statistical reliability. Email is treated as a re-engagement tactic, not an acquisition channel.  
**Impact:** Generator (`customers` table), SQL segmentation queries, findings register.

---

## DEC-005 | Stage 0 | 2026-09-28

**Decision:** Include an optional **`marketing_spend`** table (channel × month × spend in INR), enabling CAC context for Q7.  
**Alternatives considered:** Omit (simpler); include as part of `customers` table.  
**Rationale:** User confirmed they want it. CAC context enriches Q7 (channel quality) — a channel that looks high-churn may still be positive-ROI if its CAC is very low. Clearly labelled synthetic in the data dictionary.  
**Impact:** Generator (additional table), SQL script 06, notebook 03.

---

## DEC-006 | Stage 0 | 2026-09-28

**Decision:** Target dataset size: approximately **30,000 customers**, ~24 months of history (January 2024 – December 2025). As-of date: **2025-12-31**.  
**Alternatives considered:** 25,000 (lower bound) or 40,000 (upper bound). 30,000 hits the middle of the specified range, keeps all segment sizes above the planned statistical floor (n ≥ 200), and keeps CSV files well under 25 MB.  
**Rationale:** Stable segment sizes are essential for the Wilson CI analysis. At 30,000 customers with ~8% monthly churn, even a small segment (e.g., one city in one plan tier) typically clears 200 customers and 30 churn events.  
**Impact:** Generator config, all analyses that reference segment sizes.

---

## DEC-007 | Stage 0 | 2026-09-28

**Decision:** Database engine: **SQLite** (via Python stdlib `sqlite3` and `sqlite-utils` for CLI).  
**Alternatives considered:** PostgreSQL (more production-realistic but requires a running server), DuckDB (excellent for analytics but less widely known by hiring managers). SQLite is zero-setup, file-based, fully reproducible from a clone, and supports CTEs and window functions (needed from Stage 3 onward).  
**Rationale:** The brief mandates SQLite. Dialect differences vs PostgreSQL/MySQL are documented in `docs/sql_dialect_notes.md`.  
**Impact:** All SQL scripts, `src/db_loader.py`.

---

## DEC-008 | Stage 0 | 2026-09-28

**Decision:** Machine learning extension (logistic regression) is **deferred** — decision will be made at Stage 5 based on project progress.  
**Alternatives considered:** Include now; exclude entirely.  
**Rationale:** User preference. Including it now risks scope creep before the core analysis is solid. At Stage 5 we will assess whether it adds genuine portfolio value.  
**Impact:** Stage 5 design.

---

## DEC-009 | Stage 0 | 2026-09-28

**Decision:** Git initialised locally. GitHub remote URL will be added after Stage 0 setup is approved.  
**Alternatives considered:** GitHub-first (create remote first). Local-first is simpler for a student starting fresh.  
**Impact:** Version control workflow.

---

## DEC-010 | Stage 0 | 2026-09-28

**Decision:** Random seed for all synthetic data generation: **42** (default; overridable via `--seed` flag in `run_pipeline.py`).  
**Alternatives considered:** Any other fixed integer. 42 is conventional and universally understood.  
**Rationale:** Determinism is mandatory for reproducibility. The same seed always produces the same data, which means the same test results, the same figures, and the same findings register entries.  
**Impact:** Generator, all downstream artefacts.

---

*Future entries will be added here as decisions are made in subsequent stages.*

## DEC-011 | Stage 2 | 2026-09-28

**Decision:** Drop duplicate customer rows based on keeping the first chronological signup.  
**Alternatives considered:** Keep all (corrupts analysis), average them.  
**Rationale:** Synthetic generation injected exact dupes; keeping one preserves the true customer count.  
**Impact:** `clean_customers`

---

## DEC-012 | Stage 2 | 2026-09-28

**Decision:** Nullify subscription `end_date` if it falls before `start_date`.  
**Alternatives considered:** Drop the row entirely, swap the dates.  
**Rationale:** We assume the start_date is correct and the end_date was a logging error. Nullifying it treats the subscription as active, preserving MRR.  
**Impact:** `clean_subscriptions`

---

## DEC-013 | Stage 2 | 2026-09-28

**Decision:** Drop orphan payments (no matching customer_id).  
**Alternatives considered:** Keep them, impute a dummy customer.  
**Rationale:** Payments unlinked to a customer cannot be used for cohort or churn analysis. They are dropped.  
**Impact:** `clean_payments`

---

## DEC-014 | Stage 2 | 2026-09-28

**Decision:** Impute missing acquisition channels as 'Unknown'.  
**Alternatives considered:** Drop the rows, impute with mode (Organic Search).  
**Rationale:** Missing channel is a valid business state (e.g. cookie blockers). Imputing 'Unknown' preserves the customer for overall churn metrics while accurately reflecting tracking gaps in channel analysis.  
**Impact:** `clean_customers`

---

## DEC-015 | Stage 6 | 2026-10-04

**Decision:** Refactor behavioral feature engineering from churn-anchored window (v1) to fixed observation window (v2).  
**Alternatives considered:** Retain v1 (anchored on each customer's own cancellation date); variable rolling window without fixed prospective horizon.  
**Rationale:** v1 had temporal leakage because the 30-day feature window was anchored on each customer's own `end_date` for churned customers (vs `2025-12-31` for active customers). Inactivity, support complaints, and low collaboration immediately prior to cancellation were consequences of churn rather than early predictive signals, resulting in artificially inflated separation (Critical 100%, High 99.54%). v2 fixes ONE single observation date (`2025-11-01`, exactly 60 days before dataset cutoff `2025-12-31`), computes all features strictly within the 30-day lookback prior to `2025-11-01`, prospectively labels churn based on cancellations occurring within the 60 days post-observation date, and strictly excludes customers already churned before `2025-11-01` or lacking usage tracking.  
**Impact:** `sql/07_feature_usage.sql`, `sql/09_high_value_churn.sql`, `outputs/findings_register.csv`, `tests/test_leakage_and_reconciliation.py`, and all downstream documentation.

---

## DEC-016 | Stage 6/7 | 2026-10-11

**Decision:** Expand single-snapshot evaluation to monthly rolling snapshots across all eligible month-ends (`2024-01-31` to `2025-10-31`), splitting into earlier discovery (`2024`) and out-of-time validation (`2025`), and enforce a statistical sample size floor ($n \ge 200$, events $\ge 30$).  
**Alternatives considered:** Maintain single snapshot `2025-11-01` (limited sample size, unpopulated Critical tier); cross-validation with shuffled folds (violates temporal sequence and causes lookahead leakage).  
**Rationale:** A single snapshot only evaluated 2,249 account observations and left the Critical tier with zero samples. Monthly rolling snapshots across 22 eligible month-ends yield 34,450 customer-month observation records (12,645 in 2024 discovery; 21,805 in 2025 validation). Feature thresholds (30d inactivity, open support tickets, collaboration adoption) selected on 2024 snapshots are strictly validated on 2025 holdout snapshots. Any tier or subgroup with $n < 200$ or $< 30$ events (e.g. Critical tier $n=1$, High tier $n=130$) is explicitly flagged as "insufficient sample size for standalone certainty" rather than presented as a standalone statistical certainty.  
**Impact:** `scratch_monthly_snapshots.py`, `outputs/findings_register.csv`, `docs/business_report.md`, verification reports, and playbook.

