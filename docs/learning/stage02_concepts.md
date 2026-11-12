# Stage 2 Learning Concepts

## Concepts Used

1. **Row-Count Conservation (Data Engineering 101):**
   - *What it is:* When you clean data, the number of rows in the output must equal the number of rows in the input minus the exact number of rows you deliberately decided to drop.
   - *Why we chose it:* A common beginner mistake is using an `INNER JOIN` during cleaning and silently losing 10% of the dataset without noticing. We wrote a `pytest` script specifically to prove that our row counts are mathematically perfect. This is how senior analysts and engineers work.

2. **Imputation over Deletion:**
   - *What it is:* When dealing with missing acquisition channels, we could have dropped the rows, or guessed the mode (e.g. Organic Search). Instead, we imputed them as 'Unknown'.
   - *Why we chose it:* Dropping the rows would artificially lower our total customer count and MRR calculations later. An 'Unknown' category preserves the revenue data while accurately reflecting the reality of tracking blockers (like ad-blockers preventing attribution).

3. **ELT over ETL (Extract, Load, Transform):**
   - *What it is:* We loaded the messy, raw CSVs *directly* into the database first, and then used SQL to clean them (creating `clean_` tables). 
   - *Why we chose it:* This pattern (ELT) is the modern standard (used with Snowflake/BigQuery/dbt). It means the raw truth is always queryable in the database if we ever need to audit our cleaning logic.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Just doing `df.dropna()` in pandas and exporting a new CSV.
- **Why we avoided it:** It hides the logic, silently destroys data, and cannot be version-controlled easily. By writing explicit SQL cleaning rules (`sql/02_staging_and_cleaning.sql`), we created a traceable, repeatable pipeline.
- **Shortcut avoided:** Not documenting why we made cleaning choices.
- **Why we avoided it:** Every choice (like nullifying an end date instead of dropping the subscription) has business implications. We logged these in `docs/decision_log.md` to show deliberate, defensible decision-making.
