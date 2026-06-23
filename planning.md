# planning.md — PMO & PPM Demo build tracker

Living execution tracker for building the PMO & PPM demo in
**`di-demo.atlassian.net`**. Mirrors the Confluence **Configuration Audit /
Checklist** (`1450147852`). Keep this and the Confluence ledger in sync.

- **Status legend:** ✅ done · ⚠️ drift · ❌ missing · ⏭️ manual-required · ☐ pending
- **Workflow:** audit-first → report → **owner go-ahead** → apply (Layer A only).
- **Authority:** Thompson is named approver; **Liss authorised** this greenfield run (2026-06-19).
- **Last update:** 2026-06-23.

## Execution status — 2026-06-23 (update 6 — delivery sample data: epics/stories/bugs + sprints)

Added a software-delivery slice on board **546 "PMO SCRUM"** to demonstrate hybrid (Agile) execution:

- ✅ **5 Epics:** PMOD-55 Customer Portal — Account Management · PMOD-56 Customer Portal — Payments & Billing · PMOD-57 ERP Integration Layer · PMOD-68 Cloud Migration — Platform & Workloads · PMOD-69 Payroll Automation — Pay Run & Compliance.
- ✅ **40 Stories** (all epic-parented, each with an **original estimate**): **PMOD-58–63** + **PMOD-70–103**, ~8 per epic across the 5 epics. Estimates range 4h–8d. Labels: CustomerPortal / ERP / CloudMigration / PayrollAutomation.
- ✅ **3 Bugs** (epic-parented, estimates + priority): PMOD-64 Profile save fails on special characters (1d, High, →55) · PMOD-65 Duplicate charge on payment retry (4h, Highest, →56) · PMOD-66 Order sync drops line items over 50 (2d, High, →57).
- ✅ **2 Sprints on board 546:** **Sprint 1 = 1919 (ACTIVE)** [PMOD-58/59/62/63] · **Sprint 2 = 1920 (future)** [PMOD-60/61/64]. Backlog: PMOD-65, PMOD-66 + the 34 new stories (PMOD-70–103).
- ❌ **Components & Versions — BLOCKED via MCP (new tool gap).** The Admin MCP has **no** `create_component` / `create_version` tool (confirmed by name lookup); Jira rejects unknown names on create/update (`Version name 'Release 1.0' is not valid`). **Action:** create in-app (Project settings → Components and → Releases), then stamp onto the slice via `update_issue`.
  - **Proposed Components:** Frontend · Backend · Payments · Integration · Infrastructure · Payroll.
  - **Proposed Versions (Releases):** Release 1.0 · Release 1.1 · Release 2.0.
  - **Default mapping rule (stamp once created):** by epic — Account Mgmt → Frontend/Backend; Payments & Billing → Payments; ERP Integration → Integration; Cloud Migration → Infrastructure; Payroll Automation → Payroll. Versions: Customer Portal R1.0/R1.1; ERP/Cloud/Payroll R2.0. Confirm the list with Liss before stamping.

## Execution status — 2026-06-19 (update 5 — automation rules built in-app)

- ◧ **A11 Automation — 6 of 8 rules built** (in-app / via browser, not MCP):
  - ✅ Rule 1 Variance & Financial RAG · ✅ Rule 2 Action reminders · ✅ Rule 3 Risk escalation · ✅ Rule 5 Readiness enforcement · ✅ Rule 7 UAT criteria check · ✅ Rule 8 High-severity defect alert.
  - ☐ **Pending: Rule 4 (Mandatory Hold Reason)** and **Rule 6 (Enhancement stage notifications)** — not yet created.
- Build aids on Confluence: *Automation Rules Design (A11)* + *Claude Browser Prompt — Rule 1*.

## Execution status — 2026-06-19 (update 4 — after MCP fix)

The dev-team fix covered **create_status** and **create_workflow** (both now work). Implemented:

- ✅ **Workflows APPLIED (A6–A8):** created 9 statuses + 4 workflows — **PMO Project Lifecycle** (Intake→Close), **PMO Enhancement Lifecycle** (Submitted→Closed), **PMO Defect Lifecycle** (Open→Done), **PMO Baseline**. Workflow scheme set on PMOD via **draft + publish** on the project's own scheme **10602** (status migration: Project In Progress→Deliver, Done→Close). Project issues PMOD-1..4 transitioned to their stages (Deliver/Plan/Deliver/Initiate).
- ✅ **A10 Forms:** Enhancement Intake (conditional AI) + Project Intake — both created.
- ✅ **Backfilled** Likelihood (1-Rare…5-Almost Certain) on the 6 risks + Reason for Hold on PMOD-28.
- ◧ **A15 Issue security PARTIAL:** scheme **10133** + level **10101** ("Restricted — Customer Portal") created; **member-add + project-assign BLOCKED by NEW tool bugs** — `add_security_level_member` → "Invalid request payload"; `assign_issue_security_scheme` → 404 (wrong endpoint).
- ◧ **A11 Automation — 6 of 8 rules now built** in-app (see update 5); only Rule 4 (Mandatory Hold Reason) & Rule 6 (Enhancement stage notifications) pending. (`create_automation_rule` MCP tool remained blocked, so rules were built manually.)
- ☐ **Remaining:** A9 UAT approval (workflow approval config / manual), A13 dashboard gadgets (no MCP gadget tool — add in-app), A14 permission-scheme grants (4 roles exist; grants pending).

> New tool bugs logged for the dev team on the "Admin MCP Tooling Issues" child page.

## Execution status — 2026-06-19 (update 3)

- ✅ **Done:** A1 Project, A2 Issue types, A3 Fields, A4 Options, A5 Screens, A12 Boards & sprints (board 545; Sprint 1 = 1917, Sprint 2 = 1918).
- ✅ **A16 Sample data DONE:** 30 issues — 4 Projects (PMOD-1..4), 9 milestones (PMOD-5..13, criticals flagged), 6 risks (PMOD-14..19, 2 escalated), 10 enhancements (PMOD-20..29; Sprint 1=1917 closed with 6 delivered/Done, Sprint 2=1918 active with 4), 1 UAT defect (PMOD-30, linked to PMOD-3). NB: reused Likelihood (cf_11330) + Reason for Hold (cf_11255) left unset (option values unreadable in agent) — set manually if needed.
- ❌ **BLOCKED (Admin MCP tooling):** A6–A9 (Project/Enhancement/Defect **workflows**, custom **statuses**, UAT **approval**).
  - `create_status` → opaque `Invalid request payload` for both GLOBAL and PROJECT scope.
  - `create_workflow` with inline `newStatuses` → tool schema rejects (`Expected object, received array`); transitions confirmed to need the new `links` array (not `from`/`to`).
  - Atlassian dev-docs not retrievable in this environment to pin exact payloads.
  - **Recommendation:** build the three workflows + custom statuses **manually in-app** (like Layers B/C), OR revisit once the Admin MCP `create_status`/`create_workflow` payloads are confirmed. The Stage field (Intake→Close) already gives the lifecycle vocabulary on issues in the interim.
- ◧ **Partial (reliable):** A10 Forms (Enhancement Intake w/ conditional AI ✅; Project Intake pending), A13 Dashboards (2 containers 10100/10101 ✅; gadgets in-app), A14 Permissions (4 project roles ✅; permission-scheme grants pending).
- ❌ **BLOCKED (also tooling):** A11 Automation — `create_automation_rule` returns "request body could not be parsed" (opaque rule-tree schema, same class as workflows). Recommend building rules in-app, or revisit with confirmed component schemas.
- ☐ **Pending (reliable):** A15 Issue security (hide Customer Portal PMOD-3 from Stakeholder RO).

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
| A6 | ✅ | Workflow — Project | DONE — PMO Project Lifecycle (Intake→Close) applied to PMOD via draft+publish |
| A7 | ✅ | Workflow — Enhancement | DONE — PMO Enhancement Lifecycle (Submitted→Closed) applied |
| A8 | ✅ | Workflow — Defect | DONE — PMO Defect Lifecycle (Open→Done) applied |
| A9 | ❌ | Approval — UAT sign-off | Manual/workflow-approval config — not done (sits with Xray Test Plan, Layer C) |
| A10 | ✅ | Forms | DONE — Enhancement Intake (conditional AI) + Project Intake (id fdf2021d) both created |
| A11 | ◧ | Automation | 6 of 8 rules built in-app (1 Variance/RAG, 2 Action reminders, 3 Risk escalation, 5 Readiness, 7 UAT criteria, 8 High-sev alert); **Rule 4 (Mandatory Hold Reason) & Rule 6 (Enhancement stage notifications) pending**. MCP create_automation_rule still blocked |
| A12 | ✅ | Boards & sprints | DONE — board 545 "Enhancement Board" (Sprint 1=1917 closed, Sprint 2=1918 active) **+ board 546 "PMO SCRUM"** (Sprint 1=1919 active, Sprint 2=1920 future) for the epics/stories/bugs delivery slice |
| A13 | ◧ | Dashboards | 2 containers created — Portfolio (10100) + Defect (10101); gadgets added in-app |
| A14 | ◧ | Permissions | Scheme **10510** + 29 grants created (4 roles); PMO Admin role seeded (Liss). **Project-assignment NOT possible via MCP** (no assign-permission-scheme-to-project tool) → assign in-app |
| A15 | ◧ | Issue security | Scheme 10133 + level 10101 created; member-add + project-assign BLOCKED (tool bugs) |
| A16 | ✅ | Sample data | DONE — 30 core issues + RAID set (Issue/Assumption/Decision/Dependency/Action ×3 = PMOD-40..54, Dependency added to scheme 12122). 4 Projects, 9 milestones, 6 risks, 10 enhancements (2 sprints), 1 defect. **+ delivery slice PMOD-55..103** (5 epics, 40 stories, 3 bugs; original estimates; sprints 1919 active / 1920 future on board 546). Components/versions pending in-app (no MCP tool) |

## Layer B — BigPicture (⏭️ manual-required) · Layer C — Xray (⏭️ manual-required)

Unchanged from the Confluence ledger — app-internal; not configurable via MCP.
Xray issue types are already present site-wide (enable on PMOD = manual, C1).

## Sign-off tracker

| Check | Owner | Status |
| --- | --- | --- |
| Active instance confirmed = di-demo | Executing session | ✅ 2026-06-19 |
| Layer A audit findings reported | Executing session | ✅ (to Liss) |
| Approval to apply | Thompson | ✅ Liss authorised in lieu (2026-06-19) |
| Layer A applied + verified | Executing session | ⏳ A1–A5, A12, A16 done; A10/A13/A14 partial; A6–A9 + A11 blocked (tooling); A15 pending |
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
