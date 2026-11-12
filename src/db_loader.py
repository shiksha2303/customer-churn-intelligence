import os
import sqlite3
import pandas as pd
from pathlib import Path

def load_data_to_db(db_path="db/churn.db", raw_data_dir="data/raw"):
    print("Loading raw CSVs into SQLite database...")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize schema
    schema_path = Path("sql/00_schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
        
    # Mapping of filename to table name
    tables = {
        "customers.csv": "raw_customers",
        "subscriptions.csv": "raw_subscriptions",
        "payments.csv": "raw_payments",
        "usage_daily.csv": "raw_usage_daily",
        "support_tickets.csv": "raw_support_tickets",
        "marketing_spend.csv": "raw_marketing_spend"
    }
    
    for filename, table_name in tables.items():
        file_path = Path(raw_data_dir) / filename
        if file_path.exists():
            print(f"  Loading {filename} -> {table_name}...")
            # Use pandas to load chunk by chunk for safety, though 25MB fits in memory easily
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="append", index=False)
        else:
            print(f"  Warning: {filename} not found. Did you run Stage 1?")
            
    conn.commit()
    conn.close()
    print("Database load complete.")

if __name__ == "__main__":
    load_data_to_db()
