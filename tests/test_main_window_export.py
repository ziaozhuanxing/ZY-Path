"""Tests for exporting results and opening saved history records."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from torch import nn

import ui.main_window as main_window_module
from ui.main_window import MainWindow


class TinyClassifier(nn.Module):
	def __init__(self) -> None:
		super().__init__()
		self.pool = nn.AdaptiveAvgPool2d((1, 1))
		self.classifier = nn.Linear(3, 3)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		return self.classifier(self.pool(inputs).flatten(1))


@pytest.fixture(autouse=True)
def accept_export_reminders(qtbot):
	"""Continue through the real reminder dialog during export workflows."""
	def accept_reminder():
		dialog = QApplication.activeModalWidget()
		if isinstance(dialog, QMessageBox) and dialog.windowTitle() in (
			"Export PNG", "Export PDF"
		):
			for button in dialog.buttons():
				if dialog.buttonRole(button) == QMessageBox.AcceptRole:
					button.click()
					break

	timer = QTimer()
	timer.timeout.connect(accept_reminder)
	timer.start(10)
	yield
	timer.stop()


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


def create_window(
	qtbot,
	tmp_path: Path,
	settings: QSettings | None = None,
) -> MainWindow:
	tmp_path.mkdir(parents=True, exist_ok=True)
	if settings is None:
		settings = QSettings(str(tmp_path / "legacy-settings.ini"), QSettings.IniFormat)
		settings.setValue("export/pngReminderEnabled", False)
		settings.setValue("export/pdfReminderEnabled", False)
		settings.sync()
	model_path = tmp_path / "classifier.pth"
	torch.save(TinyClassifier(), model_path)
	window = MainWindow(
		builtin_model_path=tmp_path / "missing-builtin.pth",
		results_dir=tmp_path / "results",
		db_path=tmp_path / "history.db",
		settings=settings,
	)
	qtbot.addWidget(window)
	qtbot.waitUntil(
		lambda: "not loaded yet" not in window.inference_panel.model_status_label.text(),
		timeout=5000,
	)
	window.inference_panel.set_custom_model(str(model_path))
	image_path = tmp_path / "source.png"
	Image.new("RGB", (20, 14), (100, 120, 140)).save(image_path)
	window.inference_panel.set_image(str(image_path))
	return window


def run_inference(qtbot, window: MainWindow) -> None:
	def wait_for_result(*_args: object) -> None:
		engine = window._inference_engine
		assert engine is not None
		with qtbot.waitSignal(engine.result_ready, timeout=10000):
			pass

	window.inference_panel.run_requested.connect(wait_for_result)
	try:
		qtbot.mouseClick(window.inference_panel.run_button, 1)
		qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	finally:
		window.inference_panel.run_requested.disconnect(wait_for_result)


def configure_save_dialog(monkeypatch, selected_path: Path) -> None:
	monkeypatch.setattr(
		main_window_module.QFileDialog,
		"getSaveFileName",
		lambda *_args, **_kwargs: (str(selected_path), ""),
	)


def fresh_settings(tmp_path: Path) -> QSettings:
	return QSettings(str(tmp_path / "export-reminders.ini"), QSettings.IniFormat)


def choose_export_explanation(
	monkeypatch: pytest.MonkeyPatch,
	choice: str,
	checked: bool = False,
) -> dict[str, str]:
	selected: dict[str, str] = {}
	clicked_button: list[object] = []

	def fake_exec(dialog: QMessageBox) -> int:
		dialog.checkBox().setChecked(checked)
		button = next(
			button
			for button in dialog.buttons()
			if button.text() == choice
		)
		clicked_button.append(button)
		selected["title"] = dialog.windowTitle()
		selected["message"] = dialog.text()
		selected["checkbox"] = dialog.checkBox().text()
		return 0

	monkeypatch.setattr(QMessageBox, "exec_", fake_exec)
	monkeypatch.setattr(
		QMessageBox,
		"clickedButton",
		lambda _dialog: clicked_button[-1] if clicked_button else None,
	)
	return selected


def test_export_buttons_enable_after_inference_and_export_files(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
	warning_messages: list[str],
) -> None:
	window = create_window(qtbot, tmp_path)
	assert not window.action_panel.export_png_button.isEnabled()
	assert not window.action_panel.export_pdf_button.isEnabled()
	run_inference(qtbot, window)
	assert window.action_panel.export_png_button.isEnabled()
	assert window.action_panel.export_pdf_button.isEnabled()

	png_path = tmp_path / "exported.png"
	configure_save_dialog(monkeypatch, png_path)
	qtbot.mouseClick(window.action_panel.export_png_button, 1)
	assert png_path.is_file() and png_path.stat().st_size > 0

	pdf_path = tmp_path / "report.pdf"
	configure_save_dialog(monkeypatch, pdf_path)
	qtbot.mouseClick(window.action_panel.export_pdf_button, 1)
	qtbot.waitUntil(lambda: window._pdf_export_worker is None, timeout=15000)
	pdf_data = pdf_path.read_bytes()
	assert pdf_data.startswith(b"%PDF")
	assert pdf_data.count(b"/Subtype /Image") >= 2
	assert window.statusBar().currentMessage() == f"Saved to {pdf_path}"
	assert warning_messages == []


def test_cancelled_export_does_not_create_file(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	window = create_window(qtbot, tmp_path)
	run_inference(qtbot, window)
	monkeypatch.setattr(
		main_window_module.QFileDialog,
		"getSaveFileName",
		lambda *_args, **_kwargs: ("", ""),
	)
	qtbot.mouseClick(window.action_panel.export_png_button, 1)
	qtbot.mouseClick(window.action_panel.export_pdf_button, 1)
	assert list(tmp_path.glob("zypath_*.png")) == []
	assert list(tmp_path.glob("zypath_*.pdf")) == []


def test_export_reminders_continue_and_cancel_before_save_dialog(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	settings = fresh_settings(tmp_path)
	window = create_window(qtbot, tmp_path, settings)
	result_path = tmp_path / "result.png"
	Image.new("RGB", (20, 14), "white").save(result_path)
	window._current_result = {
		"original_image_path": str(result_path),
		"result_image_path": str(result_path),
		"metadata": {},
	}

	cancel_dialog = choose_export_explanation(monkeypatch, "Cancel")
	file_dialog_calls: list[bool] = []
	monkeypatch.setattr(
		main_window_module.QFileDialog,
		"getSaveFileName",
		lambda *_args, **_kwargs: file_dialog_calls.append(True) or ("", ""),
	)
	window._export_current_png()
	assert cancel_dialog["title"] == "Export PNG"
	assert cancel_dialog["message"] == (
		"PNG exports the result image only. Choose PDF if you need a full report."
	)
	assert not file_dialog_calls
	assert settings.value("export/pngReminderEnabled", True, type=bool)

	continue_dialog = choose_export_explanation(monkeypatch, "Continue")
	configure_save_dialog(monkeypatch, tmp_path / "continued.png")
	window._export_current_png()
	assert continue_dialog["checkbox"] == "Don't show this again for PNG exports"
	assert (tmp_path / "continued.png").is_file()


def test_export_reminders_are_independent_and_persist_across_restart(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	settings = fresh_settings(tmp_path)
	window = create_window(qtbot, tmp_path, settings)
	result_path = tmp_path / "result.png"
	Image.new("RGB", (20, 14), "white").save(result_path)
	window._current_result = {
		"original_image_path": str(result_path),
		"result_image_path": str(result_path),
		"metadata": {},
	}

	choose_export_explanation(monkeypatch, "Continue", checked=True)
	configure_save_dialog(monkeypatch, tmp_path / "png.png")
	window._export_current_png()
	assert settings.value("export/pngReminderEnabled", True, type=bool) is False
	assert settings.value("export/pdfReminderEnabled", True, type=bool) is True

	pdf_dialog = choose_export_explanation(monkeypatch, "Continue", checked=True)
	configure_save_dialog(monkeypatch, tmp_path / "pdf.pdf")
	monkeypatch.setattr(window.export_manager, "export_pdf", lambda *args, **kwargs: args[0])
	window._export_current_pdf()
	qtbot.waitUntil(lambda: window._pdf_export_worker is None, timeout=15000)
	assert pdf_dialog["title"] == "Export PDF"
	assert pdf_dialog["message"] == (
		"PDF exports a report containing the original image, result image, and analysis details."
	)
	assert settings.value("export/pdfReminderEnabled", True, type=bool) is False

	restarted_settings = QSettings(settings.fileName(), QSettings.IniFormat)
	restarted = create_window(qtbot, tmp_path / "restarted", restarted_settings)
	assert restarted._show_export_explanation("PNG") is True
	assert restarted._show_export_explanation("PDF") is True


def test_reset_export_reminders_restores_both_preferences(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	settings = fresh_settings(tmp_path)
	settings.setValue("export/pngReminderEnabled", False)
	settings.setValue("export/pdfReminderEnabled", False)
	settings.sync()
	window = create_window(qtbot, tmp_path, settings)
	messages: list[str] = []
	monkeypatch.setattr(
		QMessageBox,
		"information",
		lambda _parent, _title, message: messages.append(str(message)),
	)

	window.reset_export_reminders_action.trigger()

	assert settings.value("export/pngReminderEnabled", False, type=bool) is True
	assert settings.value("export/pdfReminderEnabled", False, type=bool) is True
	assert messages == ["PNG and PDF export reminders have been restored."]


def test_pdf_export_warns_when_original_image_is_missing(
	qtbot,
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
	warning_messages: list[str],
) -> None:
	window = create_window(qtbot, tmp_path)
	run_inference(qtbot, window)
	original_path = Path(window._current_result["original_image_path"])
	original_path.unlink()
	pdf_path = tmp_path / "missing-source-report.pdf"
	configure_save_dialog(monkeypatch, pdf_path)

	qtbot.mouseClick(window.action_panel.export_pdf_button, 1)

	assert not pdf_path.exists()
	assert warning_messages
	assert "Original image not found" in warning_messages[0]
	assert str(original_path) in warning_messages[0]


def test_opening_history_record_displays_result_and_metadata(
	qtbot,
	tmp_path: Path,
) -> None:
	window = create_window(qtbot, tmp_path)
	original_path = tmp_path / "history-source.png"
	result_path = tmp_path / "history-result.png"
	Image.new("RGB", (30, 20), "white").save(original_path)
	Image.new("RGB", (60, 40), "green").save(result_path)
	record_id = window.database_manager.insert_record(
		str(original_path),
		"history-model.pth",
		"classification",
		"tumour",
		0.875,
		str(result_path),
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	window.tabs.setCurrentWidget(window.history_panel)

	window.history_panel.record_activated.emit(record_id)

	assert window.tabs.currentWidget() is window.result_panel
	assert window.result_panel.classification_label.text() == "tumour"
	assert window.result_panel.confidence_label.text() == "Confidence: 87.5 %"
	assert len(window.result_panel._result_figure.axes[0].images) == 1
	assert window.action_panel.export_png_button.isEnabled()
	assert window.action_panel.export_pdf_button.isEnabled()
	assert window.action_panel.metadata_labels["model"].text() == "history-model.pth"
	assert window.action_panel.metadata_labels["image"].text() == original_path.name
	assert window.action_panel.metadata_labels["time"].text() == window._current_result["metadata"]["timestamp"]
	assert window._current_result["metadata"]["task_type"] == "classification"
	assert window._current_result["metadata"]["image_path"] == str(original_path)
	assert window._current_result["metadata"]["result_label"] == "tumour"
	assert window.statusBar().currentMessage() == f"Showing record #{record_id}"


def test_opening_record_with_missing_original_still_displays_result(
	qtbot,
	tmp_path: Path,
) -> None:
	window = create_window(qtbot, tmp_path)
	result_path = tmp_path / "history-result.png"
	Image.new("RGB", (60, 40), "green").save(result_path)
	original_path = tmp_path / "missing-source.png"
	record_id = window.database_manager.insert_record(
		str(original_path),
		"builtin",
		"segmentation",
		result_image_path=str(result_path),
	)

	window.history_panel.record_activated.emit(record_id)

	assert "Original image not found" in window.result_panel.image_label.text()
	assert len(window.result_panel._result_figure.axes[0].images) == 1
	assert window.tabs.currentWidget() is window.result_panel
	assert window.statusBar().currentMessage() == f"Showing record #{record_id}"


def test_opening_history_record_with_missing_result_image_shows_message(
	qtbot,
	tmp_path: Path,
) -> None:
	window = create_window(qtbot, tmp_path)
	original_path = tmp_path / "history-source.png"
	Image.new("RGB", (30, 20), "white").save(original_path)
	record_id = window.database_manager.insert_record(
		str(original_path),
		"builtin",
		"segmentation",
		result_image_path=str(tmp_path / "missing-result.png"),
	)
	window.history_panel.record_activated.emit(record_id)

	message_text = [
		text.get_text()
		for axis in window.result_panel._result_figure.axes
		for text in axis.texts
	]
	assert "Stored result image not found" in message_text
	assert window.action_panel.export_png_button.isEnabled()
	assert window.tabs.currentWidget() is window.result_panel
	assert window.statusBar().currentMessage() == f"Showing record #{record_id}"
