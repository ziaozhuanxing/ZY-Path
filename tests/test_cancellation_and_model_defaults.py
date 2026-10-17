"""Exercise cancellation and task defaults with tiny temporary test models."""
import threading
from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, Qt
from PyQt5.QtTest import QSignalSpy
from torch import nn

from core.inference_engine import InferenceEngine
from core.model_loader import ModelLoader
from core.classification_tiles import ClassificationTileSpec, exploratory_metadata, predict_classification_tiles, CLASSIFICATION_LABELS
from core.large_image_segmentation import predict_large_image
from ui.main_window import MainWindow
from ui.model_settings import ModelSettingsPage, default_model_key


class Classifier(nn.Module):
    def forward(self, x):
        return x.mean((2, 3)).repeat(1, 3)


class Segmenter(nn.Module):
    def forward(self, x):
        return x.repeat(1, 3, 1, 1)


@pytest.fixture(autouse=True)
def one_torch_thread():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


@pytest.fixture
def assets(tmp_path):
    classification = tmp_path / "classifier.pt"
    segmentation = tmp_path / "segmenter.pt"
    torch.jit.trace(Classifier(), torch.ones(1, 3, 8, 8)).save(str(classification))
    torch.jit.trace(Segmenter(), torch.ones(1, 3, 8, 8)).save(str(segmentation))
    image = tmp_path / "image.png"
    Image.new("RGB", (20, 16), (70, 130, 190)).save(image)
    return {"classification": classification, "segmentation": segmentation, "image": image}


@pytest.fixture
def settings(tmp_path):
    return QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)


def window_for(qtbot, tmp_path, settings, assets):
    window = MainWindow(settings=settings, builtin_model_path=assets["classification"],
                        db_path=tmp_path / "db.sqlite", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None or window._custom_model_status is not None)
    return window


def test_cancel_before_loading_does_not_touch_model(monkeypatch):
    engine = InferenceEngine("absent.pt", "absent.png", "classification")
    monkeypatch.setattr(ModelLoader, "load_with_info", lambda *a: pytest.fail("Cancelled work must not load"))
    cancelled, results, errors = QSignalSpy(engine.cancelled), QSignalSpy(engine.result_ready), QSignalSpy(engine.error_occurred)
    engine.cancel()
    engine.run()
    assert len(cancelled) == 1 and not results and not errors


@pytest.mark.parametrize("task", ["classification", "segmentation"])
@pytest.mark.parametrize("phase", ["load", "validate", "predict", "publish"])
def test_cancel_at_pipeline_checkpoints(task, phase, assets, monkeypatch):
    engine = InferenceEngine(assets[task], assets["image"], task)
    if phase == "load":
        original = ModelLoader.load_with_info
        def load(loader, path):
            result = original(loader, path)
            engine.cancel()
            return result
        monkeypatch.setattr(ModelLoader, "load_with_info", load)
    elif phase == "validate":
        original = ModelLoader.validate
        def validate(model):
            result = original(model)
            engine.cancel()
            return result
        monkeypatch.setattr(ModelLoader, "validate", validate)
    elif phase == "predict":
        original = ModelLoader.forward
        count = 0
        def forward(model, x):
            nonlocal count
            result = original(model, x)
            count += 1
            if count == 2:  # validation first, actual inference second
                engine.cancel()
            return result
        monkeypatch.setattr(ModelLoader, "forward", forward)
    else:
        original = engine.run_pipeline
        def pipeline():
            result = original()
            engine.cancel()
            return result
        monkeypatch.setattr(engine, "run_pipeline", pipeline)
    cancelled, results, errors = QSignalSpy(engine.cancelled), QSignalSpy(engine.result_ready), QSignalSpy(engine.error_occurred)
    engine.run()
    assert len(cancelled) == 1 and not results and not errors


@pytest.mark.parametrize("task", ["classification", "segmentation"])
def test_cancel_at_final_tile_does_not_return_partial_result(task):
    cancelled = threading.Event()
    progress = []
    def callback(done, total):
        progress.append((done, total))
        if done == total:
            cancelled.set()
    image = Image.new("RGB", (8, 8))
    with pytest.raises(InterruptedError):
        if task == "classification":
            spec = ClassificationTileSpec.from_metadata(exploratory_metadata(4, 4), list(CLASSIFICATION_LABELS), "raw255")
            predict_classification_tiles(image, Classifier(), spec, callback, cancelled.is_set)
        else:
            predict_large_image(image, Segmenter(), torch.device("cpu"), tile=4, stride=4, input_size=4,
                                progress_callback=callback, cancel_callback=cancelled.is_set)
    assert progress[-1] == (4, 4)


class PausedEngine(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(int, int)
    status_changed = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.release = threading.Event()
        self.entered = threading.Event()
        self.cancel_calls = 0

    def cancel(self):
        self.cancel_calls += 1

    def run(self):
        self.entered.set()
        self.release.wait(5)
        # Deliberately emulate success already queued around cancellation.
        self.result_ready.emit({"late": True})
        self.progress_changed.emit(1, 1)
        self.status_changed.emit("Late worker status")


def test_gui_cancel_rejects_late_results_and_preserves_previous(qtbot, tmp_path, settings, assets, monkeypatch):
    window = window_for(qtbot, tmp_path, settings, assets)
    window.show()
    window.inference_panel.set_image(str(assets["image"]))
    window.inference_panel.run_button.click()
    qtbot.waitUntil(lambda: window._inference_engine is None)
    previous = window._current_result
    records = window.database_manager.get_all_records()
    files = set(window.results_dir.iterdir())
    monkeypatch.setattr("ui.main_window.InferenceEngine", PausedEngine)
    window.inference_panel.run_button.click()
    worker = window._inference_engine
    assert worker is not None
    qtbot.waitUntil(worker.entered.is_set)
    assert window.inference_panel.cancel_button.isVisible()
    assert not window.inference_panel.controls_scroll.isEnabled()
    window.inference_panel.cancel_button.click()
    window._cancel_inference()
    assert worker.cancel_calls == 1
    assert not window.inference_panel.cancel_button.isEnabled()
    assert window._inference_engine is worker
    assert not window.inference_panel.run_button.isEnabled()
    worker.release.set()
    qtbot.waitUntil(lambda: window._inference_engine is None)
    assert window._current_result is previous
    assert window.database_manager.get_all_records() == records
    assert set(window.results_dir.iterdir()) == files
    assert window.inference_panel.run_button.isEnabled()
    assert window.inference_panel.cancel_button.isHidden()
    assert "cancelled" in window.statusBar().currentMessage()


def test_close_waits_for_worker_without_blocking(qtbot, tmp_path, settings, assets, monkeypatch):
    window = window_for(qtbot, tmp_path, settings, assets)
    monkeypatch.setattr("ui.main_window.InferenceEngine", PausedEngine)
    window.show()
    window.inference_panel.set_image(str(assets["image"]))
    window.inference_panel.run_button.click()
    worker = window._inference_engine
    assert not window.close()
    assert window.isVisible() and worker.cancel_calls == 1
    worker.release.set()
    qtbot.waitUntil(lambda: not window.isVisible())
    assert window._inference_engine is None
    assert not window.database_manager.get_all_records()


@pytest.mark.parametrize("task", ["classification", "segmentation"])
def test_defaults_validate_save_and_restore_only_model_preferences(qtbot, settings, assets, task):
    settings.setValue("classificationTiles/width", 777)
    settings.setValue("appearance/theme", "Dark")
    page = ModelSettingsPage(settings, assets)
    qtbot.addWidget(page)
    page.rows[task]["path"].setText(str(assets[task]))
    changed = QSignalSpy(page.default_changed)
    page.validate_default(task)
    assert page.is_validating
    assert not page.rows[task]["save"].isEnabled()
    qtbot.waitUntil(lambda: not page.is_validating)
    assert settings.value(default_model_key(task)) == str(assets[task].resolve())
    assert list(changed[0]) == [task]
    other = "segmentation" if task == "classification" else "classification"
    settings.setValue(default_model_key(other), "keep-other.pt")
    page.restore_default(task)
    assert settings.value(default_model_key(task)) == ""
    assert settings.value(default_model_key(other)) == "keep-other.pt"
    assert settings.value("classificationTiles/width", type=int) == 777
    assert settings.value("appearance/theme") == "Dark"
    assert assets[task].is_file()


@pytest.mark.parametrize("case", ["missing", "invalid", "wrong_task"])
def test_invalid_default_never_replaces_saved_choice(qtbot, tmp_path, settings, assets, case):
    settings.setValue(default_model_key("classification"), str(assets["classification"]))
    page = ModelSettingsPage(settings, assets)
    qtbot.addWidget(page)
    candidate = tmp_path / "invalid.pt"
    if case == "invalid":
        candidate.write_bytes(b"invalid")
    elif case == "wrong_task":
        candidate = assets["segmentation"]
    page.rows["classification"]["path"].setText(str(candidate))
    page.validate_default("classification")
    qtbot.waitUntil(lambda: not page.is_validating)
    assert settings.value(default_model_key("classification")) == str(assets["classification"])
    assert "not changed" in page.rows["classification"]["status"].text() or "unchanged" in page.rows["classification"]["status"].text()


def test_startup_task_switch_and_restore_use_separate_defaults(qtbot, tmp_path, settings, assets):
    for task in ("classification", "segmentation"):
        settings.setValue(default_model_key(task), str(assets[task]))
    window = window_for(qtbot, tmp_path, settings, assets)
    assert not window.inference_panel.built_in_checkbox.isChecked()
    assert window._custom_model_path_validated == assets["classification"]
    window.inference_panel.set_task("segmentation")
    assert window._custom_model_task == "segmentation"
    assert window._custom_model_path_validated == assets["segmentation"]
    window.inference_panel.set_task("classification")
    assert window._custom_model_path_validated == assets["classification"]
    window._show_settings()
    window._settings_dialog.models_page.restore_default("classification")
    assert window.inference_panel.built_in_checkbox.isChecked()
    assert window._builtin_model_status[1]
    assert settings.value(default_model_key("segmentation")) == str(assets["segmentation"])


def test_missing_default_no_silent_fallback_and_wrong_task_keeps_task(qtbot, tmp_path, settings, assets):
    missing = str(tmp_path / "gone.pt")
    settings.setValue(default_model_key("classification"), missing)
    window = window_for(qtbot, tmp_path, settings, assets)
    assert not window.inference_panel.built_in_checkbox.isChecked()
    assert "unavailable" in window.inference_panel.model_status_label.text()
    assert not window.inference_panel._model_ready
    settings.setValue(default_model_key("classification"), str(assets["segmentation"]))
    window._default_changed("classification")
    assert window.inference_panel.classification_radio.isChecked()
    assert not window.inference_panel._model_ready
    assert "not classification" in window.inference_panel.model_status_label.text()


def test_history_rerun_keeps_recorded_model_despite_defaults(qtbot, tmp_path, settings, assets):
    window = window_for(qtbot, tmp_path, settings, assets)
    recorded = tmp_path / "recorded.pt"
    torch.jit.trace(Classifier(), torch.ones(1, 3, 8, 8)).save(str(recorded))
    record_id = window.database_manager.insert_record(str(assets["image"]), str(recorded), "classification")
    settings.setValue(default_model_key("classification"), str(assets["classification"]))
    window._load_all_history()
    window.history_panel.table.selectRow(0)
    assert window.history_panel.selected_record_id() == record_id
    window._handle_rerun_requested()
    assert window._inference_engine.model_path == recorded
    qtbot.waitUntil(lambda: window._inference_engine is None)
    new = [r for r in window.database_manager.get_all_records() if r["id"] != record_id]
    assert len(new) == 1 and new[0]["model_path"] == str(recorded.resolve())


def test_models_scroll_and_cancel_reachable_in_small_window(qtbot, tmp_path, settings, assets):
    window = window_for(qtbot, tmp_path, settings, assets)
    window.resize(640, 480)
    window.show()
    window.inference_panel.set_running(True)
    qtbot.wait(50)
    button = window.inference_panel.cancel_button
    assert button.isVisible() and button.isEnabled()
    assert window.rect().contains(button.mapTo(window, button.rect().center()))
    window.inference_panel.set_running(False)
    window._show_settings()
    dialog = window._settings_dialog
    dialog.resize(620, 400)
    dialog.navigation.setCurrentRow(2)
    qtbot.wait(50)
    scroll = dialog.pages.currentWidget()
    assert scroll.widgetResizable()
    assert scroll.verticalScrollBar().maximum() > 0
    scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    restore = dialog.models_page.rows["segmentation"]["restore"]
    assert scroll.viewport().rect().contains(restore.mapTo(scroll.viewport(), restore.rect().center()))


def test_switch_from_custom_default_to_unconfigured_task_uses_builtin(qtbot, tmp_path, settings, assets):
    settings.setValue(default_model_key("classification"), str(assets["classification"]))
    window = window_for(qtbot, tmp_path, settings, assets)
    window.builtin_model_paths["segmentation"] = assets["segmentation"]
    window.inference_panel.set_task("segmentation")
    qtbot.waitUntil(lambda: window._model_validation_thread is None)
    assert window.inference_panel.built_in_checkbox.isChecked()
    assert window._builtin_model_task == "segmentation"
    assert window._builtin_model_status[1]


def test_busy_models_page_cannot_change_saved_defaults(qtbot, settings, assets):
    page = ModelSettingsPage(settings, assets)
    qtbot.addWidget(page)
    settings.setValue(default_model_key("classification"), "existing.pt")
    page.rows["classification"]["path"].setText(str(assets["classification"]))
    page.set_busy(True)
    page.validate_default("classification")
    page.restore_default("classification")
    assert not page.is_validating
    assert settings.value(default_model_key("classification")) == "existing.pt"
    assert not page.rows["classification"]["browse"].isEnabled()
    page.set_busy(False)
    assert page.rows["classification"]["restore"].isEnabled()


def test_async_history_validation_resumes_recorded_model(qtbot, tmp_path, settings, assets, monkeypatch):
    import os
    window = window_for(qtbot, tmp_path, settings, assets)
    recorded = tmp_path / "large-recorded.pt"
    torch.jit.trace(Classifier(), torch.ones(1, 3, 8, 8)).save(str(recorded))
    original_stat = Path.stat
    def stat(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if path == recorded:
            values = list(result)
            values[6] = 200 * 1024 * 1024  # exercise the asynchronous size threshold
            return os.stat_result(values)
        return result
    monkeypatch.setattr(Path, "stat", stat)
    monkeypatch.setattr("ui.main_window.QMessageBox.warning", lambda *args: pytest.fail(str(args[2])))
    record_id = window.database_manager.insert_record(str(assets["image"]), str(recorded), "classification")
    window._load_all_history()
    window.history_panel.table.selectRow(0)
    settings.setValue(default_model_key("classification"), str(assets["classification"]))
    window._handle_rerun_requested()
    assert window._pending_rerun == record_id
    assert window._model_validation_thread is not None
    qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 2, timeout=10000)
    qtbot.waitUntil(lambda: window._inference_engine is None)
    result = [r for r in window.database_manager.get_all_records() if r["id"] != record_id][0]
    assert result["model_path"] == str(recorded.resolve())
    assert window._pending_rerun is None


def test_close_waits_for_settings_validation(qtbot, tmp_path, settings, assets, monkeypatch):
    class PausedValidation(QThread):
        validation_ready = pyqtSignal(object, object)
        validation_error = pyqtSignal(str)
        def __init__(self, path, parent=None):
            super().__init__(parent)
            self.release = threading.Event()
        def run(self):
            self.release.wait(5)
    window = window_for(qtbot, tmp_path, settings, assets)
    window.show()
    window._show_settings()
    monkeypatch.setattr("ui.model_settings.ModelValidationThread", PausedValidation)
    page = window._settings_dialog.models_page
    page.rows["classification"]["path"].setText(str(assets["classification"]))
    page.validate_default("classification")
    worker = page._worker
    assert not window.close() and window.isVisible()
    worker.release.set()
    qtbot.waitUntil(lambda: not window.isVisible())
    assert not page.is_validating


@pytest.mark.parametrize("task", ["classification", "segmentation"])
def test_builtin_history_rerun_after_custom_default_startup(qtbot, tmp_path, settings, assets, monkeypatch, task):
    custom = tmp_path / "custom-default.pt"
    torch.jit.trace(Classifier(), torch.ones(1, 3, 8, 8)).save(str(custom))
    settings.setValue(default_model_key("classification"), str(custom))
    window = window_for(qtbot, tmp_path, settings, assets)
    assert window._builtin_model_statuses["classification"] is None
    window.builtin_model_paths["segmentation"] = assets["segmentation"]
    record_id = window.database_manager.insert_record(str(assets["image"]), str(assets[task]), task)
    window._load_all_history()
    window.history_panel.table.selectRow(0)
    monkeypatch.setattr("ui.main_window.QMessageBox.warning", lambda *args: pytest.fail(str(args[2])))
    window._handle_rerun_requested()
    qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 2, timeout=10000)
    qtbot.waitUntil(lambda: window._inference_engine is None)
    new = [r for r in window.database_manager.get_all_records() if r["id"] != record_id][0]
    assert new["model_path"] == str(assets[task].resolve())
    assert new["task_type"] == task
    assert settings.value(default_model_key("classification")) == str(custom)
