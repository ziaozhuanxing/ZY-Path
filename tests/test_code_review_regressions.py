"""Regressions for model compatibility, result persistence and workload safety.

Models below are synthetic fixtures; no trained weights or model metrics are used.
"""
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QDate, QSettings
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QMessageBox
from torch import nn

import core.classification_tiles as tiles_module
from core.classification_tiles import (
    CLASSIFICATION_LABELS, MAX_CLASSIFICATION_TILES, ClassificationTileSpec,
    exploratory_metadata, predict_classification_tiles, validate_classification_workload,
)
from core.inference_engine import InferenceEngine, ModelValidationThread
from core.model_loader import LoadedModel, ModelLoader, ModelValidationError
from core.output_parser import OutputParser
from data.database_manager import DatabaseError
from data.export_manager import ExportError
from ui.classification_result import ClassificationResult
from ui.main_window import MainWindow
from ui.model_settings import ModelSettingsPage, default_model_key


class FixtureLogits(nn.Module):
    def __init__(self, channels=3, segmentation=False, value=2.):
        super().__init__()
        self.channels, self.segmentation, self.value = channels, segmentation, value
        self.calls = 0

    def forward(self, image):
        self.calls += 1
        shape = (1, self.channels, 2, 2) if self.segmentation else (1, self.channels)
        return torch.full(shape, self.value)


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
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Yes)
    widget = MainWindow(db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results',
                        builtin_model_path=tmp_path / 'not-installed.pth',
                        settings=QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat))
    qtbot.addWidget(widget)
    qtbot.waitUntil(lambda: widget._builtin_model_status is not None)
    widget.review_warnings = warnings
    return widget


def fixture_result(tmp_path, kind='single'):
    path = tmp_path / 'source.png'
    Image.new('RGB', (12, 8), (100, 110, 120)).save(path)
    classes = list(CLASSIFICATION_LABELS) if kind == 'tiled' else ['A', 'B', 'C']
    loaded = LoadedModel(FixtureLogits(len(classes), kind == 'segmentation'),
                         'module', classes, None, 'raw255')
    return InferenceEngine('synthetic-model-only', path,
                           'segmentation' if kind == 'segmentation' else 'classification',
                           loaded_model=loaded, classification_mode='tiled_analysis' if kind == 'tiled' else 'single_image',
                           classification_tile_metadata=exploratory_metadata(5, 3) if kind == 'tiled' else None).run_pipeline()


@pytest.mark.parametrize('logit', [-20., 0., 20.])
def test_single_logit_cannot_become_a_certain_class(logit):
    with pytest.raises(ModelValidationError, match='at least two'):
        ModelLoader.validate_loaded(LoadedModel(FixtureLogits(1, value=logit), 'module', ['Positive'], None, None))
    with pytest.raises(ValueError, match='Single-logit'):
        OutputParser.parse_classification(torch.tensor([[logit]]), ['Positive'])


@pytest.mark.parametrize('segmentation', [False, True])
def test_label_mismatch_rejected_by_validation_worker_and_pipeline(tmp_path, monkeypatch, segmentation):
    loaded = LoadedModel(FixtureLogits(3, segmentation), 'checkpoint', ['Wrong count'], None, 'imagenet')
    monkeypatch.setattr(ModelLoader, 'load_with_info', lambda self, path: loaded)
    with pytest.raises(ModelValidationError, match='1 class labels but outputs 3'):
        ModelLoader.validate_loaded(loaded)
    worker = ModelValidationThread('in-memory-only')
    ready, errors = QSignalSpy(worker.validation_ready), QSignalSpy(worker.validation_error)
    worker.run()
    assert len(ready) == 0 and len(errors) == 1
    assert 'class labels' in errors[0][0]
    with pytest.raises(ModelValidationError, match='class labels'):
        InferenceEngine('in-memory-only', tmp_path / 'unused.png',
                        'segmentation' if segmentation else 'classification', loaded_model=loaded).run_pipeline()


def test_incompatible_checkpoint_cannot_replace_saved_default(qtbot, tmp_path, monkeypatch):
    # Load a supported checkpoint through the actual loader, not a mocked validator.
    from torchvision.models import resnet18
    model_file = tmp_path / 'mismatched.pth'
    torch.save({'arch': 'resnet18', 'num_classes': 2, 'state_dict': resnet18(num_classes=2).state_dict(),
                'classes': ['Only one'], 'preprocess': 'imagenet'}, model_file)
    settings = QSettings(str(tmp_path / 'defaults.ini'), QSettings.IniFormat)
    settings.setValue(default_model_key('classification'), 'previous-default.pth')
    page = ModelSettingsPage(settings, {'classification': 'builtin-c', 'segmentation': 'builtin-s'})
    qtbot.addWidget(page)
    changed = QSignalSpy(page.default_changed)
    page.rows['classification']['path'].setText(str(model_file))
    page.validate_default('classification')
    qtbot.waitUntil(lambda: not page.is_validating, timeout=10000)
    assert settings.value(default_model_key('classification')) == 'previous-default.pth'
    assert len(changed) == 0
    assert 'class labels' in page.rows['classification']['status'].text()


@pytest.mark.parametrize('classes', [None, ['A', 'B', 'C']])
def test_compatible_labels_keep_existing_softmax_results(classes):
    model = FixtureLogits(3)
    loaded = LoadedModel(model, 'module', classes, None, None)
    validation = ModelLoader.validate_loaded(loaded)
    assert validation.num_classes == 3 and model.calls == 1
    result = OutputParser.parse_classification(model(torch.empty(0)), classes or ['Class 0', 'Class 1', 'Class 2'])
    assert result['confidence'] == pytest.approx(1 / 3)
    assert result['probabilities'] == pytest.approx([1 / 3] * 3)


@pytest.mark.parametrize(('kind', 'stage'), [
    ('single', 'png'), ('single', 'database'),
    ('tiled', 'png'), ('tiled', '_classes.png'), ('tiled', '.json'), ('tiled', 'database'),
    ('segmentation', 'png'), ('segmentation', '_labels.png'), ('segmentation', '_mask.png'),
    ('segmentation', '_overlay.png'), ('segmentation', '.json'), ('segmentation', 'database'),
])
def test_partial_save_keeps_previous_result_without_incomplete_history(window, tmp_path, monkeypatch, kind, stage):
    window._accept_inference_result(fixture_result(tmp_path))
    previous = window._current_result
    previous_id = window.current_record_id
    previous_label = window.result_panel.classification_label.text()
    files_before = set(window.results_dir.iterdir())
    record_before = window.database_manager.get_all_records()
    incoming = fixture_result(tmp_path, kind)
    if stage == 'png':
        def fail_png(image, path):
            Path(path).write_bytes(b'partial image')
            raise ExportError('injected storage failure')
        monkeypatch.setattr(window.export_manager, 'export_png', fail_png)
    elif stage == 'database':
        def fail_insert(*args, **kwargs):
            raise DatabaseError('injected database failure')
        monkeypatch.setattr(window.database_manager, 'insert_record', fail_insert)
    elif stage == '.json':
        original_write = Path.write_text
        def fail_json(path, data, *args, **kwargs):
            if path.suffix == '.json' and path.parent == window.results_dir:
                path.write_bytes(b'partial metadata')
                raise OSError('injected metadata failure')
            return original_write(path, data, *args, **kwargs)
        monkeypatch.setattr(Path, 'write_text', fail_json)
    else:
        original_save = Image.Image.save
        def fail_image(image, path, *args, **kwargs):
            if str(path).endswith(stage):
                Path(path).write_bytes(b'partial artifact')
                raise OSError('injected artifact failure')
            return original_save(image, path, *args, **kwargs)
        monkeypatch.setattr(Image.Image, 'save', fail_image)
    window._inference_result_accepted = False
    window._accept_inference_result(incoming)
    assert window._inference_result_accepted is False
    assert window.database_manager.get_all_records() == record_before
    assert set(window.results_dir.iterdir()) == files_before
    assert window.current_record_id == previous_id and window._current_result is previous
    assert window.result_panel.classification_label.text() == previous_label
    assert 'no history record was added' in window.review_warnings[-1]


def test_filename_collision_keeps_existing_files(window, tmp_path, monkeypatch):
    window.results_dir.mkdir()
    occupied = window.results_dir / 'occupied.png'
    occupied.write_bytes(b'previous data')
    monkeypatch.setattr(window, '_new_result_path', lambda timestamp: occupied)
    window._accept_inference_result(fixture_result(tmp_path))
    assert occupied.read_bytes() == b'previous data'
    assert window.database_manager.get_all_records() == []
    assert not window._inference_result_accepted


def test_history_refresh_failure_does_not_remove_a_committed_result(window, tmp_path, monkeypatch):
    get_records = window.database_manager.get_all_records
    def unavailable():
        raise DatabaseError('injected refresh failure')
    monkeypatch.setattr(window.database_manager, 'get_all_records', unavailable)
    window._accept_inference_result(fixture_result(tmp_path, 'tiled'))
    record = get_records()[0]
    assert window._inference_result_accepted and window.current_record_id == record['id']
    assert Path(record['result_image_path']).is_file()
    assert Path(record['result_color_mask_path']).is_file()
    assert Path(record['result_image_path']).with_suffix('.json').is_file()
    assert 'Result saved' in window.statusBar().currentMessage()


@pytest.mark.parametrize('kind', ['tiled', 'segmentation'])
def test_deleting_spatial_result_removes_all_managed_files(window, tmp_path, kind):
    source = fixture_result(tmp_path, kind)
    window._accept_inference_result(source)
    record_id = window.current_record_id
    assert any(p.suffix == '.json' for p in window.results_dir.iterdir())
    window._confirm_delete_records([record_id])
    assert window.database_manager.get_all_records() == []
    assert list(window.results_dir.iterdir()) == []
    assert Path(source['image_path']).is_file()


@pytest.mark.parametrize('reference', ['source', 'shared_result', 'active_input', 'outside'])
def test_deletion_protects_referenced_and_external_files(window, tmp_path, reference):
    window._accept_inference_result(fixture_result(tmp_path, 'tiled'))
    deleted = window.database_manager.get_record_by_id(window.current_record_id)
    png = Path(deleted['result_image_path'])
    sidecar = png.with_suffix('.json')
    if reference == 'source':
        window.database_manager.insert_record(str(sidecar), 'model', 'classification')
    elif reference == 'shared_result':
        window.database_manager.insert_record(str(tmp_path / 'other.png'), 'model', 'classification', result_image_path=str(png))
    elif reference == 'active_input':
        window.inference_panel._image_path = str(sidecar)
    else:
        external = tmp_path / 'user-export.png'
        external.write_bytes(b'user export')
        external.with_suffix('.json').write_text('user metadata')
        deleted['result_image_path'] = str(external)
    window.database_manager.delete_records([deleted['id']])
    window._delete_saved_result_images([deleted])
    if reference == 'outside':
        assert external.read_bytes() == b'user export'
        assert external.with_suffix('.json').read_text() == 'user metadata'
    else:
        assert sidecar.is_file()
        assert png.exists() is (reference == 'shared_result')


def test_history_includes_entire_last_second_and_preserves_bounds_on_reload(window):
    target = date(2026, 10, 19)
    local_midnight = datetime.combine(target, time.min).astimezone()
    times = [local_midnight - timedelta(microseconds=1), local_midnight,
             datetime.combine(target, time.max).astimezone() - timedelta(microseconds=499999),
             datetime.combine(target, time.max).astimezone(), local_midnight + timedelta(days=1)]
    ids = [window.database_manager.insert_record('source', 'model', 'classification') for _ in times]
    with window.database_manager._connection() as connection:
        for record_id, timestamp in zip(ids, times):
            connection.execute('UPDATE inference_records SET timestamp=? WHERE id=?',
                               (timestamp.astimezone(timezone.utc).isoformat(timespec='microseconds'), record_id))
    panel = window.history_panel
    panel.date_filter_checkbox.setChecked(True)
    panel.from_date_edit.setDate(QDate(target.year, target.month, target.day))
    panel.to_date_edit.setDate(panel.from_date_edit.date())
    spy = QSignalSpy(panel.search_requested)
    panel.search_button.click()
    bounds = spy[-1]
    assert datetime.fromisoformat(bounds[2]).microsecond == 999999
    expected = set(ids[1:4])
    assert {r['id'] for r in window.database_manager.search('', start=bounds[1], end=bounds[2])} == expected
    window._reload_history_with_current_filters()
    assert set(panel.selected_record_ids()) == set()
    assert panel.table.rowCount() == len(expected)
    assert {int(panel.table.item(row, 0).text()) for row in range(panel.table.rowCount())} == expected


@pytest.mark.parametrize(('day', 'zone_name', 'utc_start_hour', 'day_hours'), [
    (date(2026, 3, 8), 'EST5EDT,M3.2.0/2,M11.1.0/2', 5, 23),
    (date(2026, 11, 1), 'EST5EDT,M3.2.0/2,M11.1.0/2', 4, 25),
    (date(2026, 10, 19), 'MYT-8', 16, 24),
])
def test_date_bounds_keep_precision_across_offsets_and_dst(day, zone_name, utc_start_hour, day_hours):
    from dateutil.tz import tzstr
    from ui.history_panel import HistoryPanel
    zone = tzstr(zone_name)
    # An aware time supplies an explicit local zone on every OS; no global TZ
    # change or platform-specific timezone database is required by this test.
    start = datetime.fromisoformat(HistoryPanel._local_date_to_utc_iso(day, time.min.replace(tzinfo=zone)))
    end = datetime.fromisoformat(HistoryPanel._local_date_to_utc_iso(day, time.max.replace(tzinfo=zone)))
    assert start.utcoffset() == timedelta(0) and start.hour == utc_start_hour
    assert start.date() == (day - timedelta(days=1) if zone_name == 'MYT-8' else day)
    assert end - start + timedelta(microseconds=1) == timedelta(hours=day_hours)
    assert end.microsecond == 999999


def test_tile_limit_is_checked_before_map_allocation_or_model_call(monkeypatch):
    image = Image.new('RGB', (101, 101))
    spec = ClassificationTileSpec.from_metadata(exploratory_metadata(1, 1), list(CLASSIFICATION_LABELS), 'raw255')
    model = FixtureLogits(9)
    allocations = []
    monkeypatch.setattr(tiles_module.np, 'zeros', lambda *args, **kwargs: allocations.append(args))
    with pytest.raises(ValueError, match='10,201 tiles'):
        predict_classification_tiles(image, model, spec)
    assert allocations == [] and model.calls == 0
    assert validate_classification_workload((100, 100), (1, 1)) == MAX_CLASSIFICATION_TILES
    assert validate_classification_workload((5000, 5000), (512, 512)) == 100
    with pytest.raises(ValueError, match='25,000,000'):
        validate_classification_workload((5000, 5000), (1, 1))


def test_worker_blocks_excessive_request_before_loading_model(tmp_path, monkeypatch):
    path = tmp_path / 'image.png'
    Image.new('RGB', (101, 101)).save(path)
    def unexpected_load(*args):
        pytest.fail('An unsafe request must not load the model')
    monkeypatch.setattr(ModelLoader, 'load_with_info', unexpected_load)
    with pytest.raises(ValueError, match='Increase the tile width'):
        InferenceEngine('unused', path, 'classification', classification_mode='tiled_analysis',
                        classification_tile_metadata=exploratory_metadata(1, 1)).run_pipeline()


def test_checkpoint_tile_budget_is_checked_before_decoding_image(tmp_path, monkeypatch):
    path = tmp_path / 'image.png'
    Image.new('RGB', (101, 101)).save(path)
    model = FixtureLogits(9)
    loaded = LoadedModel(model, 'checkpoint', list(CLASSIFICATION_LABELS), None, 'raw255',
                         classification_tiles=exploratory_metadata(1, 1))
    def unexpected_decode(*args, **kwargs):
        pytest.fail('An unsafe checkpoint geometry must not decode the full image')
    monkeypatch.setattr(Image.Image, 'convert', unexpected_decode)
    with pytest.raises(ValueError, match='Increase the tile width'):
        InferenceEngine('in-memory-only', path, 'classification', loaded_model=loaded,
                        classification_mode='tiled_analysis').run_pipeline()
    assert model.calls == 1  # Output validation only; no classification crop ran.


def test_gui_blocks_excessive_request_without_changing_preferences_or_starting_worker(window, tmp_path, virtual_model_resources):
    path = tmp_path / 'image.png'
    Image.new('RGB', (101, 101)).save(path)
    virtual_model_resources.add(window.builtin_model_paths['classification'])
    window._builtin_model_statuses['classification'] = ('Ready', True)
    window.settings.setValue('classificationTiles/width', 1)
    window.settings.setValue('classificationTiles/height', 1)
    parameters = {'tile_size': [1, 1], 'classification_mode': 'tiled_analysis'}
    assert not window._start_inference('', True, str(path), 'classification', 'Running', 'Busy', parameters)
    assert window._inference_engine is None and not window._cancel_requested
    assert window.settings.value('classificationTiles/width', type=int) == 1
    assert window.settings.value('classificationTiles/height', type=int) == 1
    assert '10,201 tiles' in window.review_warnings[-1]


def test_oversized_stored_tile_table_rejected_before_view_changes(qtbot):
    page = ClassificationResult()
    qtbot.addWidget(page)
    with pytest.raises(ValueError, match='limit'):
        page.show_result(None, None, {'tiles': [None] * (MAX_CLASSIFICATION_TILES + 1)})
    assert page.table.rowCount() == 0 and page.analysis is None
