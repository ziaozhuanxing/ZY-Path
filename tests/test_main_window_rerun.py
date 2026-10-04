"""Tests for loading a selected history record to re-run inference."""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy, QTest
from PyQt5.QtWidgets import QMessageBox
from torch import nn

from ui.main_window import MainWindow


class TinyClassifier(nn.Module):
	def __init__(self) -> None:
		super().__init__()
		self.pool = nn.AdaptiveAvgPool2d((1, 1))
		self.classifier = nn.Linear(3, 3)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		return self.classifier(self.pool(inputs).flatten(1))


class TinySegmenter(nn.Module):
	def __init__(self) -> None:
		super().__init__()
		self.layer = nn.Conv2d(3, 3, kernel_size=1)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		time.sleep(0.5)
		return self.layer(inputs)


class SlowClassifier(TinyClassifier):
	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		time.sleep(0.5)
		return super().forward(inputs)


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


def _save_model(path: Path, model: nn.Module) -> None:
	torch.save(model, path)


def _save_image(path: Path, color: tuple[int, int, int] = (120, 80, 160)) -> None:
	Image.new("RGB", (32, 24), color).save(path)


def _create_window(
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
	window.show()
	qtbot.waitExposed(window)
	return window


def _click_run_and_wait(qtbot, window: MainWindow, record_count: int) -> None:
	assert window.inference_panel.run_button.isEnabled()
	qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
	qtbot.waitUntil(
		lambda: window._inference_engine is None
		and len(window.database_manager.get_all_records()) == record_count,
		timeout=10000,
	)


def _click_rerun_and_capture(qtbot, window: MainWindow) -> QSignalSpy:
	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)
	engine = window._inference_engine
	assert engine is not None
	return QSignalSpy(engine.result_ready)


def _click_history_tab(qtbot, window: MainWindow) -> None:
	tab_bar = window.tabs.tabBar()
	qtbot.mouseClick(
		tab_bar,
		Qt.LeftButton,
		pos=tab_bar.tabRect(1).center(),
	)
	assert window.tabs.currentWidget() is window.history_panel


def _select_history_row(qtbot, window: MainWindow, row: int = 0) -> None:
	window.history_panel.table.selectRow(row)
	qtbot.waitUntil(lambda: window.action_panel.rerun_button.isEnabled())


def test_rerun_uses_current_second_then_first_selected_history_row(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	builtin_path = tmp_path / "builtin.pth"
	segmenter_path = tmp_path / "segmenter.pt"
	image_a = tmp_path / "image-a.png"
	image_b = tmp_path / "image-b.png"
	_save_model(builtin_path, TinyClassifier())
	_save_model(segmenter_path, TinySegmenter())
	_save_image(image_a, (220, 30, 30))
	_save_image(image_b, (20, 40, 220))
	window = _create_window(qtbot, tmp_path, builtin_path)
	assert window.action_panel.rerun_button.toolTip() == "Select a history record first"
	window.inference_panel.set_image(str(image_a))
	_click_run_and_wait(qtbot, window, 1)
	record_a = window.database_manager.get_all_records()[0]
	assert record_a["model_path"] == "builtin"
	assert record_a["task_type"] == "classification"
	assert window.result_panel.classification_label.text() == record_a["result_label"]

	id_b = window.database_manager.insert_record(
		str(image_b.resolve()),
		str(segmenter_path.resolve()),
		"segmentation",
	)
	record_b = window.database_manager.get_record_by_id(id_b)
	assert record_b is not None
	window.history_panel.set_records([record_a, record_b])
	_click_history_tab(qtbot, window)
	window.history_panel.table.selectRow(1)
	assert window.history_panel.selected_record_id() == id_b
	assert window._selected_history_record_id == id_b
	assert window.action_panel.rerun_button.toolTip() == (
		f"Re-run record #{id_b} with the same image, model and task"
	)

	result_spy = _click_rerun_and_capture(qtbot, window)
	assert len(result_spy) == 0
	assert window.tabs.currentWidget() is window.result_panel
	assert window.result_panel.result_stack.currentWidget() is window.result_panel.empty_page
	assert window.result_panel.classification_label.text() == ""
	assert not window.result_panel.image_label.pixmap().isNull()
	shown_color = window.result_panel.image_label.pixmap().toImage().pixelColor(
		window.result_panel.image_label.pixmap().width() // 2,
		window.result_panel.image_label.pixmap().height() // 2,
	)
	assert (shown_color.red(), shown_color.green(), shown_color.blue()) == (20, 40, 220)
	assert window.statusBar().currentMessage() == f"Re-running record #{id_b}..."
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(
		lambda: len(window.database_manager.get_all_records()) == 3,
		timeout=10000,
	)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	records = window.database_manager.get_all_records()
	new_b = next(record for record in records if record["id"] not in {record_a["id"], id_b})
	assert new_b["image_path"] == record_b["image_path"]
	assert new_b["model_path"] == record_b["model_path"]
	assert new_b["task_type"] == record_b["task_type"]
	assert window.result_panel.classification_label.text() != record_a["result_label"]
	assert window.history_panel.selected_record_id() == new_b["id"]
	assert window.current_record_id == new_b["id"]
	assert window.action_panel.metadata_labels["record"].text() == f"#{new_b['id']}"

	window.history_panel.set_records([record_a, record_b])
	window.history_panel.table.selectRow(0)
	assert window.history_panel.selected_record_id() == record_a["id"]
	result_spy = _click_rerun_and_capture(qtbot, window)
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(
		lambda: len(window.database_manager.get_all_records()) == 4,
		timeout=10000,
	)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	records = window.database_manager.get_all_records()
	new_a = next(record for record in records if record["id"] not in {record["id"] for record in (record_a, record_b, new_b)})
	assert new_a["image_path"] == record_a["image_path"]
	assert new_a["model_path"] == record_a["model_path"]
	assert new_a["task_type"] == record_a["task_type"]
	assert new_a["result_label"] == record_a["result_label"]
	assert new_a["confidence"] == record_a["confidence"]
	assert window.history_panel.selected_record_id() == new_a["id"]
	assert window.current_record_id == new_a["id"]
	assert window.action_panel.metadata_labels["record"].text() == f"#{new_a['id']}"
	assert warning_messages == []


def test_custom_segmentation_rerun_uses_record_task(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "segmenter.pt"
	image_path = tmp_path / "sample.png"
	_save_model(model_path, TinySegmenter())
	_save_image(image_path)
	window = _create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(model_path))
	window.inference_panel.set_image(str(image_path))
	assert window.inference_panel.segmentation_radio.isChecked()

	_click_run_and_wait(qtbot, window, 1)
	original = window.database_manager.get_all_records()[0]
	assert original["model_path"] == str(model_path.resolve())
	assert original["task_type"] == "segmentation"

	_click_history_tab(qtbot, window)
	_select_history_row(qtbot, window)
	use_builtin_changes: list[bool] = []
	window.inference_panel.use_builtin_changed.connect(use_builtin_changes.append)
	result_spy = _click_rerun_and_capture(qtbot, window)

	panel = window.inference_panel
	assert not panel.built_in_checkbox.isChecked()
	assert panel.trust_warning_label.isVisible()
	assert use_builtin_changes == [False]
	assert window._custom_model_status is not None
	assert window._custom_model_status[1]
	assert panel._custom_model_path == str(model_path)
	assert panel._image_path == str(image_path)
	assert panel.segmentation_radio.isChecked()
	assert window.tabs.currentWidget() is window.result_panel
	assert window.statusBar().currentMessage() == f"Re-running record #{original['id']}..."
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 2, timeout=10000)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	records = window.database_manager.get_all_records()
	new_record = next(record for record in records if record["id"] != original["id"])
	assert new_record["task_type"] == "segmentation"
	assert new_record["result_label"] is None
	assert new_record["confidence"] is None
	assert window.history_panel.selected_record_id() == new_record["id"]
	assert window.current_record_id == new_record["id"]
	assert window.action_panel.metadata_labels["record"].text() == f"#{new_record['id']}"
	assert warning_messages == []


def test_missing_original_image_warns_without_changing_panel(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "builtin.pth"
	missing_image = tmp_path / "deleted.png"
	other_image = tmp_path / "current.png"
	_save_model(model_path, TinyClassifier())
	_save_image(other_image)
	window = _create_window(qtbot, tmp_path, model_path)
	window.inference_panel.set_image(str(other_image))
	window.inference_panel.set_task("segmentation")
	record_id = window.database_manager.insert_record(
		str(missing_image), "builtin", "classification"
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	_select_history_row(qtbot, window)
	previous_task = window.inference_panel.segmentation_radio.isChecked()
	count_before = len(window.database_manager.get_all_records())

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	expected_message = f"The original image file no longer exists: {missing_image}"
	assert warning_messages == [expected_message]
	assert window.statusBar().currentMessage() == expected_message
	assert window.inference_panel.built_in_checkbox.isChecked()
	assert window.inference_panel._image_path == str(other_image)
	assert window.inference_panel.segmentation_radio.isChecked() == previous_task
	assert window.tabs.currentWidget() is window.history_panel
	assert len(window.database_manager.get_all_records()) == count_before
	assert window.database_manager.get_record_by_id(record_id) is not None


def test_missing_custom_model_warns_without_changing_panel(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	image_path = tmp_path / "sample.png"
	missing_model = tmp_path / "deleted.pt"
	builtin_path = tmp_path / "builtin.pth"
	_save_image(image_path)
	_save_model(builtin_path, TinyClassifier())
	window = _create_window(qtbot, tmp_path, builtin_path)
	window.inference_panel.set_image(str(image_path))
	record_id = window.database_manager.insert_record(
		str(image_path), str(missing_model), "segmentation"
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	_select_history_row(qtbot, window)
	previous_task = window.inference_panel.classification_radio.isChecked()
	count_before = len(window.database_manager.get_all_records())

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	expected_message = f"The model file no longer exists: {missing_model}"
	assert warning_messages == [expected_message]
	assert window.statusBar().currentMessage() == expected_message
	assert window.inference_panel.built_in_checkbox.isChecked()
	assert window.inference_panel._image_path == str(image_path)
	assert window.inference_panel.classification_radio.isChecked() == previous_task
	assert window.tabs.currentWidget() is window.history_panel
	assert len(window.database_manager.get_all_records()) == count_before
	assert window.database_manager.get_record_by_id(record_id) is not None


def test_rerun_without_selection_shows_status_message(
	qtbot,
	tmp_path: Path,
) -> None:
	window = _create_window(qtbot, tmp_path)
	window.action_panel.rerun_button.setEnabled(True)

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	assert window.statusBar().currentMessage() == "Select a history record first"


def test_double_click_history_record_only_displays_stored_result(
	qtbot,
	tmp_path: Path,
) -> None:
	image_path = tmp_path / "sample.png"
	result_image_path = tmp_path / "result.png"
	_save_image(image_path)
	_save_image(result_image_path)
	window = _create_window(qtbot, tmp_path)
	window.database_manager.insert_record(
		str(image_path), "builtin", "classification", "Class 0", 0.75,
		str(result_image_path),
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	item = window.history_panel.table.item(0, 0)
	assert item is not None
	position = window.history_panel.table.visualItemRect(item).center()
	qtbot.mouseClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=position)
	qtbot.mouseDClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=position)

	assert window.tabs.currentWidget() is window.result_panel
	assert window.result_panel.classification_label.text() == "Class 0"
	assert len(window.database_manager.get_all_records()) == 1
	assert window._inference_engine is None


def test_re_run_target_tracks_latest_uploaded_image(qtbot, tmp_path: Path) -> None:
	model_path = tmp_path / "builtin.pth"
	image_a = tmp_path / "original-a.png"
	image_new = tmp_path / "new-upload.png"
	_save_model(model_path, TinyClassifier())
	_save_image(image_a, (210, 20, 20))
	_save_image(image_new, (20, 210, 20))
	window = _create_window(qtbot, tmp_path, model_path)
	window.inference_panel.set_image(str(image_a))
	_click_run_and_wait(qtbot, window, 1)
	original_a = window.database_manager.get_all_records()[0]

	_click_history_tab(qtbot, window)
	window.history_panel.table.selectRow(0)
	result_spy = _click_rerun_and_capture(qtbot, window)
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 2, timeout=10000)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	re_run_a = window.database_manager.get_all_records()[0]
	assert re_run_a["image_path"] == original_a["image_path"]
	assert window.current_record_id == re_run_a["id"]

	current_id_before_upload = window.current_record_id
	window.inference_panel.set_image(str(image_new))
	assert window.current_record_id == current_id_before_upload
	assert window.action_panel.metadata_labels["record"].text() == (
		f"#{current_id_before_upload}"
	)
	_click_run_and_wait(qtbot, window, 3)
	new_upload_record = window.database_manager.get_all_records()[0]
	assert new_upload_record["image_path"] == str(image_new.resolve())
	assert window.history_panel.selected_record_id() == new_upload_record["id"]
	assert window.current_record_id == new_upload_record["id"]
	assert window.action_panel.metadata_labels["record"].text() == (
		f"#{new_upload_record['id']}"
	)

	result_spy = _click_rerun_and_capture(qtbot, window)
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 4, timeout=10000)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	repeated_new_image = window.database_manager.get_all_records()[0]
	assert repeated_new_image["image_path"] == new_upload_record["image_path"]
	assert repeated_new_image["image_path"] != original_a["image_path"]


def test_double_click_selects_and_reruns_record_b(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	builtin_path = tmp_path / "builtin.pth"
	image_a = tmp_path / "image-a.png"
	image_b = tmp_path / "image-b.png"
	_save_model(builtin_path, TinyClassifier())
	_save_image(image_a, (220, 30, 30))
	_save_image(image_b, (20, 40, 220))
	window = _create_window(qtbot, tmp_path, builtin_path)
	image_result = tmp_path / "stored-result.png"
	_save_image(image_result)
	id_a = window.database_manager.insert_record(
		str(image_a.resolve()), "builtin", "classification", "Class 0", 0.7,
		str(image_result),
	)
	id_b = window.database_manager.insert_record(
		str(image_b.resolve()), "builtin", "classification", "Class 0", 0.7,
		str(image_result),
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	row_b = next(
		row
		for row in range(window.history_panel.table.rowCount())
		if int(window.history_panel.table.item(row, 0).data(Qt.UserRole)) == id_b
	)
	item = window.history_panel.table.item(row_b, 0)
	assert item is not None
	position = window.history_panel.table.visualItemRect(item).center()
	qtbot.mouseClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=position)
	qtbot.mouseDClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=position)

	assert window.history_panel.selected_record_id() == id_b
	assert window.current_record_id == id_b
	assert window.action_panel.metadata_labels["record"].text() == f"#{id_b}"
	assert len(window.database_manager.get_all_records()) == 2
	result_spy = _click_rerun_and_capture(qtbot, window)
	qtbot.waitUntil(lambda: len(result_spy) == 1, timeout=10000)
	qtbot.waitUntil(lambda: len(window.database_manager.get_all_records()) == 3, timeout=10000)
	qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
	new_record = window.database_manager.get_all_records()[0]
	assert new_record["image_path"] == str(image_b.resolve())
	assert new_record["model_path"] == "builtin"
	assert new_record["task_type"] == "classification"
	assert window.current_record_id == new_record["id"]
	assert warning_messages == []


def test_select_record_only_updates_selection_and_rerun_state(
	qtbot, tmp_path: Path
) -> None:
	window = _create_window(qtbot, tmp_path)
	record_ids = [
		window.database_manager.insert_record(
			str(tmp_path / f"image-{index}.png"),
			"builtin",
			"classification",
		)
		for index in range(40)
	]
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	activated_spy = QSignalSpy(window.history_panel.record_activated)
	run_spy = QSignalSpy(window.inference_panel.run_requested)
	selection_spy = QSignalSpy(window.history_panel.selection_changed)
	last_record_id = record_ids[-1]

	assert window.history_panel.select_record(last_record_id)
	item = next(
		window.history_panel.table.item(row, 0)
		for row in range(window.history_panel.table.rowCount())
		if int(window.history_panel.table.item(row, 0).data(Qt.UserRole))
		== last_record_id
	)

	assert window.history_panel.selected_record_id() == last_record_id
	assert window.history_panel.table.visualItemRect(item).intersects(
		window.history_panel.table.viewport().rect()
	)
	assert len(selection_spy) == 1
	assert len(activated_spy) == 0
	assert len(run_spy) == 0
	assert window.tabs.currentWidget() is window.history_panel
	assert window._inference_engine is None


def test_invalid_custom_model_warns_and_does_not_start_inference(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	image_path = tmp_path / "sample.png"
	model_path = tmp_path / "invalid.pt"
	_save_image(image_path)
	model_path.write_bytes(b"not a torch model")
	window = _create_window(qtbot, tmp_path)
	window.database_manager.insert_record(
		str(image_path), str(model_path), "segmentation"
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	_click_history_tab(qtbot, window)
	window.history_panel.table.selectRow(0)
	count_before = len(window.database_manager.get_all_records())

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	assert window._inference_engine is None
	assert len(window.database_manager.get_all_records()) == count_before
	assert warning_messages
	assert "could not be loaded" in warning_messages[-1]


def test_rerun_while_inference_is_running_is_ignored(
	qtbot,
	tmp_path: Path,
	warning_messages: list[str],
) -> None:
	model_path = tmp_path / "slow.pth"
	image_path = tmp_path / "sample.png"
	_save_model(model_path, SlowClassifier())
	_save_image(image_path)
	window = _create_window(qtbot, tmp_path)
	window.inference_panel.set_custom_model(str(model_path))
	window.inference_panel.set_image(str(image_path))
	window.database_manager.insert_record(
		str(image_path), str(model_path), "classification"
	)
	window.history_panel.set_records(window.database_manager.get_all_records())
	window.history_panel.table.selectRow(0)
	count_before_run = len(window.database_manager.get_all_records())
	qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
	assert window._inference_engine is not None

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	assert window.statusBar().currentMessage() == "Inference is already running"
	qtbot.waitUntil(
		lambda: window._inference_engine is None
		and len(window.database_manager.get_all_records()) == count_before_run + 1,
		timeout=10000,
	)
	assert warning_messages == []
