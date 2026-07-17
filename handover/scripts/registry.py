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
import re

REGISTRY = pathlib.Path("D:/mybot/handover/registry/facts.jsonl")

REQUIRED = ("key", "scope", "fact", "source", "owner", "captured", "ttl", "volatile", "confidence")
CONFIDENCE = ("verified", "reported", "assumed")


def _is_date(value):
    # fromisoformat on Python 3.11+ accepts ISO basic (20260717) and week-date
    # (2026-W29-5) formats. The registry requires literal YYYY-MM-DD to ensure
    # string comparisons for ttl expiry work correctly: if ttl="20260101" and
    # today="2026-07-17", str(ttl) < today becomes "20260101" < "2026-07-17"
    # (False, since '0' is 48 and '-' is 45), so an expired fact would read as live.
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(value)):
        return False
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


def lookup(facts, key, today=None):
    """Deterministic key lookup -- no fuzzy matching, no guessing.

    status:
      hit      -- usable fact
      miss     -- no entry; the caller MUST escalate, never improvise
      expired  -- entry exists but is past its ttl, so it is not usable
      volatile -- must be probed at runtime; the stored value is not truth
    """
    today = today or datetime.date.today().isoformat()
    for f in facts:
        if f.get("key") != key:
            continue
        if f.get("volatile"):
            return {"status": "volatile", "probe": f.get("probe"), "fact": f}
        ttl = f.get("ttl")
        if ttl and str(ttl) < today:
            return {"status": "expired", "fact": f}
        return {"status": "hit", "fact": f}
    return {"status": "miss"}
