/*
 * ScriptRunner for Jira CLOUD — POST-FUNCTION (project-property counter variant)
 * Assign yearly sequential Case ID on NEW -> 1. INTAKE using a stored counter.
 * ---------------------------------------------------------------------------
 * Instead of deriving the next number from a JQL search (which lags the search
 * index on Cloud), this keeps a per-year counter in a PROJECT PROPERTY and
 * increments it. Reads are strongly consistent, so it avoids index-lag
 * duplicates. It is NOT fully atomic (Jira Cloud has no compare-and-set for
 * entity properties), so two truly simultaneous transitions can still collide —
 * fine for a demo, not a guarantee.
 *
 * INSTALL: workflow editor -> transition NEW -> 1. INTAKE -> Post functions ->
 *   "Custom script post-function [ScriptRunner]" -> paste -> set the CONFIG
 *   values -> Add -> Publish. (No changelog guard: it is bound to this one
 *   transition, so it only ever runs on NEW -> 1. INTAKE.)
 */

// ---------------------------------------------------------------------------
// CONFIG
final String COUNTER_KEY   = 'iaigm.auditCaseCounters'  // project-property key holding {year: count}
final String CASE_ID_FIELD = 'customfield_17384'        // Case ID custom field ID
final String PROJECT_KEY   = 'IAIGM'                    // project holding the counter
final int    PAD_WIDTH     = 3                          // 3 -> 2026-001 ; 2 -> 2026-01
// ---------------------------------------------------------------------------

def issueKey = issue.key
def year     = new Date().format('yyyy')

// 0) IDEMPOTENCY — if the issue already has a Case ID, do nothing.
//    Prevents re-entering Intake from overwriting the ID or burning a number.
def cur = get("/rest/api/3/issue/${issueKey}")
        .queryString('fields', CASE_ID_FIELD)
        .asObject(Map)
def existing = cur.body?.fields?.get(CASE_ID_FIELD)
if (existing != null && existing.toString().trim()) {
    logger.info("${issueKey} already has Case ID '${existing}' — skipping")
    return
}

// 1) Read the saved counters ( {"2026": 7, "2025": 42, ...} ). 404 on first ever run.
def resp = get("/rest/api/3/project/${PROJECT_KEY}/properties/${COUNTER_KEY}")
        .header('Accept', 'application/json')
        .asObject(Map)
def counters = resp.status == 200 ? (resp.body.value ?: [:]) : [:]

// 2) Increment for the current year (cold start: 0 -> 1).
def next = ((counters[year] ?: 0) as Integer) + 1
counters[year] = next

// 3) Persist the counter FIRST, so a later failure can't reuse this number.
def saveResp = put("/rest/api/3/project/${PROJECT_KEY}/properties/${COUNTER_KEY}")
        .header('Content-Type', 'application/json')
        .body(counters)
        .asString()
if (saveResp.status < 200 || saveResp.status >= 300) {
    logger.error("Could not persist counter (HTTP ${saveResp.status}) — aborting to avoid duplicate IDs")
    return
}

// 4) Build the ID (zero-padded).
def caseId = "${year}-${next.toString().padLeft(PAD_WIDTH, '0')}"

// 5) Write it to the issue.
def upd = put("/rest/api/3/issue/${issueKey}")
        .header('Content-Type', 'application/json')
        .body([fields: [(CASE_ID_FIELD): caseId]])
        .asString()
if (upd.status < 200 || upd.status >= 300) {
    logger.error("Set Case ID failed for ${issueKey}: HTTP ${upd.status} — ${upd.body}")
} else {
    logger.info("Assigned Case ID ${caseId} to ${issueKey} (NEW -> 1. INTAKE)")
}
