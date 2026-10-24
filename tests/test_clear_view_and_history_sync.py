"""Transient view resets and history navigation, without model weights."""

from copy import deepcopy

from PIL import Image
import pytest
from PyQt5.QtCore import QPoint, QRect, QSettings, Qt
from PyQt5.QtTest import QSignalSpy

from core.classification_tiles import CLASSIFICATION_COLORS, CLASSIFICATION_LABELS
from ui.history_panel import HistoryPanel
from ui.main_window import MainWindow


def make_window(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("classification/defaultMode", "tiled_analysis")
    settings.setValue("classificationTiles/width", 256)
    settings.setValue("classificationTiles/height", 128)
    window = MainWindow(
        settings=settings, db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "not-installed.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    window.resize(1000, 720)
    window.show()
    qtbot.waitExposed(window)
    return window


def save_record(window, tmp_path, mode):
    """Store tiny synthetic display artifacts; no inference or model is claimed."""
    original = tmp_path / (mode + "-original.png")
    overlay = tmp_path / (mode + "-overlay.png")
    color = tmp_path / (mode + "-map.png")
    Image.new("RGB", (24, 16), (200, 40, 60)).save(original)
    Image.new("RGB", (24, 16), (120, 70, 80)).save(overlay)
    Image.new("RGB", (24, 16), CLASSIFICATION_COLORS[7]).save(color)
    if mode == "tiled_analysis":
        analysis = {
            "mode": "classification_tiles", "classification_mode": mode,
            "image_size": [24, 16], "tile_size": [24, 16],
            "input_size": [224, 224], "preprocess": "raw255",
            "resize_backend": "pillow_bilinear",
            "classes": [{"label": label, "color": list(rgb)}
                        for label, rgb in zip(CLASSIFICATION_LABELS, CLASSIFICATION_COLORS)],
            "tiles": [{"box": [0, 0, 24, 16], "class_index": 7, "label": "STR",
                       "confidence": .8, "probabilities": [.025] * 7 + [.8, .025]}],
            "tile_counts": [0] * 7 + [1, 0],
            "pixel_counts": [0] * 7 + [384, 0],
            "area_ratios": [0] * 7 + [1, 0],
            "presentation": {"boundaries": True, "opacity": .4},
        }
    elif mode == "segmentation":
        analysis = {
            "mode": "segmentation", "image_size": [24, 16],
            "classes": [{"label": "Test tissue", "color": [204, 121, 167]}],
            "pixel_counts": [384], "presentation": {"opacity": .3},
            "overlay_default_opacity": .2,
        }
    else:
        analysis = {"mode": "single_image", "classification_mode": "single_image"}
    record_id = window.database_manager.insert_record(
        str(original), "synthetic-layout-only", "segmentation" if mode == "segmentation" else "classification",
        None if mode == "segmentation" else "STR", None if mode == "segmentation" else .8,
        str(overlay), result_color_mask_path=str(color), analysis_metadata=analysis,
    )
    window.history_panel.set_records(window.database_manager.get_all_records())
    return record_id, (original, overlay, color)


@pytest.mark.parametrize("mode", ["single_image", "tiled_analysis", "segmentation"])
def test_history_activation_restores_real_source_thumbnail(qtbot, tmp_path, mode):
    window = make_window(qtbot, tmp_path)
    previous = tmp_path / "previous.png"
    Image.new("RGB", (12, 12), (10, 20, 230)).save(previous)
    window.inference_panel.set_image(str(previous))
    record_id, paths = save_record(window, tmp_path, mode)
    window.history_panel.record_activated.emit(record_id)

    panel = window.inference_panel
    assert panel._image_path == str(paths[0])
    assert panel.image_filename_label.toolTip() == paths[0].name
    assert panel._source_pixmap.size().width() == 24
    assert panel._source_pixmap.toImage().pixelColor(0, 0).getRgb()[:3] == (200, 40, 60)
    assert panel.thumbnail_label.pixmap().toImage().pixelColor(0, 0).getRgb()[:3] == (200, 40, 60)
    assert window._current_result["original_image_path"] == panel._image_path
    assert window.action_panel.metadata_labels["record"].text() == f"#{record_id}"
    assert window.tabs.currentWidget() is window.result_panel


def test_missing_history_source_removes_previous_thumbnail(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    record_id, paths = save_record(window, tmp_path, "single_image")
    window.inference_panel.set_image(str(paths[0]))
    paths[0].unlink()
    window.history_panel.record_activated.emit(record_id)

    assert window.inference_panel._image_path == ""
    assert window.inference_panel._source_pixmap.isNull()
    assert window.inference_panel.thumbnail_label.isHidden()
    assert not window.inference_panel.image_error_label.isHidden()
    assert not window.inference_panel.run_button.isEnabled()
    assert window.result_panel.classification_label.text() == "STR"
    assert window.action_panel.export_png_button.isEnabled()


@pytest.mark.parametrize("mode", ["single_image", "tiled_analysis", "segmentation"])
def test_clear_view_preserves_records_files_settings_and_allows_history_restore(qtbot, tmp_path, mode):
    window = make_window(qtbot, tmp_path)
    record_id, paths = save_record(window, tmp_path, mode)
    window.history_panel.record_activated.emit(record_id)
    window.history_panel.search_input.setText("keep my filter")
    window._last_pdf_path = tmp_path / "previous.pdf"
    window.open_export_button.show()
    records_before = deepcopy(window.database_manager.get_all_records())
    files_before = {path: path.read_bytes() for path in paths}
    settings_before = {key: window.settings.value(key) for key in window.settings.allKeys()}
    parameters_before = deepcopy(window.inference_panel.classification_parameters())
    model_before = (window.inference_panel.built_in_checkbox.isChecked(),
                    window.inference_panel._custom_model_path,
                    window.inference_panel.model_status_label.text())

    qtbot.mouseClick(window.action_panel.clear_view_button, Qt.LeftButton)

    assert window._current_result is None
    assert window.current_record_id is None
    assert window._selected_history_record_id is None
    assert window.inference_panel._image_path == ""
    assert window.inference_panel._source_pixmap.isNull()
    assert window.inference_panel.image_filename_label.text() == ""
    assert window.inference_panel.image_error_label.isHidden()
    assert not window.inference_panel.run_button.isEnabled()
    assert window.result_panel.result_stack.currentWidget() is window.result_panel.empty_page
    assert window.result_panel.image_label.pixmap().isNull()
    assert window.result_panel.tile_page.analysis is None
    assert window.result_panel.segmentation_page.analysis is None
    assert window.history_panel.selected_record_ids() == []
    assert not window.history_panel.table.currentIndex().isValid()
    assert not window.action_panel.rerun_button.isEnabled()
    assert not window.action_panel.export_png_button.isEnabled()
    assert not window.action_panel.export_pdf_button.isEnabled()
    assert all(label.text() == "-" for label in window.action_panel.metadata_labels.values())
    assert window._last_pdf_path is None
    assert window.open_export_button.isHidden()
    assert window.database_manager.get_all_records() == records_before
    assert {path: path.read_bytes() for path in paths} == files_before
    assert {key: window.settings.value(key) for key in settings_before} == settings_before
    assert window.inference_panel.classification_parameters() == parameters_before
    assert (window.inference_panel.built_in_checkbox.isChecked(),
            window.inference_panel._custom_model_path,
            window.inference_panel.model_status_label.text()) == model_before
    assert window.history_panel.search_input.text() == "keep my filter"

    # Clearing is repeatable and a saved record can still be reopened.
    window.action_panel.clear_view_button.click()
    window.history_panel.record_activated.emit(record_id)
    assert window.current_record_id == record_id
    assert window.inference_panel._image_path == str(paths[0])
    assert window.action_panel.export_pdf_button.isEnabled()


@pytest.mark.parametrize("method", ["button", "escape", "empty_space", "ctrl_click"])
def test_history_can_return_to_zero_selected_rows(qtbot, tmp_path, method):
    window = make_window(qtbot, tmp_path)
    record_id, _ = save_record(window, tmp_path, "single_image")
    window.history_panel.record_activated.emit(record_id)
    result_before = deepcopy(window._current_result)
    window.tabs.setCurrentWidget(window.history_panel)
    table = window.history_panel.table
    qtbot.waitUntil(lambda: table.viewport().height() > table.rowHeight(0) * 2)
    assert window.history_panel.selected_record_ids() == [record_id]
    spy = QSignalSpy(window.history_panel.selection_changed)
    if method == "button":
        qtbot.mouseClick(window.history_panel.clear_selection_button, Qt.LeftButton)
    elif method == "escape":
        qtbot.keyClick(table, Qt.Key_Escape)
    elif method == "empty_space":
        pos = QPoint(10, table.viewport().height() - 8)
        assert not table.indexAt(pos).isValid()
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=pos)
    else:
        pos = table.visualItemRect(table.item(0, 0)).center()
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, Qt.ControlModifier, pos=pos)

    assert window.history_panel.selected_record_ids() == []
    assert spy[-1] == [None]
    assert not window.action_panel.rerun_button.isEnabled()
    assert not window.history_panel.delete_selected_button.isEnabled()
    assert not window.history_panel.clear_selection_button.isEnabled()
    assert window._current_result == result_before
    assert window.action_panel.export_png_button.isEnabled()
    assert window.database_manager.get_record_by_id(record_id) is not None
    if method != "ctrl_click":
        assert not table.currentIndex().isValid()


@pytest.mark.parametrize("busy", ["inference", "export", "pending_rerun"])
def test_clear_view_is_blocked_during_active_work(qtbot, tmp_path, busy):
    window = make_window(qtbot, tmp_path)
    record_id, paths = save_record(window, tmp_path, "single_image")
    window.history_panel.record_activated.emit(record_id)
    before = deepcopy(window._current_result)
    attribute = {"inference": "_inference_engine", "export": "_pdf_export_worker",
                 "pending_rerun": "_pending_rerun"}[busy]
    setattr(window, attribute, record_id if busy == "pending_rerun" else object())
    try:
        window._update_clear_view_enabled()
        assert not window.action_panel.clear_view_button.isEnabled()
        window._clear_current_view()
        assert window._current_result == before
        assert window.inference_panel._image_path == str(paths[0])
        assert window.current_record_id == record_id
    finally:
        setattr(window, attribute, None)
        window._update_clear_view_enabled()
    assert window.action_panel.clear_view_button.isEnabled()


def test_refresh_does_not_retain_an_old_row_selection(qtbot):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    records = [{"id": 1}, {"id": 2}]
    panel.set_records(records)
    panel.table.selectRow(0)
    panel.set_records(list(reversed(records)))
    assert panel.selected_record_ids() == []
    assert not panel.table.currentIndex().isValid()
    assert not panel.delete_selected_button.isEnabled()


@pytest.mark.parametrize("size", [(640, 480), (480, 360)])
def test_clear_and_run_controls_remain_accessible_in_small_windows(qtbot, tmp_path, monkeypatch, size):
    available = QRect(0, 0, *size)
    monkeypatch.setattr(MainWindow, "_available_geometry", lambda self: QRect(available))
    window = make_window(qtbot, tmp_path)
    qtbot.waitUntil(lambda: available.contains(window.frameGeometry()))
    run = window.inference_panel.run_button
    assert window.rect().contains(QRect(run.mapTo(window, run.rect().topLeft()), run.size()))
    bar = window.body_scroll.horizontalScrollBar()
    bar.setValue(bar.maximum())
    qtbot.wait(20)
    for button in (window.action_panel.rerun_button, window.action_panel.clear_view_button):
        assert window.rect().contains(QRect(button.mapTo(window, button.rect().topLeft()), button.size()))


def test_pending_rerun_validation_failure_reenables_clear(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    record_id, _ = save_record(window, tmp_path, "single_image")
    window._pending_rerun = record_id
    window._pending_rerun_builtin = True
    window._update_clear_view_enabled()
    assert not window.action_panel.clear_view_button.isEnabled()
    window._model_validation_finished()
    assert window._pending_rerun is None
    assert window.action_panel.clear_view_button.isEnabled()
