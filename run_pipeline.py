#!/usr/bin/env python3
"""
run_pipeline.py
===============
One-command pipeline runner for the Zorvio Customer Churn Intelligence project.

Usage:
    python run_pipeline.py [--stage STAGE] [--seed SEED]

Steps:
    1. Generate synthetic data (deterministic, seeded)
    2. Load raw data into SQLite (churn.db)
    3. Run SQL cleaning and staging scripts
    4. Run SQL analysis and export scripts
    5. Export star-schema CSVs for Power BI

This script is a thin orchestrator. The heavy logic lives in:
    synthetic_data/generator.py     — data generation
    src/db_loader.py                — CSV → SQLite loader
    src/sql_runner.py               — SQL script executor
    src/exporter.py                 — export to data/exports/

NOTE: Populated incrementally. At Stage 0 this file is a placeholder
that confirms the entry point exists and the environment works.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def check_environment():
    """Verify Python version and key imports before running."""
    print("=== Environment Check ===")
    version = sys.version_info
    assert version.major == 3 and version.minor >= 10, (
        f"Python 3.10+ required; found {sys.version}"
    )
    print(f"  Python: {sys.version.split()[0]}  [OK]")

    required = ["pandas", "numpy", "matplotlib", "seaborn", "scipy", "sqlite3"]
    for pkg in required:
        __import__(pkg)
        print(f"  {pkg}  [OK]")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Zorvio Churn Intelligence Pipeline"
    )
    parser.add_argument(
        "--stage",
        type=int,
        default=None,
        help="Run up to and including this stage number (default: all)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for synthetic data generator (default: 42)",
    )
    args = parser.parse_args()

    check_environment()

    target_stage = args.stage if args.stage is not None else 8

    print("=== Zorvio Churn Intelligence Pipeline ===")
    print(f"Status: Stages 1-8 implemented. Running up to Stage {target_stage}.")
    print()
    print("Pipeline steps:")
    steps = [
        "1. Generate synthetic data          [Stage 1]",
        "2. Load raw CSV -> SQLite + clean   [Stage 2]",
        "3. Core churn metrics (Q1/Q2)       [Stage 3]",
        "4. Cohort retention (Q3/Q4)         [Stage 4]",
        "5. Segmentation + channel (Q3/Q7)  [Stage 5]",
        "6. Feature usage + indicators (Q5/Q6/Q10) [Stage 6]",
        "7. Revenue at risk (Q8/Q9/Q11)     [Stage 7]",
        "8. Export Power BI CSVs            [Stage 8]",
    ]
    for s in steps:
        print(f"   {s}")

    print()
    if target_stage >= 1:
        print("=== STAGE 1: Data Generation ===")
        import sys
        sys.path.append(str(Path(__file__).parent))
        from synthetic_data import generator
        generator.generate_data(seed=args.seed)
        
    if target_stage >= 2:
        print("=== STAGE 2: DB Load & Cleaning ===")
        import sys
        sys.path.append(str(Path(__file__).parent))
        from src import db_loader, sql_runner
        
        # Load raw data
        db_loader.load_data_to_db()
        
        # Run cleaning
        sql_runner.run_sql_script("db/churn.db", Path("sql/02_staging_and_cleaning.sql"))
        
        # Run tests
        print("Running data quality tests...")
        # pyrefly: ignore [missing-import]
        import pytest
        pytest.main(["-v", "tests/test_data_quality.py"])
        
    if target_stage >= 3:
        print("=== STAGE 3: Core Analytical Metrics (Q1/Q2) ===")
        import sys
        import pandas as pd
        import sqlite3
        sys.path.append(str(Path(__file__).parent))
        from src import sql_runner
        
        # Run the SQL to calculate historical churn rates
        sql_runner.run_sql_script("db/churn.db", Path("sql/03_historical_churn_Q1_Q2.sql"))
        
        # Run tests for math logic
        print("Running SQL logic tests...")
        # pyrefly: ignore [missing-import]
        import pytest
        pytest.main(["-v", "tests/test_sql_logic.py"])
        
        # Extract the findings for the register
        conn = sqlite3.connect("db/churn.db")
        df_churn = pd.read_sql("SELECT * FROM monthly_churn_metrics", conn)
        conn.close()
        
        # We know from our generator spec that the outage was Sept 2025. 
        # Let's extract the average baseline and the peak.
        baseline_df = df_churn[~df_churn['month'].str.contains('2025-09|2025-10')]
        avg_voluntary = baseline_df['voluntary_churn_rate_pct'].mean()
        avg_total = baseline_df['total_churn_rate_pct'].mean()
        peak_row = df_churn.loc[df_churn['voluntary_churn_rate_pct'].idxmax()]
        
        finding_id = "F001"
        question_id = "Q1/Q2"
        observed = f"Baseline total churn: {avg_total:.1f}%. Baseline voluntary churn: {avg_voluntary:.1f}%. Peak voluntary churn: {peak_row['voluntary_churn_rate_pct']}% in {peak_row['month']}."
        finding = "Voluntary churn spiked massively in late 2025 but returned to baseline."
        
        finding_row = f'{finding_id},{question_id},"{observed}","{finding}",sql,High,,,,,"sql/03_historical_churn_Q1_Q2.sql",\n'
        
        # Check if F001 is already in there to avoid duplication on re-runs
        with open("outputs/findings_register.csv", "r", encoding="utf-8") as f:
            existing = f.read()
            
        if "F001" not in existing:
            with open("outputs/findings_register.csv", "a", encoding="utf-8") as f:
                f.write(finding_row)
            print("  -> Appended finding F001 to outputs/findings_register.csv")
        else:
            print("  -> Finding F001 already in register.")
            
    if target_stage >= 4:
        print("=== STAGE 4: Cohort Analysis (Q3/Q4) ===")
        import sys
        import pandas as pd
        import sqlite3
        sys.path.append(str(Path(__file__).parent))
        from src import sql_runner
        
        # Run SQL
        sql_runner.run_sql_script("db/churn.db", Path("sql/04_cohort_retention_Q3_Q4.sql"))
        
        # Extract findings
        conn = sqlite3.connect("db/churn.db")
        df_cohort = pd.read_sql("SELECT * FROM cohort_retention", conn)
        df_tenure = pd.read_sql("SELECT * FROM average_tenure WHERE status_group = 'Churned'", conn)
        conn.close()
        
        avg_m6_retention = df_cohort['retention_pct_m6'].mean()
        avg_churned_tenure = df_tenure.iloc[0]['avg_tenure_months']
        
        finding_id_3 = "F003"
        finding_id_4 = "F004"
        
        row_3 = f'{finding_id_3},Q3,"Average M6 retention is {avg_m6_retention:.1f}%","Retention holds steady through M6 for most cohorts, no obvious seasonal cohort drops.",sql,High,,,,,"sql/04_cohort_retention_Q3_Q4.sql",\n'
        row_4 = f'{finding_id_4},Q4,"Average tenure of a churned user is {avg_churned_tenure} months.","Churned users tend to leave early. High early mortality.",sql,High,,,,,"sql/04_cohort_retention_Q3_Q4.sql",\n'
        
        with open("outputs/findings_register.csv", "r", encoding="utf-8") as f:
            existing = f.read()
            
        with open("outputs/findings_register.csv", "a", encoding="utf-8") as f:
            appended = False
            if "F003" not in existing:
                f.write(row_3)
                appended = True
            if "F004" not in existing:
                f.write(row_4)
                appended = True
            if appended:
                print("  -> Appended findings F003 and F004 to register.")
            else:
                print("  -> Findings F003 and F004 already in register.")
        
    if target_stage >= 5:
        print("=== STAGE 5: Segmentation & Channel Analysis (Q3/Q7) ===")
        import sys
        import pandas as pd
        import sqlite3
        sys.path.append(str(Path(__file__).parent))
        from src import sql_runner

        sql_runner.run_sql_script("db/churn.db", Path("sql/05_segmentation.sql"))
        sql_runner.run_sql_script("db/churn.db", Path("sql/06_channel_and_tenure.sql"))

        conn = sqlite3.connect("db/churn.db")
        df_plan    = pd.read_sql("SELECT * FROM churn_by_plan", conn)
        df_billing = pd.read_sql("SELECT * FROM churn_by_billing_cycle", conn)
        conn.close()

        top_plan = df_plan.iloc[0]
        bot_plan = df_plan.iloc[-1]
        monthly_churn = df_billing[df_billing['billing_cycle'] == 'Monthly']['total_churn_pct'].values
        annual_churn  = df_billing[df_billing['billing_cycle'] == 'Annual']['total_churn_pct'].values

        observed_f005 = (
            f"{top_plan['plan']} plan has highest churn at {top_plan['total_churn_pct']}%; "
            f"{bot_plan['plan']} plan has lowest at {bot_plan['total_churn_pct']}%."
        )
        finding_f005 = "Churn varies significantly by plan tier. Lower plans show higher churn."

        billing_diff = ""
        if len(monthly_churn) > 0 and len(annual_churn) > 0:
            billing_diff = (
                f"Monthly billing churn: {monthly_churn[0]}% vs "
                f"Annual billing churn: {annual_churn[0]}%."
            )
        observed_f006 = billing_diff
        finding_f006 = "Annual billing is associated with significantly lower churn (commitment effect)."

        with open("outputs/findings_register.csv", "r", encoding="utf-8") as f:
            existing = f.read()

        with open("outputs/findings_register.csv", "a", encoding="utf-8") as f:
            if "F005" not in existing:
                f.write(f'F005,Q3,"{observed_f005}","{finding_f005}",sql,High,,,,,"sql/05_segmentation.sql",\n')
                print("  -> Appended finding F005 (churn by plan).")
            if "F006" not in existing and observed_f006:
                f.write(f'F006,Q3,"{observed_f006}","{finding_f006}",sql,High,,,,,"sql/05_segmentation.sql",\n')
                print("  -> Appended finding F006 (churn by billing cycle).")

    if target_stage >= 6:
        print("=== STAGE 6: Feature Usage & Leading Indicators (Q5/Q6/Q7/Q10) ===")
        import sys
        import pandas as pd
        import sqlite3
        sys.path.append(str(Path(__file__).parent))
        from src import sql_runner

        sql_runner.run_sql_script("db/churn.db", Path("sql/07_feature_usage.sql"))
        sql_runner.run_sql_script("db/churn.db", Path("sql/09_high_value_churn.sql"))  # risk scores depend on snapshot

        conn = sqlite3.connect("db/churn.db")
        df_inact   = pd.read_sql("SELECT * FROM churn_by_inactivity", conn)
        df_feat    = pd.read_sql("SELECT * FROM churn_by_feature_use", conn)
        df_channel = pd.read_sql("SELECT * FROM churn_by_channel ORDER BY total_churn_pct DESC", conn)
        conn.close()

        inactive_row = df_inact[df_inact['inactivity_group'].str.contains('Inactive')]
        active_row   = df_inact[df_inact['inactivity_group'].str.contains('Active \\(')]
        rr_inact = "N/A"
        if len(inactive_row) > 0 and len(active_row) > 0 and active_row.iloc[0]['churn_pct'] > 0:
            rr_inact = f"{inactive_row.iloc[0]['churn_pct'] / active_row.iloc[0]['churn_pct']:.2f}x"

        uses_row = df_feat[df_feat['feature_group'] == 'Uses Collaboration']
        no_uses_row = df_feat[df_feat['feature_group'] == 'No Collaboration Use']
        uses_val = uses_row.iloc[0]['churn_pct'] if len(uses_row) > 0 else 0
        no_uses_val = no_uses_row.iloc[0]['churn_pct'] if len(no_uses_row) > 0 else 0
        rr_collab = f"{no_uses_val / uses_val:.2f}x" if uses_val > 0 else "N/A"

        observed_f007 = (
            f"Inactive customers churn at {inactive_row.iloc[0]['churn_pct'] if len(inactive_row)>0 else '?'}%; "
            f"active customers at {active_row.iloc[0]['churn_pct'] if len(active_row)>0 else '?'}%. "
            f"Relative risk: {rr_inact}."
        )
        finding_f007 = "30-day inactivity is the strongest leading indicator of churn in prospective window."

        observed_f008 = (
            f"Collaboration feature users churn at {uses_val:.2f}%; non-users at {no_uses_val:.2f}%. "
            f"Relative risk (non-user vs user): {rr_collab}."
        )
        finding_f008 = "Collaboration feature use is associated with materially lower churn (stickiness signal)."

        top_ch = df_channel.iloc[0] if len(df_channel) > 0 else None
        bot_ch = df_channel.iloc[-1] if len(df_channel) > 0 else None
        observed_f009 = (
            f"Highest churn channel: {top_ch['acquisition_channel']} ({top_ch['total_churn_pct']}%); "
            f"Lowest: {bot_ch['acquisition_channel']} ({bot_ch['total_churn_pct']}%)."
        ) if top_ch is not None and bot_ch is not None else "Channel churn computed - see notebook 03."
        finding_f009 = (
            "App Store channel associated with highest churn - partly confounded by Starter plan skew. "
            "Referral channel associated with lowest churn."
        )

        with open("outputs/findings_register.csv", "r", encoding="utf-8") as f:
            existing = f.read()

        with open("outputs/findings_register.csv", "a", encoding="utf-8") as f:
            if "F007" not in existing:
                f.write(f'F007,Q6,"{observed_f007}","{finding_f007}",sql,High,,,,,"sql/07_feature_usage.sql",\n')
                print("  -> Appended finding F007 (inactivity indicator).")
            if "F008" not in existing:
                f.write(f'F008,Q5,"{observed_f008}","{finding_f008}",sql,High,,,,,"sql/07_feature_usage.sql",\n')
                print("  -> Appended finding F008 (feature stickiness).")
            if "F009" not in existing:
                f.write(f'F009,Q7,"{observed_f009}","{finding_f009}",sql,Medium,,,,,"sql/06_channel_and_tenure.sql",Confounding: App Store -> Starter plan.\n')
                print("  -> Appended finding F009 (channel churn).")

    if target_stage >= 7:
        print("=== STAGE 7: Revenue at Risk & Core Analytics Engine ===")
        import sys
        sys.path.append(str(Path(__file__).parent))
        from src import sql_runner, analytics

        sql_runner.run_sql_script("db/churn.db", Path("sql/08_revenue_and_risk.sql"))
        sql_runner.run_sql_script("db/churn.db", Path("sql/09_high_value_churn.sql"))

        # Run analytical calculations and generate expected_kpis.json
        analytics.run_full_analytics(db_path="db/churn.db", outputs_dir="outputs")
        print("  -> Executed full analytical engine and updated outputs/expected_kpis.json.")

    if target_stage >= 8:
        print("=== STAGE 8: Star Schema & Data Mart Export ===")
        import sys
        sys.path.append(str(Path(__file__).parent))
        from src import exporter, build_dashboard
        exporter.export_star_schema()
        print("  -> Exported star-schema CSVs to data/exports/.")
        build_dashboard.build_dashboard()


if __name__ == "__main__":
    main()
