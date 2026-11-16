"""Prefer the explicit normal rectangle to conflicting native startup metadata."""
import pytest
from PyQt5.QtCore import QRect, QSettings, QSize, QTimer
from PyQt5.QtWidgets import QWidget

from ui.main_window import MainWindow


def settings_with_geometry(tmp_path, normal):
    settings = QSettings(str(tmp_path / 'window.ini'), QSettings.IniFormat)
    previous = QWidget()
    previous.setGeometry(40, 40, 540, 380)
    settings.setValue('window/geometry', previous.saveGeometry())
    settings.setValue('window/maximized', True)
    if normal is not None:
        settings.setValue('window/normalGeometry', normal)
    settings.sync()
    previous.deleteLater()
    return settings


def create_window(qtbot, tmp_path, settings, monkeypatch):
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    window = MainWindow(settings=settings, db_path=tmp_path / 'history.db',
                        results_dir=tmp_path / 'results', builtin_model_path=tmp_path / 'missing.pth')
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(window.isMaximized, timeout=1500)
    qtbot.wait(120)  # Include delayed native-decoration/screen fitting.
    return window


def test_explicit_normal_rectangle_survives_a_conflicting_delayed_native_restore(
    qtbot, tmp_path, monkeypatch
):
    settings = settings_with_geometry(tmp_path, QRect(40, 40, 520, 360))
    native_restore = MainWindow.restoreGeometry

    def restore_with_late_native_geometry(window, value):
        restored = native_restore(window, value)
        # Some native backends can deliver the geometry restored from the blob
        # after a subsequent hidden setGeometry. The persisted normal rectangle
        # must remain authoritative across that window-manager transaction.
        QTimer.singleShot(0, lambda: window.setGeometry(QRect(30, 30, 700, 500)))
        return restored

    monkeypatch.setattr(MainWindow, 'restoreGeometry', restore_with_late_native_geometry)
    window = create_window(qtbot, tmp_path, settings, monkeypatch)
    window.showNormal()
    qtbot.waitUntil(lambda: window.size() == QSize(520, 360), timeout=1500)
    qtbot.wait(150)
    assert window.size() == QSize(520, 360)
    window.close()
    assert settings.value('window/normalGeometry').size() == QSize(520, 360)


@pytest.mark.parametrize('saved_normal', [None, QRect(), 'invalid rectangle'])
def test_legacy_geometry_blob_remains_usable_without_a_valid_normal_rectangle(
    qtbot, tmp_path, monkeypatch, saved_normal
):
    settings = settings_with_geometry(tmp_path, saved_normal)
    window = create_window(qtbot, tmp_path, settings, monkeypatch)
    window.showNormal()
    qtbot.waitUntil(lambda: window.size() == QSize(540, 380), timeout=1500)
    qtbot.wait(150)
    window.close()
    assert settings.value('window/normalGeometry').size() == QSize(540, 380)
