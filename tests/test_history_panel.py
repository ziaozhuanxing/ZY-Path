"""Tests for history filtering, display, and database integration."""

from datetime import date, datetime, time, timezone

from PyQt5.QtCore import QDate, Qt
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