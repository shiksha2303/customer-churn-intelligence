# Question Traceability Matrix

> **Status:** ✅ Complete — All 12 business questions answered, traced to empirical SQL queries, notebooks, Power BI pages, and findings register IDs.
> Every number in the report traces to reproducible pipeline outputs.

| Q# | Question | SQL Script(s) | Notebook(s) | Dashboard Page | Finding(s) ID | Status |
|---|---|---|---|---|---|---|
| **Q1** | What is the current churn rate? | `03_historical_churn_Q1_Q2.sql` | `02_churn_overview_and_trend.ipynb` | Page 1 | `F001` | ✅ Complete |
| **Q2** | Is churn increasing or decreasing? | `03_historical_churn_Q1_Q2.sql` | `02_churn_overview_and_trend.ipynb` | Page 1 | `F001` | ✅ Complete |
| **Q3** | Which customer segments churn the most? | `05_segmentation.sql` | `03_segmentation_and_tenure.ipynb` | Page 2 | `F005`, `F006` | ✅ Complete |
| **Q4** | Are new customers more likely to churn than existing ones? | `04_cohort_retention_Q3_Q4.sql` | `04_cohorts_and_retention.ipynb` | Page 2 | `F003`, `F004` | ✅ Complete |
| **Q5** | Does product/feature usage affect churn? | `07_feature_usage.sql` | `05_behavior_and_feature_usage.ipynb` | Page 3 | `F008` | ✅ Complete |
| **Q6** | Does inactivity predict churn? | `07_feature_usage.sql` | `06_leading_indicators.ipynb` | Page 3 | `F007` | ✅ Complete |
| **Q7** | Which acquisition channels produce higher-churn customers? | `06_channel_and_tenure.sql` | `03_segmentation_and_tenure.ipynb` | Page 2 | `F009` | ✅ Complete |
| **Q8** | Which customer types generate the most revenue? | `08_revenue_and_risk.sql` | `08_revenue_at_risk_and_synthesis.ipynb` | Page 2, 4 | `F010` | ✅ Complete |
| **Q9** | Where is the greatest revenue at risk? | `08_revenue_and_risk.sql`, `09_high_value_churn.sql` | `08_revenue_at_risk_and_synthesis.ipynb` | Page 1, 4 | `F011` | ✅ Complete |
| **Q10** | What are the strongest observable leading indicators of churn? | `07_feature_usage.sql` | `06_leading_indicators.ipynb` | Page 3 | `F007`, `F008` | ✅ Complete |
| **Q11** | Can we identify high-risk customer groups? | `09_high_value_churn.sql` | `07_risk_framework_and_validation.ipynb` | Page 3, 5 | `F012` | ✅ Complete |
| **Q12** | What should the business do? | `08_revenue_and_risk.sql`, `09_high_value_churn.sql` | `08_revenue_at_risk_and_synthesis.ipynb`, `playbook/` | Page 5 | `Playbook` | ✅ Complete |

---

*Verified against `outputs/findings_register.csv` and SQLite database `db/churn.db`.*
