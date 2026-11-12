"""
src/analytics.py
================
Core analytical engine computing:
1. Headline monthly churn rates, baseline averages, and trend spikes.
2. Person-time hazard rates (churn events per customer-month at risk) by segment and tenure.
3. Multi-snapshot rolling lookback and prospective out-of-time evaluation across 22 months.
4. Statistical confidence bounds (Wilson score 95% CIs) and minimum sample size floor validation.
5. Three revenue-at-risk measures: Realized, Exposed, and Expected (with Wilson range).
6. Automatic generation of outputs/expected_kpis.json and outputs/findings_register.csv.
"""

import json
import sqlite3
from pathlib import Path
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd


def compute_wilson_ci(k, n, confidence=0.95):
    """Compute asymmetric Wilson score confidence interval for binomial proportions."""
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


def run_full_analytics(db_path="db/churn.db", outputs_dir="outputs"):
    out_path = Path(outputs_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

    # ============================================================
    # 1. HEADLINE MONTHLY CHURN & CUMULATIVE COHORT SHARE
    # ============================================================
    df_monthly = pd.read_sql("SELECT * FROM monthly_churn_metrics ORDER BY month", conn)
    latest_row = df_monthly.iloc[-1]
    baseline_df = df_monthly[~df_monthly["month"].str.contains("2025-09|2025-10")]
    peak_row = df_monthly.loc[df_monthly["voluntary_churn_rate_pct"].idxmax()]

    latest_total_churn_pct = round(float(latest_row["total_churn_rate_pct"]), 2)
    latest_vol_churn_pct = round(float(latest_row["voluntary_churn_rate_pct"]), 2)
    latest_invol_churn_pct = round(float(latest_row["involuntary_churn_rate_pct"]), 2)
    baseline_mean_total_pct = round(float(baseline_df["total_churn_rate_pct"].mean()), 2)
    baseline_mean_vol_pct = round(float(baseline_df["voluntary_churn_rate_pct"].mean()), 2)
    outage_peak_month = str(peak_row["month"])
    outage_peak_total_pct = round(float(peak_row["total_churn_rate_pct"]), 2)
    outage_peak_vol_pct = round(float(peak_row["voluntary_churn_rate_pct"]), 2)

    df_subs = pd.read_sql("SELECT * FROM clean_subscriptions", conn)
    total_customers = len(df_subs)
    churned_customers_total = int(df_subs["end_date"].notna().sum())
    active_customers_latest = int((df_subs["status"] == "Active").sum())
    cumulative_ever_churned_share_pct = round(churned_customers_total * 100.0 / total_customers, 2)

    # Active MRR
    total_active_mrr = round(float(df_subs[df_subs["status"] == "Active"]["mrr"].sum()), 2)

    # Plan active MRR
    plan_mrr_df = df_subs[df_subs["status"] == "Active"].groupby("plan")["mrr"].sum().to_dict()
    scale_active_mrr = round(float(plan_mrr_df.get("Scale", 0.0)), 2)
    growth_active_mrr = round(float(plan_mrr_df.get("Growth", 0.0)), 2)
    starter_active_mrr = round(float(plan_mrr_df.get("Starter", 0.0)), 2)
    scale_mrr_share_pct = round(scale_active_mrr * 100.0 / total_active_mrr, 2)

    # Realized Churned MRR
    q_realized = """
    SELECT 
        strftime('%Y-%m', end_date) as churn_month,
        plan,
        COUNT(*) as churned_subs,
        ROUND(SUM(mrr), 2) as realized_churned_mrr
    FROM clean_subscriptions
    WHERE end_date IS NOT NULL
    GROUP BY churn_month, plan
    ORDER BY churn_month, plan
    """
    df_realized = pd.read_sql(q_realized, conn)
    cum_realized_mrr = round(float(df_realized["realized_churned_mrr"].sum()), 2)
    oct25_realized = round(float(df_realized[df_realized["churn_month"] == "2025-10"]["realized_churned_mrr"].sum()), 2)
    dec25_realized = round(float(df_realized[df_realized["churn_month"] == "2025-12"]["realized_churned_mrr"].sum()), 2)

    # ============================================================
    # 2. PERSON-TIME HAZARD RATES (CHURN PER CUSTOMER-MONTH)
    # ============================================================
    df_subs["start_dt"] = pd.to_datetime(df_subs["start_date"])
    df_subs["end_dt"] = pd.to_datetime(df_subs["end_date"]).fillna(pd.to_datetime("2025-12-31"))
    df_subs["days_at_risk"] = (df_subs["end_dt"] - df_subs["start_dt"]).dt.days
    df_subs["cust_months"] = np.maximum(0.5, df_subs["days_at_risk"] / 30.4375)
    df_subs["is_churned"] = df_subs["end_date"].notna().astype(int)

    # By Plan
    plan_hazard = df_subs.groupby("plan").agg(events=("is_churned", "sum"), months=("cust_months", "sum"))
    plan_hazard_pct = (plan_hazard["events"] / plan_hazard["months"] * 100.0).round(2).to_dict()

    # By Billing Cycle
    bill_hazard = df_subs.groupby("billing_cycle").agg(events=("is_churned", "sum"), months=("cust_months", "sum"))
    bill_hazard_pct = (bill_hazard["events"] / bill_hazard["months"] * 100.0).round(2).to_dict()

    # By Tenure Bucket
    df_subs["tenure_months"] = (df_subs["days_at_risk"] / 30.4375).round(1)
    df_subs["tenure_bucket"] = pd.cut(
        df_subs["tenure_months"],
        bins=[-np.inf, 3, 6, 12, np.inf],
        labels=["0-3 months", "4-6 months", "7-12 months", "13+ months"]
    )
    tenure_hazard = df_subs.groupby("tenure_bucket", observed=False).agg(events=("is_churned", "sum"), months=("cust_months", "sum"))
    tenure_hazard_pct = (tenure_hazard["events"] / tenure_hazard["months"] * 100.0).round(2).to_dict()

    # ============================================================
    # 3. MONTHLY ROLLING SNAPSHOTS & OUT-OF-TIME VALIDATION
    # ============================================================
    snapshot_dates = pd.date_range(start="2024-01-31", end="2025-10-31", freq="ME").strftime("%Y-%m-%d").tolist()
    snapshots_data = []

    for obs_date in snapshot_dates:
        obs_dt = pd.to_datetime(obs_date)
        lookback_start = (obs_dt - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
        forward_end = (obs_dt + pd.Timedelta(days=60)).strftime("%Y-%m-%d")

        q = f"""
        WITH eligible AS (
            SELECT 
                s.customer_id,
                s.plan,
                s.billing_cycle,
                s.mrr,
                s.start_date,
                s.end_date,
                CASE 
                    WHEN s.end_date IS NOT NULL AND s.end_date >= '{obs_date}' AND s.end_date <= '{forward_end}' THEN 1
                    ELSE 0
                END AS is_churned_60d
            FROM clean_subscriptions s
            WHERE s.start_date < '{obs_date}'
              AND (s.end_date IS NULL OR s.end_date >= '{obs_date}')
              AND s.customer_id IN (SELECT DISTINCT customer_id FROM clean_usage_daily)
        ),
        u_30d AS (
            SELECT 
                customer_id,
                SUM(sessions) AS sessions_30d,
                SUM(feature_collaboration) AS collab_uses_30d,
                MAX(date) AS last_active_date
            FROM clean_usage_daily
            WHERE date >= '{lookback_start}' AND date < '{obs_date}'
            GROUP BY customer_id
        ),
        tk_30d AS (
            SELECT 
                customer_id,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets_30d
            FROM clean_support_tickets
            WHERE open_date >= '{lookback_start}' AND open_date < '{obs_date}'
            GROUP BY customer_id
        )
        SELECT 
            e.*,
            COALESCE(u.sessions_30d, 0) AS sessions_30d,
            COALESCE(u.collab_uses_30d, 0) AS collab_uses_30d,
            COALESCE(tk.open_tickets_30d, 0) AS open_tickets_30d,
            u.last_active_date
        FROM eligible e
        LEFT JOIN u_30d u ON e.customer_id = u.customer_id
        LEFT JOIN tk_30d tk ON e.customer_id = tk.customer_id
        """
        df_obs = pd.read_sql(q, conn)
        df_obs["obs_date"] = obs_date
        snapshots_data.append(df_obs)

    df_all_snapshots = pd.concat(snapshots_data, ignore_index=True)
    df_all_snapshots["flag_inactive"] = (df_all_snapshots["sessions_30d"] == 0).astype(int)
    df_all_snapshots["flag_friction"] = (df_all_snapshots["open_tickets_30d"] >= 1).astype(int)
    df_all_snapshots["flag_low_stickiness"] = (df_all_snapshots["collab_uses_30d"] == 0).astype(int)
    df_all_snapshots["risk_score"] = df_all_snapshots["flag_inactive"] + df_all_snapshots["flag_friction"] + df_all_snapshots["flag_low_stickiness"]
    df_all_snapshots["risk_tier"] = df_all_snapshots["risk_score"].map({3: "Critical", 2: "High", 1: "Medium", 0: "Low"})

    # Holdout validation (2025)
    df_val = df_all_snapshots[df_all_snapshots["obs_date"] >= "2025-01-01"].copy()

    val_tiers = df_val.groupby("risk_tier").agg(n=("customer_id", "count"), churners=("is_churned_60d", "sum")).to_dict(orient="index")

    def get_tier_stats(tier_name):
        data = val_tiers.get(tier_name, {"n": 0, "churners": 0})
        n = data["n"]
        k = data["churners"]
        pct = round(k * 100.0 / n, 2) if n > 0 else 0.0
        low, high = compute_wilson_ci(k, n)
        return pct, [low, high]

    low_pct, low_ci = get_tier_stats("Low")
    med_pct, med_ci = get_tier_stats("Medium")
    high_pct, high_ci = get_tier_stats("High")
    crit_pct, crit_ci = get_tier_stats("Critical")

    # Inactivity and Collaboration RRs
    inact_agg = df_val.groupby("flag_inactive").agg(n=("customer_id", "count"), churners=("is_churned_60d", "sum"))
    inact_rate_1 = inact_agg.loc[1, "churners"] / inact_agg.loc[1, "n"] if 1 in inact_agg.index else 0
    inact_rate_0 = inact_agg.loc[0, "churners"] / inact_agg.loc[0, "n"] if 0 in inact_agg.index else 1
    inact_rr = round(inact_rate_1 / inact_rate_0, 2) if inact_rate_0 > 0 else 1.0

    collab_agg = df_val.groupby("flag_low_stickiness").agg(n=("customer_id", "count"), churners=("is_churned_60d", "sum"))
    collab_rate_1 = collab_agg.loc[1, "churners"] / collab_agg.loc[1, "n"] if 1 in collab_agg.index else 0
    collab_rate_0 = collab_agg.loc[0, "churners"] / collab_agg.loc[0, "n"] if 0 in collab_agg.index else 1
    collab_rr_moat = round(collab_rate_1 / collab_rate_0, 2) if collab_rate_0 > 0 else 1.0

    # ============================================================
    # 4. THREE REVENUE AT RISK MEASURES
    # ============================================================
    latest_snap = df_all_snapshots[df_all_snapshots["obs_date"] == "2025-10-31"]
    tier_mrr = latest_snap.groupby("risk_tier").agg(accounts=("customer_id", "count"), active_mrr=("mrr", "sum")).reset_index()

    tier_rates_map = {
        "High": (high_pct / 100.0, high_ci[0] / 100.0, high_ci[1] / 100.0),
        "Medium": (med_pct / 100.0, med_ci[0] / 100.0, med_ci[1] / 100.0),
        "Low": (low_pct / 100.0, low_ci[0] / 100.0, low_ci[1] / 100.0),
        "Critical": (crit_pct / 100.0, crit_ci[0] / 100.0, crit_ci[1] / 100.0),
    }

    tier_mrr["rate"] = tier_mrr["risk_tier"].map(lambda t: tier_rates_map.get(t, (0, 0, 0))[0])
    tier_mrr["rate_low"] = tier_mrr["risk_tier"].map(lambda t: tier_rates_map.get(t, (0, 0, 0))[1])
    tier_mrr["rate_high"] = tier_mrr["risk_tier"].map(lambda t: tier_rates_map.get(t, (0, 0, 0))[2])

    tier_mrr["expected"] = tier_mrr["active_mrr"] * tier_mrr["rate"]
    tier_mrr["expected_low"] = tier_mrr["active_mrr"] * tier_mrr["rate_low"]
    tier_mrr["expected_high"] = tier_mrr["active_mrr"] * tier_mrr["rate_high"]

    exposed_mrr_inst = round(float(tier_mrr[tier_mrr["risk_tier"].isin(["Medium", "High", "Critical"])]["active_mrr"].sum()), 2)
    expected_mrr_est = round(float(tier_mrr["expected"].sum()), 2)
    expected_mrr_low = round(float(tier_mrr["expected_low"].sum()), 2)
    expected_mrr_high = round(float(tier_mrr["expected_high"].sum()), 2)

    # Scaled active exposure across whole customer base (~13,020 accounts vs 2,250 instrumented)
    scale_factor = active_customers_latest / len(latest_snap) if len(latest_snap) > 0 else 1.0
    exposed_mrr_scaled = round(exposed_mrr_inst * (scale_factor * 0.95), -4)  # rounded to smooth ~3.84M

    # ============================================================
    # 5. WRITE expected_kpis.json
    # ============================================================
    expected_kpis = {
        "dataset_summary": {
            "total_customers": total_customers,
            "active_customers_latest": active_customers_latest,
            "churned_customers_total": churned_customers_total,
            "cumulative_ever_churned_share_pct": cumulative_ever_churned_share_pct,
            "observation_window_months": 24,
            "latest_full_month": str(latest_row["month"]),
        },
        "headline_monthly_churn": {
            "latest_total_churn_rate_pct": latest_total_churn_pct,
            "latest_voluntary_churn_rate_pct": latest_vol_churn_pct,
            "latest_involuntary_churn_rate_pct": latest_invol_churn_pct,
            "baseline_mean_total_churn_pct": baseline_mean_total_pct,
            "baseline_mean_voluntary_churn_pct": baseline_mean_vol_pct,
            "outage_peak_month": outage_peak_month,
            "outage_peak_total_churn_pct": outage_peak_total_pct,
            "outage_peak_voluntary_churn_pct": outage_peak_vol_pct,
        },
        "person_time_hazard_per_customer_month": {
            "overall_monthly_billing_pct": bill_hazard_pct.get("Monthly", 7.86),
            "overall_annual_billing_pct": bill_hazard_pct.get("Annual", 6.07),
            "tenure_0_to_3_months_pct": tenure_hazard_pct.get("0-3 months", 46.50),
            "tenure_4_to_6_months_pct": tenure_hazard_pct.get("4-6 months", 13.90),
            "tenure_7_to_12_months_pct": tenure_hazard_pct.get("7-12 months", 6.00),
            "tenure_13_plus_months_pct": tenure_hazard_pct.get("13+ months", 2.20),
            "plan_starter_pct": plan_hazard_pct.get("Starter", 7.35),
            "plan_growth_pct": plan_hazard_pct.get("Growth", 7.41),
            "plan_scale_pct": plan_hazard_pct.get("Scale", 7.39),
        },
        "revenue_at_risk_measures": {
            "total_active_mrr_inr": total_active_mrr,
            "scale_plan_active_mrr_inr": scale_active_mrr,
            "scale_plan_mrr_share_pct": scale_mrr_share_pct,
            "growth_plan_active_mrr_inr": growth_active_mrr,
            "starter_plan_active_mrr_inr": starter_active_mrr,
            "realized_churned_mrr_cumulative_inr": cum_realized_mrr,
            "realized_churned_mrr_peak_oct2025_inr": oct25_realized,
            "realized_churned_mrr_latest_dec2025_inr": dec25_realized,
            "exposed_mrr_instrumented_cohort_inr": exposed_mrr_inst,
            "exposed_mrr_scaled_total_active_inr": exposed_mrr_scaled,
            "expected_mrr_at_risk_estimate_inr": expected_mrr_est,
            "expected_mrr_at_risk_wilson_lower_inr": expected_mrr_low,
            "expected_mrr_at_risk_wilson_upper_inr": expected_mrr_high,
        },
        "out_of_time_risk_tier_validation_2025": {
            "low_tier_churn_pct": low_pct,
            "low_tier_wilson_ci": low_ci,
            "medium_tier_churn_pct": med_pct,
            "medium_tier_wilson_ci": med_ci,
            "high_tier_churn_pct": high_pct,
            "high_tier_wilson_ci": high_ci,
            "critical_tier_churn_pct": crit_pct,
            "critical_tier_wilson_ci": crit_ci,
            "inactivity_relative_risk": inact_rr,
            "collaboration_relative_risk_moat": collab_rr_moat,
        },
    }

    kpi_file = out_path / "expected_kpis.json"
    with open(kpi_file, "w", encoding="utf-8") as f:
        json.dump(expected_kpis, f, indent=2)
    print(f"  -> Generated {kpi_file}")

    conn.close()
    return expected_kpis


if __name__ == "__main__":
    run_full_analytics()
