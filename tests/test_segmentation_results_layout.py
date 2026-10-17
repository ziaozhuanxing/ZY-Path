"""Segmentation presentation, statistics and history without production weights."""
import json

import numpy as np
import pytest
from PIL import Image
from fpdf import FPDF
from PyQt5.QtCore import QPointF, QRect, QSettings, Qt
from PyQt5.QtGui import QColor, QFont

from core.large_image_segmentation import SEGMENTATION_COLORS, SEGMENTATION_LABELS, make_overlay
from ui.main_window import MainWindow
from ui.result_panel import ResultPanel
from ui.segmentation_result import SegmentationResult
from ui.theme import apply_theme
from data.export_manager import ExportManager


def segmentation_fixture(tmp_path, custom=False):
    """Known pixels, including non-contiguous class IDs, not a model prediction."""
    original = Image.new('RGB', (600, 400), (100, 120, 140))
    image_path = tmp_path / 'source.png'
    original.save(image_path)
    mask = np.zeros((400, 600), dtype=np.uint8)
    mask[:, 100:400] = 2
    mask[:, 400:] = 8 if not custom else 2
    counts = np.bincount(mask.ravel(), minlength=9)
    colors = np.asarray(SEGMENTATION_COLORS, dtype=np.uint8)
    if custom:
        colors = colors.copy()
        colors[0], colors[2] = (25, 35, 45), (65, 75, 85)
    color_mask = Image.fromarray(colors[mask])
    overlay = make_overlay(original, color_mask, .4 if custom else .2)
    return {
        'task_type': 'segmentation', 'model_path': str(tmp_path / 'recorded-model.pth'),
        'model_name': 'Recorded model', 'image_path': str(image_path),
        'timestamp': '2026-10-17T04:00:00+00:00', 'preprocess_profile': 'recorded-profile',
        'source_format': 'checkpoint' if custom else 'upernet_state_dict',
        'mask': mask, 'color_mask': Image.fromarray(np.asarray(SEGMENTATION_COLORS, dtype=np.uint8)[mask]) if custom else color_mask,
        'overlay': Image.fromarray(np.dstack((colors[mask], np.full(mask.shape, 102, dtype=np.uint8))), 'RGBA') if custom else overlay,
        'blended': overlay, 'counts': counts, 'width': 600, 'height': 400,
        'classes_present': [0, 2] if custom else [0, 2, 8],
        'legend_items': [('Custom background', tuple(colors[0])), ('Custom tissue', tuple(colors[2]))] if custom else list(zip(SEGMENTATION_LABELS, SEGMENTATION_COLORS)),
        'tile': 512, 'stride': 384, 'input_size': 512, 'device': 'cpu', 'elapsed_seconds': 1.25,
    }


@pytest.mark.parametrize('size', [(1000, 700), (600, 500), (360, 420)])
@pytest.mark.parametrize('theme,font_size', [('Light', 10), ('Dark', 15)])
def test_segmentation_image_summary_and_comparison_fit(qtbot, qapp, tmp_path, size, theme, font_size):
    old_font, old_style, old_theme = QFont(qapp.font()), qapp.styleSheet(), qapp.property('zyTheme')
    apply_theme(qapp, theme)
    font = QFont(old_font)
    font.setPointSize(font_size)
    qapp.setFont(font)
    try:
        result = segmentation_fixture(tmp_path)
        analysis, colors, legend = MainWindow._segmentation_display_data(result)
        page = SegmentationResult()
        qtbot.addWidget(page)
        page.resize(*size)
        with Image.open(result['image_path']) as original:
            page.show_result(result['blended'], legend, original, colors, result['counts'], analysis)
        page.show()
        qtbot.wait(40)
        assert (page.width(), page.height()) == size
        assert page.view_mode.currentText() == 'Overlay'
        assert not page.compare.isChecked()
        assert page.original_pane.isHidden()
        assert page.image.graphics_view.viewport().height() >= 60
        assert page.image.pixmap().toImage().pixelColor(150, 150) == QColor(*result['blended'].getpixel((150, 150)))
        assert page.legend_scroll.horizontalScrollBar().maximum() == 0
        assert len(page.cards) == 9
        for i, (card, swatch, name, stat) in enumerate(page.cards):
            page.legend_scroll.ensureWidgetVisible(card, 0, 0)
            qtbot.wait(2)
            visible = QRect(card.mapTo(page.legend_scroll.viewport(), card.rect().topLeft()), card.size())
            assert page.legend_scroll.viewport().rect().contains(visible)
            assert name.text() == SEGMENTATION_LABELS[i]
            assert f"{result['counts'][i] / 240000:.2%}" in stat.text()
            assert swatch.grab().toImage().pixelColor(5, 5) == QColor(*SEGMENTATION_COLORS[i])
        page.compare.setChecked(True)
        qtbot.wait(30)
        assert page.original_pane.isVisible()
        assert page.image.isVisible()
        assert page.original_view.graphics_view.viewport().height() >= 20
        assert page.image.graphics_view.viewport().height() >= 20
        assert page.comparison_splitter.orientation() == (Qt.Horizontal if size[0] >= 700 else Qt.Vertical)
        assert page.comparison_splitter.handleWidth() == 6
        assert page.rect().contains(QRect(page.compare.mapTo(page, page.compare.rect().topLeft()), page.compare.size()))
        page.compare.setChecked(False)
        assert page.original_pane.isHidden()
    finally:
        qapp.setStyleSheet(old_style)
        qapp.setProperty('zyTheme', old_theme)
        qapp.setFont(old_font)


def test_views_opacity_and_task_transitions_preserve_pixels_statistics_and_zoom(qtbot, tmp_path):
    result = segmentation_fixture(tmp_path)
    before_mask, before_counts = result['mask'].copy(), result['counts'].copy()
    analysis, colors, legend = MainWindow._segmentation_display_data(result)
    panel = ResultPanel()
    qtbot.addWidget(panel)
    panel.resize(900, 700)
    panel.show()
    with Image.open(result['image_path']) as source:
        original = source.copy()
    panel.show_segmentation(result['blended'], legend, original, colors, result['counts'], analysis)
    qtbot.wait(30)
    page = panel.segmentation_page
    assert panel.image_pane.isHidden()
    page.image.actual_size()
    page.image.graphics_view.centerOn(QPointF(350, 220))
    transform = page.image.graphics_view.transform()
    center = page.image.graphics_view.mapToScene(page.image.graphics_view.viewport().rect().center())
    for mode, expected in [('original', original), ('segmentation_map', colors), ('overlay', result['blended'])]:
        page.view_mode.setCurrentIndex(page.view_mode.findData(mode))
        assert page.render_image().tobytes() == expected.tobytes()
        assert page.image.graphics_view.transform() == transform
        restored_center = page.image.graphics_view.mapToScene(page.image.graphics_view.viewport().rect().center())
        assert abs(restored_center.x() - center.x()) < 2
        assert abs(restored_center.y() - center.y()) < 2
        assert page.opacity.isEnabled() == (mode == 'overlay')
    page.opacity.setValue(65)
    assert page.render_image().tobytes() == make_overlay(original, colors, .65).tobytes()
    assert np.array_equal(before_mask, result['mask'])
    assert np.array_equal(before_counts, result['counts'])
    panel.show_classification('STR', .9, [.9, .1], ['STR', 'NORM'])
    assert not panel.image_pane.isHidden()
    panel.clear()
    assert page.analysis is None and not page.compare.isChecked()
    assert page.image.pixmap().isNull() and page.original_view.pixmap().isNull()
    assert all(card.isHidden() for card, *_ in page.cards)


@pytest.mark.parametrize('custom', [False, True])
def test_history_and_exports_preserve_segmentation_view_class_ids_and_model(qtbot, tmp_path, monkeypatch, custom):
    result = segmentation_fixture(tmp_path, custom)
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    settings.setValue('export/pngReminderEnabled', False)
    settings.setValue('export/pdfReminderEnabled', False)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.show()
    window._show_inference_result(result)
    qtbot.wait(30)
    record_id = window.current_record_id
    assert record_id is not None
    record = window.database_manager.get_record_by_id(record_id)
    initial = json.loads(record['analysis_json'])
    assert initial['pixel_counts'] == result['counts'].tolist()
    assert initial['presentation'] == {'view': 'overlay', 'opacity': .4 if custom else .2, 'compare': False, 'link_views': True, 'split_ratio': .5}
    with Image.open(record['result_image_path']) as stored:
        assert stored.tobytes() == result['blended'].tobytes()
    page = window.result_panel.segmentation_page
    if custom:
        assert [item['index'] for item in initial['classes']] == [0, 2]
        assert '83.33%' in page.cards[1][3].text()
        assert page.color_mask.getpixel((500, 100)) == (65, 75, 85)
    initial_without_view = {k: v for k, v in initial.items() if k != 'presentation'}
    page.view_mode.setCurrentIndex(page.view_mode.findData('segmentation_map'))
    page.compare.setChecked(True)
    page.opacity.setValue(55)
    page.link_views.setChecked(False)
    splitter = page.comparison_splitter
    span = splitter.width() if splitter.orientation() == Qt.Horizontal else splitter.height()
    splitter.moveSplitter(round(span * .6), 1)
    qtbot.wait(20)
    selected = page.presentation()
    updated = json.loads(window.database_manager.get_record_by_id(record_id)['analysis_json'])
    assert updated['presentation'] == selected
    assert {k: v for k, v in updated.items() if k != 'presentation'} == initial_without_view
    # Load a different task first to expose stale display state.
    window.result_panel.show_classification('STR', .9, [.9, .1], ['STR', 'NORM'])
    window._show_record_activated(record_id)
    qtbot.wait(30)
    assert page.presentation() == selected and page.original_pane.isVisible()
    assert window.result_panel.image_pane.isHidden()
    assert window._current_result['metadata']['model_path'] == result['model_path']
    expected = page.color_mask.tobytes()
    target = tmp_path / 'current-view.png'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(target), ''))
    window._export_current_png()
    with Image.open(target) as exported:
        assert exported.tobytes() == expected
    metadata = json.loads(target.with_suffix('.png.json').read_text())
    assert metadata['task_type'] == 'segmentation'
    assert metadata['model_path'] == result['model_path']
    assert metadata['segmentation_analysis']['presentation'] == selected
    assert metadata['segmentation_analysis']['pixel_counts'] == initial['pixel_counts']
    assert 'classification_analysis' not in metadata
    pdf_target = tmp_path / 'current-view.pdf'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(pdf_target), ''))
    pdf_calls = []

    def inspect_pdf(path, original, rendered, report_metadata):
        with Image.open(rendered) as image:
            assert image.tobytes() == expected
        assert report_metadata == metadata
        pdf_calls.append(path)

    monkeypatch.setattr(window.export_manager, 'export_pdf', inspect_pdf)
    window._export_current_pdf()
    assert pdf_calls == [str(pdf_target)]


def test_old_overlay_only_results_disable_unavailable_views(qtbot):
    page = SegmentationResult()
    qtbot.addWidget(page)
    overlay = Image.new('RGBA', (15, 10), (20, 30, 40, 102))
    page.show_result(overlay, [('Stored class', (20, 30, 40))],
                     presentation={'view': 'original', 'compare': True, 'opacity': .6})
    assert page.view_mode.currentData() == 'overlay'
    assert not page.view_mode.model().item(1).isEnabled()
    assert not page.view_mode.model().item(2).isEnabled()
    assert not page.compare.isEnabled() and not page.compare.isChecked()
    assert not page.opacity.isEnabled()
    assert page.render_image().tobytes() == overlay.tobytes()
    assert 'unavailable' in page.cards[0][3].text()


def test_real_pdf_includes_segmentation_model_view_colors_and_pixel_statistics(tmp_path, monkeypatch):
    result = segmentation_fixture(tmp_path)
    analysis, _, _ = MainWindow._segmentation_display_data(result)
    analysis['presentation'] = {'view': 'segmentation_map', 'opacity': .65, 'compare': True}
    result_path = tmp_path / 'mask.png'
    result['color_mask'].save(result_path)
    texts = []
    original_multi_cell = FPDF.multi_cell

    def record_text(pdf, width, height, text='', *args, **kwargs):
        texts.append(str(text))
        return original_multi_cell(pdf, width, height, text, *args, **kwargs)

    monkeypatch.setattr(FPDF, 'multi_cell', record_text)
    path = ExportManager().export_pdf(tmp_path / 'report.pdf', result['image_path'], result_path,
                                    {'model_name': result['model_name'], 'model_path': result['model_path'],
                                     'task_type': 'segmentation', 'segmentation_analysis': analysis})
    content = path.read_bytes()
    assert content.startswith(b'%PDF') and content.count(b'/Subtype /Image') >= 2
    report = '\n'.join(texts)
    assert result['model_path'] in report
    assert 'segmentation_map' in report and '0.65' in report
    assert '120000 pixels; full-image coverage=50.00%' in report
    assert 'RGB=[0, 255, 0]' in report
    assert 'background and excluded labels included' in report
