"""Small logical screens and vector grid/true-pixel zoom regressions."""
import copy
import json

from PIL import Image
import pytest
from PyQt5.QtCore import QPointF, QRect, Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget

from core.classification_tiles import CLASSIFICATION_LABELS, CLASSIFICATION_COLORS
from ui.main_window import MainWindow
from ui.window_geometry import bounded_frame
from ui.zoomable_image_view import ZoomableImageView


def tile_analysis():
    width, height = 3552, 3536
    tiles, counts, pixels = [], [0] * 9, [0] * 9
    for y in range(0, height, 512):
        for x in range(0, width, 512):
            index = 6 if len(tiles) == 24 else 4 if len(tiles) == 48 else 7
            box = [x, y, min(x + 512, width), min(y + 512, height)]
            counts[index] += 1
            pixels[index] += (box[2] - x) * (box[3] - y)
            probabilities = [.025] * 9
            probabilities[index] = .8
            tiles.append({'box': box, 'class_index': index, 'label': CLASSIFICATION_LABELS[index],
                          'confidence': .8, 'probabilities': probabilities})
    return {'mode': 'classification_tiles', 'classification_mode': 'tiled_analysis',
            'classes': [{'label': n, 'color': list(CLASSIFICATION_COLORS[i])} for i, n in enumerate(CLASSIFICATION_LABELS)],
            'image_size': [width, height], 'tile_size': [512, 512], 'input_size': [224, 224],
            'preprocess': 'raw255', 'resize_backend': 'pillow_bilinear', 'tiles': tiles,
            'tile_counts': counts, 'pixel_counts': pixels,
            'area_ratios': [p / (width * height) for p in pixels]}


def synthetic_result(tmp_path):
    analysis = tile_analysis()
    original = Image.new('RGB', tuple(analysis['image_size']), (55, 65, 75))
    color = Image.new('RGB', original.size)
    for tile in analysis['tiles']:
        color.paste(CLASSIFICATION_COLORS[tile['class_index']], tile['box'])
    filename = tmp_path / 'source.png'
    original.save(filename)
    return {'task_type': 'classification', 'classification_mode': 'tiled_analysis',
            'analysis_mode': 'classification_tiles', 'classification_analysis': analysis,
            'color_map': color, 'image_path': str(filename), 'model_path': str(tmp_path / 'not-written.pth'),
            'model_name': 'Synthetic layout data', 'timestamp': '2026-10-16T08:00:00+00:00',
            'label': 'STR', 'confidence': .8, 'elapsed_seconds': 0}


@pytest.mark.parametrize('available', [QRect(0, 0, 640, 480), QRect(120, 40, 800, 540), QRect(0, 0, 480, 360)])
def test_modes_results_and_saved_geometry_fit_small_available_area(qtbot, tmp_path, monkeypatch, available):
    from PyQt5.QtCore import QSettings
    monkeypatch.setattr(MainWindow, '_available_geometry', lambda self: QRect(available))
    settings = QSettings(str(tmp_path / 'window.ini'), QSettings.IniFormat)
    previous = QWidget()
    previous.setGeometry(5000, -3000, 1900, 1300)
    settings.setValue('window/geometry', previous.saveGeometry())
    previous.deleteLater()
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        builtin_model_path=tmp_path / 'missing.pth', results_dir=tmp_path / 'results')
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(30)
    assert available.contains(window.frameGeometry())
    initial = window.frameGeometry()
    for mode in ('tiled_analysis', 'single_image', 'tiled_analysis'):
        window.inference_panel.set_classification_mode(mode)
        qtbot.wait(20)
        assert available.contains(window.frameGeometry())
        assert window.frameGeometry().size() == initial.size()
        button = window.inference_panel.run_button
        button_rect = QRect(button.mapTo(window, button.rect().topLeft()), button.size())
        assert window.rect().contains(button_rect)
        assert window.inference_panel.controls_scroll.viewport().height() > 0
        assert window.tabs.width() >= 320
        if available.width() < 732:
            scrollbar = window.body_scroll.horizontalScrollBar()
            assert scrollbar.maximum() > 0
            scrollbar.setValue(scrollbar.maximum())
            qtbot.wait(10)
            rerun = window.action_panel.rerun_button
            assert window.rect().contains(QRect(rerun.mapTo(window, rerun.rect().topLeft()), rerun.size()))
            scrollbar.setValue(0)
    result = synthetic_result(tmp_path)
    window._show_inference_result(result)
    qtbot.wait(30)
    assert available.contains(window.frameGeometry())
    assert window.frameGeometry().size() == initial.size()
    page = window.result_panel.tile_page
    page.details_button.setChecked(True)
    qtbot.wait(20)
    assert available.contains(window.frameGeometry())
    record = window.database_manager.get_all_records()[0]
    window._show_record_activated(record['id'])
    qtbot.wait(20)
    assert available.contains(window.frameGeometry())
    window.tabs.setCurrentWidget(window.history_panel)
    qtbot.wait(20)
    assert window.history_panel.table.viewport().height() > 0
    assert available.contains(window.frameGeometry())
    window.close()
    assert settings.value('window/geometry')
    reopened = MainWindow(settings=settings, db_path=tmp_path / 'history.db', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(reopened)
    reopened.show()
    qtbot.wait(30)
    assert available.contains(reopened.frameGeometry())


def test_maximize_normal_restore_respects_real_screen(qtbot, tmp_path):
    from PyQt5.QtCore import QSettings
    settings = QSettings(str(tmp_path / 'window.ini'), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.show()
    qtbot.wait(30)
    available = window._available_geometry()
    for mode in ('single_image', 'tiled_analysis'):
        window.inference_panel.set_classification_mode(mode)
        window.showMaximized()
        qtbot.wait(30)
        assert window.isMaximized()
        assert not window.isFullScreen()
        if QApplication.platformName() == 'windows':
            # Windows maximization extends invisible resize borders beyond the
            # work area. Validate the client area and Qt's actual native margins,
            # rather than imposing the offscreen plugin's synthetic 2px frame.
            assert available.contains(window.geometry())
            assert window.frameGeometry() == window.geometry().marginsAdded(window.windowHandle().frameMargins())
        else:
            assert available.adjusted(-2, -2, 2, 2).contains(window.frameGeometry())
        window.showNormal()
        qtbot.wait(30)
        assert not window.isMaximized()
        assert available.contains(window.frameGeometry())
    window.showMaximized()
    qtbot.wait(20)
    window.close()
    assert settings.value('window/maximized', type=bool)
    restored = MainWindow(settings=settings, db_path=tmp_path / 'history.db', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(restored)
    restored.show()
    qtbot.wait(30)
    assert restored.isMaximized()
    restored.showNormal()
    qtbot.wait(30)
    assert restored._available_geometry().contains(restored.frameGeometry())


def test_logical_screen_coordinates_do_not_assume_primary_origin_or_dpr():
    for bounds in (QRect(0, 0, 640, 360), QRect(-1280, 80, 1280, 720), QRect(1920, 0, 960, 540)):
        result = bounded_frame(QRect(5000, -1000, 2000, 1800), bounds)
        assert bounds.contains(result)
        assert result.size() == bounds.size()
        small = bounded_frame(QRect(bounds.x() + 20, bounds.y() + 20, 320, 240), bounds)
        assert small == QRect(bounds.x() + 20, bounds.y() + 20, 320, 240)


def assert_visible_grid_lines(view, require_all=False):
    transform = view.graphics_view.viewportTransform()
    viewport = view.graphics_view.viewport()
    grab = viewport.grab().toImage()
    dpr = grab.devicePixelRatio()
    checked = 0
    for k in range(1, 7):
        for scene_point in (QPointF(k * 512, 3536 / 2), QPointF(3552 / 2, k * 512)):
            p = transform.map(scene_point)
            if not viewport.rect().adjusted(3, 3, -3, -3).contains(p.toPoint()):
                continue
            x, y = round(p.x() * dpr), round(p.y() * dpr)
            bright = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    color = grab.pixelColor(x + dx, y + dy)
                    bright.append(min(color.red(), color.green(), color.blue()))
            assert max(bright) > 210, (scene_point, p)
            checked += 1
    if require_all:
        assert checked == 12
    else:
        assert checked > 0


def test_grid_survives_fit_zoom_resize_and_uses_actual_pixel_percentage(qtbot):
    view = ZoomableImageView()
    qtbot.addWidget(view)
    view.resize(620, 620)
    view.show()
    pixmap = QPixmap(3552, 3536)
    pixmap.fill(QColor(55, 65, 75))
    view.set_source_pixmap(pixmap)
    boxes = [tile['box'] for tile in tile_analysis()['tiles']]
    view.set_tile_grid(boxes)
    qtbot.wait(40)
    assert len(view._grid_lines) == 16
    xs = sorted({line.x1() for line in view._grid_lines if line.x1() == line.x2()})
    ys = sorted({line.y1() for line in view._grid_lines if line.y1() == line.y2()})
    assert xs == [0, 512, 1024, 1536, 2048, 2560, 3072, 3552]
    assert ys == [0, 512, 1024, 1536, 2048, 2560, 3072, 3536]
    assert xs[-1] - xs[-2] == 480
    assert ys[-1] - ys[-2] == 464
    assert view.zoom_indicator.text().startswith('Fit (')
    fit = view.zoom_percent()
    assert fit < 100
    assert view.displayed_size().width() <= view.graphics_view.viewport().width()
    assert_visible_grid_lines(view, require_all=True)
    view.zoom_in()
    assert view.zoom_percent() == pytest.approx(fit * 1.25)
    assert_visible_grid_lines(view)
    view.zoom_out()
    view.zoom_out()
    assert view.zoom_percent() == pytest.approx(fit * .8)
    assert_visible_grid_lines(view, require_all=True)
    view.actual_size()
    assert view.zoom_indicator.text() == '100%'
    assert view.graphics_view.transform().m11() * view.graphics_view.viewport().devicePixelRatioF() == pytest.approx(1)
    view.resize(480, 400)
    qtbot.wait(30)
    assert view.zoom_percent() == pytest.approx(100)
    view.fit_to_view()
    assert_visible_grid_lines(view, require_all=True)
    for _ in range(10):
        view.zoom_in()
        view.zoom_out()
    assert len(view._grid_lines) == 16
    view.fit_to_view()
    assert_visible_grid_lines(view, require_all=True)
    view.set_tile_grid([])
    assert view._grid_lines == []
    assert view.pixmap().toImage().pixelColor(512, 256) == QColor(55, 65, 75)


def test_overlay_color_history_grid_are_aligned_without_changing_predictions(qtbot, tmp_path):
    from PyQt5.QtCore import QSettings
    window = MainWindow(settings=QSettings(str(tmp_path / 'window.ini'), QSettings.IniFormat),
        db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.show()
    result = synthetic_result(tmp_path)
    before = copy.deepcopy(result['classification_analysis'])
    window._show_inference_result(result)
    qtbot.wait(30)
    page = window.result_panel.tile_page
    for mode in (0, 1, 0):
        page.view_mode.setCurrentIndex(mode)
        page.boundaries.setChecked(True)
        page.image.fit_to_view()
        qtbot.wait(15)
        assert len(page.image._grid_lines) == 16
        assert page.image._pixmap_item.sceneBoundingRect().size().toSize().width() == 3552
        page.image.zoom_in()
        page.image.zoom_out()
        page.boundaries.setChecked(False)
        assert page.image._grid_lines == []
        assert result['classification_analysis'] == before
        assert {k: v for k, v in page.analysis.items() if k != 'presentation'} == before
    record = window.database_manager.get_all_records()[0]
    analysis = json.loads(record['analysis_json'])
    analysis['presentation']['boundaries'] = True
    # Restore a recorded grid choice, as a previously saved display presentation.
    with window.database_manager._connection() as connection:
        connection.execute('UPDATE segmentation_artifacts SET analysis_json=? WHERE record_id=?', (json.dumps(analysis), record['id']))
    window._show_record_activated(record['id'])
    qtbot.wait(30)
    assert page.boundaries.isChecked()
    assert len(page.image._grid_lines) == 16
    assert page.analysis['tile_counts'] == before['tile_counts']
    assert page.analysis['tiles'] == before['tiles']


@pytest.mark.parametrize('scrollbar_extent', [16, 30])
def test_short_body_keeps_both_panel_actions_inside_its_viewport(qtbot, qapp, tmp_path, scrollbar_extent):
    """Native scrollbar hints must not stretch every panel past a short body."""
    from PyQt5.QtCore import QSettings
    old_style = qapp.styleSheet()
    qapp.setStyleSheet(old_style + f' QScrollBar:horizontal {{height: {scrollbar_extent}px;}}'
                      + f' QScrollBar:vertical {{width: {scrollbar_extent}px;}}')
    try:
        window = MainWindow(settings=QSettings(str(tmp_path / 'short.ini'), QSettings.IniFormat),
                            db_path=tmp_path / 'short.db', builtin_model_path=tmp_path / 'missing.pth')
        qtbot.addWidget(window)
        window.resize(478, 307)
        # Reproduce the actual native failure's body height independently of
        # platform title-bar/font metrics. With 30px bars the viewport is 120px.
        window.body_scroll.setFixedHeight(150)
        window.show()
        qtbot.waitExposed(window)
        qtbot.wait(40)
        viewport = window.body_scroll.viewport()
        assert viewport.height() == 150 - scrollbar_extent
        for mode in ('tiled_analysis', 'single_image'):
            window.inference_panel.set_classification_mode(mode)
            qtbot.wait(10)
            assert window.splitter.height() == viewport.height()
            assert window.body_scroll.verticalScrollBar().maximum() == 0
            for panel, button, right in (
                (window.inference_panel, window.inference_panel.run_button, False),
                (window.action_panel, window.action_panel.rerun_button, True),
            ):
                bar = window.body_scroll.horizontalScrollBar()
                bar.setValue(bar.maximum() if right else 0)
                qtbot.wait(2)
                bounds = QRect(button.mapTo(viewport, button.rect().topLeft()), button.size())
                assert viewport.rect().contains(bounds)
                assert panel.controls_scroll.verticalScrollBar().maximum() > 0
    finally:
        qapp.setStyleSheet(old_style)
