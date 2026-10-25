"""Real worker lifetimes, responsive event loop and atomic PDF destinations."""
import threading

from PIL import Image
import pytest
from PyQt5.QtCore import QThread, QTimer, QSettings

from data.export_manager import ExportCancelled, ExportError, ExportManager
from ui.pdf_export_worker import PdfExportWorker
from ui.main_window import MainWindow


def inputs(tmp_path):
    original, result = tmp_path / "original.png", tmp_path / "overlay.png"
    Image.new("RGB", (40, 30), "white").save(original)
    Image.new("RGB", (40, 30), "green").save(result)
    return original, result


def test_pdf_generation_failure_keeps_existing_destination_and_removes_partial(tmp_path, monkeypatch):
    original, result = inputs(tmp_path)
    destination = tmp_path / "existing.pdf"
    destination.write_bytes(b"previous complete report")

    def fail_write(path, *args, **kwargs):
        path.write_bytes(b"partial PDF")
        raise ValueError("Simulated write failure")

    monkeypatch.setattr("data.export_manager.write_report", fail_write)
    with pytest.raises(ExportError):
        ExportManager().export_pdf(destination, original, result, {})
    assert destination.read_bytes() == b"previous complete report"
    assert not list(tmp_path.glob(".zy-path-*"))


def test_cancel_before_atomic_replace_preserves_existing_file(tmp_path):
    original, result = inputs(tmp_path)
    destination = tmp_path / "existing.pdf"
    destination.write_bytes(b"previous report")

    def cancel(message, percent):
        if percent == 98:
            raise ExportCancelled("Cancelled")

    with pytest.raises(ExportCancelled):
        ExportManager().export_pdf(destination, original, result, {}, progress=cancel)
    assert destination.read_bytes() == b"previous report"
    assert not list(tmp_path.glob(".zy-path-*"))


def test_worker_snapshots_inputs_and_leaves_gui_event_loop_responsive(qtbot, tmp_path, qapp):
    original, result = inputs(tmp_path)
    entered, release = threading.Event(), threading.Event()
    ticks, observed = [], []

    class SlowManager:
        def export_pdf(self, path, original, result, metadata, **kwargs):
            observed.append(QThread.currentThread() != qapp.thread())
            entered.set()
            assert release.wait(5)
            observed.append(metadata["nested"]["label"])
            observed.append(kwargs["color_map"].getpixel((0, 0)))
            observed.append(kwargs["options"]["image_quality"])
            kwargs["progress"]("Done", 98)

    metadata = {"nested": {"label": "saved class"}}
    options = {"image_quality": "original_resolution"}
    color_map = Image.new("RGB", (40, 30), "red")
    worker = PdfExportWorker(SlowManager(), tmp_path / "out.pdf", original, result,
                             metadata, color_map=color_map, options=options)
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(5)
    try:
        worker.start()
        qtbot.waitUntil(entered.is_set, timeout=5000)
        metadata["nested"]["label"] = "changed after start"
        options["image_quality"] = "standard"
        color_map.paste("blue", (0, 0, 40, 30))
        qtbot.waitUntil(lambda: len(ticks) >= 3, timeout=1000)
    finally:
        release.set()
        assert worker.wait(5000)
        timer.stop()
    assert worker.outcome == "saved"
    assert observed == [True, "saved class", (255, 0, 0), "original_resolution"]


def test_window_waits_for_cancelled_export_before_close(qtbot, tmp_path, monkeypatch):
    original, result = inputs(tmp_path)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("export/pdfReminderEnabled", False)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.db",
                        results_dir=tmp_path / "results", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window.show()
    window._current_result = {"original_image_path": str(original),
                              "result_image_path": str(result), "metadata": {}}
    entered, release = threading.Event(), threading.Event()

    def slow_export(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        kwargs["progress"]("Next step", 50)

    monkeypatch.setattr(window.export_manager, "export_pdf", slow_export)
    monkeypatch.setattr("ui.main_window.QFileDialog.getSaveFileName",
                        lambda *a, **k: (str(tmp_path / "out.pdf"), ""))
    try:
        window._export_current_pdf()
        qtbot.waitUntil(entered.is_set, timeout=5000)
        worker = window._pdf_export_worker
        assert not window.action_panel.export_pdf_button.isEnabled()
        assert window._pdf_progress_dialog.isVisible()
        window.close()
        assert window.isVisible()
        assert worker.isInterruptionRequested()
    finally:
        release.set()
        qtbot.waitUntil(lambda: window._pdf_export_worker is None, timeout=5000)
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=5000)
    assert worker.outcome == "cancelled"
    assert not (tmp_path / "out.pdf").exists()


def test_worker_failure_is_reported_after_thread_stops(qtbot, tmp_path, monkeypatch):
    original, result = inputs(tmp_path)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("export/pdfReminderEnabled", False)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.db",
                        builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window._current_result = {"original_image_path": str(original),
                              "result_image_path": str(result), "metadata": {}}
    messages = []
    monkeypatch.setattr("ui.main_window.QMessageBox.warning",
                        lambda parent, title, message: messages.append(message))
    monkeypatch.setattr("ui.main_window.QFileDialog.getSaveFileName",
                        lambda *a, **k: (str(tmp_path / "out.pdf"), ""))

    def fail(*args, **kwargs):
        raise ExportError("Simulated permission error")

    monkeypatch.setattr(window.export_manager, "export_pdf", fail)
    window._export_current_pdf()
    qtbot.waitUntil(lambda: window._pdf_export_worker is None, timeout=5000)
    assert len(messages) == 1
    assert "could not be saved" in messages[0]
    assert window._pdf_progress_dialog is None
    assert window.action_panel.export_pdf_button.isEnabled()
    assert not (tmp_path / "out.pdf").exists()
    assert window.open_export_button.isHidden()
