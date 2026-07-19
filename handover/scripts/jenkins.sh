#!/usr/bin/env bash
# jenkins.sh - thin wrapper over the Positive Grid Jenkins API.
#
# WHY: prior sessions re-assembled the identical auth string
#   -u "alice.chan@positivegrid.com:$(cat D:/mybot/git/tool/.jenkins-token)"
# 500+ times (audit-review 2026-07-19 flagged the repetition). This wraps it
# once so the token/base/auth is never retyped again.
#
# Auth = HTTP basic (email : personal API token). This is exactly what the
# session logs show works; not invented. No jq in this env -> crumb via python.
# Runs under Git Bash on Windows.
#
# USAGE:
#   jenkins.sh jobs                          # list all job names
#   jenkins.sh info    <JOB> [tree]          # job JSON (optional Jenkins ?tree=)
#   jenkins.sh build   <JOB> <N> [tree]      # build #N JSON
#   jenkins.sh queue   <ITEM_ID>             # queue item JSON (after a trigger)
#   jenkins.sh console <JOB> <N>             # build #N consoleText
#   jenkins.sh trigger <JOB> [KEY=VAL ...]   # buildWithParameters (POST + CSRF crumb)
#
# Override defaults via env: JENKINS_USER, JENKINS_TOKEN_FILE
set -euo pipefail

JENKINS_USER="${JENKINS_USER:-alice.chan@positivegrid.com}"
JENKINS_TOKEN_FILE="${JENKINS_TOKEN_FILE:-D:/mybot/git/tool/.jenkins-token}"
BASE="https://jk-builds.positivegrid.com/jenkins"

die() { echo "jenkins.sh: $*" >&2; exit 2; }

_require_token() {
  # NOTE: must be its own guard (not inside the $(...) below): a `die`/exit
  # inside command substitution only kills the subshell, so curl would still
  # run with empty auth and hang on the network. Call this in _get's context.
  [ -r "$JENKINS_TOKEN_FILE" ] || die "token file not readable: $JENKINS_TOKEN_FILE (set JENKINS_TOKEN_FILE)"
}
_userpass() { printf '%s:%s' "$JENKINS_USER" "$(tr -d '[:space:]' < "$JENKINS_TOKEN_FILE")"; }
_get() { _require_token; curl -sS --connect-timeout 10 --max-time 120 -u "$(_userpass)" "$@"; }

cmd="${1:-help}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  jobs)
    _get "$BASE/api/json?tree=jobs[name]" ;;
  info)
    [ $# -ge 1 ] || die "usage: info <JOB> [tree]"
    _get "$BASE/job/$1/api/json${2:+?tree=$2}" ;;
  build)
    [ $# -ge 2 ] || die "usage: build <JOB> <N> [tree]"
    _get "$BASE/job/$1/$2/api/json${3:+?tree=$3}" ;;
  queue)
    [ $# -ge 1 ] || die "usage: queue <ITEM_ID>"
    _get "$BASE/queue/item/$1/api/json" ;;
  console)
    [ $# -ge 2 ] || die "usage: console <JOB> <N>"
    _get "$BASE/job/$1/$2/consoleText" ;;
  trigger)
    [ $# -ge 1 ] || die "usage: trigger <JOB> [KEY=VAL ...]"
    job="$1"; shift
    # Jenkins CSRF protection: fetch a crumb, then POST with it.
    crumb_json="$(_get "$BASE/crumbIssuer/api/json")" || die "could not fetch CSRF crumb"
    crumb_pair="$(printf '%s' "$crumb_json" | python -c "import sys,json; d=json.load(sys.stdin); print(d['crumbRequestField'], d['crumb'])")" \
      || die "could not parse crumb JSON"
    crumb_field="${crumb_pair%% *}"; crumb_value="${crumb_pair#* }"
    params=()
    for kv in "$@"; do params+=(--data-urlencode "$kv"); done
    # -D - prints response headers (shows the queued item Location); body discarded.
    _get -X POST -H "$crumb_field: $crumb_value" "${params[@]}" \
      "$BASE/job/$job/buildWithParameters" -D - -o /dev/null ;;
  help|--help|-h|*)
    sed -n '2,20p' "$0"; exit 0 ;;
esac
