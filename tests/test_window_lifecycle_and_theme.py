"""Window-manager ownership and rendered theme regressions, without real weights."""
import logging
from math import ceil

import pytest
from pytestqt.exceptions import TimeoutError as QtWaitTimeoutError
from PyQt5.QtCore import QByteArray, QEvent, QPoint, QPointF, QRect, QSettings, QSize, Qt
from PyQt5.QtGui import QColor, QCursor, QHoverEvent, QPalette, QMouseEvent
from PyQt5.QtWidgets import QApplication, QAbstractButton, QScrollArea, QScrollBar, QStyle, QStyleOptionSlider, QWidget

from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.theme import ACCENT, PRIMARY, DARK_COLORS, LIGHT_COLORS, apply_theme
from test_screen_fit_and_tile_grid import synthetic_result


def widget_color(widget, point):
    """Sample a logical widget position in its physical-pixel screenshot."""
    assert widget.rect().contains(point)
    image = widget.grab().toImage()
    ratio = image.devicePixelRatio()
    return image.pixelColor(round(point.x() * ratio), round(point.y() * ratio))


def image_region_colors(image, rect):
    """Inspect every device pixel inside a logical style-control rectangle."""
    ratio = image.devicePixelRatio()
    left, top = ceil(rect.left() * ratio), ceil(rect.top() * ratio)
    right, bottom = ceil((rect.right() + 1) * ratio), ceil((rect.bottom() + 1) * ratio)
    assert 0 <= left < right <= image.width()
    assert 0 <= top < bottom <= image.height()
    return {image.pixelColor(x, y).name() for x in range(left, right) for y in range(top, bottom)}


def scrollbar_state(bar, point):
    """Report actual native input/rendering state if a hover never arrives."""
    option = QStyleOptionSlider()
    bar.initStyleOption(option)
    image = bar.grab().toImage()
    cursor = bar.mapFromGlobal(QCursor.pos())
    return {
        'platform': QApplication.platformName(),
        'visible': bar.isVisible(),
        'active_window': bar.window().isActiveWindow(),
        'under_mouse': bar.underMouse(),
        'cursor_local': (cursor.x(), cursor.y()),
        'sample_logical': (point.x(), point.y()),
        'logical_size': (bar.width(), bar.height()),
        'image_size': (image.width(), image.height()),
        'image_dpr': image.devicePixelRatio(),
        'style_state': int(option.state),
        'active_subcontrols': int(option.activeSubControls),
        'actual_color': widget_color(bar, point).name(),
        'expected_hover': QColor(ACCENT).name(),
    }


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


@pytest.mark.parametrize('available, expected_size', [
    (QRect(0, 0, 1360, 900), QSize(1088, 720)),
    (QRect(-1000, 40, 1000, 700), QSize(800, 560)),
    (QRect(120, 20, 640, 480), QSize(512, 384)),
])
@pytest.mark.parametrize('invalid_saved_geometry', [False, True])
def test_first_launch_uses_centered_eighty_percent_of_logical_work_area(
    qtbot, tmp_path, monkeypatch, available, expected_size, invalid_saved_geometry,
):
    monkeypatch.setattr(MainWindow, '_available_geometry', lambda self: QRect(available))
    settings = QSettings(str(tmp_path/'window.ini'), QSettings.IniFormat)
    if invalid_saved_geometry:
        settings.setValue('window/geometry', QByteArray(b'not a Qt geometry'))
    w = MainWindow(settings=settings, db_path=tmp_path/'history.db', builtin_model_path=tmp_path/'missing.pth')
    qtbot.addWidget(w)
    assert w.size() == expected_size
    assert w.geometry().center() == available.center()
    w.show()
    qtbot.wait(150)  # Include the deferred decoration/screen correction.
    assert w.size() == expected_size
    frame = w.frameGeometry()
    assert available.contains(frame)
    # Native decorations can shift the initial client position (offscreen adds
    # 2px on negative-coordinate screens); centering may differ only by that frame.
    assert abs((frame.left() - available.left()) - (available.right() - frame.right())) <= frame.width() - w.width()
    assert abs((frame.top() - available.top()) - (available.bottom() - frame.bottom())) <= frame.height() - w.height()
    for mode in ('tiled_analysis', 'single_image'):
        w.inference_panel.set_classification_mode(mode)
        qtbot.wait(20)
        assert w.size() == expected_size
        assert available.contains(w.frameGeometry())


def test_reopening_keeps_user_size_and_position_instead_of_default(qtbot, tmp_path, monkeypatch):
    available = QRect(0, 0, 800, 600)
    monkeypatch.setattr(MainWindow, '_available_geometry', lambda self: QRect(available))
    settings = QSettings(str(tmp_path/'window.ini'), QSettings.IniFormat)
    options = dict(settings=settings, db_path=tmp_path/'history.db', builtin_model_path=tmp_path/'missing.pth')
    w = MainWindow(**options)
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(150)
    w.resize(520, 350)
    w.move(50, 60)
    qtbot.wait(150)
    normal = QRect(w.geometry())
    w.close()
    reopened = MainWindow(**options)
    qtbot.addWidget(reopened)
    reopened.show()
    qtbot.wait(150)
    assert reopened.geometry() == normal
    assert reopened.size() == QSize(520, 350)


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
    try:
        qtbot.waitUntil(lambda: w.size() == QSize(520, 360), timeout=1500)
    except QtWaitTimeoutError as error:
        raise AssertionError({
            'expected_size': (520, 360), 'platform': QApplication.platformName(),
            'geometry': w.geometry().getRect(), 'frame': w.frameGeometry().getRect(),
            'normal_geometry': w.normalGeometry().getRect(),
            'remembered_normal': w._normal_geometry.getRect(),
            'available': w._available_geometry().getRect(),
            'state': int(w.windowState()), 'minimum': (w.minimumWidth(), w.minimumHeight()),
            'dpr': w.devicePixelRatioF(),
        }) from error
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
    w._show_inference_result(synthetic_result(tmp_path))
    page = w.result_panel.tile_page
    page.tile_details_button.setChecked(True)
    qtbot.mouseMove(w, QPoint(0, 0))
    qtbot.wait(20)
    handle = page.content_splitter.handle(1)
    assert widget_color(handle, QPoint(3, 2)) == QColor(colors['border'])


def test_result_tables_clear_selection_current_and_keep_keyboard_scroll(qtbot, tmp_path, themed_app):
    _, colors = themed_app
    result = synthetic_result(tmp_path)
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(740, 400)
    page.show_result(result['color_map'], result['color_map'], result['classification_analysis'])
    page.show()
    page.tile_details_button.setChecked(True)
    for index, table in ((1, page.legend), (0, page.table)):
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
        assert widget_color(table.viewport(), point) == QColor(colors['surface'])
        corner = table.findChild(QAbstractButton)
        assert corner is not None
        assert widget_color(corner, QPoint(4, 4)) == QColor(colors['soft'])
        table.setCurrentCell(0, 0)
        table.item(0, 0).setSelected(True)
        assert widget_color(table.viewport(), point) == QColor(colors['surface'])
        table.clearFocus()
        assert widget_color(table.viewport(), point) == QColor(colors['surface'])
        page.tabs.setCurrentIndex(1 - index)
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
    assert widget_color(page.legend.viewport(), swatch) == QColor(*result['classification_analysis']['classes'][0]['color'])
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
    # A scrollbar is a child control in the application. A standalone native
    # Windows scrollbar becomes a top-level window with frame/minimum-size rules.
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(300, 280)
    bar = QScrollBar(orientation, host)
    bar.resize(240, 12) if orientation == Qt.Horizontal else bar.resize(12, 240)
    bar.move(20, 20)
    bar.setRange(0, 100)
    bar.setPageStep(20)
    bar.setValue(40)
    host.show()
    qtbot.waitExposed(host)
    host.activateWindow()
    qtbot.waitUntil(host.isActiveWindow, timeout=1500)
    assert bar.size() == (QSize(240, 12) if orientation == Qt.Horizontal else QSize(12, 240))
    option = QStyleOptionSlider()
    bar.initStyleOption(option)
    for control in (QStyle.SC_ScrollBarAddPage, QStyle.SC_ScrollBarSubPage):
        rect = bar.style().subControlRect(QStyle.CC_ScrollBar, option, control, bar).adjusted(3, 3, -3, -3)
        assert not rect.isEmpty()
        image = bar.grab().toImage()
        actual = image_region_colors(image, rect)
        assert actual == {colors['soft'].lower()}
    handle = bar.style().subControlRect(QStyle.CC_ScrollBar, option, QStyle.SC_ScrollBarSlider, bar)
    qtbot.mouseMove(host, QPoint(4, 4))
    qtbot.mouseMove(bar, handle.center())
    # QTest cursor motion on Windows can leave the pointer at the right position
    # without delivering Enter/Hover to QWidget. Reproduce that state, then send
    # the actual input sequence; never set UnderMouse or stylesheet state by hand.
    position = QPointF(handle.center())
    outside = QPointF(-1, -1)
    QApplication.sendEvent(bar, QEvent(QEvent.Leave))
    QApplication.sendEvent(bar, QHoverEvent(QEvent.HoverLeave, outside, position))
    assert not bar.underMouse()
    QApplication.sendEvent(bar, QEvent(QEvent.Enter))
    QApplication.sendEvent(bar, QHoverEvent(QEvent.HoverEnter, position, outside))
    QApplication.sendEvent(bar, QMouseEvent(
        QEvent.MouseMove, position, QPointF(bar.mapToGlobal(handle.center())),
        Qt.NoButton, Qt.NoButton, Qt.NoModifier,
    ))
    QApplication.sendEvent(bar, QHoverEvent(QEvent.HoverMove, position, outside))
    assert bar.underMouse()
    try:
        qtbot.waitUntil(lambda: widget_color(bar, handle.center()) == QColor(ACCENT), timeout=1500)
    except QtWaitTimeoutError as error:
        raise AssertionError(scrollbar_state(bar, handle.center())) from error
    assert widget_color(bar, handle.center()) == QColor(ACCENT), scrollbar_state(bar, handle.center())
    qtbot.mousePress(bar, Qt.LeftButton, pos=handle.center())
    assert widget_color(bar, handle.center()) == QColor(PRIMARY)
    target = handle.center() + (QPoint(20,0) if orientation == Qt.Horizontal else QPoint(0,20))
    QApplication.sendEvent(bar, QMouseEvent(QEvent.MouseMove, target, Qt.NoButton, Qt.LeftButton, Qt.NoModifier))
    qtbot.mouseRelease(bar, Qt.LeftButton, pos=target)
    assert bar.value() != 40
    bar.setDisabled(True)
    qtbot.wait(10)
    bar.initStyleOption(option)
    handle = bar.style().subControlRect(QStyle.CC_ScrollBar, option, QStyle.SC_ScrollBarSlider, bar)
    assert widget_color(bar, handle.center()) == QColor(colors['border'])
