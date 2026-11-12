"""
src/exporter.py
===============
Exports star-schema dimension and fact tables from SQLite (db/churn.db)
to data/exports/ for Power BI dashboard consumption.
"""

import sqlite3
import pandas as pd
from pathlib import Path


def export_star_schema(db_path="db/churn.db", export_dir="data/exports"):
    """Extracts analytical views and tables into star-schema CSVs for Power BI."""
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    print(f"Exporting star schema from {db_path} to {export_path}...")

    # 1. dim_customer
    dim_customer_query = """
    SELECT 
        c.customer_id,
        c.signup_date,
        c.acquisition_channel,
        c.city,
        c.city_tier,
        c.company_size_band,
        s.plan AS current_plan,
        s.billing_cycle,
        s.status AS subscription_status,
        s.mrr,
        CASE WHEN s.status != 'Active' THEN 1 ELSE 0 END AS is_churned
    FROM clean_customers c
    LEFT JOIN clean_subscriptions s ON c.customer_id = s.customer_id
    """
    df_customer = pd.read_sql(dim_customer_query, conn)
    df_customer.to_csv(export_path / "dim_customer.csv", index=False, encoding="utf-8")
    print(f"  -> dim_customer.csv ({len(df_customer):,} rows)")

    # 2. dim_plan
    dim_plan_data = [
        {"plan_id": 1, "plan_name": "Starter", "tier_level": 1, "monthly_price_inr": 499, "target_segment": "Individuals & Freelancers"},
        {"plan_id": 2, "plan_name": "Growth", "tier_level": 2, "monthly_price_inr": 1499, "target_segment": "Small Teams (2-10)"},
        {"plan_id": 3, "plan_name": "Scale", "tier_level": 3, "monthly_price_inr": 3999, "target_segment": "Mid Teams (11-50)"},
    ]
    df_plan = pd.DataFrame(dim_plan_data)
    df_plan.to_csv(export_path / "dim_plan.csv", index=False, encoding="utf-8")
    print(f"  -> dim_plan.csv ({len(df_plan)} rows)")

    # 3. dim_date (2024-01-01 to 2025-12-31)
    dates = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")
    df_date = pd.DataFrame({
        "date_key": dates.strftime("%Y%m%d").astype(int),
        "full_date": dates.strftime("%Y-%m-%d"),
        "year": dates.year,
        "quarter": "Q" + dates.quarter.astype(str),
        "month_num": dates.month,
        "month_name": dates.strftime("%B"),
        "year_month": dates.strftime("%Y-%m"),
        "day_of_month": dates.day,
        "day_of_week": dates.strftime("%A"),
        "is_month_end": dates.is_month_end.astype(int),
    })
    df_date.to_csv(export_path / "dim_date.csv", index=False, encoding="utf-8")
    print(f"  -> dim_date.csv ({len(df_date):,} rows)")

    # 4. fact_subscriptions
    df_subs = pd.read_sql("SELECT * FROM clean_subscriptions", conn)
    df_subs["arr"] = df_subs["mrr"] * 12
    # Compute tenure months
    ref_end = df_subs["end_date"].fillna("2025-12-31")
    df_subs["tenure_months"] = (
        (pd.to_datetime(ref_end).dt.year - pd.to_datetime(df_subs["start_date"]).dt.year) * 12 +
        (pd.to_datetime(ref_end).dt.month - pd.to_datetime(df_subs["start_date"]).dt.month)
    )
    df_subs.to_csv(export_path / "fact_subscriptions.csv", index=False, encoding="utf-8")
    print(f"  -> fact_subscriptions.csv ({len(df_subs):,} rows)")

    # 5. fact_monthly_churn
    df_monthly = pd.read_sql("SELECT * FROM monthly_churn_metrics", conn)
    df_monthly.to_csv(export_path / "fact_monthly_churn.csv", index=False, encoding="utf-8")
    print(f"  -> fact_monthly_churn.csv ({len(df_monthly):,} rows)")

    # 6. fact_cohort_retention
    df_cohort = pd.read_sql("SELECT * FROM cohort_retention", conn)
    df_cohort.to_csv(export_path / "fact_cohort_retention.csv", index=False, encoding="utf-8")
    print(f"  -> fact_cohort_retention.csv ({len(df_cohort):,} rows)")

    # 7. fact_customer_risk
    df_risk = pd.read_sql("SELECT * FROM customer_risk_scores", conn)
    df_risk.to_csv(export_path / "fact_customer_risk.csv", index=False, encoding="utf-8")
    print(f"  -> fact_customer_risk.csv ({len(df_risk):,} rows)")

    # 8. fact_high_risk_active
    df_high_risk = pd.read_sql("SELECT * FROM high_risk_active_customers", conn)
    df_high_risk.to_csv(export_path / "fact_high_risk_active.csv", index=False, encoding="utf-8")
    print(f"  -> fact_high_risk_active.csv ({len(df_high_risk):,} rows)")

    # 9. fact_mrr_by_plan
    df_mrr = pd.read_sql("SELECT * FROM mrr_by_plan", conn)
    df_mrr.to_csv(export_path / "fact_mrr_by_plan.csv", index=False, encoding="utf-8")
    print(f"  -> fact_mrr_by_plan.csv ({len(df_mrr):,} rows)")

    conn.close()
    print("Star schema export completed successfully!")


if __name__ == "__main__":
    export_star_schema()
