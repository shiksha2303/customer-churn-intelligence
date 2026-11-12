# Power BI Dashboard Wireframes: Zorvio Churn Intelligence

> **SYNTHETIC DATA NOTICE:** All mockups illustrate dashboards built on synthetic data for Zorvio.

---

## Global Header & Filter Banner (All Pages)
```
+---------------------------------------------------------------------------------------------------------+
| [ZORVIO LOGO]  CUSTOMER CHURN INTELLIGENCE                                  Last Updated: 2025-12-31    |
| Filters: [ Date Range: 2024-2025 v ] [ Plan: All v ] [ Channel: All v ] [ Billing: All v ] [ City Tier ]|
+---------------------------------------------------------------------------------------------------------+
```

---

## Page 1: Executive KPI & Churn Trend Overview (Answers Q1, Q2)

### Layout & Visual Grid
```
+---------------------------------------------------------------------------------------------------------+
| [ KPI 1: Active MRR ]  | [ KPI 2: Active Users ] | [ KPI 3: Baseline Churn ] | [ KPI 4: Peak Churn (Sept)]|
|   INR 15.90M           |   10,380                |   6.1% (Voluntary 5.0%)   |   10.8% (Outage Spike)     |
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 1: Monthly Churn Rate Trend (Line & Area Chart) ]                                              |
|  - Line 1: Total Churn Rate % (Dark Blue)                                                               |
|  - Line 2: Voluntary Churn Rate % (Cyan)                                                                |
|  - Shaded Region: Sept-Oct 2025 Major Outage Event (Spike to 10.8%)                                     |
|  - Dotted Reference Line: Baseline Churn (6.1%)                                                         |
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 2: Churn Type Composition (Stacked Bar) ] | [ VISUAL 3: Churn vs Growth Net Additions ]        |
|  - Voluntary (Cancellation Request)                |  - New Signups (Green Bar)                         |
|  - Involuntary (Payment / Billing Failure)         |  - Churned Customers (Red Bar)                     |
|                                                    |  - Net Customer Growth (Line)                      |
+----------------------------------------------------+----------------------------------------------------+
```

---

## Page 2: Customer Segmentation & Cohort Retention (Answers Q3, Q4, Q7)

### Layout & Visual Grid
```
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 1: Churn Rate by Plan Tier (Bar Chart) ]  | [ VISUAL 2: Monthly vs Annual Billing (Donut) ]    |
|  - Starter (56.5% churn, High Volume)              |  - Monthly Billing: 59.1% Churn                    |
|  - Growth (56.4% churn)                            |  - Annual Billing: 49.4% Churn (10% lower churn)   |
|  - Scale (56.7% churn, High MRR Impact)            |                                                    |
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 3: Acquisition Channel Churn & Volume (Scatter / Bar Chart) ]                                  |
|  - App Store: 58.9% Churn (Lowest retention, skewed toward Starter tier)                               |
|  - Paid Social: 57.2% Churn                                                                             |
|  - Campus / Partnership: 56.4% Churn                                                                    |
|  - Organic Search: 56.1% Churn                                                                          |
|  - Referral: 55.6% Churn (Highest retention & LTV)                                                      |
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 4: Cohort Retention Heatmap (Matrix Visual) ]                                                  |
|  Rows: Signup Cohort (2024-01 to 2025-11) | Columns: Month 1, Month 2, Month 3, Month 6, Month 12        |
|  Values: Retention % (Color scale: Deep Green 100% -> Pale Yellow 70% -> Coral 50%)                      |
|  Key Insight: Steepest drop occurs between M0 and M2 (~20% drop), stabilizing by M6 (~69% retention)    |
+---------------------------------------------------------------------------------------------------------+
```

---

## Page 3: Behavioral Drivers & Leading Indicators (Answers Q5, Q6, Q10)

### Layout & Visual Grid
```
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 1: Inactivity Leading Indicator (Bar) ]   | [ VISUAL 2: Collaboration Stickiness Signal ]      |
|  - Inactive (0 sessions in 30d): 100.0% Churn      |  - Uses Collaboration: 11.1% Churn (89% retained!) |
|  - Active (1+ sessions in 30d): 48.4% Churn        |  - No Collaboration: 87.6% Churn                   |
|  * Relative Risk: 2.07x higher churn risk!         |  * Stickiness Effect: 7.9x lower churn!            |
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 3: Support Friction Indicator (Column Chart) ]                                                 |
|  - 0 Open Tickets in 30d: 48.2% Churn                                                                   |
|  - 1 Open Ticket in 30d: 72.5% Churn                                                                    |
|  - 2+ Open Tickets in 30d: 91.8% Churn                                                                  |
|  * Key Takeaway: Unresolved support tickets create immediate churn velocity                             |
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 4: Activity Decay Prior to Churn (Multi-line Chart) ]                                          |
|  X-Axis: Days Prior to Reference Date (-90d to 0d)                                                      |
|  Y-Axis: Average Daily Sessions & Active Minutes                                                        |
|  Lines: Retained Cohort (Flat line) vs Churned Cohort (Sharp cliff 25-35 days before cancel)             |
+---------------------------------------------------------------------------------------------------------+
```

---

## Page 4: Revenue at Risk & Financial Exposure (Answers Q8, Q9)

### Layout & Visual Grid
```
+---------------------------------------------------------------------------------------------------------+
| [ Total Active MRR ]   | [ Projected Monthly Risk ] | [ Annualized Risk ]   | [ High-Risk Active MRR ]  |
|   INR 15,903,979       |   INR 8,999,013            |   INR 107.98M         |   INR 1,299,675           |
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 1: Active MRR by Plan Tier (Treemap / Bar) ]                                                   |
|  - Scale Plan: INR 6.55M (41.2% of Total MRR) - High Value Concentration                                |
|  - Growth Plan: INR 5.48M (34.5% of Total MRR)                                                          |
|  - Starter Plan: INR 3.87M (24.3% of Total MRR)                                                         |
+----------------------------------------------------+----------------------------------------------------+
| [ VISUAL 2: Realized vs Exposed MRR Waterfall ]    | [ VISUAL 3: Revenue at Risk by Customer Type ]     |
|  - Active Base MRR: INR 15.90M                     |  - Mid Teams (11-50 seats): INR 5.8M at risk       |
|  - Outage Loss Impact: -INR 1.85M                  |  - Small Teams (2-10 seats): INR 5.2M at risk      |
|  - Monthly At-Risk Exposure: -INR 8.99M            |  - Individuals: INR 4.9M at risk                   |
+----------------------------------------------------+----------------------------------------------------+
```

---

## Page 5: Churn Action Center & CS Triage Queue (Answers Q11, Q12)

### Layout & Visual Grid
```
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 1: Risk Framework Validation Funnel (Monotonicity Verification) ]                             |
|  - Critical Risk (Score 3): 100.0% Churn Rate [ Wilson CI: 100.0% - 100.0% ]                            |
|  - High Risk (Score 2):     99.5% Churn Rate  [ Wilson CI: 99.0% - 100.0% ]                            |
|  - Medium Risk (Score 1):   84.7% Churn Rate  [ Wilson CI: 83.1% - 86.2% ]                             |
|  - Low Risk (Score 0):      11.4% Churn Rate  [ Wilson CI: 10.1% - 12.8% ]                             |
+---------------------------------------------------------------------------------------------------------+
| [ VISUAL 2: Actionable Priority Table: High-Risk Active Customer Queue (Direct Actionable Export) ]     |
| Customer ID | Plan   | Billing | MRR      | Sessions 30d | Open Tickets | Collab Used | Recommended Play |
|-------------+--------+---------+----------+--------------+--------------+-------------+------------------|
| CUST_10822  | Scale  | Monthly | INR 3,999| 0 (Inactive) | 2 (Friction) | No          | Play 1: CS Concierge
| CUST_04918  | Scale  | Monthly | INR 3,999| 1 (Decaying) | 1 (Friction) | No          | Play 2: Ticket Sprint
| CUST_18291  | Growth | Monthly | INR 1,499| 0 (Inactive) | 0            | No          | Play 3: Re-engage
+---------------------------------------------------------------------------------------------------------+
| [ INTERACTIVE BUTTONS: Export Triage Queue to CSV | View Playbook Guidelines | Trigger CS Notification ]|
+---------------------------------------------------------------------------------------------------------+
```
