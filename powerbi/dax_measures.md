# Power BI DAX Measures Library: Zorvio Churn Intelligence

> **SYNTHETIC DATA NOTICE:** All calculations operate on synthetic data generated for Zorvio.

---

## 1. Customer Volume & Status Measures

### [Total Customers]
```dax
Total Customers = 
DISTINCTCOUNT(dim_customer[customer_id])
```

### [Active Customers]
```dax
Active Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customer[customer_id]),
    dim_customer[subscription_status] = "Active"
)
```

### [Churned Customers]
```dax
Churned Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customer[customer_id]),
    dim_customer[is_churned] = 1
)
```

### [Overall Churn Rate %]
```dax
Overall Churn Rate % = 
DIVIDE(
    [Churned Customers],
    [Total Customers],
    0
)
```

---

## 2. Monthly Trend & Rate Measures

### [Monthly Active Start Customers]
```dax
Monthly Active Start Customers = 
SUM(fact_monthly_churn[active_start])
```

### [Monthly Total Churns]
```dax
Monthly Total Churns = 
SUM(fact_monthly_churn[total_churns])
```

### [Monthly Voluntary Churns]
```dax
Monthly Voluntary Churns = 
SUM(fact_monthly_churn[voluntary_churns])
```

### [Monthly Involuntary Churns]
```dax
Monthly Involuntary Churns = 
SUM(fact_monthly_churn[involuntary_churns])
```

### [Monthly Total Churn Rate %]
```dax
Monthly Total Churn Rate % = 
DIVIDE(
    [Monthly Total Churns],
    [Monthly Active Start Customers],
    0
)
```

### [Monthly Voluntary Churn Rate %]
```dax
Monthly Voluntary Churn Rate % = 
DIVIDE(
    [Monthly Voluntary Churns],
    [Monthly Active Start Customers],
    0
)
```

### [Baseline Voluntary Churn Rate %]
```dax
Baseline Voluntary Churn Rate % = 
CALCULATE(
    AVERAGEX(fact_monthly_churn, fact_monthly_churn[voluntary_churn_rate_pct] / 100),
    NOT(fact_monthly_churn[month] IN {"2025-09", "2025-10"})
)
```

---

## 3. Revenue & Financial Impact Measures

### [Active MRR]
```dax
Active MRR = 
CALCULATE(
    SUM(fact_subscriptions[mrr]),
    fact_subscriptions[status] = "Active"
)
```

### [Active ARR]
```dax
Active ARR = 
[Active MRR] * 12
```

### [Average ARPU]
```dax
Average ARPU = 
DIVIDE(
    [Active MRR],
    [Active Customers],
    0
)
```

### [Realized Churn MRR]
```dax
Realized Churn MRR = 
CALCULATE(
    SUM(fact_subscriptions[mrr]),
    fact_subscriptions[status] <> "Active"
)
```

### [Projected Monthly MRR at Risk]
```dax
Projected Monthly MRR at Risk = 
[Active MRR] * [Baseline Voluntary Churn Rate %]
```

### [Annualized Revenue at Risk]
```dax
Annualized Revenue at Risk = 
[Projected Monthly MRR at Risk] * 12
```

---

## 4. Cohort & Retention Measures

### [Average M1 Retention %]
```dax
Average M1 Retention % = 
AVERAGE(fact_cohort_retention[retention_pct_m1]) / 100
```

### [Average M3 Retention %]
```dax
Average M3 Retention % = 
AVERAGE(fact_cohort_retention[retention_pct_m3]) / 100
```

### [Average M6 Retention %]
```dax
Average M6 Retention % = 
AVERAGE(fact_cohort_retention[retention_pct_m6]) / 100
```

### [Average Customer Tenure (Months)]
```dax
Average Customer Tenure (Months) = 
AVERAGE(fact_subscriptions[tenure_months])
```

### [Average Churned Customer Tenure (Months)]
```dax
Average Churned Customer Tenure (Months) = 
CALCULATE(
    AVERAGE(fact_subscriptions[tenure_months]),
    fact_subscriptions[status] <> "Active"
)
```

---

## 5. Risk Framework & Leading Indicator Measures

### [Tracked Customers with Usage]
```dax
Tracked Customers with Usage = 
COUNTROWS(fact_customer_risk)
```

### [Inactive Customers (30d)]
```dax
Inactive Customers (30d) = 
CALCULATE(
    COUNTROWS(fact_customer_risk),
    fact_customer_risk[flag_inactive] = 1
)
```

### [Inactivity Churn Rate %]
```dax
Inactivity Churn Rate % = 
CALCULATE(
    DIVIDE(
        CALCULATE(COUNTROWS(fact_customer_risk), fact_customer_risk[is_churned] = 1),
        COUNTROWS(fact_customer_risk),
        0
    ),
    fact_customer_risk[flag_inactive] = 1
)
```

### [Collaboration Users Churn Rate %]
```dax
Collaboration Users Churn Rate % = 
CALCULATE(
    DIVIDE(
        CALCULATE(COUNTROWS(fact_customer_risk), fact_customer_risk[is_churned] = 1),
        COUNTROWS(fact_customer_risk),
        0
    ),
    fact_customer_risk[uses_collaboration] = 1
)
```

### [Non-Collaboration Users Churn Rate %]
```dax
Non-Collaboration Users Churn Rate % = 
CALCULATE(
    DIVIDE(
        CALCULATE(COUNTROWS(fact_customer_risk), fact_customer_risk[is_churned] = 1),
        COUNTROWS(fact_customer_risk),
        0
    ),
    fact_customer_risk[uses_collaboration] = 0
)
```

### [Critical Risk Active Customers]
```dax
Critical Risk Active Customers = 
CALCULATE(
    COUNTROWS(fact_high_risk_active),
    fact_high_risk_active[risk_tier] = "Critical"
)
```

### [High Risk MRR Exposure]
```dax
High Risk MRR Exposure = 
SUM(fact_high_risk_active[mrr])
```
