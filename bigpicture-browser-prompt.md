# Claude Browser Prompt — Configure BigPicture (Layer B) for the PMO Demo

**What this is.** A ready-to-paste prompt for a **Claude agent with browser / computer-use** capability to configure the **BigPicture (Appfire)** app in di-demo for the PMO demo. BigPicture is app-internal (not configurable via the Admin MCP), so it must be driven through the UI. Grounded in current Appfire BigPicture docs (June 2026).

**How to use.** Open a Claude session that can drive a browser; ensure it's signed in to `di-demo.atlassian.net` as a Jira admin with **BigPicture App Admin** (and **App Financial Admin** for Financials); paste the prompt below.

> Companion to the Configuration Guide **Layer B (B1–B7)** and the PMO demo data already built in Jira (project **PMOD**).

---

```
You are operating a web browser (computer use). Configure the BigPicture (Appfire) app in Jira
for the PMO demo, exactly as specified. BigPicture is app-internal — it cannot be configured by
API, so you must drive the UI. Work module by module and verify as you go.

== ENVIRONMENT AND SAFETY ==
- Target: https://di-demo.atlassian.net  — the DI demo sandbox ONLY. Sign in must have Jira admin
  + BigPicture App Admin (and App Financial Admin for the Financials module).
- BigPicture Enterprise edition is required for Financials / Risks / Resources / OKR. If the app
  isn't installed or those modules aren't available, STOP and report.
- Only create the demo Boxes named below. Do NOT modify or delete existing Boxes, other apps'
  data, or any other project. Confirm you are on di-demo before any change.

== DATA ALREADY IN JIRA (project PMOD) ==
- Four demo "projects" are Jira issues of type Project, each tagged with a label:
  ERP (PMOD-1), CloudMigration (PMOD-2), CustomerPortal (PMOD-3), PayrollAutomation (PMOD-4).
- Milestones (type Milestone) carry the project label + "critical" on key ones.
- Risks (type Risk) have Likelihood (customfield_11330, 1-Rare…5-Almost Certain),
  Consequence (customfield_11865, 1…5), Inherent Rating, Residual Rating, Risk Category;
  two risks are labelled Escalated.
- Project records carry Budget (customfield_11673), Forecast at Completion/FAC (customfield_11850),
  Variance, Overall RAG, Financial RAG, Target Go-Live.
- Enhancements + 1 defect exist; Sprint 1 (closed) + Sprint 2 (active) on board
  "PMO Demo — Enhancement Board".

== GOAL ==
Stand up a portfolio with Gantt, Risks, Resources, Financials, OKR and Overview so the demo can
show portfolio health from one surface.

== B1 — Boxes & hierarchy ==
1. Open BigPicture (top nav → Apps → BigPicture).
2. Keep the Home box. Create a Portfolio-type Box named "Enterprise PMO Portfolio".
3. Under it, create four Project-type child boxes: "ERP Platform Upgrade", "Cloud Migration",
   "Customer Portal", "Payroll Automation".
4. Set each box's Scope by JQL to pull that project's issues, e.g. for ERP:
        project = PMOD AND labels = ERP
   (repeat with CloudMigration / CustomerPortal / PayrollAutomation). Verify each box lists issues.

== B2 — Gantt (per project box) ==
1. Open a project box → Gantt module; confirm tasks + milestones show.
2. Mark the key milestones as Critical (the ones labelled "critical").
3. Create a baseline: Data → Baselines → New baseline. Then change a forecast date to show slip
   against the locked baseline.
4. Create a dependency between two tasks (drag from one taskbar to the next, or right-click →
   dependency). Show the auto-shift and the critical path.

== B3 — Risks ==
1. App configuration → Modules → Risks. Map matrix fields: Probability = Likelihood
   (customfield_11330); Consequence = Consequence (customfield_11865). Keep the 5×5 matrix and
   enable Heatmap mode.
2. Open the portfolio → Risks module; confirm the 6 PMOD risks appear on the matrix (they have
   Likelihood + Consequence set). Confirm the 2 Escalated risks surface.
3. Show inherent vs residual rating (residual lower after mitigation).

== B4 — Resources ==
1. Resources module → define 2–3 Teams; add resources (people); assign hourly rates (also used by
   Financials).
2. Enter allocations (role/person, % or hours, dates) on the demo projects.
3. Show capacity vs demand and an overallocation flag.

== B5 — Financials (Enterprise; App Financial Admin) ==
1. Assign hourly rates. Set a Budget per project box using the Jira Budget values:
   ERP 2,500,000 · Cloud 1,800,000 · Customer Portal 1,200,000 · Payroll 600,000.
2. Let estimated/actual cost calculate from effort × rates; show budget vs estimated/actual and
   variance at project AND portfolio level.
3. Talk track: CapEx categorisation lives in the CapEx system of record; the CapEx Reference field
   links execution back to it.

== B6 — OKR ==
1. Create 1–2 strategic Objectives (e.g., "Modernise core platforms", "Improve customer experience").
2. Link the demo projects/initiatives to them to show strategic value alignment.

== B7 — Overview & Reports ==
1. Configure Overview columns: Overall RAG, next critical milestone, budget health, top risk.
2. Build a Reports view for status/trend (note: trends rely on historical snapshots over time).

== VERIFY ==
- Overview shows the 4 projects with RAG, milestones, budget health, top risk.
- A project Gantt shows baseline vs forecast slip + a dependency.
- Risks matrix shows the 6 risks with the escalated ones flagged.
- Financials shows variance at project + portfolio.

== REPORT ==
List what you created (boxes, baselines, dependencies, risk field-mapping, teams/rates, budgets,
objectives, overview columns), the verification results, anything the installed BigPicture edition
did NOT support (e.g., a missing module = not Enterprise), and any UI deviations from these steps.
```

---

## References (Appfire BigPicture docs, current)

- [Getting started with BigPicture](https://appfire.atlassian.net/wiki/spaces/DLP/pages/297670134/Getting+Started)
- [Gantt module](https://appfire.atlassian.net/wiki/spaces/DLP/pages/297766176/Gantt+module) · [Task dependencies](https://appfire.atlassian.net/wiki/spaces/DLP/pages/297540440)
- [Risks module](https://appfire.atlassian.net/wiki/spaces/DLP/pages/296981188/Risks+module) · [Risks matrix report](https://appfire.atlassian.net/wiki/spaces/DLP/pages/298224738/Risks+matrix+report)
- [BigPicture Enterprise features](https://appfire.atlassian.net/wiki/spaces/DLP/pages/298092765)

> Layers B (BigPicture) and C (Xray) are app-internal and must be configured in-app — this prompt drives that. Field IDs reflect the objects built in di-demo on 2026-06-19.
