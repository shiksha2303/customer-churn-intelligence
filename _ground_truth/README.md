# ⚠️ GROUND TRUTH — DO NOT OPEN UNTIL STAGE 6 ⚠️

This folder contains:

1. **`GENERATOR_SPEC.md`** — the complete specification of the synthetic data generator:
   - All planted effects (which variables affect churn, and by how much)
   - Confounders deliberately designed into the data
   - Red herrings (variables with no effect)
   - The one or more time events that shift churn for specific segments
   - Design targets and calibration choices

2. **`injected_issues.json`** — a complete list of every data-quality problem
   deliberately injected into the raw data:
   - Duplicate customer rows
   - Inconsistent capitalisations and spelling variants
   - Missing values
   - Impossible values
   - Orphan records
   - Timestamp format inconsistencies

## Instructions

**Do not read these files before Stage 6.** The purpose of this project is to demonstrate
that the analytical method (Stages 2–5) recovers real effects from data alone,
without peeking at what was planted. This is a learning exercise.

In **Stage 6**, after all findings have been registered, you will open this folder and
compare the analysis findings against the ground truth. The validation report
(`docs/synthetic_validation.md`) will honestly record:
- Which planted effects the analysis recovered ✓
- Which it missed ✗
- Whether it reported spurious findings for the red herrings
- Whether the Simpson's-paradox confounder was handled correctly

**Opening this folder early undermines the entire point of the synthetic validation.**

---

*Files in this folder are created in Stage 1.*
