# Power BI Package: Zorvio Churn Intelligence

> **SYNTHETIC DATA NOTICE:** All data is computer-generated for fictional company Zorvio.

This directory contains the complete Power BI delivery artifacts for the **Customer Churn Intelligence** project.

---

## Deliverables in this Directory

| File | Purpose |
|---|---|
| [`build_guide.md`](build_guide.md) | Step-by-step tutorial for building the 5-page dashboard in Power BI Desktop. |
| [`data_model.md`](data_model.md) | Star-schema architecture, table dictionary, and relationship cardinalities. |
| [`dax_measures.md`](dax_measures.md) | Complete repository of production-ready DAX formulas with business context. |
| [`wireframes.md`](wireframes.md) | Layout blueprints, visual grids, and component placement for all 5 pages. |
| [`theme.json`](theme.json) | Custom color palette and styling theme file importable directly into Power BI. |

---

## 5-Page Dashboard Architecture

1. **Page 1 — Executive Overview:** High-level KPIs, monthly total & voluntary churn trends, outage anomaly deep-dive.
2. **Page 2 — Segmentation & Cohorts:** Plan tier breakdown, billing cycle commitment effect, cohort retention matrix.
3. **Page 3 — Behavioral Drivers & Indicators:** Inactivity cliff (89.5% vs 14.1%), collaboration stickiness signal (12.4% vs 24.7%), support friction.
4. **Page 4 — Revenue at Risk:** MRR concentration in Scale tier, realized vs projected exposure, customer size impact.
5. **Page 5 — Churn Action Center:** Verified monotonic risk funnel, priority high-risk account queue ready for CS export.
