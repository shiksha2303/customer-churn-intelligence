# Stage 0 Learning Concepts

## Concepts Used

1. **Synthetic vs. Real Data:** 
   - *Why we chose it:* We couldn't find a real public dataset that met all our requirements (churn label, time dimension, revenue, acquisition channel, voluntary/involuntary split). Building a synthetic dataset gives us complete control over the realism and allows us to rigorously test our analytical methods. We can plant effects and then see if our analysis recovers them (this is called "synthetic validation").
   - *Interview angle:* In an interview, you can explain that while real data is messy, synthetic data allowed you to design specific complexities (like Simpson's paradox or censored data) to demonstrate advanced analytical techniques that simple public datasets wouldn't support.

2. **Deterministic Generation (Seeding):**
   - *What it is:* Using a fixed number (the "seed", like 42) to initialize a random number generator. 
   - *Why we chose it:* It ensures that every time we run the generator, it produces the exact same dataset. This is crucial for reproducibility—if you run the code, you should get the exact same charts and numbers as me.

3. **Environment Pinning:**
   - *What it is:* Specifying exact versions in `requirements.txt` (e.g., `pandas==2.2.2`).
   - *Why we chose it:* Code that works today might break tomorrow if a library updates and changes a function name. Pinning guarantees the code runs reliably in the future.

4. **Cross-Sectional vs. Time-Series (Longitudinal) Data:**
   - *What it is:* Cross-sectional data is a snapshot at one point in time (like the famous Telco churn dataset). Time-series or longitudinal data tracks events over time.
   - *Why we chose it:* You cannot answer "Is churn increasing?" (Q2) or "Does inactivity predict churn?" (Q6) with cross-sectional data. We explicitly require a time dimension to do cohort analysis and leading-indicator analysis.

## Avoiding Beginner Shortcuts

- **Shortcut avoided:** Just downloading the IBM Telco Churn dataset from Kaggle.
- **Why we avoided it:** It's too common (recruiters see it hundreds of times), and it lacks the time dimension needed to show off advanced skills like cohort analysis and window functions in SQL. 
- **Shortcut avoided:** Using an `.ipynb` for everything.
- **Why we avoided it:** We structured the project with proper Python scripts (`src/`, `run_pipeline.py`) and explicit SQL files. Notebooks are used *only* for EDA and visualization, which reflects professional engineering standards better than a single massive notebook.

## Exercises for You

1. Open `run_pipeline.py` and change the `--seed` argument's default value to something else (e.g., `123`). Run `python run_pipeline.py --help` to see how the command-line arguments are structured using `argparse`. 
2. Review the 4 candidates in `docs/dataset_decision.md`. Try to articulate in your own words why Candidate A (Telco churn) fails to support Q2 (trend) and Q6 (leading indicators).
