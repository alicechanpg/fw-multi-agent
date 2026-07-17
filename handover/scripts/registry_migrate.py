"""One-shot migration helper: inventory memory files and SUGGEST a triage class.

Read-only by contract. It never deletes and never writes to the registry --
classification is a judgement call, and a wrong call either drags non-facts into
the registry or drops a real fact on the floor. The suggestion is reviewed by the
user before anything is migrated or removed (spec section 6).
"""
import pathlib
import re

MEMORY_DIR = pathlib.Path("C:/Users/alice/.claude/projects/D--mybot/memory")

# Hardware identifiers are the strongest mechanical signal that a file states a fact.
HARDWARE_ID = re.compile(
    r"\b(?:0x[0-9a-fA-F]{4}|295[dD]|0d8c|PID[_ ]?[0-9a-fA-F]{4}|COM\s?\d{1,2}"
    r"|STM32[A-Z0-9]+|ESP32|H7R3|H750)\b"
)
# Phrasing that marks a behavioural rule rather than a fact about the world.
RULE_MARKER = re.compile(r"優先於|一律|必須|不可|不要|禁止|要先|適合放|記得")


def suggest_class(filename, body):
    """Suggest 'fact' / 'mixed' / 'not-fact' for one memory file. A suggestion only."""
    has_id = bool(HARDWARE_ID.search(body))
    has_rule = bool(RULE_MARKER.search(body))
    if has_id and has_rule:
        return "mixed"
    if has_id:
        return "fact"
    return "not-fact"


def triage(memory_dir=MEMORY_DIR):
    """Inventory every memory file with a suggested class. The index is excluded."""
    rows = []
    for path in sorted(pathlib.Path(memory_dir).glob("*.md")):
        if path.name == "MEMORY.md":
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        lines = body.splitlines()
        # Frontmatter is a delimited BLOCK, not a set of known keys: real memory
        # files nest keys under `metadata:` with indented children, so guessing
        # at key prefixes silently fails on any shape we didn't enumerate. Find
        # the closing "---" instead and only look for content after it.
        start = 0
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    start = i + 1
                    break
            else:
                start = len(lines)  # unterminated frontmatter: no body to show
        first = ""
        for line in lines[start:]:
            line = line.strip()
            if line and not line.startswith("#"):
                first = line
                break
        rows.append({"file": path.name, "suggest": suggest_class(path.name, body), "first_line": first[:80]})
    return rows


def render_triage(rows):
    """Markdown table for the user to confirm before any migration or deletion."""
    out = [
        "# Memory 分流清單（建議，待使用者確認）",
        "",
        "_工具只做機械建議；`mixed` 需人工拆分（事實進 registry，守則留 SOP）。_",
        "",
        "| 檔案 | 建議分類 | 首行 |",
        "|---|---|---|",
    ]
    for r in rows:
        out.append(f"| {r['file']} | {r['suggest']} | {r['first_line']} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    rows = triage()
    dest = pathlib.Path("D:/mybot/handover/registry/triage.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_triage(rows), encoding="utf-8")
    # ASCII only: this console is cp950 and mangles Chinese.
    print(f"triage rows={len(rows)} written: {dest}")
