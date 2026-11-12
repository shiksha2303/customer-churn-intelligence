-- sql/01_data_quality_checks.sql
-- Run this against the raw_ tables to identify injected quality issues.

-- 1. Identify Duplicates in Customers
SELECT customer_id, count(*) as row_count 
FROM raw_customers 
GROUP BY customer_id 
HAVING count(*) > 1;

-- 2. Inconsistent categories in City
SELECT city, count(*) as freq 
FROM raw_customers 
GROUP BY city 
ORDER BY city;

-- 3. Missing values in Acquisition Channel
SELECT count(*) as missing_channel_count 
FROM raw_customers 
WHERE acquisition_channel IS NULL OR acquisition_channel = '';

-- 4. Logic errors in Subscriptions (End Date before Start Date)
SELECT subscription_id, start_date, end_date 
FROM raw_subscriptions 
WHERE end_date IS NOT NULL AND end_date < start_date;

-- 5. Impossible values in Usage
SELECT * 
FROM raw_usage_daily 
WHERE session_minutes < 0;

-- 6. Orphan records in Payments
SELECT count(*) as orphan_payments 
FROM raw_payments p 
LEFT JOIN raw_customers c ON p.customer_id = c.customer_id 
WHERE c.customer_id IS NULL;
