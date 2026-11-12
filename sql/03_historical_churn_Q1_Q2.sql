-- sql/03_historical_churn_Q1_Q2.sql
-- Answers Q1: What is our historical churn rate?
-- Answers Q2: Is it trending up or down?

DROP TABLE IF EXISTS monthly_churn_metrics;

CREATE TABLE monthly_churn_metrics AS
WITH months AS (
    -- Generate the first day of every month in our dataset (2024-01-01 to 2025-12-01)
    WITH RECURSIVE dates(d) AS (
        SELECT '2024-01-01'
        UNION ALL
        SELECT date(d, '+1 month')
        FROM dates
        WHERE d < '2025-12-01'
    )
    SELECT d as month_start FROM dates
),
customer_status AS (
    SELECT 
        m.month_start,
        s.customer_id,
        s.status as final_status,
        -- Is the customer active on the 1st of the month? (Started before, hasn't ended before)
        CASE 
            WHEN s.start_date < m.month_start 
                 AND (s.end_date IS NULL OR s.end_date >= m.month_start) 
            THEN 1 ELSE 0 
        END as is_active_start,
        
        -- Did the customer churn voluntarily DURING this month?
        CASE 
            WHEN s.end_date >= m.month_start 
                 AND s.end_date < date(m.month_start, '+1 month')
                 AND s.status = 'Canceled'
            THEN 1 ELSE 0 
        END as churned_voluntary,
        
        -- Did the customer churn involuntarily DURING this month?
        CASE 
            WHEN s.end_date >= m.month_start 
                 AND s.end_date < date(m.month_start, '+1 month')
                 AND s.status = 'Past_Due'
            THEN 1 ELSE 0 
        END as churned_involuntary
        
    FROM months m
    JOIN clean_subscriptions s 
        ON s.start_date < date(m.month_start, '+1 month')
)
SELECT 
    month_start as month,
    SUM(is_active_start) as active_customers,
    SUM(churned_voluntary) as voluntary_churns,
    SUM(churned_involuntary) as involuntary_churns,
    ROUND(CAST(SUM(churned_voluntary) AS REAL) / SUM(is_active_start) * 100, 2) as voluntary_churn_rate_pct,
    ROUND(CAST(SUM(churned_involuntary) AS REAL) / SUM(is_active_start) * 100, 2) as involuntary_churn_rate_pct,
    ROUND(CAST(SUM(churned_voluntary) + SUM(churned_involuntary) AS REAL) / SUM(is_active_start) * 100, 2) as total_churn_rate_pct
FROM customer_status
WHERE is_active_start = 1
GROUP BY month_start
ORDER BY month_start;
