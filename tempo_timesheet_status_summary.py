"""
Tempo Timesheet Status Summary - WEEK-WISE (2- or 3-month window) -> Excel
=========================================================================
Walks a date range ONE WEEK AT A TIME (Mon..Sun, the way Tempo approval periods
work) and produces a single Excel workbook with TWO worksheets:

  Sheet 1  "Weekly Summary"
    One row per week, counting UNIQUE users by timesheet status:
        - Open / Unsubmitted
        - Waiting Approval
        - Approved
        - Rejected / Other   (any other status, so the row reconciles)
        - Total Users

  Sheet 2  "Open Timesheets"
    One row per (week x user) whose timesheet is OPEN/unsubmitted, with the
    user's name, email, program and the team(s) they belong to.

Range
  AUTO_LAST_N_WEEKS controls the window:
      8  weeks ~= 2 months
      13 weeks ~= 3 months
  or set AUTO_LAST_N_WEEKS = 0 and use the manual WINDOW_FROM / WINDOW_TO dates.

Scope / exclusions
  Teams are scoped to PROGRAMS (name prefix). By default the same two exclusions
  as the late-submission report are applied so "Open" means genuinely late:
  team leads and members of "Default Workload Scheme". Flip
  EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD to False to count everyone.

Notes
  - Timesheet status is per user per period, so a user in multiple in-scope
    teams is counted ONCE per week (deduped by accountId).
  - Names/emails are resolved via Jira only for the OPEN users (Sheet 2), so the
    summary sheet stays fast.
  - /timesheet-approvals/team/{id} requires the "Approve Timesheets" permission
    on the Tempo token. Teams returning 403 are skipped (printed), not fatal.

Secrets come from environment variables:
    export TEMPO_API_TOKEN="..."        # needs "Approve Timesheets" permission
    export JIRA_EMAIL="you@example.com"
    export JIRA_API_TOKEN="..."
"""

import os
import requests
from datetime import date, timedelta
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# =============================================================================
# CONFIG
# =============================================================================

TEMPO_BASE_URL  = "https://api.tempo.io/4"
TEMPO_API_TOKEN = os.environ.get("TEMPO_API_TOKEN", "")   # needs Approve Timesheets permission

JIRA_BASE_URL   = os.environ.get("JIRA_BASE_URL", "https://bunnings.atlassian.net")
JIRA_EMAIL      = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN  = os.environ.get("JIRA_API_TOKEN", "")

# A team's Program = the first prefix below that its name starts with.
PROGRAMS = ["DAIL", "Workforce", "Core", "Strategy", "Infrastructure", "Cyber", "C&S"]

DEFAULT_WORKLOAD_SCHEME = "Default Workload Scheme"
EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD = True

# Debug / reconciliation ----------------------------------------------------
# DEBUG = True prints, per team per week, the RAW member count, the status
# breakdown, and how many were excluded - so you can match a single team+week
# against the Tempo UI and find where a count mismatch comes from.
# Optionally restrict debug output to one team + one week to keep it readable:
DEBUG           = False
DEBUG_TEAM_LIKE = ""            # e.g. "Core Platform" - substring match on team name ("" = all)
DEBUG_WEEK_MON  = ""            # e.g. "2026-07-07"   - the Monday of one week ("" = all weeks)

# Reporting window ----------------------------------------------------------
# AUTO_LAST_N_WEEKS > 0  -> last N full Mon..Sun weeks up to last Sunday.
#                           8 ~= 2 months, 13 ~= 3 months.
# AUTO_LAST_N_WEEKS = 0  -> use manual WINDOW_FROM / WINDOW_TO below.
AUTO_LAST_N_WEEKS = 8
WINDOW_FROM = "2026-06-01"
WINDOW_TO   = "2026-07-31"

OUTPUT_XLSX = "Tempo Timesheet Status Summary.xlsx"

# Map Tempo status keys -> report buckets. Unknown keys fall into "other".
OPEN_KEYS     = {"OPEN"}
WAITING_KEYS  = {"WAITING_FOR_APPROVAL", "IN_REVIEW", "PENDING", "SUBMITTED", "READY_TO_REVIEW"}
APPROVED_KEYS = {"APPROVED"}

# =============================================================================

if not TEMPO_API_TOKEN or not JIRA_EMAIL or not JIRA_API_TOKEN:
    raise SystemExit(
        "Missing credentials. Set TEMPO_API_TOKEN, JIRA_EMAIL and JIRA_API_TOKEN "
        "as environment variables before running."
    )

TEMPO_HEADERS = {"Authorization": f"Bearer {TEMPO_API_TOKEN}", "Content-Type": "application/json"}
JIRA_AUTH     = (JIRA_EMAIL, JIRA_API_TOKEN)


# -- Window / week helpers ----------------------------------------------------

def resolve_window():
    if AUTO_LAST_N_WEEKS and AUTO_LAST_N_WEEKS > 0:
        today       = date.today()
        last_sunday = today - timedelta(days=today.weekday() + 1)  # most recent Sunday
        last_monday = last_sunday - timedelta(days=6)
        first_monday = last_monday - timedelta(weeks=AUTO_LAST_N_WEEKS - 1)
        return first_monday.isoformat(), last_sunday.isoformat()
    return WINDOW_FROM, WINDOW_TO


def week_periods(window_from, window_to):
    """Yield (from_iso, to_iso) Mon..Sun weeks covering the window."""
    start = date.fromisoformat(window_from)
    end   = date.fromisoformat(window_to)
    monday = start - timedelta(days=start.weekday())
    weeks = []
    while monday <= end:
        sunday = monday + timedelta(days=6)
        weeks.append((monday.isoformat(), sunday.isoformat()))
        monday += timedelta(days=7)
    return weeks


def bucket_for(status_key):
    if status_key in OPEN_KEYS:
        return "open"
    if status_key in WAITING_KEYS:
        return "waiting"
    if status_key in APPROVED_KEYS:
        return "approved"
    return "other"


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


# -- Exclusions ---------------------------------------------------------------

def build_default_workload_exclusions():
    print("Fetching workload schemes...")
    schemes  = tempo_get_all("/workload-schemes")
    excluded = set()
    for s in schemes:
        if s.get("name", "") != DEFAULT_WORKLOAD_SCHEME:
            continue
        members = tempo_get_all(f"/workload-schemes/{s.get('id')}/members")
        for m in members:
            acct = m.get("accountId") or m.get("member", {}).get("accountId")
            if acct:
                excluded.add(acct)
        print(f"  Default Workload Scheme (id={s.get('id')}): {len(excluded)} member(s) excluded.")
    if not excluded:
        print("  No members found under Default Workload Scheme (or scheme not found).")
    return excluded


# -- Teams --------------------------------------------------------------------

def get_teams_list():
    data = query(f"{TEMPO_BASE_URL}/teams")
    return [{
        "name": team["name"],
        "id":   team["id"],
        "lead": (team.get("lead") or {}).get("accountId"),
    } for team in data]


def program_for(team_name):
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


# -- Fetch one team, one week -------------------------------------------------

ERRORED_TEAMS = []   # (team_name, week_from, reason) for teams that couldn't be read


def _debug_match(team_name, from_date):
    if not DEBUG:
        return False
    if DEBUG_TEAM_LIKE and DEBUG_TEAM_LIKE.lower() not in team_name.lower():
        return False
    if DEBUG_WEEK_MON and DEBUG_WEEK_MON != from_date:
        return False
    return True


def get_team_week(team, program, from_date, to_date, lead_ids, default_workload_ids):
    """Return list of {accountId, status_key, program, team} for a team+week."""
    url = f"{TEMPO_BASE_URL}/timesheet-approvals/team/{team['id']}?from={from_date}&to={to_date}"
    try:
        r = requests.get(url, headers=TEMPO_HEADERS)
        if r.status_code != 200:
            ERRORED_TEAMS.append((team["name"], from_date, f"HTTP {r.status_code}"))
            print(f"    ! {team['name']} [{from_date}] -> HTTP {r.status_code} (skipped)")
            return []
        results = r.json().get("results", [])

        out           = []
        raw_by_status = defaultdict(int)   # before exclusions
        excluded      = 0
        for result in results:
            user_id    = result["user"]["accountId"]
            status_key = (result.get("status") or {}).get("key", "UNKNOWN")
            raw_by_status[status_key] += 1
            if EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD and (user_id in lead_ids or user_id in default_workload_ids):
                excluded += 1
                continue
            out.append({
                "accountId":  user_id,
                "status_key": status_key,
                "program":    program,
                "team":       team["name"],
            })

        if _debug_match(team["name"], from_date):
            raw_total = sum(raw_by_status.values())
            breakdown = ", ".join(f"{k}={v}" for k, v in sorted(raw_by_status.items()))
            print(f"    [DEBUG] {team['name']} [{from_date}]  members={raw_total}  "
                  f"excluded={excluded}  kept={len(out)}  | raw: {breakdown or '(none)'}")

        return out
    except Exception as e:
        ERRORED_TEAMS.append((team["name"], from_date, str(e)))
        print(f"    Error on {team['name']} [{from_date}]: {e}")
        return []


# -- Excel writing helpers ----------------------------------------------------

HEADER_FILL = PatternFill("solid", fgColor="305496")
HEADER_FONT = Font(bold=True, color="FFFFFF")
TOTAL_FONT  = Font(bold=True)


def style_header(ws, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"


def autosize(ws, ncols):
    for c in range(1, ncols + 1):
        letter = get_column_letter(c)
        width  = max((len(str(ws.cell(row=r, column=c).value or "")) for r in range(1, ws.max_row + 1)), default=10)
        ws.column_dimensions[letter].width = min(max(width + 2, 10), 50)


# -- Main ---------------------------------------------------------------------

def main():
    window_from, window_to = resolve_window()
    weeks = week_periods(window_from, window_to)
    print(f"Status summary over {len(weeks)} week(s): {window_from} -> {window_to}")
    print(f"Exclusions applied: {EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD}\n")

    default_workload_ids = build_default_workload_exclusions() if EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD else set()

    teams    = get_teams_list()
    in_scope = [t for t in teams if program_for(t["name"])]
    lead_ids = {t["lead"] for t in in_scope if t["lead"]} if EXCLUDE_LEADS_AND_DEFAULT_WORKLOAD else set()
    print(f"\nIn-scope teams              : {len(in_scope)}")
    print(f"Team leads excluded         : {len(lead_ids)}")
    print(f"Default workload excluded   : {len(default_workload_ids)}\n")

    # Per week: dedupe user -> bucket; and remember which teams an OPEN user was in.
    weekly_counts   = {}   # (wf,wt) -> {open,waiting,approved,other}
    open_detail     = {}   # (wf, accountId) -> {"programs": set, "teams": set, "wt": ..}
    seen_status_keys = set()

    for i, (wf, wt) in enumerate(weeks, 1):
        print(f"Week {i}/{len(weeks)}: {wf} -> {wt}")
        user_bucket = {}          # accountId -> bucket (deduped across teams)
        user_context = defaultdict(lambda: {"programs": set(), "teams": set()})
        for team in in_scope:
            program = program_for(team["name"])
            for rec in get_team_week(team, program, wf, wt, lead_ids, default_workload_ids):
                acct = rec["accountId"]
                seen_status_keys.add(rec["status_key"])
                b = bucket_for(rec["status_key"])
                # Keep the first bucket seen (status is per-user-per-period, so consistent).
                user_bucket.setdefault(acct, b)
                user_context[acct]["programs"].add(rec["program"])
                user_context[acct]["teams"].add(rec["team"])

        counts = {"open": 0, "waiting": 0, "approved": 0, "other": 0}
        for acct, b in user_bucket.items():
            counts[b] += 1
            if b == "open":
                open_detail[(wf, acct)] = {
                    "wt":       wt,
                    "programs": user_context[acct]["programs"],
                    "teams":    user_context[acct]["teams"],
                }
        weekly_counts[(wf, wt)] = counts

    # ---- Build workbook -----------------------------------------------------
    wb = Workbook()

    # Sheet 1: Weekly Summary
    ws1 = wb.active
    ws1.title = "Weekly Summary"
    headers1 = ["Week Start (Mon)", "Week End (Sun)", "Open / Unsubmitted",
                "Waiting Approval", "Approved", "Rejected / Other", "Total Users"]
    ws1.append(headers1)
    totals = {"open": 0, "waiting": 0, "approved": 0, "other": 0, "total": 0}
    for (wf, wt) in weeks:
        c = weekly_counts.get((wf, wt), {"open": 0, "waiting": 0, "approved": 0, "other": 0})
        total = c["open"] + c["waiting"] + c["approved"] + c["other"]
        ws1.append([wf, wt, c["open"], c["waiting"], c["approved"], c["other"], total])
        totals["open"]     += c["open"]
        totals["waiting"]  += c["waiting"]
        totals["approved"] += c["approved"]
        totals["other"]    += c["other"]
        totals["total"]    += total
    # Totals row (sum of person-weeks across the window)
    trow = ["TOTAL (person-weeks)", "", totals["open"], totals["waiting"],
            totals["approved"], totals["other"], totals["total"]]
    ws1.append(trow)
    for c in range(1, len(headers1) + 1):
        ws1.cell(row=ws1.max_row, column=c).font = TOTAL_FONT
    style_header(ws1, len(headers1))
    autosize(ws1, len(headers1))

    # Sheet 2: Open Timesheets (detail)
    ws2 = wb.create_sheet("Open Timesheets")
    headers2 = ["Week Start (Mon)", "Week End (Sun)", "Program(s)", "Team(s)",
                "Account ID", "User Name", "User Email"]
    ws2.append(headers2)
    open_rows = []
    for (wf, acct), info in open_detail.items():
        name, email = get_user_display_name(acct)
        open_rows.append([
            wf, info["wt"],
            "; ".join(sorted(info["programs"])),
            "; ".join(sorted(info["teams"])),
            acct, name, email,
        ])
    # Sort by week, then user name
    open_rows.sort(key=lambda r: (r[0], str(r[5]).lower()))
    for row in open_rows:
        ws2.append(row)
    style_header(ws2, len(headers2))
    autosize(ws2, len(headers2))

    wb.save(OUTPUT_XLSX)

    # ---- Console summary ----------------------------------------------------
    print("\n" + "=" * 60)
    print(f"  Window            : {window_from} -> {window_to} ({len(weeks)} weeks)")
    print(f"  Open person-weeks : {totals['open']}")
    print(f"  Waiting           : {totals['waiting']}")
    print(f"  Approved          : {totals['approved']}")
    print(f"  Rejected/Other    : {totals['other']}")
    print(f"  Open detail rows  : {len(open_rows)}")
    print(f"  Status keys seen  : {', '.join(sorted(seen_status_keys)) or '(none)'}")
    print(f"  Teams skipped/err : {len(ERRORED_TEAMS)}"
          + (f"  (these users are NOT in the totals)" if ERRORED_TEAMS else ""))
    for tname, twf, reason in ERRORED_TEAMS[:20]:
        print(f"      - {tname} [{twf}]: {reason}")
    if len(ERRORED_TEAMS) > 20:
        print(f"      ... and {len(ERRORED_TEAMS) - 20} more")
    print(f"\n  Workbook saved    : {OUTPUT_XLSX}")
    print("=" * 60)
    unmapped = [k for k in seen_status_keys if bucket_for(k) == 'other']
    if unmapped:
        print(f"\n  NOTE: these status keys fell into 'Rejected / Other': {', '.join(sorted(unmapped))}")
        print("        If any should count as Waiting/Approved, add them to the *_KEYS sets.")


if __name__ == "__main__":
    main()
