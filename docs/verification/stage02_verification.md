# Stage 2 Verification Report

**Stage:** 2 (Database, Data Quality Audit, and Cleaning)  
**Date:** 2026-09-28  
**Status:** ✅ Passed

## What was run
1. Raw schema defined in `sql/00_schema.sql`.
2. Raw data ingested into `db/churn.db` via `src/db_loader.py`.
3. Data quality audited via SQL (`sql/01_data_quality_checks.sql`) and Pandas (`notebooks/01_data_understanding_and_quality.ipynb`).
4. Data cleaning pipeline executed via `sql/02_staging_and_cleaning.sql`.
5. Row conservation tests run via `tests/test_data_quality.py`.

## Outputs and Sanity Checks
- **Data Load:** All 6 raw CSV files successfully loaded into SQLite.
- **Audit Findings:** We successfully identified duplicates, missing channels, inconsistent city casing, backwards dates, negative session minutes, and orphan payments.
- **Cleaning Actions:** 
  - `clean_customers`: Deduplicated to exactly 30,000 customers. Channels imputed to 'Unknown'. Cities standardized.
  - `clean_subscriptions`: Logically impossible `end_date` values were nullified.
  - `clean_payments`: Orphan records dropped.
  - `clean_usage_daily`: Negative session minutes capped to 0.
- **Tests Passed:** The `pytest` suite confirmed that row counts follow exact conservation laws (e.g. `raw_customers` - `duplicates` = `clean_customers`).

## Readiness for Stage 3
The data is now clean, consistent, and staged in SQLite. We are ready to move into the core analytical phase, starting with the calculation of historical churn rates and the "As-Of" cohort analysis (Stage 3).
