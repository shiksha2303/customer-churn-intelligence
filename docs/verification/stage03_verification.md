# Stage 3 Verification Report

**Stage:** 3 (Core Metrics: Defining "Churn")  
**Date:** 2026-09-28  
**Status:** ✅ Passed

## What was run
1. Core business metrics mathematically defined in `docs/metric_definitions.md`.
2. Developed SQL CTEs (`sql/03_historical_churn_Q1_Q2.sql`) to calculate active customers and churn rates on a monthly basis.
3. Created mathematical logic tests in `tests/test_sql_logic.py` to ensure same-month churners are excluded.
4. Integrated into `run_pipeline.py` to extract findings into `outputs/findings_register.csv`.

## Outputs and Sanity Checks
- **Math Logic Verified:** The `pytest` script confirmed that our SQL aggregation (which excludes same-month sign-up-and-cancels) correctly reconciles with the raw cancellation counts in the database.
- **Key Finding Extracted (F001):** The pipeline queried the final SQL output and successfully logged the baseline churn and the massive spike in late 2025 into the findings register. 

## Readiness for Stage 4
Our foundational metric definition is solid and proven. We are now ready to tackle Cohort Analysis and MRR/Retention Curves (Stage 4), using this base definition of churn.
