# ⚠️ GENERATOR SPECIFICATION (GROUND TRUTH) ⚠️

> **DO NOT READ UNTIL STAGE 6.**
> This file contains the true, planted effects in the synthetic dataset.

## Simulation Parameters
- **Timeframe:** Jan 1, 2024 to Dec 31, 2025 (24 months)
- **Total Customers:** ~30,000
- **Overall Target Churn Rate:** ~5-8% monthly

## 1. Planted Churn Drivers (Real Effects)
These variables genuinely increase or decrease the probability of voluntary churn:

1. **Inactivity (Strongest Signal):** Customers with zero sessions in the last 14 days have a 3x higher baseline churn hazard.
2. **Usage Intensity:** Customers using the product < 3 days per week have a 1.5x higher churn hazard.
3. **Feature Adoption (The "Sticky" Feature):** Customers who have used `feature_collaboration` at least once have a 0.6x churn hazard (40% less likely to churn).
4. **Support Ticket Friction:** Customers with an unresolved support ticket in the last 30 days have a 2x higher churn hazard.

## 2. Involuntary Churn (Payment Failures)
Payment failures are a separate mechanism from voluntary churn.
- A failed payment triggers an involuntary churn event if not recovered within 14 days.
- **Card Expiry:** Annual plan customers have a much higher rate of payment failure at renewal due to expired cards, leading to higher involuntary churn spikes at their 12-month mark.

## 3. Confounder (Simpson's Paradox Trap)
- **The Setup:** The "App Store" acquisition channel appears to have a *much higher* overall churn rate than "Organic Search". 
- **The Reality (Confounder):** App Store customers are heavily skewed toward the "Starter" plan and Monthly billing. When you stratify by Plan and Billing Cycle, the "App Store" channel has the *exact same* churn hazard as "Organic Search". The channel itself is not bad; it just acquires a demographic that naturally churns faster.

## 4. Red Herrings (No Effect)
These variables have absolutely zero effect on churn probability, despite sounding like they might:
1. **Company Size / Account Type:** Solo users churn at the exact same rate as 50-person teams (controlling for plan).
2. **City Tier:** Customers in Tier 1 cities churn at the exact same rate as Tier 3.

## 5. Temporal Event (Trend Shift)
- **The Event:** In **September 2025**, Zorvio suffered a major 2-day outage.
- **The Effect:** Voluntary churn hazard temporarily increased by 2.5x for all Monthly plan customers during September and October 2025, before returning to normal in November. (Annual customers couldn't churn immediately, so their effect is muted).
