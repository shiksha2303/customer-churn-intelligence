import sqlite3
import pandas as pd

DB_PATH = "db/churn.db"

def test_churn_math():
    """Verify that churn calculation logic is mathematically sound."""
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Total Churns in the metrics table should match the raw Canceled + Past_Due counts (excluding same-month churns)
    # Wait, our metrics table filters for `is_active_start = 1`. 
    # If someone signs up and cancels in the *same* month, they are not counted in the rate.
    
    metrics = pd.read_sql("SELECT SUM(voluntary_churns) as v, SUM(involuntary_churns) as i FROM monthly_churn_metrics", conn)
    total_metrics_churns = metrics['v'][0] + metrics['i'][0]
    
    raw_churns = pd.read_sql("SELECT count(*) as c FROM clean_subscriptions WHERE end_date IS NOT NULL", conn).iloc[0,0]
    same_month_churns = pd.read_sql("SELECT count(*) as c FROM clean_subscriptions WHERE end_date IS NOT NULL AND strftime('%Y-%m', start_date) = strftime('%Y-%m', end_date)", conn).iloc[0,0]
    
    assert total_metrics_churns == (raw_churns - same_month_churns), "Churn math mismatch: Monthly aggregations do not tie back to individual records."
    
    conn.close()
