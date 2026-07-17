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
