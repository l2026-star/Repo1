# CLAUDE.md

Operating guide for Claude sessions working in this repository.

## What this repository is

This repo is the **control / working-docs repository for the "PMO & PPM Demo
(BigPicture + Xray)"** — a reusable Solutions Engineering (SE) Demo Center asset
for Design Industries (DI). The demo proves that the Atlassian platform
(**Appfire BigPicture Enterprise + Xray, on Jira**) meets an enterprise PMO's
requirements for running projects, enhancements and change in a hybrid
(Waterfall + Agile) environment.

The actual demo is **built in the `di-demo.atlassian.net` Jira/Confluence
sandbox**. This repo holds the planning, requirements and execution-tracking
documents (`PRD.md`, `planning.md`) and this operating guide. It does **not**
contain application source code.

- **Target opportunity:** Enterprise PMO tooling RFP (Orora-aligned)
- **Owner:** Thompson Cherian · **Operator (this work):** Liss (lissmaria@di.net.au)
- **Source of truth (specs):** Confluence space `SE` on production
  `designindustries.atlassian.net` (see page index below).

## Two-MCP workflow (read here, write there)

This is the single most important operating rule. **Two different Atlassian MCP
servers are in play and they must not be confused:**

| Purpose | MCP server | Site | Notes |
| --- | --- | --- | --- |
| **Read** the spec/source pages | **Atlassian (Rovo official) MCP** (`mcp__Atlassian__*`) | `designindustries.atlassian.net` (production) | cloudId `5e3cbf6f-7022-4827-9194-a606c47ca2d5`. Use for reading the Confluence spec pages and for updating the audit-log page. |
| **Apply** Jira/Confluence config | **Atlassian Admin MCP** (`mcp__Atlassian_Admin_MCP__*`) | `di-demo.atlassian.net` (sandbox) | Active instance `inst_701645d904d94267` ("DI-demo-rovo-dev"). Jira cloudId `f26308eb-487f-4388-945e-660349660d2d`. |

### Hard guardrails

1. **Instance discipline.** All demo configuration happens in
   **`di-demo.atlassian.net` ONLY**. **Never** create demo Jira/Confluence
   content in production `designindustries.atlassian.net`.
2. **Confirm before every write.** Before any Admin-MCP write, call
   `list_instances` + `get_active_instance` and confirm the active instance is
   `di-demo`. If it cannot be confirmed as di-demo, **stop and report**.
   (Switch with `select_instance` if needed.)
3. **Audit-first → report → approval → apply.** For each config item: read
   current state → classify ✅ present / ⚠️ drift / ❌ missing → summarise
   findings → **get the owner's (Thompson's) go-ahead** → only then apply
   changes for ❌/⚠️ items. This matches the standing rule to confirm before
   creating in Jira.
4. **Scope split — only Layer A is automatable:**
   - **Layer A (Jira platform)** — projects, issue types, fields, screens,
     workflows, forms, automation, boards, dashboards, permissions, sample
     data. **Automate via the Admin MCP.**
   - **Layer B (BigPicture)** and **Layer C (Xray)** — **app-internal; the
     Admin MCP cannot configure them.** Do **not** attempt. Mark them
     _Manual-required_ and report so a human completes them in-app.
5. **Refer to the latest Atlassian documentation before implementing.** Before
   building a config object, check current Atlassian docs (REST/Jira Cloud
   Admin, BigPicture, Xray) so the approach and tool usage are current. MCP tool
   names in the spec pages are *indicative* — confirm exact names/params at
   runtime via `ToolSearch` before calling.
6. **The owner approves applies.** The execution checklist names **Thompson**
   as the approver for di-demo changes. Do not apply Layer A changes without
   that go-ahead (or explicit delegation).

## Confluence source pages (production `SE` space — read via Rovo MCP)

Parent → children. Read these for authoritative detail; the **Configuration
Guide** is authoritative for config detail, the **Configuration Audit /
Checklist** is the execution ledger.

| Page | ID | Role |
| --- | --- | --- |
| 📊 PMO & PPM Demo (BigPicture + Xray) — Overview | `1449951252` | Vision, audience, stack, requirement map, demo flow |
| ✅ PMO Demo — Prerequisites & Setup | `1450770435` | Apps/editions, roles, personas, sample-data prerequisites |
| ⚙️ PMO Demo — Configuration Guide | `1450311754` | **Authoritative** step-by-step build (Layers A/B/C/D/E) |
| 🔍 PMO Demo — Configuration Audit / Checklist | `1450147852` | **Execution ledger** for the Admin-MCP session (A1–A16, B, C) |
| 🎬 PMO Demo — Demo Script | `1450704899` | Segment-by-segment talk track + requirement mapping |

## Audit log / progress tracking

The user has asked that the **audit log in Confluence be updated as changes are
made**. Treat the **Configuration Audit / Checklist** page (`1450147852`) as the
canonical ledger: update item status (✅/⚠️/❌/⏭️) and the Sign-off table as work
progresses, and/or append timestamped entries. Mirror the same status in
`planning.md` in this repo so the repo and Confluence stay in sync.
**Confirm the exact audit-log target with the user before writing to the
production SE space.**

## Repo conventions

- Working branch: **`claude/wonderful-goldberg-4phov1`**. Develop here; commit
  with clear messages; push with `git push -u origin <branch>`. Do not open a
  PR unless asked.
- Docs are GitHub-flavoured Markdown. Keep tables/headings scannable.
- Keep `planning.md` (status tracker) and `PRD.md` (requirements) current as the
  build progresses.

## Useful identifiers

- designindustries (prod) cloudId: `5e3cbf6f-7022-4827-9194-a606c47ca2d5`
- di-demo (sandbox) Jira cloudId: `f26308eb-487f-4388-945e-660349660d2d`
- di-demo Admin-MCP instanceId: `inst_701645d904d94267`
- Proposed demo project key: **PMOD** (company-managed). _Confirm availability —
  not present in di-demo as of the baseline audit._
