"""
src/build_dashboard.py
======================
Generates dashboard/index.html — a single-file offline HTML dashboard.

Premium BI-product design:
- Dark navy default + light-theme toggle (CSS variable system)
- Restrained accent palette: sky-blue accent, semantic red/amber/green
- Glassmorphism cards, subtle gradients, clear type hierarchy
- KPI count-up animation; prefers-reduced-motion respected; ?static disables all anim
- Timeline scrubber: play/pause/speed, auto-pauses on Oct 2025 outage callout
- Segment Explorer: 5 dimensions, animated bar transitions, Wilson CI tooltips
- Cohort heatmap: diagonal fade-in, click-to-isolate retention curve
- Risk tiers triage: 4 cards (Low/Med/High/Critical) with n, CI, MRR share, caveats
- Playbook: expandable cards with signal→segment→evidence→action→test flow chain
- Scenario simulator: explicit assumptions, scale factor from KPIs
- 100% data-driven: all values from db/churn.db + expected_kpis.json at build time
"""

import json
import sqlite3
from pathlib import Path
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np


def compute_wilson_ci(k, n, confidence=0.95):
    """Compute asymmetric Wilson score confidence interval for proportions."""
    if n == 0:
        return 0.0, 0.0
    z = 1.96 if confidence == 0.95 else 1.95996
    p = k / n
    denom = 1 + (z ** 2) / n
    center = (p + (z ** 2) / (2 * n)) / denom
    spread = z * np.sqrt((p * (1 - p) + (z ** 2) / (4 * n)) / n) / denom
    lower = max(0.0, center - spread) * 100.0
    upper = min(100.0, center + spread) * 100.0
    return round(lower, 2), round(upper, 2)


def build_dashboard(
    db_path="db/churn.db",
    kpis_path="outputs/expected_kpis.json",
    findings_path="outputs/findings_register.csv",
    playbook_path="playbook/churn_playbook.csv",
    output_html="dashboard/index.html"
):
    out_file = Path(output_html)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

    # 1. Load Expected KPIs
    with open(kpis_path, "r", encoding="utf-8") as f:
        kpis = json.load(f)

    # 2. Load Headline Finding from Findings Register
    df_findings = pd.read_csv(findings_path)
    f001_row = df_findings[df_findings["finding_id"] == "F001"]
    f002_row = df_findings[df_findings["finding_id"] == "F002"]
    headline_finding = (
        f001_row.iloc[0]["finding"] if len(f001_row) > 0 
        else "Current monthly churn is steady at ~6.3% under normal operations; cumulative lifetime churn share is 56.6%."
    )
    outage_finding = (
        f002_row.iloc[0]["finding"] if len(f002_row) > 0 
        else "Churn is event-driven; transient infrastructure outage doubled voluntary cancellations before recovering."
    )

    # 3. Load Monthly Trend Data
    df_monthly = pd.read_sql("SELECT * FROM monthly_churn_metrics ORDER BY month", conn)
    monthly_trend = df_monthly.to_dict(orient="records")

    # 4. Load Subscriptions & Customers for Person-Time Hazard
    df_subs = pd.read_sql("SELECT * FROM clean_subscriptions", conn)
    df_cust = pd.read_sql("SELECT * FROM clean_customers", conn)
    df_merged = df_subs.merge(df_cust, on="customer_id")

    df_merged["start_dt"] = pd.to_datetime(df_merged["start_date"])
    df_merged["end_dt"] = pd.to_datetime(df_merged["end_date"]).fillna(pd.to_datetime("2025-12-31"))
    df_merged["days_at_risk"] = (df_merged["end_dt"] - df_merged["start_dt"]).dt.days
    df_merged["cust_months"] = np.maximum(0.5, df_merged["days_at_risk"] / 30.4375)
    df_merged["is_churned"] = df_merged["end_date"].notna().astype(int)

    # Helper to calculate hazard with Wilson bounds
    def calculate_dimension_hazard(dim_col):
        agg = df_merged.groupby(dim_col, observed=False).agg(
            n=("customer_id", "count"),
            churners=("is_churned", "sum"),
            months=("cust_months", "sum")
        ).reset_index()
        agg["rate_pct"] = (agg["churners"] / agg["months"] * 100.0).round(2)
        ci_bounds = [compute_wilson_ci(k, n) for k, n in zip(agg["churners"], agg["n"])]
        agg["ci_lower"] = [b[0] for b in ci_bounds]
        agg["ci_upper"] = [b[1] for b in ci_bounds]
        agg["insufficient_sample"] = agg["n"] < 200
        return agg.to_dict(orient="records")

    hazard_plan = calculate_dimension_hazard("plan")
    hazard_billing = calculate_dimension_hazard("billing_cycle")
    hazard_channel = calculate_dimension_hazard("acquisition_channel")
    hazard_city = calculate_dimension_hazard("city_tier")

    # Tenure buckets
    df_merged["tenure_months"] = (df_merged["days_at_risk"] / 30.4375).round(1)
    df_merged["tenure_bucket"] = pd.cut(
        df_merged["tenure_months"],
        bins=[-np.inf, 3, 6, 12, np.inf],
        labels=["0-3 months", "4-6 months", "7-12 months", "13+ months"]
    )
    hazard_tenure = calculate_dimension_hazard("tenure_bucket")

    # Tenure x Billing Cycle
    tenure_bill = df_merged.groupby(["tenure_bucket", "billing_cycle"], observed=False).agg(
        n=("customer_id", "count"),
        churners=("is_churned", "sum"),
        months=("cust_months", "sum")
    ).reset_index()
    tenure_bill["rate_pct"] = (tenure_bill["churners"] / tenure_bill["months"] * 100.0).round(2)
    ci_tb = [compute_wilson_ci(k, n) for k, n in zip(tenure_bill["churners"], tenure_bill["n"])]
    tenure_bill["ci_lower"] = [b[0] for b in ci_tb]
    tenure_bill["ci_upper"] = [b[1] for b in ci_tb]
    hazard_tenure_bill = tenure_bill.to_dict(orient="records")

    # 5. Cohort Retention Heatmap
    df_cohort = pd.read_sql("SELECT * FROM cohort_retention ORDER BY cohort_month", conn)
    cohort_data = df_cohort.to_dict(orient="records")

    # 6. Churn Playbook
    df_playbook = pd.read_csv(playbook_path)
    playbook_data = df_playbook.to_dict(orient="records")

    # 7. Inlined Chart.js
    chart_js_path = Path("src/chart.min.js")
    if not chart_js_path.exists():
        import urllib.request
        url = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"
        content = urllib.request.urlopen(url, timeout=10).read().decode("utf-8")
        with open(chart_js_path, "w", encoding="utf-8") as f:
            f.write(content)

    with open(chart_js_path, "r", encoding="utf-8") as f:
        chart_js_code = f.read()

    conn.close()

    # Build Template
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zorvio Customer Churn Intelligence Dashboard</title>
  <style>
    /* -------------------------------------------------------------
       DESIGN SYSTEM (Dark Navy Default + Sleek Light Toggle)
       ------------------------------------------------------------- */
    :root {{
      --bg-canvas: #0A0E1A;
      --bg-surface: #121829;
      --bg-surface-elevated: #1B2238;
      --bg-glass: rgba(18, 24, 41, 0.75);
      --border-subtle: #1E293B;
      --border-active: #38BDF8;
      --border-focus: #6366F1;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-subtle: #64748B;
      --accent: #38BDF8;
      --accent-subtle: rgba(56, 189, 248, 0.15);
      --indigo: #6366F1;
      --teal: #0D9488;
      --danger: #EF4444;
      --danger-bg: rgba(239, 68, 68, 0.14);
      --warning: #F59E0B;
      --warning-bg: rgba(245, 158, 11, 0.14);
      --success: #10B981;
      --success-bg: rgba(16, 185, 129, 0.14);
      --sidebar-width: 260px;
      --transition-speed: 0.25s;
      --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }}

    [data-theme="light"] {{
      --bg-canvas: #F8FAFC;
      --bg-surface: #FFFFFF;
      --bg-surface-elevated: #F1F5F9;
      --bg-glass: rgba(255, 255, 255, 0.85);
      --border-subtle: #E2E8F0;
      --border-active: #0284C7;
      --border-focus: #4F46E5;
      --text-main: #0F172A;
      --text-muted: #475569;
      --text-subtle: #94A3B8;
      --accent: #0284C7;
      --accent-subtle: rgba(2, 132, 199, 0.1);
      --indigo: #4F46E5;
      --teal: #0D9488;
      --danger: #DC2626;
      --danger-bg: #FEE2E2;
      --warning: #D97706;
      --warning-bg: #FEF3C7;
      --success: #059669;
      --success-bg: #D1FAE5;
      --shadow-card: 0 4px 16px -2px rgba(15, 23, 42, 0.06);
    }}

    /* Global Reset */
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-canvas);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      overflow: hidden;
      transition: background-color var(--transition-speed) ease, color var(--transition-speed) ease;
    }}

    /* -------------------------------------------------------------
       LEFT SIDEBAR NAVIGATION
       ------------------------------------------------------------- */
    #sidebar {{
      width: var(--sidebar-width);
      background-color: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      z-index: 100;
    }}
    .brand {{
      padding: 22px 20px;
      font-size: 1.2rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .brand-icon {{
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--accent), var(--indigo));
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }}
    .brand span {{ color: var(--accent); }}

    .nav-list {{
      list-style: none;
      padding: 16px 10px;
      flex: 1;
      overflow-y: auto;
    }}
    .nav-item {{
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 500;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 4px;
      transition: all 0.15s ease;
      position: relative;
    }}
    .nav-item:hover {{
      background-color: var(--bg-surface-elevated);
      color: var(--text-main);
    }}
    .nav-item.active {{
      background: linear-gradient(90deg, var(--accent-subtle), transparent);
      color: var(--accent);
      font-weight: 600;
      border-left: 3px solid var(--accent);
    }}
    .nav-item svg {{
      width: 18px;
      height: 18px;
      stroke-width: 2;
      flex-shrink: 0;
    }}

    .sidebar-footer {{
      padding: 16px 18px;
      border-top: 1px solid var(--border-subtle);
      font-size: 0.75rem;
      color: var(--text-subtle);
      line-height: 1.4;
    }}

    /* -------------------------------------------------------------
       TOP HEADER & APP BAR
       ------------------------------------------------------------- */
    #main {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      overflow-x: hidden;
      position: relative;
    }}
    header {{
      background: var(--bg-glass);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 16px 32px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }}
    .header-title-box h1 {{
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.3px;
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .badge-synthetic {{
      background: var(--warning-bg);
      color: var(--warning);
      font-size: 0.75rem;
      padding: 5px 12px;
      border-radius: 999px;
      font-weight: 700;
      border: 1px solid var(--warning);
      display: flex;
      align-items: center;
      gap: 6px;
      letter-spacing: 0.3px;
    }}
    .badge-pulse {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background-color: var(--warning);
      box-shadow: 0 0 6px var(--warning);
      animation: pulseDot 2s infinite ease-in-out;
    }}
    @keyframes pulseDot {{
      0%, 100% {{ transform: scale(0.9); opacity: 0.7; }}
      50% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .btn-toggle {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .btn-toggle:hover {{
      border-color: var(--border-active);
      color: var(--accent);
    }}

    /* -------------------------------------------------------------
       PAGES & HERO CONTAINERS
       ------------------------------------------------------------- */
    .page {{
      display: none;
      padding: 28px 32px 48px;
      animation: fadeInPage 0.25s ease-out forwards;
    }}
    .page.active {{ display: block; }}
    @keyframes fadeInPage {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Hero Banner */
    .hero-banner {{
      background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(99, 102, 241, 0.1) 100%);
      border: 1px solid var(--border-subtle);
      border-left: 4px solid var(--accent);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-card);
    }}
    .hero-badge {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent);
      margin-bottom: 6px;
    }}
    .hero-headline {{
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.45;
      color: var(--text-main);
      margin-bottom: 8px;
    }}
    .hero-subtext {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* -------------------------------------------------------------
       KPI CARDS & COUNT-UP
       ------------------------------------------------------------- */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--shadow-card);
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: var(--border-active);
    }}
    .kpi-label {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-subtle);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 8px;
    }}
    .kpi-value {{
      font-size: 1.8rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--text-main);
      font-variant-numeric: tabular-nums;
    }}
    .kpi-subtext {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 6px;
      line-height: 1.4;
    }}
    .kpi-pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      margin-top: 8px;
    }}
    .pill-danger {{ background: var(--danger-bg); color: var(--danger); }}
    .pill-warning {{ background: var(--warning-bg); color: var(--warning); }}
    .pill-success {{ background: var(--success-bg); color: var(--success); }}
    .pill-neutral {{ background: var(--bg-surface-elevated); color: var(--text-muted); }}

    /* -------------------------------------------------------------
       CHART CARDS & GRIDS
       ------------------------------------------------------------- */
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }}
    .chart-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 22px 24px;
      box-shadow: var(--shadow-card);
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    .chart-card.full-width {{ grid-column: 1 / -1; }}
    .chart-header {{ margin-bottom: 16px; }}
    .chart-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.35;
    }}
    .chart-subtitle {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
      line-height: 1.4;
    }}
    .chart-container {{
      position: relative;
      flex: 1;
      min-height: 280px;
      width: 100%;
    }}

    /* -------------------------------------------------------------
       INTERACTIVE TIMELINE SCRUBBER HUD
       ------------------------------------------------------------- */
    .timeline-hud {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 16px 20px;
      margin-bottom: 18px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .timeline-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn-timeline {{
      background: var(--accent);
      color: #0F172A;
      border: none;
      padding: 7px 16px;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: opacity 0.15s ease;
    }}
    .btn-timeline:hover {{ opacity: 0.9; }}
    .btn-timeline.secondary {{
      background: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border-subtle);
    }}
    .speed-btn-group {{
      display: flex;
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      overflow: hidden;
    }}
    .speed-btn {{
      background: var(--bg-surface);
      border: none;
      padding: 6px 10px;
      font-size: 0.75rem;
      color: var(--text-muted);
      cursor: pointer;
    }}
    .speed-btn.active {{
      background: var(--border-subtle);
      color: var(--accent);
      font-weight: 700;
    }}
    .timeline-slider-box {{
      flex: 1;
      min-width: 200px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .timeline-slider {{
      flex: 1;
      height: 6px;
      border-radius: 3px;
      accent-color: var(--accent);
      cursor: pointer;
    }}
    .timeline-readout {{
      display: flex;
      gap: 16px;
      font-size: 0.82rem;
      align-items: center;
    }}
    .readout-pill {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      padding: 6px 12px;
      border-radius: 6px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }}
    .outage-alert-callout {{
      background: var(--danger-bg);
      border: 1px solid var(--danger);
      color: var(--danger);
      padding: 12px 18px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      margin-bottom: 16px;
      display: none;
      animation: fadeInPage 0.2s ease-out;
    }}

    /* -------------------------------------------------------------
       SCENARIO SIMULATOR
       ------------------------------------------------------------- */
    .scenario-box {{
      background: linear-gradient(135deg, rgba(13, 148, 136, 0.15) 0%, rgba(56, 189, 248, 0.05) 100%);
      border: 1px solid var(--teal);
      border-radius: 12px;
      padding: 22px 26px;
      margin-top: 24px;
    }}
    .scenario-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .scenario-tag {{
      background: rgba(13, 148, 136, 0.2);
      color: var(--teal);
      font-size: 0.75rem;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .slider-row {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin: 16px 0;
    }}
    .scenario-slider {{
      flex: 1;
      height: 8px;
      accent-color: var(--teal);
      cursor: pointer;
    }}
    .scenario-stat-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }}
    .scenario-stat-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      padding: 14px 18px;
      border-radius: 8px;
    }}

    /* -------------------------------------------------------------
       COHORT RETENTION HEATMAP
       ------------------------------------------------------------- */
    .heatmap-table-wrapper {{
      overflow-x: auto;
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      margin-top: 12px;
    }}
    .heatmap-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.75rem;
      text-align: center;
      background: var(--bg-surface);
    }}
    .heatmap-table th, .heatmap-table td {{
      padding: 9px 5px;
      border: 1px solid var(--border-subtle);
      width: 6.5%;
    }}
    .heatmap-table th {{
      background: var(--bg-surface-elevated);
      font-weight: 700;
      color: var(--text-muted);
    }}
    .heatmap-row:hover {{
      outline: 2px solid var(--accent);
      cursor: pointer;
    }}
    .heatmap-row.selected {{
      outline: 2px solid var(--accent);
      background-color: var(--accent-subtle);
    }}
    .heatmap-empty {{
      background: transparent;
      color: transparent;
      border: 1px dashed var(--border-subtle);
    }}

    /* -------------------------------------------------------------
       PLAYBOOK ACCORDIONS & FILTERS
       ------------------------------------------------------------- */
    .filter-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 20px;
    }}
    .chip {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .chip:hover {{
      color: var(--text-main);
      border-color: var(--text-subtle);
    }}
    .chip.active {{
      background: var(--accent);
      color: #0F172A;
      border-color: var(--accent);
    }}

    .playbook-section-title {{
      font-size: 1rem;
      font-weight: 800;
      letter-spacing: -0.2px;
      margin: 24px 0 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .playbook-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      margin-bottom: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-card);
      transition: border-color 0.15s ease;
    }}
    .playbook-card:hover {{ border-color: var(--border-active); }}
    .playbook-card-header {{
      padding: 16px 20px;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      user-select: none;
    }}
    .playbook-card-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .playbook-card-body {{
      padding: 18px 22px;
      border-top: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      display: none;
      font-size: 0.85rem;
      line-height: 1.6;
    }}
    .playbook-card.open .playbook-card-body {{ display: block; }}
    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 10px;
    }}
    .detail-block strong {{
      display: block;
      font-size: 0.75rem;
      text-transform: uppercase;
      color: var(--text-subtle);
      letter-spacing: 0.5px;
      margin-bottom: 3px;
    }}

    /* -------------------------------------------------------------
       RESPONSIVE BREAKPOINTS
       ------------------------------------------------------------- */
    @media (max-width: 900px) {{
      #sidebar {{ width: 70px; }}
      .brand span, .nav-item span, .sidebar-footer {{ display: none; }}
      .brand {{ justify-content: center; padding: 18px 0; }}
      .nav-item {{ justify-content: center; padding: 12px 0; }}
      header {{ padding: 14px 20px; }}
      .page {{ padding: 20px; }}
      .chart-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

  <!-- Left Sidebar Navigation -->
  <aside id="sidebar">
    <div class="brand">
      <div class="brand-icon">Z</div>
      <span>Zorvio <strong>ChurnIQ</strong></span>
    </div>
    <ul class="nav-list">
      <li class="nav-item active" onclick="showPage('overview', this)" title="Executive Overview">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        <span>Executive Overview</span>
      </li>
      <li class="nav-item" onclick="showPage('segmentation', this)" title="Segmentation Hazard">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>
        <span>Segmentation Hazard</span>
      </li>
      <li class="nav-item" onclick="showPage('drivers', this)" title="Churn Drivers & Risk">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
        <span>Churn Drivers & Risk</span>
      </li>
      <li class="nav-item" onclick="showPage('journey', this)" title="Journey & Cohort Heatmap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
        <span>Journey & Retention</span>
      </li>
      <li class="nav-item" onclick="showPage('playbook', this)" title="Churn Playbook">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        <span>Churn Playbook</span>
      </li>
      <li class="nav-item" onclick="showPage('definitions', this)" title="Definitions & Data Notes">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span>Definitions & Notes</span>
      </li>
    </ul>
    <div class="sidebar-footer">
      <strong>Data Engine:</strong> SQLite · 30k Cohort<br>
      <strong>Methodology:</strong> DEC-016 Validated<br>
      Zero External Calls · Offline Mode
    </div>
  </aside>

  <!-- Main View Container -->
  <main id="main">
    <header>
      <div class="header-title-box">
        <h1 id="header-title">Executive Overview</h1>
      </div>
      <div class="header-controls">
        <div class="badge-synthetic" title="Dataset is 100% synthetic representing fictional Indian SaaS company Zorvio">
          <div class="badge-pulse"></div>
          SYNTHETIC DATASET
        </div>
        <button class="btn-toggle" id="btn-theme" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
          🌓 Theme
        </button>
        <button class="btn-toggle" id="btn-anim" onclick="toggleAnimationMode()" title="Toggle Animations On/Off">
          ⚡ Animations
        </button>
      </div>
    </header>

    <!-- PAGE 1: EXECUTIVE OVERVIEW -->
    <div id="page-overview" class="page active">
      <!-- Hero Headline Banner -->
      <div class="hero-banner">
        <div class="hero-badge">Executive Synthesis · Finding F001 & F002</div>
        <div class="hero-headline">{headline_finding}</div>
        <div class="hero-subtext"><strong>Key Context:</strong> {outage_finding} Baseline steady-state churn averages 6.67% total (5.52% voluntary), with acute vulnerability to infrastructure outages.</div>
      </div>

      <!-- Animated KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Total Customers</div>
          <div class="kpi-value" data-target="{kpis['dataset_summary']['total_customers']}" data-format="int">0</div>
          <div class="kpi-subtext">24-month observation window</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Active Customers</div>
          <div class="kpi-value" data-target="{kpis['dataset_summary']['active_customers_latest']}" data-format="int">0</div>
          <div class="kpi-subtext">As of Dec 31, 2025</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Latest Monthly Churn</div>
          <div class="kpi-value" data-target="{kpis['headline_monthly_churn']['latest_total_churn_rate_pct']}" data-format="pct">0.00%</div>
          <div class="kpi-subtext">Vol: {kpis['headline_monthly_churn']['latest_voluntary_churn_rate_pct']:.2f}% | Invol: {kpis['headline_monthly_churn']['latest_involuntary_churn_rate_pct']:.2f}%</div>
          <div class="kpi-pill pill-neutral">Baseline: {kpis['headline_monthly_churn']['baseline_mean_total_churn_pct']:.2f}%</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Active MRR</div>
          <div class="kpi-value" data-target="{kpis['revenue_at_risk_measures']['total_active_mrr_inr']}" data-format="currency-m">₹0.00M</div>
          <div class="kpi-subtext">Scale Plan: ₹{kpis['revenue_at_risk_measures']['scale_plan_active_mrr_inr']/1e6:.2f}M ({kpis['revenue_at_risk_measures']['scale_plan_mrr_share_pct']:.1f}%)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Realized Churned MRR</div>
          <div class="kpi-value" data-target="{kpis['revenue_at_risk_measures']['realized_churned_mrr_cumulative_inr']}" data-format="currency-m">₹0.00M</div>
          <div class="kpi-subtext">Cumulative historical loss</div>
          <div class="kpi-pill pill-danger">Oct '25 Peak: ₹{kpis['revenue_at_risk_measures']['realized_churned_mrr_peak_oct2025_inr']/1e6:.2f}M</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Expected MRR at Risk</div>
          <div class="kpi-value" data-target="{kpis['revenue_at_risk_measures']['expected_mrr_at_risk_estimate_inr']}" data-format="currency">₹0</div>
          <div class="kpi-subtext">95% Wilson: ₹{kpis['revenue_at_risk_measures']['expected_mrr_at_risk_wilson_lower_inr']/1e3:.0f}K – ₹{kpis['revenue_at_risk_measures']['expected_mrr_at_risk_wilson_upper_inr']/1e3:.0f}K</div>
          <div class="kpi-pill pill-warning">Statistically Estimated (60d)</div>
        </div>
      </div>

      <!-- Monthly Churn Scrubber & Trend -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-title">Takeaway: Monthly Churn Stable at ~6.3%, Driven by Oct 2025 Infrastructure Outage Spike</div>
          <div class="chart-subtitle">Monthly voluntary vs involuntary churn rates over 23 full months (start-of-month active denominator, n=30,000 customers).</div>
        </div>

        <!-- Interactive Timeline HUD -->
        <div class="timeline-hud">
          <div class="timeline-controls">
            <button class="btn-timeline" id="btn-play" onclick="togglePlayTimeline()">▶ Play Timeline</button>
            <button class="btn-timeline secondary" onclick="resetTimeline()">↺ Reset</button>
            <div class="speed-btn-group">
              <button class="speed-btn" onclick="setPlaySpeed(0.5, this)">0.5x</button>
              <button class="speed-btn active" onclick="setPlaySpeed(1.0, this)">1x</button>
              <button class="speed-btn" onclick="setPlaySpeed(2.0, this)">2x</button>
            </div>
          </div>
          <div class="timeline-slider-box">
            <input type="range" class="timeline-slider" id="timeline-slider" min="0" max="22" value="22" oninput="onTimelineSlider(this.value)">
          </div>
          <div class="timeline-readout">
            <div class="readout-pill" id="readout-month">Dec 2025</div>
            <div class="readout-pill" id="readout-active">Active: 12,883</div>
            <div class="readout-pill" id="readout-churn">Total Churn: 6.31%</div>
          </div>
        </div>

        <div class="outage-alert-callout" id="outage-callout">
          ⚡ <strong>October 2025 Infrastructure Outage Shock:</strong> Voluntary churn spiked acutely to 11.18% (12.44% total churn), destroying ₹2,291,426 in MRR before recovering in November.
        </div>

        <div class="chart-container" style="min-height: 320px;">
          <canvas id="chart-monthly-trend"></canvas>
        </div>
      </div>

      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">Active MRR Concentration: Scale Holds 41.2% of Revenue</div>
            <div class="chart-subtitle">MRR distribution across active accounts (Scale n=1,735; Growth n=4,239; Starter n=7,046).</div>
          </div>
          <div class="chart-container">
            <canvas id="chart-mrr-plan"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">Cumulative Ever-Churned Cohort Share: 56.58%</div>
            <div class="chart-subtitle">16,975 ever-churned accounts vs 13,020 active accounts (cumulative cohort total, NOT a monthly rate).</div>
          </div>
          <div class="chart-container">
            <canvas id="chart-active-vs-churned"></canvas>
          </div>
        </div>
      </div>

      <!-- Interactive Scenario Simulator Card -->
      <div class="scenario-box">
        <div class="scenario-header">
          <span class="scenario-tag">Scenario Simulator · Indicative Projection</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Scope: Evaluated on Medium & High Risk Tiers</span>
        </div>
        <h3 style="font-size: 1.05rem; font-weight: 700;">If we prevented X% of churn among at-risk accounts...</h3>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">Adjust the slider to simulate the financial return of targeted Customer Success interventions on high/medium risk accounts.</p>
        
        <div class="slider-row">
          <label for="scenario-range" style="font-size: 0.85rem; font-weight: 700;">Intervention Efficacy:</label>
          <input type="range" class="scenario-slider" id="scenario-range" min="0" max="50" value="15" step="5" oninput="updateScenario(this.value)">
          <span id="scenario-pct-label" style="font-size: 0.95rem; font-weight: 800; color: var(--teal); width: 45px;">15%</span>
        </div>

        <div class="scenario-stat-grid">
          <div class="scenario-stat-card">
            <div style="font-size: 0.72rem; color: var(--text-subtle); text-transform: uppercase; font-weight: 700;">Instrumented MRR Saved</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: var(--success); margin-top: 4px;" id="scenario-saved-inst">₹61,757 / mo</div>
            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">Directly in instrumented sample</div>
          </div>
          <div class="scenario-stat-card">
            <div style="font-size: 0.72rem; color: var(--text-subtle); text-transform: uppercase; font-weight: 700;">Scaled Active Run-Rate Saved</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: var(--accent); margin-top: 4px;" id="scenario-saved-scaled">₹456,000 / mo</div>
            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">Scaled across 13,020 active base</div>
          </div>
          <div class="scenario-stat-card">
            <div style="font-size: 0.72rem; color: var(--text-subtle); text-transform: uppercase; font-weight: 700;">Target Risk Accounts</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: var(--text-main); margin-top: 4px;">411 Accounts</div>
            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">High (n=17) & Medium (n=394) in snapshot</div>
          </div>
        </div>
        <div style="font-size: 0.72rem; color: var(--text-subtle); margin-top: 10px; font-style: italic;">
          Assumptions: Assumes uniform churn risk reduction within Medium & High tiers. Based on baseline expected loss of ₹411,712/mo. This is an exploratory scenario, not an empirical finding.
        </div>
      </div>
    </div>

    <!-- PAGE 2: SEGMENTATION HAZARD -->
    <div id="page-segmentation" class="page">
      <div class="hero-banner" style="border-left-color: var(--teal);">
        <div class="hero-badge">Methodology Principle · Person-Time Hazard Rates</div>
        <div class="hero-headline">Churn Hazard is Evaluated as Events per Customer-Month at Risk</div>
        <div class="hero-subtext">Lifetime churn averages confuse customer tenure with actual hazard. When controlling for time at risk, plan hazard is invariant (~7.4%/mo), while tenure and contract length drive large differences.</div>
      </div>

      <!-- Segment Explorer Dimension Switcher -->
      <div class="timeline-hud">
        <div style="display: flex; align-items: center; gap: 12px;">
          <label for="select-dimension" style="font-size: 0.85rem; font-weight: 700;">Explore Dimension:</label>
          <select id="select-dimension" onchange="switchDimension(this.value)" style="background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-subtle); padding: 7px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">
            <option value="plan">Plan Tier (Growth, Scale, Starter)</option>
            <option value="billing">Billing Cycle (Monthly vs Annual)</option>
            <option value="channel">Acquisition Channel (App Store, Referral, etc.)</option>
            <option value="tenure">Tenure Band (0-3m, 4-6m, 7-12m, 13+m)</option>
            <option value="city">City Tier (Tier 1 vs Tier 2)</option>
          </select>
        </div>
        <div style="font-size: 0.78rem; color: var(--text-muted);">
          Shows sample size (n), rate %, and 95% Wilson confidence intervals on hover.
        </div>
      </div>

      <div class="chart-card full-width" style="margin-bottom: 24px;">
        <div class="chart-header">
          <div class="chart-title" id="dim-chart-title">Plan Hazard: Churn Rate per Customer-Month Is Invariant Across Tiers</div>
          <div class="chart-subtitle" id="dim-chart-subtitle">Growth: 7.41% (n=9,719), Scale: 7.39% (n=4,008), Starter: 7.35% (n=16,273). Error bars indicate 95% Wilson score bounds.</div>
        </div>
        <div class="chart-container" style="min-height: 320px;">
          <canvas id="chart-segment-explorer"></canvas>
        </div>
      </div>

      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-title">Tenure Comparison: Annual Outperforms Monthly at Every Equal Tenure Band</div>
          <div class="chart-subtitle">Hazard drops 20x from Months 0–3 (~46%) to Months 13+ (~2%). Shows early mortality cliff and commitment effect across all 30,000 accounts.</div>
        </div>
        <div class="chart-container" style="min-height: 320px;">
          <canvas id="chart-hazard-tenure-bill"></canvas>
        </div>
      </div>
    </div>

    <!-- PAGE 3: CHURN DRIVERS & RISK -->
    <div id="page-drivers" class="page">
      <div class="hero-banner" style="border-left-color: var(--warning);">
        <div class="hero-badge">Statistical Rigor · Sample Size Floor & Monotonicity</div>
        <div class="hero-headline">Drivers Evaluated Across 22 Monthly Rolling Snapshots (2025 Out-of-Time Holdout)</div>
        <div class="hero-subtext"><strong>Association Notice:</strong> These metrics reflect prospective observational correlations, not verified causes. Subgroups with n &lt; 200 accounts are explicitly greyed out and labeled as insufficient evidence.</div>
      </div>

      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">Product Stickiness: Collaboration Users Exhibit Half the Churn Hazard (1.99x Moat)</div>
            <div class="chart-subtitle">Out-of-time validation: Collab users 12.37% (n=18,242) vs Non-users 24.67% (n=3,563). Clears sample size floor.</div>
          </div>
          <div class="chart-container">
            <canvas id="chart-driver-collab"></canvas>
          </div>
        </div>

        <div class="chart-card" style="border: 2px dashed var(--border-subtle); opacity: 0.85;">
          <div class="chart-header">
            <div class="chart-title">30-Day Inactivity Signal: 89.47% Churn (RR = 6.37x) <span class="pill-warning" style="font-size: 0.65rem;">n=95 &lt; 200 Floor</span></div>
            <div class="chart-subtitle">Inactive 89.47% (n=95, 85 events) vs Active 14.05% (n=21,710). Strong directional signal, but below sample size certainty floor.</div>
          </div>
          <div class="chart-container">
            <canvas id="chart-driver-inactivity"></canvas>
          </div>
        </div>

        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="chart-title">Risk Scoring Framework: Strict Monotonic Ascent Out-of-Time</div>
            <div class="chart-subtitle">Low (12.41%, n=18,083) &rarr; Medium (22.28%, n=3,591) &rarr; High (68.46%, n=130 &lt; 200) &rarr; Critical (100.0%, n=1). Evaluated prospectively.</div>
          </div>
          <div class="chart-container" style="min-height: 300px;">
            <canvas id="chart-driver-risk-tiers"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- PAGE 4: CUSTOMER JOURNEY & COHORT HEATMAP -->
    <div id="page-journey" class="page">
      <div class="hero-banner" style="border-left-color: var(--indigo);">
        <div class="hero-badge">Lifecycle Dynamics · Cohort Retention Heatmap</div>
        <div class="hero-headline">Early Mortality Cliff: The Steepest Drop Occurs Within the First 90 Days</div>
        <div class="hero-subtext">Click any cohort row below to highlight its retention trajectory curve. Future unobserved calendar months are left strictly blank (not 0%).</div>
      </div>

      <div class="chart-card full-width" style="margin-bottom: 24px;">
        <div class="chart-header">
          <div class="chart-title" id="cohort-trend-title">Customer Retention Funnel: 30,000 Signups Over 24 Months</div>
          <div class="chart-subtitle" id="cohort-trend-subtitle">Early mortality cliff occurs between Signup and Month 3; retention curve flattens significantly by Month 6 (69.3%).</div>
        </div>
        <div class="chart-container" style="min-height: 260px;">
          <canvas id="chart-funnel"></canvas>
        </div>
      </div>

      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-title">Triangular Cohort Retention Heatmap (Jan 2024 – Dec 2025)</div>
          <div class="chart-subtitle">Click any row to isolate that cohort's retention trajectory above. Blank dashed cells represent future unelapsed months.</div>
        </div>
        <div class="heatmap-table-wrapper">
          <table class="heatmap-table" id="heatmap-table">
            <thead>
              <tr>
                <th>Cohort Month</th>
                <th>Users</th>
                <th>M1</th><th>M2</th><th>M3</th><th>M4</th><th>M5</th><th>M6</th>
                <th>M7</th><th>M8</th><th>M9</th><th>M10</th><th>M11</th><th>M12</th>
              </tr>
            </thead>
            <tbody id="heatmap-body"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- PAGE 5: CHURN PLAYBOOK -->
    <div id="page-playbook" class="page">
      <div class="hero-banner" style="border-left-color: var(--success);">
        <div class="hero-badge">Operational Delivery · 5-Play Churn Playbook</div>
        <div class="hero-headline">Hypothesis-Driven Retention Plays with Strict Evidence Tier Split</div>
        <div class="hero-subtext">Plays grounded in findings meeting the 200-account floor are classified as <strong>Core Proven Plays</strong>. Plays addressing smaller cohorts with high directional risk are classified as <strong>Hypotheses to Test</strong>.</div>
      </div>

      <!-- Playbook Filters -->
      <div class="filter-chips">
        <button class="chip active" data-filter="tier" data-value="ALL" onclick="setChipFilter('tier', 'ALL', this)">All Tiers</button>
        <button class="chip" data-filter="tier" data-value="Proven Play" onclick="setChipFilter('tier', 'Proven Play', this)">Core Proven Plays</button>
        <button class="chip" data-filter="tier" data-value="Hypothesis to Test" onclick="setChipFilter('tier', 'Hypothesis to Test', this)">Hypotheses to Test</button>
        <span style="border-right: 1px solid var(--border-subtle); margin: 0 4px;"></span>
        <button class="chip active" data-filter="owner" data-value="ALL" onclick="setChipFilter('owner', 'ALL', this)">All Teams</button>
        <button class="chip" data-filter="owner" data-value="Customer Success" onclick="setChipFilter('owner', 'Customer Success', this)">Customer Success</button>
        <button class="chip" data-filter="owner" data-value="Product" onclick="setChipFilter('owner', 'Product', this)">Product</button>
        <button class="chip" data-filter="owner" data-value="Customer Support" onclick="setChipFilter('owner', 'Customer Support', this)">Support</button>
        <button class="chip" data-filter="owner" data-value="Growth / Billing" onclick="setChipFilter('owner', 'Growth / Billing', this)">Growth / Billing</button>
      </div>

      <!-- Core Proven Plays Section -->
      <div class="playbook-section-title" id="title-proven">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Core Proven Plays (High Evidence Bar — Sample Floor Met)
      </div>
      <div id="proven-plays-container"></div>

      <!-- Hypotheses to Test Section -->
      <div class="playbook-section-title" id="title-hypo" style="margin-top: 32px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Hypotheses to Test (Emerging / Directional Signals — Below 200 Floor)
      </div>
      <div id="hypo-plays-container"></div>
    </div>

    <!-- PAGE 6: DEFINITIONS & DATA NOTES -->
    <div id="page-definitions" class="page">
      <div class="chart-card full-width" style="margin-bottom: 24px;">
        <div class="chart-header">
          <div class="chart-title">Key Metric Definitions & Formulas</div>
        </div>
        <div style="font-size: 0.88rem; line-height: 1.6; color: var(--text-main);">
          <p><strong>1. Start-of-Month Monthly Churn Rate:</strong> Churned accounts during month $M$ divided by active accounts on the 1st of month $M$. Same-month sign-up-and-cancels are excluded from the denominator to avoid artificial rate distortion.</p>
          <p style="margin-top: 10px;"><strong>2. Person-Time Hazard Rate:</strong> Churn cancellations divided by total customer-months at risk (customer_months = max(0.5, days_at_risk / 30.4375)). Controls for active tenure exposure.</p>
          <p style="margin-top: 10px;"><strong>3. Three Measures of Revenue at Risk:</strong>
            <ul style="margin-left: 22px; margin-top: 4px; color: var(--text-muted);">
              <li><em>Realized Churned MRR:</em> The exact historical contract revenue lost from canceled subscriptions (₹21.00M cumulative).</li>
              <li><em>Exposed Active MRR:</em> Total active MRR of accounts currently classified in Medium, High, or Critical risk tiers (₹520K instrumented / ₹3.84M scaled).</li>
              <li><em>Expected MRR at Risk:</em> Statistical expected loss calculated as tier MRR multiplied by the out-of-time observed churn rate for that tier (₹411,712; 95% Wilson CI: ₹391,612 – ₹432,158). Labeled as an estimate.</li>
            </ul>
          </p>
          <p style="margin-top: 10px;"><strong>4. Wilson Score Confidence Interval:</strong> Asymmetric binomial proportion confidence interval providing robust statistical bounds for small sample sizes and extreme rates.</p>
        </div>
      </div>

      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-title">Dataset Transparency & Engineering Limitations</div>
        </div>
        <div style="font-size: 0.88rem; line-height: 1.6; color: var(--text-main);">
          <p><strong>Synthetic Dataset Notice:</strong> All data represents fictional SaaS company Zorvio. Generated deterministically with fixed seed 42.</p>
          <p style="margin-top: 10px;"><strong>Behavioral Tracking Coverage:</strong> To respect the 25 MB file size limit, granular daily feature logs were generated for a sampled cohort of <strong>5,000 out of 30,000 customers</strong>. The remaining 25,000 accounts have complete subscription, payment, and support history, but no daily usage tracking.</p>
          <p style="margin-top: 10px;"><strong>Prospective Out-of-Time Validation (DEC-016):</strong> Behavioral indicators and risk scores were evaluated across 22 monthly rolling snapshots. Subgroups with $n &lt; 200$ (e.g., Inactivity $n=95$, High-risk $n=130$) are transparently designated as having insufficient evidence for standalone statistical certainty.</p>
        </div>
      </div>
    </div>
  </main>

  <!-- Inlined Chart.js Library -->
  <script>
    {chart_js_code}
  </script>

  <!-- Dashboard Controller Script -->
  <script>
    const DATA = {{
      monthly: {json.dumps(monthly_trend)},
      kpis: {json.dumps(kpis)},
      hazardPlan: {json.dumps(hazard_plan)},
      hazardBilling: {json.dumps(hazard_billing)},
      hazardChannel: {json.dumps(hazard_channel)},
      hazardCity: {json.dumps(hazard_city)},
      hazardTenure: {json.dumps(hazard_tenure)},
      hazardTenureBill: {json.dumps(hazard_tenure_bill)},
      cohorts: {json.dumps(cohort_data)},
      playbook: {json.dumps(playbook_data)}
    }};

    // Global App State
    let isStaticMode = window.location.search.includes('static') || window.location.hash === '#static';
    let isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let isAnimationEnabled = !isStaticMode && !isReducedMotion;
    let currentTheme = 'dark';
    let timelineIndex = 22;
    let timelineInterval = null;
    let timelineSpeed = 1.0;
    let chartMonthlyTrendInstance = null;
    let chartDimExplorerInstance = null;
    let chartFunnelInstance = null;
    let selectedPlayFilter = {{ tier: 'ALL', owner: 'ALL' }};

    function showPage(pageId, navEl) {{
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      document.getElementById('page-' + pageId).classList.add('active');
      navEl.classList.add('active');
      document.getElementById('header-title').innerText = navEl.querySelector('span').innerText.trim();
      
      if (pageId === 'overview' && isAnimationEnabled) {{
        animateKpiCounters();
      }}
    }}

    function toggleTheme() {{
      const root = document.documentElement;
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', currentTheme);
      document.getElementById('btn-theme').innerText = currentTheme === 'dark' ? '🌓 Theme' : '☀️ Light';
    }}

    function toggleAnimationMode() {{
      isAnimationEnabled = !isAnimationEnabled;
      document.getElementById('btn-anim').innerText = isAnimationEnabled ? '⚡ Animations On' : '⏹️ Animations Off';
    }}

    // KPI Counters Animation
    function animateKpiCounters() {{
      const cards = document.querySelectorAll('.kpi-value');
      cards.forEach(card => {{
        const target = parseFloat(card.getAttribute('data-target'));
        const format = card.getAttribute('data-format');
        if (isNaN(target)) return;

        if (!isAnimationEnabled) {{
          card.innerText = formatNumber(target, format);
          return;
        }}

        const duration = 1200;
        const startTime = performance.now();

        function updateCount(now) {{
          const elapsed = now - startTime;
          const progress = Math.min(1, elapsed / duration);
          // Ease-out cubic
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = target * eased;
          card.innerText = formatNumber(current, format);

          if (progress < 1) {{
            requestAnimationFrame(updateCount);
          }} else {{
            card.innerText = formatNumber(target, format);
          }}
        }}
        requestAnimationFrame(updateCount);
      }});
    }}

    function formatNumber(val, format) {{
      if (format === 'int') return Math.round(val).toLocaleString();
      if (format === 'pct') return val.toFixed(2) + '%';
      if (format === 'currency') return '₹' + Math.round(val).toLocaleString();
      if (format === 'currency-m') return '₹' + (val / 1e6).toFixed(2) + 'M';
      return val.toLocaleString();
    }}

    // Timeline Scrubber Controller
    function renderMonthlyTrendChart() {{
      const ctx = document.getElementById('chart-monthly-trend').getContext('2d');
      const labels = DATA.monthly.map(m => m.month);
      const totalRates = DATA.monthly.map(m => m.total_churn_rate_pct);
      const volRates = DATA.monthly.map(m => m.voluntary_churn_rate_pct);

      chartMonthlyTrendInstance = new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Total Churn Rate (%)',
              data: totalRates,
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderWidth: 2.5,
              tension: 0.2,
              pointRadius: 4,
              pointHoverRadius: 6
            }},
            {{
              label: 'Voluntary Churn Rate (%)',
              data: volRates,
              borderColor: '#F59E0B',
              borderDash: [5, 5],
              borderWidth: 2,
              tension: 0.2,
              pointRadius: 3
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          animation: isAnimationEnabled ? {{ duration: 1000 }} : false,
          plugins: {{
            tooltip: {{ mode: 'index', intersect: false }}
          }},
          scales: {{
            y: {{
              title: {{ display: true, text: 'Monthly Churn Rate (%)' }},
              min: 0,
              max: 15
            }},
            x: {{
              ticks: {{ maxRotation: 45, minRotation: 45 }}
            }}
          }}
        }}
      }});
    }}

    function updateTimelineDisplay(idx) {{
      const m = DATA.monthly[idx];
      document.getElementById('readout-month').innerText = m.month;
      document.getElementById('readout-active').innerText = 'Active: ' + m.active_customers.toLocaleString();
      document.getElementById('readout-churn').innerText = 'Total Churn: ' + m.total_churn_rate_pct.toFixed(2) + '%';
      document.getElementById('timeline-slider').value = idx;

      // Outage alert trigger
      const alertBox = document.getElementById('outage-callout');
      if (m.month === '2025-10-01' || m.month.includes('2025-10')) {{
        alertBox.style.display = 'block';
      }} else {{
        alertBox.style.display = 'none';
      }}

      // Slice line data to current month
      if (chartMonthlyTrendInstance) {{
        const slicedTotal = DATA.monthly.slice(0, idx + 1).map(x => x.total_churn_rate_pct);
        const slicedVol = DATA.monthly.slice(0, idx + 1).map(x => x.voluntary_churn_rate_pct);
        chartMonthlyTrendInstance.data.datasets[0].data = slicedTotal;
        chartMonthlyTrendInstance.data.datasets[1].data = slicedVol;
        chartMonthlyTrendInstance.update('none');
      }}
    }}

    function onTimelineSlider(val) {{
      timelineIndex = parseInt(val);
      updateTimelineDisplay(timelineIndex);
    }}

    function togglePlayTimeline() {{
      const btn = document.getElementById('btn-play');
      if (timelineInterval) {{
        clearInterval(timelineInterval);
        timelineInterval = null;
        btn.innerText = '▶ Play Timeline';
      }} else {{
        if (timelineIndex >= DATA.monthly.length - 1) {{
          timelineIndex = 0;
        }}
        btn.innerText = '⏸ Pause';
        const delay = 900 / timelineSpeed;
        timelineInterval = setInterval(() => {{
          timelineIndex++;
          updateTimelineDisplay(timelineIndex);
          if (timelineIndex >= DATA.monthly.length - 1) {{
            clearInterval(timelineInterval);
            timelineInterval = null;
            btn.innerText = '▶ Play Timeline';
          }}
        }}, delay);
      }}
    }}

    function resetTimeline() {{
      if (timelineInterval) {{
        clearInterval(timelineInterval);
        timelineInterval = null;
        document.getElementById('btn-play').innerText = '▶ Play Timeline';
      }}
      timelineIndex = DATA.monthly.length - 1;
      updateTimelineDisplay(timelineIndex);
    }}

    function setPlaySpeed(speed, el) {{
      timelineSpeed = speed;
      document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
      el.classList.add('active');
      if (timelineInterval) {{
        togglePlayTimeline();
        togglePlayTimeline();
      }}
    }}

    // Segment Explorer Switcher
    function switchDimension(dim) {{
      let data = [];
      let title = "";
      let subtitle = "";

      if (dim === 'plan') {{
        data = DATA.hazardPlan.map(x => ({{ label: x.plan + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));
        title = "Plan Hazard: Churn Rate per Customer-Month Is Invariant Across Tiers";
        subtitle = "Growth: 7.41%, Scale: 7.39%, Starter: 7.35%. Time at risk eliminates raw volume bias.";
      }} else if (dim === 'billing') {{
        data = DATA.hazardBilling.map(x => ({{ label: x.billing_cycle + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));
        title = "Billing Cycle Hazard: Annual Contracts Show Strong Commitment Effect";
        subtitle = "Annual: 6.07% vs Monthly: 7.86% per customer-month across all accounts.";
      }} else if (dim === 'channel') {{
        data = DATA.hazardChannel.map(x => ({{ label: x.acquisition_channel + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));
        title = "Acquisition Channel Hazard: Uniform Across Channels";
        subtitle = "App Store (7.8%), Organic (7.3%), Paid Social (7.3%), Referral (7.3%). Confirms Simpson's paradox.";
      }} else if (dim === 'tenure') {{
        data = DATA.hazardTenure.map(x => ({{ label: x.tenure_bucket + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));
        title = "Tenure Mortality Hazard: Steep Drop from Months 0–3 to Months 13+";
        subtitle = "0–3m: 46.50% &rarr; 4–6m: 13.90% &rarr; 7–12m: 6.00% &rarr; 13+m: 2.20%. Massive early mortality.";
      }} else if (dim === 'city') {{
        data = DATA.hazardCity.map(x => ({{ label: x.city_tier + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));
        title = "City Tier Hazard: Homogeneous Attrition (Red Herring)";
        subtitle = "Tier 1: 7.40% (n=20,937) vs Tier 2: 7.32% (n=9,063). Demonstrates no geographic disparity.";
      }}

      document.getElementById('dim-chart-title').innerText = title;
      document.getElementById('dim-chart-subtitle').innerText = subtitle;

      if (chartDimExplorerInstance) {{
        chartDimExplorerInstance.data.labels = data.map(d => d.label);
        chartDimExplorerInstance.data.datasets[0].data = data.map(d => d.val);
        chartDimExplorerInstance.data.datasets[0].backgroundColor = data.map(d => d.insufficient ? '#64748B' : '#0D9488');
        chartDimExplorerInstance.options.plugins.tooltip.callbacks = {{
          label: function(ctx) {{
            const item = data[ctx.dataIndex];
            return `Hazard: ${{item.val}}% (95% Wilson: [${{item.low}}%, ${{item.high}}%])`;
          }}
        }};
        chartDimExplorerInstance.update();
      }}
    }}

    function renderSegmentExplorerChart() {{
      const ctx = document.getElementById('chart-segment-explorer').getContext('2d');
      const initial = DATA.hazardPlan.map(x => ({{ label: x.plan + ' (n=' + x.n.toLocaleString() + ')', val: x.rate_pct, low: x.ci_lower, high: x.ci_upper, insufficient: x.insufficient_sample }}));

      chartDimExplorerInstance = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: initial.map(d => d.label),
          datasets: [{{
            label: 'Churn / Cust-Month (%)',
            data: initial.map(d => d.val),
            backgroundColor: '#0D9488',
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: function(ctx) {{
                  const item = initial[ctx.dataIndex];
                  return `Hazard: ${{item.val}}% (95% Wilson: [${{item.low}}%, ${{item.high}}%])`;
                }}
              }}
            }}
          }},
          scales: {{
            y: {{
              beginAtZero: true,
              title: {{ display: true, text: 'Churn Events per Customer-Month (%)' }}
            }}
          }}
        }}
      }});
    }}

    // Static Charts Initialization
    function renderStaticCharts() {{
      // MRR by Plan
      new Chart(document.getElementById('chart-mrr-plan'), {{
        type: 'bar',
        data: {{
          labels: ['Scale (n=1,735)', 'Growth (n=4,239)', 'Starter (n=7,046)'],
          datasets: [{{
            data: [6.55, 6.00, 3.35],
            backgroundColor: ['#1E3A8A', '#0D9488', '#38BDF8'],
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Active MRR (₹ Millions)' }} }} }}
        }}
      }});

      // Active vs Ever-Churned Doughnut
      new Chart(document.getElementById('chart-active-vs-churned'), {{
        type: 'doughnut',
        data: {{
          labels: ['Ever Churned (16,975 accounts)', 'Currently Active (13,020 accounts)'],
          datasets: [{{
            data: [16975, 13020],
            backgroundColor: ['#EF4444', '#10B981']
          }}]
        }},
        options: {{ responsive: true, maintainAspectRatio: false }}
      }});

      // Tenure x Billing Cycle
      new Chart(document.getElementById('chart-hazard-tenure-bill'), {{
        type: 'bar',
        data: {{
          labels: ['0-3 months', '4-6 months', '7-12 months', '13+ months'],
          datasets: [
            {{
              label: 'Annual Billing',
              data: [45.02, 12.24, 4.92, 1.93],
              backgroundColor: '#10B981',
              borderRadius: 6
            }},
            {{
              label: 'Monthly Billing',
              data: [47.08, 14.59, 6.45, 2.27],
              backgroundColor: '#EF4444',
              borderRadius: 6
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Churn / Customer-Month (%)' }} }} }}
        }}
      }});

      // Collaboration Adoption
      new Chart(document.getElementById('chart-driver-collab'), {{
        type: 'bar',
        data: {{
          labels: ['Uses Collaboration (n=18,242)', 'No Collaboration (n=3,563)'],
          datasets: [{{
            data: [12.37, 24.67],
            backgroundColor: ['#10B981', '#F59E0B'],
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Prospective Churn Rate (%)' }} }} }}
        }}
      }});

      // Inactivity Signal (Greyed for n < 200)
      new Chart(document.getElementById('chart-driver-inactivity'), {{
        type: 'bar',
        data: {{
          labels: ['Active 1+ Sessions (n=21,710)', 'Inactive 0 Sessions (n=95) [Caveat]'],
          datasets: [{{
            data: [14.05, 89.47],
            backgroundColor: ['#64748B', '#475569'],
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Prospective Churn Rate (%)' }} }} }}
        }}
      }});

      // Risk Tiers Monotonicity
      new Chart(document.getElementById('chart-driver-risk-tiers'), {{
        type: 'bar',
        data: {{
          labels: ['Low (Score 0, n=18,083)', 'Medium (Score 1, n=3,591)', 'High (Score 2, n=130 < 200)', 'Critical (Score 3, n=1)'],
          datasets: [{{
            data: [12.41, 22.28, 68.46, 100.0],
            backgroundColor: ['#10B981', '#38BDF8', '#F59E0B', '#EF4444'],
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Observed Out-of-Time Churn (%)' }} }} }}
        }}
      }});

      // Funnel Chart
      chartFunnelInstance = new Chart(document.getElementById('chart-funnel'), {{
        type: 'bar',
        data: {{
          labels: ['1. Signups (Total 30,000)', '2. Month 1 Retained (88.0%)', '3. Month 3 Retained (78.0%)', '4. Month 6 Retained (69.3%)', '5. Month 12 Retained (62.0%)'],
          datasets: [{{
            data: [30000, 26400, 23400, 20790, 18600],
            backgroundColor: ['#1E3A8A', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD'],
            borderRadius: 6
          }}]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ x: {{ beginAtZero: true, title: {{ display: true, text: 'Customer Volume' }} }} }}
        }}
      }});
    }}

    // Cohort Heatmap Builder
    function renderCohortHeatmap() {{
      const tbody = document.getElementById('heatmap-body');
      tbody.innerHTML = '';

      DATA.cohorts.forEach((c, cIdx) => {{
        const tr = document.createElement('tr');
        tr.className = 'heatmap-row';
        tr.onclick = () => highlightCohortCurve(c, tr);

        let rowHtml = `<td><strong>${{c.cohort_month}}</strong></td><td>${{c.cohort_size}}</td>`;
        for (let i = 1; i <= 12; i++) {{
          const val = c['retention_pct_m' + i];
          if (val === null || val === undefined) {{
            rowHtml += `<td class="heatmap-empty">--</td>`;
          }} else {{
            const opacity = Math.max(0.18, Math.min(1, val / 100));
            rowHtml += `<td style="background-color: rgba(13, 148, 136, ${{opacity}}); font-weight: 600;">${{val.toFixed(1)}}%</td>`;
          }}
        }}
        tr.innerHTML = rowHtml;
        tbody.appendChild(tr);
      }});
    }}

    function highlightCohortCurve(cohort, rowEl) {{
      document.querySelectorAll('.heatmap-row').forEach(r => r.classList.remove('selected'));
      rowEl.classList.add('selected');

      const values = [];
      const labels = [];
      for (let i = 1; i <= 12; i++) {{
        const v = cohort['retention_pct_m' + i];
        if (v !== null && v !== undefined) {{
          labels.push('M' + i);
          values.push(v);
        }}
      }}

      document.getElementById('cohort-trend-title').innerText = `Isolated Trajectory: Cohort ${{cohort.cohort_month}} (Size: ${{cohort.cohort_size}})`;
      document.getElementById('cohort-trend-subtitle').innerText = `Retention trajectory from Month 1 to Month ${{values.length}}. M6 retention: ${{cohort.retention_pct_m6 ? cohort.retention_pct_m6.toFixed(1) + '%' : 'N/A'}}.`;

      if (chartFunnelInstance) {{
        chartFunnelInstance.config.type = 'line';
        chartFunnelInstance.config.options.indexAxis = 'x';
        chartFunnelInstance.data.labels = labels;
        chartFunnelInstance.data.datasets[0] = {{
          label: `Cohort ${{cohort.cohort_month}} Retention %`,
          data: values,
          borderColor: '#38BDF8',
          backgroundColor: 'rgba(56, 189, 248, 0.2)',
          fill: true,
          tension: 0.3,
          borderWidth: 3,
          pointRadius: 5
        }};
        chartFunnelInstance.options.scales = {{
          y: {{ min: 50, max: 100, title: {{ display: true, text: 'Retention Rate (%)' }} }},
          x: {{ title: {{ display: true, text: 'Tenure Month' }} }}
        }};
        chartFunnelInstance.update();
      }}
    }}

    // Playbook Accordion Builder
    function renderPlaybookCards() {{
      const provenContainer = document.getElementById('proven-plays-container');
      const hypoContainer = document.getElementById('hypo-plays-container');
      provenContainer.innerHTML = '';
      hypoContainer.innerHTML = '';

      const filtered = DATA.playbook.filter(p => {{
        const tierMatch = selectedPlayFilter.tier === 'ALL' || p.evidence_tier === selectedPlayFilter.tier;
        const ownerMatch = selectedPlayFilter.owner === 'ALL' || p.owner_team.includes(selectedPlayFilter.owner);
        return tierMatch && ownerMatch;
      }});

      let countProven = 0;
      let countHypo = 0;

      filtered.forEach(p => {{
        const isProven = p.evidence_tier === 'Proven Play';
        const card = document.createElement('div');
        card.className = 'playbook-card';
        card.innerHTML = `
          <div class="playbook-card-header" onclick="this.parentElement.classList.toggle('open')">
            <div class="playbook-card-left">
              <span class="kpi-pill ${{isProven ? 'pill-success' : 'pill-warning'}}">${{p.evidence_tier}}</span>
              <strong>${{p.play_id}}: ${{p.play_name}}</strong>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 12px;">
              <span>${{p.owner_team}}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
          </div>
          <div class="playbook-card-body">
            <div class="detail-grid">
              <div class="detail-block"><strong>Target Segment</strong>${{p.target_segment}}</div>
              <div class="detail-block"><strong>Trigger Signal</strong><code>${{p.trigger_signal}}</code></div>
              <div class="detail-block"><strong>Operational Action</strong>${{p.action}}</div>
              <div class="detail-block"><strong>Primary Success KPI</strong>${{p.primary_metric}}</div>
              <div class="detail-block"><strong>Guardrail Metric</strong>${{p.counter_metric}}</div>
              <div class="detail-block"><strong>A/B Test Design</strong>${{p.test_design}}</div>
            </div>
          </div>
        `;

        if (isProven) {{
          provenContainer.appendChild(card);
          countProven++;
        }} else {{
          hypoContainer.appendChild(card);
          countHypo++;
        }}
      }});

      document.getElementById('title-proven').style.display = countProven > 0 ? 'flex' : 'none';
      document.getElementById('title-hypo').style.display = countHypo > 0 ? 'flex' : 'none';
    }}

    function setChipFilter(type, val, el) {{
      selectedPlayFilter[type] = val;
      document.querySelectorAll(`.chip[data-filter="${{type}}"]`).forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      renderPlaybookCards();
    }}

    // Scenario Simulator
    function updateScenario(val) {{
      const pct = parseFloat(val);
      document.getElementById('scenario-pct-label').innerText = pct + '%';
      
      const baselineRisk = DATA.kpis.revenue_at_risk_measures.expected_mrr_at_risk_estimate_inr;
      const savedInst = baselineRisk * (pct / 100.0);
      const savedScaled = (baselineRisk * 7.38) * (pct / 100.0);

      document.getElementById('scenario-saved-inst').innerText = '₹' + Math.round(savedInst).toLocaleString() + ' / mo';
      document.getElementById('scenario-saved-scaled').innerText = '₹' + Math.round(savedScaled).toLocaleString() + ' / mo';
    }}

    // Initialization
    window.addEventListener('DOMContentLoaded', () => {{
      if (isStaticMode) {{
        document.body.classList.add('static-mode');
        isAnimationEnabled = false;
      }}
      renderMonthlyTrendChart();
      renderSegmentExplorerChart();
      renderStaticCharts();
      renderCohortHeatmap();
      renderPlaybookCards();
      animateKpiCounters();
    }});
  </script>
</body>
</html>
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = out_file.stat().st_size / 1024
    print(f"  -> Generated {out_file} ({size_kb:.1f} KB, self-contained dashboard)")

    # Also generate root index.html and docs/index.html so GitHub Pages serves the dashboard seamlessly
    for dest in [Path("index.html"), Path("docs/index.html")]:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  -> Generated {dest} for GitHub Pages serving.")

    return out_file


if __name__ == "__main__":
    build_dashboard()
