# P1 Source-of-Truth Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立機械可查、可 git-diff 的原子事實庫（`facts.jsonl`），並把既有 memory 的硬體事實安全遷移進去。

**Architecture:** 一個純函式模組 `registry.py` 負責 schema 驗證 + 確定性 key 查找 + 衝突偵測；一個一次性工具 `registry_migrate.py` 產出「分流清單」與「覆蓋率對照表」供人審。**P1 不含任何 hook 強制力**（那是 P2），也不呼叫 model。查找永不臆測：miss 就回 miss，由呼叫端升級。

**Tech Stack:** Python 3.13.3、pytest 9.1.1、JSONL、Git Bash（Windows）

**Spec:** `docs/superpowers/specs/2026-07-17-p1-source-of-truth-registry-design.md`

## Global Constraints

- Registry 檔路徑：`D:/mybot/handover/registry/facts.jsonl`（一行一條 JSON）
- Schema 必填欄位：`key, scope, fact, source, owner, captured, ttl, volatile, confidence`
- `confidence` 只允許：`verified` / `reported` / `assumed`
- `volatile: true` 的事實**必須**帶 `probe`，且查找時**不得回傳快取值**
- `ttl` 為 `null`（長青）或 `YYYY-MM-DD`；已過期視同 miss
- **一筆事實的識別碼是 `(key, scope)` 而非 `key` 單獨**：任何「選定/比對某筆事實」的函式都必須同時使用兩者——H7R3 與 H750 刻意在同一個 `key` 下持有相反事實，只看 `key` 會讓不同 task 對「這是不是同一筆」給出矛盾答案
- **console 是 cp950**：任何腳本**不得**把中文印到 stdout；報表一律寫檔，用 Read 讀
- **`C:\Users\alice\.claude\projects\D--mybot\memory\` 不在 git 版控**——本計畫**不刪除任何 memory 檔**；刪除須待分流清單經使用者確認後另行執行
- Bash 中多行字串用 `printf`，**不得**使用 PowerShell heredoc `@'...'@`
- 不修改 `session-digest.py` / `metrics.py`（P0 已穩，不在本計畫範圍）

---

## File Structure

| 檔案 | 責任 |
|---|---|
| `handover/scripts/registry.py`（新） | schema 驗證、載入、確定性查找、衝突偵測、append。純函式，無 side effect（除 append） |
| `handover/tests/conftest.py`（新） | 讓測試能 import `handover/scripts/` 下的模組 |
| `handover/tests/test_registry.py`（新） | registry.py 的測試 |
| `handover/scripts/registry_migrate.py`（新） | 一次性工具：產出分流清單 + 覆蓋率對照表。**只讀不刪** |
| `handover/tests/test_registry_migrate.py`（新） | 遷移工具的測試 |
| `handover/registry/facts.jsonl`（新，資料） | 事實庫本體 |

---

### Task 1: Registry schema 驗證

**Files:**
- Create: `D:/mybot/handover/scripts/registry.py`
- Create: `D:/mybot/handover/tests/conftest.py`
- Test: `D:/mybot/handover/tests/test_registry.py`

**Interfaces:**
- Produces: `validate(fact: dict) -> list[str]`（回傳問題清單，空 list == 合法）；常數 `REQUIRED: tuple`、`CONFIDENCE: tuple`、`REGISTRY: pathlib.Path`

- [ ] **Step 1: 建立 conftest 讓測試找得到模組**

Create `D:/mybot/handover/tests/conftest.py`:

```python
"""Put handover/scripts on sys.path so tests can import registry.py directly.

The scripts are standalone hook entry points, not an installed package.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
```

- [ ] **Step 2: 寫失敗的測試**

Create `D:/mybot/handover/tests/test_registry.py`:

```python
import registry


def valid_fact(**over):
    base = {
        "key": "PID:295D:0501",
        "scope": "Reactor",
        "fact": "295D:0501 = Actions BT Audio chip, not the MCU",
        "source": "reference_reactor_usb_pid_chip_map.md",
        "owner": "alice",
        "captured": "2026-07-17",
        "ttl": None,
        "volatile": False,
        "confidence": "verified",
    }
    base.update(over)
    return base


def test_validate_accepts_a_well_formed_fact():
    assert registry.validate(valid_fact()) == []


def test_validate_rejects_missing_source():
    # provenance is mandatory: it is what makes a poisoned entry traceable
    errs = registry.validate(valid_fact(source=""))
    assert any("source" in e for e in errs)


def test_validate_rejects_volatile_fact_without_probe():
    # a volatile value must never be cached as truth; it must carry how to probe it
    errs = registry.validate(valid_fact(volatile=True))
    assert any("probe" in e for e in errs)


def test_validate_accepts_volatile_fact_with_probe():
    f = valid_fact(key="COM:ESP32", volatile=True, probe="Get-PnpDevice, match VID 303A")
    assert registry.validate(f) == []


def test_validate_rejects_unknown_confidence():
    errs = registry.validate(valid_fact(confidence="probably"))
    assert any("confidence" in e for e in errs)


def test_validate_rejects_bad_ttl_format():
    errs = registry.validate(valid_fact(ttl="next week"))
    assert any("ttl" in e for e in errs)


def test_validate_accepts_null_ttl():
    assert registry.validate(valid_fact(ttl=None)) == []


def test_validate_rejects_a_com_key_stored_as_a_constant():
    # COM numbers change on replug. Storing one as a fixed truth is exactly how the
    # COM7-vs-COM19 contradiction got into memory in the first place.
    errs = registry.validate(valid_fact(key="COM:ESP32", volatile=False))
    assert any("volatile" in e for e in errs)
```

- [ ] **Step 3: 跑測試確認失敗**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'registry'`

- [ ] **Step 4: 寫最小實作**

Create `D:/mybot/handover/scripts/registry.py`:

```python
"""Source-of-truth registry: schema validation + deterministic lookup.

P1 of the SOP-governance system. See
docs/superpowers/specs/2026-07-17-p1-source-of-truth-registry-design.md

Deterministic by design: lookup() never guesses. A miss is returned as a miss so
the caller must escalate instead of improvising -- a wrong fact is worse than no
fact, because it passes every downstream check that shares this same source.
"""
import datetime
import json
import pathlib

REGISTRY = pathlib.Path("D:/mybot/handover/registry/facts.jsonl")

REQUIRED = ("key", "scope", "fact", "source", "owner", "captured", "ttl", "volatile", "confidence")
CONFIDENCE = ("verified", "reported", "assumed")


def _is_date(value):
    try:
        datetime.date.fromisoformat(str(value))
        return True
    except Exception:
        return False


def validate(fact):
    """Return a list of problems with one fact record. Empty list means valid."""
    if not isinstance(fact, dict):
        return ["not a dict"]
    missing = [f"missing field: {f}" for f in REQUIRED if f not in fact]
    if missing:
        return missing

    errs = []
    for field in ("key", "fact", "source"):
        if not str(fact[field]).strip():
            errs.append(f"{field} is empty")
    if fact["confidence"] not in CONFIDENCE:
        errs.append(f"confidence must be one of {CONFIDENCE}")
    if not isinstance(fact["volatile"], bool):
        errs.append("volatile must be a bool")
    elif fact["volatile"] and not str(fact.get("probe", "")).strip():
        errs.append("a volatile fact must carry a probe instruction")
    elif not fact["volatile"] and str(fact["key"]).upper().startswith("COM:"):
        # Port numbers change on replug; a COM fact stored as a constant is how the
        # COM7-vs-COM19 contradiction arose. Force it to be probed instead.
        errs.append("a COM: key must be volatile, never a stored constant")
    if not _is_date(fact["captured"]):
        errs.append("captured must be YYYY-MM-DD")
    if fact["ttl"] is not None and not _is_date(fact["ttl"]):
        errs.append("ttl must be YYYY-MM-DD or null")
    return errs
```

- [ ] **Step 5: 跑測試確認通過**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v`
Expected: PASS — 8 passed

- [ ] **Step 6: Commit**

```bash
cd /d/mybot/fw-multi-agent
mkdir -p handover/scripts handover/tests
cp /d/mybot/handover/scripts/registry.py handover/scripts/
cp /d/mybot/handover/tests/conftest.py /d/mybot/handover/tests/test_registry.py handover/tests/
git add handover/scripts/registry.py handover/tests/conftest.py handover/tests/test_registry.py
git commit -m "$(printf 'feat(registry): fact schema validation\n\nProvenance and probe are mandatory: a volatile value must never be\ncached as truth, and an entry without a source cannot be traced when\nit turns out wrong.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 2: 確定性查找（miss / expired / volatile 語義）

**Files:**
- Modify: `D:/mybot/handover/scripts/registry.py`
- Test: `D:/mybot/handover/tests/test_registry.py`

**Interfaces:**
- Consumes: `validate`, `REGISTRY`（Task 1）
- Produces: `load(path=REGISTRY) -> list[dict]`；`lookup(facts: list[dict], key: str, scope: str | None = None, today: str | None = None) -> dict`，回傳 `{"status": "hit"|"miss"|"expired"|"volatile"|"ambiguous", ...}`

- [ ] **Step 1: 寫失敗的測試**

Append to `D:/mybot/handover/tests/test_registry.py`:

```python
def test_lookup_returns_hit_for_a_live_fact():
    facts = [valid_fact()]
    got = registry.lookup(facts, "PID:295D:0501", today="2026-07-17")
    assert got["status"] == "hit"
    assert got["fact"]["scope"] == "Reactor"


def test_lookup_reports_miss_instead_of_guessing():
    # a miss must be explicit so the caller escalates rather than improvising
    got = registry.lookup([valid_fact()], "PID:295D:9999", today="2026-07-17")
    assert got["status"] == "miss"


def test_lookup_treats_expired_ttl_as_unusable():
    facts = [valid_fact(ttl="2026-01-01")]
    got = registry.lookup(facts, "PID:295D:0501", today="2026-07-17")
    assert got["status"] == "expired"


def test_lookup_honours_ttl_that_has_not_passed():
    facts = [valid_fact(ttl="2026-12-31")]
    got = registry.lookup(facts, "PID:295D:0501", today="2026-07-17")
    assert got["status"] == "hit"


def test_lookup_of_volatile_fact_returns_probe_not_a_value():
    facts = [valid_fact(key="COM:ESP32", volatile=True, probe="Get-PnpDevice, match VID 303A")]
    got = registry.lookup(facts, "COM:ESP32", today="2026-07-17")
    assert got["status"] == "volatile"
    assert "303A" in got["probe"]


def test_load_of_missing_file_is_an_empty_registry(tmp_path):
    assert registry.load(tmp_path / "nope.jsonl") == []


def test_load_reads_one_fact_per_line(tmp_path):
    p = tmp_path / "facts.jsonl"
    p.write_text(
        '{"key":"A","fact":"a"}\n\n{"key":"B","fact":"b"}\n', encoding="utf-8"
    )
    assert [f["key"] for f in registry.load(p)] == ["A", "B"]
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v -k "lookup or load"`
Expected: FAIL — `AttributeError: module 'registry' has no attribute 'lookup'`

- [ ] **Step 3: 寫最小實作**

Append to `D:/mybot/handover/scripts/registry.py`:

```python
def load(path=REGISTRY):
    """Read every fact record. A missing file is an empty registry, not an error."""
    p = pathlib.Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def lookup(facts, key, scope=None, today=None):
    """Deterministic (key, scope) lookup -- no fuzzy matching, no guessing.

    A fact's identity is (key, scope), not key alone: H7R3 and H750 deliberately
    hold opposite facts under the same key, so a key match that spans several
    scopes must not be resolved by picking one -- that is exactly the bug this
    function exists to prevent.

    status:
      hit       -- usable fact
      miss      -- no entry; the caller MUST escalate, never improvise
      expired   -- past its ttl, not usable
      volatile  -- must be probed at runtime; the stored value is not truth
      ambiguous -- key matches several scopes; caller must supply scope
    """
    today = today or datetime.date.today().isoformat()
    matches = [
        f for f in facts
        if f.get("key") == key and (scope is None or f.get("scope") == scope)
    ]
    if not matches:
        return {"status": "miss"}
    if len(matches) > 1:
        return {"status": "ambiguous", "scopes": [f.get("scope") for f in matches]}
    f = matches[0]
    if f.get("volatile"):
        return {"status": "volatile", "probe": f.get("probe"), "fact": f}
    ttl = f.get("ttl")
    if ttl and str(ttl) < today:
        return {"status": "expired", "fact": f}
    return {"status": "hit", "fact": f}
```

- [ ] **Step 4: 跑測試確認通過**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
cd /d/mybot/fw-multi-agent
cp /d/mybot/handover/scripts/registry.py handover/scripts/
cp /d/mybot/handover/tests/test_registry.py handover/tests/
git add handover/scripts/registry.py handover/tests/test_registry.py
git commit -m "$(printf 'feat(registry): deterministic lookup with ttl and volatile semantics\n\nA miss is reported as a miss so callers escalate instead of improvising.\nExpired entries are unusable rather than silently stale, and volatile\nkeys return a probe instruction instead of a cached value.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 3: 衝突偵測 + 安全 append

**Files:**
- Modify: `D:/mybot/handover/scripts/registry.py`
- Test: `D:/mybot/handover/tests/test_registry.py`

**Interfaces:**
- Consumes: `validate`, `load`, `REGISTRY`（Task 1–2）
- Produces: `find_conflict(facts: list[dict], new_fact: dict) -> dict | None`；`append(fact: dict, path=REGISTRY) -> None`（invalid 時 raise `ValueError`）

- [ ] **Step 1: 寫失敗的測試**

Append to `D:/mybot/handover/tests/test_registry.py`:

```python
def test_find_conflict_flags_a_contradicting_entry():
    existing = [valid_fact()]
    incoming = valid_fact(fact="295D:0501 is the MCU")
    assert registry.find_conflict(existing, incoming) is not None


def test_find_conflict_ignores_the_same_assertion():
    assert registry.find_conflict([valid_fact()], valid_fact()) is None


def test_find_conflict_does_not_fire_across_different_scopes():
    # STM32H7R3 and H750 are deliberately isolated: the same key in a different
    # scope is a different fact, not a contradiction
    existing = [valid_fact(key="CHIP:FLASH", scope="STM32H7R3", fact="has no internal flash")]
    incoming = valid_fact(key="CHIP:FLASH", scope="STM32H750", fact="has internal flash")
    assert registry.find_conflict(existing, incoming) is None


def test_append_writes_one_line_and_is_readable(tmp_path):
    p = tmp_path / "facts.jsonl"
    registry.append(valid_fact(), path=p)
    assert [f["key"] for f in registry.load(p)] == ["PID:295D:0501"]


def test_append_refuses_an_invalid_fact(tmp_path):
    import pytest

    p = tmp_path / "facts.jsonl"
    with pytest.raises(ValueError):
        registry.append(valid_fact(confidence="probably"), path=p)
    assert registry.load(p) == []
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v -k "conflict or append"`
Expected: FAIL — `AttributeError: module 'registry' has no attribute 'find_conflict'`

- [ ] **Step 3: 寫最小實作**

Append to `D:/mybot/handover/scripts/registry.py`:

```python
def find_conflict(facts, new_fact):
    """Return an existing record that contradicts new_fact, else None.

    Same key AND same scope but a different assertion is a conflict. Scope is part
    of identity on purpose: STM32H7R3 and H750 hold opposite facts under the same
    key and must not be treated as contradicting each other.

    The capture flow must stop and ask rather than overwrite -- a silent overwrite
    poisons every future lookup of that key.
    """
    for f in facts:
        same_key = f.get("key") == new_fact.get("key")
        same_scope = f.get("scope") == new_fact.get("scope")
        if same_key and same_scope:
            if str(f.get("fact")).strip() != str(new_fact.get("fact")).strip():
                return f
    return None


def append(fact, path=REGISTRY):
    """Validate, then append one fact. Raises ValueError if the record is invalid.

    Validation is not optional here: an unvalidated write is exactly how a fact
    without provenance, or a cached volatile value, gets into the registry.
    """
    errs = validate(fact)
    if errs:
        raise ValueError("; ".join(errs))
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(fact, ensure_ascii=False) + "\n")
```

- [ ] **Step 4: 跑測試確認通過**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry.py -v`
Expected: PASS — 20 passed

- [ ] **Step 5: Commit**

```bash
cd /d/mybot/fw-multi-agent
cp /d/mybot/handover/scripts/registry.py handover/scripts/
cp /d/mybot/handover/tests/test_registry.py handover/tests/
git add handover/scripts/registry.py handover/tests/test_registry.py
git commit -m "$(printf 'feat(registry): conflict detection and validated append\n\nScope is part of identity so H7R3 and H750 can hold opposite facts under\nthe same key without falsely conflicting. append() validates first: an\nunvalidated write is how a fact without provenance gets in.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 4: 遷移分流清單（只讀，不刪）

**Files:**
- Create: `D:/mybot/handover/scripts/registry_migrate.py`
- Test: `D:/mybot/handover/tests/test_registry_migrate.py`

**Interfaces:**
- Produces: `suggest_class(filename: str, body: str) -> str`（回傳 `"fact"` / `"mixed"` / `"not-fact"`）；`triage(memory_dir: pathlib.Path) -> list[dict]`（每筆 `{"file","suggest","first_line"}`）；`render_triage(rows: list[dict]) -> str`

**為什麼只建議不自動決定：** 分類是判斷題，錯分會把非事實搬進 registry 或漏掉事實。工具只做機械盤點與建議，最終分流由使用者確認（見 spec §6）。

- [ ] **Step 1: 寫失敗的測試**

Create `D:/mybot/handover/tests/test_registry_migrate.py`:

```python
import registry_migrate


def test_reference_file_with_hardware_ids_is_suggested_as_fact():
    body = "Reactor PID 295D:0501 is the BT Audio chip, not the MCU."
    assert registry_migrate.suggest_class("reference_reactor_usb_pid_chip_map.md", body) == "fact"


def test_misfiled_feedback_holding_a_hardware_id_is_suggested_as_fact():
    body = "COM19 appearing means the ESP32 is powered on."
    assert registry_migrate.suggest_class("feedback_com19_means_esp32_on.md", body) == "fact"


def test_file_holding_both_a_fact_and_a_rule_is_suggested_as_mixed():
    body = "STM32H7R3 has no internal flash unlike H750. Anti-Hallucination 優先於 DRY."
    assert registry_migrate.suggest_class("feedback_stm32h7_chip_isolation.md", body) == "mixed"


def test_preference_note_is_suggested_as_not_fact():
    body = "Google Drive 老闆可見，適合放需主管可見的文件。"
    assert registry_migrate.suggest_class("reference_google_drive_visibility.md", body) == "not-fact"


def test_triage_lists_every_markdown_file(tmp_path):
    (tmp_path / "reference_a.md").write_text("PID 295D:0501 is the audio chip", encoding="utf-8")
    (tmp_path / "MEMORY.md").write_text("index", encoding="utf-8")
    rows = registry_migrate.triage(tmp_path)
    names = [r["file"] for r in rows]
    assert "reference_a.md" in names
    assert "MEMORY.md" not in names  # the index is not a fact source


def test_render_triage_is_a_markdown_table():
    out = registry_migrate.render_triage([{"file": "reference_a.md", "suggest": "fact", "first_line": "x"}])
    assert "| reference_a.md |" in out
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry_migrate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'registry_migrate'`

- [ ] **Step 3: 寫最小實作**

Create `D:/mybot/handover/scripts/registry_migrate.py`:

```python
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
        first = ""
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith(("---", "name:", "description:", "metadata:", "#")):
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
```

- [ ] **Step 4: 跑測試確認通過**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry_migrate.py -v`
Expected: PASS — 6 passed

- [ ] **Step 5: 對真實 memory 產出分流清單**

Run: `cd /d/mybot && python handover/scripts/registry_migrate.py`
Expected: `triage rows=67 written: D:\mybot\handover\registry\triage.md`（rows 約 66–67）
然後用 Read 讀 `D:/mybot/handover/registry/triage.md`（**不要看 stdout**，cp950 會亂碼），確認分類建議合理。

- [ ] **Step 6: Commit**

```bash
cd /d/mybot/fw-multi-agent
cp /d/mybot/handover/scripts/registry_migrate.py handover/scripts/
cp /d/mybot/handover/tests/test_registry_migrate.py handover/tests/
git add handover/scripts/registry_migrate.py handover/tests/test_registry_migrate.py
git commit -m "$(printf 'feat(registry): read-only migration triage tool\n\nSuggests fact/mixed/not-fact per memory file and renders a table for the\nuser to confirm. It never deletes and never writes facts: classification\nis a judgement call and memory/ is not under version control.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 5: 遷移覆蓋率對照表（證明沒漏事實）

**Files:**
- Modify: `D:/mybot/handover/scripts/registry_migrate.py`
- Test: `D:/mybot/handover/tests/test_registry_migrate.py`

**Interfaces:**
- Consumes: `triage`（Task 4）、`registry.load`（Task 2）
- Produces: `coverage(source_files: list[str], facts: list[dict]) -> list[dict]`（每筆 `{"file","covered","keys"}`）；`render_coverage(rows) -> str`

**為什麼需要這個：** memory 不在 git，刪除不可回復。刪除前必須有機械證據證明「來源檔的每條事實都已在 registry 有對應 key」（spec §6 步驟 3、§9 驗收標準 2）。

- [ ] **Step 1: 寫失敗的測試**

Append to `D:/mybot/handover/tests/test_registry_migrate.py`:

```python
def test_coverage_marks_a_source_with_a_migrated_fact_as_covered():
    facts = [{"key": "PID:295D:0501", "source": "reference_a.md｜實機驗證"}]
    rows = registry_migrate.coverage(["reference_a.md"], facts)
    assert rows[0]["covered"] is True
    assert rows[0]["keys"] == ["PID:295D:0501"]


def test_coverage_marks_an_unmigrated_source_as_not_covered():
    rows = registry_migrate.coverage(["reference_b.md"], [{"key": "X", "source": "reference_a.md"}])
    assert rows[0]["covered"] is False
    assert rows[0]["keys"] == []


def test_render_coverage_flags_uncovered_sources():
    out = registry_migrate.render_coverage([{"file": "reference_b.md", "covered": False, "keys": []}])
    assert "reference_b.md" in out
    assert "NOT COVERED" in out
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd /d/mybot && python -m pytest handover/tests/test_registry_migrate.py -v -k coverage`
Expected: FAIL — `AttributeError: module 'registry_migrate' has no attribute 'coverage'`

- [ ] **Step 3: 寫最小實作**

Append to `D:/mybot/handover/scripts/registry_migrate.py` (above the `if __name__` block):

```python
def coverage(source_files, facts):
    """Map each source file to the registry keys that cite it.

    memory/ is not in version control, so deletion is irreversible. This is the
    mechanical evidence that a source file's facts survived the migration; a file
    that is not covered must not be deleted.
    """
    rows = []
    for name in source_files:
        keys = [f.get("key") for f in facts if name in str(f.get("source", ""))]
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
        out.append(f"| {r['file']} | {status} | {', '.join(k for k in r['keys'] if k) or '—'} |")
    return "\n".join(out) + "\n"
```

- [ ] **Step 4: 跑測試確認通過**

Run: `cd /d/mybot && python -m pytest handover/tests/ -v`
Expected: PASS — 29 passed（Task 1–5 全部）

- [ ] **Step 5: Commit**

```bash
cd /d/mybot/fw-multi-agent
cp /d/mybot/handover/scripts/registry_migrate.py handover/scripts/
cp /d/mybot/handover/tests/test_registry_migrate.py handover/tests/
git add handover/scripts/registry_migrate.py handover/tests/test_registry_migrate.py
git commit -m "$(printf 'feat(registry): migration coverage report\n\nMechanical evidence that facts from a source file reached the registry.\nmemory/ is not in git, so an uncovered source must never be deleted.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## 完成後的人工關卡（不在本計畫自動執行）

1. Read `handover/registry/triage.md` → 使用者確認分流（`mixed` 需拆分）。
2. **備份** `memory/` 到 fw-multi-agent（memory 不在 git，這是唯一的回復點）。
3. 依確認後的分流逐檔遷移事實（COM 類一律 `volatile:true` + `probe`）。
4. 跑覆蓋率對照表 → 全部 `covered` 才可刪除原檔。
5. 更新 `MEMORY.md` 指向 registry。

> 步驟 2–5 涉及不可回復的刪除，須經使用者逐項確認，**不由本計畫的 task 自動完成**。

---

## 執行紀錄：經核准的偏離

本計畫已執行完畢（Task 1–5，最終 **56 個測試通過**——計畫中逐 task 標注的 8 / 15 / 20 / 6 / 29 已被此數字取代）。執行過程中，計畫自身的參考程式碼發現 **4 處缺陷**：每一處都通過了計畫自己寫的測試，卻在真實資料上失敗。以下 4 處修正皆已在執行當下經使用者核准：

1. **Task 1 `_is_date`** —— 計畫用裸的 `datetime.date.fromisoformat`，在 Python 3.11+ 上會接受 ISO basic 格式（`20260717`）與 week-date 格式（`2026-W29-5`）。由於 `lookup()` 把 ttl 當字串比較，`ttl="20260101"` 會同時「驗證通過」且「比較結果為永不過期」。已改為先用 `re.fullmatch` 強制 `YYYY-MM-DD` 字面格式，再檢查日期是否合法。
2. **Task 4 `triage()`** —— 計畫用一組前綴 tuple 跳過 frontmatter，但真實 memory 檔案的 frontmatter 有巢狀/縮排，導致全部 67 列都預覽到 frontmatter 的 key，沒有一列顯示到內容。已改為用 frontmatter 區塊定界。
3. **Task 5 `coverage()`** —— 計畫用未錨定的子字串比對（`name in str(source)`），導致 `a.md` 被算進其實來自 `extra.md` 的事實，會誤判為可以刪除一個事實其實從未遷移過去的來源檔。已加固為先做精確比對，再改為只計算 `.md` 形狀 token 的最前導連續段。
4. **Task 2 `lookup()`** —— 前述的識別碼模型缺陷。只有最終跨 task 整體 review 才發現，因為它藏在 Task 2 與 Task 3 的縫隙裡。

**流程教訓**：這 4 處都通過了計畫自己的 fixture，因為 fixture 與參考程式碼出自同一人之手，盲點也共享。全部 4 處都是靠拿真實資料實測（真的 memory 目錄、真的 frontmatter、真的檔名）才抓到的。
