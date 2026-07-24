"""Per-session efficiency / quality metrics -- P0 of the SOP-governance system.

Pure and read-only: no writes from compute(), no model calls, and compute() never
raises (returns partial data with None for anything it could not read). This is the
measuring stick the rest of the system is judged against -- see
docs/superpowers/specs/2026-07-17-sop-governance-p0-metrics-design.md.

Called by session-digest.py at Stop. tokens come from the harness transcript;
tool/prompt counts come from the already-loaded audit trail; interjections come from
the queued-prompt count the digest already computed (so we don't re-read the transcript
twice).
"""
import datetime
import json
import pathlib


def _transcript_usage(transcript_path):
    """Sum main-thread token usage from the harness transcript.

    Returns (totals, by_model) or (None, None) if the transcript is unreadable.
    Sidechain (subagent) messages are excluded on purpose -- their usage lives in
    separate task transcripts, so counting only what is here keeps the number honest.
    """
    if not transcript_path:
        return None, None
    path = pathlib.Path(transcript_path)
    if not path.exists():
        return None, None
    totals = {"out_tokens": 0, "cache_read": 0, "cache_create": 0, "input_tokens": 0, "turns": 0}
    by_model = {}
    saw_any = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"usage"' not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("isSidechain"):
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        u = msg.get("usage")
        if not isinstance(u, dict):
            continue
        saw_any = True
        out = u.get("output_tokens", 0) or 0
        totals["out_tokens"] += out
        totals["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
        totals["cache_create"] += u.get("cache_creation_input_tokens", 0) or 0
        totals["input_tokens"] += u.get("input_tokens", 0) or 0
        totals["turns"] += 1
        model = msg.get("model") or "?"
        by_model[model] = by_model.get(model, 0) + out
    if not saw_any:
        return None, None
    return totals, by_model


def _is_rejection(content):
    """A user-declined tool call is not a failure -- keep the two apart."""
    if isinstance(content, list):
        content = " ".join(b.get("text", "") if isinstance(b, dict) else str(b)
                            for b in content)
    low = str(content).lower()
    return ("tool use was rejected" in low
            or "user doesn't want to proceed" in low
            or "user rejected" in low)


def _transcript_failures(transcript_path):
    """Count REAL tool failures from the harness transcript.

    Why not the audit trail: the PostToolUse hook (audit-log.py) never fires on a
    failed tool call -- verified 2026-07-24 by an exit-7 probe that left no audit
    record -- so the trail's tool_fails is structurally ~always 0 and its fail_rate
    is a lie. The transcript is the only place failures are recorded: tool_result
    blocks carry is_error. Returns (real_fails, rejected, results_seen) or None if
    the transcript is unreadable. Sidechain (subagent) results are excluded, matching
    the token scope in _transcript_usage.
    """
    if not transcript_path:
        return None
    path = pathlib.Path(transcript_path)
    if not path.exists():
        return None
    real = rejected = seen = 0
    saw_any = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"tool_result"' not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("isSidechain"):
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict) or b.get("type") != "tool_result":
                continue
            saw_any = True
            seen += 1
            if b.get("is_error"):
                if _is_rejection(b.get("content")):
                    rejected += 1
                else:
                    real += 1
    if not saw_any:
        return None
    return real, rejected, seen


def _duration_min(events):
    """Minutes between first and last audit event (local-time ISO strings)."""
    if len(events) < 2:
        return 0
    try:
        a = datetime.datetime.fromisoformat(events[0]["ts"])
        b = datetime.datetime.fromisoformat(events[-1]["ts"])
        return round((b - a).total_seconds() / 60)
    except Exception:
        return None


def _ratio(n, d):
    return round(n / d, 1) if d else None


def compute(transcript_path, events, queued_count):
    """Build the metric dict for one session. Never raises."""
    try:
        prompts = sum(1 for e in events if e.get("event") == "UserPromptSubmit")
        tools = [e for e in events if e.get("event") == "PostToolUse"]
        tool_calls = len(tools)
        tool_fails = sum(1 for e in tools if e.get("ok") is False)
        interjections = int(queued_count or 0)
        # A session's total user turns = typed prompts + mid-turn interjections.
        total_prompts = prompts + interjections

        totals, by_model = _transcript_usage(transcript_path)

        # Real failures live in the transcript, not the audit trail (see
        # _transcript_failures). These are additive fields -- the audit-based
        # tool_fails/fail_rate below are kept but are structurally blind to failures.
        fails = _transcript_failures(transcript_path)
        real_fails = fails[0] if fails else None
        rejected = fails[1] if fails else None
        results_seen = fails[2] if fails else None

        m = {
            "prompts": prompts,
            "interjections": interjections,
            "tool_calls": tool_calls,
            "tool_fails": tool_fails,  # audit-trail based -- structurally ~always 0
            "fail_rate": _ratio(tool_fails * 100, tool_calls),  # blind; see fail_rate_real
            # Real failures from the transcript (the honest numbers):
            "tool_fails_real": real_fails,
            "tool_rejected": rejected,
            "results_seen": results_seen,
            "fail_rate_real": _ratio(real_fails * 100, results_seen) if fails else None,
            "duration_min": _duration_min(events),
            "out_tokens": totals["out_tokens"] if totals else None,
            "cache_read": totals["cache_read"] if totals else None,
            "cache_create": totals["cache_create"] if totals else None,
            "input_tokens": totals["input_tokens"] if totals else None,
            "turns": totals["turns"] if totals else None,
            "tokens_by_model": by_model,  # None if transcript unreadable
            "subagent_tokens": None,  # not included -- lives in separate task transcripts
            "out_per_prompt": _ratio(totals["out_tokens"], total_prompts) if totals else None,
            "tools_per_prompt": _ratio(tool_calls, total_prompts),
            "interj_per_prompt": _ratio(interjections, total_prompts),
        }
        return m
    except Exception:
        return {"error": "metrics compute failed"}


def _k(n):
    if n is None:
        return "—"
    if n >= 1000:
        return f"{n/1000:,.0f}k"
    return str(n)


def render_md(m):
    """Markdown section appended to the session digest."""
    if not m or m.get("error"):
        return "## 效率 / Token\n\n_metric 計算失敗，本 session 無資料。_\n"
    by_model = m.get("tokens_by_model") or {}
    # Skip zero-token models (e.g. "<synthetic>") -- they are noise in the table.
    model_line = ", ".join(f"{mod}: {_k(v)}" for mod, v in
                           sorted(by_model.items(), key=lambda kv: -kv[1]) if v) or "—"
    frr = m.get("fail_rate_real")
    fail_line = (
        f"| **真實失敗（transcript）** | {m.get('tool_fails_real')} / "
        f"{m.get('results_seen')} 工具結果（{frr}%）；使用者拒絕 {m.get('tool_rejected')} |"
        if m.get("tool_fails_real") is not None
        else "| 真實失敗（transcript） | _transcript 無法讀，本場無資料_ |"
    )
    lines = [
        "## 效率 / Token",
        "",
        "> `interjections` 是試誤的**代理指標，≠ 已確認糾正**（P3 opus 稽核再精算）。"
        "subagent token 未納入（在各自 task transcript）。cache_read 為每輪重讀累加。"
        "**失敗率取自 transcript**：PostToolUse hook 在工具失敗時不觸發，audit trail 看不到失敗"
        "（2026-07-24 exit-7 探針驗證），故 audit 版 tool_fails 恆 0、不可信。",
        "",
        "| 指標 | 值 |",
        "|---|---|",
        f"| output tokens（真正生成） | {_k(m.get('out_tokens'))} |",
        f"| cache_read（重讀累加） | {_k(m.get('cache_read'))} |",
        f"| cache_create | {_k(m.get('cache_create'))} |",
        f"| tokens by model | {model_line} |",
        f"| prompts / 中途插話 | {m.get('prompts')} / {m.get('interjections')} |",
        f"| tool calls（audit，僅成功） | {m.get('tool_calls')} |",
        fail_line,
        f"| turns / 時長(min) | {_k(m.get('turns'))} / {m.get('duration_min')} |",
        f"| output/prompt · tools/prompt · 插話/prompt | "
        f"{_k(m.get('out_per_prompt'))} · {m.get('tools_per_prompt')} · {m.get('interj_per_prompt')} |",
    ]
    return "\n".join(lines) + "\n"


def append_record(path, session, m):
    """Append one flat JSON line per session to metrics.jsonl (the trend source)."""
    rec = {"session": session, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    rec.update(m or {})
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
