"""Persistent image/summary and source-coordinate inspection without model weights."""
import copy
import json

import pytest
from PIL import Image
from PyQt5.QtCore import QEvent, QPointF, QRect, QSettings, Qt
from PyQt5.QtGui import QColor, QFont, QHelpEvent
from PyQt5.QtWidgets import QApplication, QToolTip

from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.theme import apply_theme
from test_screen_fit_and_tile_grid import synthetic_result


@pytest.mark.parametrize('size', [(900, 640), (520, 460), (360, 420)])
@pytest.mark.parametrize('font_scale', [1, 1.5])
def test_image_summary_and_details_share_a_small_window(qtbot, qapp, tmp_path, size, font_scale):
    old_font = QFont(qapp.font())
    old_style = qapp.styleSheet()
    old_theme = qapp.property('zyTheme')
    apply_theme(qapp, 'Dark' if font_scale > 1 else 'Light')
    font = QFont(old_font)
    font.setPointSizeF(10 * font_scale)
    qapp.setFont(font)
    try:
        result = synthetic_result(tmp_path)
        analysis = result['classification_analysis']
        page = ClassificationResult()
        qtbot.addWidget(page)
        page.resize(*size)
        page.show_result(result['color_map'], result['color_map'], analysis)
        page.show()
        qtbot.wait(40)
        assert not page.tile_details_button.isChecked()
        assert not page.tabs.isVisible()
        assert page.legend_scroll.isVisible()
        assert len(page.class_cards) == 9
        assert page.legend_scroll.horizontalScrollBar().maximum() == 0
        for index, (card, text, swatch) in enumerate(zip(page.class_cards, page.class_labels, page.class_swatches)):
            assert text.text().startswith(analysis['classes'][index]['label'])
            assert f"{analysis['tile_counts'][index]} tiles" in text.text()
            assert f"{analysis['area_ratios'][index]:.2%}" in text.text()
            assert str(tuple(analysis['classes'][index]['color'])) in card.toolTip()
            page.legend_scroll.ensureWidgetVisible(card, 0, 0)
            qtbot.wait(2)
            visible = QRect(card.mapTo(page.legend_scroll.viewport(), card.rect().topLeft()), card.size())
            assert page.legend_scroll.viewport().rect().contains(visible)
            assert swatch.grab().toImage().pixelColor(4, 4) == QColor(*analysis['classes'][index]['color'])
        # MUC is a partial 480x464 crop, so its area ratio is not its tile ratio.
        assert analysis['area_ratios'][4] != pytest.approx(1 / 49)
        for expanded in (True, False, True):
            page.tile_details_button.setChecked(expanded)
            qtbot.wait(30)
            assert page.tabs.isVisible() == expanded
            assert page.image.isVisible()
            assert page.image.graphics_view.viewport().height() >= 60
            assert page.legend_scroll.isVisible()
            button = page.tile_details_button
            assert page.rect().contains(QRect(button.mapTo(page, button.rect().topLeft()), button.size()))
            if expanded:
                for table in (page.table, page.legend):
                    page.tabs.setCurrentWidget(table)
                    qtbot.wait(10)
                    assert table.viewport().height() >= 20
                    assert page.image.isVisible()
                    assert page.legend_scroll.isVisible()
                    assert table.selectionMode() == table.NoSelection
        assert page.table.rowCount() == 49
        assert page.legend.rowCount() == 9
    finally:
        qapp.setStyleSheet(old_style)
        qapp.setProperty('zyTheme', old_theme)
        qapp.setFont(old_font)


def test_hover_uses_actual_boxes_under_fit_zoom_pan_and_display_modes(qtbot, tmp_path, monkeypatch):
    result = synthetic_result(tmp_path)
    analysis = result['classification_analysis']
    before = copy.deepcopy(analysis)
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(800, 700)
    page.show_result(result['color_map'], result['color_map'], analysis)
    page.show()
    qtbot.wait(30)
    assert page.tile_at_source(QPointF(0, 0))[0] == 0
    assert page.tile_at_source(QPointF(511.99, 511.99))[0] == 0
    assert page.tile_at_source(QPointF(512, 0))[0] == 1
    assert page.tile_at_source(QPointF(3072, 3072))[0] == 48
    for outside in (QPointF(-1, 10), QPointF(3552, 100), QPointF(100, 3536)):
        assert page.tile_at_source(outside) is None
    shown = []
    monkeypatch.setattr(QToolTip, 'showText', lambda position, text, *args: shown.append(text))
    monkeypatch.setattr(QToolTip, 'hideText', lambda: None)
    source_point = QPointF(3312, 3304)
    view = page.image.graphics_view
    viewport = view.viewport()
    for expanded in (False, True):
        page.tile_details_button.setChecked(expanded)
        for mode in range(3):
            page.view_mode.setCurrentIndex(mode)
            page.boundaries.setChecked(mode == 1)
            for action in (page.image.fit_to_view, page.image.zoom_in, page.image.zoom_out, page.image.actual_size):
                action()
                view.centerOn(source_point)
                qtbot.wait(5)
                pos = view.mapFromScene(source_point)
                assert viewport.rect().contains(pos)
                event = QHelpEvent(QEvent.ToolTip, pos, viewport.mapToGlobal(pos))
                QApplication.sendEvent(viewport, event)
                assert shown[-1] == ('Tile 49: MUC\nConfidence: 80.00%\n'
                                     'Source crop: (3072, 3072, 3552, 3536)\nSize: 480 x 464 px')
                QApplication.sendEvent(viewport, QEvent(QEvent.Leave))
                assert not page._hover_tooltip_active
    assert analysis == before
    page.clear()
    assert page.tile_at_source(source_point) is None
    assert not page.tabs.isVisible()
    assert all(card.isHidden() for card in page.class_cards)


def test_history_original_view_export_and_other_tasks_keep_their_layout(qtbot, tmp_path, monkeypatch):
    result = synthetic_result(tmp_path)
    original = Image.new('RGB', (3552, 3536), (55, 65, 75))
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    settings.setValue('export/pngReminderEnabled', False)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.resize(800, 640)
    window.show()
    window._show_inference_result(result)
    qtbot.wait(30)
    page = window.result_panel.tile_page
    assert window.result_panel.image_pane.isHidden()
    record = window.database_manager.get_all_records()[0]
    analysis = json.loads(record['analysis_json'])
    analysis['presentation'] = {'view': 'original', 'opacity': .6, 'boundaries': False}
    with window.database_manager._connection() as connection:
        connection.execute('UPDATE segmentation_artifacts SET analysis_json=? WHERE record_id=?',
                           (json.dumps(analysis), record['id']))
    page.tile_details_button.setChecked(True)
    window._show_record_activated(record['id'])
    qtbot.wait(30)
    assert page.view_mode.currentText() == 'Original image'
    assert not page.opacity.isEnabled()
    assert not page.tile_details_button.isChecked()
    assert len(page.class_cards) == 9
    assert page.table.rowCount() == 49
    assert page.render_image().tobytes() == original.tobytes()
    assert page.tile_at_source(QPointF(3312, 3304))[1]['label'] == 'MUC'
    target = tmp_path / 'original-view.png'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(target), ''))
    window._export_current_png()
    with Image.open(target) as exported:
        assert exported.tobytes() == original.tobytes()
    metadata = json.loads(target.with_suffix('.png.json').read_text())
    assert metadata['classification_mode'] == 'tiled_analysis'
    assert metadata['classification_analysis']['presentation']['view'] == 'original'
    assert metadata['classification_analysis']['tile_counts'] == result['classification_analysis']['tile_counts']
    assert metadata['model_path'] == result['model_path']
    settings.setValue('export/pdfReminderEnabled', False)
    pdf_target = tmp_path / 'original-view.pdf'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(pdf_target), ''))
    pdf_calls = []

    def inspect_pdf_inputs(output_path, original_path, result_path, report_metadata):
        with Image.open(result_path) as exported:
            assert exported.tobytes() == original.tobytes()
        assert report_metadata['classification_mode'] == 'tiled_analysis'
        assert report_metadata['classification_analysis']['presentation']['view'] == 'original'
        pdf_calls.append(str(output_path))

    monkeypatch.setattr(window.export_manager, 'export_pdf', inspect_pdf_inputs)
    window._export_current_pdf()
    assert pdf_calls == [str(pdf_target)]
    window.result_panel.show_classification('STR', .8, [.8, .2], ['STR', 'NORM'])
    qtbot.wait(20)
    assert not window.result_panel.image_pane.isHidden()
    assert window.result_panel.image_label.graphics_view.viewport().height() > 0
    window.result_panel.show_classification_tiles(result['color_map'], result['classification_analysis'], original)
    assert window.result_panel.image_pane.isHidden()
    window.result_panel.show_segmentation(Image.new('RGBA', (20, 20)), [('Existing segmentation', (10, 20, 30))])
    qtbot.wait(20)
    assert window.result_panel.image_pane.isHidden()
    assert window.result_panel.overlay_label.graphics_view.viewport().height() > 0
    assert window.result_panel.result_stack.currentWidget() is window.result_panel.segmentation_page
