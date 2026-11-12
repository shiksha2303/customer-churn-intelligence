# Stage 5 Learning Concepts

## Concepts Used

1. **Multidimensional Customer Segmentation:**
   - *What it is:* Slicing customer retention behavior across multiple demographic and contract dimensions: Plan Tier (Starter, Growth, Scale), Billing Frequency (Monthly vs. Annual), Company Size, and City Tier.
   - *Why we chose it:* Aggregate churn hides structural vulnerabilities. By isolating segments, we discovered that Annual contracts exhibit significantly lower churn than Monthly contracts (the "Commitment Effect", ~49.4% vs ~59.1%), while entry-level Starter tiers experience the highest customer turnover.
   - *Interview angle:* In SaaS analytics, always check for the "Annual Discount Effect." Annual billing reduces decision friction from 12 moments of renewal per year down to 1, drastically dampening churn.

2. **Confounding Variables and Simpson's Paradox:**
   - *What it is:* When an observed relationship between two variables (e.g., acquisition channel and churn) is distorted or driven by a third underlying confounding variable (e.g., plan selection).
   - *Why we chose it:* App Store showed the highest churn rate among all channels (~58.9%). However, when stratifying by plan tier, we found App Store predominantly acquires Starter plan users. When controlling for plan type, channel differences narrow significantly.
   - *Interview angle:* Highlighting confounding shows senior analytical maturity. Junior analysts report "App Store is a bad channel; turn it off." Senior analysts ask: "Is App Store underperforming because of the channel audience, or because it acquires self-serve Starter users with lower product commitment?"

3. **Wilson Score Confidence Intervals for Proportions:**
   - *What it is:* An asymmetric binomial proportion confidence interval that provides reliable bounds even with moderate sample sizes or extreme proportions, avoiding the fatal flaws of normal approximation (Wald) intervals.
   - *How we used it:* Evaluated whether observed churn differences across channels and segments were statistically meaningful or mere random sampling variation.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Drawing causal conclusions from raw channel churn rankings.
- **Why we avoided it:** Correlation does not imply causation. Without stratifying across plan tier and company size, raw rankings mislead marketing spend allocation.
