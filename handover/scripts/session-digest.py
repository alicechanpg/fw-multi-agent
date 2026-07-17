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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    import metrics  # P0 metric layer; optional -- digest must survive its absence
except Exception:
    metrics = None

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


def to_local(stamp):
    """Transcript timestamps are UTC ('...Z'); the audit trail is local time. Mixing them
    silently reorders the log, which is worse than a missing entry -- it reads as fact."""
    if not stamp:
        return ""
    try:
        parsed = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return parsed.astimezone().replace(tzinfo=None).isoformat(timespec="seconds")
    except Exception:
        return str(stamp)[:19]


def queued_prompts(transcript_path):
    """Recover mid-turn messages, which the UserPromptSubmit hook never sees.

    A message sent while Claude is working is queued and delivered as a `queued_command`
    attachment, so it bypasses the hook entirely -- and those are often the user cutting in
    to correct course, i.e. exactly what an audit must not miss. The harness transcript is
    the only complete record, so pull them from there.
    """
    if not transcript_path:
        return []
    path = pathlib.Path(transcript_path)
    if not path.exists():
        return []
    found = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"queued_command"' not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        att = rec.get("attachment") or {}
        if att.get("type") != "queued_command" or not att.get("prompt"):
            continue
        prompt = att["prompt"]
        # Background-task notifications are queued the same way but are machine events,
        # not the user speaking. Attributing them to the user corrupts the audit.
        if prompt.lstrip().startswith("<task-notification>"):
            continue
        found.append({"ts": to_local(rec.get("timestamp")), "prompt": prompt})
    # The same queued message appears more than once (enqueue, then delivery).
    seen, unique = set(), []
    for item in found:
        if item["prompt"] not in seen:
            seen.add(item["prompt"])
            unique.append(item)
    return unique


def render(session, events, queued=()):
    prompts = [e for e in events if e.get("event") == "UserPromptSubmit"]
    prompts = prompts + [dict(q, event="QueuedMidTurn") for q in queued]
    prompts.sort(key=lambda e: e.get("ts") or "")
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
        tag = " **[中途插話]**" if e.get("event") == "QueuedMidTurn" else ""
        lines.append(f"- `{e['ts']}`{tag} {text[:300]}")

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
    queued = queued_prompts(data.get("transcript_path"))
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    out_dir = HANDOVER / "sessions" / TERMINAL
    out_dir.mkdir(parents=True, exist_ok=True)

    digest = render(session, events, queued)
    if metrics is not None:
        try:  # P0 metrics must never break the digest or the Stop hook
            m = metrics.compute(data.get("transcript_path"), events, len(queued))
            digest += "\n" + metrics.render_md(m)
            metrics.append_record(AUDIT_DIR / "metrics.jsonl", session, m)
        except Exception:
            pass
    (out_dir / f"{stamp}-audit.md").write_text(digest, encoding="utf-8")

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
        # Exit 2 so the asyncRewake Stop hook wakes Claude to write the handover it skipped,
        # rather than only recording that it was skipped. Converges: once latest-*.md is
        # written its mtime is fresh, so the next Stop passes silently.
        print(
            f"{warning}\n\n"
            f"Write the real handover to {latest} now (what was done, what is unfinished, "
            f"next step), using sessions/{TERMINAL}/{stamp}-audit.md as the source of truth."
        )
        return 2
    return 0


try:
    sys.exit(main())
except SystemExit:
    raise
except Exception as exc:  # never block the Stop hook
    print(f"digest failed: {exc}")
    sys.exit(0)
