"""Regression tests for explicit modes, source-coordinate overlays and resizable UI."""
import json
import re

import cv2
import numpy as np
from PIL import Image
import pytest
import torch
from torch import nn
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QApplication, QLabel, QScrollArea, QMessageBox

from core.classification_tiles import (CLASSIFICATION_LABELS, CLASSIFICATION_COLORS,
    ClassificationTileSpec, exploratory_metadata, predict_classification_tiles, render_classification_map)
from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel
from core.preprocessor import Preprocessor
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


class RecordingClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def forward(self, value):
        self.inputs.append(value.clone())
        index = int(round(value[0, 2].mean().item()))
        label = 6 if index == 24 else 4 if index == 48 else 7
        logits = torch.zeros((1, 9))
        logits[0, label] = 5
        return logits


@pytest.mark.parametrize('backend', ['pillow_bilinear', 'opencv_linear'])
def test_real_coordinate_crops_and_single_crop_predictions_match(tmp_path, backend):
    # Match the reported geometry, using synthetic coordinate-coded pixels, not a fake weight file.
    width, height = 3552, 3536
    pixels = np.empty((height, width, 3), dtype=np.uint8)
    pixels[:, :, 0] = np.arange(width, dtype=np.uint16)[None, :] % 251
    pixels[:, :, 1] = np.arange(height, dtype=np.uint16)[:, None] % 253
    pixels[:, :, 2] = np.arange(width)[None, :] // 512 + 7 * (np.arange(height)[:, None] // 512)
    image = Image.fromarray(pixels)
    model = RecordingClassifier().eval()
    metadata = exploratory_metadata(512, 512, backend)
    spec = ClassificationTileSpec.from_metadata(metadata, list(CLASSIFICATION_LABELS), 'raw255')
    tiled = predict_classification_tiles(image, model, spec)
    analysis = tiled['classification_analysis']
    assert len(analysis['tiles']) == 49
    assert analysis['tile_counts'] == [0, 0, 0, 0, 1, 0, 1, 47, 0]
    assert analysis['tiles'][-1]['box'] == [3072, 3072, 3552, 3536]
    assert analysis['pixel_counts'][4] == 480 * 464
    assert analysis['pixel_counts'][6] == 512 * 512
    assert sum(analysis['pixel_counts']) == width * height
    coverage = np.zeros((height, width), dtype=np.uint8)
    tiled_inputs = list(model.inputs)
    assert len(tiled_inputs) == 49
    for tile, actual in zip(analysis['tiles'], tiled_inputs):
        x0, y0, x1, y1 = tile['box']
        coverage[y0:y1, x0:x1] += 1
        expected = Preprocessor('raw255', resize_backend=backend).transform(image.crop(tile['box']))
        assert actual.dtype == torch.float32
        assert torch.equal(actual, expected)
    assert coverage.min() == coverage.max() == 1
    assert len({tensor[0, 2, 0, 0].item() for tensor in tiled_inputs}) == 49
    loaded = LoadedModel(model, 'checkpoint', list(CLASSIFICATION_LABELS), 'test', 'raw255')
    for index in (0, 24, 48):
        tile = analysis['tiles'][index]
        crop_path = tmp_path / f'crop-{index}.png'
        image.crop(tile['box']).save(crop_path)
        direct = InferenceEngine(tmp_path / 'not-written.pth', crop_path, 'classification',
            loaded_model=loaded, classification_mode='single_image', classification_resize_backend=backend).run_pipeline()
        assert torch.equal(model.inputs[-1], tiled_inputs[index])
        assert direct['label'] == tile['label']
        assert direct['confidence'] == tile['confidence']
        assert direct['probabilities'] == tile['probabilities']


def test_resize_backend_matches_opencv_and_differs_from_pillow_on_texture():
    rng = np.random.default_rng(42)
    pixels = rng.integers(0, 256, (512, 512, 3), dtype=np.uint8)
    image = Image.fromarray(pixels)
    actual = Preprocessor('raw255', resize_backend='opencv_linear').transform(image)
    expected = cv2.resize(pixels, (224, 224), interpolation=cv2.INTER_LINEAR)
    assert np.array_equal(actual[0].permute(1, 2, 0).numpy(), expected.astype(np.float32))
    legacy = Preprocessor('raw255').transform(image)
    assert not torch.equal(actual, legacy)
    assert actual.min() >= 0 and actual.max() <= 255


def test_overlay_alpha_boundaries_and_coordinate_dimensions():
    original = Image.new('RGB', (12, 10), (20, 40, 60))
    spec = ClassificationTileSpec.from_metadata(exploratory_metadata(6, 5), list(CLASSIFICATION_LABELS), 'raw255')
    result = predict_classification_tiles(original, RecordingClassifier(), spec)
    color = result['color_map']
    analysis = result['classification_analysis']
    assert render_classification_map(original, color, analysis, 0).tobytes() == original.tobytes()
    assert render_classification_map(original, color, analysis, 1).tobytes() == color.tobytes()
    overlay = render_classification_map(original, color, analysis, .4)
    assert overlay.size == original.size == color.size
    assert overlay.getpixel((2, 2)) == tuple(int(a * .6 + b * .4) for a, b in zip((20, 40, 60), CLASSIFICATION_COLORS[7]))
    boundary = render_classification_map(original, color, analysis, .4, boundaries=True)
    assert boundary.getpixel((6, 2)) == (255, 255, 255)
    assert boundary.getpixel((2, 2)) == overlay.getpixel((2, 2))
    assert render_classification_map(original, color, analysis, color_only=True).tobytes() == color.tobytes()
    with pytest.raises(ValueError, match='coordinates'):
        render_classification_map(Image.new('RGB', (3, 3)), color, analysis)


@pytest.mark.parametrize('scale', [1, 1.25, 1.5, 2])
def test_preferences_scroll_and_controls_at_larger_fonts(qtbot, tmp_path, scale):
    app = QApplication.instance()
    old_font = app.font()
    font = QFont(old_font)
    font.setPointSizeF(10 * scale)
    app.setFont(font)
    try:
        dialog = SettingsDialog(QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat))
        qtbot.addWidget(dialog)
        assert dialog.windowFlags() & Qt.WindowMaximizeButtonHint
        dialog.navigation.setCurrentRow(1)
        dialog.resize(620, 400)
        dialog.show()
        qtbot.waitExposed(dialog)
        qtbot.wait(20)
        scroll = dialog.pages.currentWidget()
        assert isinstance(scroll, QScrollArea)
        assert scroll.widgetResizable()
        assert scroll.horizontalScrollBar().maximum() == 0
        assert scroll.verticalScrollBar().maximum() > 0
        assert (dialog.tile_width.value(), dialog.tile_height.value()) == (512, 512)
        for label, name in zip(dialog.palette_labels, CLASSIFICATION_LABELS):
            scroll.ensureWidgetVisible(label)
            qtbot.wait(5)
            assert name in label.text()
            assert label.height() >= QFontMetrics(label.font()).height()
            assert label.mapTo(scroll.viewport(), label.rect().topLeft()).y() >= 0
        text = ' '.join(label.text() for label in dialog.findChildren(QLabel))
        assert not re.search(r'[\u4e00-\u9fff]', text)
        dialog.showMaximized()
        qtbot.wait(20)
        dialog.showNormal()
    finally:
        app.setFont(old_font)


@pytest.mark.parametrize('mode', ['single_image', 'tiled_analysis'])
@pytest.mark.parametrize('backend', ['pillow_bilinear', 'opencv_linear'])
def test_record_mode_and_rerun_ignore_current_preferences(qtbot, tmp_path, mode, backend, monkeypatch):
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(str(args[-1])))
    settings = QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat)
    settings.setValue('classification/resizeBackend', backend)
    settings.setValue('classificationTiles/width', 6)
    settings.setValue('classificationTiles/height', 5)
    path = tmp_path / 'in-memory.pth'
    source = tmp_path / 'image.png'
    Image.new('RGB', (12, 10), (20, 40, 48)).save(source)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        builtin_model_path=path, results_dir=tmp_path / 'results')
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window._builtin_model_statuses['classification'] is not None)
    loaded = LoadedModel(RecordingClassifier().eval(), 'checkpoint', list(CLASSIFICATION_LABELS), 'test', 'raw255')
    window._validated_builtin_model = (path, loaded)
    window._builtin_model_statuses['classification'] = ('In-memory classifier', True)
    window._builtin_model_task = 'classification'
    window.inference_panel.set_model_ready(True)
    window.inference_panel.set_image(str(source))
    window.inference_panel.set_classification_mode(mode)
    assert ('Tiled analysis' if mode == 'tiled_analysis' else 'Single image') in window.inference_panel.mode_summary.text()
    qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    record = window.database_manager.get_all_records()[0]
    assert json.loads(record['analysis_json'])['classification_mode'] == mode
    assert window._current_result['metadata']['classification_mode'] == mode
    assert json.loads(record['analysis_json'])['resize_backend'] == backend
    assert window._current_result['metadata']['classification_analysis']['resize_backend'] == backend
    settings.setValue('export/pngReminderEnabled', False)
    exported = tmp_path / 'classification-export.png'
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *args, **kwargs: (str(exported), ''))
    window._export_current_png()
    exported_metadata = json.loads((tmp_path / 'classification-export.png.json').read_text())
    assert exported_metadata['classification_mode'] == mode
    assert exported_metadata['classification_analysis']['resize_backend'] == backend
    settings.setValue('classificationTiles/width', 100)
    settings.setValue('classificationTiles/height', 100)
    settings.setValue('classification/resizeBackend', 'opencv_linear' if backend == 'pillow_bilinear' else 'pillow_bilinear')
    window.inference_panel.set_classification_mode('single_image' if mode == 'tiled_analysis' else 'tiled_analysis')
    window._show_record_activated(record['id'])
    assert window.inference_panel.classification_mode() == mode
    if mode == 'tiled_analysis':
        page = window.result_panel.tile_page
        assert page.view_mode.currentText() == 'Overlay'
        qtbot.wait(20)
        page.image.zoom_in()
        transform = page.image.graphics_view.transform()
        page.opacity.setValue(60)
        assert page.image.graphics_view.transform() == transform
        assert page.render_image().size == (12, 10)
        page.view_mode.setCurrentIndex(1)
        page.boundaries.setChecked(True)
        assert page.presentation() == {'view': 'color_map', 'opacity': .6, 'boundaries': True, 'compare': False, 'link_views': True, 'split_ratio': .5}
        page.tile_details_button.setChecked(True)
        page.tabs.setCurrentWidget(page.legend)
        assert page.image.isVisible()
        assert page.legend.isVisible()
        assert page.legend.rowCount() == 9
        assert [page.legend.item(i, 0).text() for i in range(9)] == list(CLASSIFICATION_LABELS)
    window.history_panel.select_record(record['id'])
    window._handle_rerun_requested()
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    records = window.database_manager.get_all_records()
    assert not warnings, warnings
    assert len(records) == 2
    rerun = json.loads(records[0]['analysis_json'])
    assert rerun['classification_mode'] == mode
    assert rerun['resize_backend'] == backend
    if mode == 'tiled_analysis':
        assert rerun['tile_size'] == [6, 5]
        assert len(rerun['tiles']) == 4


def test_tiled_analysis_explicitly_classifies_one_small_tile(tmp_path):
    image_path = tmp_path / 'small.png'
    Image.new('RGB', (32, 24), (20, 40, 48)).save(image_path)
    loaded = LoadedModel(RecordingClassifier().eval(), 'checkpoint', list(CLASSIFICATION_LABELS), 'test', 'raw255')
    engine = InferenceEngine(tmp_path / 'not-written.pth', image_path, 'classification',
        loaded_model=loaded, classification_mode='tiled_analysis', classification_tile_metadata=exploratory_metadata(512, 512))
    tiled = engine.run_pipeline()
    assert tiled['classification_mode'] == 'tiled_analysis'
    assert [tile['box'] for tile in tiled['classification_analysis']['tiles']] == [[0, 0, 32, 24]]
    assert sum(tiled['classification_analysis']['pixel_counts']) == 32 * 24
    engine.classification_mode = 'single_image'
    direct = engine.run_pipeline()
    assert direct['classification_mode'] == 'single_image'
    assert 'classification_analysis' not in direct
    assert direct['label'] == tiled['label']
    assert direct['probabilities'] == tiled['probabilities']


def test_default_resize_is_legacy_pillow_and_opencv_choice_is_consistent(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'defaults.ini'), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert dialog.resize_method.currentText() == 'Pillow bilinear (legacy)'
    assert dialog.resize_method.currentData() == 'pillow_bilinear'
    pixels = np.random.default_rng(7).integers(0, 256, (513, 511, 3), dtype=np.uint8)
    image = Image.fromarray(pixels)
    actual_default = Preprocessor('raw255').transform(image)[0].permute(1, 2, 0).numpy()
    expected_legacy = np.asarray(image.resize((224, 224), Image.Resampling.BILINEAR), dtype=np.float32)
    assert np.array_equal(actual_default, expected_legacy)
    index = dialog.resize_method.findText('OpenCV linear')
    assert index >= 0
    assert dialog.resize_method.itemData(index) == 'opencv_linear'
    dialog.resize_method.setCurrentIndex(index)
    assert settings.value('classification/resizeBackend', type=str) == 'opencv_linear'
    restored = SettingsDialog(QSettings(settings.fileName(), QSettings.IniFormat))
    qtbot.addWidget(restored)
    assert restored.resize_method.currentText() == 'OpenCV linear'
    backend = restored.resize_method.currentData()
    actual = Preprocessor('raw255', resize_backend=backend).transform(image)[0].permute(1, 2, 0).numpy()
    expected = cv2.resize(pixels, (224, 224), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    assert np.array_equal(actual, expected)
