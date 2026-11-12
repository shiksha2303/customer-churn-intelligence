# Stage 6 Learning Concepts

## Concepts Used

1. **Fixed Prospective Observation Windows (Leakage Prevention - DEC-015):**
   - *What it is:* A rigorous temporal evaluation design where a single historical observation cutoff (e.g., `2025-11-01`) is chosen. All behavioral features (sessions, actions, support tickets) are extracted strictly from the lookback window *prior* to this cutoff. Churn outcome labels are then evaluated strictly within the prospective forward window (e.g., the subsequent 60 days).
   - *Why we chose it:* The common beginner approach anchors the lookback window on each customer's own cancellation date. This causes catastrophic temporal data leakage: looking at activity right before someone clicks "Cancel" only captures the consequence of their decision, not an early warning signal. Fixed windows mirror real-world operational forecasting.
   - *Interview angle:* Discussing prospective vs. retrospective feature windows and temporal leakage prevention is one of the clearest differentiators between self-taught beginners and production-ready analysts.

2. **Relative Risk (RR) and Risk Ratios:**
   - *What it is:* The probability of an event (churn) occurring in an exposed group divided by the probability of the event occurring in an unexposed group: $RR = \frac{P(\text{churn} \mid \text{Inactive})}{P(\text{churn} \mid \text{Active})}$.
   - *Why we chose it:* Relative risk quantifies signal strength in an interpretable, non-parametric metric. Showing that inactive users have a $6.88\times$ higher likelihood of churning than active users gives leadership an actionable threshold for intervention.

3. **Product Stickiness & Multi-User Collaboration Moat:**
   - *What it is:* Identifying high-leverage product interactions that correlate with long-term retention. 
   - *How we used it:* Customers utilizing collaboration features had a churn rate of only ~10.9% versus ~28.0% for non-users (over a $2.5\times$ retention moat). This isolates product onboarding targets for the product management and customer success teams.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Including post-churn or event-day activity in feature aggregations.
- **Why we avoided it:** Including events that occur after or during cancellation creates artificial model accuracy that collapses in production.
- **Shortcut avoided:** Confusing correlational feature usage with guaranteed causality without experimental verification.
