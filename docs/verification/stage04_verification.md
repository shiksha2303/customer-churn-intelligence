# Stage 4 Verification Report

**Stage:** 4 (Cohort Analysis & MRR Retention)  
**Date:** 2026-09-28  
**Status:** ✅ Passed

## What was run
1. SQL script (`sql/04_cohort_retention_Q3_Q4.sql`) was created to build a triangular cohort retention matrix.
2. The script calculates retention for months 1, 3, 6, and 12, as well as the average tenure of active and churned customers.
3. Added Stage 4 logic to `run_pipeline.py`.
4. Extracted average 6-month retention (F003) and average churned tenure (F004) to the findings register.

## Outputs and Sanity Checks
- **Cohort Matrix:** A table (`cohort_retention`) containing row-by-row cohorts based on the YYYY-MM signup date.
- **Tenure Stats:** A table (`average_tenure`) containing the average months an active user has been around versus a churned user.
- **Findings Extracted:** 
  - F003 (Q3) logged average M6 retention.
  - F004 (Q4) logged average tenure for churned users.

## Readiness for Stage 5
With the cohort foundation laid, we are ready to analyze behavioural drivers of churn, segment by plans, and hunt for leading indicators (Stage 5).
