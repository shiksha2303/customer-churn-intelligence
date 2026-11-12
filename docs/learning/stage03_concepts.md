# Stage 3 Learning Concepts

## Concepts Used

1. **Denominators are Hard:**
   - *What it is:* The hardest part of churn analysis isn't counting cancellations; it's defining the denominator (who had the *opportunity* to cancel).
   - *Why we chose it:* By explicitly defining "Active on the 1st of the month" in SQL (using `start_date < m.month_start`), we avoided artificially inflating the churn rate with users who signed up and canceled in the same month.
   - *Interview angle:* When asked about churn, always start by defining the denominator. "Before calculating churn, we must define an active user. I defined it as..." This immediately flags you as a senior thinker.

2. **Test-Driven SQL:**
   - *What it is:* Writing Python `pytest` tests that run aggregations on the database to verify the SQL logic.
   - *Why we chose it:* SQL is notoriously hard to debug because a wrong `JOIN` doesn't throw an error; it just gives you the wrong number. By asserting that `total aggregated churns == total raw churns - same_month churns`, we mathematically proved our SQL is correct.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Just dividing `COUNT(canceled)` by `COUNT(all_customers)`.
- **Why we avoided it:** That produces a meaningless "overall" number that ignores time. Churn is a rate over time, which requires cohorting or monthly snapshotting.
