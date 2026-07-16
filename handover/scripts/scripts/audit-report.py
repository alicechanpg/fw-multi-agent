"""Aggregate the session audit trails into a review report.

Usage:  python audit-report.py [days]      (default: 7)

Reads handover/audit/*.jsonl and writes handover/audit/report-{today}.md.
Prints only a short ASCII summary to stdout -- this console is cp950 and mangles
Chinese, so the real report goes to the file (open it in Notepad++).

This script only COUNTS things. Judging what to improve is Claude's job -- see
.claude/commands/audit-review.md.
"""
import collections
import datetime
import json
import pathlib
import re
import sys

AUDIT_DIR = pathlib.Path("D:/mybot/handover/audit")

# Prompts that look like the user correcting or re-steering me. These are the highest
# value signal for "what should improve" -- each one is a round trip that should not
# have been needed. Deliberately over-inclusive: it is a shortlist to read, not a verdict.
CORRECTION = re.compile(
    r"不是|不對|錯|重來|算了|我說|你有沒有|為什麼|還是|又|沒有嗎|確定|"
    r"\bno\b|\bwrong\b|actually|instead",
    re.IGNORECASE,
)


def load_sessions(days):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    sessions = {}
    for path in sorted(AUDIT_DIR.glob("*.jsonl")):
        if path.name.startswith("report-"):
            continue
        events = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        if not events:
            continue
        try:
            first = datetime.datetime.fromisoformat(events[0]["ts"])
        except Exception:
            continue
        if first >= cutoff:
            sessions[path.stem] = events
    return sessions


def label_of(event):
    inp = event.get("input") or {}
    text = inp.get("command") or inp.get("file_path") or inp.get("description") or ""
    return " ".join(str(text).split())


def build(sessions, days):
    out = [
        f"# Audit Review — 最近 {days} 天",
        "",
        f"產生時間 {datetime.datetime.now():%Y-%m-%d %H:%M}｜"
        f"{len(sessions)} 個 session",
        "",
        "## 每個 session",
        "",
        "| session | 開始 | prompts | tools | 失敗 |",
        "|---|---|---|---|---|",
    ]
    all_fail, all_corr = [], []
    tool_calls = collections.Counter()
    tool_fails = collections.Counter()
    cmd_counter = collections.Counter()

    for sid, events in sessions.items():
        prompts = [e for e in events if e.get("event") == "UserPromptSubmit"]
        tools = [e for e in events if e.get("event") == "PostToolUse"]
        fails = [e for e in tools if e.get("ok") is False]
        out.append(
            f"| `{sid[:8]}` | {events[0]['ts'][:16]} | {len(prompts)} | {len(tools)} | {len(fails)} |"
        )
        all_fail += fails
        for e in tools:
            tool_calls[e.get("tool")] += 1
            if e.get("ok") is False:
                tool_fails[e.get("tool")] += 1
            lab = label_of(e)
            if lab:
                cmd_counter[lab[:80]] += 1
        for p in prompts:
            if CORRECTION.search(p.get("prompt") or ""):
                all_corr.append(p)

    total = sum(tool_calls.values())
    rate = (len(all_fail) / total * 100) if total else 0
    out += [
        "",
        "## 失敗率",
        "",
        f"總共 {total} 次 tool call，{len(all_fail)} 次失敗（{rate:.1f}%）。",
        "",
        "| tool | 呼叫 | 失敗 |",
        "|---|---|---|",
    ]
    for tool, n in tool_calls.most_common():
        out.append(f"| {tool} | {n} | {tool_fails.get(tool, 0)} |")

    out += ["", "## 失敗的動作（逐筆，要看這裡找根因）", ""]
    out += [f"- `{e['ts']}` **{e.get('tool')}**: {label_of(e)[:200]}" for e in all_fail] or ["_無_"]

    out += [
        "",
        "## 使用者疑似在糾正我的 prompt（改善空間的主要線索）",
        "",
        "_每一筆都代表一次本來不該發生的來回。這是要人讀的清單，不是判決。_",
        "",
    ]
    out += [
        f"- `{p['ts']}` {' '.join((p.get('prompt') or '').split())[:200]}" for p in all_corr
    ] or ["_無_"]

    repeats = [(c, n) for c, n in cmd_counter.most_common(10) if n > 2]
    out += ["", "## 重複超過 2 次的動作（可能是重試/繞圈）", ""]
    out += [f"- ({n}x) `{c}`" for c, n in repeats] or ["_無_"]

    return "\n".join(out) + "\n", total, len(all_fail), len(all_corr)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    sessions = load_sessions(days)
    if not sessions:
        print(f"No audit trails in the last {days} days. Nothing to review.")
        return
    report, total, fails, corrections = build(sessions, days)
    dest = AUDIT_DIR / f"report-{datetime.datetime.now():%Y-%m-%d}.md"
    dest.write_text(report, encoding="utf-8")
    # ASCII only: this console is cp950.
    print(f"sessions={len(sessions)} tool_calls={total} failures={fails} corrections={corrections}")
    print(f"report written: {dest}")


main()
