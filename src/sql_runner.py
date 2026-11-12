import sqlite3
from pathlib import Path

def run_sql_script(db_path, script_path):
    print(f"Running SQL script: {script_path.name}")
    conn = sqlite3.connect(db_path)
    with open(script_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
