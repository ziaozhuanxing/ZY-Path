"""Tests for the inference panel controls and signal contract."""

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QMessageBox

from ui.inference_panel import InferencePanel
from ui.main_window import MainWindow
from ui.theme import ERROR, SUCCESS


def create_image(path) -> str:
    Image.new("RGB", (24, 16), color="white").save(path)
    return str(path)


def test_default_controls(qtbot) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)

    assert panel.built_in_checkbox.isChecked()
    assert not panel.browse_model_button.isEnabled()
    assert panel.classification_radio.isChecked()
    assert not panel.run_button.isEnabled()
    assert panel.model_status_label.text() == "⚠ Built-in model: not loaded yet"


def test_custom_model_controls_show_trust_warning(qtbot) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)
    initial_status = panel.model_status_label.text()
    state_spy = QSignalSpy(panel.use_builtin_changed)

    panel.built_in_checkbox.setChecked(False)

    assert panel.browse_model_button.isEnabled()
    assert not panel.trust_warning_label.isHidden()
    assert panel.model_status_label.text() == initial_status
    panel.built_in_checkbox.setChecked(True)
    assert not panel.browse_model_button.isEnabled()
    assert panel.trust_warning_label.isHidden()
    assert panel.model_status_label.text() == initial_status
    assert list(state_spy) == [[False], [True]]
    assert panel.trust_warning_label.text() == (
        "Only load model files from sources you trust."
    )


def test_image_enables_run_and_emits_request(qtbot, tmp_path) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)
    image_path = create_image(tmp_path / "sample.png")
    panel.set_custom_model(str(tmp_path / "custom.pth"))
    panel.set_image(image_path)
    panel.segmentation_radio.setChecked(True)
    spy = QSignalSpy(panel.run_requested)

    assert panel.run_button.isEnabled()
    qtbot.mouseClick(panel.run_button, Qt.LeftButton)

    assert len(spy) == 1
    assert spy[0] == [str(tmp_path / "custom.pth"), False, image_path, "segmentation"]


def test_unreadable_image_shows_friendly_error(qtbot, tmp_path) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)
    bad_image_path = tmp_path / "not-an-image.png"
    bad_image_path.write_text("not an image", encoding="utf-8")

    panel.set_image(str(bad_image_path))

    assert not panel.image_error_label.isHidden()
    assert "could not be opened" in panel.image_error_label.text()
    assert not panel.run_button.isEnabled()


def test_set_running_disables_and_restores_controls(qtbot, tmp_path) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_custom_model(str(tmp_path / "custom.pt"))
    panel.set_image(create_image(tmp_path / "sample.png"))

    panel.set_running(True)
    assert not panel.isEnabled()
    assert panel.run_button.text() == "Running..."
    assert not panel.run_button.isEnabled()

    panel.set_running(False)
    assert panel.isEnabled()
    assert panel.run_button.text() == "Run Inference"
    assert panel.browse_model_button.isEnabled()
    assert panel.upload_image_button.isEnabled()
    assert panel.classification_radio.isEnabled()
    assert panel.run_button.isEnabled()


def test_model_status_includes_icon_and_color(qtbot) -> None:
    panel = InferencePanel()
    qtbot.addWidget(panel)

    panel.set_model_status("Model ready", True)
    assert panel.model_status_label.text() == "✔ Model ready"
    assert SUCCESS in panel.model_status_label.styleSheet()

    panel.set_model_status("Model unavailable", False)
    assert panel.model_status_label.text() == "⚠ Model unavailable"
    assert ERROR in panel.model_status_label.styleSheet()


def test_main_window_reports_run_request(qtbot, tmp_path, monkeypatch) -> None:
    warning_messages: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, _title, message: warning_messages.append(str(message)),
    )
    window = MainWindow(
        db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "missing-model.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    window.inference_panel.set_image(create_image(tmp_path / "sample.png"))

    run_state: dict[str, object] = {}

    def capture_started_engine(*_args: object) -> None:
        engine = window._inference_engine
        assert engine is not None
        run_state["status"] = window.statusBar().currentMessage()
        run_state["engine"] = engine
        run_state["finished"] = QSignalSpy(engine.finished)

    window.inference_panel.run_requested.connect(capture_started_engine)
    qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)

    assert run_state["status"] == "Running inference..."
    finished_spy = run_state["finished"]
    qtbot.waitUntil(lambda: len(finished_spy) == 1, timeout=5000)
    assert run_state["engine"].isFinished()
    assert warning_messages == [
        "The model file could not be found. Choose an existing .pt or .pth file."
    ]
    assert window.inference_panel.isEnabled()