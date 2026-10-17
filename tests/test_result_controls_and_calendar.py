"""Mouse, keyboard and locale regressions for result controls and history dates."""
from copy import deepcopy

import pytest
from PyQt5.QtCore import QDate, QLocale, QPoint, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QTableView, QToolButton, QWidget

from test_linked_image_comparison import make_page
from ui.history_panel import HistoryPanel
from ui.result_check_box import ResultCheckBox
from ui.theme import apply_theme


@pytest.fixture(params=["Light", "Dark"])
def result_theme(qapp, request):
    style, font, theme = qapp.styleSheet(), QFont(qapp.font()), qapp.property("zyTheme")
    apply_theme(qapp, request.param)
    yield
    qapp.setStyleSheet(style)
    qapp.setFont(font)
    qapp.setProperty("zyTheme", theme)


@pytest.mark.parametrize("kind", ["classification", "segmentation"])
def test_result_controls_toggle_once_from_text_padding_and_edges(qtbot, tmp_path, result_theme, kind):
    page, result = make_page(qtbot, tmp_path, kind, (1100, 740))
    analysis = deepcopy(result.get("classification_analysis"))
    controls = [page.compare, page.link_views]
    if kind == "classification":
        controls.insert(0, page.boundaries)
    for control in controls:
        page.compare.setChecked(True)
        qtbot.wait(20)
        for location in ("text", "left_padding", "right_padding", "bottom_padding"):
            rect = control.rect()
            point = {"text": QPoint(rect.width() // 2, rect.height() // 2),
                     "left_padding": QPoint(2, rect.height() // 2),
                     "right_padding": QPoint(rect.width() - 3, rect.height() // 2),
                     "bottom_padding": QPoint(rect.width() // 2, rect.height() - 2)}[location]
            before, size = control.isChecked(), control.sizeHint()
            spy = QSignalSpy(control.toggled)
            qtbot.mouseClick(control, Qt.LeftButton, pos=point)
            qtbot.wait(20)
            assert control.isChecked() is not before, location
            assert len(spy) == 1
            assert not control.property("keyboardFocus")
            assert control.sizeHint() == size
        control.setEnabled(False)
        before = control.isChecked()
        qtbot.mouseClick(control, Qt.LeftButton, pos=control.rect().center())
        assert control.isChecked() == before
        control.setEnabled(True)
    assert result.get("classification_analysis") == analysis
    if kind == "classification":
        page.boundaries.setChecked(True)
        assert len(page.image._grid_lines) == 16  # Eight x and eight y boundaries.
        assert page.image._grid_lines == page.original_view._grid_lines
        page.boundaries.setChecked(False)
        assert page.image._grid_lines == page.original_view._grid_lines == []


def test_keyboard_focus_is_visible_without_mouse_focus_frame(qtbot, result_theme):
    row = QWidget()
    layout = QHBoxLayout(row)
    first = QPushButton("Before")
    toggle = ResultCheckBox("Tile boundaries")
    last = QPushButton("After")
    for control in (first, toggle, last):
        layout.addWidget(control)
    qtbot.addWidget(row)
    row.show()
    row.activateWindow()
    first.setFocus()
    qtbot.wait(20)
    size = toggle.sizeHint()
    qtbot.keyClick(first, Qt.Key_Tab)
    assert toggle.hasFocus() and toggle.property("keyboardFocus")
    qtbot.keyClick(toggle, Qt.Key_Space)
    assert toggle.isChecked()
    assert toggle.sizeHint() == size
    qtbot.mouseClick(toggle, Qt.LeftButton, pos=QPoint(toggle.width() - 3, 2))
    assert not toggle.isChecked() and not toggle.property("keyboardFocus")
    assert toggle.sizeHint() == size
    qtbot.keyClick(toggle, Qt.Key_Tab)
    assert last.hasFocus()
    qtbot.keyClick(last, Qt.Key_Backtab)
    assert toggle.hasFocus() and toggle.property("keyboardFocus")


def test_history_calendar_stays_english_under_chinese_system_locale(qtbot, qapp):
    original_default = QLocale()
    chinese = QLocale(QLocale.Chinese, QLocale.China)
    QLocale.setDefault(chinese)
    try:
        panel = HistoryPanel()
        panel.setLocale(chinese)
        qtbot.addWidget(panel)
        panel.resize(1000, 600)
        panel.show()
        panel.date_filter_checkbox.setChecked(True)
        for edit in (panel.from_date_edit, panel.to_date_edit):
            calendar = edit.calendarWidget()
            assert edit.locale().language() == QLocale.English
            assert calendar.locale().language() == QLocale.English
            edit.setDate(QDate(2026, 10, 17))
            qtbot.mouseClick(edit, Qt.LeftButton, pos=QPoint(edit.width() - 8, edit.height() // 2))
            qtbot.waitUntil(calendar.isVisible)
            month = calendar.findChild(QToolButton, "qt_calendar_monthbutton")
            assert month.text() == "October"
            view = calendar.findChild(QTableView, "qt_calendar_calendarview")
            model = view.model()
            headers = [str(model.index(0, column).data()) for column in range(model.columnCount())]
            assert "Mon" in headers and "Sun" in headers
            target = next(model.index(row, column) for row in range(1, model.rowCount())
                          for column in range(model.columnCount())
                          if str(model.index(row, column).data()) == "18")
            qtbot.mouseClick(view.viewport(), Qt.LeftButton, pos=view.visualRect(target).center())
            qtbot.waitUntil(lambda: not calendar.isVisible())
            assert edit.date() == QDate(2026, 10, 18)
            assert edit.text() == "2026-10-18"
        assert panel.locale().language() == QLocale.Chinese
        assert QLocale().language() == QLocale.Chinese
        spy = QSignalSpy(panel.search_requested)
        panel.search_button.click()
        assert len(spy) == 1
        assert spy[0][1] is not None and spy[0][2] is not None
    finally:
        QLocale.setDefault(original_default)
