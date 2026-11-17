"""Model selection must publish its input contract before the first Run."""
from ui_test_helpers import wait_for_model_idle
import json
import threading

from PIL import Image
import pytest
import torch
from torch import nn
from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import QMessageBox

from core.model_profile import SCHEMA, file_sha256
from core.model_loader import ModelLoader, ModelValidationError
from ui.main_window import MainWindow
from ui.theme import apply_theme


class MeanClassifier(nn.Module):
    def forward(self, image):
        return image.mean((2, 3))


class TinySegmenter(nn.Module):
    def forward(self, image):
        return image


def model_file(tmp_path, name, *, field=4, decoder='opencv_color', task='classification'):
    path = tmp_path / (name + '.pt')
    torch.jit.script(MeanClassifier() if task == 'classification' else TinySegmenter()).save(str(path))
    data = {'schema': SCHEMA, 'model_sha256': file_sha256(path), 'task_type': task,
        'classes': ['A', 'B', 'C'], 'input_size': [8, 8], 'normalization': 'raw255',
        'image_decoder': decoder, 'resize_backend': 'opencv_linear', 'input_scope': 'patch',
        'field_um': [field, field] if field else None, 'tile_size': [8, 8], 'stride': [8, 8],
        'edge_policy': 'skip', 'pixel_edge_policy': 'skip'}
    path.with_name(path.name + '.zypath-model.json').write_text(json.dumps(data))
    return path


@pytest.fixture
def window(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat)
    settings.setValue('classification/defaultMode', 'tiled_analysis')
    settings.setValue('classificationTiles/width', 8)
    settings.setValue('classificationTiles/height', 8)
    w = MainWindow(settings=settings, builtin_model_path=tmp_path / 'missing.pt',
        db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results')
    qtbot.addWidget(w)
    qtbot.waitUntil(lambda: w._builtin_model_status is not None)
    return w


def calibrate(window, source):
    p = window.inference_panel
    p.set_image(str(source))
    p._manual_mpp = (.5, .5)
    p._refresh_scale_information()
    p.match_scale_checkbox.setChecked(True)


def run(qtbot, window):
    previous = window.current_record_id
    assert window.inference_panel.run_button.isEnabled()
    window.inference_panel.run_button.click()
    qtbot.waitUntil(lambda: window._inference_engine is None and window.current_record_id != previous, timeout=10000)
    record = window.database_manager.get_record_by_id(window.current_record_id)
    return json.loads(record['analysis_json'])


@pytest.mark.parametrize('decoder', ['opencv_color', 'pillow_rgb'])
def test_first_and_second_run_after_model_switch_keep_matching(qtbot, tmp_path, window, decoder):
    a = model_file(tmp_path, 'A', decoder=decoder)
    b = model_file(tmp_path, 'B', field=12, decoder=decoder)
    source = tmp_path / 'image.png'
    Image.new('RGB', (96, 72), (120, 80, 50)).save(source)
    window.inference_panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, window.inference_panel)
    calibrate(window, source)
    assert len(run(qtbot, window)['tiles']) == 108
    window.inference_panel.set_custom_model(str(b))
    wait_for_model_idle(qtbot, window.inference_panel)
    assert window.inference_panel.match_scale_checkbox.isChecked()
    first = run(qtbot, window)
    second = run(qtbot, window)
    assert first['tile_size'] == second['tile_size'] == [24, 24]
    assert len(first['tiles']) == len(second['tiles']) == 12
    assert first['spatial_context'] == second['spatial_context']
    assert first['input_profile']['model_sha256'] == file_sha256(b)
    assert window.settings.value('classificationTiles/width', type=int) == 8


@pytest.mark.parametrize('theme', ['Light', 'Dark'])
def test_sampling_dialog_and_shared_feedback_keep_first_run_coherent(qapp, qtbot, tmp_path, window, theme):
    from ui.input_setup import InputSetupDialog

    previous_theme = qapp.property('zyTheme') or 'Light'
    apply_theme(qapp, theme)
    try:
        panel = window.inference_panel
        panel.set_custom_model(str(model_file(tmp_path, 'A')))
        wait_for_model_idle(qtbot, panel)
        source = tmp_path / 'image.png'
        Image.new('RGB', (96, 72), (120, 80, 50)).save(source)
        panel.set_image(str(source))
        window.show()

        def apply_sampling():
            dialog = panel._input_setup_dialog
            assert isinstance(dialog, InputSetupDialog)
            dialog.physical_mode.setChecked(True)
            dialog.editor.mpp_boxes[0].setValue(.5)
            assert dialog.preview.count == 108
            dialog.apply_button.click()

        QTimer.singleShot(0, apply_sampling)
        panel.image_scale_button.click()
        panel.set_custom_model(str(model_file(tmp_path, 'B', field=12)))
        wait_for_model_idle(qtbot, panel)

        def review_sampling():
            dialog = panel._input_setup_dialog
            assert dialog.physical_mode.isChecked()
            assert dialog.editor.mpp_boxes[0].value() == .5
            assert dialog.preview.tile == (24, 24)
            assert dialog.preview.count == 12
            dialog.reject()

        QTimer.singleShot(0, review_sampling)
        panel.image_scale_button.click()
        first, second = run(qtbot, window), run(qtbot, window)
        assert first['tile_size'] == second['tile_size'] == [24, 24]
        assert len(first['tiles']) == len(second['tiles']) == 12
        assert first['spatial_context'] == second['spatial_context']
    finally:
        apply_theme(qapp, previous_theme)


def test_deferred_startup_does_not_override_an_explicit_model(qtbot, tmp_path):
    model = model_file(tmp_path, 'selected')
    w = MainWindow(settings=QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat),
        builtin_model_path=tmp_path / 'missing.pt', db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results')
    qtbot.addWidget(w)
    w.inference_panel.set_custom_model(str(model))
    wait_for_model_idle(qtbot, w.inference_panel)
    qtbot.wait(40)  # Deliver the startup callback queued before Browse.
    assert w.inference_panel._active_input_profile is not None
    assert w.inference_panel._active_input_profile.model_sha256 == file_sha256(model)
    assert w.inference_panel._model_ready


def test_no_model_field_disables_matching_without_guessing_one(qtbot, tmp_path, window):
    a = model_file(tmp_path, 'A')
    b = model_file(tmp_path, 'undocumented', field=None)
    source = tmp_path / 'image.png'
    Image.new('RGB', (96, 72), (120, 80, 50)).save(source)
    panel = window.inference_panel
    panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, panel)
    calibrate(window, source)
    panel.set_custom_model(str(b))
    wait_for_model_idle(qtbot, panel)
    assert not panel.match_scale_checkbox.isEnabled()
    assert not panel.match_scale_checkbox.isChecked()
    assert panel._manual_mpp == (.5, .5)
    assert panel._active_input_profile.field_um is None
    first, second = run(qtbot, window), run(qtbot, window)
    assert first['spatial_context']['mode'] == second['spatial_context']['mode'] == 'pixel'
    assert len(first['tiles']) == len(second['tiles']) == 108


def test_different_reader_does_not_reuse_manual_mpp(qtbot, tmp_path, window):
    a = model_file(tmp_path, 'A', decoder='pillow_rgb')
    b = model_file(tmp_path, 'B', field=12)
    source = tmp_path / 'image.png'
    Image.new('RGB', (96, 72)).save(source)
    panel = window.inference_panel
    panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, panel)
    calibrate(window, source)
    panel.set_custom_model(str(b))
    wait_for_model_idle(qtbot, panel)
    assert panel._manual_mpp is None
    assert not panel.match_scale_checkbox.isChecked()


def test_run_reconciles_stale_panel_with_selected_model_before_freezing(qtbot, tmp_path, window):
    a = model_file(tmp_path, 'A')
    b = model_file(tmp_path, 'B', field=12)
    source = tmp_path / 'image.png'
    Image.new('RGB', (96, 72), (120, 80, 50)).save(source)
    panel = window.inference_panel
    panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, panel)
    calibrate(window, source)
    old = panel._active_input_profile
    panel.set_custom_model(str(b))
    wait_for_model_idle(qtbot, panel)
    panel.set_active_input_profile(old)  # Simulate a late UI update from A.
    panel.match_scale_checkbox.setChecked(True)
    first, second = run(qtbot, window), run(qtbot, window)
    assert first['tile_size'] == second['tile_size'] == [24, 24]
    assert len(first['tiles']) == len(second['tiles']) == 12


def test_first_and_second_segmentation_run_use_new_model_geometry(qtbot, tmp_path, window):
    a = model_file(tmp_path, 'A', task='segmentation')
    b = model_file(tmp_path, 'B', field=12, task='segmentation')
    source = tmp_path / 'image.png'
    Image.new('RGB', (48, 48), (120, 80, 50)).save(source)
    panel = window.inference_panel
    panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, panel)
    calibrate(window, source)
    panel.set_custom_model(str(b))
    wait_for_model_idle(qtbot, panel)
    assert panel.match_scale_checkbox.isChecked()
    first, second = run(qtbot, window), run(qtbot, window)
    assert first['tile'] == second['tile'] == [24, 24]
    assert first['stride'] == second['stride'] == [24, 24]
    assert first['spatial_context'] == second['spatial_context']


@pytest.mark.parametrize('action', ['wait', 'another_image', 'choose_C', 'failure'])
def test_background_validation_publishes_only_latest_model_input(qtbot, tmp_path, window, monkeypatch, action):
    a = model_file(tmp_path, 'A')
    b = model_file(tmp_path, 'B', field=12)
    c = model_file(tmp_path, 'C', field=24)
    source = tmp_path / 'image.png'
    Image.new('RGB', (96, 72), (120, 80, 50)).save(source)
    panel = window.inference_panel
    panel.set_custom_model(str(a))
    wait_for_model_idle(qtbot, panel)
    calibrate(window, source)
    original = ModelLoader.load_with_info
    entered, release = threading.Event(), threading.Event()
    def paused_load(loader, path):
        if str(path) == str(b):
            entered.set()
            assert release.wait(5)
            if action == 'failure':
                raise ModelValidationError('Test rejected B')
        return original(loader, path)
    monkeypatch.setattr(ModelLoader, 'load_with_info', paused_load)
    monkeypatch.setattr(window, '_BACKGROUND_MODEL_BYTES', 1)
    warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda parent, title, text: warnings.append(text))
    panel.set_custom_model(str(b))
    try:
        qtbot.waitUntil(entered.is_set, timeout=5000)
        assert not panel.run_button.isEnabled()
        assert not panel.image_scale_button.isEnabled()
        # Even a direct request cannot bypass the validation gate.
        panel.run_requested.emit(str(b), False, str(source), 'classification')
        assert window._inference_engine is None
        assert window.database_manager.get_all_records() == []
        if action == 'another_image':
            other = tmp_path / 'other.png'
            Image.new('RGB', (96, 72), (10, 20, 30)).save(other)
            panel.set_image(str(other))
        elif action == 'choose_C':
            panel.set_custom_model(str(c))
    finally:
        release.set()
    qtbot.waitUntil(lambda: window._model_validation_thread is None and window._pending_custom_path is None, timeout=10000)
    if action == 'failure':
        assert not panel._model_ready
        assert not panel.match_scale_checkbox.isChecked()
        assert panel._pending_model_input is None
        assert window.database_manager.get_all_records() == []
        return
    assert panel._model_ready
    assert panel._active_input_profile.model_sha256 == file_sha256(c if action == 'choose_C' else b)
    first, second = run(qtbot, window), run(qtbot, window)
    expected = 108 if action == 'another_image' else 2 if action == 'choose_C' else 12
    assert len(first['tiles']) == len(second['tiles']) == expected
    assert first['spatial_context'] == second['spatial_context']
    if action == 'another_image':
        assert panel._manual_mpp is None
        assert not panel.match_scale_checkbox.isChecked()
    else:
        assert panel._manual_mpp == (.5, .5)
        assert panel.match_scale_checkbox.isChecked()
