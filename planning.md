# planning.md — PMO & PPM Demo build tracker

Living execution tracker for building the PMO & PPM demo in
**`di-demo.atlassian.net`**. Mirrors the Confluence **Configuration Audit /
Checklist** (`1450147852`). Keep this and the Confluence ledger in sync.

- **Status legend:** ✅ done · ⚠️ drift · ❌ missing · ⏭️ manual-required · ☐ pending
- **Workflow:** audit-first → report → **owner go-ahead** → apply (Layer A only).
- **Authority:** Thompson is named approver; **Liss authorised** this greenfield run (2026-06-19).
- **Last update:** 2026-06-19.

## Execution status — 2026-06-19 (update 3)

- ✅ **Done:** A1 Project, A2 Issue types, A3 Fields, A4 Options, A5 Screens, A12 Boards & sprints (board 545; Sprint 1 = 1917, Sprint 2 = 1918).
- ◧ **In progress:** A16 Sample data — 4 Project records done; full dataset (milestones, risks, ~10 enhancements, UAT defect) being built.
- ❌ **BLOCKED (Admin MCP tooling):** A6–A9 (Project/Enhancement/Defect **workflows**, custom **statuses**, UAT **approval**).
  - `create_status` → opaque `Invalid request payload` for both GLOBAL and PROJECT scope.
  - `create_workflow` with inline `newStatuses` → tool schema rejects (`Expected object, received array`); transitions confirmed to need the new `links` array (not `from`/`to`).
  - Atlassian dev-docs not retrievable in this environment to pin exact payloads.
  - **Recommendation:** build the three workflows + custom statuses **manually in-app** (like Layers B/C), OR revisit once the Admin MCP `create_status`/`create_workflow` payloads are confirmed. The Stage field (Intake→Close) already gives the lifecycle vocabulary on issues in the interim.
- ☐ **Pending:** A10 Forms, A11 Automation, A13 Dashboards, A14 Permissions, A15 Issue security. (A10/A11 to be attempted via MCP; flag if similarly blocked.)

## Workflow & guardrails (summary)

1. di-demo ONLY for config; never write to production. Confirm active instance
   (`list_instances` + `get_active_instance`) before every write.
2. Layer A (Jira) via Admin MCP. Layers B (BigPicture) + C (Xray) are
   **manual-required** — do not attempt via MCP.
3. Consult latest Atlassian docs before each build step; confirm exact MCP tool
   names/params at runtime (`ToolSearch`).
4. See `CLAUDE.md` for full detail.

## Key identifiers (di-demo)

- Project: **PMOD** — id **10549** (company-managed *software*, category Demo, lead Liss Jose)
- Issue type scheme: **12122** ("PMO Demo Issue Type Scheme")
- Created issue types: Action **10491**, Issue **10492**, Decision **10493**, Enhancement **10494**
- Reused issue types: Risk 10404, Assumption 10420, Project 10422, Milestone 10423, Bug 10072, Story 10004, Task 10038, Sub-task 10039, Epic 10000

### Custom field ID map

Created (28):

| Field | id | Type | Field | id | Type |
| --- | --- | --- | --- | --- | --- |
| Sponsor | 11845 | user | Financial RAG | 11859 | select (R/A/G) |
| Project Manager | 11846 | user | Delivery Stream / BU | 11860 | select |
| Business Owner | 11847 | user | Stage | 11861 | select |
| Target Go-Live | 11848 | date | Value Category | 11862 | select |
| CapEx Reference | 11849 | text | Value Magnitude | 11863 | select |
| Forecast at Completion (FAC) | 11850 | number | Planned / Unplanned | 11864 | select |
| Variance | 11851 | number | Consequence | 11865 | select (1–5) |
| Blocker Reason | 11852 | text | Inherent Rating | 11866 | select |
| ARB Reference | 11853 | url | Residual Rating | 11867 | select |
| Contributors | 11854 | multiuser | Risk Category | 11868 | select |
| Assignees (additional) | 11855 | multiuser | Artefact Type | 11869 | select |
| Business Areas Impacted | 11856 | labels | Carry-over Reason | 11870 | select |
| Artefact Link | 11857 | url | Readiness (Ready for Sprint) | 11871 | select |
| Overall RAG | 11858 | select (R/A/G) | AI Enhancement? | 11872 | checkbox |

Reused (3, to avoid duplicates): **Budget** `cf_11673` (number), **Likelihood**
`cf_11330` (select — verify 1–5 scale for matrix), **Hold Reason** →
"Reason for Hold" `cf_11255` (select).

## Layer A — Jira platform (Admin MCP — execute)

| # | Status | Object | Notes / next step |
| --- | --- | --- | --- |
| A1 | ✅ | Project | DONE — PMOD (10549), company-managed software, lead Liss Jose, Demo category |
| A2 | ✅ | Issue type scheme | DONE — scheme 12122 assigned; created Action/Issue/Decision/Enhancement; reused the rest |
| A3 | ✅ | Custom fields | DONE — 28 created (cf 11845–11872); 3 reused |
| A4 | ✅ | Select field options | DONE — options on all 15 new select/checkbox fields |
| A5 | ✅ | Screens / field config | DONE — 31 fields on PMOD Create (10744/tab 10747) + Edit/View (10745/tab 10748). Shared screen across types (per-type screens = future refinement); stage-mandatory enforcement to be done via workflow validators (A6) |
| A6 | ☐ | Workflow — Project | Intake → Initiate → Plan → Deliver → Close; validators on stage-mandatory fields |
| A7 | ☐ | Workflow — Enhancement | Submitted → Triaged → Approved → Ready → In Progress → Delivered → Closed; ARB + Readiness gates |
| A8 | ☐ | Workflow — Defect | Open → Triage → In Progress → Ready for Retest → Done |
| A9 | ☐ | Approval — UAT sign-off | Approval step capturing approver + timestamp + comment |
| A10 | ☐ | Forms | Project Intake; Enhancement Intake with conditional AI fields |
| A11 | ☐ | Automation | 8 rules per Config Guide A7 |
| A12 | ☐ | Boards & sprints | Enhancement board + quick filters; Sprint 1 (closed) + Sprint 2 (active) |
| A13 | ☐ | Dashboards | Defect dashboard; Portfolio dashboard |
| A14 | ☐ | Permissions | Scheme with roles PMO Admin / PM / Team Member / Stakeholder Read-only |
| A15 | ☐ | Issue security | Hide restricted project (Customer Portal) from Stakeholder RO |
| A16 | ◧ | Sample data | PARTIAL — 4 Project register issues created (PMOD-1 ERP/Amber, PMOD-2 Cloud/Green, PMOD-3 Customer Portal/Red, PMOD-4 Payroll/Green). Bulk backlog (milestones, risks, ~10 enhancements, UAT defect) awaits review per the gate |

## Layer B — BigPicture (⏭️ manual-required) · Layer C — Xray (⏭️ manual-required)

Unchanged from the Confluence ledger — app-internal; not configurable via MCP.
Xray issue types are already present site-wide (enable on PMOD = manual, C1).

## Sign-off tracker

| Check | Owner | Status |
| --- | --- | --- |
| Active instance confirmed = di-demo | Executing session | ✅ 2026-06-19 |
| Layer A audit findings reported | Executing session | ✅ (to Liss) |
| Approval to apply | Thompson | ✅ Liss authorised in lieu (2026-06-19) |
| Layer A applied + verified | Executing session | ⏳ A1–A5 done; A6–A16 pending |
| Layers B/C flagged manual-required | Executing session | ✅ |
| End-to-end validation pass (Config Guide Layer E) | Operator | ☐ |

## Notes / decisions

- PMOD created as **company-managed Software** (not Business) so native
  sprints/boards are available for the enhancement-delivery segment.
- New select fields use global default contexts (field names are demo-specific;
  low collision risk). Screen association (A5) controls visibility per issue type.
- Likelihood reused (`cf_11330`): confirm its option scale suits the 5×5 matrix;
  if not, add a PMOD-scoped context rather than editing the shared global context.

## Next actions

- [ ] A16: sample data — create the four Project register issues first (unblocks BigPicture portfolio + dashboards), then milestones/risks/enhancements/defect. Label per demo project for BigPicture scoping.
- [ ] A12: confirm PMOD board type; create Scrum board if needed; Sprint 1 (closed) + Sprint 2 (active).
- [ ] A14–A15: permission scheme + roles; issue security (hide Customer Portal from Stakeholder RO).
- [ ] A6–A9: Project / Enhancement / Defect workflows + UAT approval (latest-doc check first; flag if MCP workflow API is a blocker — these are the most intricate via API).
- [ ] A10–A11: Forms + automation rules (also intricate via API).
- [ ] A13: dashboards.
- [ ] Re-sync the Confluence ledger at the next milestone.

> **Complexity note:** A6–A11 (workflows, approvals, forms, automation) are the
> intricate, higher-risk items via the Admin MCP. If a specific operation isn't
> supported/reliable, flag it as manual-required (like Layers B/C) rather than
> forcing it.
