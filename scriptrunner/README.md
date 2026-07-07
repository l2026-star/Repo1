# Case ID auto-numbering (ScriptRunner)

Assigns a unique, human-readable **Case ID** in the form `YYYY-NNN`
(`2026-001`, `2026-002`, …) the first time a ticket moves **NEW → 1. INTAKE**.

## Why it works the way you asked

| Requirement | How it's met |
| --- | --- |
| ID minted only when a ticket reaches Intake | Post-function lives **only** on the `NEW → 1. INTAKE` transition. |
| Tickets in **New / Not Relevant / Existing Case** are ignored | They never fire this transition, so they get no ID and **consume no number**. |
| Sequential per calendar year, reset each year | Sequence is derived from the highest existing `YYYY-*` value; a new year starts back at `001`. |
| No duplicate / no re-numbering | Idempotency guard: if the issue already has a Case ID, the script exits. |

## Setup

1. **Create the custom field**
   - Type: **Text Field (single line)**
   - Name: **`Case ID`** (must match `FIELD_NAME` in the script)
   - Add it to the project's field context and to the Intake screen (so it shows on the issue).

2. **Add the post-function**
   - Edit the workflow → open the **`NEW → 1. INTAKE`** transition → **Post Functions** → **Add** → **Script post-function** (ScriptRunner).
   - Paste `assign-case-id-postfunction.groovy`.
   - **Move it above** the built-in *"Update change history for an issue"* step.

3. **Publish** the workflow.

## Test

- Create an issue (status **NEW**) → transition to **1. INTAKE** → field shows `2026-001`.
- Repeat → `2026-002`, `2026-003`, …
- Move one back to Pended and into Intake again → **value stays the same** (no re-numbering).
- Send a NEW ticket straight to **Not Relevant** → **no ID**, and the next real Intake still gets the next number in sequence.

## Notes & caveats

- **Concurrency:** the next number is read from the search index. If two agents transition tickets to Intake in the *exact* same second, both could theoretically read the same max and collide. For a demo this is fine. For production, either:
  - add a ScriptRunner **Behaviour**/database-backed counter, or
  - wrap the read+write in a lock, or
  - use a ScriptRunner **fragment** with an atomic sequence table.
- **Padding:** IDs pad to 3 digits (`001`). Sequence `1000+` simply prints as `2026-1000` — sort order stays correct.
- **Field name:** change `FIELD_NAME` at the top of the script if you name the field something other than `Case ID`.

## Alternative: Script Listener

If you'd rather not touch the workflow, the same logic can run as a **ScriptRunner Listener** on the *Issue Updated / Generic Event* filtered to the `NEW → 1. INTAKE` status change. The post-function is preferred because it fires exactly on that one transition and persists cleanly within it.
