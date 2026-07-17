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
