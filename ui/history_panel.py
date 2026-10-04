"""Search and display saved inference records."""

from datetime import date, datetime, time, timezone
from pathlib import Path

from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
	QAbstractItemView,
	QCheckBox,
	QDateEdit,
	QGridLayout,
	QHeaderView,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QPushButton,
	QStackedWidget,
	QTableWidget,
	QTableWidgetItem,
	QVBoxLayout,
	QWidget,
)

from ui.theme import MONO_FONT


class HistoryPanel(QWidget):
	"""Let the user filter, inspect, and select history records."""

	search_requested = pyqtSignal(str, object, object)
	clear_requested = pyqtSignal()
	record_activated = pyqtSignal(int)
	selection_changed = pyqtSignal(object)

	HEADERS = [
		"ID",
		"Timestamp",
		"Image Filename",
		"Model Name",
		"Task",
		"Result/Label",
		"Confidence",
	]

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("HistoryPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)

		layout = QVBoxLayout(self)
		layout.setContentsMargins(16, 16, 16, 16)
		layout.setSpacing(10)

		search_row = QHBoxLayout()
		self.search_input = QLineEdit(self)
		self.search_input.setObjectName("historySearchInput")
		self.search_input.setPlaceholderText("Search by image or model name")
		self.search_input.setToolTip("Search image and model paths by name.")
		self.search_button = QPushButton("Search", self)
		self.search_button.setObjectName("historySearchButton")
		self.search_button.setToolTip("Search history using the current filters.")
		self.clear_button = QPushButton("Clear Filter", self)
		self.clear_button.setObjectName("historyClearButton")
		self.clear_button.setToolTip("Clear search and date filters.")
		search_row.addWidget(self.search_input, 1)
		search_row.addWidget(self.search_button)
		search_row.addWidget(self.clear_button)
		layout.addLayout(search_row)

		date_row = QHBoxLayout()
		self.date_filter_checkbox = QCheckBox("Filter by date", self)
		self.date_filter_checkbox.setObjectName("dateFilterCheckbox")
		self.date_filter_checkbox.setToolTip("Limit results to the selected local dates.")
		self.from_label = QLabel("From", self)
		self.from_label.setToolTip("Start date, using local time.")
		self.from_date_edit = self._create_date_edit("Start date in local time.")
		self.to_label = QLabel("To", self)
		self.to_label.setToolTip("End date, using local time.")
		self.to_date_edit = self._create_date_edit("End date in local time.")
		date_row.addWidget(self.date_filter_checkbox)
		date_row.addSpacing(8)
		date_row.addWidget(self.from_label)
		date_row.addWidget(self.from_date_edit)
		date_row.addWidget(self.to_label)
		date_row.addWidget(self.to_date_edit)
		date_row.addStretch()
		layout.addLayout(date_row)

		self.validation_label = QLabel(self)
		self.validation_label.setObjectName("historyValidationLabel")
		self.validation_label.setToolTip("Date filter validation message.")
		self.validation_label.hide()
		layout.addWidget(self.validation_label)

		self.table_stack = QStackedWidget(self)
		self.table_stack.setObjectName("historyTableStack")
		self.table = QTableWidget(0, len(self.HEADERS), self.table_stack)
		self.table.setObjectName("historyTable")
		self.table.setHorizontalHeaderLabels(self.HEADERS)
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSelectionMode(QAbstractItemView.SingleSelection)
		self.table.setAlternatingRowColors(True)
		self.table.verticalHeader().setVisible(False)
		header = self.table.horizontalHeader()
		header.setSectionResizeMode(QHeaderView.ResizeToContents)
		header.setStretchLastSection(True)
		self.table_stack.addWidget(self.table)

		self.empty_label = QLabel("No records found", self.table_stack)
		self.empty_label.setObjectName("historyEmptyLabel")
		self.empty_label.setAlignment(Qt.AlignCenter)
		self.empty_label.setToolTip("No history records match the current filters.")
		self.table_stack.addWidget(self.empty_label)
		self.table_stack.setCurrentWidget(self.empty_label)
		layout.addWidget(self.table_stack, 1)

		self.date_filter_checkbox.toggled.connect(self._set_date_filter_enabled)
		self.search_button.clicked.connect(self._emit_search_requested)
		self.search_input.returnPressed.connect(self._emit_search_requested)
		self.clear_button.clicked.connect(self.clear_requested.emit)
		self.table.itemSelectionChanged.connect(self._emit_selection_changed)
		self.table.itemDoubleClicked.connect(self._emit_record_activated)
		self._set_date_filter_enabled(False)

	def set_records(self, records: list[dict]) -> None:
		"""Replace table contents with database records."""
		previous_record_id = self.selected_record_id()
		self.table.blockSignals(True)
		self.table.clearContents()
		self.table.setRowCount(len(records))
		for row, record in enumerate(records):
			values = self._record_values(record)
			for column, value in enumerate(values):
				item = QTableWidgetItem(value)
				item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
				if column in (0, 1, 6):
					item.setFont(QFont(MONO_FONT))
				if column == 0:
					item.setData(Qt.UserRole, int(record["id"]))
				self.table.setItem(row, column, item)
		self.table.blockSignals(False)
		self.table_stack.setCurrentWidget(
			self.table if records else self.empty_label
		)
		current_record_id = self.selected_record_id()
		if previous_record_id != current_record_id:
			self.selection_changed.emit(current_record_id)

	def selected_record_id(self) -> int | None:
		"""Return the selected record ID, if a row is selected."""
		selected_rows = self.table.selectionModel().selectedRows()
		if not selected_rows:
			return None
		item = self.table.item(selected_rows[0].row(), 0)
		return int(item.data(Qt.UserRole)) if item is not None else None

	def select_record(self, record_id: int) -> bool:
		"""Select a record row without activating it or switching tabs."""
		for row in range(self.table.rowCount()):
			item = self.table.item(row, 0)
			if item is None or item.data(Qt.UserRole) != record_id:
				continue

			signals_were_blocked = self.table.blockSignals(True)
			try:
				self.table.selectRow(row)
				self.table.scrollToItem(item, QAbstractItemView.EnsureVisible)
			finally:
				self.table.blockSignals(signals_were_blocked)
			self.selection_changed.emit(record_id)
			return True
		return False

	def reset_filters(self) -> None:
		"""Clear the keyword and date filter controls."""
		self.search_input.clear()
		self.date_filter_checkbox.setChecked(False)
		self.from_date_edit.setDate(QDate.currentDate())
		self.to_date_edit.setDate(QDate.currentDate())
		self.validation_label.clear()
		self.validation_label.hide()

	def _create_date_edit(self, tooltip: str) -> QDateEdit:
		date_edit = QDateEdit(self)
		date_edit.setCalendarPopup(True)
		date_edit.setDisplayFormat("yyyy-MM-dd")
		date_edit.setDate(QDate.currentDate())
		date_edit.setToolTip(tooltip)
		date_edit.setEnabled(False)
		return date_edit

	def _set_date_filter_enabled(self, enabled: bool) -> None:
		for widget in (
			self.from_label,
			self.from_date_edit,
			self.to_label,
			self.to_date_edit,
		):
			widget.setEnabled(enabled)
		if not enabled:
			self.validation_label.clear()
			self.validation_label.hide()

	def _emit_search_requested(self) -> None:
		self.validation_label.clear()
		self.validation_label.hide()
		start_iso = None
		end_iso = None
		if self.date_filter_checkbox.isChecked():
			start_date = self.from_date_edit.date().toPyDate()
			end_date = self.to_date_edit.date().toPyDate()
			if start_date > end_date:
				self.validation_label.setText(
					"From date must be on or before To date."
				)
				self.validation_label.show()
				return
			start_iso = self._local_date_to_utc_iso(start_date, time.min)
			end_iso = self._local_date_to_utc_iso(
				end_date, time(23, 59, 59)
			)
		self.search_requested.emit(
			self.search_input.text().strip(), start_iso, end_iso
		)

	@staticmethod
	def _local_date_to_utc_iso(local_date: date, local_time: time) -> str:
		local_datetime = datetime.combine(local_date, local_time).astimezone()
		return local_datetime.astimezone(timezone.utc).isoformat(timespec="seconds")

	def _emit_selection_changed(self) -> None:
		self.selection_changed.emit(self.selected_record_id())

	def _emit_record_activated(self, item: QTableWidgetItem) -> None:
		record_id = self.table.item(item.row(), 0).data(Qt.UserRole)
		self.record_activated.emit(int(record_id))

	def _record_values(self, record: dict) -> list[str]:
		confidence = record.get("confidence")
		confidence_text = (
			f"{float(confidence) * 100:.1f} %" if confidence is not None else "-"
		)
		return [
			str(record.get("id", "-")),
			self._local_timestamp(record.get("timestamp")),
			self._filename(record.get("image_path")),
			self._model_name(record.get("model_path")),
			str(record.get("task_type") or "-").title(),
			str(record.get("result_label") or "-"),
			confidence_text,
		]

	@staticmethod
	def _local_timestamp(value: object) -> str:
		if not value:
			return "-"
		try:
			timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
			if timestamp.tzinfo is None:
				timestamp = timestamp.replace(tzinfo=timezone.utc)
			return timestamp.astimezone().strftime("%Y-%m-%d %H:%M:%S")
		except ValueError:
			return str(value)

	@staticmethod
	def _filename(value: object) -> str:
		return Path(str(value)).name if value else "-"

	@staticmethod
	def _model_name(value: object) -> str:
		model_path = str(value or "").strip()
		marker = model_path.replace("_", "-").casefold()
		if not model_path or marker in {
			"builtin",
			"built-in",
			"built-in-model",
			"__builtin__",
		}:
			return "Built-in model"
		return Path(model_path).name