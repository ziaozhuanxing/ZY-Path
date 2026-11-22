from ui_test_helpers import wait_for_history_idle
"""Real saved artifacts, overlap accounting and background I/O regressions."""
import json
import threading
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from PyQt5.QtCore import QPointF, QSettings, QTimer
from PyQt5.QtWidgets import QMessageBox

from test_audit_source_and_loader import fixtures, infer
from ui_test_helpers import wait_for_model_idle
from core.inference_engine import InferenceEngine
from core.model_loader import ModelLoader
from core.image_budget import validate_raster_budget, PREVIEW_MAX_SIDE
from data.artifact_integrity import verify_saved_artifacts
from data.export_manager import ExportError
from ui.main_window import MainWindow
from ui.input_setup import InputSetupDialog
from ui.inference_panel import InferencePanel


@pytest.fixture
def window(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    w = MainWindow(settings=QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat),
                   db_path=tmp_path / 'db.sqlite', results_dir=tmp_path / 'results')
    qtbot.addWidget(w)
    w.warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: w.warnings.append(str(args[-1])))
    return w


@pytest.mark.parametrize('role', ['result', 'colors', 'metadata'])
def test_replaced_artifact_blocks_history_and_export_without_deleting_record(window, qtbot, tmp_path, role):
    model, source, loaded = fixtures(tmp_path)
    assert window._show_inference_result(infer(model, source, loaded))
    record_id = window.current_record_id
    metadata = window._current_result['metadata']
    analysis = metadata['classification_analysis']
    path = Path(analysis['artifact_manifest']['files'][role]['path'])
    if role == 'metadata':
        path.write_text('{}')
    else:
        Image.new('RGB', (16, 16), 'cyan').save(path)
    assert not window._validate_export_sources(include_original=False)
    destination = tmp_path / 'invalid.pdf'
    with pytest.raises(ExportError, match='could not be created'):
        window.export_manager.export_pdf(destination, source, window._current_result['result_image_path'], metadata)
    assert not destination.exists()
    window._show_record_activated(record_id)
    wait_for_history_idle(qtbot, window)
    assert window._current_result is None
    assert window.result_panel.tile_page.analysis is None
    assert window.database_manager.get_record_by_id(record_id) is not None
    assert any('has changed' in warning for warning in window.warnings)


def test_legacy_history_is_kept_and_explicitly_marked_unverified(window, qtbot, tmp_path):
    model, source, loaded = fixtures(tmp_path)
    assert window._show_inference_result(infer(model, source, loaded))
    record_id = window.current_record_id
    analysis = dict(window._current_result['metadata']['classification_analysis'])
    analysis.pop('artifact_manifest')
    window.database_manager.update_analysis_metadata(record_id, analysis)
    window._show_record_activated(record_id)
    wait_for_history_idle(qtbot, window)
    assert window.result_panel.tile_page.analysis is not None
    assert 'integrity was not recorded' in window.statusBar().currentMessage()
    assert verify_saved_artifacts(analysis) is False


def test_cover_borders_keeps_full_fields_and_counts_every_pixel_once(window, tmp_path):
    model, source, loaded = fixtures(tmp_path, size=(21, 19))
    result = infer(model, source, loaded, {'match_scale': True, 'manual_mpp': [.5, .5], 'cover_borders': True})
    analysis = result['classification_analysis']
    assert analysis['edge_policy'] == 'cover'
    assert analysis['input_profile']['edge_policy'] == 'skip'  # Model contract unchanged.
    assert len(analysis['tiles']) == 9
    owners = np.zeros((19, 21), np.uint8)
    for tile in analysis['tiles']:
        x0, y0, x1, y1 = tile['box']
        assert (x1 - x0, y1 - y0) == (8, 8)
        ax, ay, bx, by = tile['area_box']
        assert x0 <= ax < bx <= x1 and y0 <= ay < by <= y1
        owners[ay:by, ax:bx] += 1
    assert np.all(owners == 1)
    assert sum(analysis['pixel_counts']) == 21 * 19
    assert sum(analysis['area_ratios']) == pytest.approx(1)
    assert analysis['unanalysed_pixels'] == 0
    assert window._show_inference_result(result)
    page = window.result_panel.tile_page
    assert 'Analysed: 100.00%' in page.coverage_label.text()
    for y in range(19):
        for x in range(21):
            assert page.tile_at_source(QPointF(x + .5, y + .5)) is not None
    page = window.result_panel.tile_page
    page.inspect_tile(8)
    assert page.table.item(8, 1).text() == str(analysis['tiles'][8]['box'])
    assert '8 x 8 px' in page.tile_inspection_text.text()
    record = window.database_manager.get_record_by_id(window.current_record_id)
    saved = json.loads(record['analysis_json'])
    replay = infer(model, source, loaded, {'recorded_input_profile': saved['input_profile'],
        'recorded_spatial_context': saved['spatial_context']})['classification_analysis']
    assert replay['tiles'] == analysis['tiles']
    assert replay['pixel_counts'] == analysis['pixel_counts']


def test_border_choice_rejects_too_small_image_without_stretching(tmp_path):
    model, source, loaded = fixtures(tmp_path, size=(7, 7))
    with pytest.raises(ValueError, match='No complete model field'):
        infer(model, source, loaded, {'match_scale': True, 'manual_mpp': [.5, .5], 'cover_borders': True})


def test_reject_large_raster_before_decoder_allocation(monkeypatch):
    import core.classification_input as reader
    monkeypatch.setattr(reader, 'decoded_image_size', lambda *args: (12000, 12000))
    monkeypatch.setattr('cv2.imread', lambda *args: pytest.fail('Oversize image must not decode'))
    with pytest.raises(ValueError, match='native-resolution region'):
        reader.load_rgb_image('unused.png', 'opencv_color')
    assert validate_raster_budget((5000, 5000)) > 0


def test_thumbnail_does_not_change_calibration_or_sampling_geometry(qtbot, tmp_path):
    source = tmp_path / 'large.png'
    Image.new('RGB', (3000, 1000), (120, 80, 50)).save(source)
    panel = InferencePanel()
    qtbot.addWidget(panel)
    from core.model_profile import known_profile, CRC_SHA256
    panel.set_active_input_profile(known_profile(CRC_SHA256))
    panel.set_classification_mode('tiled_analysis')
    panel.set_image(str(source))
    assert panel._source_pixmap.width() == PREVIEW_MAX_SIDE
    assert panel.source_image_size() == (3000, 1000)
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    assert dialog.preview.count == 14 * 5
    assert dialog.diagram.region_rect.width() / dialog.diagram.source_rect.width() == pytest.approx(224 / 3000)


def test_background_image_load_ignores_replaced_selection_and_keeps_ui_alive(qtbot, tmp_path, monkeypatch):
    from ui import image_load_worker
    first, second = tmp_path / 'first.png', tmp_path / 'second.png'
    Image.new('RGB', (32, 32), 'red').save(first)
    Image.new('RGB', (48, 24), 'blue').save(second)
    panel = InferencePanel()
    qtbot.addWidget(panel)
    original = image_load_worker.load_verified_image
    entered, release = threading.Event(), threading.Event()
    def delayed(path, **kwargs):
        if Path(path) == first:
            entered.set()
            assert release.wait(5)
        return original(path, **kwargs)
    monkeypatch.setattr(image_load_worker, 'load_verified_image', delayed)
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(True))
    timer.start(1)
    try:
        panel.load_image_async(str(first))
        qtbot.waitUntil(entered.is_set)
        assert not panel.run_button.isEnabled()
        qtbot.waitUntil(lambda: len(ticks) >= 3)
        panel.load_image_async(str(second))
    finally:
        release.set()
    qtbot.waitUntil(lambda: not panel.image_loading(), timeout=10000)
    timer.stop()
    assert panel._image_path == str(second)
    assert panel.source_image_size() == (48, 24)
    assert panel._source_pixmap.toImage().pixelColor(0, 0).blue() == 255


def test_normal_pipeline_saves_on_worker_and_cancel_rolls_back(window, qtbot, tmp_path, monkeypatch):
    model, source, _ = fixtures(tmp_path)
    panel = window.inference_panel
    panel.set_custom_model(str(model))
    wait_for_model_idle(qtbot, window)
    panel.set_image(str(source))
    panel.set_classification_mode('tiled_analysis')
    window.settings.setValue('classificationTiles/width', 8)
    window.settings.setValue('classificationTiles/height', 8)
    window._refresh_classification_parameters()
    entered, release = threading.Event(), threading.Event()
    identities = []
    main_thread = threading.get_ident()
    real_export = window.export_manager.export_png
    def paused_export(*args):
        identities.append(threading.get_ident())
        entered.set()
        assert release.wait(5)
        return real_export(*args)
    monkeypatch.setattr(window.export_manager, 'export_png', paused_export)
    assert panel.run_button.isEnabled(), (panel._running, panel._model_ready, panel._image_path, panel._custom_model_path, panel._matched_run_problem, panel.run_button.isEnabledTo(window), panel.run_button.toolTip())
    panel.run_button.click()
    assert window._inference_engine is not None, window.statusBar().currentMessage()
    try:
        qtbot.waitUntil(entered.is_set, timeout=10000)
        assert identities == [identities[0]] and identities[0] != main_thread
        assert window.database_manager.get_all_records() == []
        window._cancel_inference()
    finally:
        release.set()
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    assert window.database_manager.get_all_records() == []
    assert list(window.results_dir.iterdir()) == []


def test_cover_preview_reports_real_count_without_changing_model_contract(qtbot, tmp_path):
    from test_guided_input_setup import panel_image
    panel, _ = panel_image(qtbot, tmp_path, size=(2035, 1061), mpp=[.3, .3])
    panel.set_classification_mode('tiled_analysis')
    dialog = InputSetupDialog(panel, prefer_matching=True)
    qtbot.addWidget(dialog)
    dialog.show()
    assert dialog.preview.count == 10
    assert dialog.cover_borders.isHidden()
    dialog.edge_toggle.click()
    assert dialog.cover_borders.isVisible()
    dialog.cover_borders.click()
    dialog.edge_toggle.click()
    assert dialog.cover_borders.isHidden()
    assert dialog.preview.tile == (373, 373)
    assert dialog.preview.count == 18
    assert dialog.choices()['cover_borders'] is True
    assert panel._active_input_profile.edge_policy == 'skip'
    dialog.reject()
    assert panel._cover_borders is False


def test_segmentation_labels_are_checked_as_well_as_display_images(window, tmp_path):
    from test_model_sampling_transition import model_file
    model = model_file(tmp_path, 'segmenter', task='segmentation')
    source = tmp_path / 'source.png'
    Image.new('RGB', (24, 24), (120, 80, 50)).save(source)
    result = InferenceEngine(model, source, 'segmentation').run_pipeline()
    assert window._show_inference_result(result)
    analysis = window._current_result['metadata']['segmentation_analysis']
    labels = Path(analysis['artifact_manifest']['files']['labels']['path'])
    Image.new('L', (24, 24), 2).save(labels)
    assert not window._validate_export_sources(include_original=False)
    assert 'labels' in window.warnings[-1]


def test_closing_during_image_decode_waits_without_blocking_gui(window, qtbot, tmp_path, monkeypatch):
    from ui import image_load_worker
    source = tmp_path / 'source.png'
    Image.new('RGB', (32, 32), 'red').save(source)
    real_load = image_load_worker.load_verified_image
    entered, release = threading.Event(), threading.Event()
    def paused_load(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return real_load(*args, **kwargs)
    monkeypatch.setattr(image_load_worker, 'load_verified_image', paused_load)
    window.show()
    window.inference_panel.load_image_async(str(source))
    try:
        qtbot.waitUntil(entered.is_set)
        window.close()
        assert window.isVisible()
        assert window._close_requested
    finally:
        release.set()
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=10000)
    assert not window.inference_panel.image_loading()


def test_border_option_is_transactional_and_preview_matches_execution(qtbot, tmp_path):
    from test_guided_input_setup import panel_image
    panel, _ = panel_image(qtbot, tmp_path, size=(2035, 1061), mpp=[.3, .3])
    dialog = InputSetupDialog(panel, prefer_matching=True)
    qtbot.addWidget(dialog)
    assert dialog.preview.tile == (373, 373)
    assert dialog.preview.count == 10
    dialog.cover_borders.setChecked(True)
    assert dialog.preview.count == 18
    assert dialog.preview.tile == (373, 373)
    assert dialog.choices()['cover_borders']
    dialog.reject()
    assert not panel._cover_borders
