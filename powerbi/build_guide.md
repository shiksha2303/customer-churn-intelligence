# Power BI Build Guide: Zorvio Churn Intelligence Dashboard

> **SYNTHETIC DATA NOTICE:** All data is computer-generated for fictional SaaS company Zorvio.

This guide provides end-to-end instructions for creating the Zorvio Churn Intelligence 5-page dashboard in **Power BI Desktop**.

---

## Prerequisites
1. Power BI Desktop installed (August 2023 version or later recommended).
2. Run the pipeline to populate export CSVs:
   ```bash
   python run_pipeline.py
   ```
   Confirm files are present in `data/exports/`.

---

## Step 1: Ingest Data
1. Launch Power BI Desktop.
2. Select **Get Data** -> **Folder** (or **Text/CSV**) pointing to `data/exports/`.
3. Load the following files:
   - `dim_customer.csv`
   - `dim_plan.csv`
   - `dim_date.csv`
   - `fact_subscriptions.csv`
   - `fact_monthly_churn.csv`
   - `fact_cohort_retention.csv`
   - `fact_customer_risk.csv`
   - `fact_high_risk_active.csv`
   - `fact_mrr_by_plan.csv`

---

## Step 2: Configure Relationships (Model View)
Navigate to the **Model** view and configure the Star Schema:
1. `dim_customer[customer_id]` -> `fact_subscriptions[customer_id]` (1 to Many, Single)
2. `dim_plan[plan_name]` -> `fact_subscriptions[plan]` (1 to Many, Single)
3. `dim_date[full_date]` -> `fact_subscriptions[start_date]` (1 to Many, Single)
4. `dim_date[full_date]` -> `fact_subscriptions[end_date]` (1 to Many, Single, Inactive)
5. `dim_customer[customer_id]` -> `fact_customer_risk[customer_id]` (1 to 1, Both)
6. `dim_customer[customer_id]` -> `fact_high_risk_active[customer_id]` (1 to 1, Both)

---

## Step 3: Apply Custom Theme
1. In the top ribbon, select **View** -> **Themes dropdown** -> **Browse for themes**.
2. Select `powerbi/theme.json`.
3. The report canvas will instantly adopt Zorvio's corporate SaaS palette (Indigo, Cyan, Emerald, Amber, Slate).

---

## Step 4: Create Measures Table
1. Click **Enter Data** in the Home ribbon. Name the table `_Measures`.
2. Right-click `_Measures` -> **New Measure** and add DAX measures from `powerbi/dax_measures.md`:
   - `Total Customers`, `Active Customers`, `Churned Customers`, `Overall Churn Rate %`
   - `Monthly Total Churn Rate %`, `Monthly Voluntary Churn Rate %`
   - `Active MRR`, `Active ARR`, `Realized Churn MRR`, `Projected Monthly MRR at Risk`
   - `Inactivity Churn Rate %`, `Collaboration Users Churn Rate %`

---

## Step 5: Build Report Pages

### Page 1: Executive KPI & Churn Overview
- **Top Cards:** `Active MRR`, `Active Customers`, `Monthly Total Churn Rate %`, `Projected Monthly MRR at Risk`.
- **Primary Visual:** Line and Clustered Column Chart:
  - Shared Axis: `dim_date[year_month]`
  - Column Values: `[Monthly Voluntary Churns]`, `[Monthly Involuntary Churns]`
  - Line Values: `[Monthly Total Churn Rate %]`
- **Callout Box:** Annotate September 2025 Outage spike where voluntary churn peaked at 10.81%.

### Page 2: Customer Segmentation & Cohort Retention
- **Bar Chart:** `[Overall Churn Rate %]` by `dim_customer[current_plan]`.
- **Donut Chart:** `[Total Customers]` and `[Overall Churn Rate %]` by `dim_customer[billing_cycle]`.
- **Horizontal Bar:** `[Overall Churn Rate %]` by `dim_customer[acquisition_channel]`.
- **Matrix Visual:** Cohort Retention Heatmap:
  - Rows: `fact_cohort_retention[cohort_month]`
  - Values: `retention_pct_m1`, `retention_pct_m2`, `retention_pct_m3`, `retention_pct_m6`, `retention_pct_m12`
  - Conditional Formatting: Background color gradient (Green -> Amber -> Coral).

### Page 3: Behavioral Drivers & Leading Indicators
- **Clustered Column:** Churn Rate by Inactivity (Active 48.4% vs Inactive 100.0%).
- **Clustered Column:** Churn Rate by Collaboration Feature Use (Users 11.1% vs Non-Users 87.6%).
- **Support Friction Visual:** Churn Rate by Open Support Tickets (0, 1, 2+ open tickets).

### Page 4: Revenue at Risk & Financial Exposure
- **Treemap / Bar Chart:** `[Active MRR]` by `dim_plan[plan_name]`. Shows Scale plan concentration (₹6.55M).
- **KPI Tiles:** `[Realized Churn MRR]` vs `[Projected Monthly MRR at Risk]`.
- **Table:** MRR at Risk segmented by `dim_customer[company_size_band]` and `dim_customer[city_tier]`.

### Page 5: Churn Action Center & CS Triage Queue
- **Risk Funnel Visual:** Validation of Risk Tiers showing strictly monotone churn rates:
  - Critical (100.0%) -> High (99.5%) -> Medium (84.7%) -> Low (11.4%).
- **Priority Customer Table:** Top high-risk active accounts from `fact_high_risk_active`:
  - Columns: `customer_id`, `plan`, `billing_cycle`, `mrr`, `sessions_30d`, `open_tickets_30d`, `recommended_play`.
- **Export Button:** Standard Power BI CSV export enabled for Customer Success team handoff.
