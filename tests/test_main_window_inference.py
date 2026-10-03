"""Headless tests for connecting inference to the main window."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import threading
from datetime import datetime
from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from torch import nn

import ui.main_window as main_window_module
from ui.main_window import MainWindow
from ui.result_panel import ResultPanel


class TinyClassifier(nn.Module):
	def __init__(self, num_classes: int = 3) -> None:
		super().__init__()
		self.pool = nn.AdaptiveAvgPool2d((1, 1))
		self.classifier = nn.Linear(3, num_classes)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		return self.classifier(self.pool(inputs).flatten(1))


class TinySegmenter(nn.Module):
	def __init__(self, num_classes: int = 4) -> None:
		super().__init__()
		self.layer = nn.Conv2d(3, num_classes, kernel_size=1)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		return self.layer(inputs)


@pytest.fixture(autouse=True)
def use_one_torch_thread():
	previous_thread_count = torch.get_num_threads()
	torch.set_num_threads(1)
	yield
	torch.set_num_threads(previous_thread_count)


@pytest.fixture
def warning_messages(monkeypatch: pytest.MonkeyPatch) -> list[str]:
	messages: list[str] = []
	monkeypatch.setattr(
		QMessageBox,
		"warning",
		lambda _parent, _title, message: messages.append(str(message)),
	)
	return messages


def save_module(path: Path, model: nn.Module) -> None:
	torch.save(model, path)


def save_image(path: Path, size: tuple[int, int] = (20, 14)) -> None:
	Image.new("RGB", size, (100, 120, 140)).save(path)


def create_window(
	qtbot,
	tmp_path: Path,
	builtin_model_path: Path | None = None,
) -> MainWindow:
	window = MainWindow(
		builtin_model_path=builtin_model_path or tmp_path / "missing-builtin.pth",
		results_dir=tmp_path / "results",
		db_path=tmp_path / "history.db",
	)
	qtbot.addWidget(window)
	qtbot.waitUntil(
		lambda: "not loaded yet" not in window.inference_panel.model_status_label.text(),
		timeout=5000,
	)
	return window


def run_and_wait_for_result(qtbot, window: MainWindow) -> None:
	"""Click Run and wait for the worker result signal."""
	def wait_for_result(*_args: object) -> None:
		engine = window._inference_engine
		assert engine is not None
		with qtbot.waitSignal(engine.result_ready, timeout=10000):
			pass

	window.inference_panel.run_requested.connect(wait_for_result)
	qtbot.mouseClick(window.inference_panel.run_button, 1)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)


def test_missing_builtin_model_shows_guidance(qtbot, tmp_path: Path) -> None:
	window = create_window(qtbot, tmp_path)

	assert "Built-in model file not found" in window.inference_panel.model_status_label.text()
	assert "Untick the box" in window.inference_panel.model_status_label.text()
	assert window.statusBar().currentMessage() == "Ready"


def test_builtin_model_is_loaded_and_validated(qtbot, tmp_path: Path) -> None:
	model_path = tmp_path / "builtin.pth"
	save_module(model_path, TinyClassifier(num_classes=9))
	window = create_window(qtbot, tmp_path, model_path)

	assert window.inference_panel.model_status_label.text() == "✔ Built-in model: ready (9 classes)"
	assert window.statusBar().currentMessage() == "Ready"


def test_custom_segmentation_model_selects_segmentation_task(
	qtbot,
	tmp_path: Path,
) -> None:
	model_path = tmp_path / "segmenter.pt"
	traced_model = torch.jit.trace(TinySegmenter(), torch.rand((1, 3, 8, 8)))
	traced_model.save(str(model_path))
	window = create_window(qtbot, tmp_path)

	window.inference_panel.set_custom_model(str(model_path))

	assert window.inference_panel.model_status_label.text() == (
		"✔ Custom model: valid, Segmentation (4 classes)"
	)
	assert window.inference_panel.segmentation_radio.isChecked()


def test_classification_run_displays_saves_and_records_result(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "classifier.pth"
	image_path = tmp_path / "sample.png"
	save_module(model_path, TinyClassifier())
	save_image(image_path)
	window = create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(model_path))
	window.inference_panel.set_image(str(image_path))

	run_and_wait_for_result(qtbot, window)

	assert isinstance(window.tabs.widget(0), ResultPanel)
	assert window.result_panel.get_result_figure() is not None
	assert window.result_panel.image_label.pixmap() is not None
	assert window.history_panel.table.rowCount() == 1
	record = window.database_manager.get_all_records()[0]
	assert record["image_path"] == str(image_path.resolve())
	assert record["model_path"] == str(model_path.resolve())
	assert record["task_type"] == "classification"
	assert record["result_label"] is not None
	assert record["confidence"] is not None
	assert Path(record["result_image_path"]).is_file()
	assert "Done in " in window.statusBar().currentMessage()
	assert warning_messages == []


def test_segmentation_run_saves_blended_image_and_records_result(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "segmenter.pt"
	image_path = tmp_path / "sample.png"
	traced_model = torch.jit.trace(TinySegmenter(), torch.rand((1, 3, 8, 8)))
	traced_model.save(str(model_path))
	save_image(image_path, (23, 17))
	window = create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(model_path))
	window.inference_panel.set_image(str(image_path))

	run_and_wait_for_result(qtbot, window)

	assert window.inference_panel.segmentation_radio.isChecked()
	assert window.history_panel.table.rowCount() == 1
	record = window.database_manager.get_all_records()[0]
	assert record["task_type"] == "segmentation"
	assert record["result_label"] is None
	assert record["confidence"] is None
	with Image.open(record["result_image_path"]) as result_image:
		assert result_image.mode == "RGB"
		assert result_image.size == (23, 17)
	assert "Done in " in window.statusBar().currentMessage()
	assert warning_messages == []


def test_builtin_result_uses_history_builtin_marker(
	qtbot,
	tmp_path: Path,
) -> None:
	model_path = tmp_path / "builtin.pth"
	image_path = tmp_path / "sample.png"
	save_module(model_path, TinyClassifier())
	save_image(image_path)
	window = create_window(qtbot, tmp_path, model_path)
	window.inference_panel.set_image(str(image_path))

	run_and_wait_for_result(qtbot, window)

	assert window.database_manager.get_all_records()[0]["model_path"] == "builtin"


def test_corrupt_image_shows_warning_and_restores_panel(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "classifier.pth"
	image_path = tmp_path / "broken.png"
	save_module(model_path, TinyClassifier())
	image_path.write_bytes(b"not an image")
	window = create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(model_path))
	window.inference_panel.run_requested.emit(
		str(model_path), False, str(image_path), "classification"
	)
	qtbot.waitUntil(lambda: bool(warning_messages), timeout=10000)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)

	assert "image could not be opened" in warning_messages[0]
	assert window.statusBar().currentMessage() == warning_messages[0]
	assert window.inference_panel.isEnabled()
	assert window.inference_panel.run_button.text() == "Run Inference"
	assert window.history_panel.table.rowCount() == 0


def test_repeated_run_request_is_ignored_while_worker_is_running(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	started = threading.Event()
	release = threading.Event()
	created_engines: list[QThread] = []

	class PausedEngine(QThread):
		result_ready = pyqtSignal(dict)
		error_occurred = pyqtSignal(str)

		def __init__(self, *_args: object, **_kwargs: object) -> None:
			super().__init__()
			created_engines.append(self)

		def run(self) -> None:
			started.set()
			release.wait(5)

	monkeypatch.setattr(main_window_module, "InferenceEngine", PausedEngine)
	window = create_window(qtbot, tmp_path)
	image_path = tmp_path / "sample.png"
	save_image(image_path)
	window.inference_panel.set_image(str(image_path))
	qtbot.mouseClick(window.inference_panel.run_button, 1)
	qtbot.waitUntil(started.is_set, timeout=5000)
	first_engine = window._inference_engine

	window._show_run_requested("another.pth", False, str(image_path), "classification")

	assert len(created_engines) == 1
	assert window._inference_engine is first_engine
	assert window.statusBar().currentMessage() == "Running inference..."
	release.set()
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=5000)


def test_custom_model_validation_error_is_shown_in_status(
	qtbot,
	tmp_path: Path,
) -> None:
	window = create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(tmp_path / "missing.pt"))

	assert "could not be found" in window.inference_panel.model_status_label.text()
	assert "⚠" in window.inference_panel.model_status_label.text()


def test_session_timestamp_is_local_and_ui_does_not_import_torch_or_sqlite() -> None:
	assert "import torch" not in Path(main_window_module.__file__).read_text(encoding="utf-8")
	assert "import sqlite3" not in Path(main_window_module.__file__).read_text(encoding="utf-8")
	utc_timestamp = "2026-10-03T12:00:00+00:00"
	expected_local = datetime.fromisoformat(utc_timestamp).astimezone().strftime(
		"%Y-%m-%d %H:%M:%S"
	)
	assert MainWindow._local_timestamp(utc_timestamp) == expected_local