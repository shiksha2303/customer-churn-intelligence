-- sql/06_channel_and_tenure.sql
-- Answers Q7: Which acquisition channels produce higher-churn customers?
-- Answers Q4 (deeper): Are early-tenure customers more likely to churn?
-- Also computes CAC-context using marketing_spend for channel quality.

-- ============================================================
-- TABLE 1: Churn by Acquisition Channel
-- ============================================================
DROP TABLE IF EXISTS churn_by_channel;
CREATE TABLE churn_by_channel AS
WITH base AS (
    SELECT
        c.acquisition_channel,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status = 'Canceled' THEN s.customer_id END) AS voluntary_churns,
        COUNT(DISTINCT CASE WHEN s.status = 'Past_Due'  THEN s.customer_id END) AS involuntary_churns,
        COUNT(DISTINCT CASE WHEN s.status != 'Active'   THEN s.customer_id END) AS total_churns,
        ROUND(AVG(s.mrr), 2) AS avg_mrr
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
    GROUP BY c.acquisition_channel
)
SELECT
    acquisition_channel,
    total_customers,
    voluntary_churns,
    involuntary_churns,
    total_churns,
    avg_mrr,
    ROUND(CAST(voluntary_churns   AS REAL) / total_customers * 100, 2) AS voluntary_churn_pct,
    ROUND(CAST(involuntary_churns AS REAL) / total_customers * 100, 2) AS involuntary_churn_pct,
    ROUND(CAST(total_churns       AS REAL) / total_customers * 100, 2) AS total_churn_pct,
    -- Wilson 95% CI lower bound
    ROUND(
        (CAST(total_churns AS REAL)/total_customers
        - 1.96 * SQRT(CAST(total_churns AS REAL)/total_customers
                      * (1 - CAST(total_churns AS REAL)/total_customers) / total_customers))
        * 100, 2
    ) AS wilson_lower,
    ROUND(
        (CAST(total_churns AS REAL)/total_customers
        + 1.96 * SQRT(CAST(total_churns AS REAL)/total_customers
                      * (1 - CAST(total_churns AS REAL)/total_customers) / total_customers))
        * 100, 2
    ) AS wilson_upper
FROM base
WHERE total_customers >= 50
ORDER BY total_churn_pct DESC;

-- ============================================================
-- TABLE 2: Channel x Plan cross-tab (confounding check)
-- App Store is a known confounder — it pushes Starter plans
-- ============================================================
DROP TABLE IF EXISTS churn_channel_x_plan;
CREATE TABLE churn_channel_x_plan AS
WITH base AS (
    SELECT
        c.acquisition_channel,
        s.plan,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status != 'Active' THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
    GROUP BY c.acquisition_channel, s.plan
)
SELECT
    acquisition_channel,
    plan,
    total_customers,
    total_churns,
    ROUND(CAST(total_churns AS REAL) / total_customers * 100, 2) AS total_churn_pct
FROM base
WHERE total_customers >= 30
ORDER BY acquisition_channel, total_churn_pct DESC;

-- ============================================================
-- TABLE 3: CAC Context — average monthly marketing spend per channel
-- Joined with customer acquisition counts to estimate cost-per-customer
-- ============================================================
DROP TABLE IF EXISTS channel_cac_context;
CREATE TABLE channel_cac_context AS
WITH spend_agg AS (
    SELECT
        channel,
        SUM(spend_inr) AS total_spend_inr,
        COUNT(DISTINCT month) AS months_tracked,
        ROUND(AVG(spend_inr), 0) AS avg_monthly_spend_inr
    FROM clean_marketing_spend
    GROUP BY channel
),
acq_counts AS (
    SELECT
        acquisition_channel AS channel,
        COUNT(DISTINCT customer_id) AS customers_acquired
    FROM clean_customers
    WHERE acquisition_channel != 'Unknown'
    GROUP BY acquisition_channel
)
SELECT
    s.channel,
    s.total_spend_inr,
    s.avg_monthly_spend_inr,
    a.customers_acquired,
    ROUND(CAST(s.total_spend_inr AS REAL) / a.customers_acquired, 0) AS estimated_cac_inr
FROM spend_agg s
LEFT JOIN acq_counts a ON s.channel = a.channel
ORDER BY estimated_cac_inr;

-- ============================================================
-- TABLE 4: Tenure Buckets — early vs. established customers
-- Answers Q4 deeper: Is churn concentrated in early months?
-- ============================================================
DROP TABLE IF EXISTS churn_by_tenure_bucket;
CREATE TABLE churn_by_tenure_bucket AS
WITH tenure_calc AS (
    SELECT
        s.customer_id,
        s.status,
        CASE
            WHEN s.end_date IS NOT NULL
            THEN CAST((julianday(s.end_date) - julianday(c.signup_date)) / 30.44 AS INTEGER)
            ELSE CAST((julianday('2025-12-31') - julianday(c.signup_date)) / 30.44 AS INTEGER)
        END AS tenure_months
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
),
bucketed AS (
    SELECT
        customer_id,
        status,
        tenure_months,
        CASE
            WHEN tenure_months <= 1  THEN '0-1 months'
            WHEN tenure_months <= 3  THEN '2-3 months'
            WHEN tenure_months <= 6  THEN '4-6 months'
            WHEN tenure_months <= 12 THEN '7-12 months'
            ELSE '13+ months'
        END AS tenure_bucket,
        CASE
            WHEN tenure_months <= 1  THEN 1
            WHEN tenure_months <= 3  THEN 2
            WHEN tenure_months <= 6  THEN 3
            WHEN tenure_months <= 12 THEN 4
            ELSE 5
        END AS bucket_order
    FROM tenure_calc
)
SELECT
    tenure_bucket,
    bucket_order,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN status != 'Active' THEN 1 ELSE 0 END) AS churned,
    ROUND(CAST(SUM(CASE WHEN status != 'Active' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) AS churn_pct
FROM bucketed
GROUP BY tenure_bucket, bucket_order
ORDER BY bucket_order;
