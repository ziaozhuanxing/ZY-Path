"""Readable tile identifiers and preference actions without production weights."""
from copy import deepcopy
import json

from PIL import Image
import pytest
from PyQt5.QtCore import QPointF, QSettings
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel

from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from test_screen_fit_and_tile_grid import synthetic_result


@pytest.mark.parametrize("mode", ["overlay", "color_map", "original"])
def test_numbers_match_details_actual_crops_and_survive_navigation(qtbot, tmp_path, mode):
    result = synthetic_result(tmp_path)
    analysis = result["classification_analysis"]
    before = deepcopy(analysis)
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(1000, 850)
    original = Image.open(result["image_path"]).copy()
    page.show_result(original, result["color_map"], analysis)
    page.show()
    page.view_mode.setCurrentIndex(page.view_mode.findData(mode))
    qtbot.wait(40)
    unnumbered = page.render_image().tobytes()
    raw_pixmap = page.image.pixmap().toImage()
    assert not page.tile_numbers.isChecked()
    assert not page.image._numbered_tiles
    page.tile_numbers.setChecked(True)
    assert page.image._grid_lines == []  # numbering does not require grid lines
    assert page.image.pixmap().toImage() == raw_pixmap
    boxes = [tuple(tile["box"]) for tile in analysis["tiles"]]
    assert page.image._numbered_tiles == boxes
    assert page.original_view._numbered_tiles == boxes
    assert [page.table.item(row, 0).text() for row in range(49)] == [str(n) for n in range(1, 50)]
    assert page.table.item(48, 1).text() == "[3072, 3072, 3552, 3536]"
    assert page.table.item(48, 2).text() == "MUC"
    assert page.table.item(48, 3).text() == "80.00%"
    assert page.render_image().tobytes() != unnumbered

    for action in (page.image.fit_to_view, page.image.zoom_in, page.image.zoom_out,
                   page.image.fit_to_view):
        action()
        qtbot.wait(10)
        view = page.image.graphics_view
        pixels = view.viewport().grab().toImage()
        dpr = pixels.devicePixelRatio()
        visible = 0
        for box in boxes:
            x0, y0, x1, y1 = box
            centre = view.mapFromScene(QPointF((x0 + x1) / 2, (y0 + y1) / 2))
            if not view.viewport().rect().adjusted(18, 18, -18, -18).contains(centre):
                continue
            colours = [pixels.pixelColor(round((centre.x() + dx) * dpr),
                                         round((centre.y() + dy) * dpr))
                       for dx in range(-12, 13) for dy in range(-8, 9)]
            # Each visible crop centre contains a dark badge and white numeral,
            # even though the unmodified source pixels have no such markings.
            assert any(c.red() < 40 and c.green() < 50 for c in colours)
            assert any(min(c.red(), c.green(), c.blue()) > 210 for c in colours)
            visible += 1
        assert visible > 0
        if action == page.image.fit_to_view:
            assert visible == 49
    assert page.tile_tooltip_at(page.image.graphics_view.mapFromScene(QPointF(3312, 3304))).startswith("Tile 49: MUC")
    page.boundaries.setChecked(True)
    assert len(page.image._grid_lines) == 16
    assert page.image._numbered_tiles == boxes
    page.tile_numbers.setChecked(False)
    assert page.render_image(include_boundaries=False).tobytes() == unnumbered
    assert not page.image._numbered_tiles and not page.original_view._numbered_tiles
    assert analysis == before
    page.clear()
    assert page.image._numbered_tiles == page.original_view._numbered_tiles == []


def test_numbered_history_png_and_pdf_preserve_ids_and_predictions(qtbot, tmp_path, monkeypatch):
    result = synthetic_result(tmp_path)
    predictions = deepcopy(result["classification_analysis"])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("export/pngReminderEnabled", False)
    settings.setValue("export/pdfReminderEnabled", False)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.db", results_dir=tmp_path / "results",
                        builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window.resize(1100, 850)
    window.show()
    window._show_inference_result(result)
    page = window.result_panel.tile_page
    record_id = window.database_manager.get_all_records()[0]["id"]
    page.tile_numbers.setChecked(True)
    page.compare.setChecked(True)
    saved = window.database_manager.get_all_records()[0]
    assert json.loads(saved["analysis_json"])["presentation"]["tile_numbers"] is True
    window._show_record_activated(record_id)
    qtbot.wait(30)
    assert page.tile_numbers.isChecked() and page.compare.isChecked()
    assert page.image._numbered_tiles == page.original_view._numbered_tiles
    expected = page.render_image()
    target = tmp_path / "numbered.png"
    monkeypatch.setattr("ui.main_window.QFileDialog.getSaveFileName", lambda *a, **k: (str(target), ""))
    window._export_current_png()
    with Image.open(target) as exported:
        assert exported.size == (3552, 3536)
        assert exported.tobytes() == expected.tobytes()
    metadata = json.loads(target.with_suffix(".png.json").read_text())
    saved_analysis = metadata["classification_analysis"]
    assert saved_analysis["presentation"]["tile_numbers"] is True
    for key in ("tiles", "tile_counts", "pixel_counts", "area_ratios", "classes"):
        assert saved_analysis[key] == predictions[key]
    pdf_calls = []
    def inspect_pdf(output, original, rendered, report, **kwargs):
        with Image.open(rendered) as image:
            assert image.tobytes() == expected.tobytes()
        assert report["classification_analysis"]["presentation"]["tile_numbers"] is True
        assert kwargs["color_map"].tobytes() == window.result_panel.tile_page.color_map.tobytes()
        pdf_calls.append(output)
    monkeypatch.setattr(window.export_manager, "export_pdf", inspect_pdf)
    window._export_current_pdf()
    assert len(pdf_calls) == 1


def test_square_action_persists_height_without_locking_dimensions(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("classificationTiles/width", 300)
    settings.setValue("classificationTiles/height", 500)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.sync_tile_height_button.click()
    assert dialog.tile_height.value() == 300
    assert settings.value("classificationTiles/height", type=int) == 300
    dialog.tile_width.setValue(700)
    assert dialog.tile_height.value() == 300
    dialog.tile_height.setValue(99)
    assert dialog.tile_width.value() == 700
    reopened = SettingsDialog(settings)
    qtbot.addWidget(reopened)
    assert (reopened.tile_width.value(), reopened.tile_height.value()) == (700, 99)
    assert reopened.resize_method.currentData() == "pillow_bilinear"


@pytest.mark.parametrize("point_size", [10, 20])
def test_resize_advice_expands_without_changing_preferences_and_contact_is_current(qtbot, tmp_path, point_size):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    font = QFont(dialog.font())
    font.setPointSize(point_size)
    dialog.setFont(font)
    qtbot.addWidget(dialog)
    dialog.navigation.setCurrentRow(1)
    dialog.resize(620, 400)
    dialog.show()
    qtbot.wait(20)
    before = {key: settings.value(key) for key in settings.allKeys()}
    assert dialog.resize_advice.isHidden()
    dialog.resize_advice_button.click()
    assert not dialog.resize_advice.isHidden()
    qtbot.wait(30)  # Allow the expanded wrapped text to update the scroll range.
    advice = dialog.resize_advice.text()
    for phrase in ("Pillow bilinear", "OpenCV linear (INTER_LINEAR)", "512 x 512 crops",
                   "Neither backend is guaranteed to be more accurate", "History Re-run"):
        assert phrase in advice
    assert dialog.pages.currentWidget().horizontalScrollBar().maximum() == 0
    scroll = dialog.pages.currentWidget()
    scroll.ensureWidgetVisible(dialog.resize_advice_button)
    qtbot.wait(20)
    assert scroll.viewport().rect().contains(dialog.resize_advice_button.rect().translated(
        dialog.resize_advice_button.mapTo(scroll.viewport(), dialog.resize_advice_button.rect().topLeft())))
    dialog.resize_advice_button.click()
    assert dialog.resize_advice.isHidden()
    assert {key: settings.value(key) for key in settings.allKeys()} == before
    dialog.navigation.setCurrentRow(3)
    assert "mailto:ziyao604502@gmail.com" in dialog.guide_view.browser.toHtml()
    dialog.navigation.setCurrentRow(5)
    about = dialog.pages.currentWidget().widget()
    contacts = [label for label in about.findChildren(QLabel) if "mailto:ziyao604502@gmail.com" in label.text()]
    assert len(contacts) == 1 and contacts[0].openExternalLinks()
    assert "+601123612318" in contacts[0].text()
