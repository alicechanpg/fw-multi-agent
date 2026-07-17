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


def test_triage_first_line_skips_nested_frontmatter_block(tmp_path):
    # Real memory files nest keys under `metadata:` (with a TRAILING SPACE) and
    # indent the children (`  node_type:`, `  type:`). After .strip() those
    # indented lines match none of the old exclusion prefixes, so the old
    # code picked "node_type: memory" as the preview and never reached the
    # real body line below the closing "---".
    body = (
        "---\n"
        "name: reference-reactor-usb-pid-chip-map\n"
        "description: Reactor 50 PID_0503 USB Audio 是 Actions BT Audio chip 產生的，不是 STM32 MCU\n"
        "metadata: \n"
        "  node_type: memory\n"
        "  type: reference\n"
        "  originSessionId: 7b26a649-6ac4-49d5-8d14-003107877db9\n"
        "---\n"
        "\n"
        "Reactor 50 的 USB 設備由不同晶片產生：\n"
    )
    (tmp_path / "reference_a.md").write_text(body, encoding="utf-8")
    rows = registry_migrate.triage(tmp_path)
    row = next(r for r in rows if r["file"] == "reference_a.md")
    assert row["first_line"] == "Reactor 50 的 USB 設備由不同晶片產生："


def test_triage_first_line_skips_flat_frontmatter_with_unlisted_keys(tmp_path):
    # Flat frontmatter whose keys (type:, originSessionId:) simply weren't in
    # the old hard-coded exclusion list -- same failure mode as nested, but
    # without any indentation involved.
    body = (
        "---\n"
        "type: reference\n"
        "originSessionId: abc123\n"
        "---\n"
        "\n"
        "真正的內容在這裡\n"
    )
    (tmp_path / "reference_b.md").write_text(body, encoding="utf-8")
    rows = registry_migrate.triage(tmp_path)
    row = next(r for r in rows if r["file"] == "reference_b.md")
    assert row["first_line"] == "真正的內容在這裡"


def test_triage_first_line_with_no_frontmatter_is_first_body_line(tmp_path):
    # Pins the existing behaviour the plan's own test relies on: files with
    # no frontmatter block at all must keep working exactly as before.
    body = "第一行內容\n第二行\n"
    (tmp_path / "reference_c.md").write_text(body, encoding="utf-8")
    rows = registry_migrate.triage(tmp_path)
    row = next(r for r in rows if r["file"] == "reference_c.md")
    assert row["first_line"] == "第一行內容"


def test_triage_first_line_skips_a_leading_markdown_heading(tmp_path):
    # A heading is structure, not content -- it must not be used as the
    # human-facing preview.
    body = "# Heading Title\n\n真正內容\n"
    (tmp_path / "reference_d.md").write_text(body, encoding="utf-8")
    rows = registry_migrate.triage(tmp_path)
    row = next(r for r in rows if r["file"] == "reference_d.md")
    assert row["first_line"] == "真正內容"


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


def test_coverage_does_not_false_positive_on_substring_match():
    # Proven false positive: "a.md" is a substring of "extra.md", so naive
    # `name in source` marks a.md covered by a fact that never mentioned it.
    # Over-reporting coverage here authorises deleting a.md's facts forever
    # (memory/ has no version control) -- must be NOT covered.
    rows = registry_migrate.coverage(["a.md"], [{"key": "X", "source": "extra.md"}])
    assert rows[0]["covered"] is False
    assert rows[0]["keys"] == []


def test_coverage_does_not_false_positive_when_name_is_a_filename_suffix():
    # "dfu_flash.md" is a suffix of "reference_dfu_flash.md" -- same substring
    # hazard as above, just via a realistic filename collision instead of a
    # contrived one. Must still require exact equality.
    rows = registry_migrate.coverage(["dfu_flash.md"], [{"key": "X", "source": "reference_dfu_flash.md"}])
    assert rows[0]["covered"] is False
    assert rows[0]["keys"] == []


def test_coverage_still_matches_exact_filename_with_annotation_suffix():
    # Pins the normal path: a source field carrying a "｜annotation" suffix
    # must still exactly match the filename before the separator.
    facts = [{"key": "PID:X", "source": "reference_a.md｜實機驗證"}]
    rows = registry_migrate.coverage(["reference_a.md"], facts)
    assert rows[0]["covered"] is True
    assert rows[0]["keys"] == ["PID:X"]
