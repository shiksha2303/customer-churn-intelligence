-- sql/00_schema.sql
-- Initializes the RAW layer tables for Zorvio customer churn data

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
    customer_id TEXT,
    signup_date TEXT,
    acquisition_channel TEXT,
    city TEXT,
    city_tier TEXT,
    company_size_band TEXT
);

DROP TABLE IF EXISTS raw_subscriptions;
CREATE TABLE raw_subscriptions (
    subscription_id TEXT,
    customer_id TEXT,
    plan TEXT,
    billing_cycle TEXT,
    mrr REAL,
    start_date TEXT,
    end_date TEXT,
    status TEXT,
    cancel_reason TEXT
);

DROP TABLE IF EXISTS raw_payments;
CREATE TABLE raw_payments (
    payment_id TEXT,
    customer_id TEXT,
    payment_date TEXT,
    amount REAL,
    status TEXT
);

DROP TABLE IF EXISTS raw_usage_daily;
CREATE TABLE raw_usage_daily (
    customer_id TEXT,
    date TEXT,
    sessions INTEGER,
    session_minutes INTEGER,
    feature_core_actions INTEGER,
    feature_collaboration INTEGER,
    failed_actions INTEGER
);

DROP TABLE IF EXISTS raw_support_tickets;
CREATE TABLE raw_support_tickets (
    ticket_id TEXT,
    customer_id TEXT,
    open_date TEXT,
    close_date TEXT,
    category TEXT,
    status TEXT
);

DROP TABLE IF EXISTS raw_marketing_spend;
CREATE TABLE raw_marketing_spend (
    month TEXT,
    channel TEXT,
    spend_inr REAL
);
