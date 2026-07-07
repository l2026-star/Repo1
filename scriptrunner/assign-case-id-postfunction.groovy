/*
 * ScriptRunner post-function — Assign yearly sequential Case ID on NEW -> 1. INTAKE
 * ----------------------------------------------------------------------------------
 * Generates a unique, human-friendly ID (YYYY-NNN, e.g. 2026-001, 2026-002 ...)
 * the FIRST time a ticket enters the "1. INTAKE" status from "NEW".
 *
 * WHERE TO INSTALL
 *   Workflow  ->  transition  NEW  ->  1. INTAKE
 *   Add a "Script post-function".
 *   Position it BEFORE the built-in "Update change history for an issue" step so the
 *   value is persisted as part of the transition.
 *
 * WHY ONLY THIS TRANSITION
 *   Because the number is minted only on NEW -> 1. INTAKE, tickets that go
 *   NEW -> "Not Relevant" or NEW -> "Existing Case" (or that simply stay in NEW)
 *   never receive an ID and therefore never consume a sequence number. The counter
 *   only ever reflects tickets that actually reached Intake.
 *
 * IDEMPOTENT
 *   If the issue already has a Case ID it is left untouched, so re-entering Intake
 *   later (e.g. Pended -> Intake) will not overwrite the value or burn a new number.
 */

import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.bc.issue.search.SearchService
import com.atlassian.jira.jql.builder.JqlQueryBuilder
import com.atlassian.jira.web.bean.PagerFilter
import java.util.Calendar

// ---------------------------------------------------------------------------
// CONFIG — change this to match the exact name of your custom field.
// Create it first as a short "Text Field (single line)" if it doesn't exist.
final String FIELD_NAME = "Case ID"
// ---------------------------------------------------------------------------

def customFieldManager = ComponentAccessor.customFieldManager
def caseIdField = customFieldManager.getCustomFieldObjectsByName(FIELD_NAME)?.getAt(0)
assert caseIdField : "Custom field named '${FIELD_NAME}' was not found — check the name / field context."

// 1) Idempotency guard — never regenerate an ID that already exists.
def existing = issue.getCustomFieldValue(caseIdField)
if (existing != null && existing.toString().trim()) {
    return
}

// 2) Current calendar year, e.g. "2026".
def year = Calendar.instance.get(Calendar.YEAR).toString()

// 3) Find the highest sequence already issued for this year (this project).
//    We search only issues that already carry a "YYYY-*" Case ID, so tickets
//    still in NEW / Not Relevant / Existing Case (which have no ID) are ignored.
def user = ComponentAccessor.jiraAuthenticationContext.loggedInUser
def searchService = ComponentAccessor.getComponent(SearchService)

def query = JqlQueryBuilder.newBuilder()
        .where()
        .project(issue.projectObject.id)
        .and()
        .customField(caseIdField.idAsLong).like("${year}-*")
        .buildQuery()

def results = searchService.search(user, query, PagerFilter.unlimitedFilter)

int maxSeq = 0
results.results.each { docIssue ->
    def val = docIssue.getCustomFieldValue(caseIdField)?.toString()
    if (val && val ==~ /${year}-\d+/) {
        int seq = val.substring(year.length() + 1) as int
        if (seq > maxSeq) maxSeq = seq
    }
}

// 4) Mint the next ID, zero-padded to 3 digits (2026-001, 2026-002, ... 2026-999+).
def nextSeq = maxSeq + 1
def newId = String.format("%s-%03d", year, nextSeq)

// 5) Set it on the transitioning issue. Because this post-function runs before
//    "Update change history", the value is stored as part of the transition.
issue.setCustomFieldValue(caseIdField, newId)

log.info("Assigned Case ID ${newId} to ${issue.key} on NEW -> 1. INTAKE")
