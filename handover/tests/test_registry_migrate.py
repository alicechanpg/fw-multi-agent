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
