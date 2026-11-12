# Stage 4 Learning Concepts

## Concepts Used

1. **Cohort Analysis:**
   - *What it is:* Grouping customers by a shared characteristic (usually the month they signed up) and tracking their behavior over time.
   - *Why we chose it:* Overall churn rate (Q1/Q2) tells you *if* you have a problem. Cohort analysis tells you *where* the problem is. If the January cohort retains at 80% after 6 months, but the June cohort retains at 40%, you know something went wrong in June (e.g. bad marketing traffic, a buggy product release).
   - *Interview angle:* Most juniors just group by demographic variables. Showing that you understand *temporal cohorting* (grouping by time) is a massive green flag for a SaaS data role.

2. **Triangular Matrices in SQL:**
   - *What it is:* A matrix where rows are cohorts (Jan, Feb, Mar) and columns are months since signup (Month 1, Month 2, Month 3). Because the Dec cohort hasn't existed for 6 months yet, the matrix naturally forms a triangle shape.
   - *How we built it:* We calculated the exact month index of churn `(churn_year - signup_year)*12 + (churn_month - signup_month)`.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Just calculating "Average Lifespan" for everyone.
- **Why we avoided it:** Averages are misleading in subscription businesses. Active users haven't churned yet, so their "lifespan" is censored. By splitting tenure between Active and Churned customers in `average_tenure`, we get an accurate picture of mortality vs survival.
