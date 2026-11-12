# Stage 1 Learning Concepts

## Concepts Used

1. **Synthetic Data Generation for Hypothesis Testing:**
   - *What it is:* Instead of using real data, we simulate it using logic that dictates how variables relate (e.g., if a user is inactive, multiply their churn probability by 3).
   - *Why we chose it:* It allows us to prove our analytical rigor. If we plant a specific effect (like inactivity driving churn) and our SQL/EDA later uncovers it perfectly, it proves our analytical method is sound. If we also plant a "red herring" (like city tier having zero effect) and our analysis correctly ignores it, it proves our method doesn't generate false positives.

2. **Simpson's Paradox (Planted Confounder):**
   - *What it is:* A statistical phenomenon where a trend appears in several different groups of data but disappears or reverses when these groups are combined.
   - *How we built it:* We designed the "App Store" channel to look like it has a high churn rate. However, the *real* reason is that App Store users overwhelmingly pick the "Starter" plan (which has naturally higher churn). The channel itself isn't bad; it's just acquiring a riskier demographic.
   - *Interview angle:* When an interviewer asks "How do you ensure you aren't just finding spurious correlations?", you can explain that you always stratify your results (e.g., check channel churn *within* each plan tier) to catch confounders like Simpson's paradox.

3. **Involuntary vs. Voluntary Churn:**
   - *What it is:* Voluntary churn is when a user clicks "cancel." Involuntary churn is when their credit card fails and the account is closed for non-payment.
   - *Why it matters:* They require entirely different business solutions. You fix voluntary churn by improving the product (Product/Success teams). You fix involuntary churn by implementing better dunning emails or card-updater systems (Billing/Ops teams). Mixing them up in your analysis will destroy the predictive power of behavioral indicators.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Using the `random` module without a seed.
- **Why we avoided it:** Random data that changes on every run makes a portfolio project impossible to verify. If a recruiter pulls your repo and runs it, they need to see the exact numbers you quoted in your README.
- **Shortcut avoided:** Making churn too easy to predict.
- **Why we avoided it:** If every churned user had 0 sessions and every retained user had 100 sessions, the analysis would be trivial and unrealistic. We used base probabilities and multiplied hazards to ensure the data is noisy and realistic.

## Exercises for You

1. Open `docs/data_dictionary.md` and familiarize yourself with the schema. Which tables will you need to join to answer "Does product usage affect churn?" (Q5)?
2. Look at `synthetic_data/generator.py` (specifically the section where `base_hazard` is modified). Can you identify one factor that *increases* churn risk and one that *decreases* it?
3. (Optional) Run `python run_pipeline.py --stage 1 --seed 99` and check the file sizes again. They will be slightly different because a different seed generates a different alternate reality. (Be sure to run it with `--seed 42` again afterward to reset your data for the project!)
