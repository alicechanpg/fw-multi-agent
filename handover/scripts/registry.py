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


def lookup(facts, key, scope=None, today=None):
    """Deterministic lookup -- no fuzzy matching, no guessing.

    A fact's identity is (key, scope): H7R3 and H750 hold opposite facts under the
    same key, so a key alone does not identify one. Omitting scope is only safe
    when the key is unique; if it is not, the caller is told so rather than served
    an arbitrary one -- silently picking whichever line came first in the file is
    exactly how the wrong chip's fact gets passed off as verified.

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
    # volatile is checked BEFORE ttl on purpose: a volatile value must return its
    # probe even when stale, never a cached value. Do not reorder.
    if f.get("volatile"):
        return {"status": "volatile", "probe": f.get("probe"), "fact": f}
    ttl = f.get("ttl")
    if ttl and str(ttl) < today:
        return {"status": "expired", "fact": f}
    return {"status": "hit", "fact": f}


def find_conflict(facts, new_fact):
    """Return an existing record that contradicts new_fact, else None.

    Same key AND same scope but a different assertion is a conflict. Scope is part
    of identity on purpose: STM32H7R3 and H750 hold opposite facts under the same
    key and must not be treated as contradicting each other.

    The capture flow must stop and ask rather than overwrite -- a silent overwrite
    poisons every future lookup of that key.

    Identity fields are compared trimmed, matching how append() normalizes them on
    write. Comparing `fact` trimmed but `key` raw let 'CHIP:FLASH ' and 'CHIP:FLASH'
    read as different keys, so a real contradiction slipped past this gate. This is
    called on facts that have NOT been through append() yet -- that is its purpose --
    so it cannot rely on the write-side normalization alone.
    """
    new_key = str(new_fact.get("key")).strip()
    new_scope = str(new_fact.get("scope")).strip()
    for f in facts:
        same_key = str(f.get("key")).strip() == new_key
        same_scope = str(f.get("scope")).strip() == new_scope
        if same_key and same_scope:
            if str(f.get("fact")).strip() != str(new_fact.get("fact")).strip():
                return f
    return None


def append(fact, path=REGISTRY):
    """Validate, then append one fact. Raises ValueError if the record is invalid.

    Validation is not optional here: an unvalidated write is exactly how a fact
    without provenance, or a cached volatile value, gets into the registry.

    The identity fields (key, scope) are normalized before validation so that
    whitespace variants can never become two distinct identities in the file --
    which would hide a contradiction from find_conflict() and leave lookup() with
    two opposite facts to choose between. The caller's dict is copied, not mutated.
    """
    if isinstance(fact, dict):
        fact = dict(fact)
        for field in ("key", "scope"):
            if isinstance(fact.get(field), str):
                fact[field] = fact[field].strip()
    errs = validate(fact)
    if errs:
        raise ValueError("; ".join(errs))
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(fact, ensure_ascii=False) + "\n")
