"""
src/build_preview.py
====================
Compiles outputs/preview.html embedding all analytical figures from outputs/figures/
with descriptive captions, takeaway summaries, and methodology notes.
"""

import base64
from pathlib import Path


def build_preview(figures_dir="outputs/figures", output_file="outputs/preview.html"):
    fig_path = Path(figures_dir)
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Dictionary of captions and takeaways for each generated figure
    figure_metadata = {
        "02_monthly_churn_trend.png": {
            "title": "Figure 1: Monthly Churn Trend (Jan 2024 – Dec 2025)",
            "takeaway": "Baseline voluntary churn averages 5.52%. An acute spike to 11.18% occurred in October 2025 following a major infrastructure outage, recovering within 60 days.",
            "finding": "F001 & F002 (Q1 & Q2)"
        },
        "03_churn_by_plan.png": {
            "title": "Figure 2: Lifetime Churn Rate by Plan Tier",
            "takeaway": "Raw cumulative churn rates are virtually identical across tiers (Starter: 56.70%, Scale: 56.71%, Growth: 56.38%). Underlying hazard is ~7.4% per customer-month.",
            "finding": "F005 (Q3)"
        },
        "03_churn_by_channel.png": {
            "title": "Figure 3: Raw Acquisition Channel Churn Ranking",
            "takeaway": "App Store shows the highest raw churn (58.86%), but cross-stratification reveals this is confounded by an 82.1% Starter plan concentration.",
            "finding": "F009 (Q7)"
        },
        "03_churn_segments.png": {
            "title": "Figure 4: Multidimensional Customer Segmentation",
            "takeaway": "Annual billing contracts show substantially lower churn hazard across all company sizes and city tiers (commitment effect).",
            "finding": "F006 (Q3)"
        },
        "03_confound_channel_x_plan.png": {
            "title": "Figure 5: Channel by Plan Stratification (Simpson's Paradox)",
            "takeaway": "Controlling for plan tier eliminates channel variation (7.0%–8.1% per customer-month), proving App Store traffic is not intrinsically defective.",
            "finding": "F009 (Q7)"
        },
        "04_churn_by_tenure_bucket.png": {
            "title": "Figure 6: Churn Hazard by Tenure Bucket",
            "takeaway": "Steep early mortality cliff: Month 0–3 hazard is ~46% per customer-month, dropping 20x to ~2% beyond Month 13.",
            "finding": "F003 & F004 (Q4)"
        },
        "04_cohort_retention_heatmap.png": {
            "title": "Figure 7: Triangular Cohort Retention Matrix Heatmap",
            "takeaway": "Tracks 24 monthly cohorts across M1–M12. Average 6-month retention is 69.3%. Blank cells indicate unobserved future calendar months.",
            "finding": "F003 (Q3)"
        },
        "05_avg_usage_churned_vs_retained.png": {
            "title": "Figure 8: Average Weekly Usage: Churned vs Retained Accounts",
            "takeaway": "Accounts that eventually cancel show early session velocity decay and engagement drop-off 30 to 60 days prior to formal cancellation.",
            "finding": "F007 (Q6)"
        },
        "05_inactivity_churn.png": {
            "title": "Figure 9: Inactivity Signal & Prospective Churn Risk",
            "takeaway": "Zero sessions in 30 days is associated with an 89.47% churn rate vs 14.05% for active users (RR = 6.37x). Flagged for n=95 sample size.",
            "finding": "F007 (Q6)"
        },
        "05_feature_use_churn.png": {
            "title": "Figure 10: Multi-User Collaboration Adoption Moat",
            "takeaway": "Adopting team collaboration features is associated with half the churn hazard (12.37% vs 24.67%, RR = 1.99x; n=18,242 vs 3,563).",
            "finding": "F008 (Q5)"
        },
        "06_leading_indicators.png": {
            "title": "Figure 11: Prospective Leading Indicator Relative Risk Ranking",
            "takeaway": "Rank ordering of early behavioral warning signals evaluated out-of-time across 22 monthly rolling snapshots.",
            "finding": "F010 & F012 (Q10)"
        },
        "07_risk_tier_validation.png": {
            "title": "Figure 12: Rule-Based Risk Framework Monotonicity Validation",
            "takeaway": "Prospective validation shows strict monotonic risk escalation: Low (12.41%) -> Medium (22.28%) -> High (68.46%) -> Critical (100.0%).",
            "finding": "F012 (Q11)"
        },
        "07_revenue_at_risk_by_tier.png": {
            "title": "Figure 13: Exposed MRR by Risk Tier",
            "takeaway": "Exposed active revenue is concentrated in Medium and High risk accounts, providing operational routing for customer success teams.",
            "finding": "F011 (Q9)"
        },
        "08_mrr_by_plan.png": {
            "title": "Figure 14: Active MRR Concentration by Plan Tier",
            "takeaway": "Scale accounts concentrate 41.2% of active MRR (INR 6.55M) despite comprising only 13.3% of active customer volume.",
            "finding": "F010 (Q8)"
        },
        "08_realised_churned_mrr_over_time.png": {
            "title": "Figure 15: Realized Churned MRR Losses Over Time",
            "takeaway": "Cumulative INR 21.00M in recurring revenue permanently lost, with acute spikes during the infrastructure outage period.",
            "finding": "F011 (Q9)"
        },
        "08_revenue_at_risk_three_measures.png": {
            "title": "Figure 16: Three Distinct Measures of Revenue at Risk",
            "takeaway": "Distinguishes Realized historical losses (INR 21.00M), Exposed portfolio MRR (INR 520K inst. / INR 3.84M tot.), and Expected loss (INR 411,712 with Wilson CI).",
            "finding": "F011 (Q9)"
        }
    }

    # Find all PNG files
    png_files = sorted([f for f in fig_path.glob("*.png")])

    cards_html = []
    for f in png_files:
        meta = figure_metadata.get(f.name, {
            "title": f.name.replace("_", " ").replace(".png", "").title(),
            "takeaway": "Empirical analytical figure generated by Jupyter EDA notebooks.",
            "finding": "Analytical Finding"
        })

        # Read image and convert to base64 for 100% self-contained embedding
        with open(f, "rb") as img_f:
            b64_str = base64.b64encode(img_f.read()).decode("utf-8")

        cards_html.append(f"""
        <div class="figure-card">
          <div class="card-header">
            <span class="finding-badge">{meta['finding']}</span>
            <h3>{meta['title']}</h3>
          </div>
          <div class="image-wrapper">
            <img src="data:image/png;base64,{b64_str}" alt="{meta['title']}" loading="lazy">
          </div>
          <div class="card-caption">
            <p><strong>Core Takeaway:</strong> {meta['takeaway']}</p>
          </div>
        </div>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zorvio Churn Intelligence — Analytical Figures Preview</title>
  <style>
    :root {{
      --bg: #F8FAFC;
      --card-bg: #FFFFFF;
      --text: #0F172A;
      --muted: #475569;
      --primary: #1E3A8A;
      --accent: #0D9488;
      --border: #E2E8F0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 32px 24px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ margin-bottom: 32px; border-bottom: 2px solid var(--border); padding-bottom: 20px; }}
    header h1 {{ font-size: 2rem; color: var(--primary); font-weight: 800; letter-spacing: -0.5px; }}
    header p {{ color: var(--muted); margin-top: 6px; font-size: 0.95rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(520px, 1fr)); gap: 24px; }}
    .figure-card {{
      background: var(--card-bg);
      border-radius: 12px;
      border: 1px solid var(--border);
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.03);
      display: flex;
      flex-direction: column;
    }}
    .card-header {{ padding: 16px 20px; border-bottom: 1px solid var(--border); }}
    .finding-badge {{
      display: inline-block;
      background: #EFF6FF;
      color: var(--primary);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
    }}
    .card-header h3 {{ font-size: 1.1rem; color: var(--text); }}
    .image-wrapper {{ padding: 16px; background: #FFF; display: flex; justify-content: center; align-items: center; }}
    .image-wrapper img {{ max-width: 100%; height: auto; border-radius: 6px; border: 1px solid var(--border); }}
    .card-caption {{ padding: 16px 20px; background: var(--bg); border-top: 1px solid var(--border); font-size: 0.85rem; line-height: 1.5; color: var(--muted); }}
    .card-caption strong {{ color: var(--text); }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Zorvio Analytical Figures & Visual Gallery</h1>
      <p>All 16 empirical charts generated by the exploratory data analysis notebooks (<code>outputs/figures/</code>), self-contained with takeaways and findings traceability.</p>
    </header>
    <div class="grid">
      {"".join(cards_html)}
    </div>
  </div>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    size_kb = out_path.stat().st_size / 1024
    print(f"  -> Generated {out_path} ({size_kb:.1f} KB, self-contained embedded preview)")
    return out_path


if __name__ == "__main__":
    build_preview()
