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
