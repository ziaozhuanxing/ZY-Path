"""Real Qt comparison navigation with synthetic, unchanged prediction data."""
import copy
import json

import pytest
from PIL import Image
from PyQt5.QtCore import QEvent, QPoint, QPointF, QRect, QSettings, Qt
from PyQt5.QtGui import QFont, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QApplication

from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.segmentation_result import SegmentationResult
from ui.theme import apply_theme
from test_screen_fit_and_tile_grid import synthetic_result, assert_visible_grid_lines
from test_segmentation_results_layout import segmentation_fixture


def make_page(qtbot, tmp_path, kind, size):
    if kind == 'classification':
        result = synthetic_result(tmp_path)
        page = ClassificationResult()
        with Image.open(result['image_path']) as original:
            page.show_result(original, result['color_map'], result['classification_analysis'])
    else:
        result = segmentation_fixture(tmp_path)
        page = SegmentationResult()
        analysis, colors, legend = MainWindow._segmentation_display_data(result)
        with Image.open(result['image_path']) as original:
            page.show_result(result['blended'], legend, original, colors, result['counts'], analysis)
    qtbot.addWidget(page)
    page.resize(*size)
    page.show()
    page.compare.setChecked(True)
    qtbot.wait(50)
    return page, result


def assert_linked(page):
    left, right = page.original_view, page.image
    assert left.zoom_percent() == pytest.approx(right.zoom_percent())
    # Compare the screen offsets of the SAME source point from each viewport's
    # center. This also works when the panes have different dimensions.
    point = QPointF(left.pixmap().width() * .45, left.pixmap().height() * .55)
    offsets = []
    for view in (left, right):
        offset = view.graphics_view.mapFromScene(point) - view.graphics_view.viewport().rect().center()
        offsets.append(offset)
    assert abs(offsets[0].x() - offsets[1].x()) <= 2
    assert abs(offsets[0].y() - offsets[1].y()) <= 2


@pytest.mark.parametrize('kind', ['classification', 'segmentation'])
@pytest.mark.parametrize('size', [(1000, 700), (600, 650), (360, 500)])
def test_equal_initial_split_common_fit_and_preserved_manual_ratio(qtbot, tmp_path, kind, size):
    page, _ = make_page(qtbot, tmp_path, kind, size)
    comparison = page.comparison
    splitter = comparison.splitter
    assert page.link_views.isChecked()
    assert page.view_mode.isVisible() and page.view_mode.width() >= 80
    assert comparison.primary.rect().contains(page.view_mode.geometry())
    sizes = splitter.sizes()
    assert abs(sizes[0] - sizes[1]) <= 1
    assert splitter.orientation() == (Qt.Horizontal if size[0] >= 700 else Qt.Vertical)
    assert_linked(page)
    # An explicit Fit must take priority even when resize happens before the
    # next Qt event-loop turn (the peer may previously have been zoomed).
    page.image.zoom_in()
    page.image.fit_to_view()
    page.resize(size[0] + 10, size[1] + 10)
    qtbot.wait(20)
    assert page.image.view_state()['fit'] and page.original_view.view_state()['fit']
    assert_linked(page)
    for view in (page.image, page.original_view):
        assert view.view_state()['fit']
        assert view.graphics_view.viewport().height() >= 20
        assert view.displayed_size().width() <= view.graphics_view.viewport().width()
        assert view.displayed_size().height() <= view.graphics_view.viewport().height()
    assert page.image.zoom_percent() == pytest.approx(min(page.image.fit_zoom_percent(), page.original_view.fit_zoom_percent()))
    span = splitter.width() if splitter.orientation() == Qt.Horizontal else splitter.height()
    splitter.moveSplitter(round(span * .63), 1)
    qtbot.wait(30)
    ratio = page.comparison.presentation()['split_ratio']
    assert ratio == pytest.approx(.63, abs=.03)
    page.resize(size[0] + 40, size[1] + 30)
    qtbot.wait(30)
    assert_linked(page)
    actual = splitter.sizes()
    assert actual[0] / sum(actual) == pytest.approx(ratio, abs=.02)
    page.compare.setChecked(False)
    qtbot.wait(10)
    page.compare.setChecked(True)
    qtbot.wait(30)
    actual = splitter.sizes()
    assert actual[0] / sum(actual) == pytest.approx(ratio, abs=.02)
    assert_linked(page)


@pytest.mark.parametrize('kind', ['classification', 'segmentation'])
def test_bidirectional_buttons_wheel_drag_edges_and_unlinked_navigation(qtbot, tmp_path, kind):
    page, _ = make_page(qtbot, tmp_path, kind, (1000, 800))
    for driver in (page.original_view, page.image):
        qtbot.mouseClick(driver.zoom_in_button, Qt.LeftButton)
        qtbot.wait(20)
        assert_linked(page)
        qtbot.mouseClick(driver.actual_size_button, Qt.LeftButton)
        qtbot.wait(20)
        assert page.image.zoom_percent() == pytest.approx(100)
        assert_linked(page)
        driver.graphics_view.centerOn(QPointF(10, 15))
        qtbot.wait(20)
        assert_linked(page)
        center = driver.view_state()['center']
        scale = driver.graphics_view.transform().m11()
        assert abs(center.x() - 10) <= 2 / scale
        assert abs(center.y() - 15) <= 2 / scale
        viewport = driver.graphics_view.viewport()
        pos = viewport.rect().center()
        wheel = QWheelEvent(QPointF(pos), QPointF(viewport.mapToGlobal(pos)), QPoint(), QPoint(0, 120),
                            Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False)
        QApplication.sendEvent(viewport, wheel)
        qtbot.wait(20)
        assert driver.zoom_percent() == pytest.approx(125)
        assert_linked(page)
        before = driver.view_state()['center']
        end = pos + QPoint(25, 15)
        for event_type, point, button, buttons in (
            (QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton),
            (QEvent.MouseMove, end, Qt.NoButton, Qt.LeftButton),
            (QEvent.MouseButtonRelease, end, Qt.LeftButton, Qt.NoButton),
        ):
            QApplication.sendEvent(viewport, QMouseEvent(event_type, QPointF(point), QPointF(viewport.mapToGlobal(point)), button, buttons, Qt.NoModifier))
        qtbot.wait(20)
        assert driver.view_state()['center'] != before
        assert_linked(page)
        page.resize(950, 760)
        qtbot.wait(30)
        assert_linked(page)
        qtbot.mouseClick(driver.fit_button, Qt.LeftButton)
        qtbot.wait(20)
        assert page.image.view_state()['fit'] and page.original_view.view_state()['fit']
        assert_linked(page)
    page.link_views.setChecked(False)
    peer_zoom = page.image.zoom_percent()
    page.original_view.zoom_in()
    qtbot.wait(20)
    assert page.image.zoom_percent() == pytest.approx(peer_zoom)
    assert page.original_view.zoom_percent() != pytest.approx(peer_zoom)
    page.link_views.setChecked(True)
    qtbot.wait(20)
    assert_linked(page)


def test_classification_grid_hover_modes_and_history_export_keep_predictions(qtbot, tmp_path, monkeypatch):
    result = synthetic_result(tmp_path)
    baseline = copy.deepcopy(result['classification_analysis'])
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    settings.setValue('export/pngReminderEnabled', False)
    settings.setValue('export/pdfReminderEnabled', False)
    monkeypatch.setattr(MainWindow, '_available_geometry', lambda self: QRect(0, 0, 1800, 1100))
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.resize(1700, 1000)
    window.show()
    window.splitter.setSizes([230, 1200, 230])
    window._show_inference_result(result)
    page = window.result_panel.tile_page
    page.compare.setChecked(True)
    page.boundaries.setChecked(True)
    qtbot.wait(50)
    for mode in range(3):
        page.view_mode.setCurrentIndex(mode)
        page.image.fit_to_view()
        qtbot.wait(20)
        assert_linked(page)
        for view in (page.image, page.original_view):
            assert len(view._grid_lines) == 16
            assert_visible_grid_lines(view, require_all=True)
        point = page.image.graphics_view.mapFromScene(QPointF(3312, 3304))
        assert 'Tile 49: MUC' in page.tile_tooltip_at(point)
        assert '480 x 464 px' in page.tile_tooltip_at(point)
        original_point = page.original_view.graphics_view.mapFromScene(QPointF(3312, 3304))
        assert 'Tile 49: MUC' in page.tile_tooltip_at(original_point, page.original_view)
        page.image.zoom_in()
        qtbot.wait(10)
        assert_linked(page)
        page.image.zoom_out()
    page.boundaries.setChecked(False)
    assert page.image._grid_lines == [] and page.original_view._grid_lines == []
    assert result['classification_analysis'] == baseline
    page.link_views.setChecked(False)
    splitter = page.comparison_splitter
    splitter.moveSplitter(round(splitter.width() * .6), 1)
    qtbot.wait(20)
    chosen = page.presentation()
    record_id = window.current_record_id
    stored = window.database_manager.get_record_by_id(record_id)
    assert json.loads(stored['analysis_json'])['presentation'] == chosen
    window._show_record_activated(record_id)
    qtbot.wait(40)
    assert page.presentation() == chosen
    assert {k: v for k, v in page.analysis.items() if k != 'presentation'} == baseline
    target = tmp_path / 'comparison-view.png'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(target), ''))
    expected = page.render_image().tobytes()
    window._export_current_png()
    with Image.open(target) as image:
        assert image.tobytes() == expected
        assert image.size == (3552, 3536)
    metadata = json.loads(target.with_suffix('.png.json').read_text())
    assert metadata['classification_analysis']['presentation'] == chosen
    assert metadata['classification_mode'] == 'tiled_analysis'
    assert metadata['model_path'] == result['model_path']


def test_short_large_font_comparison_and_tables_scroll_without_growing_page(qtbot, qapp, tmp_path):
    old_font, old_style, old_theme = QFont(qapp.font()), qapp.styleSheet(), qapp.property('zyTheme')
    apply_theme(qapp, 'Dark')
    font = QFont(old_font)
    font.setPointSize(15)
    qapp.setFont(font)
    try:
        page, _ = make_page(qtbot, tmp_path, 'classification', (360, 420))
        page.tile_details_button.setChecked(True)
        qtbot.wait(40)
        assert (page.width(), page.height()) == (360, 420)
        scroll = page.comparison.image_scroll
        assert scroll.verticalScrollBar().maximum() > 0
        for view in (page.original_view, page.image):
            assert view.graphics_view.viewport().height() >= 20
            scroll.ensureWidgetVisible(view.zoom_in_button, 0, 0)
            qtbot.wait(5)
            button = view.zoom_in_button
            rect = QRect(button.mapTo(scroll.viewport(), button.rect().topLeft()), button.size())
            assert scroll.viewport().rect().contains(rect)
        assert page.legend_scroll.isVisible() and page.table.isVisible()
        assert page.table.viewport().height() >= 20
    finally:
        qapp.setStyleSheet(old_style)
        qapp.setProperty('zyTheme', old_theme)
        qapp.setFont(old_font)
