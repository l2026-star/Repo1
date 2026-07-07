# Case ID auto-numbering (ScriptRunner)

Assigns a unique, human-readable **Case ID** in the form `YYYY-NNN`
(`2026-001`, `2026-002`, …) the first time a ticket moves **NEW → 1. INTAKE**.

> **Cloud vs Server/DC — pick the right file.** The APIs are completely different.
>
> | Your Jira | Use | File |
> | --- | --- | --- |
> | **Cloud** (`*.atlassian.net`) — recommended | Script **Listener** (REST API) | `assign-case-id-listener-CLOUD.groovy` |
> | **Cloud** — alternative | Workflow **post-function** (REST API) | `assign-case-id-postfunction-CLOUD.groovy` |
> | **Cloud** — counter-based | Workflow **post-function**, project-property counter | `assign-case-id-postfunction-CLOUD-counter.groovy` |
> | Server / Data Center | Workflow **post-function** (Java API) | `assign-case-id-postfunction-SERVER-DC.groovy` |
>
> `di-demo.atlassian.net` is **Cloud**, so use a CLOUD file.

### Cloud: Listener vs post-function
You **can** use a ScriptRunner post-function on Cloud (workflow editor → transition
→ Post functions → "Custom script post-function"). The logic is identical (and it
needs no changelog check, since it's bound to the one transition). The reason the
**Listener** is recommended: on Cloud a post-function that updates the *same issue
that is transitioning* can race the transition commit, so the value occasionally
fails to stick under rapid/parallel transitions. Adaptavist recommends a Listener
for modifying the transitioning issue. For a demo either is fine — pick the
post-function if you prefer it living in the workflow.

## Why it works the way you asked

| Requirement | How it's met |
| --- | --- |
| ID minted only when a ticket reaches Intake | The script only acts on the `NEW → 1. INTAKE` status change. |
| **New / Not Relevant / Existing Case** are ignored | They never make that transition, so they get no ID and **consume no number**. |
| Sequential per calendar year, resets each year | Sequence = highest existing `YYYY-*` value + 1; a new year finds nothing and starts at `001`. |
| No duplicate / no re-numbering | Idempotency guard: if the issue already has a Case ID, the script exits. |

### Two ways to derive the number

- **JQL max+1** (`...-listener-CLOUD` / `...-postfunction-CLOUD`): reads existing
  `YYYY-*` IDs and adds 1. Always reflects real data (self-healing) but relies on
  the search index, which lags a second or two on Cloud — rapid transitions can
  collide.
- **Project-property counter** (`...-postfunction-CLOUD-counter`): keeps a
  per-year count in a project property and increments it. Strongly-consistent
  reads (no index lag) and fast, but trusts the stored number (drifts if the
  property is reset) and is still not atomic — Jira Cloud has no compare-and-set,
  so simultaneous transitions can still collide. Good default for a demo.

Neither is truly concurrency-proof on Cloud; both are safe for demo-scale traffic.

### How the first number is derived

There is **no stored counter**. Each run re-derives the number: it searches
existing `YYYY-*` IDs, takes the highest (`maxSeq`, initialised to `0`), and adds 1.
So the first ticket of the year finds nothing → `maxSeq = 0` → `2026-001`. Using
*max + 1* (not *count + 1*) means a deleted ID never gets reused.

---

## Cloud setup (recommended)

### 1. Create the custom field
- **Settings → Issues → Custom fields → Create field**
- Type: **Short text (plain text)**, Name: **`Case ID`**
- Associate it with the demo project's screens (at least the Intake/View screen).

### 2. Get the field ID
The script needs the `customfield_XXXXX` ID, not the name. Find it via:
`https://<site>.atlassian.net/rest/api/3/field` → search the JSON for `"Case ID"` → copy its `id`.
Paste that into `CASE_ID_FIELD` at the top of the script.

### 3. Create the Listener
- **Apps → ScriptRunner → Listeners → Create Listener**
- **Project:** your demo project (scope it — don't leave it global)
- **Events:** **Issue Updated**
- Paste `assign-case-id-listener-CLOUD.groovy`, set `CASE_ID_FIELD` / `CASE_ID_NAME`, **Save**.

The listener fires on every update but the changelog guard means it only *does*
anything on `NEW → 1. INTAKE`.

### 4. Test
- New issue (NEW) → transition to **1. INTAKE** → `Case ID = 2026-001`.
- Repeat → `2026-002`, `2026-003` …
- Send a NEW ticket to **Not Relevant** → no ID; next real Intake is still the next number.
- Move one Pended → Intake again → value **unchanged**.

### Cloud notes
- Uses the **enhanced search** endpoint `POST /rest/api/3/search/jql` with
  `nextPageToken` pagination (the old `/rest/api/3/search` was retired in 2025).
- The HTTP helpers (`get`/`post`/`put`) are pre-authenticated for the site — no tokens in the script.
- **Seeding a start number:** set one ticket's Case ID manually to e.g. `2026-042`; the next Intake becomes `2026-043`.
- **Concurrency:** two Intake transitions in the same instant could read the same max and collide. Fine for a demo. For production, back it with an atomic counter (e.g. an Assets/entity property) or a lock.

---

## Server / Data Center setup

Use `assign-case-id-postfunction-SERVER-DC.groovy` as a **Script post-function** on
the `NEW → 1. INTAKE` transition, positioned **above** "Update change history".
Create a single-line **Text** custom field named `Case ID` first. (Details in the
file header.)
