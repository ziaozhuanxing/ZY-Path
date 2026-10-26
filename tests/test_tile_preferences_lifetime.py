"""Current tile preferences must not be replaced by saved record parameters."""

from copy import deepcopy
import json
import threading

from PIL import Image
import pytest
from PyQt5.QtCore import QSettings, Qt
import torch
from torch import nn

from core.classification_tiles import CLASSIFICATION_LABELS, exploratory_metadata
from core.model_loader import LoadedModel
from core.inference_engine import InferenceEngine
from ui.main_window import MainWindow


class InMemoryClassifier(nn.Module):
    def forward(self, value):
        return value.mean((2, 3)).repeat(1, 3)


@pytest.fixture
def ready_window(qtbot, tmp_path):
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    settings.setValue("classification/defaultMode", "tiled_analysis")
    settings.setValue("classificationTiles/width", 8)
    settings.setValue("classificationTiles/height", 7)
    path = tmp_path / "not-written.pth"
    window = MainWindow(settings=settings, builtin_model_path=path,
                        db_path=tmp_path / "history.db", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window._builtin_model_statuses["classification"] is not None)
    loaded = LoadedModel(InMemoryClassifier(), "checkpoint", list(CLASSIFICATION_LABELS),
                         "test", "raw255", exploratory_metadata(99, 99))
    window._validated_builtin_model = (path, loaded)
    window._builtin_model_statuses["classification"] = ("In-memory test classifier", True)
    window._builtin_model_tasks["classification"] = "classification"
    window._builtin_model_task = "classification"
    window.inference_panel.set_model_ready(True)
    source = tmp_path / "source.png"
    Image.new("RGB", (31, 23), (80, 140, 190)).save(source)
    window.inference_panel.set_image(str(source))
    yield window, source
    torch.set_num_threads(previous_threads)


def run_new(qtbot, window):
    assert window.inference_panel.run_button.isEnabled()
    qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    return window.database_manager.get_all_records()[0]


def saved_analysis(record):
    return json.loads(record["analysis_json"])


def choose_current_preferences(window, width=16, height=12):
    window._show_settings()
    dialog = window._settings_dialog
    dialog.tile_width.setValue(width)
    dialog.tile_height.setValue(height)
    dialog.resize_method.setCurrentIndex(dialog.resize_method.findData("opencv_linear"))
    dialog.hide()
    return dialog


@pytest.mark.parametrize("action", ["history", "same_values", "switch_mode", "new_image", "clear_view"])
def test_new_run_after_history_uses_preferences_and_records_actual_crops(qtbot, ready_window, action):
    window, source = ready_window
    old = run_new(qtbot, window)
    old_analysis = deepcopy(saved_analysis(old))
    assert old_analysis["tile_size"] == [8, 7]
    dialog = choose_current_preferences(window)
    window._show_record_activated(old["id"])
    if action == "same_values":
        window._show_settings()
        # Re-entering an unchanged value does not emit valueChanged.
        dialog.tile_width.setValue(16)
        dialog.tile_height.setValue(12)
        dialog.hide()
    elif action == "switch_mode":
        window.inference_panel.set_classification_mode("single_image")
        window.inference_panel.set_classification_mode("tiled_analysis")
    elif action == "new_image":
        other = source.with_name("another.png")
        Image.new("RGB", (31, 23), (90, 150, 180)).save(other)
        window.inference_panel.set_image(str(other))
    elif action == "clear_view":
        window._clear_current_view()
        window.inference_panel.set_image(str(source))
    current = run_new(qtbot, window)
    actual = saved_analysis(current)
    assert actual["tile_size"] == [16, 12]
    assert actual["resize_backend"] == "opencv_linear"
    assert [tile["box"] for tile in actual["tiles"]] == [
        [0, 0, 16, 12], [16, 0, 31, 12], [0, 12, 16, 23], [16, 12, 31, 23]]
    assert sum(actual["tile_counts"]) == 4
    assert sum(actual["pixel_counts"]) == 31 * 23
    assert window._current_result["metadata"]["classification_analysis"]["tile_size"] == [16, 12]
    assert saved_analysis(window.database_manager.get_record_by_id(old["id"])) == old_analysis
    assert "16 x 12" in window.inference_panel.mode_summary.text()
    assert "4 (2 columns x 2 rows)" in window.inference_panel.mode_summary.text()


def test_recorded_rerun_preserves_old_parameters_then_next_run_uses_current_preferences(qtbot, ready_window):
    window, _ = ready_window
    old = run_new(qtbot, window)
    choose_current_preferences(window)
    window.history_panel.select_record(old["id"])
    window._handle_rerun_requested()
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    repeated = window.database_manager.get_all_records()[0]
    assert repeated["id"] != old["id"]
    assert saved_analysis(repeated)["tile_size"] == [8, 7]
    assert saved_analysis(repeated)["resize_backend"] == "pillow_bilinear"
    assert saved_analysis(repeated)["tiles"] == saved_analysis(old)["tiles"]
    fresh = run_new(qtbot, window)
    assert saved_analysis(fresh)["tile_size"] == [16, 12]
    assert saved_analysis(fresh)["resize_backend"] == "opencv_linear"
    assert window.settings.value("classificationTiles/width", type=int) == 16
    assert window.settings.value("classificationTiles/height", type=int) == 12


def test_history_view_keeps_current_run_summary_separate_from_displayed_result(qtbot, ready_window):
    window, _ = ready_window
    old = run_new(qtbot, window)
    choose_current_preferences(window)
    window._show_record_activated(old["id"])
    assert window.inference_panel.classification_parameters()["tile_size"] == [16, 12]
    assert window.inference_panel.classification_parameters()["resize_backend"] == "opencv_linear"
    assert window.result_panel.tile_page.analysis["tile_size"] == [8, 7]
    assert window._current_result["metadata"]["classification_analysis"]["tile_size"] == [8, 7]


def test_reset_at_already_default_values_clears_history_parameter_cache(qtbot, ready_window):
    window, _ = ready_window
    old = run_new(qtbot, window)
    dialog = choose_current_preferences(window, 512, 512)
    window._show_record_activated(old["id"])
    # No numeric valueChanged is emitted here because both already show 512.
    dialog.reset_classification_button.click()
    window.inference_panel.set_classification_mode("tiled_analysis")
    assert window.inference_panel.classification_parameters()["tile_size"] == [512, 512]
    actual = saved_analysis(run_new(qtbot, window))
    assert actual["tile_size"] == [512, 512]
    assert actual["resize_backend"] == "pillow_bilinear"
    assert [tile["box"] for tile in actual["tiles"]] == [[0, 0, 31, 23]]


def test_reopened_settings_reflect_saved_dimensions_and_backend_without_partial_writes(qtbot, ready_window):
    window, _ = ready_window
    window._show_settings()
    dialog = window._settings_dialog
    dialog.hide()
    window.settings.setValue("classificationTiles/width", 16)
    window.settings.setValue("classificationTiles/height", 12)
    window.settings.setValue("classification/resizeBackend", "opencv_linear")
    before = {key: window.settings.value(key) for key in window.settings.allKeys()}
    window._show_settings()
    assert (dialog.tile_width.value(), dialog.tile_height.value()) == (16, 12)
    assert dialog.resize_method.currentData() == "opencv_linear"
    assert window.inference_panel.classification_parameters()["tile_size"] == [16, 12]
    assert {key: window.settings.value(key) for key in window.settings.allKeys()} == before
    dialog.hide()


def test_run_reads_saved_preferences_even_if_panel_cache_is_stale(qtbot, ready_window):
    window, _ = ready_window
    window.settings.setValue("classificationTiles/width", 16)
    window.settings.setValue("classificationTiles/height", 12)
    window.settings.setValue("classification/resizeBackend", "opencv_linear")
    window.inference_panel.set_classification_parameters({
        **exploratory_metadata(8, 7), "classification_mode": "tiled_analysis"})
    actual = saved_analysis(run_new(qtbot, window))
    assert actual["tile_size"] == [16, 12]
    assert actual["resize_backend"] == "opencv_linear"
    assert len(actual["tiles"]) == 4


def test_preferences_changed_during_inference_apply_only_to_next_run(qtbot, ready_window, monkeypatch):
    window, _ = ready_window
    window._show_settings()
    dialog = window._settings_dialog
    dialog.hide()
    entered, release = threading.Event(), threading.Event()
    original_pipeline = InferenceEngine.run_pipeline

    def paused_pipeline(engine):
        entered.set()
        assert release.wait(5)
        return original_pipeline(engine)

    monkeypatch.setattr(InferenceEngine, "run_pipeline", paused_pipeline)
    qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
    try:
        qtbot.waitUntil(entered.is_set, timeout=5000)
        engine = window._inference_engine
        assert engine.classification_tile_metadata["tile_size"] == [8, 7]
        dialog.tile_width.setValue(16)
        dialog.tile_height.setValue(12)
        dialog.resize_method.setCurrentIndex(dialog.resize_method.findData("opencv_linear"))
        assert engine.classification_tile_metadata["tile_size"] == [8, 7]
        assert engine.classification_resize_backend == "pillow_bilinear"
        assert "8 x 7" in window.inference_panel.mode_summary.text()
    finally:
        release.set()
        qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    completed = window.database_manager.get_all_records()[0]
    assert saved_analysis(completed)["tile_size"] == [8, 7]
    assert saved_analysis(completed)["resize_backend"] == "pillow_bilinear"
    assert "16 x 12" in window.inference_panel.mode_summary.text()
    fresh = run_new(qtbot, window)
    assert saved_analysis(fresh)["tile_size"] == [16, 12]
    assert saved_analysis(fresh)["resize_backend"] == "opencv_linear"
