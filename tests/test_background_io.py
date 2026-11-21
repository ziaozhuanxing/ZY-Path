"""Latest-selection history, responsive checks and frozen export presentations."""
import json
import threading
from pathlib import Path
import pytest
from PIL import Image
from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import QMessageBox
from test_audit_source_and_loader import fixtures, infer
from ui.main_window import MainWindow
from ui_test_helpers import wait_for_history_idle, wait_for_export_idle
from data.png_bundle import export_png_bundle, verify_png_bundle
from core.model_profile import ModelInputProfile, SCHEMA
from core.model_loader import LoadedModel, ValidationResult
from ui.model_settings import ModelSettingsPage, model_requirements_summary


@pytest.fixture
def window(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    settings.setValue('export/pngReminderEnabled', False)
    settings.setValue('export/pdfReminderEnabled', False)
    w = MainWindow(settings=settings, db_path=tmp_path / 'db.sqlite', results_dir=tmp_path / 'results')
    qtbot.addWidget(w)
    w.warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: w.warnings.append(str(args[-1])))
    for name in ('a', 'b'):
        folder = tmp_path / name
        folder.mkdir()
        model, source, loaded = fixtures(folder)
        assert w._show_inference_result(infer(model, source, loaded))
        setattr(w, name + '_id', w.current_record_id)
    w.show()
    return w


@pytest.mark.parametrize('action', ['newer', 'cancel', 'clear', 'close', 'delete'])
def test_history_load_keeps_event_loop_responsive_and_ignores_stale_completion(window, qtbot, monkeypatch, action):
    entered, release = threading.Event(), threading.Event()
    get_record = window.database_manager.get_record_by_id
    threads = []
    def slow_get(record_id):
        threads.append(threading.get_ident())
        if record_id == window.a_id:
            entered.set()
            assert release.wait(5)
        return get_record(record_id)
    monkeypatch.setattr(window.database_manager, 'get_record_by_id', slow_get)
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(1)
    try:
        window._show_record_activated(window.a_id)
        qtbot.waitUntil(entered.is_set)
        qtbot.waitUntil(lambda: len(ticks) >= 3)
        assert threads[0] != threading.get_ident()
        assert window.current_record_id == window.b_id
        assert not window.action_panel.export_png_button.isEnabled()
        if action == 'newer':
            window._show_record_activated(window.b_id)
        elif action == 'cancel':
            window._cancel_history_load()
        elif action == 'clear':
            window._clear_current_view()
        elif action == 'close':
            window.close()
            assert window.isVisible()
        else:
            # A delete must cancel an in-flight restoration of the same record.
            monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.Yes)
            # Remove only synthetic app-owned files; the input images remain.
            monkeypatch.setattr(window.database_manager, 'get_record_by_id', get_record)
            window._confirm_delete_records([window.a_id])
    finally:
        release.set()
    wait_for_history_idle(qtbot, window)
    timer.stop()
    if action == 'close':
        qtbot.waitUntil(lambda: not window.isVisible())
    elif action == 'clear':
        assert window._current_result is None
        assert window.current_record_id is None
    else:
        assert window.current_record_id == window.b_id
        assert '/b/' in window._current_result['metadata']['model_path'].replace('\\', '/')
    assert not window.warnings


def test_png_export_checks_and_rendering_run_in_background_and_snapshot_current_view(window, qtbot, tmp_path, monkeypatch):
    import ui.png_export_worker as module
    destination = tmp_path / 'out.png'
    entered, release = threading.Event(), threading.Event()
    real_export = module.export_png_bundle
    observed = []
    def paused_export(image, *args, **kwargs):
        observed.append((threading.get_ident(), image.getpixel((0, 0))))
        entered.set()
        assert release.wait(5)
        return real_export(image, *args, **kwargs)
    monkeypatch.setattr(module, 'export_png_bundle', paused_export)
    monkeypatch.setattr(window, '_validate_export_sources', lambda *a, **k: pytest.fail('GUI thread must not hash export inputs'))
    chooser_calls = []
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *a, **k: (chooser_calls.append(1) or str(destination), ''))
    page = window.result_panel.tile_page
    before = page.render_image()
    try:
        window._export_current_png()
        qtbot.waitUntil(entered.is_set)
        window._export_current_png()
        assert len(chooser_calls) == 1
        assert observed[0][0] != threading.get_ident()
        assert observed[0][1] == before.getpixel((0, 0))
        page.opacity.setValue(0)
    finally:
        release.set()
    wait_for_export_idle(qtbot, window)
    saved = verify_png_bundle(destination, destination.with_suffix('.png.json'))
    assert saved['classification_analysis']['presentation']['opacity'] == .4
    assert page.presentation()['opacity'] == 0
    assert window.action_panel.export_png_button.isEnabled()
    assert not window.warnings


def test_closing_during_png_check_preserves_previous_pair(window, qtbot, tmp_path, monkeypatch):
    import ui.png_export_worker as module
    destination = tmp_path / 'out.png'
    export_png_bundle(Image.new('RGB', (10, 8), 'yellow'), destination, {})
    sidecar = destination.with_suffix('.png.json')
    old = destination.read_bytes(), sidecar.read_bytes()
    entered, release = threading.Event(), threading.Event()
    verify = module.verify_saved_artifacts
    def paused_verify(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return verify(*args, **kwargs)
    monkeypatch.setattr(module, 'verify_saved_artifacts', paused_verify)
    monkeypatch.setattr('ui.main_window.QFileDialog.getSaveFileName', lambda *a, **k: (str(destination), ''))
    try:
        window._export_current_png()
        qtbot.waitUntil(entered.is_set)
        worker = window._png_export_worker
        window.close()
        assert window.isVisible()
        assert worker.isInterruptionRequested()
    finally:
        release.set()
    wait_for_export_idle(qtbot, window)
    qtbot.waitUntil(lambda: not window.isVisible())
    assert worker.outcome == 'cancelled'
    assert (destination.read_bytes(), sidecar.read_bytes()) == old


def test_model_summary_uses_declared_non224_geometry_and_non_nine_class_output(qtbot, tmp_path):
    from types import SimpleNamespace
    profile = ModelInputProfile.from_dict({'schema': SCHEMA, 'model_sha256': 'a' * 64,
        'task_type': 'classification', 'classes': ['X', 'Y', 'Z'], 'input_size': [320, 192],
        'normalization': 'raw255', 'input_scope': 'patch', 'field_um': [160, 96]})
    loaded = SimpleNamespace(input_profile=profile, classes=['X', 'Y', 'Z'])
    validation = ValidationResult('classification', 3, (1, 3))
    text = model_requirements_summary(loaded, validation)
    assert '320 x 192 RGB' in text
    assert '3 classes' in text and 'X, Y, Z' in text and 'raw255' in text
    assert '160 x 96 um' in text
    assert '224' not in text and '9 classes' not in text
    settings = QSettings(str(tmp_path / 'models.ini'), QSettings.IniFormat)
    page = ModelSettingsPage(settings, {'classification': 'builtin.pth', 'segmentation': 'seg.pth'})
    qtbot.addWidget(page)
    model = (tmp_path / 'custom.pth').resolve()
    page._validated('classification', model, validation, loaded)
    assert page.rows['classification']['details'].text() == text
    page.rows['classification']['path'].setText(str(tmp_path / 'different.pth'))
    assert 'have not been checked' in page.rows['classification']['details'].text()
