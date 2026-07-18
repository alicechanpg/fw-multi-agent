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


def test_validate_rejects_ttl_in_iso_basic_format():
    # ISO basic format (20260717) must not be accepted, even though it is valid
    # ISO. Only YYYY-MM-DD is allowed for deterministic string comparison.
    errs = registry.validate(valid_fact(ttl="20260717"))
    assert any("ttl" in e for e in errs)


def test_validate_rejects_ttl_in_iso_week_date_format():
    # ISO week-date (2026-W29-5) must not be accepted. Only YYYY-MM-DD.
    errs = registry.validate(valid_fact(ttl="2026-W29-5"))
    assert any("ttl" in e for e in errs)


def test_validate_rejects_captured_in_iso_basic_format():
    # ISO basic format must not be accepted for captured either.
    errs = registry.validate(valid_fact(captured="20260717"))
    assert any("captured" in e for e in errs)


def test_validate_rejects_impossible_date():
    # Even if the format is YYYY-MM-DD, it must be a real calendar date.
    errs = registry.validate(valid_fact(captured="2026-13-45"))
    assert any("captured" in e for e in errs)


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


def test_lookup_volatile_beats_expired_ttl():
    # A volatile fact must ALWAYS return its probe, never a cached value, even when
    # its ttl says it is stale. The invariant depends on the volatile check running
    # BEFORE the ttl check; a future refactor that reorders them must fail this test.
    facts = [
        valid_fact(
            key="COM:ESP32",
            volatile=True,
            probe="Get-PnpDevice, match VID 303A",
            ttl="2026-01-01",
        )
    ]
    got = registry.lookup(facts, "COM:ESP32", today="2026-07-17")
    assert got["status"] == "volatile"
    assert "303A" in got["probe"]


def test_lookup_ttl_equal_to_today_is_still_hit():
    # The ttl comparison is strict (<), not (<=), so a fact whose ttl is exactly
    # today is treated as live (good through the end of today), not expired.
    # This boundary must not change to <= without breaking real workflows.
    facts = [valid_fact(ttl="2026-07-17")]
    got = registry.lookup(facts, "PID:295D:0501", today="2026-07-17")
    assert got["status"] == "hit"


def test_find_conflict_flags_a_contradicting_entry():
    # The contract is `-> dict | None`: callers show the user the conflicting
    # record, so asserting merely `is not None` would pass for True/1/"yes" and
    # leave a caller crashing on a non-dict. Assert the actual record comes back.
    existing = [valid_fact()]
    incoming = valid_fact(fact="295D:0501 is the MCU")
    got = registry.find_conflict(existing, incoming)
    assert got["fact"] == existing[0]["fact"]
    assert got["key"] == existing[0]["key"]


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


def chip_facts():
    # The canonical isolation case: the SAME key holds OPPOSITE facts in each
    # scope, and find_conflict() deliberately lets both coexist in the file.
    return [
        valid_fact(key="CHIP:FLASH", scope="STM32H7R3", fact="has NO internal flash"),
        valid_fact(key="CHIP:FLASH", scope="STM32H750", fact="has internal flash"),
    ]


def test_lookup_without_scope_is_ambiguous_when_a_key_spans_scopes():
    # A key alone does not identify a fact once two scopes hold it. Returning the
    # first line in the file would pass off whichever record happened to be
    # written first as verified truth -- exactly the H7R3/H750 cross-context
    # misuse the scope field exists to prevent (spec §9.6). Say so instead.
    got = registry.lookup(chip_facts(), "CHIP:FLASH", today="2026-07-17")
    assert got["status"] == "ambiguous"
    assert sorted(got["scopes"]) == sorted(["STM32H7R3", "STM32H750"])
    assert "fact" not in got  # must not hand back a guessed record


def test_lookup_with_scope_serves_the_h750_fact():
    got = registry.lookup(chip_facts(), "CHIP:FLASH", scope="STM32H750", today="2026-07-17")
    assert got["status"] == "hit"
    assert got["fact"]["fact"] == "has internal flash"


def test_lookup_with_scope_serves_the_h7r3_fact():
    # Proves neither record is unreachable: the same key in the other scope must
    # return the OPPOSITE fact, not whichever one came first in the list.
    got = registry.lookup(chip_facts(), "CHIP:FLASH", scope="STM32H7R3", today="2026-07-17")
    assert got["status"] == "hit"
    assert got["fact"]["fact"] == "has NO internal flash"


def test_lookup_with_a_scope_that_matches_nothing_is_a_miss():
    got = registry.lookup(chip_facts(), "CHIP:FLASH", scope="STM32F4", today="2026-07-17")
    assert got["status"] == "miss"


def test_lookup_with_scope_still_returns_probe_for_a_volatile_fact():
    # Adding scope filtering must not disturb the volatile-before-ttl ordering.
    facts = [
        valid_fact(
            key="COM:ESP32",
            scope="ESP32",
            volatile=True,
            probe="Get-PnpDevice, match VID 303A",
            ttl="2026-01-01",
        )
    ]
    got = registry.lookup(facts, "COM:ESP32", scope="ESP32", today="2026-07-17")
    assert got["status"] == "volatile"
    assert "303A" in got["probe"]


def test_find_conflict_sees_through_untrimmed_whitespace_in_a_key():
    # `fact` was compared with .strip() but key/scope were compared raw, so a
    # hand-migrated record with a trailing space in its key read as a DIFFERENT
    # key. The contradiction slipped past the gate, both records were appended,
    # and lookup then had two opposite facts to choose between.
    existing = [valid_fact(key="CHIP:FLASH ", scope="STM32H750", fact="has internal flash")]
    incoming = valid_fact(key="CHIP:FLASH", scope="STM32H750", fact="has NO internal flash")
    got = registry.find_conflict(existing, incoming)
    assert got is not None
    assert got["fact"] == "has internal flash"


def test_append_stores_the_key_normalized(tmp_path):
    # Normalizing on write keeps whitespace variants from ever becoming two
    # distinct identities in the file.
    p = tmp_path / "facts.jsonl"
    registry.append(valid_fact(key="K ", scope=" Reactor "), path=p)
    stored = registry.load(p)[0]
    assert stored["key"] == "K"
    assert stored["scope"] == "Reactor"


def test_append_does_not_mutate_the_callers_dict(tmp_path):
    p = tmp_path / "facts.jsonl"
    caller = valid_fact(key="K ")
    registry.append(caller, path=p)
    assert caller["key"] == "K "  # the caller's object is theirs, not ours to edit
