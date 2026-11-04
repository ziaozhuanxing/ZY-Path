"""Check deployed tensors against the training script's deterministic operations."""

import cv2
import numpy as np
import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QSettings
from torch import nn

from core.classification_input import load_rgb_image
from core.classification_tiles import CLASSIFICATION_LABELS, exploratory_metadata
from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel, ModelValidationError
from core.preprocessor import Preprocessor
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


class RecordingClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def forward(self, value):
        self.inputs.append(value.detach().clone())
        return value.mean((2, 3)).repeat(1, 3)


def training_reference(path):
    rgb = cv2.cvtColor(cv2.imread(str(path), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_LINEAR)
    return torch.from_numpy(resized.transpose(2, 0, 1).copy()).float().unsqueeze(0)


@pytest.mark.parametrize('dimensions', [(224, 224), (256, 256), (300, 300), (512, 512), (401, 257)])
@pytest.mark.parametrize('mode', ['single_image', 'tiled_analysis'])
def test_actual_network_tensor_matches_training_validation(tmp_path, dimensions, mode):
    width, height = dimensions
    pixels = np.random.default_rng(42).integers(0, 256, (height, width, 3), dtype=np.uint8)
    path = tmp_path / 'source.png'
    Image.fromarray(pixels).save(path)
    model = RecordingClassifier()
    loaded = LoadedModel(model, 'checkpoint', list(CLASSIFICATION_LABELS), 'densenet', 'raw255')
    result = InferenceEngine(tmp_path / 'not-written.pth', path, 'classification', loaded_model=loaded,
        classification_mode=mode, classification_tile_metadata=exploratory_metadata(width, height)).run_pipeline()
    assert torch.equal(model.inputs[-1], training_reference(path))
    assert model.inputs[-1].dtype == torch.float32
    assert model.inputs[-1].shape == (1, 3, 224, 224)
    assert model.inputs[-1].max() > 1  # raw255, not 0-1 or ImageNet scaling.
    analysis = result['classification_analysis' if mode == 'tiled_analysis' else 'classification_parameters']
    assert analysis['resize_backend'] == 'opencv_linear'
    assert analysis['image_decoder'] == 'opencv_color'


@pytest.mark.parametrize('kind', ['gray', 'rgba', 'uint16', 'exif_jpeg'])
def test_file_decoding_matches_training_including_bit_depth_and_orientation(tmp_path, kind):
    pixels = np.random.default_rng(7).integers(0, 256, (31, 47, 3), dtype=np.uint8)
    path = tmp_path / ('source.jpg' if kind == 'exif_jpeg' else 'source.png')
    if kind == 'gray':
        Image.fromarray(pixels[:, :, 0]).save(path)
    elif kind == 'rgba':
        Image.fromarray(np.dstack((pixels, pixels[:, :, 0]))).save(path)
    elif kind == 'uint16':
        Image.fromarray(pixels[:, :, 0].astype(np.uint16) * 257).save(path)
    else:
        exif = Image.Exif()
        exif[274] = 6
        Image.fromarray(pixels).save(path, exif=exif)
    actual = Preprocessor('raw255').transform(load_rgb_image(path, 'opencv_color'))
    assert torch.equal(actual, training_reference(path))


@pytest.mark.parametrize('extension', ['png', 'jpg'])
def test_unicode_filename_uses_same_opencv_decoder_on_fallback(tmp_path, monkeypatch, extension):
    path = tmp_path / ('结直肠测试.' + extension)
    exif = Image.Exif()
    exif[274] = 6
    Image.new('RGB', (17, 13), (7, 89, 230)).save(path, exif=exif)
    expected = load_rgb_image(path, 'opencv_color')
    monkeypatch.setattr(cv2, 'imread', lambda *args: None)
    assert np.array_equal(np.asarray(load_rgb_image(path, 'opencv_color')), np.asarray(expected))


@pytest.mark.parametrize('contents', [b'', b'not an image'])
def test_bad_input_is_rejected_without_falling_back_to_another_reader(tmp_path, contents):
    path = tmp_path / 'broken.png'
    path.write_bytes(contents)
    with pytest.raises(OSError, match='decoded by OpenCV'):
        load_rgb_image(path, 'opencv_color')


def test_upgrade_preserves_custom_dimensions_then_allows_explicit_legacy_choice(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'old.ini'), QSettings.IniFormat)
    settings.setValue('classificationTiles/width', 300)
    settings.setValue('classificationTiles/height', 256)
    settings.setValue('classification/resizeBackend', 'pillow_bilinear')
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert (dialog.tile_width.value(), dialog.tile_height.value()) == (300, 256)
    assert dialog.resize_method.currentData() == 'opencv_linear'
    dialog.resize_method.setCurrentIndex(dialog.resize_method.findData('pillow_bilinear'))
    reopened = SettingsDialog(settings)
    qtbot.addWidget(reopened)
    assert reopened.resize_method.currentData() == 'pillow_bilinear'


def test_missing_preferences_start_at_dataset_pixel_dimensions(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'new.ini'), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert (dialog.tile_width.value(), dialog.tile_height.value()) == (224, 224)
    assert dialog.resize_method.currentData() == 'opencv_linear'


def test_legacy_history_reader_and_resize_do_not_inherit_new_defaults(tmp_path):
    path = tmp_path / 'uint16.png'
    Image.fromarray(np.arange(240, dtype=np.uint16).reshape(12, 20) * 257).save(path)
    settings = MainWindow._record_classification_parameters({'analysis_json': None}, for_rerun=True)
    assert settings['resize_backend'] == 'pillow_bilinear'
    assert settings['image_decoder'] == 'pillow_rgb'
    model = RecordingClassifier()
    loaded = LoadedModel(model, 'checkpoint', list(CLASSIFICATION_LABELS), 'densenet', 'raw255')
    InferenceEngine(tmp_path / 'not-written.pth', path, 'classification', loaded_model=loaded,
        classification_resize_backend=settings['resize_backend'],
        classification_image_decoder=settings['image_decoder']).run_pipeline()
    with Image.open(path) as image:
        expected = Preprocessor('raw255', resize_backend='pillow_bilinear').transform(image)
    assert torch.equal(model.inputs[-1], expected)
    assert not torch.equal(model.inputs[-1], training_reference(path))


@pytest.mark.parametrize('profile,input_size', [('imagenet', [224, 224]), ('raw255', [128, 128])])
def test_crc_model_rejects_incompatible_recorded_network_parameters(tmp_path, profile, input_size):
    path = tmp_path / 'source.png'
    Image.new('RGB', (40, 40)).save(path)
    loaded = LoadedModel(RecordingClassifier(), 'checkpoint', list(CLASSIFICATION_LABELS), 'densenet', 'raw255')
    metadata = exploratory_metadata(40, 40)
    metadata['preprocess'] = profile
    metadata['input_size'] = input_size
    with pytest.raises(ModelValidationError, match='raw255|224 x 224'):
        InferenceEngine(tmp_path / 'not-written.pth', path, 'classification', loaded_model=loaded,
            preprocess_profile=profile, classification_mode='tiled_analysis', classification_tile_metadata=metadata).run_pipeline()


@pytest.mark.parametrize('mode', ['single_image', 'tiled_analysis'])
def test_source_orientation_and_reader_survive_history_and_pdf(qtbot, tmp_path, monkeypatch, mode):
    from pypdf import PdfReader

    path = tmp_path / 'rotated.jpg'
    exif = Image.Exif()
    exif[274] = 6
    pixels = np.random.default_rng(3).integers(0, 256, (48, 64, 3), dtype=np.uint8)
    Image.fromarray(pixels).save(path, exif=exif)
    original = load_rgb_image(path, 'opencv_color')
    assert original.size == (48, 64)
    loaded = LoadedModel(RecordingClassifier(), 'checkpoint', list(CLASSIFICATION_LABELS), 'densenet', 'raw255')
    result = InferenceEngine(tmp_path / 'not-written.pth', path, 'classification', loaded_model=loaded,
        classification_mode=mode, classification_tile_metadata=exploratory_metadata(224, 224)).run_pipeline()
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results')
    qtbot.addWidget(window)
    assert window._show_inference_result(result)
    record_id = window.current_record_id
    for restore in [False, True]:
        if restore:
            window._show_record_activated(record_id)
        assert window.inference_panel._source_pixmap.size().width() == 48
        assert window.inference_panel._source_pixmap.size().height() == 64
        assert window.result_panel._source_pixmap.size().width() == 48
        assert window.result_panel._source_pixmap.size().height() == 64
        if mode == 'tiled_analysis':
            assert np.array_equal(np.asarray(window.result_panel.tile_page.original), np.asarray(original))
    current = window._current_result
    destination = tmp_path / 'report.pdf'
    window.export_manager.export_pdf(destination, current['original_image_path'], current['result_image_path'], current['metadata'])
    text = '\n'.join(page.extract_text() for page in PdfReader(destination).pages)
    assert 'opencv_color' in text


@pytest.mark.parametrize('profile', ['raw255', 'imagenet'])
def test_classification_defaults_do_not_change_generic_segmentation_inputs(tmp_path, profile):
    class RecordingSegmenter(nn.Module):
        def __init__(self):
            super().__init__()
            self.inputs = []

        def forward(self, value):
            self.inputs.append(value.detach().clone())
            return value[:, :2]

    path = tmp_path / 'source.png'
    pixels = np.random.default_rng(4).integers(0, 256, (257, 401, 3), dtype=np.uint8)
    Image.fromarray(pixels).save(path)
    model = RecordingSegmenter()
    loaded = LoadedModel(model, 'module', None, None, profile)
    InferenceEngine(tmp_path / 'not-written.pt', path, 'segmentation', loaded_model=loaded).run_pipeline()
    with Image.open(path) as source:
        expected = Preprocessor(profile, resize_backend='pillow_bilinear').transform(source)
    assert torch.equal(model.inputs[-1], expected)
