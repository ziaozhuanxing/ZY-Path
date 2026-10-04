"""Tests for history filtering, display, and database integration."""

from datetime import date, datetime, time, timezone

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtTest import QSignalSpy

from data.database_manager import DatabaseManager
from ui.history_panel import HistoryPanel
from ui.main_window import MainWindow


def sample_records() -> list[dict]:
	return [
		{
			"id": 21,
			"timestamp": "2024-04-03T12:34:56+00:00",
			"image_path": "C:/images/sample.png",
			"model_path": "C:/models/custom.pt",
			"task_type": "classification",
			"result_label": "benign",
			"confidence": 0.947,
		},
		{
			"id": 22,
			"timestamp": "2024-04-04T01:02:03Z",
			"image_path": "C:/images/segment.png",
			"model_path": "Built-in model",
			"task_type": "segmentation",
			"result_label": None,
			"confidence": None,
		},
	]


def test_empty_table_shows_message(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)

	assert panel.table.rowCount() == 0
	assert panel.empty_label.text() == "No records found"
	assert panel.table_stack.currentWidget() is panel.empty_label


def test_set_records_formats_values_and_local_timestamp(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	first_timestamp = datetime.fromisoformat(
		"2024-04-03T12:34:56+00:00"
	).astimezone().strftime("%Y-%m-%d %H:%M:%S")

	assert panel.table.rowCount() == 2
	assert panel.table.columnCount() == 7
	assert [panel.table.horizontalHeaderItem(i).text() for i in range(7)] == [
		"ID",
		"Timestamp",
		"Image Filename",
		"Model Name",
		"Task",
		"Result/Label",
		"Confidence",
	]
	assert [panel.table.item(0, column).text() for column in range(7)] == [
		"21",
		first_timestamp,
		"sample.png",
		"custom.pt",
		"Classification",
		"benign",
		"94.7 %",
	]
	assert [panel.table.item(1, column).text() for column in range(7)] == [
		"22",
		datetime.fromisoformat("2024-04-04T01:02:03+00:00")
		.astimezone()
		.strftime("%Y-%m-%d %H:%M:%S"),
		"segment.png",
		"Built-in model",
		"Segmentation",
		"-",
		"-",
	]
	assert panel.table.item(0, 0).font().family() == "Consolas"
	assert panel.table.item(0, 1).font().family() == "Consolas"
	assert panel.table.item(0, 6).font().family() == "Consolas"
	assert panel.table_stack.currentWidget() is panel.table


def test_search_emits_local_date_bounds_as_utc(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.date_filter_checkbox.setChecked(True)
	panel.from_date_edit.setDate(QDate(2024, 4, 3))
	panel.to_date_edit.setDate(QDate(2024, 4, 5))
	panel.search_input.setText("sample")
	spy = QSignalSpy(panel.search_requested)

	qtbot.mouseClick(panel.search_button, Qt.LeftButton)

	assert len(spy) == 1
	keyword, start_iso, end_iso = spy[0]
	assert keyword == "sample"
	start_expected = datetime.combine(date(2024, 4, 3), time.min).astimezone(
		timezone.utc
	)
	end_expected = datetime.combine(
		date(2024, 4, 5), time(23, 59, 59)
	).astimezone(timezone.utc)
	assert datetime.fromisoformat(start_iso) == start_expected
	assert datetime.fromisoformat(end_iso) == end_expected


def test_search_without_date_filter_emits_no_date_bounds(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	spy = QSignalSpy(panel.search_requested)

	panel.search_input.returnPressed.emit()

	assert len(spy) == 1
	assert spy[0] == ["", None, None]


def test_invalid_date_range_does_not_emit_search(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.date_filter_checkbox.setChecked(True)
	panel.from_date_edit.setDate(QDate(2024, 4, 6))
	panel.to_date_edit.setDate(QDate(2024, 4, 5))
	spy = QSignalSpy(panel.search_requested)

	panel.search_button.click()

	assert len(spy) == 0
	assert panel.validation_label.text() == "From date must be on or before To date."
	assert not panel.validation_label.isHidden()


def test_selection_and_double_click_emit_record_ids(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	panel.resize(900, 450)
	panel.show()
	qtbot.waitExposed(panel)
	selection_spy = QSignalSpy(panel.selection_changed)
	activation_spy = QSignalSpy(panel.record_activated)

	panel.table.selectRow(1)
	assert panel.selected_record_id() == 22
	assert selection_spy[-1] == [22]

	item = panel.table.item(1, 2)
	panel.table.scrollToItem(item)
	cell_rect = panel.table.visualItemRect(item)
	assert cell_rect.isValid()
	assert panel.table.indexAt(cell_rect.center()).row() == 1
	qtbot.mouseClick(panel.table.viewport(), Qt.LeftButton, pos=cell_rect.center())
	qtbot.mouseDClick(
		panel.table.viewport(), Qt.LeftButton, pos=cell_rect.center(), delay=50
	)
	assert activation_spy[-1] == [22]

	panel.table.clearSelection()
	assert panel.selected_record_id() is None
	assert selection_spy[-1] == [None]


def test_multi_selection_updates_delete_button_and_selection_signal(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	panel.resize(900, 450)
	panel.show()
	qtbot.waitExposed(panel)
	selection_spy = QSignalSpy(panel.selection_changed)

	assert panel.table.selectionMode() == QAbstractItemView.ExtendedSelection
	assert panel.delete_selected_button.text() == "Delete Selected (0)"
	assert not panel.delete_selected_button.isEnabled()

	first_cell = panel.table.visualItemRect(panel.table.item(0, 0)).center()
	second_cell = panel.table.visualItemRect(panel.table.item(1, 0)).center()
	qtbot.mouseClick(panel.table.viewport(), Qt.LeftButton, pos=first_cell)
	assert panel.delete_selected_button.text() == "Delete Selected (1)"
	assert panel.delete_selected_button.isEnabled()
	assert panel.selected_record_ids() == [21]
	assert selection_spy[-1] == [21]

	qtbot.mouseClick(
		panel.table.viewport(),
		Qt.LeftButton,
		pos=second_cell,
		modifier=Qt.ControlModifier,
	)
	assert panel.delete_selected_button.text() == "Delete Selected (2)"
	assert panel.selected_record_ids() == [21, 22]
	assert panel.selected_record_id() is None
	assert selection_spy[-1] == [None]

	panel.table.clearSelection()
	assert panel.delete_selected_button.text() == "Delete Selected (0)"
	assert not panel.delete_selected_button.isEnabled()
	assert selection_spy[-1] == [None]


def test_select_all_and_delete_selected_button_emit_displayed_ids(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	panel.resize(900, 450)
	panel.show()
	qtbot.waitExposed(panel)
	delete_spy = QSignalSpy(panel.delete_requested)

	assert panel.select_all_button.toolTip() == "Select all records shown"
	qtbot.mouseClick(panel.select_all_button, Qt.LeftButton)
	assert panel.selected_record_ids() == [21, 22]
	assert panel.delete_selected_button.text() == "Delete Selected (2)"
	qtbot.mouseClick(panel.delete_selected_button, Qt.LeftButton)
	assert list(delete_spy) == [[ [21, 22] ]]


def test_select_record_replaces_multi_selection_without_activation(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	panel.resize(900, 450)
	panel.show()
	qtbot.waitExposed(panel)
	panel.table.selectAll()
	activation_spy = QSignalSpy(panel.record_activated)
	selection_spy = QSignalSpy(panel.selection_changed)

	assert panel.select_record(22)

	assert panel.selected_record_ids() == [22]
	assert list(selection_spy) == [[22]]
	assert len(activation_spy) == 0
	assert panel.delete_selected_button.text() == "Delete Selected (1)"


def test_delete_key_emits_delete_requested(qtbot) -> None:
	panel = HistoryPanel()
	qtbot.addWidget(panel)
	panel.set_records(sample_records())
	panel.resize(900, 450)
	panel.show()
	qtbot.waitExposed(panel)
	panel.table.selectRow(0)
	delete_spy = QSignalSpy(panel.delete_requested)

	qtbot.keyClick(panel.table.viewport(), Qt.Key_Delete)

	assert list(delete_spy) == [[[21]]]


def test_select_all_only_selects_filtered_rows(qtbot, tmp_path) -> None:
	db_path = tmp_path / "history.db"
	manager = DatabaseManager(db_path)
	alpha_id = manager.insert_record(
		"images/alpha.png", "models/model.pt", "classification"
	)
	manager.insert_record("images/beta.png", "models/model.pt", "classification")
	window = MainWindow(db_path=db_path)
	qtbot.addWidget(window)
	window.show()
	qtbot.waitExposed(window)
	window.history_panel.search_input.setText("alpha")
	qtbot.mouseClick(window.history_panel.search_button, Qt.LeftButton)
	qtbot.mouseClick(window.history_panel.select_all_button, Qt.LeftButton)

	assert window.history_panel.selected_record_ids() == [alpha_id]


def test_main_window_loads_searches_and_resets_database_records(qtbot, tmp_path) -> None:
	db_path = tmp_path / "history.db"
	manager = DatabaseManager(db_path)
	first_id = manager.insert_record(
		"images/alpha.png", "models/custom.pt", "classification", "benign", 0.947
	)
	manager.insert_record(
		"images/beta.png", "Built-in model", "segmentation"
	)
	window = MainWindow(db_path=db_path)
	qtbot.addWidget(window)

	assert window.history_panel.table.rowCount() == 2
	first_row = next(
		row
		for row in range(window.history_panel.table.rowCount())
		if window.history_panel.table.item(row, 0).data(Qt.UserRole) == first_id
	)
	window.history_panel.table.selectRow(first_row)
	assert window.action_panel.rerun_button.isEnabled()
	assert window.history_panel.selected_record_id() == first_id

	window.history_panel.search_input.setText("alpha")
	window.history_panel.search_button.click()
	assert window.history_panel.table.rowCount() == 1
	assert window.history_panel.table.item(0, 2).text() == "alpha.png"

	window.history_panel.clear_button.click()
	assert window.history_panel.search_input.text() == ""
	assert not window.history_panel.date_filter_checkbox.isChecked()
	assert window.history_panel.table.rowCount() == 2
	assert not window.action_panel.rerun_button.isEnabled()


def test_main_window_reports_database_initialization_error(qtbot, tmp_path) -> None:
	not_a_directory = tmp_path / "file"
	not_a_directory.write_text("not a directory", encoding="utf-8")

	window = MainWindow(db_path=not_a_directory / "history.db")
	qtbot.addWidget(window)

	assert window.database_manager is None
	assert "database" in window.statusBar().currentMessage().lower()
	assert window.history_panel.table.rowCount() == 0