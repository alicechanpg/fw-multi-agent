"""UserPromptSubmit hook: auto-surface source-of-truth facts (P2.2, engineering control).

When a prompt mentions a hardware identifier (PID/VID, chip part number, COM, DFU,
product name + a fact-seeking word), inject the matching registry facts as context
BEFORE the model answers -- so the right verified fact is in front of it at the
moment it's needed, instead of relying on the model remembering to run a query
(that reliance is the administrative-control weakness this replaces).

Contract (mirrors audit-log.py): read stdin JSON, NEVER raise, ALWAYS exit 0.
Output nothing unless there is a confident, relevant hit -- silence adds no context,
so a bad run degrades to "no help", never to a broken prompt. JIT: capped at 3 facts,
fires only on strong signals, so it does not dump the registry on every prompt.
"""
import json
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

MAX_FACTS = 3
MIN_SCORE = 2  # a surfaced fact must match >=2 query tokens (precision over recall)

# Strong, unambiguous hardware identifiers -- any of these alone is enough to fire.
HARD_ID = re.compile(
    r"\b(295[dd]|0d8c|0x0[0-9a-f]{3}|0[0-9a-f]{3}(?=\b)|stm32h7r3|stm32h750|stm32n6"
    r"|h7r3|h750|esp32(?:-s3)?|com\d{1,3}|dfu|stldr|bootloader|airoha|ab15\d5)\b",
    re.I,
)
# Product names -- only fire when paired with a fact-seeking word (else too noisy).
PRODUCT = re.compile(
    r"\b(reactor(?:\s*(?:50|100))?|spark(?:\s*(?:live|edge|mini\s*2?|pedal|2|gen\s*[12]))?)\b",
    re.I,
)
FACT_SEEK = re.compile(
    r"\b(chip|mcu|pid|vid|flash|dfu|audio|com|port|updater|bootloader|led|power|usb"
    r"|handshake|driver|jenkins|baud|serial|relay|nor|nand|ota)\b",
    re.I,
)


def _tokens(prompt):
    """Return the set of trigger tokens to search on, or empty set = do not fire."""
    hard = {m.group(0).lower() for m in HARD_ID.finditer(prompt)}
    prods = {m.group(0).lower().strip() for m in PRODUCT.finditer(prompt)}
    seeks = {m.group(0).lower() for m in FACT_SEEK.finditer(prompt)}
    if hard:
        return hard | prods | seeks
    if prods and seeks:  # product name alone is too broad; need a fact-seeking word
        return prods | seeks
    return set()


def main():
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    if (data.get("hook_event_name") or "") != "UserPromptSubmit":
        return
    prompt = data.get("prompt") or ""
    if not prompt.strip():
        return

    terms = _tokens(prompt)
    if not terms:
        return

    import registry, registry_query
    facts = registry.load()
    if not facts:
        return
    hits = [(s, f) for s, f in registry_query.search(facts, list(terms)) if s >= MIN_SCORE]
    if not hits:
        return

    lines = ["[registry] 查證過的硬體事實 (auto-surfaced，優先於記憶；conf 越低越不可信):"]
    for _, f in hits[:MAX_FACTS]:
        scope = f.get("scope", "")
        conf = f.get("confidence", "?")
        if f.get("volatile"):
            body = f"[VOLATILE-不可快取] PROBE: {f.get('probe', '')}"
        else:
            body = str(f.get("fact", ""))[:220]
        lines.append(f"- {f['key']} ({scope}) <{conf}>: {body}")
    lines.append("(查更多/精確查: python handover/scripts/registry_query.py <關鍵字> | --key K --scope S)")
    ctx = "\n".join(lines)

    out = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}}
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))


try:
    main()
except Exception:
    pass  # a context helper must never break prompt submission
sys.exit(0)
