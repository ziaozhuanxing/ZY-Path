"""Integration tests for confirmed history-record deletion."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest
import torch
from PIL import Image
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMessageBox
from torch import nn

from data.database_manager import DatabaseError
from ui.main_window import MainWindow


class TinyClassifier(nn.Module):
	def __init__(self) -> None:
		super().__init__()
		self.pool = nn.AdaptiveAvgPool2d((1, 1))
		self.classifier = nn.Linear(3, 3)

	def forward(self, inputs: torch.Tensor) -> torch.Tensor:
		return self.classifier(self.pool(inputs).flatten(1))


@pytest.fixture(autouse=True)
def use_one_torch_thread():
	previous_thread_count = torch.get_num_threads()
	torch.set_num_threads(1)
	yield
	torch.set_num_threads(previous_thread_count)


@pytest.fixture
def dialogs(monkeypatch: pytest.MonkeyPatch) -> dict:
	state = {
		"answer": QMessageBox.No,
		"questions": [],
		"warnings": [],
	}

	def question(_parent, title, text, buttons, default_button):
		state["questions"].append((title, text, buttons, default_button))
		return state["answer"]

	monkeypatch.setattr(QMessageBox, "question", question)
	monkeypatch.setattr(
		QMessageBox,
		"warning",
		lambda _parent, title, text: state["warnings"].append((title, str(text))),
	)
	return state


def _save_image(path: Path, color: tuple[int, int, int] = (40, 90, 150)) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	Image.new("RGB", (32, 24), color).save(path)


def _create_window(qtbot, tmp_path: Path) -> MainWindow:
	model_path = tmp_path / "builtin.pth"
	torch.save(TinyClassifier(), model_path)
	window = MainWindow(
		builtin_model_path=model_path,
		db_path=tmp_path / "history.db",
		results_dir=tmp_path / "results",
	)
	qtbot.addWidget(window)
	qtbot.waitUntil(
		lambda: "not loaded yet" not in window.inference_panel.model_status_label.text(),
		timeout=5000,
	)
	window.show()
	qtbot.waitExposed(window)
	return window


def _insert_record(
	window: MainWindow,
	image_path: Path,
	result_path: Path,
	label: str = "Class 0",
) -> int:
	return window.database_manager.insert_record(
		str(image_path.resolve()),
		"builtin",
		"classification",
		label,
		0.75,
		str(result_path.resolve()),
	)


def _open_history(qtbot, window: MainWindow) -> None:
	bar = window.tabs.tabBar()
	qtbot.mouseClick(bar, Qt.LeftButton, pos=bar.tabRect(1).center())
	assert window.tabs.currentWidget() is window.history_panel


def _reload_history_through_ui(qtbot, window: MainWindow) -> None:
	qtbot.mouseClick(window.history_panel.clear_button, Qt.LeftButton)


def _row_for_id(window: MainWindow, record_id: int) -> int:
	for row in range(window.history_panel.table.rowCount()):
		item = window.history_panel.table.item(row, 0)
		if item is not None and item.data(Qt.UserRole) == record_id:
			return row
	raise AssertionError(f"Record #{record_id} is not shown in history")


def _select_id(qtbot, window: MainWindow, record_id: int) -> None:
	window.history_panel.table.selectRow(_row_for_id(window, record_id))


def _click_delete(qtbot, window: MainWindow) -> None:
	assert window.history_panel.delete_selected_button.isEnabled()
	qtbot.mouseClick(window.history_panel.delete_selected_button, Qt.LeftButton)


def test_cancel_delete_keeps_records_selection_and_result_files(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_path = tmp_path / "original.png"
	result_path = window.results_dir / "stored.png"
	_save_image(image_path)
	_save_image(result_path)
	record_id = _insert_record(window, image_path, result_path)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	_select_id(qtbot, window, record_id)

	_click_delete(qtbot, window)

	assert len(dialogs["questions"]) == 1
	title, text, buttons, default_button = dialogs["questions"][0]
	assert title == "Delete records"
	assert text == (
		"Delete 1 record(s)? This cannot be undone. Saved result images will also be removed. "
		"Your original image files are not touched."
	)
	assert buttons == QMessageBox.Yes | QMessageBox.No
	assert default_button == QMessageBox.No
	assert window.database_manager.get_record_by_id(record_id) is not None
	assert result_path.is_file()
	assert image_path.is_file()
	assert window.history_panel.selected_record_id() == record_id


def test_confirmed_single_delete_removes_only_selected_saved_result(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_one = tmp_path / "original-one.png"
	image_two = tmp_path / "original-two.png"
	result_one = window.results_dir / "result-one.png"
	result_two = window.results_dir / "result-two.png"
	for path in (image_one, image_two, result_one, result_two):
		_save_image(path)
	id_one = _insert_record(window, image_one, result_one)
	id_two = _insert_record(window, image_two, result_two)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	_select_id(qtbot, window, id_one)
	dialogs["answer"] = QMessageBox.Yes

	_click_delete(qtbot, window)

	assert window.database_manager.get_record_by_id(id_one) is None
	assert window.database_manager.get_record_by_id(id_two) is not None
	assert not result_one.exists()
	assert result_two.is_file()
	assert image_one.is_file()
	assert image_two.is_file()
	assert window.history_panel.selected_record_ids() == []
	assert window.statusBar().currentMessage() == "Deleted 1 record(s)"


def test_confirmed_multi_delete_and_select_all_delete_all_rows(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	paths = []
	record_ids = []
	for index in range(3):
		image_path = tmp_path / f"original-{index}.png"
		result_path = window.results_dir / f"result-{index}.png"
		_save_image(image_path)
		_save_image(result_path)
		paths.extend((image_path, result_path))
		record_ids.append(_insert_record(window, image_path, result_path))
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	first_row = _row_for_id(window, record_ids[0])
	last_row = _row_for_id(window, record_ids[1])
	first_position = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(first_row, 0)
	).center()
	last_position = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(last_row, 0)
	).center()
	qtbot.mouseClick(
		window.history_panel.table.viewport(), Qt.LeftButton, pos=first_position
	)
	qtbot.mouseClick(
		window.history_panel.table.viewport(),
		Qt.LeftButton,
		pos=last_position,
		modifier=Qt.ControlModifier,
	)
	assert window.history_panel.selected_record_ids() == record_ids[:2]
	dialogs["answer"] = QMessageBox.Yes

	_click_delete(qtbot, window)

	assert window.database_manager.get_record_by_id(record_ids[0]) is None
	assert window.database_manager.get_record_by_id(record_ids[1]) is None
	assert window.database_manager.get_record_by_id(record_ids[2]) is not None
	assert not paths[1].exists()
	assert not paths[3].exists()
	assert paths[5].is_file()

	qtbot.mouseClick(window.history_panel.select_all_button, Qt.LeftButton)
	assert window.history_panel.selected_record_ids() == [record_ids[2]]
	_click_delete(qtbot, window)
	assert window.database_manager.get_all_records() == []
	assert window.history_panel.table.rowCount() == 0
	assert window.history_panel.table_stack.currentWidget() is window.history_panel.empty_label
	assert window.history_panel.empty_label.text() == "No records found"
	assert not paths[5].exists()


def test_delete_never_removes_result_file_outside_results_folder(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_path = tmp_path / "original.png"
	outside_result = tmp_path / "outside-result.png"
	_save_image(image_path)
	_save_image(outside_result)
	record_id = _insert_record(window, image_path, outside_result)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	_select_id(qtbot, window, record_id)
	dialogs["answer"] = QMessageBox.Yes

	_click_delete(qtbot, window)

	assert window.database_manager.get_record_by_id(record_id) is None
	assert outside_result.is_file()
	assert image_path.is_file()


def test_deleting_currently_displayed_record_clears_result_and_exports(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_path = tmp_path / "current-image.png"
	_save_image(image_path)
	window.inference_panel.set_image(str(image_path))
	qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
	qtbot.waitUntil(
		lambda: window._inference_engine is None
		and len(window.database_manager.get_all_records()) == 1,
		timeout=10000,
	)
	record = window.database_manager.get_all_records()[0]
	result_path = Path(record["result_image_path"])
	assert result_path.is_file()
	assert window.current_record_id == record["id"]
	_open_history(qtbot, window)
	_select_id(qtbot, window, record["id"])
	dialogs["answer"] = QMessageBox.Yes

	_click_delete(qtbot, window)

	assert window.current_record_id is None
	assert window._current_result is None
	assert window.result_panel.result_stack.currentWidget() is window.result_panel.empty_page
	assert window.action_panel.metadata_labels["record"].text() == "-"
	assert not window.action_panel.export_png_button.isEnabled()
	assert not window.action_panel.export_pdf_button.isEnabled()
	assert not result_path.exists()


def test_two_selected_rows_disable_rerun(qtbot, tmp_path: Path) -> None:
	window = _create_window(qtbot, tmp_path)
	for index in range(2):
		image_path = tmp_path / f"image-{index}.png"
		result_path = window.results_dir / f"result-{index}.png"
		_save_image(image_path)
		_save_image(result_path)
		_insert_record(window, image_path, result_path)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	first = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(0, 0)
	).center()
	second = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(1, 0)
	).center()
	qtbot.mouseClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=first)
	qtbot.mouseClick(
		window.history_panel.table.viewport(),
		Qt.LeftButton,
		pos=second,
		modifier=Qt.ControlModifier,
	)

	assert len(window.history_panel.selected_record_ids()) == 2
	assert not window.action_panel.rerun_button.isEnabled()


def test_rerun_guard_reports_multiple_selected_rows(
	qtbot, tmp_path: Path
) -> None:
	window = _create_window(qtbot, tmp_path)
	for index in range(2):
		image_path = tmp_path / f"guard-image-{index}.png"
		result_path = window.results_dir / f"guard-result-{index}.png"
		_save_image(image_path)
		_save_image(result_path)
		_insert_record(window, image_path, result_path)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	first = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(0, 0)
	).center()
	second = window.history_panel.table.visualItemRect(
		window.history_panel.table.item(1, 0)
	).center()
	qtbot.mouseClick(window.history_panel.table.viewport(), Qt.LeftButton, pos=first)
	qtbot.mouseClick(
		window.history_panel.table.viewport(),
		Qt.LeftButton,
		pos=second,
		modifier=Qt.ControlModifier,
	)
	assert len(window.history_panel.selected_record_ids()) == 2
	assert not window.action_panel.rerun_button.isEnabled()
	window.action_panel.rerun_button.setEnabled(True)

	qtbot.mouseClick(window.action_panel.rerun_button, Qt.LeftButton)

	assert window.statusBar().currentMessage() == "Select exactly one record to re-run"
	assert window._inference_engine is None
	assert len(window.database_manager.get_all_records()) == 2


def test_delete_key_uses_confirmation_and_deletes_selected_record(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_path = tmp_path / "image.png"
	result_path = window.results_dir / "result.png"
	_save_image(image_path)
	_save_image(result_path)
	record_id = _insert_record(window, image_path, result_path)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	_select_id(qtbot, window, record_id)
	dialogs["answer"] = QMessageBox.Yes

	qtbot.keyClick(window.history_panel.table.viewport(), Qt.Key_Delete)

	assert window.database_manager.get_record_by_id(record_id) is None
	assert not result_path.exists()
	assert len(dialogs["questions"]) == 1


def test_filter_is_preserved_when_select_all_deletes_displayed_matches(
	qtbot, tmp_path: Path, dialogs: dict
) -> None:
	window = _create_window(qtbot, tmp_path)
	entries = []
	for name in ("alpha", "beta"):
		image_path = tmp_path / f"{name}.png"
		result_path = window.results_dir / f"{name}-result.png"
		_save_image(image_path)
		_save_image(result_path)
		record_id = _insert_record(window, image_path, result_path)
		entries.append((name, record_id, result_path))
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	panel = window.history_panel
	panel.search_input.setText("alpha")
	panel.date_filter_checkbox.setChecked(True)
	panel.from_date_edit.setDate(QDate.currentDate())
	panel.to_date_edit.setDate(QDate.currentDate())
	qtbot.mouseClick(panel.search_button, Qt.LeftButton)
	assert panel.table.rowCount() == 1
	qtbot.mouseClick(panel.select_all_button, Qt.LeftButton)
	assert panel.selected_record_ids() == [entries[0][1]]
	dialogs["answer"] = QMessageBox.Yes

	_click_delete(qtbot, window)

	assert window.database_manager.get_record_by_id(entries[0][1]) is None
	assert window.database_manager.get_record_by_id(entries[1][1]) is not None
	assert not entries[0][2].exists()
	assert entries[1][2].is_file()
	assert panel.search_input.text() == "alpha"
	assert panel.date_filter_checkbox.isChecked()
	assert panel.table.rowCount() == 0
	assert panel.table_stack.currentWidget() is panel.empty_label


def test_database_delete_error_shows_warning_and_keeps_result_file(
	qtbot, tmp_path: Path, dialogs: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
	window = _create_window(qtbot, tmp_path)
	image_path = tmp_path / "image.png"
	result_path = window.results_dir / "result.png"
	_save_image(image_path)
	_save_image(result_path)
	record_id = _insert_record(window, image_path, result_path)
	_reload_history_through_ui(qtbot, window)
	_open_history(qtbot, window)
	_select_id(qtbot, window, record_id)
	dialogs["answer"] = QMessageBox.Yes
	monkeypatch.setattr(
		window.database_manager,
		"delete_records",
		lambda _ids: (_ for _ in ()).throw(DatabaseError("delete failed")),
	)

	_click_delete(qtbot, window)

	assert window.database_manager.get_record_by_id(record_id) is not None
	assert result_path.is_file()
	assert dialogs["warnings"]
	assert window.history_panel.selected_record_id() == record_id
