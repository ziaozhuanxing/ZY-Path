"""Long session names must not widen buttons; progress identifies the running task."""

import pytest
from PIL import Image
from PyQt5.QtCore import QObject, QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from ui.action_panel import ActionPanel
from ui.main_window import MainWindow
from ui.theme import apply_theme


MODEL = "UPerNet_TME_tissue-panoptils_best_model_100ep.pth"
FILENAME = "TCGA-22-5492-01Z-00-DX1.A1CD76-4B12-9C5C-DB8DFB23C003_x19800_y39600_tissue_1.000.png"


@pytest.fixture(params=["Light", "Dark"])
def theme(qapp, request):
    old_style, old_font, old_theme = qapp.styleSheet(), QFont(qapp.font()), qapp.property("zyTheme")
    apply_theme(qapp, request.param)
    yield request.param
    qapp.setStyleSheet(old_style)
    qapp.setFont(old_font)
    qapp.setProperty("zyTheme", old_theme)


@pytest.mark.parametrize("width", [240, 320])
@pytest.mark.parametrize("point_size", [10, 15])
def test_long_segmentation_metadata_does_not_expand_export_buttons(qtbot, theme, width, point_size):
    panel = ActionPanel()
    qtbot.addWidget(panel)
    panel.setMinimumWidth(160)
    panel.setMaximumWidth(360)
    panel.resize(width, 550)
    panel.setFont(QFont(panel.font().family(), point_size))
    panel.show()
    qtbot.waitExposed(panel)
    viewport = panel.controls_scroll.viewport()
    for model, filename in [("classifier.pth", "patch.png"), (MODEL, FILENAME),
                            (MODEL * 3, "unbroken" * 50 + ".png"), ("classifier.pth", "patch.png")]:
        panel.set_metadata(model, filename, "2026-10-24 20:37:59", 37)
        qtbot.wait(30)
        assert panel.width() == width
        assert panel.controls_scroll.widget().width() == viewport.width()
        assert panel.controls_scroll.horizontalScrollBar().maximum() == 0
        for button in (panel.export_png_button, panel.export_pdf_button):
            assert button.width() <= viewport.width()
            assert viewport.rect().contains(button.mapTo(viewport, button.rect().center()))
        for key, original in [("model", model), ("image", filename)]:
            field = panel.metadata_labels[key]
            assert field.text() == original
            assert field.toolTip() == original
            assert field.width() <= viewport.width()
    assert panel.clear_view_button.width() == panel.rerun_button.width()


def test_metadata_wraps_unbroken_names_completely_and_copies_original_text(qtbot, qapp):
    panel = ActionPanel()
    qtbot.addWidget(panel)
    panel.resize(240, 700)
    panel.set_metadata(MODEL, FILENAME, "2026-10-24 20:37:59", 37)
    panel.show()
    qtbot.wait(30)
    field = panel.metadata_labels["image"]
    assert field.text() == FILENAME
    # Measure the laid-out text, including unbroken tokens, rather than just
    # checking a tooltip while visible text is silently clipped.
    document = field.document()
    block = document.begin()
    line_count = 0
    while block.isValid():
        layout = block.layout()
        for index in range(layout.lineCount()):
            line_count += 1
            assert layout.lineAt(index).naturalTextWidth() <= field.viewport().width() + 1
        block = block.next()
    assert line_count >= 3
    assert document.size().height() <= field.viewport().height() + 1
    field.setFocus()
    qtbot.keyClick(field, Qt.Key_A, Qt.ControlModifier)
    qtbot.keyClick(field, Qt.Key_C, Qt.ControlModifier)
    assert qapp.clipboard().text() == FILENAME


class ManualEngine(QObject):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(int, int)
    status_changed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, model_path, image_path, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.classification_mode = "single_image"

    def start(self):
        pass


def make_window(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr("ui.main_window.InferenceEngine", ManualEngine)
    window = MainWindow(
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat),
        builtin_model_path=tmp_path / "not-installed.pth", db_path=tmp_path / "history.db",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    Image.new("RGB", (20, 20), "white").save(tmp_path / "source.png")
    return window


def start(window, tmp_path, task, mode="single_image"):
    window._builtin_model_statuses[task] = ("Test-ready", True)
    assert window._start_inference("", True, str(tmp_path / "source.png"), task,
                                   "Running", "Busy", {"classification_mode": mode})
    return window._inference_engine


@pytest.mark.parametrize("task,mode,prefix", [
    ("segmentation", "single_image", "Segmentation tiles"),
    ("classification", "tiled_analysis", "Classification tiles"),
    ("classification", "single_image", "Classification"),
])
def test_progress_names_the_actual_worker_task_not_current_controls(qtbot, tmp_path, monkeypatch, task, mode, prefix):
    window = make_window(qtbot, tmp_path, monkeypatch)
    worker = start(window, tmp_path, task, mode)
    try:
        window.inference_panel.set_classification_mode("single_image" if mode == "tiled_analysis" else "tiled_analysis")
        worker.progress_changed.emit(3, 81)
        assert window._progress_bar.maximum() == 81
        assert window._progress_bar.value() == 3
        assert window._progress_bar.text() == f"{prefix}: 3/81"
        assert window.statusBar().currentMessage() == f"{prefix}: 3/81"
        assert not window._progress_bar.isHidden()
    finally:
        worker.finished.emit()
    assert window._progress_bar.isHidden()


def test_new_run_resets_old_segmentation_progress_and_cancel_ignores_late_updates(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path, monkeypatch)
    worker = start(window, tmp_path, "segmentation")
    worker.progress_changed.emit(81, 81)
    worker.finished.emit()
    worker = start(window, tmp_path, "classification", "tiled_analysis")
    try:
        assert window._progress_bar.isHidden()
        assert window._progress_bar.value() == 0
        worker.progress_changed.emit(1, 49)
        assert window._progress_bar.text() == "Classification tiles: 1/49"
        window._cancel_requested = True
        worker.progress_changed.emit(2, 49)
        assert window._progress_bar.value() == 1
    finally:
        worker.finished.emit()
