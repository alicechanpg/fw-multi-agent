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
        "## 失敗率（audit trail — 結構性看不到失敗）",
        "",
        "> ⚠️ PostToolUse hook **在工具失敗時不觸發**（2026-07-24 exit-7 探針：失敗指令零紀錄）。"
        "所以這裡的失敗數恆為 0，**不是品質證據**。真實失敗率見下方 KPI 趨勢的『真失敗%』欄"
        "（取自 harness transcript）。",
        "",
        f"總共 {total} 次 tool call（僅成功），{len(all_fail)} 次失敗（{rate:.1f}%）。",
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

    out += metrics_trend(days)

    return "\n".join(out) + "\n", total, len(all_fail), len(all_corr)


def _fmt(n):
    if n is None:
        return "—"
    if isinstance(n, (int, float)) and n >= 1000:
        return f"{n/1000:,.0f}k"
    return str(n)


def metrics_trend(days):
    """KPI trend from metrics.jsonl (written per session by metrics.py at Stop).

    A trend, not a verdict: these are diagnostic signals for where work stalls, NOT a
    scorecard to optimise -- treating them as a target invites gaming (see spec §1.2).
    """
    path = AUDIT_DIR / "metrics.jsonl"
    if not path.exists():
        return ["", "## 效率 / 成本 趨勢 (KPI)", "", "_尚無 metrics.jsonl（下次 session 結束後產生）_"]
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if (r.get("date") or "") >= cutoff:
            rows.append(r)
    out = ["", "## 效率 / 成本 趨勢 (KPI)", "",
           "_診斷訊號，非計分板；當成 KPI 去衝會被 game（見 spec §1.2）。"
           "`插話` 是試誤代理指標，非確認糾正。_", "",
           "| session | 日期 | output | cache_rd | prompts | 插話 | tools | 真失敗% | out/p | 插話/p |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        # 真失敗% from transcript (fail_rate_real); rows written before 2026-07-24 lack
        # it -> show "—" rather than the audit-based fail_rate (which is a blind 0).
        real = r.get("fail_rate_real", "—")
        rej = r.get("tool_rejected")
        real_cell = f"{real}" + (f" (拒{rej})" if rej else "") if real not in (None, "—") else "—"
        out.append(
            f"| `{str(r.get('session'))[:8]}` | {r.get('date','')} | {_fmt(r.get('out_tokens'))} | "
            f"{_fmt(r.get('cache_read'))} | {r.get('prompts')} | {r.get('interjections')} | "
            f"{r.get('tool_calls')} | {real_cell} | {_fmt(r.get('out_per_prompt'))} | "
            f"{r.get('interj_per_prompt')} |"
        )
    if not rows:
        out.append("| _窗內無資料_ |||||||||| ")
    return out


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
