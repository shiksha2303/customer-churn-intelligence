# Stage 7 Learning Concepts

## Concepts Used

1. **Three Measures of Revenue at Risk:**
   - *Realized Churned MRR:* The actual contract revenue permanently lost when accounts churned in previous periods ($INR\ 73.1M$ over the 24-month horizon). This measures retrospective impact.
   - *Exposed MRR:* The total active MRR associated with accounts currently categorized in elevated risk tiers (High or Critical: $\approx INR\ 3.84M$). This measures the total capital currently in jeopardy.
   - *Estimated / Projected Next-Month Churned MRR:* The statistical expected loss next month calculated by weighting active segment MRR by segment baseline churn probability ($\approx INR\ 9.0M$).
   - *Why we chose it:* In business discussions, people carelessly say "revenue at risk" without defining whether they mean retrospective losses, currently vulnerable accounts, or forward expected loss. Distinguishing these three avoids confusion in executive presentations.
   - *Interview angle:* Always clarify definitions of financial risk. Demonstrating the distinction between realized loss, exposure, and expected loss marks immediate credibility with CFOs and finance teams.

2. **Transparent Rule-Based Risk Scoring vs. Black-Box ML:**
   - *What it is:* Constructing an integer additive risk score (0 to 3) from observable business signals:
     - $+1$ for 30-day inactivity
     - $+1$ for unresolved support ticket friction
     - $+1$ for lack of collaboration feature adoption
   - *Why we chose it:* For Customer Success and Account Management teams, an interpretable score mapped to transparent business triggers is immediately operationalizable. Reps understand *why* an account is flagged and what action to take (e.g., re-engagement outreach or onboarding training), unlike an uninterpretable ML probability.
   - *Monotonicity Validation:* In prospective holdout evaluation, churn probability strictly ascended with risk score: Low (11.1%) $\rightarrow$ Medium (24.5%) $\rightarrow$ High (70.6%), confirming strict rank monotonicity without data snooping.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Confusing volume of churn with revenue loss.
- **Why we avoided it:** Starter plan accounts represent the largest share of churned accounts by raw count, but Scale plan accounts contribute over 41% of active MRR (INR 6.55M). Saving one Scale account is worth more than saving eight Starter accounts. Prioritizing by head-count rather than MRR destroys retention ROI.
