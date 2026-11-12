# Stage 8 Learning Concepts

## Concepts Used

1. **Dimensional Modeling (Kimball Star Schema) for BI:**
   - *What it is:* Organizing analytical data into fact tables (containing quantitative metrics and foreign keys) and dimension tables (containing descriptive attributes with primary keys).
   - *Why we chose it:* Many data analysts dump one flat, denormalized CSV file into Power BI. This causes massive memory bloat, slower DAX query execution, and confusing relationship models. By structuring the Power BI export into 3 dimensions (`dim_customer`, `dim_plan`, `dim_date`) and 5 focused fact tables (`fact_subscriptions`, `fact_monthly_churn`, `fact_cohort_retention`, `fact_customer_risk`, `fact_high_risk_active`), we conform to enterprise BI standards.
   - *Interview angle:* Demonstrating clean star schema modeling with 1-to-many single-direction relationships sets you apart from analysts who only know how to connect flat tables.

2. **DAX Measure Hygiene:**
   - *Explicit vs Implicit Measures:* Never use Power BI's automatic drag-and-drop summaries. Always define explicit DAX measures (`[Total Active MRR]`, `[Churn Rate %]`, `[Net Revenue Retention]`).
   - *Safe Division:* Always use `DIVIDE(numerator, denominator, 0)` rather than `/` to guard against division-by-zero exceptions.
   - *Filter Context Control:* Using `CALCULATE` and `ALL` / `KEEPFILTERS` cleanly controls calculation scope across dynamic report slicers.

3. **Hypothesis-Driven Action Playbooks (Q12):**
   - *What it is:* Bridging the gap between analytical findings and operational business action by constructing structured "plays" for functional teams (Customer Success, Product, Support, Marketing).
   - *Structure of a Play:* Each play defines the **Target Cohort**, **Trigger Signal**, **Strategic Hypothesis**, **Operational Action**, **Responsible Owner**, **Success KPI**, and **A/B Test Design**.
   - *Interview angle:* Executives don't pay data analysts to make pretty charts; they pay them to drive business outcomes. Delivering a concrete 5-play operational playbook proves business acumen.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Recommending generic advice like "improve product quality" or "offer discounts."
- **Why we avoided it:** Generic recommendations are ignored. Every play in our playbook addresses an empirically validated root cause (e.g., Play 1 targets Scale accounts entering inactivity; Play 3 targets Day 30–60 collaboration onboarding; Play 4 drives monthly-to-annual billing incentives).
