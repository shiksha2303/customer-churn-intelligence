-- sql/08_revenue_and_risk.sql
-- Answers Q8: Which customer types generate the most revenue?
-- Answers Q9: Where is the greatest revenue at risk?
--
-- Three distinct revenue-at-risk measures (per project brief):
--   1. Realised churned revenue  — MRR already lost from churned customers
--   2. Exposed revenue at risk   — MRR of currently active high-risk customers
--   3. Estimated future risk     — projected monthly loss if churn rate holds

-- ============================================================
-- TABLE 1: MRR by Segment (Q8)
-- ============================================================
DROP TABLE IF EXISTS mrr_by_segment;
CREATE TABLE mrr_by_segment AS
SELECT
    s.plan,
    s.billing_cycle,
    c.company_size_band,
    c.acquisition_channel,
    c.city_tier,
    COUNT(DISTINCT s.customer_id) AS active_customers,
    ROUND(SUM(s.mrr), 2) AS total_mrr,
    ROUND(AVG(s.mrr), 2) AS avg_mrr_per_customer
FROM clean_subscriptions s
JOIN clean_customers c ON s.customer_id = c.customer_id
WHERE s.status = 'Active'
GROUP BY s.plan, s.billing_cycle, c.company_size_band, c.acquisition_channel, c.city_tier
ORDER BY total_mrr DESC;

-- ============================================================
-- TABLE 2: MRR Summary by Plan (simpler view for reporting)
-- ============================================================
DROP TABLE IF EXISTS mrr_by_plan;
CREATE TABLE mrr_by_plan AS
SELECT
    s.plan,
    COUNT(DISTINCT CASE WHEN s.status = 'Active' THEN s.customer_id END) AS active_customers,
    ROUND(SUM(CASE WHEN s.status = 'Active' THEN s.mrr ELSE 0 END), 2) AS active_mrr,
    ROUND(AVG(CASE WHEN s.status = 'Active' THEN s.mrr END), 2) AS avg_mrr,
    -- Realised churned MRR (measure 1)
    COUNT(DISTINCT CASE WHEN s.status != 'Active' THEN s.customer_id END) AS churned_customers,
    ROUND(SUM(CASE WHEN s.status != 'Active' THEN s.mrr ELSE 0 END), 2) AS realised_churned_mrr
FROM clean_subscriptions s
GROUP BY s.plan
ORDER BY active_mrr DESC;

-- ============================================================
-- TABLE 3: Revenue at Risk — Measure 1 (Realised)
-- MRR that is ALREADY LOST from churned customers
-- ============================================================
DROP TABLE IF EXISTS revenue_realised_churned;
CREATE TABLE revenue_realised_churned AS
SELECT
    strftime('%Y-%m', s.end_date) AS churn_month,
    s.plan,
    COUNT(*) AS churned_customers,
    ROUND(SUM(s.mrr), 2) AS mrr_lost,
    ROUND(SUM(s.mrr) * 12, 2) AS annualised_revenue_lost
FROM clean_subscriptions s
WHERE s.status != 'Active'
  AND s.end_date IS NOT NULL
GROUP BY churn_month, s.plan
ORDER BY churn_month, s.plan;

-- ============================================================
-- TABLE 4: Revenue at Risk — Measure 2 (Exposed)
-- MRR held by active customers who show high-risk signals.
-- High-risk = zero sessions in last 30 days OR open support tickets.
-- Joins with behavioral snapshot.
-- ============================================================
DROP TABLE IF EXISTS revenue_exposed_at_risk;
CREATE TABLE revenue_exposed_at_risk AS
SELECT
    bs.plan,
    bs.billing_cycle,
    COUNT(*) AS high_risk_customers,
    ROUND(SUM(bs.mrr), 2) AS exposed_mrr,
    ROUND(AVG(bs.mrr), 2) AS avg_mrr_at_risk
FROM customer_behavioral_snapshot bs
WHERE bs.is_churned = 0  -- Active customers only
  AND (
      bs.is_inactive_30d = 1           -- Inactive in last 30 days
      OR bs.open_tickets_30d >= 1      -- Open support friction
  )
GROUP BY bs.plan, bs.billing_cycle
ORDER BY exposed_mrr DESC;

-- ============================================================
-- TABLE 5: Revenue at Risk — Measure 3 (Projected / Estimated)
-- Using the average monthly churn rate per plan to project
-- how much MRR will likely be lost next month.
-- ============================================================
DROP TABLE IF EXISTS revenue_projected_risk;
CREATE TABLE revenue_projected_risk AS
WITH active_mrr AS (
    SELECT
        plan,
        COUNT(*) AS active_customers,
        SUM(mrr) AS total_active_mrr
    FROM clean_subscriptions
    WHERE status = 'Active'
    GROUP BY plan
),
churn_rates AS (
    SELECT
        plan,
        ROUND(CAST(total_churn_pct AS REAL) / 100.0, 4) AS monthly_churn_rate
    FROM churn_by_plan
)
SELECT
    a.plan,
    a.active_customers,
    ROUND(a.total_active_mrr, 2) AS total_active_mrr,
    ROUND(cr.monthly_churn_rate * 100, 2) AS monthly_churn_rate_pct,
    ROUND(a.total_active_mrr * cr.monthly_churn_rate, 2) AS projected_mrr_at_risk_next_month,
    ROUND(a.total_active_mrr * cr.monthly_churn_rate * 12, 2) AS projected_annual_mrr_at_risk
FROM active_mrr a
JOIN churn_rates cr ON a.plan = cr.plan
ORDER BY projected_mrr_at_risk_next_month DESC;
