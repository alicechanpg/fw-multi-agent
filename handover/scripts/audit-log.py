"""Append-only session audit trail.

Fed by the UserPromptSubmit and PostToolUse hooks (see .claude/settings.local.json).
The harness runs this, not Claude, so the trail cannot be skipped by forgetting.
One JSONL line per event in handover/audit/{session_id}.jsonl.

Contract: NEVER fail and never write to stdout -- a non-zero exit or stray output
from a PostToolUse hook disrupts the tool call it is auditing.
"""
import datetime
import json
import pathlib
import sys

AUDIT_DIR = pathlib.Path("D:/mybot/handover/audit")

# Fields worth auditing per tool. Anything else is noise or too large to keep.
INPUT_FIELDS = ("command", "file_path", "description", "pattern", "prompt", "url", "old_string")
MAX_FIELD = 400
MAX_PROMPT = 4000


def summarize_input(tool_input):
    if not isinstance(tool_input, dict):
        return {}
    out = {}
    for key in INPUT_FIELDS:
        if key in tool_input and tool_input[key] not in (None, ""):
            out[key] = str(tool_input[key])[:MAX_FIELD]
    return out


def build_record(data):
    event = data.get("hook_event_name") or "?"
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "event": event,
        # session id per record so a line is self-joining -- the trace-id idea from
        # the 2026-07-22/23 audit suggestions. Previously it lived only in the filename,
        # so concatenated/moved lines lost which session they came from.
        "session": data.get("session_id"),
        "cwd": data.get("cwd"),
    }
    if event == "unparsed":
        # Keep the payload -- an audit entry that records only "something happened"
        # is worse than useless, it looks like coverage.
        rec["raw"] = data.get("raw", "")
    elif event == "UserPromptSubmit":
        rec["prompt"] = (data.get("prompt") or "")[:MAX_PROMPT]
    else:
        rec["tool"] = data.get("tool_name")
        rec["input"] = summarize_input(data.get("tool_input"))
        resp = data.get("tool_response")
        if isinstance(resp, dict):
            # Record failures explicitly: an audit that only shows successes is a lie.
            rec["ok"] = not resp.get("is_error", False)
    return rec


def main():
    # Read bytes, not text: Windows defaults stdin to cp950, which raises on the UTF-8
    # the harness sends and would silently drop every Chinese prompt.
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except Exception:
        data = {"hook_event_name": "unparsed", "raw": raw[:MAX_FIELD]}

    session = str(data.get("session_id") or "unknown").replace("/", "_")
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(build_record(data), ensure_ascii=False)
    with open(AUDIT_DIR / f"{session}.jsonl", "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


try:
    main()
except Exception:
    pass  # auditing must never break the tool call it observes
sys.exit(0)
