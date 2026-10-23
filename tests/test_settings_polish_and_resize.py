"""Settings feedback, real scroll ranges and dock/restore comparison regressions."""
from copy import deepcopy

import pytest
from PyQt5.QtCore import QRect, QSettings, Qt
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QApplication, QBoxLayout

from ui.help_content import GUIDE_SECTIONS
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from test_linked_image_comparison import assert_linked
from test_screen_fit_and_tile_grid import synthetic_result
from test_segmentation_results_layout import segmentation_fixture


def make_dialog(qtbot, tmp_path):
    dialog = SettingsDialog(QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat))
    qtbot.addWidget(dialog)
    dialog.show()
    return dialog


def test_copy_feedback_expires_restarts_and_clears_without_refresh(qtbot, tmp_path):
    dialog = make_dialog(qtbot, tmp_path)
    dialog.navigation.setCurrentRow(dialog._PAGE_NAMES.index("System Information"))
    timer = dialog._copy_feedback_timer
    assert timer.interval() == 2500 and timer.isSingleShot()
    timer.setInterval(140)
    text = dialog.system_info_view.toPlainText()
    dialog.copy_system_info_button.click()
    assert dialog.system_info_feedback.text() == "Copied to clipboard."
    assert QApplication.clipboard().text() == text
    qtbot.wait(90)
    dialog.copy_system_info_button.click()
    qtbot.wait(90)
    assert dialog.system_info_feedback.text() == "Copied to clipboard."
    qtbot.waitUntil(lambda: not dialog.system_info_feedback.text())
    assert QApplication.clipboard().text() == text
    assert dialog.system_info_view.toPlainText() == text
    assert not timer.isActive()
    dialog.copy_system_info_button.click()
    dialog.refresh_system_info_button.click()
    assert not dialog.system_info_feedback.text() and not timer.isActive()
    dialog.copy_system_info_button.click()
    dialog.hide()
    assert not dialog.system_info_feedback.text() and not timer.isActive()
    dialog.show()
    assert not dialog.system_info_feedback.text()


@pytest.mark.parametrize("point_size", [10, 15, 20])
def test_preferences_height_follows_wrapped_content_on_repeated_resize(qtbot, qapp, tmp_path, point_size):
    original_font = QFont(qapp.font())
    font = QFont(original_font)
    font.setPointSize(point_size)
    qapp.setFont(font)
    try:
        dialog = make_dialog(qtbot, tmp_path)
        dialog.navigation.setCurrentRow(1)
        heights = []
        for width in (620, 1100, 620, 1100):
            dialog.resize(width, 600)
            qtbot.wait(40)
            scroll = dialog.pages.currentWidget()
            page = scroll.widget()
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
            qtbot.wait(10)
            last = dialog.reset_layout_button
            bottom = last.mapTo(page, last.rect().bottomLeft()).y()
            assert 0 < page.height() - bottom <= 40
            assert abs(page.height() - page.layout().heightForWidth(page.width())) <= 2
            assert scroll.horizontalScrollBar().maximum() == 0
            assert scroll.viewport().rect().contains(last.rect().translated(
                last.mapTo(scroll.viewport(), last.rect().topLeft())))
            heights.append(page.height())
        assert heights[1] < heights[0]
        assert heights[0] == heights[2] and heights[1] == heights[3]
    finally:
        qapp.setFont(original_font)


def test_guide_contents_tracks_reading_and_remains_visible(qtbot, tmp_path):
    dialog = make_dialog(qtbot, tmp_path)
    dialog.resize(860, 560)
    dialog.navigation.setCurrentRow(3)
    qtbot.wait(40)
    guide = dialog.guide_view
    bar = guide.browser.verticalScrollBar()
    toolbar_position = guide.contents_button.mapTo(dialog, guide.contents_button.rect().topLeft())
    assert guide.current_section == 0
    assert not guide.previous_button.isEnabled() and guide.next_button.isEnabled()
    qtbot.mouseClick(guide.next_button, Qt.LeftButton)
    assert guide.current_section == 1
    qtbot.mouseClick(guide.previous_button, Qt.LeftButton)
    assert guide.current_section == 0
    for index in (3, 5, 8):
        guide.section_actions[index].trigger()
        qtbot.wait(20)
        assert guide.current_section == index
        cursor = QTextCursor(guide.browser.document())
        cursor.setPosition(guide._heading_positions[index])
        assert abs(guide.browser.cursorRect(cursor).top()) <= 10
        # Scrolling directly through the document must update the indicator,
        # not only menu actions or next/previous commands.
        bar.setValue(bar.value() + 30)
        qtbot.wait(10)
        assert guide.current_section == index
        assert guide.section_actions[index].isChecked()
        assert GUIDE_SECTIONS[index][0] in guide.section_label.text()
        assert guide.contents_button.mapTo(dialog, guide.contents_button.rect().topLeft()) == toolbar_position
    bar.setValue(bar.maximum())
    assert guide.current_section == len(GUIDE_SECTIONS) - 1
    assert not guide.next_button.isEnabled() and guide.previous_button.isEnabled()
    bar.setValue(0)
    assert guide.current_section == 0 and not guide.previous_button.isEnabled()
    for width in (620, 1100, 620):
        dialog.resize(width, 600)
        qtbot.wait(40)
        assert dialog.pages.currentWidget().verticalScrollBar().maximum() == 0
        assert guide.browser.horizontalScrollBar().maximum() == 0
        expected_range = guide.browser.document().size().height() - guide.browser.viewport().height()
        assert abs(bar.maximum() - max(0, expected_range)) <= 2
    assert all(":" not in title for title, _ in GUIDE_SECTIONS)
    html = guide.browser.toHtml()
    assert "mailto:ziyao604502@gmail.com" in html
    assert "+601123612318" in guide.browser.toPlainText()
    for unwanted in ("Replace these examples", "fictional", "example.invalid", "supported release"):
        assert unwanted not in guide.browser.toPlainText()


@pytest.mark.parametrize("kind", ["classification", "segmentation"])
def test_main_comparison_returns_to_side_by_side_after_docking(qtbot, tmp_path, monkeypatch, kind):
    # Logical desktop geometry, independent of the offscreen plugin's tiny screen.
    monkeypatch.setattr(MainWindow, "_available_geometry", lambda self: QRect(0, 0, 1920, 1080))
    window = MainWindow(settings=QSettings(str(tmp_path / "main.ini"), QSettings.IniFormat),
                        db_path=tmp_path / "db.sqlite", results_dir=tmp_path / "results",
                        builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window.resize(1500, 900)
    window.show()
    qtbot.wait(150)
    result = synthetic_result(tmp_path) if kind == "classification" else segmentation_fixture(tmp_path)
    window._show_inference_result(result)
    page = window.result_panel.tile_page if kind == "classification" else window.result_panel.segmentation_page
    page.compare.setChecked(True)
    qtbot.wait(60)
    before_image = page.render_image().tobytes()
    analysis = deepcopy(result.get("classification_analysis"))
    counts = result.get("counts")
    counts = counts.copy() if counts is not None else None
    for manual_zoom in (False, True):
        if manual_zoom:
            page.image.zoom_in()
            qtbot.wait(20)
        zoom = page.image.zoom_percent()
        for width in (1500, 680, 1500, 1366, 680, 1500):
            window.resize(width, 900)
            qtbot.wait(80)
            expected = Qt.Horizontal if width >= 1366 else Qt.Vertical
            assert page.comparison_splitter.orientation() == expected
            assert_linked(page)
            assert page.image.view_state()["fit"] is not manual_zoom
            if manual_zoom:
                assert page.image.zoom_percent() == pytest.approx(zoom)
            assert page.render_image().tobytes() == before_image
            assert result.get("classification_analysis") == analysis
            if counts is not None:
                assert (result["counts"] == counts).all()
        if kind == "segmentation":
            page.compare.setChecked(False)
            qtbot.wait(40)
            assert page.content.direction() == QBoxLayout.LeftToRight
            page.compare.setChecked(True)
            qtbot.wait(40)
            assert page.comparison_splitter.orientation() == Qt.Horizontal
