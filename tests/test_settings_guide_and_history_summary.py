"""Settings/help and history semantics without production model weights."""
import copy
import json

import pytest
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel

from core.model_loader import ModelLoader
from data.export_manager import _add_metadata_table
from ui.history_panel import HistoryPanel
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.system_information import system_information
from utils.version import APP_VERSION


@pytest.fixture
def settings(tmp_path):
    return QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)


def tiled_record():
    return {"id": 7, "task_type": "classification", "result_label": "ADI", "confidence": .99,
            "analysis_json": json.dumps({"mode": "classification_tiles", "image_size": [10, 8],
                "classes": [{"label": "ADI"}, {"label": "BACK"}],
                "tile_counts": [1, 3], "pixel_counts": [30, 50]})}


def test_tiled_history_shows_area_summary_not_global_label_or_confidence(qtbot):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    record = tiled_record()
    original = copy.deepcopy(record)
    panel.set_records([record])
    assert panel.table.item(0, 4).text() == "Classification / Tiled analysis"
    assert panel.table.item(0, 5).text() == "4 tiles\nBACK 62.5% est. coverage"
    assert panel.table.item(0, 6).text() == "-"
    assert "75.0%" not in panel.table.item(0, 5).text()  # counts are not area
    for column in (5, 6):
        assert "not a whole-image prediction" in panel.table.item(0, column).toolTip()
        assert "real crop areas" in panel.table.item(0, column).toolTip()
    assert record == original
    assert panel.select_record(7)
    assert panel.selected_record_id() == 7


@pytest.mark.parametrize("mode", ["classification_tiles", "tiled_analysis", "classification_mode_only"])
def test_tiled_history_recognizes_saved_mode_variants(qtbot, mode):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    record = tiled_record()
    analysis = json.loads(record["analysis_json"])
    analysis["mode"] = mode
    if mode == "classification_mode_only":
        analysis.pop("mode")
        analysis["classification_mode"] = "tiled_analysis"
    record["analysis_json"] = json.dumps(analysis)
    values = panel._record_values(record)
    assert values[4] == "Classification / Tiled analysis"
    assert values[5] == "4 tiles\nBACK 62.5% est. coverage"
    assert values[6] == "-"


@pytest.mark.parametrize("bad_areas", [[30, 45], [-1, 81], ["30", 50], None, [float('nan'), 50]])
def test_history_never_replaces_missing_area_data_with_tile_percentages(qtbot, bad_areas):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    record = tiled_record()
    analysis = json.loads(record["analysis_json"])
    analysis["pixel_counts"] = bad_areas
    record["analysis_json"] = json.dumps(analysis)
    values = panel._record_values(record)
    assert values[5] == "4 tiles\nCoverage unavailable"
    assert values[6] == "-"


@pytest.mark.parametrize("metadata", ["bad json", "[]", "null", "{}"])
def test_known_tiled_record_with_missing_details_does_not_show_single_label(qtbot, metadata):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    record = {**tiled_record(), "analysis_json": metadata, "classification_mode": "tiled_analysis"}
    values = panel._record_values(record)
    assert values[4] == "Classification / Tiled analysis"
    assert values[5] == "Tile details unavailable\nCoverage unavailable"
    assert values[6] == "-"


def test_legacy_single_and_segmentation_history_keep_their_meaning(qtbot):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    single = {"task_type": "classification", "result_label": "TUM", "confidence": .875}
    assert panel._record_values(single)[4:] == ["Classification", "TUM", "87.5 %"]
    single["analysis_json"] = '{"mode":"single_image"}'
    assert panel._record_values(single)[4:] == ["Classification / Single image", "TUM", "87.5 %"]
    assert panel._record_values({"task_type": "segmentation"})[4:] == ["Segmentation", "-", "-"]


def test_system_info_is_visible_readonly_and_copy_matches_display(qtbot, settings, monkeypatch):
    monkeypatch.setattr(ModelLoader, "load_with_info", lambda *a: pytest.fail("System information must not load models"))
    settings.setValue("models/classification/defaultPath", "/private/person/source-model.pt")
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.navigation.setCurrentRow(dialog._PAGE_NAMES.index("System Information"))
    assert dialog.system_info_view.isReadOnly()
    text = dialog.system_info_view.toPlainText()
    for expected in ("ZY-Path version: 1.0", "Runtime", "Technology stack", "PyQt5:", "torch:",
                     "opencv-python-headless:", "SQLite:", "Saved configuration",
                     "NCT-CRC-HE-100K; 224 x 224 px at 0.5 micrometres/pixel",
                     "Uploaded-image physical resolution / scale matching: not verified",
                     "editable starting value, not a verified training-scale match"):
        assert expected in text
    assert "/private/person" not in text
    dialog.copy_system_info_button.click()
    assert QApplication.clipboard().text() == text
    assert "copied" in dialog.system_info_feedback.text().lower()
    settings.setValue("classificationTiles/width", 321)
    dialog.copy_system_info_button.click()
    assert QApplication.clipboard().text() == text
    dialog.refresh_system_info_button.click()
    assert "321 x 512 px" in dialog.system_info_view.toPlainText()
    dialog.copy_system_info_button.click()
    assert QApplication.clipboard().text() == dialog.system_info_view.toPlainText()


def test_missing_technology_is_reported_instead_of_silently_omitted(settings, monkeypatch):
    import importlib.metadata
    def version(package):
        if package == "opencv-python-headless":
            raise importlib.metadata.PackageNotFoundError(package)
        return "test-version"
    monkeypatch.setattr("ui.system_information.importlib.metadata.version", version)
    text = system_information(settings)
    assert "opencv-python-headless: not installed" in text
    assert "Pillow: test-version" in text


def test_about_version_defaults_to_one_and_preserves_explicit_override(qtbot, settings):
    for version in (None, "2.5-test"):
        dialog = SettingsDialog(settings, app_version=version)
        qtbot.addWidget(dialog)
        text = " ".join(label.text() for label in dialog.findChildren(QLabel))
        expected = version or APP_VERSION
        assert f"Version: {expected}" in text
        assert f"ZY-Path version: {expected}" in dialog.system_info_view.toPlainText()
        assert "Not configured" not in text


def test_classification_preference_applies_now_and_next_launch_without_rewriting_history(qtbot, tmp_path, settings):
    window = MainWindow(settings=settings, db_path=tmp_path / "db.sqlite", builtin_model_path=tmp_path / "missing.pt")
    qtbot.addWidget(window)
    window._show_settings()
    dialog = window._settings_dialog
    assert window.inference_panel.classification_mode() == "single_image"
    dialog.startup_mode.setCurrentIndex(dialog.startup_mode.findData("tiled_analysis"))
    assert settings.value("classification/defaultMode") == "tiled_analysis"
    assert window.inference_panel.classification_mode() == "tiled_analysis"
    reopened = MainWindow(settings=settings, db_path=tmp_path / "db2.sqlite", builtin_model_path=tmp_path / "missing.pt")
    qtbot.addWidget(reopened)
    assert reopened.inference_panel.classification_mode() == "tiled_analysis"
    assert reopened._record_classification_parameters({})["classification_mode"] == "single_image"
    assert reopened._record_classification_parameters(tiled_record())["classification_mode"] == "tiled_analysis"


def test_classification_reset_changes_only_its_own_preferences(qtbot, settings):
    retained = {"models/classification/defaultPath": "keep.pt", "appearance/theme": "Dark",
                "export/pngReminderEnabled": False, "window/maximized": True}
    for key, value in {**retained, "classification/defaultMode": "tiled_analysis", "classificationTiles/width": 300,
                       "classificationTiles/height": 700, "classification/resizeBackend": "opencv_linear"}.items():
        settings.setValue(key, value)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.reset_classification_button.click()
    assert dialog.startup_mode.currentData() == "single_image"
    assert dialog.tile_width.value() == dialog.tile_height.value() == 512
    assert dialog.resize_method.currentData() == "pillow_bilinear"
    for key, value in retained.items():
        assert settings.value(key) == value
    again = SettingsDialog(settings)
    qtbot.addWidget(again)
    assert again.startup_mode.currentData() == "single_image"
    assert again.tile_width.value() == again.tile_height.value() == 512
    assert again.resize_method.currentData() == "pillow_bilinear"


@pytest.mark.parametrize("point_size", [10, 15, 20])
def test_settings_pages_scroll_and_guide_sections_are_navigable(qtbot, settings, point_size):
    app = QApplication.instance()
    previous_font = app.font()
    font = QFont(previous_font)
    font.setPointSize(point_size)
    app.setFont(font)
    try:
        dialog = SettingsDialog(settings)
        qtbot.addWidget(dialog)
        dialog.resize(620, 400)
        dialog.show()
        qtbot.wait(30)
        assert dialog.navigation.horizontalScrollBar().maximum() == 0
        for name in ("Preferences", "Guide & Support", "System Information", "About"):
            dialog.navigation.setCurrentRow(dialog._PAGE_NAMES.index(name))
            qtbot.wait(20)
            scroll = dialog.pages.currentWidget()
            assert scroll.horizontalScrollBar().maximum() == 0
        dialog.navigation.setCurrentRow(dialog._PAGE_NAMES.index("Guide & Support"))
        guide = dialog.guide_view
        assert len(guide.section_actions) >= 10
        topic = len(guide.section_actions) - 1
        guide.section_actions[topic].trigger()
        qtbot.wait(30)
        scroll = dialog.pages.currentWidget()
        assert scroll.verticalScrollBar().maximum() == 0
        assert guide.browser.verticalScrollBar().value() > 0
        assert guide.current_section == topic
        assert guide.section_actions[topic].isChecked()
        assert guide.contents_button.isVisible() and guide.section_label.isVisible()
        text = guide.browser.toPlainText()
        for section in ("Input panel", "Result viewer", "Export and session", "History", "Settings"):
            assert section in text
        assert "fictional" not in text and "Replace these examples" not in text
        assert "ziyao604502@gmail.com" in text and "+601123612318" in text
        assert "do not treat segmentation as classification ground truth" in text
    finally:
        app.setFont(previous_font)


@pytest.mark.parametrize("tiled", [False, True])
def test_pdf_labels_distinguish_aggregate_from_single_image(tiled):
    from data.export_manager import _ReportPDF
    pdf = _ReportPDF(None)
    pdf.set_compression(False)
    pdf.add_page()
    _add_metadata_table(pdf, {"classification_mode": "tiled_analysis" if tiled else "single_image",
                              "result_label": "STR", "confidence": .85})
    text = bytes(pdf.output()).decode("latin-1")
    if tiled:
        assert "Aggregate tile label" in text
        assert "Area-weighted mean probability" in text
        assert "Result label" not in text
    else:
        assert "Result label" in text
        assert "Confidence" in text
        assert "Aggregate tile label" not in text
    assert "85.0%" in text


def test_tiled_history_summary_has_readable_two_line_cells(qtbot):
    panel = HistoryPanel()
    qtbot.addWidget(panel)
    panel.resize(1100, 420)
    panel.set_records([tiled_record()])
    panel.show()
    qtbot.wait(30)
    metrics = panel.table.fontMetrics()
    item = panel.table.item(0, 5)
    assert item.text().splitlines() == ["4 tiles", "BACK 62.5% est. coverage"]
    assert panel.table.rowHeight(0) >= 2 * metrics.height()
    assert panel.table.columnWidth(5) > max(metrics.horizontalAdvance(line) for line in item.text().splitlines())
