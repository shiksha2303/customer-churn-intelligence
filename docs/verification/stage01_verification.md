# Stage 1 Verification Report

**Stage:** 1 (Data Creation)  
**Date:** 2026-09-28  
**Status:** ✅ Passed

## What was run
1. Created ground truth spec (`_ground_truth/GENERATOR_SPEC.md`) and injected issues list (`_ground_truth/injected_issues.json`).
2. Developed deterministic Python script (`synthetic_data/generator.py`) to generate ~30,000 customers.
3. Hooked generator into `run_pipeline.py`.
4. Wrote Data Dictionary (`docs/data_dictionary.md`).
5. Executed `python run_pipeline.py --stage 1`.

## Outputs and Sanity Checks
- **Data Generation:** Successfully generated 6 tables representing 30,000 customers, their subscriptions, payments, support tickets, and monthly marketing spend.
- **Reproducibility:** A fixed random seed (42) ensures the data will be identical on every run.
- **File Sizes:** All files successfully fall under the 25MB constraint:
  - `customers.csv`: 2.35 MB
  - `marketing_spend.csv`: < 0.01 MB
  - `payments.csv`: 18.09 MB
  - `subscriptions.csv`: 3.77 MB
  - `support_tickets.csv`: 1.91 MB
  - `usage_daily.csv`: 8.92 MB
- **Git Tracking:** The large generated files in `data/raw/` are excluded via `.gitignore`, but the `sample_*.csv` files (first 100 rows of each) are tracked, keeping the repo lightweight.

## Readiness for Stage 2
The raw synthetic dataset is now fully materialized. We are ready to load it into a SQLite database, perform the data quality audit, and build the cleaning pipeline (Stage 2).
