# Power BI Data Model Specification: Zorvio Churn Intelligence

> **SYNTHETIC DATA NOTICE:** All data is computer-generated for fictional company Zorvio.

---

## 1. Architectural Overview: Star Schema

The analytical model is structured as a clean **Star Schema** optimized for analytical performance, intuitive DAX authoring, and seamless slicer filtering across all report pages.

```
       +--------------------+          +--------------------+
       |    dim_customer    |          |      dim_date      |
       +--------------------+          +--------------------+
       | customer_id (PK)   |<---+     | date_key (PK)      |
       | signup_date        |    |     | full_date          |<---+
       | acquisition_channel|    |     | year, quarter      |    |
       | city, city_tier    |    |     | year_month         |    |
       | company_size_band  |    |     +--------------------+    |
       +--------------------+    |               |               |
                 ^               |               |               |
                 |               |               v               |
        1:*      |        1:*    |      +--------------------+   | 1:*
+---------------------+   +------+------+  | fact_monthly_churn |   |
| fact_customer_risk  |   |fact_subscriptions| |------------------|---+
+---------------------+   +-----------------+  | month (FK date)    |
| customer_id (FK)    |   | subscription_id |  | active_start       |
| risk_score          |   | customer_id (FK)|  | voluntary_churns   |
| risk_tier           |   | plan (FK)       |  | involuntary_churns |
| flag_inactive       |   | billing_cycle   |  | total_churn_pct    |
| flag_friction       |   | start_date (FK) |  +--------------------+
+---------------------+   | end_date        |
                          | mrr, arr        |
                          +-----------------+
                                  |
                                  v 1:*
                          +-----------------+
                          |    dim_plan     |
                          +-----------------+
                          | plan_name (PK)  |
                          | tier_level      |
                          | monthly_price   |
                          | target_segment  |
                          +-----------------+
```

---

## 2. Relationships and Cardinality

| Relationship (From -> To) | Cardinality | Cross-filter Direction | Active | Rationale |
|---|---|---|---|---|
| `dim_customer[customer_id]` -> `fact_subscriptions[customer_id]` | 1 : * (1-to-many) | Single (`dim_customer` filters `fact_subscriptions`) | Yes | Standard dimension-to-fact relationship. |
| `dim_plan[plan_name]` -> `fact_subscriptions[plan]` | 1 : * (1-to-many) | Single (`dim_plan` filters `fact_subscriptions`) | Yes | Enables plan tier slicing and ARPU aggregations. |
| `dim_date[full_date]` -> `fact_subscriptions[start_date]` | 1 : * (1-to-many) | Single (`dim_date` filters `fact_subscriptions`) | Yes | Analyzes signup velocity and cohorts. |
| `dim_date[full_date]` -> `fact_subscriptions[end_date]` | 1 : * (1-to-many) | Single | No (Inactive) | Used via `USERELATIONSHIP()` for churn timing analysis. |
| `dim_date[year_month]` -> `fact_monthly_churn[month]` | 1 : * (1-to-many) | Single | Yes | Links monthly aggregate churn metrics to date calendar. |
| `dim_customer[customer_id]` -> `fact_customer_risk[customer_id]` | 1 : 1 (or 1 : *) | Both | Yes | Links customer attributes to risk scores & indicators. |
| `dim_customer[customer_id]` -> `fact_high_risk_active[customer_id]` | 1 : 1 | Both | Yes | Direct filter for CS outreach queue. |

---

## 3. Table Dictionary

### `dim_customer`
- Source: `data/exports/dim_customer.csv` (30,000 rows)
- **Primary Key:** `customer_id`
- Attributes: `signup_date`, `acquisition_channel`, `city`, `city_tier`, `company_size_band`, `current_plan`, `billing_cycle`, `subscription_status`, `mrr`, `is_churned`.

### `dim_plan`
- Source: `data/exports/dim_plan.csv` (3 rows)
- **Primary Key:** `plan_name` ('Starter', 'Growth', 'Scale')
- Attributes: `tier_level` (1, 2, 3), `monthly_price_inr` (499, 1499, 3999), `target_segment`.

### `dim_date`
- Source: `data/exports/dim_date.csv` (731 rows)
- **Primary Key:** `date_key`, `full_date`
- Attributes: `year`, `quarter`, `month_num`, `month_name`, `year_month`, `day_of_month`, `day_of_week`, `is_month_end`.

### `fact_subscriptions`
- Source: `data/exports/fact_subscriptions.csv` (30,000 rows)
- **Primary Key:** `subscription_id`
- **Foreign Keys:** `customer_id`, `plan`, `start_date`
- Measures: `mrr`, `arr`, `tenure_months`.

### `fact_monthly_churn`
- Source: `data/exports/fact_monthly_churn.csv` (23 rows)
- Grain: 1 row per calendar month
- Measures: `active_start`, `voluntary_churns`, `involuntary_churns`, `total_churns`, `voluntary_churn_rate_pct`, `total_churn_rate_pct`.

### `fact_cohort_retention`
- Source: `data/exports/fact_cohort_retention.csv` (24 rows)
- Grain: 1 row per acquisition cohort
- Measures: `cohort_size`, retention rates `retention_pct_m1` through `retention_pct_m12`.

### `fact_customer_risk`
- Source: `data/exports/fact_customer_risk.csv` (4,786 rows with tracked usage)
- Measures: `sessions_30d`, `minutes_30d`, `collab_uses_30d`, `open_tickets_30d`, `flag_inactive`, `flag_support_friction`, `flag_low_stickiness`, `risk_score`, `risk_tier`.

### `fact_high_risk_active`
- Source: `data/exports/fact_high_risk_active.csv`
- Priority list of active accounts displaying high friction or usage decay, sorted by MRR.
