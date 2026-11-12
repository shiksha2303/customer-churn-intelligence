-- sql/05_segmentation.sql
-- Answers Q3: Which customer segments churn the most?
-- Segments: Plan, Billing Cycle, City Tier, Company Size, Acquisition Channel

-- ============================================================
-- TABLE 1: Churn by Plan
-- ============================================================
DROP TABLE IF EXISTS churn_by_plan;
CREATE TABLE churn_by_plan AS
WITH base AS (
    SELECT
        s.plan,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status = 'Canceled' THEN s.customer_id END) AS voluntary_churns,
        COUNT(DISTINCT CASE WHEN s.status = 'Past_Due'  THEN s.customer_id END) AS involuntary_churns,
        COUNT(DISTINCT CASE WHEN s.status != 'Active'   THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    GROUP BY s.plan
)
SELECT
    plan,
    total_customers,
    voluntary_churns,
    involuntary_churns,
    total_churns,
    ROUND(CAST(voluntary_churns   AS REAL) / total_customers * 100, 2) AS voluntary_churn_pct,
    ROUND(CAST(involuntary_churns AS REAL) / total_customers * 100, 2) AS involuntary_churn_pct,
    ROUND(CAST(total_churns       AS REAL) / total_customers * 100, 2) AS total_churn_pct,
    -- Wilson lower bound (95%) for total churn rate
    ROUND(
        (CAST(total_churns AS REAL)/total_customers
        - 1.96 * SQRT(CAST(total_churns AS REAL)/total_customers
                      * (1 - CAST(total_churns AS REAL)/total_customers) / total_customers))
        * 100, 2
    ) AS total_churn_pct_wilson_lower,
    ROUND(
        (CAST(total_churns AS REAL)/total_customers
        + 1.96 * SQRT(CAST(total_churns AS REAL)/total_customers
                      * (1 - CAST(total_churns AS REAL)/total_customers) / total_customers))
        * 100, 2
    ) AS total_churn_pct_wilson_upper
FROM base
ORDER BY total_churn_pct DESC;

-- ============================================================
-- TABLE 2: Churn by Billing Cycle
-- ============================================================
DROP TABLE IF EXISTS churn_by_billing_cycle;
CREATE TABLE churn_by_billing_cycle AS
WITH base AS (
    SELECT
        s.billing_cycle,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status = 'Canceled' THEN s.customer_id END) AS voluntary_churns,
        COUNT(DISTINCT CASE WHEN s.status = 'Past_Due'  THEN s.customer_id END) AS involuntary_churns,
        COUNT(DISTINCT CASE WHEN s.status != 'Active'   THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    GROUP BY s.billing_cycle
)
SELECT
    billing_cycle,
    total_customers,
    voluntary_churns,
    involuntary_churns,
    total_churns,
    ROUND(CAST(voluntary_churns   AS REAL) / total_customers * 100, 2) AS voluntary_churn_pct,
    ROUND(CAST(involuntary_churns AS REAL) / total_customers * 100, 2) AS involuntary_churn_pct,
    ROUND(CAST(total_churns       AS REAL) / total_customers * 100, 2) AS total_churn_pct
FROM base
ORDER BY total_churn_pct DESC;

-- ============================================================
-- TABLE 3: Churn by City Tier
-- ============================================================
DROP TABLE IF EXISTS churn_by_city_tier;
CREATE TABLE churn_by_city_tier AS
WITH base AS (
    SELECT
        c.city_tier,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status = 'Canceled' THEN s.customer_id END) AS voluntary_churns,
        COUNT(DISTINCT CASE WHEN s.status = 'Past_Due'  THEN s.customer_id END) AS involuntary_churns,
        COUNT(DISTINCT CASE WHEN s.status != 'Active'   THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
    GROUP BY c.city_tier
)
SELECT
    city_tier,
    total_customers,
    voluntary_churns,
    involuntary_churns,
    total_churns,
    ROUND(CAST(voluntary_churns   AS REAL) / total_customers * 100, 2) AS voluntary_churn_pct,
    ROUND(CAST(involuntary_churns AS REAL) / total_customers * 100, 2) AS involuntary_churn_pct,
    ROUND(CAST(total_churns       AS REAL) / total_customers * 100, 2) AS total_churn_pct
FROM base
ORDER BY total_churn_pct DESC;

-- ============================================================
-- TABLE 4: Churn by Company Size Band
-- ============================================================
DROP TABLE IF EXISTS churn_by_company_size;
CREATE TABLE churn_by_company_size AS
WITH base AS (
    SELECT
        c.company_size_band,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status = 'Canceled' THEN s.customer_id END) AS voluntary_churns,
        COUNT(DISTINCT CASE WHEN s.status = 'Past_Due'  THEN s.customer_id END) AS involuntary_churns,
        COUNT(DISTINCT CASE WHEN s.status != 'Active'   THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
    GROUP BY c.company_size_band
)
SELECT
    company_size_band,
    total_customers,
    voluntary_churns,
    involuntary_churns,
    total_churns,
    ROUND(CAST(voluntary_churns   AS REAL) / total_customers * 100, 2) AS voluntary_churn_pct,
    ROUND(CAST(involuntary_churns AS REAL) / total_customers * 100, 2) AS involuntary_churn_pct,
    ROUND(CAST(total_churns       AS REAL) / total_customers * 100, 2) AS total_churn_pct
FROM base
ORDER BY total_churn_pct DESC;

-- ============================================================
-- TABLE 5: Plan x Billing Cycle cross-tab (confounding check)
-- ============================================================
DROP TABLE IF EXISTS churn_plan_x_billing;
CREATE TABLE churn_plan_x_billing AS
WITH base AS (
    SELECT
        s.plan,
        s.billing_cycle,
        COUNT(DISTINCT s.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN s.status != 'Active' THEN s.customer_id END) AS total_churns
    FROM clean_subscriptions s
    GROUP BY s.plan, s.billing_cycle
)
SELECT
    plan,
    billing_cycle,
    total_customers,
    total_churns,
    ROUND(CAST(total_churns AS REAL) / total_customers * 100, 2) AS total_churn_pct
FROM base
WHERE total_customers >= 30
ORDER BY plan, billing_cycle;
