-- sql/04_cohort_retention_Q3_Q4.sql
-- Answers Q3: Which cohort has the highest retention?
-- Answers Q4: What is the average customer tenure?

DROP TABLE IF EXISTS cohort_retention;
CREATE TABLE cohort_retention AS
WITH cohort_sizes AS (
    SELECT 
        strftime('%Y-%m', signup_date) as cohort_month,
        COUNT(DISTINCT customer_id) as cohort_size
    FROM clean_customers
    GROUP BY 1
),
retention_data AS (
    SELECT 
        strftime('%Y-%m', c.signup_date) as cohort_month,
        c.customer_id,
        s.start_date,
        s.end_date,
        -- Generate months 0 through 24 relative to signup
        -- We will use a CROSS JOIN trick or just calculate the maximum tenure in months
        -- For SQLite, a simpler approach for the matrix is calculating the churn month relative to signup month.
        -- Month index of churn: (strftime('%Y', end_date) - strftime('%Y', signup_date)) * 12 + (strftime('%m', end_date) - strftime('%m', signup_date))
        CASE 
            WHEN s.end_date IS NOT NULL 
            THEN (strftime('%Y', s.end_date) - strftime('%Y', c.signup_date)) * 12 + (strftime('%m', s.end_date) - strftime('%m', c.signup_date))
            ELSE 999 -- Active
        END as churn_month_index
    FROM clean_customers c
    JOIN clean_subscriptions s ON c.customer_id = s.customer_id
)
-- To build the matrix easily in pandas later, we output the raw cohort data
-- but we also pre-aggregate it here for purely SQL-based reporting.
SELECT 
    cs.cohort_month,
    cs.cohort_size,
    -- Count how many customers have a churn_month_index > N (meaning they survived PAST month N)
    -- Month 1 retention:
    SUM(CASE WHEN churn_month_index >= 1 THEN 1 ELSE 0 END) as retained_m1,
    SUM(CASE WHEN churn_month_index >= 3 THEN 1 ELSE 0 END) as retained_m3,
    SUM(CASE WHEN churn_month_index >= 6 THEN 1 ELSE 0 END) as retained_m6,
    SUM(CASE WHEN churn_month_index >= 12 THEN 1 ELSE 0 END) as retained_m12,
    
    ROUND(CAST(SUM(CASE WHEN churn_month_index >= 1 THEN 1 ELSE 0 END) AS REAL) / cs.cohort_size * 100, 2) as retention_pct_m1,
    ROUND(CAST(SUM(CASE WHEN churn_month_index >= 6 THEN 1 ELSE 0 END) AS REAL) / cs.cohort_size * 100, 2) as retention_pct_m6,
    ROUND(CAST(SUM(CASE WHEN churn_month_index >= 12 THEN 1 ELSE 0 END) AS REAL) / cs.cohort_size * 100, 2) as retention_pct_m12
    
FROM cohort_sizes cs
LEFT JOIN retention_data rd ON cs.cohort_month = rd.cohort_month
GROUP BY cs.cohort_month, cs.cohort_size
ORDER BY cs.cohort_month;

-- Table for Average Tenure (Q4)
DROP TABLE IF EXISTS average_tenure;
CREATE TABLE average_tenure AS
WITH tenure_calc AS (
    SELECT 
        s.status,
        c.customer_id,
        CASE 
            WHEN s.end_date IS NOT NULL 
            THEN (julianday(s.end_date) - julianday(c.signup_date)) / 30.44
            ELSE (julianday('2025-12-31') - julianday(c.signup_date)) / 30.44
        END as tenure_months
    FROM clean_customers c
    JOIN clean_subscriptions s ON c.customer_id = s.customer_id
)
SELECT 
    CASE 
        WHEN status = 'Active' THEN 'Active'
        ELSE 'Churned'
    END as status_group,
    COUNT(*) as customer_count,
    ROUND(AVG(tenure_months), 1) as avg_tenure_months,
    ROUND(AVG(CASE WHEN tenure_months <= 3 THEN 1 ELSE 0 END) * 100, 1) as pct_churned_under_3_months
FROM tenure_calc
GROUP BY 1;
