/*
 * ScriptRunner for Jira CLOUD — Custom script POST-FUNCTION
 * Assign yearly sequential Case ID on NEW -> 1. INTAKE
 * ---------------------------------------------------------------------------
 * Mints a unique ID (YYYY-NNN, e.g. 2026-001, 2026-002 ...) when a ticket
 * transitions from "NEW" to "1. INTAKE".
 *
 * Even as a post-function, Cloud has no ComponentAccessor / in-process issue
 * setter — you still read/write through the REST API helpers (get/put/post).
 *
 * INSTALL:
 *   Workflow editor -> transition NEW -> 1. INTAKE -> Post functions ->
 *   Add post function -> "Custom script post-function [ScriptRunner]" ->
 *   paste this script -> set CASE_ID_FIELD -> Add -> Publish the workflow.
 *
 * Because it is bound to this one transition, there is NO changelog check:
 * it can only ever run on NEW -> 1. INTAKE, so tickets going to
 * "Not Relevant" / "Existing Case" (or left in NEW) never mint an ID.
 *
 * CAVEAT (Cloud): a post-function that updates the transitioning issue can race
 * the transition commit. If IDs occasionally fail to stick under rapid/parallel
 * transitions, switch to the Listener version (assign-case-id-listener-CLOUD.groovy),
 * which Adaptavist recommends for modifying the transitioning issue.
 */

// ---------------------------------------------------------------------------
// CONFIG
final String CASE_ID_FIELD = 'customfield_XXXXX' // <-- Case ID custom field ID
final String CASE_ID_NAME  = 'Case ID'           // <-- exact field name, used in JQL
final String ISSUE_TYPE    = 'Audit Review'      // <-- scope numbering to this issue type ('' = all types)
// ---------------------------------------------------------------------------

def issueKey = issue.key
// Project key is the part of the key before the trailing -number (PMOD-123 -> PMOD).
def projectKey = issueKey.replaceAll(/-\d+$/, '')

// 1) Idempotency — never overwrite an ID that already exists.
def currentResp = get("/rest/api/3/issue/${issueKey}")
        .queryString('fields', CASE_ID_FIELD)
        .asObject(Map)
def existing = currentResp.body?.fields?.get(CASE_ID_FIELD)
if (existing != null && existing.toString().trim()) {
    logger.info("${issueKey} already has Case ID '${existing}' — leaving as-is")
    return
}

// 2) Current calendar year.
def year = new Date().format('yyyy')

// 3) Highest sequence ALREADY ISSUED this year (enhanced search, paginated).
//    IMPORTANT: we key off "has a YYYY- Case ID", NOT a count of current-status
//    matches. A number, once assigned, is taken forever — even if the ticket
//    later moves to Not Relevant / Existing Case or is closed. Deriving from a
//    COUNT (or filtering by current status) would shrink when tickets move and
//    would produce DUPLICATE ids. Always MAX(existing ids) + 1.
def typeClause = ISSUE_TYPE ? " AND issuetype = \"${ISSUE_TYPE}\"" : ""
def jql = "project = \"${projectKey}\"${typeClause} AND \"${CASE_ID_NAME}\" ~ \"${year}\" ORDER BY created ASC"

int maxSeq = 0
String nextPageToken = null
while (true) {
    def bodyMap = [jql: jql, maxResults: 100, fields: [CASE_ID_FIELD]]
    if (nextPageToken) bodyMap.nextPageToken = nextPageToken

    def searchResp = post('/rest/api/3/search/jql')
            .header('Content-Type', 'application/json')
            .body(bodyMap)
            .asObject(Map)

    (searchResp.body?.issues ?: []).each { iss ->
        def val = iss.fields?.get(CASE_ID_FIELD)?.toString()
        if (val && val ==~ /${year}-\d+/) {
            int seq = val.substring(year.length() + 1) as int
            if (seq > maxSeq) maxSeq = seq
        }
    }

    nextPageToken = searchResp.body?.nextPageToken
    if (!nextPageToken) break
}

// 4) Mint the next ID, zero-padded to 3 digits.
def newId = String.format('%s-%03d', year, maxSeq + 1)

// 5) Write it back via REST.
def updateResp = put("/rest/api/3/issue/${issueKey}")
        .header('Content-Type', 'application/json')
        .body([fields: [(CASE_ID_FIELD): newId]])
        .asObject(Map)

if (updateResp.status >= 200 && updateResp.status < 300) {
    logger.info("Assigned Case ID ${newId} to ${issueKey} (NEW -> 1. INTAKE)")
} else {
    logger.error("Failed to set Case ID on ${issueKey}: HTTP ${updateResp.status} — ${updateResp.body}")
}
