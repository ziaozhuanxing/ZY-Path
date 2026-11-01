"""Release regressions using temporary data and in-memory inference fixtures.

No production model or trained weights are created by these tests.
"""
import json
import logging
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from torch import nn

from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel, ModelValidationError
from core.output_parser import OutputParser
from core.large_image_segmentation import SEGMENTATION_COLORS
from data.export_manager import ExportError, ExportManager
from ui.main_window import MainWindow


class ConstantSegmenter(nn.Module):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes

    def forward(self, inputs):
        logits = inputs.new_zeros((1, self.classes, 4, 4))
        logits[:, -1] = 5
        return logits


@pytest.fixture(autouse=True)
def one_torch_thread():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


@pytest.fixture
def window(qtbot, tmp_path, monkeypatch):
    warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda parent, title, text: warnings.append(str(text)))
    settings = QSettings(str(tmp_path / 'preferences.ini'), QSettings.IniFormat)
    settings.setValue('export/pngReminderEnabled', False)
    settings.setValue('export/pdfReminderEnabled', False)
    widget = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'not-installed.pth')
    qtbot.addWidget(widget)
    qtbot.wait(1)
    widget.review_warnings = warnings
    return widget


def image_file(path, color='red'):
    Image.new('RGB', (12, 8), color).save(path, format='PNG')
    return path


@pytest.mark.parametrize('classes', [3, 9, 10, 300])
def test_custom_segmentation_preserves_ids_colors_and_counts(tmp_path, classes):
    source = image_file(tmp_path / 'source.png')
    loaded = LoadedModel(ConstantSegmenter(classes), 'module',
                         [f'Tissue {i}' for i in range(classes)], None, 'imagenet')
    result = InferenceEngine('in-memory-only', source, 'segmentation', loaded_model=loaded).run_pipeline()
    assert np.unique(result['mask']).tolist() == [classes - 1]
    assert result['counts'].shape == (classes,)
    assert int(result['counts'][-1]) == 96 and int(result['counts'].sum()) == 96
    color = (SEGMENTATION_COLORS[classes - 1] if classes == 9
             else OutputParser._DEFAULT_COLORS[(classes - 1) % len(OutputParser._DEFAULT_COLORS)])
    assert result['legend_items'] == [(f'Tissue {classes - 1}', color)]
    assert result['color_mask'].getpixel((2, 2)) == color
    assert result['overlay'].convert('RGB').tobytes() == result['color_mask'].tobytes()
    labels_path = tmp_path / 'labels.png'
    Image.fromarray(result['mask']).save(labels_path)
    with Image.open(labels_path) as labels:
        assert np.unique(np.asarray(labels)).tolist() == [classes - 1]


@pytest.mark.parametrize('raw', ['[]', 'null', '7', '{broken'])
def test_corrupt_history_metadata_keeps_current_view_and_blocks_rerun(window, tmp_path, raw):
    source = image_file(tmp_path / 'source.png')
    saved = image_file(tmp_path / 'saved.png', 'blue')
    record_id = window.database_manager.insert_record(str(source), 'builtin', 'classification',
                                                      'NORM', .9, str(saved))
    with window.database_manager._connection() as connection:
        connection.execute('INSERT INTO segmentation_artifacts(record_id, analysis_json) VALUES (?, ?)',
                           (record_id, raw))
    previous = {'previous': 'completed result'}
    window._current_result = previous
    window._show_record_activated(record_id)
    assert window._current_result is previous
    assert window.review_warnings and 'saved analysis' in window.review_warnings[-1].lower()
    window.review_warnings.clear()
    window._handle_rerun_requested(record_id)
    assert window._inference_engine is None
    assert window.review_warnings and 'saved analysis' in window.review_warnings[-1].lower()
    assert len(window.database_manager.get_all_records()) == 1


def test_segmentation_rerun_passes_recorded_parameters(window, tmp_path, monkeypatch):
    source = image_file(tmp_path / 'source.png')
    analysis = {'tile': 512, 'stride': 384, 'input_size': 128, 'preprocess': 'imagenet'}
    record_id = window.database_manager.insert_record(str(source), 'builtin', 'segmentation',
                                                      analysis_metadata=analysis)
    window._builtin_model_statuses['segmentation'] = ('ready', True)
    window._builtin_model_tasks['segmentation'] = 'segmentation'
    monkeypatch.setattr(window, '_set_detected_task', lambda task: None)
    requests = []
    monkeypatch.setattr(window, '_start_inference', lambda *args, **kwargs: requests.append(kwargs) or True)
    window._handle_rerun_requested(record_id)
    assert len(requests) == 1
    assert requests[0]['segmentation_parameters'] == analysis


def test_invalid_recorded_tile_geometry_does_not_fall_back_to_preferences():
    record = {'analysis_json': json.dumps({'mode': 'classification_tiles', 'tile_size': [0, 512]})}
    with pytest.raises(ValueError, match='saved analysis'):
        MainWindow._record_classification_parameters(record)


def test_summary_without_tile_geometry_can_be_read_but_not_rerun():
    record = {'analysis_json': json.dumps({'mode': 'classification_tiles', 'tile_counts': [1, 3]})}
    assert MainWindow._record_classification_parameters(record)['classification_mode'] == 'tiled_analysis'
    with pytest.raises(ValueError, match='saved analysis'):
        MainWindow._record_classification_parameters(record, for_rerun=True)


def test_png_write_failure_preserves_existing_destination(tmp_path, monkeypatch):
    destination = tmp_path / 'existing.png'
    destination.write_bytes(b'previous completed export')

    def fail_after_writing(self, path, **kwargs):
        Path(path).write_bytes(b'incomplete image')
        raise OSError('simulated disk write failure')

    monkeypatch.setattr(Image.Image, 'save', fail_after_writing)
    with pytest.raises(ExportError):
        ExportManager().export_png(Image.new('RGB', (10, 10)), destination)
    assert destination.read_bytes() == b'previous completed export'
    assert sorted(p.name for p in tmp_path.iterdir()) == ['existing.png']


@pytest.mark.parametrize('export_format', ['png', 'pdf'])
@pytest.mark.parametrize('protected', ['original', 'stored_result', 'database', 'model'])
def test_export_cannot_overwrite_analysis_inputs(window, tmp_path, monkeypatch, export_format, protected):
    source = image_file(tmp_path / 'source.png')
    stored = image_file(tmp_path / 'stored.png', 'blue')
    model = tmp_path / 'recorded-model.pth'  # Path identity only; no fake weights file.
    window._current_result = {'original_image_path': str(source), 'result_image_path': str(stored),
                              'metadata': {'task_type': 'classification', 'image_path': str(source),
                                           'model_path': str(model)}}
    paths = {'original': source, 'stored_result': stored, 'database': window.database_manager.db_path, 'model': model}
    destination = paths[protected]
    previous = {p: p.read_bytes() for p in [source, stored, window.database_manager.db_path]}
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *args, **kwargs: (str(destination), ''))
    getattr(window, f'_export_current_{export_format}')()
    if window._pdf_export_worker is not None:
        # A baseline failure must still finish its worker before test teardown.
        window._pdf_export_worker.wait()
    assert window.review_warnings and 'different' in window.review_warnings[-1].lower()
    for path, content in previous.items():
        assert path.read_bytes() == content
    assert not model.exists()


def test_windowed_application_has_persistent_nonduplicated_logging(tmp_path, monkeypatch):
    from utils.logging_setup import configure_logging
    import sys
    monkeypatch.setattr(sys, 'stderr', None)
    logger = logging.Logger('windowed-test')
    try:
        path = configure_logging(tmp_path / 'logs', logger=logger)
        configure_logging(tmp_path / 'logs', logger=logger)
        logger.error('Persistent diagnostic example')
        for handler in logger.handlers:
            handler.flush()
        assert path is not None
        text = Path(path).read_text(encoding='utf-8')
        assert text.count('Persistent diagnostic example') == 1
        assert len(logger.handlers) == 1
    finally:
        for handler in list(logger.handlers):
            handler.close(); logger.removeHandler(handler)


@pytest.mark.parametrize('remaining_use', ['original', 'result'])
def test_deleting_history_keeps_files_used_by_remaining_records(window, tmp_path, remaining_use):
    window.results_dir.mkdir()
    original = image_file(tmp_path / 'source.png')
    shared = image_file(window.results_dir / 'shared.png')
    second = image_file(window.results_dir / 'second.png', 'blue')
    first_id = window.database_manager.insert_record(str(original), 'builtin', 'classification',
                                                     result_image_path=str(shared))
    kept_id = window.database_manager.insert_record(str(shared if remaining_use == 'original' else original),
                                                    'builtin', 'classification',
                                                    result_image_path=str(second if remaining_use == 'original' else shared))
    deleted_record = window.database_manager.get_record_by_id(first_id)
    window.database_manager.delete_records([first_id])
    window._delete_saved_result_images([deleted_record])
    assert shared.is_file()
    assert second.is_file() and original.is_file()
    assert window.database_manager.get_record_by_id(kept_id) is not None


def test_removed_cached_builtin_is_not_used_for_new_inference(window, tmp_path):
    source = image_file(tmp_path / 'source.png')
    window._builtin_model_statuses['classification'] = ('ready', True)
    assert not window._start_inference('', True, str(source), 'classification', 'Running', 'Busy')
    assert window._inference_engine is None
    assert 'no longer exists' in window.statusBar().currentMessage()


@pytest.mark.parametrize('parameters', [
    {'tile': 256, 'stride': 512}, {'input_size': 0}, {'preprocess': 'unknown'},
])
def test_invalid_segmentation_snapshot_is_not_replaced_by_defaults(parameters):
    with pytest.raises(ValueError, match='saved analysis'):
        MainWindow._record_segmentation_parameters({'analysis_json': json.dumps(parameters)})


def test_unknown_single_image_resize_backend_is_rejected(tmp_path):
    loaded = LoadedModel(ConstantSegmenter(3), 'module', None, None, 'imagenet')
    engine = InferenceEngine('in-memory-only', tmp_path / 'unused.png', 'classification',
                             loaded_model=loaded, classification_resize_backend='unrecognised')
    with pytest.raises(ValueError, match='resize backend'):
        engine.run_pipeline()


def test_missing_source_at_result_delivery_keeps_previous_result(window, tmp_path):
    previous = {'previous': 'completed result'}
    window._current_result = previous
    window._accept_inference_result({'task_type': 'classification', 'analysis_mode': 'classification_tiles',
                                     'image_path': str(tmp_path / 'removed.png')})
    assert window._current_result is previous
    assert window.review_warnings and 'image' in window.review_warnings[-1].lower()
    assert window.database_manager.get_all_records() == []


def test_late_cancel_does_not_relabel_accepted_result_as_cancelled(window, monkeypatch):
    from types import SimpleNamespace
    requests = []
    window._inference_engine = SimpleNamespace(cancel=lambda: requests.append('cancel'))
    monkeypatch.setattr(window, '_show_inference_result', lambda result: None)
    try:
        window._accept_inference_result({})
        window._cancel_inference()
        assert not window._cancel_requested
        assert requests == []
    finally:
        window._inference_engine = None


@pytest.mark.parametrize('bad_value', [float('nan'), float('inf')])
def test_nonfinite_segmentation_tile_is_rejected_before_creating_a_map(bad_value):
    from core.large_image_segmentation import predict_large_image

    class NonFiniteOnSecondTile(nn.Module):
        def __init__(self):
            super().__init__()
            self.calls = 0

        def forward(self, inputs):
            self.calls += 1
            logits = inputs.new_zeros((1, 9, inputs.shape[2], inputs.shape[3]))
            if self.calls == 2:
                logits[0, 0, 0, 0] = bad_value
            return logits

    progress = []
    with pytest.raises(ModelValidationError, match='NaN|infinite'):
        predict_large_image(Image.new('RGB', (24, 12)), NonFiniteOnSecondTile(), torch.device('cpu'),
                            tile=12, stride=12, input_size=4,
                            progress_callback=lambda done, total: progress.append((done, total)))
    assert progress == [(1, 2)]
