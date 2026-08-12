"""
Tempo Timesheet Late-Submission Report - MULTI-WEEK (e.g. a 2-month window)
==========================================================================
Same idea as the weekly report, but instead of one period it walks the window
ONE WEEK AT A TIME (Mon..Sun, the way Tempo approval periods actually work) and
then rolls the results up PER USER so you can see repeat offenders.

Why week-by-week and not one wide from/to?
  Tempo's /timesheet-approvals endpoint reports the approval status of a
  timesheet *period*. Periods are weekly, so a single 2-month from/to collapses
  everything into one verdict and loses "which weeks were missed". Looping the
  weeks keeps that detail and is the reliable way to cover a long window.

Outputs
  - ONE CSV PER PROGRAM   - each late user in that program with a "Weeks Late"
                            count, the actual weeks they missed, their teams and
                            the approver(s) the timesheets are pending on.
  - ONE DEDUPED CSV        - every late user once, across all programs, ranked by
                            how many weeks they were late (worst first).

Exclusions (unchanged): team leads, and members of "Default Workload Scheme".
Names/emails resolved via the Jira API.

NOTE: /timesheet-approvals/team/{id} requires the "Approve Timesheets" permission
on the Tempo token. Teams that return 403 are skipped (printed), not fatal.
"""

import os
import requests
import csv
from datetime import date, timedelta
from collections import defaultdict

# =============================================================================
# CONFIG
# =============================================================================
# Secrets are read from environment variables so nothing sensitive is committed.
# Set them before running, e.g.:
#   export TEMPO_API_TOKEN="..."        # needs "Approve Timesheets" permission
#   export JIRA_EMAIL="you@example.com"
#   export JIRA_API_TOKEN="..."

TEMPO_BASE_URL  = "https://api.tempo.io/4"
TEMPO_API_TOKEN = os.environ.get("TEMPO_API_TOKEN", "")   # needs Approve Timesheets permission

# Jira - used to resolve display names/emails
JIRA_BASE_URL   = os.environ.get("JIRA_BASE_URL", "https://bunnings.atlassian.net")
JIRA_EMAIL      = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN  = os.environ.get("JIRA_API_TOKEN", "")

if not TEMPO_API_TOKEN or not JIRA_EMAIL or not JIRA_API_TOKEN:
    raise SystemExit(
        "Missing credentials. Set TEMPO_API_TOKEN, JIRA_EMAIL and JIRA_API_TOKEN "
        "as environment variables before running."
    )

# A team's Program = the first prefix below that its name starts with.
PROGRAMS = ["DAIL", "Workforce", "Core", "Strategy", "Infrastructure", "Cyber", "C&S"]

DEFAULT_WORKLOAD_SCHEME = "Default Workload Scheme"

# Reporting window ----------------------------------------------------------
# AUTO_LAST_N_WEEKS > 0  -> the last N full Mon..Sun weeks up to last Sunday.
#                           (8 weeks ~= 2 months, and aligns to Tempo periods.)
# AUTO_LAST_N_WEEKS = 0  -> use the manual WINDOW_FROM / WINDOW_TO below.
AUTO_LAST_N_WEEKS = 8
WINDOW_FROM = "2026-06-01"
WINDOW_TO   = "2026-07-31"

# =============================================================================

TEMPO_HEADERS = {"Authorization": f"Bearer {TEMPO_API_TOKEN}", "Content-Type": "application/json"}
JIRA_AUTH     = (JIRA_EMAIL, JIRA_API_TOKEN)


# -- Period / week helpers ----------------------------------------------------

def resolve_window():
    """Return (window_from, window_to) as ISO date strings."""
    if AUTO_LAST_N_WEEKS and AUTO_LAST_N_WEEKS > 0:
        today       = date.today()
        last_sunday = today - timedelta(days=today.weekday() + 1)  # most recent Sunday
        last_monday = last_sunday - timedelta(days=6)
        first_monday = last_monday - timedelta(weeks=AUTO_LAST_N_WEEKS - 1)
        return first_monday.isoformat(), last_sunday.isoformat()
    return WINDOW_FROM, WINDOW_TO


def week_periods(window_from, window_to):
    """
    Yield (from_iso, to_iso) Mon..Sun weekly periods covering the window.
    The first week is snapped back to the Monday on/just before window_from so
    every emitted period is a clean, Tempo-aligned week.
    """
    start = date.fromisoformat(window_from)
    end   = date.fromisoformat(window_to)
    monday = start - timedelta(days=start.weekday())   # Monday of the start week
    weeks = []
    while monday <= end:
        sunday = monday + timedelta(days=6)
        weeks.append((monday.isoformat(), sunday.isoformat()))
        monday += timedelta(days=7)
    return weeks


# -- Tempo pagination helpers -------------------------------------------------

def tryRequest(url):
    response = requests.get(url, headers=TEMPO_HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch data for {url} with {response.status_code}")
        return [], None
    response = response.json()
    return response.get("results", []), response.get("metadata", {}).get("next", None)


def query(url):
    if not url:
        return []
    values, nxt = tryRequest(url)
    return values + query(nxt)


def tempo_get_all(path):
    """Paginated GET against a Tempo v4 path. Returns all results."""
    results = []
    url     = f"{TEMPO_BASE_URL}{path}"
    params  = {"limit": 50}
    while url:
        r = requests.get(url, headers=TEMPO_HEADERS, params=params)
        if r.status_code != 200:
            print(f"  ! {url} -> {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        results.extend(data.get("results", []))
        url    = data.get("metadata", {}).get("next")
        params = {}
    return results


# -- Workload scheme exclusion ------------------------------------------------

def build_default_workload_exclusions():
    """Returns a set of accountIds assigned to the Default Workload Scheme."""
    print("Fetching workload schemes...")
    schemes  = tempo_get_all("/workload-schemes")
    excluded = set()

    for s in schemes:
        sid   = s.get("id")
        sname = s.get("name", "")
        if sname != DEFAULT_WORKLOAD_SCHEME:
            continue
        members = tempo_get_all(f"/workload-schemes/{sid}/members")
        for m in members:
            acct = m.get("accountId") or m.get("member", {}).get("accountId")
            if acct:
                excluded.add(acct)
        print(f"  Default Workload Scheme (id={sid}): {len(excluded)} member(s) will be excluded.")

    if not excluded:
        print("  No members found under Default Workload Scheme (or scheme not found).")
    return excluded


# -- Teams --------------------------------------------------------------------

def get_teams_list():
    """Return teams with their lead account ID."""
    data = query(f"{TEMPO_BASE_URL}/teams")
    return [{
        "name": team["name"],
        "id":   team["id"],
        "lead": (team.get("lead") or {}).get("accountId"),
    } for team in data]


def program_for(team_name):
    """Return the Program a team belongs to, or None if out of scope."""
    for p in PROGRAMS:
        if team_name.startswith(p):
            return p
    return None


# -- Name resolution via Jira -------------------------------------------------

_name_cache = {}

def get_user_display_name(account_id):
    if not account_id:
        return "-", "-"
    if account_id in _name_cache:
        return _name_cache[account_id]
    try:
        r = requests.get(f"{JIRA_BASE_URL}/rest/api/3/user",
                         params={"accountId": account_id}, auth=JIRA_AUTH)
        if r.status_code == 200:
            d   = r.json()
            res = (d.get("displayName") or "-", d.get("emailAddress") or "-")
        else:
            res = ("-", "-")
    except Exception as e:
        print(f"  [JIRA ERR] {account_id}: {e}")
        res = ("-", "-")
    _name_cache[account_id] = res
    return res


# -- Open (late) timesheets for a team, for ONE week --------------------------

def get_open_timesheets_for_week(team, program, from_date, to_date, lead_ids, default_workload_ids):
    """Return a list of OPEN rows for a single team for a single Mon..Sun week."""
    url = f"{TEMPO_BASE_URL}/timesheet-approvals/team/{team['id']}?from={from_date}&to={to_date}"
    try:
        response = requests.get(url, headers=TEMPO_HEADERS)
        response.raise_for_status()
        data = response.json()

        rows             = []
        skipped_lead     = 0
        skipped_workload = 0

        for result in data.get("results", []):
            if result.get("status", {}).get("key") != "OPEN":
                continue

            user_id = result["user"]["accountId"]

            if user_id in lead_ids:            # Exclusion 1 - team leads
                skipped_lead += 1
                continue
            if user_id in default_workload_ids:  # Exclusion 2 - default workload
                skipped_workload += 1
                continue

            reviewer    = result.get("reviewer") or {}
            reviewer_id = reviewer.get("accountId")

            rows.append({
                "Program":     program,
                "Team Name":   team["name"],
                "Account ID":  user_id,
                "Reviewer ID": reviewer_id,
                "Week":        from_date,   # Monday of the late week
            })

        if skipped_lead or skipped_workload:
            print(f"      excluded {skipped_lead} lead(s), {skipped_workload} default-workload")
        return rows

    except Exception as e:
        print(f"    Error on {team['name']} [{from_date}]: {e}")
        return []


# -- Main ---------------------------------------------------------------------

def main():
    window_from, window_to = resolve_window()
    weeks = week_periods(window_from, window_to)
    print(f"Late-submission review over {len(weeks)} week(s): {window_from} -> {window_to}\n")

    default_workload_ids = build_default_workload_exclusions()

    teams    = get_teams_list()
    in_scope = [t for t in teams if program_for(t["name"])]
    lead_ids = {t["lead"] for t in in_scope if t["lead"]}
    print(f"\nIn-scope teams              : {len(in_scope)}")
    print(f"Team leads excluded         : {len(lead_ids)}")
    print(f"Default workload excluded   : {len(default_workload_ids)}\n")

    # Collect every (user, week) OPEN record across all weeks -----------------
    all_records = []
    for i, (wf, wt) in enumerate(weeks, 1):
        print(f"Week {i}/{len(weeks)}: {wf} -> {wt}")
        for team in in_scope:
            program = program_for(team["name"])
            all_records.extend(
                get_open_timesheets_for_week(team, program, wf, wt, lead_ids, default_workload_ids)
            )

    # Aggregate per (user, program) -------------------------------------------
    # key = (account_id, program) so the per-program CSVs list a user once with
    # their total weeks-late in that program.
    per_prog = defaultdict(lambda: {"weeks": set(), "teams": set(), "reviewers": set()})
    # And per user overall for the deduped file.
    per_user = defaultdict(lambda: {"weeks": set(), "programs": set(), "teams": set(), "reviewers": set()})

    for r in all_records:
        acct, prog, wk = r["Account ID"], r["Program"], r["Week"]

        pk = (acct, prog)
        per_prog[pk]["weeks"].add(wk)
        per_prog[pk]["teams"].add(r["Team Name"])
        if r["Reviewer ID"]:
            per_prog[pk]["reviewers"].add(r["Reviewer ID"])

        per_user[acct]["weeks"].add(wk)
        per_user[acct]["programs"].add(prog)
        per_user[acct]["teams"].add(r["Team Name"])
        if r["Reviewer ID"]:
            per_user[acct]["reviewers"].add(r["Reviewer ID"])

    def reviewer_names(ids):
        names = sorted({get_user_display_name(rid)[0] for rid in ids})
        return "; ".join(n for n in names if n and n != "-") or "-"

    # ---- One CSV per Program ------------------------------------------------
    prog_files = []
    rows_by_prog = defaultdict(list)
    for (acct, prog), agg in per_prog.items():
        name, email = get_user_display_name(acct)
        rows_by_prog[prog].append({
            "Team Name":              "; ".join(sorted(agg["teams"])),
            "Account ID":             acct,
            "User Name":              name,
            "User Email":             email,
            "Weeks Late":             len(agg["weeks"]),
            "Weeks (Mon)":            "; ".join(sorted(agg["weeks"])),
            "Approver(s) Pending On": reviewer_names(agg["reviewers"]),
        })

    fields = ["Team Name", "Account ID", "User Name", "User Email",
              "Weeks Late", "Weeks (Mon)", "Approver(s) Pending On"]
    for prog, rows in rows_by_prog.items():
        rows.sort(key=lambda r: (-r["Weeks Late"], r["User Name"].lower()))
        fname = f"CIO Late Submission - {prog} {window_from}_to_{window_to}.csv"
        with open(fname, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        prog_files.append((prog, fname, len(rows)))

    # ---- One deduped CSV (all users, once, worst-first) ---------------------
    all_file = f"CIO Late Submission - All Users (deduped) {window_from}_to_{window_to}.csv"
    with open(all_file, "w", newline="", encoding="utf-8-sig") as f:
        fields = ["User Name", "User Email", "Account ID", "Weeks Late",
                  "Program(s)", "Teams (Late In)", "Weeks (Mon)", "Approver(s) Pending On"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        ordered = sorted(per_user.items(),
                         key=lambda kv: (-len(kv[1]["weeks"]),
                                         get_user_display_name(kv[0])[0].lower()))
        for acct, agg in ordered:
            name, email = get_user_display_name(acct)
            w.writerow({
                "User Name":              name,
                "User Email":             email,
                "Account ID":             acct,
                "Weeks Late":             len(agg["weeks"]),
                "Program(s)":             "; ".join(sorted(agg["programs"])),
                "Teams (Late In)":        "; ".join(sorted(agg["teams"])),
                "Weeks (Mon)":            "; ".join(sorted(agg["weeks"])),
                "Approver(s) Pending On": reviewer_names(agg["reviewers"]),
            })

    # ---- Summary ------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"  Window                  : {window_from} -> {window_to} ({len(weeks)} weeks)")
    print(f"  Total OPEN (user-weeks) : {len(all_records)}")
    print(f"  Unique late users       : {len(per_user)}")
    for prog, fname, n in sorted(prog_files):
        print(f"    {prog:<16} {n:>4} users -> {fname}")
    print(f"\n  Deduped all-users file  : {all_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
