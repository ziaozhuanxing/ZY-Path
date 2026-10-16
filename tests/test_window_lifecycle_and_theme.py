"""Window-manager ownership and rendered theme regressions, without real weights."""
import logging

import pytest
from PyQt5.QtCore import QEvent, QPoint, QSettings, QSize, Qt
from PyQt5.QtGui import QColor, QPalette, QMouseEvent
from PyQt5.QtWidgets import QApplication, QAbstractButton, QScrollArea, QScrollBar, QStyle, QStyleOptionSlider

from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.theme import ACCENT, PRIMARY, DARK_COLORS, LIGHT_COLORS, apply_theme
from test_screen_fit_and_tile_grid import synthetic_result


@pytest.fixture(params=['Light', 'Dark'])
def themed_app(qapp, request):
    old_theme = qapp.property('zyTheme') or 'Light'
    apply_theme(qapp, request.param)
    yield request.param, DARK_COLORS if request.param == 'Dark' else LIGHT_COLORS
    apply_theme(qapp, old_theme)


def make_window(qtbot, tmp_path):
    settings = QSettings(str(tmp_path/'window.ini'), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path/'history.db', builtin_model_path=tmp_path/'missing.pth')
    qtbot.addWidget(window)
    if not settings.contains('window/geometry'):
        window.resize(600, 420)
    window.show()
    qtbot.wait(50)
    return window


def test_interactive_resize_and_layout_leave_size_and_state_to_window_manager(qtbot, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger='ui.main_window')
    w = make_window(qtbot, tmp_path)
    flags = w.windowFlags()
    calls = []
    for method in ('setGeometry', 'setMinimumSize', 'setMaximumSize', 'setWindowState'):
        original = getattr(w, method)
        def observe(*args, original=original, method=method):
            calls.append(method)
            return original(*args)
        monkeypatch.setattr(w, method, observe)
    w.resize(560, 390)
    w.move(30, 40)
    QApplication.sendEvent(w, QEvent(QEvent.LayoutRequest))
    w.inference_panel.set_classification_mode('tiled_analysis')
    qtbot.wait(30)
    assert w.size() == QSize(560, 390)
    assert calls == []  # The previous resize/LayoutRequest implementation fails here.
    for size in (QSize(520, 360), QSize(480, 340)):
        w.showMaximized()
        qtbot.wait(40)
        assert w.isMaximized() and not w.isFullScreen()
        normal = w.normalGeometry().size()
        w._schedule_screen_fit()  # A work-area signal must not rewrite maximized geometry.
        qtbot.wait(20)
        assert calls == []
        w.showNormal()
        qtbot.wait(40)
        assert w.size() == normal
        w.resize(size)
        qtbot.wait(20)
        assert w.size() == size
        assert not w.windowState() & (Qt.WindowMaximized | Qt.WindowFullScreen)
        assert calls == []
    w.showMinimized()
    qtbot.wait(20)
    assert w.isMinimized()
    w.showNormal()
    qtbot.wait(40)
    assert w.size() == QSize(480, 340)
    w.showFullScreen()
    qtbot.wait(30)
    w._schedule_screen_fit()
    qtbot.wait(20)
    assert w.isFullScreen()
    assert calls == []
    w.showNormal()
    qtbot.wait(40)
    assert w.size() == QSize(480, 340)
    assert w.windowFlags() == flags
    assert w.maximumSize() == QSize(16777215, 16777215)
    assert any('normalGeometry' in record.message and 'state-change' in record.message for record in caplog.records)


def test_screen_change_is_deferred_when_maximized_and_corrects_normal_restore(qtbot, tmp_path, monkeypatch):
    from PyQt5.QtCore import QRect
    w = make_window(qtbot, tmp_path)
    w.showMaximized()
    qtbot.wait(40)
    before = w.geometry()
    monkeypatch.setattr(w, '_available_geometry', lambda: QRect(80, 20, 480, 360))
    w._schedule_screen_fit()
    qtbot.wait(30)
    assert w.isMaximized()
    assert w.geometry() == before
    w.showNormal()
    qtbot.waitUntil(lambda: w._available_geometry().contains(w.frameGeometry()), timeout=1500)
    assert w.maximumSize() == QSize(16777215, 16777215)


def test_saved_maximized_window_keeps_smaller_normal_rectangle(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path)
    w.resize(540, 380)
    qtbot.wait(30)
    w.showMaximized()
    qtbot.wait(40)
    w.close()
    reopened = make_window(qtbot, tmp_path)
    assert reopened.isMaximized()
    reopened.showNormal()
    qtbot.wait(40)
    assert reopened.size() == QSize(540, 380)


def test_explicit_normal_rectangle_recovers_native_maximized_geometry(qtbot, tmp_path):
    from PyQt5.QtCore import QRect
    from PyQt5.QtWidgets import QWidget
    settings = QSettings(str(tmp_path/'window.ini'), QSettings.IniFormat)
    previous = QWidget()
    previous.setGeometry(0, 0, 1900, 1200)
    settings.setValue('window/geometry', previous.saveGeometry())
    settings.setValue('window/maximized', True)
    settings.setValue('window/normalGeometry', QRect(40, 40, 520, 360))
    previous.deleteLater()
    w = make_window(qtbot, tmp_path)
    assert w.isMaximized()
    w.showNormal()
    qtbot.waitUntil(lambda: w.size() == QSize(520, 360), timeout=1500)
    qtbot.wait(150)
    w.close()
    assert settings.value('window/normalGeometry').size() == QSize(520, 360)


def test_panel_scroll_surfaces_and_pinned_action_margins(qtbot, tmp_path, themed_app):
    _, colors = themed_app
    w = make_window(qtbot, tmp_path)
    for panel, button in ((w.inference_panel, w.inference_panel.run_button), (w.action_panel, w.action_panel.rerun_button)):
        assert panel.layout().getContentsMargins() == (16, 16, 16, 16)
        rect = button.rect().translated(button.mapTo(panel, QPoint()))
        assert rect.left() >= 16
        assert rect.right() <= panel.width()-17
        assert rect.bottom() <= panel.height()-17
    dialog = SettingsDialog(w.settings, w)
    qtbot.addWidget(dialog)
    for scroll in [*w.findChildren(QScrollArea), *dialog.findChildren(QScrollArea)]:
        scroll.ensurePolished()
        assert scroll.frameShape() == QScrollArea.NoFrame
        assert scroll.property('panelScroll')
        assert scroll.viewport().property('panelSurface')
        scroll.widget().ensurePolished()
        assert scroll.widget().palette().color(QPalette.Window) == QColor(colors['surface'])
    assert w.splitter.handleWidth() == 6
    assert not w.splitter.childrenCollapsible()


def test_result_tables_clear_selection_current_and_keep_keyboard_scroll(qtbot, tmp_path, themed_app):
    _, colors = themed_app
    result = synthetic_result(tmp_path)
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(740, 400)
    page.show_result(result['color_map'], result['color_map'], result['classification_analysis'])
    page.show()
    for index, table in ((1, page.legend), (2, page.table)):
        page.tabs.setCurrentIndex(index)
        qtbot.wait(30)
        assert table.isEnabled()
        assert table.selectionMode() == table.NoSelection
        assert table.editTriggers() == table.NoEditTriggers
        rect = table.visualItemRect(table.item(0, 0))
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=rect.center())
        assert table.selectedItems() == []
        assert not table.currentIndex().isValid()
        # Cells keep the themed base in focused/unfocused states.
        point = rect.topLeft() + QPoint(3, 3)
        assert table.viewport().grab().toImage().pixelColor(point) == QColor(colors['surface'])
        corner = table.findChild(QAbstractButton)
        assert corner is not None
        assert corner.grab().toImage().pixelColor(4, 4) == QColor(colors['soft'])
        table.setCurrentCell(0, 0)
        table.item(0, 0).setSelected(True)
        assert table.viewport().grab().toImage().pixelColor(point) == QColor(colors['surface'])
        table.clearFocus()
        assert table.viewport().grab().toImage().pixelColor(point) == QColor(colors['surface'])
        page.tabs.setCurrentIndex(0)
        page.tabs.setCurrentIndex(index)
        assert table.selectedItems() == []
        assert not table.currentIndex().isValid()
    qtbot.keyClick(page.table, Qt.Key_PageDown)
    assert page.table.verticalScrollBar().value() > 0
    qtbot.keyClick(page.table, Qt.Key_Home)
    assert page.table.verticalScrollBar().value() == 0
    page.tabs.setCurrentIndex(1)
    qtbot.wait(20)
    swatch = page.legend.visualItemRect(page.legend.item(0, 3)).topLeft() + QPoint(3, 3)
    assert page.legend.viewport().grab().toImage().pixelColor(swatch) == QColor(*result['classification_analysis']['classes'][0]['color'])
    page.table.setCurrentCell(5, 1)
    page.show_result(result['color_map'], result['color_map'], result['classification_analysis'])
    assert not page.table.currentIndex().isValid()
    page.clear()
    assert not page.legend.currentIndex().isValid()


def test_history_load_clears_legacy_result_table_state(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path)
    w._show_inference_result(synthetic_result(tmp_path))
    page = w.result_panel.tile_page
    page.legend.setCurrentCell(0, 0)
    page.table.setCurrentCell(2, 1)
    record = w.database_manager.get_all_records()[0]
    w._show_record_activated(record['id'])
    assert not page.legend.currentIndex().isValid()
    assert not page.table.currentIndex().isValid()
    assert page.table.rowCount() == 49
    assert page.analysis['tile_counts'] == [0, 0, 0, 0, 1, 0, 1, 47, 0]


@pytest.mark.parametrize('orientation', [Qt.Horizontal, Qt.Vertical])
def test_scrollbar_pages_have_solid_theme_and_handle_stays_interactive(qtbot, themed_app, orientation):
    _, colors = themed_app
    bar = QScrollBar(orientation)
    qtbot.addWidget(bar)
    bar.resize(240, 12) if orientation == Qt.Horizontal else bar.resize(12, 240)
    bar.setRange(0, 100)
    bar.setPageStep(20)
    bar.setValue(40)
    bar.show()
    qtbot.wait(20)
    option = QStyleOptionSlider()
    bar.initStyleOption(option)
    for control in (QStyle.SC_ScrollBarAddPage, QStyle.SC_ScrollBarSubPage):
        rect = bar.style().subControlRect(QStyle.CC_ScrollBar, option, control, bar).adjusted(3, 3, -3, -3)
        assert not rect.isEmpty()
        image = bar.grab().toImage()
        actual = {image.pixelColor(x,y).name() for x in range(rect.left(),rect.right()+1) for y in range(rect.top(),rect.bottom()+1)}
        assert actual == {colors['soft'].lower()}
    handle = bar.style().subControlRect(QStyle.CC_ScrollBar, option, QStyle.SC_ScrollBarSlider, bar)
    qtbot.mouseMove(bar, handle.center())
    qtbot.wait(10)
    assert bar.grab().toImage().pixelColor(handle.center()) == QColor(ACCENT)
    qtbot.mousePress(bar, Qt.LeftButton, pos=handle.center())
    assert bar.grab().toImage().pixelColor(handle.center()) == QColor(PRIMARY)
    target = handle.center() + (QPoint(20,0) if orientation == Qt.Horizontal else QPoint(0,20))
    QApplication.sendEvent(bar, QMouseEvent(QEvent.MouseMove, target, Qt.NoButton, Qt.LeftButton, Qt.NoModifier))
    qtbot.mouseRelease(bar, Qt.LeftButton, pos=target)
    assert bar.value() != 40
    bar.setDisabled(True)
    qtbot.wait(10)
    bar.initStyleOption(option)
    handle = bar.style().subControlRect(QStyle.CC_ScrollBar, option, QStyle.SC_ScrollBarSlider, bar)
    assert bar.grab().toImage().pixelColor(handle.center()) == QColor(colors['border'])
