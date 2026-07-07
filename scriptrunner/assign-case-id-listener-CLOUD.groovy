/*
 * ScriptRunner for Jira CLOUD — Script Listener
 * Assign yearly sequential Case ID on NEW -> 1. INTAKE
 * ---------------------------------------------------------------------------
 * Mints a unique ID (YYYY-NNN, e.g. 2026-001, 2026-002 ...) the first time a
 * ticket transitions from "NEW" to "1. INTAKE".
 *
 * On Cloud you cannot use ComponentAccessor / issue.setCustomFieldValue — those
 * are Server/DC APIs. Cloud scripts call the Jira REST API via the built-in
 * HTTP helpers (get/post/put), which are pre-authenticated for this site.
 *
 * INSTALL: ScriptRunner -> Listeners -> Create Listener
 *   - Name:    Assign Case ID on Intake
 *   - Project: <your demo project>  (scope it to the project, not global)
 *   - Events:  "Issue Updated"      (fires on every transition; we filter below)
 *   - Paste this script into the code box and Save.
 *
 * Only the NEW -> 1. INTAKE transition does anything, so tickets sent to
 * "Not Relevant" / "Existing Case" (or left in NEW) never mint an ID and never
 * consume a sequence number.
 */

// ---------------------------------------------------------------------------
// CONFIG
final String CASE_ID_FIELD = 'customfield_XXXXX' // <-- Case ID custom field ID (see README to find it)
final String CASE_ID_NAME  = 'Case ID'           // <-- exact field name, used in JQL
final String SOURCE_STATUS = 'NEW'
final String TARGET_STATUS = '1. INTAKE'
// ---------------------------------------------------------------------------

// 1) Only act on the exact transition NEW -> 1. INTAKE.
//    `changelog` is provided to the listener for the "Issue Updated" event.
def statusItem = changelog?.items?.find { it.field == 'status' }
if (!statusItem || statusItem.fromString != SOURCE_STATUS || statusItem.toString != TARGET_STATUS) {
    return
}

def issueKey   = issue.key
def projectKey = issue.fields.project.key

// 2) Idempotency — never overwrite an ID that already exists.
def currentResp = get("/rest/api/3/issue/${issueKey}")
        .queryString('fields', CASE_ID_FIELD)
        .asObject(Map)
def existing = currentResp.body?.fields?.get(CASE_ID_FIELD)
if (existing != null && existing.toString().trim()) {
    logger.info("${issueKey} already has Case ID '${existing}' — leaving as-is")
    return
}

// 3) Current calendar year, e.g. "2026".
def year = new Date().format('yyyy')

// 4) Find the highest sequence already issued this year (paginated enhanced search).
//    We narrow with JQL to the current year, then confirm each value with a regex.
def jql = "project = \"${projectKey}\" AND \"${CASE_ID_NAME}\" ~ \"${year}\" ORDER BY created ASC"

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

// 5) Mint the next ID, zero-padded to 3 digits.
def newId = String.format('%s-%03d', year, maxSeq + 1)

// 6) Write it back via REST.
def updateResp = put("/rest/api/3/issue/${issueKey}")
        .header('Content-Type', 'application/json')
        .body([fields: [(CASE_ID_FIELD): newId]])
        .asObject(Map)

if (updateResp.status >= 200 && updateResp.status < 300) {
    logger.info("Assigned Case ID ${newId} to ${issueKey} (NEW -> 1. INTAKE)")
} else {
    logger.error("Failed to set Case ID on ${issueKey}: HTTP ${updateResp.status} — ${updateResp.body}")
}
