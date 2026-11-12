-- sql/09_high_value_churn.sql
-- Answers Q9 (deep): Which specific high-value customers are at greatest risk?
-- Answers Q11: Can we identify high-risk customer groups?
--
-- Risk framework: rule-based scoring using snapshot features.
-- LEAKAGE SAFE (v2): uses customer_behavioral_snapshot (fixed observation window).
-- Thresholds are NOT tuned; we report authentic results even if separation is weaker.

-- ============================================================
-- TABLE 1: Risk Score per Customer
-- Three risk flags → composite score 0–3.
-- ============================================================
DROP TABLE IF EXISTS customer_risk_scores;
CREATE TABLE customer_risk_scores AS
SELECT
    customer_id,
    subscription_status,
    is_churned,
    plan,
    billing_cycle,
    mrr,
    acquisition_channel,
    city_tier,
    company_size_band,
    sessions_30d,
    minutes_30d,
    collab_uses_30d,
    support_tickets_30d,
    open_tickets_30d,
    is_inactive_30d,
    uses_collaboration,

    -- Flag 1: Inactivity signal (zero sessions in 30d lookback)
    CASE WHEN is_inactive_30d = 1 THEN 1 ELSE 0 END AS flag_inactive,

    -- Flag 2: Open support ticket (unresolved friction in 30d lookback)
    CASE WHEN open_tickets_30d >= 1 THEN 1 ELSE 0 END AS flag_support_friction,

    -- Flag 3: No collaboration feature use (low stickiness in 30d lookback)
    CASE WHEN uses_collaboration = 0 THEN 1 ELSE 0 END AS flag_low_stickiness,

    -- Composite risk score (0 = low, 3 = critical)
    (CASE WHEN is_inactive_30d = 1 THEN 1 ELSE 0 END
     + CASE WHEN open_tickets_30d >= 1 THEN 1 ELSE 0 END
     + CASE WHEN uses_collaboration = 0 THEN 1 ELSE 0 END
    ) AS risk_score,

    -- Risk tier label
    CASE
        WHEN (CASE WHEN is_inactive_30d = 1 THEN 1 ELSE 0 END
              + CASE WHEN open_tickets_30d >= 1 THEN 1 ELSE 0 END
              + CASE WHEN uses_collaboration = 0 THEN 1 ELSE 0 END) = 3 THEN 'Critical'
        WHEN (CASE WHEN is_inactive_30d = 1 THEN 1 ELSE 0 END
              + CASE WHEN open_tickets_30d >= 1 THEN 1 ELSE 0 END
              + CASE WHEN uses_collaboration = 0 THEN 1 ELSE 0 END) = 2 THEN 'High'
        WHEN (CASE WHEN is_inactive_30d = 1 THEN 1 ELSE 0 END
              + CASE WHEN open_tickets_30d >= 1 THEN 1 ELSE 0 END
              + CASE WHEN uses_collaboration = 0 THEN 1 ELSE 0 END) = 1 THEN 'Medium'
        ELSE 'Low'
    END AS risk_tier
FROM customer_behavioral_snapshot;

-- ============================================================
-- TABLE 2: Risk Framework Validation
-- Churn rate by risk tier — checks predictive power
-- ============================================================
DROP TABLE IF EXISTS risk_tier_validation;
CREATE TABLE risk_tier_validation AS
SELECT
    risk_tier,
    risk_score,
    COUNT(*) AS total_customers,
    SUM(is_churned) AS churned,
    ROUND(CAST(SUM(is_churned) AS REAL) / COUNT(*) * 100, 2) AS churn_pct,
    -- Wilson 95% CI
    ROUND(
        (CAST(SUM(is_churned) AS REAL)/COUNT(*)
        - 1.96 * SQRT(CAST(SUM(is_churned) AS REAL)/COUNT(*)
                      * (1 - CAST(SUM(is_churned) AS REAL)/COUNT(*)) / COUNT(*)))
        * 100, 2
    ) AS wilson_lower,
    ROUND(
        (CAST(SUM(is_churned) AS REAL)/COUNT(*)
        + 1.96 * SQRT(CAST(SUM(is_churned) AS REAL)/COUNT(*)
                      * (1 - CAST(SUM(is_churned) AS REAL)/COUNT(*)) / COUNT(*)))
        * 100, 2
    ) AS wilson_upper
FROM customer_risk_scores
GROUP BY risk_tier, risk_score
ORDER BY risk_score DESC;

-- ============================================================
-- TABLE 3: High-risk active customers with highest MRR exposure
-- Evaluated on customers who remained active as of the study end
-- ============================================================
DROP TABLE IF EXISTS high_risk_active_customers;
CREATE TABLE high_risk_active_customers AS
SELECT
    customer_id,
    plan,
    billing_cycle,
    mrr,
    acquisition_channel,
    city_tier,
    company_size_band,
    risk_tier,
    risk_score,
    flag_inactive,
    flag_support_friction,
    flag_low_stickiness,
    sessions_30d,
    open_tickets_30d
FROM customer_risk_scores
WHERE subscription_status = 'Active'
  AND risk_tier IN ('High', 'Critical')
ORDER BY mrr DESC, risk_score DESC;

-- ============================================================
-- TABLE 4: Revenue at risk by risk tier (active customers only)
-- ============================================================
DROP TABLE IF EXISTS revenue_at_risk_by_tier;
CREATE TABLE revenue_at_risk_by_tier AS
SELECT
    risk_tier,
    risk_score,
    plan,
    COUNT(*) AS customer_count,
    ROUND(SUM(mrr), 2) AS total_mrr_at_risk,
    ROUND(AVG(mrr), 2) AS avg_mrr
FROM customer_risk_scores
WHERE subscription_status = 'Active'
GROUP BY risk_tier, risk_score, plan
ORDER BY risk_score DESC, total_mrr_at_risk DESC;
