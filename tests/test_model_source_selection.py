"""Displayed model choice must match the requested source, without changing defaults."""

from types import SimpleNamespace

import pytest
from PIL import Image
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtTest import QSignalSpy

from core.model_loader import ModelLoader, ValidationResult
from ui.inference_panel import InferencePanel
from ui.main_window import MainWindow
from ui.model_settings import default_model_key


@pytest.mark.parametrize("task", ["classification", "segmentation"])
def test_switching_sources_hides_inactive_name_and_requests_correct_model(qtbot, tmp_path, task):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.resize(300, 650)
    panel.show()
    image = tmp_path / "image.png"
    Image.new("RGB", (24, 16), "white").save(image)
    panel.set_image(str(image))
    panel.set_task(task)
    custom = str(tmp_path / "local-model.pth")
    chosen = QSignalSpy(panel.custom_model_chosen)
    panel.set_custom_model(custom)
    requested = QSignalSpy(panel.run_requested)
    builtin = panel._builtin_model_names[task]

    for use_builtin in (False, True, False, True, True, False):
        panel.set_use_builtin(use_builtin)
        assert panel._custom_model_path == custom
        assert panel.model_filename_label.isHidden() == use_builtin
        assert panel.trust_warning_label.isHidden() == use_builtin
        assert panel.browse_model_button.isEnabled() != use_builtin
        assert panel.run_button.isEnabled()
        if use_builtin:
            assert panel.model_filename_label.text() == ""
            assert panel.model_filename_label.toolTip() == ""
            assert builtin in panel.mode_summary.text()
            assert "local-model.pth" not in panel.mode_summary.text()
        else:
            assert panel.model_filename_label.toolTip() == "local-model.pth"
            assert "local-model.pth" in panel.mode_summary.text()
            assert panel.model_filename_label.text()
        panel.run_button.click()
        assert requested[-1] == ["" if use_builtin else custom, use_builtin, str(image), task]
    # Toggling restores the chosen path; it does not browse or choose a new file.
    assert list(chosen) == [[custom]]


def test_replacing_custom_choice_and_returning_from_builtin_shows_only_latest_name(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_custom_model(str(tmp_path / "first.pth"))
    panel.set_use_builtin(True)
    panel.set_custom_model(str(tmp_path / "second.pth"))
    assert not panel.built_in_checkbox.isChecked()
    assert not panel.model_filename_label.isHidden()
    assert panel.model_filename_label.toolTip() == "second.pth"
    assert "first.pth" not in panel.mode_summary.text()
    panel.set_use_builtin(True)
    panel.set_use_builtin(False)
    assert panel.model_filename_label.toolTip() == "second.pth"


def test_empty_custom_choice_clears_stale_text_and_cannot_run_unchecked(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    image = tmp_path / "image.png"
    Image.new("RGB", (16, 16), "white").save(image)
    panel.set_image(str(image))
    panel.set_custom_model(str(tmp_path / "previous.pth"))
    panel.set_custom_model("")
    assert panel.built_in_checkbox.isChecked()
    assert panel._custom_model_path == ""
    assert panel.model_filename_label.isHidden()
    assert panel.model_filename_label.text() == ""
    panel.set_use_builtin(False)
    assert panel.model_filename_label.isHidden()
    assert not panel.run_button.isEnabled()
    assert "Model: Not selected" in panel.mode_summary.text()


def test_unchecked_without_any_local_choice_updates_summary_and_run_state(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    image = tmp_path / "image.png"
    Image.new("RGB", (16, 16), "white").save(image)
    panel.set_image(str(image))
    assert panel.run_button.isEnabled()
    panel.built_in_checkbox.setChecked(False)
    assert "Model: Not selected" in panel.mode_summary.text()
    assert not panel.run_button.isEnabled()
    assert panel.model_filename_label.isHidden()


@pytest.mark.parametrize("has_saved_default", [False, True])
def test_window_source_switch_keeps_completed_session_and_saved_defaults(qtbot, tmp_path, monkeypatch, has_saved_default):
    # Only model validation is simulated; no weight or placeholder model is written.
    monkeypatch.setattr(ModelLoader, "load_with_info", lambda self, path: SimpleNamespace(model=object()))
    monkeypatch.setattr(ModelLoader, "validate", staticmethod(
        lambda model: ValidationResult("classification", 3, (1, 3))))
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.db",
                        builtin_model_path=tmp_path / "not-installed.pth", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None)
    if has_saved_default:
        settings.setValue(default_model_key("classification"), "unchanged-startup-default.pth")
    initial_settings = {key: settings.value(key) for key in settings.allKeys()}
    custom = str(tmp_path / "chosen-local.pth")
    window.inference_panel.set_custom_model(custom)
    assert window._custom_model_status[1]
    window._builtin_model_statuses["classification"] = ("Built-in test-ready", True)
    image = tmp_path / "original.png"
    result = tmp_path / "result.png"
    Image.new("RGB", (24, 16), "white").save(image)
    Image.new("RGB", (24, 16), "green").save(result)
    record_id = window.database_manager.insert_record(str(image), custom, "classification", "Tissue", .8, str(result))
    window.history_panel.record_activated.emit(record_id)
    record_before = window.database_manager.get_record_by_id(record_id)
    current = window._current_result

    window.inference_panel.set_use_builtin(True)
    assert window.inference_panel.model_filename_label.isHidden()
    assert window.inference_panel.run_button.isEnabled()
    assert window.action_panel.metadata_labels["model"].text() == "chosen-local.pth"
    assert window._current_result is current
    window.inference_panel.set_use_builtin(False)
    assert not window.inference_panel.model_filename_label.isHidden()
    assert window.inference_panel.run_button.isEnabled()
    assert window._custom_model_path_validated == (tmp_path / "chosen-local.pth").resolve()
    assert {key: settings.value(key) for key in settings.allKeys()} == initial_settings
    assert window.database_manager.get_record_by_id(record_id) == record_before


def test_restored_local_choice_still_requires_matching_task(qtbot, tmp_path):
    window = MainWindow(settings=QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat),
                        db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None)
    panel = window.inference_panel
    panel._custom_model_path = str(tmp_path / "classifier.pth")
    window._custom_model_status = ("Custom classification model ready", True)
    window._custom_model_task = "classification"
    panel.set_task("segmentation")
    panel.set_use_builtin(False)
    assert not panel.model_filename_label.isHidden()
    assert panel.model_filename_label.toolTip() == "classifier.pth"
    assert not panel._model_ready
    assert not panel.run_button.isEnabled()


@pytest.mark.parametrize("outcome", ["ready", "error"])
def test_returning_to_local_after_inactive_validation_finishes_revalidates(qtbot, tmp_path, monkeypatch, outcome):
    window = MainWindow(settings=QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat),
                        db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None)
    window._builtin_model_statuses["classification"] = ("Built-in ready", True)
    path = tmp_path / "slow-local.pth"
    # Pause the validation path without creating a weight file or real worker.
    monkeypatch.setattr(window, "_start_large_model_validation", lambda *args: True)
    window.inference_panel.set_custom_model(str(path))
    assert window._custom_model_status == ("Loading model...", False)
    window.inference_panel.set_use_builtin(True)
    validation = ValidationResult("classification", 3, (1, 3))
    if outcome == "ready":
        window._apply_model_validation(path, False, SimpleNamespace(model=object()), validation)
    else:
        window._model_validation_failed(path, False, "Simulated validation error")
    window._model_validation_finished()
    assert window.inference_panel.model_filename_label.isHidden()
    assert "Built-in ready" in window.inference_panel.model_status_label.text()

    loads = []
    monkeypatch.setattr(window, "_start_large_model_validation", lambda *args: False)
    monkeypatch.setattr(ModelLoader, "load_with_info", lambda self, p: loads.append(p) or SimpleNamespace(model=object()))
    monkeypatch.setattr(ModelLoader, "validate", staticmethod(lambda model: validation))
    window.inference_panel.set_use_builtin(False)
    qtbot.waitUntil(lambda: bool(loads))
    assert loads == [str(path)]
    assert window._custom_model_status[1]
    assert window._custom_model_path_validated == path.resolve()
    assert not window.inference_panel.model_filename_label.isHidden()
    assert "Loading" not in window.inference_panel.model_status_label.text()


def test_browsing_the_same_model_does_not_duplicate_deferred_validation(qtbot, tmp_path, monkeypatch):
    window = MainWindow(settings=QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat),
                        db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None)
    panel = window.inference_panel
    path = str(tmp_path / "chosen-again.pth")
    panel._custom_model_path = path
    window._custom_model_status = ("Loading model...", False)
    loads = []
    monkeypatch.setattr(window, "_start_large_model_validation", lambda *args: False)
    monkeypatch.setattr(ModelLoader, "load_with_info", lambda self, p: loads.append(p) or SimpleNamespace(model=object()))
    monkeypatch.setattr(ModelLoader, "validate", staticmethod(
        lambda model: ValidationResult("classification", 3, (1, 3))))
    panel.set_custom_model(path)
    qtbot.wait(20)
    assert loads == [path]
    assert window._custom_model_status[1]
