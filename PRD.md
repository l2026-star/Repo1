# PRD — PMO & PPM Demo (BigPicture + Xray)

**Status:** DRAFT · **Owner:** Thompson Cherian · **Source:** Confluence `SE`
space on `designindustries.atlassian.net` (Overview `1449951252` and children).
**Demo environment:** `https://di-demo.atlassian.net` (demo only — no
cross-writes to production).

> This PRD is a repo-local synthesis of the Confluence spec pages. The Confluence
> **Configuration Guide** remains authoritative for build detail.

## 1. Purpose

Provide a reusable Demo Center asset that proves the Atlassian platform —
**Appfire BigPicture (Enterprise) + Xray, on Jira** — meets an enterprise PMO's
requirements for running projects, enhancements and change in a **hybrid
(Waterfall + Agile)** environment, from a single source of truth. Mapped to the
PMO Tool fit analysis: Project Delivery sections **A–L** and Enhancement
requirements **US-01 to US-28**.

- **Opportunity:** Enterprise PMO tooling RFP (Orora-aligned)
- **Demo type:** Art of the Possible · **Duration:** ~55 min + Q&A

## 2. Audience & lenses

| Lens | Who | What they need to see |
| --- | --- | --- |
| Executive / Sponsor | Steering committee, exec sponsor | Portfolio health at a glance, financial variance, top risks, milestone confidence |
| PMO | PMO lead, PMO admin | Process adherence, governance gates, consistent reporting, configurability |
| Delivery | PMs, delivery leads, test leads | Schedule, RAID, sprint delivery, UAT and defects in one place |

## 3. Positioning (the story in one line)

> "One process, one board, one source of truth — governance that's enforced by
> the tool, not by people remembering steps; lightweight for small enhancements,
> scalable for major projects."

## 4. Solution stack

Lead with **BigPicture**; **Xray** for test management; **Jira** core
underneath; **Rovo** for the AI moments.

| Layer | Product | Modules / capability in the demo |
| --- | --- | --- |
| PPM / PMO | **BigPicture Enterprise** | Overview (portfolio), Gantt (schedule, baselines, dependencies, critical milestones), Risks (configurable matrix), Resources (capacity/allocation), Financials (budget vs estimated/actual, variance), OKR, Reports |
| Test management | **Xray** | UAT cycles (Test Plan), test cases + evidence, defects from failed tests, traceability/coverage |
| Platform | **Jira (company-managed)** | Project register, RAID issue types, actions, defects, enhancement backlog + sprints, Forms, workflows + gates, automation, RBAC, audit history |
| AI | **Rovo / Rovo Dev** | Draft user stories, acceptance criteria, value categories; assist test design |

**Production-only (out of demo scope, talk-track):** Tempo Financial Manager /
Timesheets for CapEx/OpEx capitalisation and finance-GL alignment; Atlassian
Guard for Okta SAML SSO + SCIM deprovisioning.

**Why BigPicture-first:** the financial, risk and resource requirements are all
met inside BigPicture's own modules, keeping the demo to a single PPM surface on
top of Jira. Tempo is only introduced in production where a capability is
genuinely absent in BigPicture (CapEx/OpEx categorisation, detailed timesheet
capitalisation).

## 5. Requirement coverage map

| Req group | Demo segment | Primarily shown in |
| --- | --- | --- |
| A. Portfolio & Project Register | 2 · Intake & register | Jira + BigPicture Overview |
| B. Financial Summary + CapEx | 4 · Financials | BigPicture Financials (+ CapEx reference field) |
| C. Schedule (Gantt + Milestones) | 3 · Schedule | BigPicture Gantt |
| D. Delivery Activities / Actions | 6 · Delivery | Jira (Action) + automation |
| E. RAID (Orora matrix-aligned) | 5 · RAID & risk | Jira RAID + BigPicture Risks matrix |
| F. Test Management (UAT) | 7 · UAT & test | Xray |
| G. Defect Management | 7 · UAT & test | Jira (Bug) + Xray |
| H. Reporting & Dashboards | 8 · Reporting | BigPicture Reports + Jira dashboards |
| I. Document & Artefact | 2 / 8 | Jira links + classification field |
| J. Security, Access & Audit | 9 · Governance | Jira RBAC + audit (Guard talk track) |
| K. Integration (CapEx + notifications) | 4 / 6 | Automation (notifications); CapEx sync = production note |
| L. Resource Management | 3 · Schedule / Resources | BigPicture Resources |
| Enhancement US-01–28 | 6 · Delivery + enhancements | Jira boards + BigPicture timeboxes + Forms |
| AI-assisted (US-20/21) | 10 · AI assist | Rovo / Xray AI |

## 6. Demo flow (~55 min)

1. Open — the PMO problem (2 min)
2. Portfolio at a glance — exec lens (6)
3. Schedule — Gantt, baselines, critical milestones, dependencies (7)
4. Financials — budget vs forecast/actual, variance, CapEx reference (6)
5. RAID & risk matrix — escalation, inherent/residual (6)
6. Delivery & enhancements — sprints, planned/unplanned, blockers/holds, ARB, value (9)
7. UAT & test management — cycles, evidence, defects, sign-off, traceability (8)
8. Reporting — portfolio dashboard, status report, trends (5)
9. Governance & security — RBAC, audit, SSO talk track (3)
10. AI assist — Rovo drafts a story + test outline (3)

Plus Q&A and next steps.

## 7. Success criteria ("what good looks like")

- Every requirement group has a credible on-screen answer.
- The exec sees decision-useful health in under 30 seconds.
- Governance gates visibly block bad data ("process enforced by the tool").
- Integration/config items (CapEx sync, multiple assignees, sign-off
  automation, trend snapshots) are positioned as scoped delivery, not gaps.

## 8. Open items / assumptions

- **TO VERIFY:** BigPicture edition on di-demo supports Financials, Risks,
  Resources and OKR (Enterprise). Confirm licence/trial before the build.
- **TO VERIFY:** Xray AI test-generation availability on the demo edition
  (Segment 10; have a manual fallback). _Xray itself is confirmed installed in
  di-demo (Xray issue types present)._
- **PENDING CONFIRMATION:** Orora likelihood/consequence scales and tolerance
  thresholds for the risk matrix (Segment 5). Use a representative 5×5 until
  supplied.

## 9. Personas (demo)

| Persona | Role in demo | Permission level |
| --- | --- | --- |
| PMO Admin | Governance, configuration | PMO Admin (project admin) |
| Project Manager (PM) | Owns a project, schedule, RAID | PM (create/edit) |
| Delivery Lead | Sprint/enhancement delivery | Team Member |
| Test Lead / UAT Coordinator | Runs UAT, sign-off | PM / Test role |
| Sponsor / Business Owner | UAT sign-off, reporting consumer | Stakeholder (limited) |
| Stakeholder (read-only) | Portfolio viewing only | Stakeholder Read-only |

## 10. Sample portfolio (demo data)

Four demo projects at different health states (represented as `Project`
issues in PMOD, scoped into BigPicture boxes):

| Demo project | Stage | Overall RAG | Story it tells |
| --- | --- | --- | --- |
| ERP Platform Upgrade | Deliver | Amber | Schedule slip + budget variance |
| Cloud Migration | Plan | Green | Healthy baseline |
| Customer Portal | Deliver | Red | Escalated risk + open Sev defects (restricted project for RBAC) |
| Payroll Automation | Initiate | Green | Intake / governance gate |

Plus: an enhancement backlog (~10 items across two sprints), one UAT cycle (~8
test cases + one raised defect), and a simple rate card (2–3 roles) for
BigPicture Financials.
