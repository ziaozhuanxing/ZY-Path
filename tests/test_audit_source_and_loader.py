"""Regression coverage for source identity, scale binding, restricted loading and skip edges."""
from ui_test_helpers import wait_for_history_idle
import json
from pathlib import Path
import pytest
import torch
from torch import nn
from PIL import Image
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox
from core.model_profile import ModelInputProfile, SCHEMA, file_sha256
from core.model_loader import ModelLoader, ModelValidationError
from core.inference_engine import InferenceEngine
from core.classification_tiles import ClassificationWorkloadError
from ui.main_window import MainWindow


class Mean(nn.Module):
    def forward(self, x):
        return x.mean((2, 3))


@pytest.fixture
def window(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    monkeypatch.setenv('APPDATA', str(tmp_path / 'appdata'))
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path / 'settings'))
    w = MainWindow(settings=QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat),
                   db_path=tmp_path / 'history.sqlite', results_dir=tmp_path / 'results')
    qtbot.addWidget(w)
    w.audit_warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: w.audit_warnings.append(args[2]))
    return w


def fixtures(tmp_path, size=(16, 16), tile=8):
    model = tmp_path / 'fixture.pt'
    torch.jit.trace(Mean(), torch.zeros(1, 3, 8, 8)).save(str(model))
    profile = ModelInputProfile.from_dict({
        'schema': SCHEMA, 'model_sha256': file_sha256(model),
        'task_type': 'classification', 'classes': ['A', 'B', 'C'],
        'input_size': [8, 8], 'normalization': 'raw255', 'input_scope': 'patch',
        'field_um': [tile / 2, tile / 2], 'tile_size': [tile, tile], 'stride': [tile, tile],
        'image_decoder': 'opencv_color', 'resize_backend': 'opencv_linear',
        'edge_policy': 'skip', 'pixel_edge_policy': 'skip'})
    model.with_name(model.name + '.zypath-model.json').write_text(json.dumps(profile.to_dict()))
    source = tmp_path / 'source.png'
    Image.new('RGB', size, (180, 30, 50)).save(source)
    loaded = ModelLoader().load_with_info(model)
    assert loaded.input_profile == profile
    return model, source, loaded


def infer(model, source, loaded, options=None):
    return InferenceEngine(model, source, 'classification', loaded_model=loaded,
        classification_mode='tiled_analysis', input_options=options or {}).run_pipeline()


def test_changed_original_keeps_stored_result_but_blocks_overlay_and_pdf(window, qtbot, tmp_path):
    model, source, loaded = fixtures(tmp_path)
    result = infer(model, source, loaded)
    original_hash = file_sha256(source)
    assert window._show_inference_result(result)
    record_id = window.current_record_id
    Image.new('RGB', (16, 16), (10, 20, 230)).save(source)
    window._show_record_activated(record_id)
    wait_for_history_idle(qtbot, window)
    assert window.result_panel.tile_page.analysis is None
    assert not window._validate_export_sources(include_original=True)
    assert window._validate_export_sources(include_original=False)
    assert 'stored result only' in window.statusBar().currentMessage()
    current = window._current_result
    destination = tmp_path / 'changed-source-report.pdf'
    from data.export_manager import ExportError
    with pytest.raises(ExportError):
        window.export_manager.export_pdf(destination, source, current['result_image_path'], current['metadata'])
    assert not destination.exists()


def test_skip_result_at_limit_is_saved_after_successful_inference(window, tmp_path, monkeypatch):
    import core.classification_tiles as tiles
    assert tiles.validate_classification_workload((1001, 1001), (10, 10), 'skip') == 10000
    with pytest.raises(ClassificationWorkloadError):
        tiles.validate_classification_workload((1001, 1001), (10, 10))
    # The same production mismatch is 1001x1001 / 10: 10,000 actual vs 10,201 ceil.
    monkeypatch.setattr(tiles, 'MAX_CLASSIFICATION_TILES', 100)
    model, source, loaded = fixtures(tmp_path, size=(21, 21), tile=2)
    result = infer(model, source, loaded, {'match_scale': True, 'manual_mpp': [.5, .5]})
    assert len(result['classification_analysis']['tiles']) == 100
    assert result['classification_analysis']['edge_policy'] == 'skip'
    assert window._show_inference_result(result)
    assert window.current_record_id is not None


def test_source_replacement_requires_new_scale_confirmation(window, tmp_path):
    model, source, loaded = fixtures(tmp_path)
    panel = window.inference_panel
    panel.set_active_input_profile(loaded.input_profile)
    panel.set_image(str(source))
    panel._manual_mpp = (.5, .5)
    panel._manual_mpp_decoder = 'opencv_color'
    panel._refresh_scale_information()
    panel.match_scale_checkbox.setChecked(True)
    assert panel.input_options()['match_scale']
    # External editor doubles resolution while the loaded preview/calibration stays unchanged.
    Image.new('RGB', (32, 32), (180, 30, 50)).save(source)
    with pytest.raises(ValueError, match='original image has changed'):
        infer(model, source, loaded, panel.input_options())
    panel.set_image(str(source))
    assert panel.input_options()['manual_mpp'] is None
    assert not panel.input_options()['match_scale']
    assert panel._source_pixmap.width() == 32


@pytest.mark.parametrize('modern_archive', [True, False])
def test_restricted_loader_never_executes_pickle_marker(tmp_path, modern_archive):
    marker = tmp_path / 'audit-benign-marker.txt'
    class BenignMarker:
        def __reduce__(self):
            return (Path.write_text, (marker, 'audit fixture executed'))
    path = tmp_path / 'untrusted-fixture.pth'
    torch.save(BenignMarker(), path, _use_new_zipfile_serialization=modern_archive)
    assert not marker.exists()
    with pytest.raises(ModelValidationError):
        ModelLoader().load_with_info(path)
    assert not marker.exists()


def test_unchanged_source_restores_overlay_and_exports_verified_pdf(window, qtbot, tmp_path):
    model, source, loaded = fixtures(tmp_path)
    assert window._show_inference_result(infer(model, source, loaded))
    window._show_record_activated(window.current_record_id)
    wait_for_history_idle(qtbot, window)
    assert window.result_panel.tile_page.analysis is not None
    assert window._validate_export_sources(include_original=True)
    current = window._current_result
    destination = tmp_path / 'verified.pdf'
    window.export_manager.export_pdf(destination, source, current['result_image_path'], current['metadata'])
    assert destination.is_file()


def test_same_stat_replacement_clears_manual_mpp_on_reload(window, tmp_path):
    import os
    _, source, loaded = fixtures(tmp_path)
    panel = window.inference_panel
    panel.set_active_input_profile(loaded.input_profile)
    # BMP's fixed-size pixels let this test preserve size and timestamp.
    source = source.with_suffix('.bmp')
    Image.new('RGB', (16, 16), (180, 30, 50)).save(source)
    panel.set_image(str(source))
    panel._manual_mpp = (.5, .5)
    panel._refresh_scale_information()
    panel.match_scale_checkbox.setChecked(True)
    stat = source.stat()
    Image.new('RGB', (16, 16), (10, 20, 230)).save(source)
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert source.stat().st_size == stat.st_size
    with pytest.raises(ValueError, match='changed'):
        from core.image_source import verify_image_source
        verify_image_source(source, panel.input_options()['expected_image_identity'])
    panel.set_image(str(source))
    assert panel.input_options()['manual_mpp'] is None
