# Zorvio Churn Playbook: Evidence-Based Retention Strategy

**Deliverable Focus:** Operational Retention Plays for Customer Success, Product, Billing, and Growth Teams  
**Grounding:** Traced directly to [`outputs/findings_register.csv`](../outputs/findings_register.csv) and out-of-time monthly snapshot validation.

> ⚠️ **SYNTHETIC DATA NOTICE:** All data describes simulated SaaS company Zorvio.

---

## 1. Executive Summary & Evidence Classification

Every operational play is strictly classified based on our statistical sample size floor ($n \ge 200, \text{events} \ge 30$):
- **Core Proven Plays (High Evidence Bar):** Grounded in large-sample empirical findings meeting the sample floor (Annual billing tenure hazard, Collaboration feature stickiness moat, Revenue concentration).
- **Hypotheses to Test (Directional / Emerging Evidence):** Grounded in strong directional signals where sample sizes are below the 200-account floor (Inactivity leading indicators with $n=95$, Support friction with $n < 200$). These are framed as targeted field experiments rather than definitive company-wide rollouts.

---

## 2. Strategic Action Matrix

| Play ID | Play Name | Evidence Tier | Target Segment | Trigger Signal | Owner Team | Primary Target Metric |
|---|---|---|---|---|---|---|
| **PLAY-01** | Scale Account Concierge Intervention | **Hypothesis to Test** | Active Scale Accounts | Inactivity $\ge 14$d OR Open Ticket | Customer Success | Scale 90-day retention |
| **PLAY-02** | Collaboration Onboarding Loop | **Proven Play** | New Signups (Days 1–7) | Zero team invites / shared docs | Product | Day-30 collaboration adoption ($RR=1.99\times$ moat) |
| **PLAY-03** | Rapid Support De-escalation Sprint | **Hypothesis to Test** | All Active Accounts | Open ticket $> 48$h | Customer Support | Ticket submitter 60-day renewal |
| **PLAY-04** | Annual Commitment Upgrade Incentive | **Proven Play** | Monthly Subscribers (Tenure $\ge 3$m) | Reaching Month 3 milestone | Marketing / Billing | Annual conversion (capturing 6.07% vs 7.86% hazard) |
| **PLAY-05** | Mobile Self-Serve Activation Flow | **Proven Play** | Mobile / App Store Signups | Channel = App Store | Growth Product | Starter plan Day-30 activation completion |

---

## 3. Core Proven Plays (High Evidence Bar)

### PLAY-02: Collaboration Onboarding Loop
- **Evidence Base (F008):** In out-of-time monthly validation across 2025, non-collaboration accounts experienced double the churn hazard of collaboration accounts (**24.67% vs 12.37%**, Relative Risk: **1.99x**, $n=3,563$, 879 events; fully meets sample floor).
- **Trigger Signal:** Account created $\ge 5$ days ago with zero team member invitations and zero shared workspaces.
- **Hypothesis:** Prompting users with contextual in-app templates and workflow incentives to invite teammates during the first week will increase collaboration adoption by 25%, moving accounts into the lower-churn cohort.
- **Action Steps:**
  1. Insert an interactive "Invite a Teammate" step in the primary onboarding flow.
  2. Provide pre-built industry workspace templates optimized for team sharing.
  3. Trigger automated Day-5 email illustrating time saved via multi-user workflows.
- **Primary Metric:** % of accounts adopting collaboration features by Day 30 (Baseline: ~16% $\rightarrow$ Target: 30%).
- **Counter-Metric:** First-session completion rate (ensure prompt does not introduce onboarding drop-off).
- **A/B Test Design:** 50/50 randomized in-app test across 2,000 new signups.

---

### PLAY-04: Annual Commitment Upgrade Incentive
- **Evidence Base (F006):** Annual contracts exhibit lower churn hazard per customer-month across every tenure band (0–3m: 45.0% vs 47.1%; 4–6m: 12.2% vs 14.6%; 7–12m: 4.9% vs 6.5%; 13+m: 1.9% vs 2.3%; overall 6.07% vs 7.86%, $n=30,000$).
- **Trigger Signal:** Monthly billing account reaching Month 3 of active tenure.
- **Hypothesis:** Offering an annual commitment discount (2 months free upon annual renewal) at Month 3 when early mortality subsides will capture a 12% conversion rate and lock in lower long-term attrition.
- **Action Steps:**
  1. Deploy an automated in-app banner and email offer at Day 75: "Upgrade to Annual and save ₹998–₹7,998."
  2. Highlight uninterrupted workflow and corporate invoice billing.
- **Primary Metric:** Monthly-to-annual upgrade conversion rate (Target: 12%).
- **Counter-Metric:** Net blended MRR impact (discount must not dilute overall revenue).
- **A/B Test Design:** Randomized rollout across 1,000 eligible monthly accounts.

---

### PLAY-05: Mobile Self-Serve Activation Flow
- **Evidence Base (F009):** Stratified hazard analysis confirms App Store churn per customer-month is uniform with other channels (7.74% Starter, 8.15% Growth, 7.84% Scale). The elevated raw churn is driven by 82.1% Starter plan concentration rather than channel defect.
- **Trigger Signal:** Signup originating from App Store channel on mobile device.
- **Hypothesis:** Guiding mobile Starter signups into complete account setup and desktop pairing will increase early activation and mitigate early tenure mortality.
- **Action Steps:**
  1. Introduce a "Continue on Desktop" prompt immediately following mobile signup.
  2. Provide quick-start mobile templates for standalone solo users.
- **Primary Metric:** Starter mobile 30-day retention rate.
- **Counter-Metric:** Mobile registration completion rate.
- **A/B Test Design:** Split-test mobile onboarding experience across 1,500 new mobile signups.

---

## 4. Hypotheses to Test (Directional / Emerging Evidence)

### PLAY-01: Scale Account Concierge Intervention
- **Evidence Base & Context (F007 & F010):** Scale accounts concentrate **41.2% of active MRR (₹6.55M)** across 1,735 accounts ($F010$, proven). 30-day inactivity exhibits an **89.47% churn rate vs 14.05%** ($RR=6.37\times$, $F007$). However, evaluated inactive accounts ($n=95$) fall below the 200-account floor.
- **Classification:** **Hypothesis to Test**. Due to massive unit financial impact (losing 1 Scale = losing 8 Starter accounts), directionally strong signals warrant proactive testing despite sample size limits.
- **Trigger Signal:** Active Scale plan customer recording zero sessions over the last 14 days OR having an open support ticket.
- **Hypothesis:** Direct telephone and concierge outreach by dedicated Customer Success Managers within 14 days of inactivity will re-engage 20% of at-risk Scale accounts before the 30-day cancellation cliff.
- **Action Steps:**
  1. Feed daily alerts from `fact_high_risk_active` directly to Customer Success CRM.
  2. Assign dedicated CSM to initiate outreach within 24 hours.
  3. Offer personalized executive audit and workflow configuration support.
- **Primary Metric:** Scale plan 60-day renewal rate in outreach cohort vs control.
- **Counter-Metric:** CSM intervention cost per retained account $< 3\times$ monthly MRR ($< ₹11,997$).
- **A/B Test Design:** 50/50 randomized holdout on high-risk Scale accounts over 60 days.

---

### PLAY-03: Rapid Support De-escalation Sprint
- **Evidence Base & Context (F012):** Unresolved open tickets contribute to composite High risk ($68.46\%$ churn, $F012$). However, isolated ticket cohorts with open status have small sample sizes ($n < 200$).
- **Classification:** **Hypothesis to Test**.
- **Trigger Signal:** Active account with any support ticket open $> 48$ hours.
- **Hypothesis:** Escalating tickets open $> 48$h to tier-2 engineering with dedicated SLA guarantees will reduce ticket-related churn by 20%.
- **Action Steps:**
  1. Implement automated SLA monitoring in Zendesk/Freshdesk flagging tickets reaching 48h.
  2. Escalate directly to on-call engineering lead.
- **Primary Metric:** 60-day renewal rate of escalated ticket submitters.
- **Counter-Metric:** CSAT resolution score $> 4.2 / 5.0$.
- **A/B Test Design:** Stepped-wedge phased rollout across support queues over 8 weeks.
