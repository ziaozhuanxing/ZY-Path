"""Real Qt input and mode synchronization without production model weights."""
from copy import deepcopy

import pytest
from PyQt5.QtCore import QPoint, QPointF, QSettings, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication

from core.classification_tiles import CLASSIFICATION_LABELS, CLASSIFICATION_COLORS
from core.large_image_segmentation import SEGMENTATION_LABELS, SEGMENTATION_COLORS
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


def make_window(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.sqlite", builtin_model_path=tmp_path / "absent.pt")
    qtbot.addWidget(window)
    window.show()
    window._show_settings()
    dialog = window._settings_dialog
    dialog.navigation.setCurrentRow(1)
    return window, dialog


def choose(qtbot, combo, index):
    combo.showPopup()
    qtbot.waitUntil(lambda: combo.view().isVisible())
    view = combo.view()
    item = combo.model().index(index, 0)
    view.scrollTo(item)
    qtbot.mouseClick(view.viewport(), Qt.LeftButton, pos=view.visualRect(item).center())
    qtbot.waitUntil(lambda: not view.isVisible())


def wheel(widget, delta=-120):
    point = widget.rect().center()
    event = QWheelEvent(QPointF(point), QPointF(widget.mapToGlobal(point)), QPoint(), QPoint(0, delta),
                        Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(widget, event)
    return event


def test_real_preferences_popup_updates_main_mode_and_persists(qtbot, tmp_path):
    window, dialog = make_window(qtbot, tmp_path)
    previous = {"metadata": {"classification_mode": "single_image", "task_type": "classification"}}
    window._current_result = deepcopy(previous)
    scroll = dialog.pages.currentWidget()
    scroll.ensureWidgetVisible(dialog.startup_mode)
    choose(qtbot, dialog.startup_mode, 1)
    assert window.inference_panel.classification_mode() == "tiled_analysis"
    assert "Tiled analysis" in window.inference_panel.mode_summary.text()
    assert window.settings.value("classification/defaultMode") == "tiled_analysis"
    assert window.inference_panel.classification_parameters()["classification_mode"] == "tiled_analysis"
    assert window._current_result == previous
    dialog.hide()
    window._show_settings()
    assert dialog.startup_mode.currentData() == "tiled_analysis"
    choose(qtbot, dialog.startup_mode, 0)
    assert window.inference_panel.classification_mode() == "single_image"
    assert window.settings.value("classification/defaultMode") == "single_image"
    assert window._current_result == previous


def test_main_user_choice_syncs_preferences_while_history_mode_preserves_default(qtbot, tmp_path):
    window, dialog = make_window(qtbot, tmp_path)
    dialog.hide()
    combo = window.inference_panel.classification_mode_combo
    window.inference_panel.controls_scroll.ensureWidgetVisible(combo)
    choose(qtbot, combo, 1)
    assert dialog.startup_mode.currentData() == "tiled_analysis"
    assert window.settings.value("classification/defaultMode") == "tiled_analysis"
    # History restoration sets the mode programmatically, as production does.
    window.inference_panel.set_classification_mode("single_image")
    window._show_settings()
    assert dialog.startup_mode.currentData() == "single_image"
    assert window.settings.value("classification/defaultMode") == "tiled_analysis"
    assert "Saved startup default: Tiled analysis" in dialog.mode_default_note.text()
    # Explicitly selecting the already displayed mode still saves that choice.
    dialog.pages.currentWidget().ensureWidgetVisible(dialog.startup_mode)
    choose(qtbot, dialog.startup_mode, 0)
    assert window.settings.value("classification/defaultMode") == "single_image"
    assert "Saved startup default: Single image" in dialog.mode_default_note.text()


def test_reset_selects_single_image_even_if_combo_already_shows_it(qtbot, tmp_path):
    window, dialog = make_window(qtbot, tmp_path)
    window.inference_panel.set_classification_mode("tiled_analysis")
    # Exercise reset after a history-selected mode, without changing model/task.
    window.settings.setValue("classification/defaultMode", "tiled_analysis")
    dialog.reset_classification_button.click()
    assert window.inference_panel.classification_mode() == "single_image"
    assert dialog.startup_mode.currentData() == "single_image"
    assert window.settings.value("classification/defaultMode") == "single_image"
    assert dialog.resize_method.currentData() == "pillow_bilinear"
    assert dialog.tile_width.value() == dialog.tile_height.value() == 512


@pytest.mark.parametrize("focused", [False, True])
@pytest.mark.parametrize("control_name", ["resize_method", "startup_mode"])
def test_closed_dropdown_wheel_scrolls_page_without_changing_analysis(qtbot, tmp_path, focused, control_name):
    window, dialog = make_window(qtbot, tmp_path)
    dialog.resize(620, 400)
    combo = getattr(dialog, control_name)
    scroll = dialog.pages.currentWidget()
    scroll.ensureWidgetVisible(combo)
    qtbot.wait(30)
    if focused:
        combo.setFocus()
        qtbot.wait(10)
    else:
        combo.clearFocus()
    saved = combo.currentData()
    parameters = window.inference_panel.classification_parameters()
    before = scroll.verticalScrollBar().value()
    assert before < scroll.verticalScrollBar().maximum()
    wheel(combo)
    qtbot.wait(30)
    assert combo.currentData() == saved
    assert window.inference_panel.classification_parameters() == parameters
    assert scroll.verticalScrollBar().value() > before
    wheel(combo, 120)
    qtbot.wait(20)
    assert combo.currentData() == saved


def test_resize_popup_and_keyboard_still_select_real_backend(qtbot, tmp_path):
    window, dialog = make_window(qtbot, tmp_path)
    combo = dialog.resize_method
    dialog.pages.currentWidget().ensureWidgetVisible(combo)
    choose(qtbot, combo, 1)
    assert combo.currentData() == "opencv_linear"
    assert window.settings.value("classification/resizeBackend") == "opencv_linear"
    assert window.inference_panel.classification_parameters()["resize_backend"] == "opencv_linear"
    combo.setFocus()
    qtbot.keyClick(combo, Qt.Key_Up)
    assert combo.currentData() == "pillow_bilinear"
    assert window.settings.value("classification/resizeBackend") == "pillow_bilinear"
    assert window.inference_panel.classification_parameters()["resize_backend"] == "pillow_bilinear"


def test_mode_controls_lock_during_inference_and_restore_after_finish(qtbot, tmp_path):
    window, dialog = make_window(qtbot, tmp_path)
    marker = object()
    window._inference_engine = marker
    try:
        window._set_models_busy(True)
        assert not dialog.startup_mode.isEnabled()
        assert not dialog.reset_classification_button.isEnabled()
        assert "inference" in dialog.startup_mode.toolTip()
    finally:
        window._inference_engine = None
        window._set_models_busy(False)
    assert dialog.startup_mode.isEnabled()
    assert dialog.reset_classification_button.isEnabled()


@pytest.mark.parametrize("point_size", [10, 15, 20])
def test_both_palettes_are_independent_readable_references(qtbot, tmp_path, point_size):
    app = QApplication.instance()
    original_font = app.font()
    font = app.font()
    font.setPointSize(point_size)
    app.setFont(font)
    try:
        settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
        dialog = SettingsDialog(settings)
        qtbot.addWidget(dialog)
        dialog.navigation.setCurrentRow(1)
        dialog.resize(620, 400)
        dialog.show()
        qtbot.wait(30)
        assert len(dialog.palette_labels) == len(CLASSIFICATION_LABELS) == 9
        for text, label, color in zip(dialog.palette_labels, CLASSIFICATION_LABELS, CLASSIFICATION_COLORS):
            assert text.text() == f"{label} - RGB {color}"
        scroll = dialog.pages.currentWidget()
        assert len(dialog.segmentation_palette_labels) == len(SEGMENTATION_LABELS) == 9
        for index, (text, swatch, label, color) in enumerate(zip(dialog.segmentation_palette_labels,
                dialog.segmentation_palette_swatches, SEGMENTATION_LABELS, SEGMENTATION_COLORS)):
            assert text.text() == f"{index}: {label} - RGB {color}"
            assert f"rgb{color}" in swatch.styleSheet()
            scroll.ensureWidgetVisible(text)
            qtbot.wait(5)
            assert text.height() >= text.fontMetrics().height()
            assert scroll.viewport().rect().intersects(text.rect().translated(text.mapTo(scroll.viewport(), text.rect().topLeft())))
        assert scroll.horizontalScrollBar().maximum() == 0
        assert settings.value("classification/resizeBackend", "pillow_bilinear") == "pillow_bilinear"
    finally:
        app.setFont(original_font)


def test_preferences_selected_mode_drives_actual_inference_and_history(qtbot, tmp_path):
    import json
    import torch
    from PIL import Image
    from torch import nn
    from core.model_loader import LoadedModel

    class TinyClassifier(nn.Module):
        def forward(self, value):
            return value.mean((2, 3)).repeat(1, 3)

    window, dialog = make_window(qtbot, tmp_path)
    qtbot.waitUntil(lambda: window._builtin_model_status is not None)
    loaded = LoadedModel(TinyClassifier(), "checkpoint", list(CLASSIFICATION_LABELS), "test", "raw255")
    window._builtin_model_statuses["classification"] = ("Ready for in-memory test", True)
    window._validated_builtin_model = (window.builtin_model_paths["classification"], loaded)
    window.inference_panel.set_model_ready(True)
    image_path = tmp_path / "source.png"
    Image.new("RGB", (11, 9), (80, 140, 190)).save(image_path)
    window.inference_panel.set_image(str(image_path))
    dialog.tile_width.setValue(4)
    dialog.tile_height.setValue(3)
    for index, mode in ((1, "tiled_analysis"), (0, "single_image")):
        window._show_settings()
        dialog.pages.currentWidget().ensureWidgetVisible(dialog.startup_mode)
        choose(qtbot, dialog.startup_mode, index)
        dialog.hide()
        qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
        qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
        assert window._current_result["metadata"]["classification_mode"] == mode
    records = window.database_manager.get_all_records()
    assert len(records) == 2
    analyses = [json.loads(record["analysis_json"]) for record in records]
    tiled = next(analysis for analysis in analyses if analysis.get("mode") == "classification_tiles")
    assert tiled["tile_size"] == [4, 3]
    assert len(tiled["tiles"]) == sum(tiled["tile_counts"]) == 9
    assert sum(tiled["pixel_counts"]) == 11 * 9
    assert sum(analysis.get("classification_mode") == "single_image" for analysis in analyses) == 1
    assert window.settings.value("classification/defaultMode") == "single_image"
