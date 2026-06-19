# planning.md — PMO & PPM Demo build tracker

Living execution tracker for building the PMO & PPM demo in
**`di-demo.atlassian.net`**. Mirrors the Confluence **Configuration Audit /
Checklist** (`1450147852`). Keep this and the Confluence ledger in sync.

- **Status legend:** ✅ present · ⚠️ drift · ❌ missing · ⏭️ manual-required · ☐ not yet audited
- **Workflow:** audit-first → report → **owner go-ahead** → apply (Layer A only).
- **Last baseline audit:** 2026-06-19 (read-only).

## Workflow & guardrails (summary)

1. di-demo ONLY for config; never write to production. Confirm active instance
   (`list_instances` + `get_active_instance`) before every write.
2. Layer A (Jira) via Admin MCP. Layers B (BigPicture) + C (Xray) are
   **manual-required** — do not attempt via MCP.
3. Consult latest Atlassian docs before each build step; confirm exact MCP tool
   names/params at runtime (`ToolSearch`).
4. See `CLAUDE.md` for full detail.

## Baseline audit findings (di-demo, 2026-06-19)

Read-only snapshot to ground the plan. Active instance confirmed = di-demo
(`inst_701645d904d94267`, Jira cloudId `f26308eb-487f-4388-945e-660349660d2d`).

- **PMOD project:** ❌ does not exist (greenfield). Unrelated `PMO` (business)
  and `APCT` (payroll) projects exist but are not the demo project.
- **Issue types present & reusable:** Risk, Assumption, Project, Milestone, Bug,
  Story, Sub-task, Epic — **plus all Xray types** (Test, Test Set, Test Plan,
  Test Execution, Precondition, Sub Test Execution) ⇒ **Xray is installed**.
- **Issue types missing (to create):** Action, Issue (RAID), Decision,
  Enhancement.
- **Custom fields:** di-demo is a shared sandbox with **~1,059** custom fields.
  The ~35 demo fields need a careful **name-by-name audit** to reuse vs. create
  (high dedup risk). Not yet performed in detail.
- **Automation / boards / dashboards / workflows / permissions / forms:** none
  scoped to PMOD (project absent). Detailed audit pending project creation.
- **BigPicture:** edition/module availability **not confirmable via MCP** —
  verify in-app (Layer B, manual).

## Layer A — Jira platform (Admin MCP — execute)

| # | Status | Object | Notes / next step |
| --- | --- | --- | --- |
| A1 | ❌ | Project | Create company-managed **PMO Demo**, key **PMOD**, lead = PMO Admin |
| A2 | ⚠️ | Issue type scheme | Reuse Risk/Assumption/Project/Milestone/Bug/Story/Sub-task/Epic; **create** Action, Issue, Decision, Enhancement; assign scheme to PMOD |
| A3 | ☐ | Custom fields | Create per Config Guide A3 — **audit 1,059 existing fields first** to reuse/avoid dupes |
| A4 | ☐ | Select field options | Populate options (RAG, Stage, Value Category/Magnitude, Likelihood 1–5, Consequence 1–5, Risk Category, Artefact Type, …) |
| A5 | ☐ | Screens / field config | Add fields to Project / Risk / Enhancement / Bug screens; stage-mandatory fields |
| A6 | ☐ | Workflow — Project | Intake → Initiate → Plan → Deliver → Close; validators on stage-mandatory fields |
| A7 | ☐ | Workflow — Enhancement | Submitted → Triaged → Approved → Ready → In Progress → Delivered → Closed; ARB gate to Approved; Readiness gate to Ready |
| A8 | ☐ | Workflow — Defect | Open → Triage → In Progress → Ready for Retest → Done |
| A9 | ☐ | Approval — UAT sign-off | Approval step capturing approver + timestamp + comment |
| A10 | ☐ | Forms | Project Intake; Enhancement Intake with conditional AI fields |
| A11 | ☐ | Automation | 8 rules per Config Guide A7 (variance+RAG, action reminders, risk escalation, mandatory hold reason, readiness enforcement, stage notifications, UAT criteria, high-sev alert) |
| A12 | ☐ | Boards & sprints | Enhancement board + quick filters; Sprint 1 (closed) + Sprint 2 (active) |
| A13 | ☐ | Dashboards | Defect dashboard; Portfolio dashboard |
| A14 | ☐ | Permissions | Scheme with roles PMO Admin / PM / Team Member / Stakeholder Read-only |
| A15 | ☐ | Issue security | Hide restricted project (Customer Portal) from Stakeholder RO |
| A16 | ☐ | Sample data | Four demo projects, milestones, risks, actions, enhancement backlog, one defect — **draft for owner review before bulk creation** |

## Layer B — BigPicture (⏭️ manual-required — do NOT attempt via MCP)

| # | Item | Note |
| --- | --- | --- |
| B1 | Boxes: Home, Portfolio, 4 project boxes, JQL scope | App-internal |
| B2 | Gantt: critical milestones, baselines, dependencies, auto-schedule | App-internal |
| B3 | Risks: configurable 5×5 matrix, RAG bands, escalation threshold | Needs Orora scales (PENDING) |
| B4 | Resources: teams, rates, allocations, capacity vs demand | App-internal |
| B5 | Financials: rates, budgets, est/actual cost, variance, portfolio summary | App Financial Admin role |
| B6 | OKR: objectives + linked initiatives | App-internal |
| B7 | Overview columns + Reports view | App-internal |

## Layer C — Xray (⏭️ manual-required — do NOT attempt via MCP)

| # | Item | Note |
| --- | --- | --- |
| C1 | Enable Xray on PMOD; confirm Xray issue types | Xray installed site-wide; enable for PMOD |
| C2 | UAT Test Plan + ~8 Test Cases + Preconditions + Test Set; coverage links | App-internal |
| C3 | Test Execution + results/evidence; defect from failed test; Ready for Retest | App-internal |
| C4 | Traceability/coverage report; sign-off gate demonstration | App-internal |
| C5 | Xray AI test generation (if available) | TO VERIFY |

## Sign-off tracker

| Check | Owner | Status |
| --- | --- | --- |
| Active instance confirmed = di-demo | Executing session | ✅ (2026-06-19) |
| Layer A audit findings reported | Executing session | ☐ |
| Owner approval to apply | Thompson | ☐ |
| Layer A applied + verified | Executing session | ☐ |
| Layers B/C flagged manual-required | Executing session | ✅ |
| End-to-end validation pass (Config Guide Layer E) | Operator | ☐ |

## Open questions / decisions pending

1. **Session scope** — proceed only to scaffold + full audit, or begin applying
   Layer A now?
2. **Apply authority** — checklist names Thompson as approver; can Liss
   authorise application?
3. **Audit-log target** — update the existing Configuration Audit / Checklist
   page (`1450147852`) in the production SE space, and/or a new running-log
   page? Confirm production-Confluence writes are sanctioned.
4. **PMOD project type** — Business/Project-management vs Software template
   (Software acceptable if native sprints are wanted for enhancements).

## Next actions

- [ ] Resolve open questions 1–4 with the user.
- [ ] On go-ahead: detailed field-by-field audit of the ~1,059 custom fields.
- [ ] Apply Layer A top-down (project → issue types → fields → screens →
      workflows → forms → automation → boards → dashboards → permissions →
      sample data), verifying each.
- [ ] Update the Confluence audit ledger + this file after each applied item.
