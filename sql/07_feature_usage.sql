-- sql/07_feature_usage.sql
-- Answers Q5: Does product/feature usage affect churn?
-- Answers Q6: Does inactivity predict churn?
-- Answers Q10: What are the strongest observable leading indicators of churn?
--
-- LEAKAGE PREVENTION (v2 FIXED OBSERVATION DATE):
-- We choose ONE fixed observation date: '2025-11-01' (60 days before the last date in data: 2025-12-31).
-- All behavioral features (sessions, minutes, collaboration, support tickets, inactivity)
-- are computed strictly within a 30-day lookback BEFORE this date: [2025-10-02, 2025-11-01).
--
-- Churn label is prospective: did the customer churn within the 60 days AFTER the observation date
-- (between 2025-11-01 and 2025-12-31)?
--
-- Population exclusions:
-- 1. Customers with no usage tracking.
-- 2. Customers who had already churned before 2025-11-01.
-- 3. Customers who signed up on or after 2025-11-01.

-- ============================================================
-- TABLE 1: Per-customer behavioral snapshot (leakage-free fixed window)
-- ============================================================
DROP TABLE IF EXISTS customer_behavioral_snapshot;
CREATE TABLE customer_behavioral_snapshot AS
WITH eligible_customers AS (
    SELECT
        s.customer_id,
        s.status AS subscription_status,
        s.plan,
        s.billing_cycle,
        s.mrr,
        c.acquisition_channel,
        c.city_tier,
        c.company_size_band,
        s.start_date,
        s.end_date,
        -- Churn label: churned within the 60-day outcome window [2025-11-01, 2025-12-31]
        CASE
            WHEN s.end_date IS NOT NULL AND s.end_date >= '2025-11-01' AND s.end_date <= '2025-12-31' THEN 1
            ELSE 0
        END AS is_churned
    FROM clean_subscriptions s
    JOIN clean_customers c ON s.customer_id = c.customer_id
    WHERE s.customer_id IN (SELECT DISTINCT customer_id FROM clean_usage_daily)
      AND s.start_date < '2025-11-01'
      AND (s.end_date IS NULL OR s.end_date >= '2025-11-01')
),
usage_30d AS (
    -- Usage strictly in the 30 days BEFORE observation date
    SELECT
        u.customer_id,
        COUNT(*) AS usage_records_30d,
        SUM(u.sessions) AS total_sessions_30d,
        SUM(u.session_minutes) AS total_minutes_30d,
        SUM(u.feature_core_actions) AS core_actions_30d,
        SUM(u.feature_collaboration) AS collab_uses_30d,
        SUM(u.failed_actions) AS failed_actions_30d,
        MAX(u.date) AS last_active_date
    FROM clean_usage_daily u
    WHERE u.date >= date('2025-11-01', '-30 days')
      AND u.date < '2025-11-01'
    GROUP BY u.customer_id
),
usage_90d AS (
    -- Usage strictly in the 90 days BEFORE observation date
    SELECT
        u.customer_id,
        COUNT(*) AS usage_records_90d,
        SUM(u.sessions) AS total_sessions_90d,
        SUM(u.session_minutes) AS total_minutes_90d,
        SUM(u.feature_collaboration) AS collab_uses_90d
    FROM clean_usage_daily u
    WHERE u.date >= date('2025-11-01', '-90 days')
      AND u.date < '2025-11-01'
    GROUP BY u.customer_id
),
ticket_30d AS (
    -- Support tickets opened in the 30 days before observation date
    SELECT
        t.customer_id,
        COUNT(*) AS tickets_30d,
        SUM(CASE WHEN t.status = 'Open' THEN 1 ELSE 0 END) AS open_tickets_30d
    FROM clean_support_tickets t
    WHERE t.open_date >= date('2025-11-01', '-30 days')
      AND t.open_date < '2025-11-01'
    GROUP BY t.customer_id
)
SELECT
    ec.customer_id,
    ec.subscription_status,
    ec.is_churned,
    ec.plan,
    ec.billing_cycle,
    ec.mrr,
    ec.acquisition_channel,
    ec.city_tier,
    ec.company_size_band,

    -- 30-day usage features
    COALESCE(u30.total_sessions_30d, 0) AS sessions_30d,
    COALESCE(u30.total_minutes_30d, 0) AS minutes_30d,
    COALESCE(u30.core_actions_30d, 0) AS core_actions_30d,
    COALESCE(u30.collab_uses_30d, 0) AS collab_uses_30d,
    COALESCE(u30.failed_actions_30d, 0) AS failed_actions_30d,

    -- 90-day usage features
    COALESCE(u90.total_sessions_90d, 0) AS sessions_90d,
    COALESCE(u90.total_minutes_90d, 0) AS minutes_90d,
    COALESCE(u90.collab_uses_90d, 0) AS collab_uses_90d,

    -- Inactivity flag: zero sessions in 30-day lookback
    CASE WHEN COALESCE(u30.total_sessions_30d, 0) = 0 THEN 1 ELSE 0 END AS is_inactive_30d,

    -- Collaboration feature use flag: 1+ collab actions in 30-day lookback
    CASE WHEN COALESCE(u30.collab_uses_30d, 0) > 0 THEN 1 ELSE 0 END AS uses_collaboration,

    -- Support ticket signals
    COALESCE(tk.tickets_30d, 0) AS support_tickets_30d,
    COALESCE(tk.open_tickets_30d, 0) AS open_tickets_30d,

    u30.last_active_date
FROM eligible_customers ec
LEFT JOIN usage_30d u30 ON ec.customer_id = u30.customer_id
LEFT JOIN usage_90d u90 ON ec.customer_id = u90.customer_id
LEFT JOIN ticket_30d tk ON ec.customer_id = tk.customer_id;

-- ============================================================
-- TABLE 2: Churn rate by inactivity flag
-- Q6: Does inactivity predict churn?
-- ============================================================
DROP TABLE IF EXISTS churn_by_inactivity;
CREATE TABLE churn_by_inactivity AS
SELECT
    CASE
        WHEN is_inactive_30d = 1 THEN 'Inactive (0 sessions in 30d)'
        ELSE 'Active (1+ sessions in 30d)'
    END AS inactivity_group,
    COUNT(*) AS total_customers,
    SUM(is_churned) AS churned,
    ROUND(CAST(SUM(is_churned) AS REAL) / COUNT(*) * 100, 2) AS churn_pct
FROM customer_behavioral_snapshot
GROUP BY inactivity_group
ORDER BY churn_pct DESC;

-- ============================================================
-- TABLE 3: Churn rate by collaboration feature use
-- Q5: Does feature usage affect churn?
-- ============================================================
DROP TABLE IF EXISTS churn_by_feature_use;
CREATE TABLE churn_by_feature_use AS
SELECT
    CASE WHEN uses_collaboration = 1 THEN 'Uses Collaboration' ELSE 'No Collaboration Use' END AS feature_group,
    COUNT(*) AS total_customers,
    SUM(is_churned) AS churned,
    ROUND(CAST(SUM(is_churned) AS REAL) / COUNT(*) * 100, 2) AS churn_pct
FROM customer_behavioral_snapshot
GROUP BY uses_collaboration
ORDER BY churn_pct DESC;

-- ============================================================
-- TABLE 4: Churn rate by support ticket volume
-- Q10: Leading indicator — open tickets as friction signal
-- ============================================================
DROP TABLE IF EXISTS churn_by_support_tickets;
CREATE TABLE churn_by_support_tickets AS
SELECT
    CASE
        WHEN open_tickets_30d = 0 THEN 'No open tickets'
        WHEN open_tickets_30d = 1 THEN '1 open ticket'
        ELSE '2+ open tickets'
    END AS ticket_group,
    COUNT(*) AS total_customers,
    SUM(is_churned) AS churned,
    ROUND(CAST(SUM(is_churned) AS REAL) / COUNT(*) * 100, 2) AS churn_pct
FROM customer_behavioral_snapshot
GROUP BY ticket_group
ORDER BY churn_pct DESC;

-- ============================================================
-- TABLE 5: Average usage metrics by churn outcome
-- Q5/Q10: Do churned customers have meaningfully different usage?
-- ============================================================
DROP TABLE IF EXISTS avg_usage_by_churn_outcome;
CREATE TABLE avg_usage_by_churn_outcome AS
SELECT
    CASE WHEN is_churned = 1 THEN 'Churned within 60d' ELSE 'Retained' END AS outcome,
    COUNT(*) AS customer_count,
    ROUND(AVG(sessions_30d), 2) AS avg_sessions_30d,
    ROUND(AVG(minutes_30d), 2) AS avg_minutes_30d,
    ROUND(AVG(core_actions_30d), 2) AS avg_core_actions_30d,
    ROUND(AVG(collab_uses_30d), 2) AS avg_collab_uses_30d,
    ROUND(AVG(sessions_90d), 2) AS avg_sessions_90d,
    ROUND(AVG(support_tickets_30d), 2) AS avg_tickets_30d
FROM customer_behavioral_snapshot
GROUP BY is_churned;
