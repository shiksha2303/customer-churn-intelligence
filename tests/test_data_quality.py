import sqlite3
import pandas as pd

DB_PATH = "db/churn.db"

def test_row_conservation():
    """Ensure we didn't silently drop valid rows during cleaning."""
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Customers: Raw - Duplicates = Clean
    raw_cust_count = pd.read_sql("SELECT count(*) as c FROM raw_customers", conn).iloc[0,0]
    clean_cust_count = pd.read_sql("SELECT count(*) as c FROM clean_customers", conn).iloc[0,0]
    duplicate_count = pd.read_sql("SELECT sum(freq - 1) as c FROM (SELECT count(*) as freq FROM raw_customers GROUP BY customer_id HAVING freq > 1)", conn).iloc[0,0]
    if pd.isna(duplicate_count): duplicate_count = 0
    
    assert raw_cust_count - duplicate_count == clean_cust_count, "Customer rows lost during cleaning"

    # 2. Payments: Raw - Orphans = Clean
    raw_pay_count = pd.read_sql("SELECT count(*) as c FROM raw_payments", conn).iloc[0,0]
    clean_pay_count = pd.read_sql("SELECT count(*) as c FROM clean_payments", conn).iloc[0,0]
    orphan_count = pd.read_sql("SELECT count(*) as c FROM raw_payments p LEFT JOIN clean_customers c ON p.customer_id = c.customer_id WHERE c.customer_id IS NULL", conn).iloc[0,0]
    
    assert raw_pay_count - orphan_count == clean_pay_count, "Payment rows lost incorrectly during cleaning"

    # 3. Subscriptions: Should have exactly the same number of rows
    raw_sub_count = pd.read_sql("SELECT count(*) as c FROM raw_subscriptions", conn).iloc[0,0]
    clean_sub_count = pd.read_sql("SELECT count(*) as c FROM clean_subscriptions", conn).iloc[0,0]
    
    assert raw_sub_count == clean_sub_count, "Subscription rows lost during cleaning"
    
    conn.close()
