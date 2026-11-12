-- sql/02_staging_and_cleaning.sql
-- Creates clean layer tables by fixing or removing data quality issues identified in Stage 2.

-- 1. CLEAN CUSTOMERS (Deduplicate, fix casing, impute missing channels)
DROP TABLE IF EXISTS clean_customers;
CREATE TABLE clean_customers AS
WITH deduped AS (
    SELECT 
        customer_id, 
        signup_date, 
        COALESCE(acquisition_channel, 'Unknown') AS acquisition_channel,
        -- Standardize city names: Capitalize first letter, handle specific known variants
        CASE 
            WHEN LOWER(city) IN ('mumbai', 'bombay') THEN 'Mumbai'
            WHEN LOWER(city) IN ('bengaluru', 'bangalore') THEN 'Bengaluru'
            WHEN LOWER(city) = 'delhi' THEN 'Delhi'
            WHEN LOWER(city) = 'hyderabad' THEN 'Hyderabad'
            WHEN LOWER(city) = 'chennai' THEN 'Chennai'
            WHEN LOWER(city) = 'pune' THEN 'Pune'
            WHEN LOWER(city) = 'kolkata' THEN 'Kolkata'
            WHEN LOWER(city) = 'ahmedabad' THEN 'Ahmedabad'
            WHEN LOWER(city) = 'jaipur' THEN 'Jaipur'
            WHEN LOWER(city) = 'lucknow' THEN 'Lucknow'
            ELSE city 
        END AS city,
        city_tier,
        company_size_band,
        ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY signup_date) as rn
    FROM raw_customers
)
SELECT customer_id, signup_date, acquisition_channel, city, city_tier, company_size_band
FROM deduped
WHERE rn = 1;

-- 2. CLEAN SUBSCRIPTIONS (Fix logic error on end_date)
DROP TABLE IF EXISTS clean_subscriptions;
CREATE TABLE clean_subscriptions AS
SELECT 
    subscription_id,
    customer_id,
    plan,
    billing_cycle,
    mrr,
    start_date,
    -- If end_date < start_date, assume end_date is wrong and set it to NULL (active), 
    -- but ideally we'd impute based on payment failures. For now, we drop the bad end_date.
    CASE 
        WHEN end_date IS NOT NULL AND end_date < start_date THEN NULL 
        ELSE end_date 
    END AS end_date,
    status,
    cancel_reason
FROM raw_subscriptions;

-- 3. CLEAN PAYMENTS (Drop orphan records)
DROP TABLE IF EXISTS clean_payments;
CREATE TABLE clean_payments AS
SELECT p.*
FROM raw_payments p
INNER JOIN clean_customers c ON p.customer_id = c.customer_id;

-- 4. CLEAN USAGE (Fix impossible negative minutes)
DROP TABLE IF EXISTS clean_usage_daily;
CREATE TABLE clean_usage_daily AS
SELECT 
    customer_id,
    date,
    sessions,
    -- Cap negative minutes at 0 (or drop the row, but keeping the row preserves session counts)
    CASE WHEN session_minutes < 0 THEN 0 ELSE session_minutes END AS session_minutes,
    feature_core_actions,
    feature_collaboration,
    failed_actions
FROM raw_usage_daily;

-- 5. CLEAN SUPPORT TICKETS (Untouched, just passed through)
DROP TABLE IF EXISTS clean_support_tickets;
CREATE TABLE clean_support_tickets AS
SELECT * FROM raw_support_tickets;

-- 6. CLEAN MARKETING SPEND (Untouched, just passed through)
DROP TABLE IF EXISTS clean_marketing_spend;
CREATE TABLE clean_marketing_spend AS
SELECT * FROM raw_marketing_spend;
