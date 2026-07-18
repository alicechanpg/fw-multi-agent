#!/usr/bin/env python3
"""Registry retrieval layer (P2 slice 1).

registry.py gives deterministic lookup BY EXACT KEY. Real questions ("what chip
is Reactor 50", "spark live audio pid") don't arrive as exact keys -- so this
adds keyword SEARCH over the fact store, while preserving the two invariants that
make the registry trustworthy:

  * volatile facts NEVER return a cached value -- they return their probe, because
    the stored number (COM port, live PID) is stale by design.
  * every result carries its confidence (verified / reported / assumed) so the
    caller knows how much to trust it -- and a miss is an explicit miss, so the
    caller escalates instead of improvising.

Usage:
    python registry_query.py reactor 50 chip
    python registry_query.py spark live audio
    python registry_query.py --key CHIP:MCU --scope "Reactor 50/100"
"""
import argparse
import sys
import pathlib

# Windows console is cp950; fact text (and markers) contain chars outside Big5.
# Force UTF-8 output so callers (agents/CLI) get clean text instead of a crash.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import registry


def _fmt(f, status="hit"):
    conf = f.get("confidence", "?")
    line = f"[{status}] {f['key']}  ({f.get('scope','')})  <{conf}>"
    if f.get("volatile"):
        line += f"\n    [!] VOLATILE - do not cache. PROBE: {f.get('probe','(none)')}"
    else:
        line += f"\n    {f['fact']}"
    line += f"\n    src: {f.get('source','?')}  captured: {f.get('captured','?')}"
    if f.get("ttl"):
        line += f"  ttl: {f['ttl']}"
    return line


def search(facts, terms):
    """Rank facts by how many query terms appear in key+scope+fact (case-insensitive).

    Returns [(score, fact)] for facts matching at least one term, best first.
    A single mechanical ranker -- no fuzzy/semantic guessing, so results are
    reproducible and a caller can see exactly why something matched.
    """
    terms = [t.lower() for t in terms if t.strip()]
    scored = []
    for f in facts:
        # key+scope identify WHAT the fact is about, so a term matching there is a
        # stronger relevance signal than the same term buried in the fact body.
        ident = f"{f.get('key','')} {f.get('scope','')}".lower()
        body = str(f.get('fact', '')).lower()
        score = sum(2 for t in terms if t in ident) + sum(1 for t in terms if t in body)
        if score:
            scored.append((score, f))
    scored.sort(key=lambda sf: (-sf[0], sf[1].get("key", "")))
    return scored


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="*", help="keywords to search")
    ap.add_argument("--key", help="exact key lookup")
    ap.add_argument("--scope", help="scope for exact lookup")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args(argv)

    facts = registry.load()
    if not facts:
        print("registry EMPTY (facts.jsonl missing/empty).")
        return 2

    if args.key:
        r = registry.lookup(facts, args.key, scope=args.scope)
        st = r["status"]
        if st in ("hit", "expired", "volatile"):
            print(_fmt(r["fact"], st))
        elif st == "ambiguous":
            print(f"[ambiguous] key '{args.key}' exists under scopes: {r['scopes']}"
                  f"\n  -> re-run with --scope to disambiguate (registry will NOT guess).")
        else:
            print(f"[miss] no fact for key '{args.key}'"
                  + (f" scope '{args.scope}'" if args.scope else "")
                  + "\n  -> escalate / verify per evidence rules; do NOT improvise.")
        return 0

    if not args.terms:
        ap.error("give keywords, or --key")
    hits = search(facts, args.terms)
    if not hits:
        print(f"[miss] nothing matches {args.terms!r} in {len(facts)} facts."
              "\n  -> escalate / verify; do NOT improvise a hardware fact.")
        return 0
    print(f"{len(hits)} match(es) for {args.terms!r} (top {min(args.limit,len(hits))}):\n")
    for score, f in hits[:args.limit]:
        print(_fmt(f) + f"\n    (matched {score} term/s)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
