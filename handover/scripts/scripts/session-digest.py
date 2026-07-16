"""Turn a session's audit trail into a readable session log, and flag a stale handover.

Called by the Stop hook via session-handoff.sh, with the hook JSON on stdin.

Why this exists: the Stop hook used to just copy latest-{terminal}.md into the archive.
If Claude never updated that file, it archived a weeks-old one and the session left no
trace -- which is exactly what happened on 2026-07-16. The digest is built from the
audit trail instead, so a record exists whether or not Claude remembered to write one.

Prints a hook JSON object on stdout (systemMessage when the handover is stale).
"""
import datetime
import json
import pathlib
import sys

HANDOVER = pathlib.Path("D:/mybot/handover")
AUDIT_DIR = HANDOVER / "audit"
TERMINAL = "mybot"


def load_trail(session):
    path = AUDIT_DIR / f"{session}.jsonl"
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events


def render(session, events):
    prompts = [e for e in events if e.get("event") == "UserPromptSubmit"]
    tools = [e for e in events if e.get("event") == "PostToolUse"]
    failed = [e for e in tools if e.get("ok") is False]
    started = events[0]["ts"] if events else "?"
    ended = events[-1]["ts"] if events else "?"

    lines = [
        f"# Session Audit ({TERMINAL}) — {started} → {ended}",
        "",
        f"Session id: `{session}`  ",
        f"Auto-generated from the audit trail by the Stop hook. "
        f"{len(prompts)} prompts, {len(tools)} recorded tool calls, {len(failed)} failed.",
        "",
        "## What the user asked",
        "",
    ]
    for e in prompts:
        text = " ".join((e.get("prompt") or "").split())
        lines.append(f"- `{e['ts']}` {text[:300]}")

    lines += ["", "## What was done", ""]
    for e in tools:
        detail = e.get("input") or {}
        label = detail.get("command") or detail.get("file_path") or detail.get("description") or ""
        label = " ".join(str(label).split())[:160]
        mark = "" if e.get("ok") is not False else " **[FAILED]**"
        lines.append(f"- `{e['ts']}` {e.get('tool')}: {label}{mark}")

    if not events:
        lines += ["", "_No audit trail recorded for this session._"]
    return "\n".join(lines) + "\n"


def main():
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except Exception:
        data = {}
    session = str(data.get("session_id") or "unknown").replace("/", "_")

    events = load_trail(session)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    out_dir = HANDOVER / "sessions" / TERMINAL
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{stamp}-audit.md").write_text(render(session, events), encoding="utf-8")

    # Staleness: was latest-{terminal}.md actually touched during this session?
    latest = HANDOVER / f"latest-{TERMINAL}.md"
    warning = None
    if events:
        first_ts = datetime.datetime.fromisoformat(events[0]["ts"]).timestamp()
        if not latest.exists():
            warning = f"latest-{TERMINAL}.md does not exist."
        elif latest.stat().st_mtime < first_ts:
            age = datetime.datetime.fromtimestamp(latest.stat().st_mtime)
            warning = (
                f"latest-{TERMINAL}.md was NOT updated this session "
                f"(last written {age:%Y-%m-%d %H:%M}). The archived handover is stale; "
                f"the auto-generated audit at sessions/{TERMINAL}/{stamp}-audit.md is the "
                f"only real record."
            )

    if warning:
        print(json.dumps({"systemMessage": f"[handover] {warning}"}, ensure_ascii=False))
    else:
        print(json.dumps({"suppressOutput": True}))


try:
    main()
except Exception as exc:  # never block the Stop hook
    print(json.dumps({"systemMessage": f"[handover] digest failed: {exc}"}, ensure_ascii=False))
sys.exit(0)
