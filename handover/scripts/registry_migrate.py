"""One-shot migration helper: inventory memory files and SUGGEST a triage class.

Read-only by contract. It never deletes and never writes to the registry --
classification is a judgement call, and a wrong call either drags non-facts into
the registry or drops a real fact on the floor. The suggestion is reviewed by the
user before anything is migrated or removed (spec section 6).
"""
import pathlib
import re

import registry

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


def _esc(text):
    """Escape pipes so a cell cannot break out of its markdown table column.

    A preview quoting a shell brace-expansion (`build-{r50|r100-v2}`) carries
    literal pipes that the renderer would otherwise emit as column separators,
    mangling the row in the document the user reads to authorise the migration.
    """
    return str(text).replace("|", "\\|")


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
        out.append(f"| {r['file']} | {r['suggest']} | {_esc(r['first_line'])} |")
    return "\n".join(out) + "\n"


def _cited_files(source):
    """Filenames a source field cites, for exact matching.

    Only the leading run of filename tokens counts. Everything from the first
    non-filename word onward is prose, and a filename merely mentioned in prose
    did not supply the fact -- crediting it would authorise deleting a file whose
    facts never migrated. Erring toward fewer citations only leaves a file in
    place; erring toward more loses it permanently.
    """
    head = re.split(r"[｜|]", str(source), maxsplit=1)[0]
    cited = set()
    # Full-width punctuation counts as a separator: the user writes Chinese and
    # `，` is her natural separator. Treating it as part of the token marked
    # genuinely-cited files NOT COVERED, and a wave of spurious NOT COVERED rows
    # trains the reader to override the deletion gate on sight. The leading-run
    # rule below still blocks the prose-mention hazard.
    for tok in re.split(r"[,，;；、\s]+", head):
        tok = tok.strip()
        if not tok:
            continue
        if not tok.endswith(".md"):
            break
        cited.add(tok)
    return cited


def coverage(source_files, facts):
    """Map each source file to the registry keys that cite it.

    memory/ is not in version control, so deletion is irreversible. This is the
    mechanical evidence that a source file's facts survived the migration; a file
    that is not covered must not be deleted.

    The `source` contract -- formats that CREDIT a file:
      "file.md"                  a bare citation
      "file.md|note"             annotation after an ASCII bar
      "file.md｜note"            annotation after a full-width bar
      "file.md, other.md"        several citations, comma or whitespace joined
      "file.md，note"            annotation after a full-width comma
    Formats that DO NOT credit it:
      "./file.md" or any path prefix   the token must equal the filename
      "File.MD"                        matching is case-sensitive
      "other.md see also file.md"      only the LEADING run of filename tokens
                                       counts; a file named in prose did not
                                       supply the fact
    A record whose key is missing or empty is never evidence, whatever its source.
    """
    rows = []
    for name in source_files:
        # Drop falsy keys: a source-matching record with no key is no evidence
        # that anything migrated. Reporting covered=True off one would print a
        # delete-safe status with an empty evidence column -- and the migration
        # is done BY HAND into a file that load() does not validate, so a keyless
        # record is expected input. Under-reporting leaves a file in place;
        # over-reporting loses it permanently.
        keys = [k for k in (f.get("key") for f in facts
                            if name in _cited_files(f.get("source", ""))) if k]
        rows.append({"file": name, "covered": bool(keys), "keys": keys})
    return rows


def render_coverage(rows):
    """Markdown table. Uncovered sources are called out, not quietly omitted."""
    out = [
        "# 遷移覆蓋率對照表",
        "",
        "_`NOT COVERED` 的來源檔**不得刪除**——代表事實尚未進 registry。_",
        "",
        "| 來源檔 | 狀態 | registry keys |",
        "|---|---|---|",
    ]
    for r in rows:
        status = "covered" if r["covered"] else "**NOT COVERED**"
        keys = ", ".join(_esc(k) for k in r["keys"] if k) or "—"
        out.append(f"| {_esc(r['file'])} | {status} | {keys} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    # Both reports are emitted from the one triage() result. coverage() gates an
    # irreversible deletion (memory/ has no version control), so it needs a real
    # entry point: without one, whoever performs the deletion writes ad-hoc glue
    # at the console, and that untested glue authorises permanent data loss.
    rows = triage()
    dest = pathlib.Path("D:/mybot/handover/registry/triage.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_triage(rows), encoding="utf-8")
    # ASCII only: this console is cp950 and mangles Chinese.
    print(f"triage rows={len(rows)} written: {dest}")

    facts = registry.load()
    cov = coverage([r["file"] for r in rows], facts)
    dest2 = pathlib.Path("D:/mybot/handover/registry/coverage.md")
    dest2.write_text(render_coverage(cov), encoding="utf-8")
    print(f"coverage rows={len(cov)} covered={sum(1 for r in cov if r['covered'])} written: {dest2}")
