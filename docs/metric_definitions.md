# Metric Definitions

This document mathematically defines how core business metrics are calculated in this project. Documenting these ensures consistency across SQL, Python, and Power BI.

## 1. Customer Churn Rate (Monthly)

**Definition:** The percentage of customers who were active at the *start* of the month who canceled their subscription *during* that month.

**Formula:**
`Monthly Churn Rate = (Canceled Customers in Month M) / (Active Customers on Day 1 of Month M)`

**Important Exclusions:**
- Customers who both signed up AND canceled in the same month are **excluded** from that month's calculation. Why? Because they were not part of the active user base on Day 1. Including them inflates the churn rate artifactually.
- Involuntary churn (payment failures) must be separated from voluntary churn for behavioral analysis.

## 2. Monthly Recurring Revenue (MRR)

**Definition:** The normalized monthly revenue from all active subscriptions.

**Formula:**
- For Monthly plans: `MRR = Subscription Price`
- For Annual plans: `MRR = (Annual Subscription Price) / 12`

## 3. Average Revenue Per User (ARPU)

**Definition:** The average MRR generated per active customer.

**Formula:**
`ARPU = (Total MRR of Active Customers) / (Count of Active Customers)`

## 4. Customer Lifetime Value (LTV)

**Definition:** The estimated total revenue a customer will generate before churning.

**Formula (Simple Method):**
`LTV = ARPU / Monthly Churn Rate`

*(Note: We use the simple method for baseline reporting. In reality, cohort-based LTV decay curves are more accurate).*
