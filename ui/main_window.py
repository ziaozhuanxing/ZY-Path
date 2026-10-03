"""Main window layout for the ZY-Path application."""

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QSplitter,
	QTabWidget,
	QVBoxLayout,
	QWidget,
)

from ui.action_panel import ActionPanel
from ui.history_panel import HistoryPanel
from ui.inference_panel import InferencePanel
from ui.result_panel import ResultPanel
from data.database_manager import DatabaseError, DatabaseManager


class MainWindow(QMainWindow):
	"""Show the three-region application shell."""

	def __init__(
		self,
		parent: QWidget | None = None,
		db_path: str | Path | None = None,
	) -> None:
		super().__init__(parent)
		self.setWindowTitle("ZY-Path")
		self.setMinimumSize(1366, 768)

		central_widget = QWidget(self)
		central_layout = QVBoxLayout(central_widget)
		central_layout.setContentsMargins(0, 0, 0, 0)
		central_layout.setSpacing(0)

		header = QWidget(central_widget)
		header.setObjectName("titleBar")
		header.setAttribute(Qt.WA_StyledBackground, True)
		header.setFixedHeight(88)
		header_layout = QVBoxLayout(header)
		header_layout.setContentsMargins(24, 10, 24, 10)
		header_layout.setSpacing(2)
		title = QLabel("ZY-Path", header)
		title.setObjectName("titleText")
		subtitle = QLabel("Histopathology image analysis", header)
		subtitle.setObjectName("subtitleText")
		header_layout.addWidget(title)
		header_layout.addWidget(subtitle)
		header_layout.addStretch()
		central_layout.addWidget(header)

		self.splitter = QSplitter(Qt.Horizontal, central_widget)
		self.splitter.setHandleWidth(8)
		self.inference_panel = InferencePanel(self.splitter)
		self.inference_panel.setFixedWidth(280)

		self.tabs = QTabWidget(self.splitter)
		self.tabs.setMinimumWidth(500)
		self.tabs.setObjectName("tabRegion")
		self.result_panel = ResultPanel(self.tabs)
		self.history_panel = HistoryPanel(self.tabs)
		self.tabs.addTab(self.result_panel, "Inference")
		self.tabs.addTab(self.history_panel, "History")

		self.action_panel = ActionPanel(self.splitter)
		self.action_panel.setFixedWidth(240)

		self.splitter.addWidget(self.inference_panel)
		self.splitter.addWidget(self.tabs)
		self.splitter.addWidget(self.action_panel)
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)
		self.splitter.setStretchFactor(2, 0)
		central_layout.addWidget(self.splitter, 1)

		self.setCentralWidget(central_widget)
		status_bar = self.statusBar()
		status_bar.showMessage("Ready")
		self.inference_panel.run_requested.connect(self._show_run_requested)
		self.history_panel.search_requested.connect(self._search_history)
		self.history_panel.clear_requested.connect(self._clear_history_filters)
		self.history_panel.record_activated.connect(self._show_record_activated)
		self.history_panel.selection_changed.connect(self._update_rerun_enabled)

		self.database_manager: DatabaseManager | None = None
		try:
			self.database_manager = DatabaseManager(db_path)
			self._load_all_history()
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))

	def _show_run_requested(
		self, model_path: str, use_builtin: bool, image_path: str, task_type: str
	) -> None:
		"""Show that inference is not connected yet."""
		self.statusBar().showMessage("Run requested (inference not connected yet)")

	def _load_all_history(self) -> None:
		if self.database_manager is None:
			return
		try:
			self.history_panel.set_records(self.database_manager.get_all_records())
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))

	def _search_history(
		self, keyword: str, start_iso: object, end_iso: object
	) -> None:
		if self.database_manager is None:
			self.statusBar().showMessage("The history database is not available.")
			return
		start = start_iso if isinstance(start_iso, str) else None
		end = end_iso if isinstance(end_iso, str) else None
		try:
			records = self.database_manager.search(keyword, start=start, end=end)
			self.history_panel.set_records(records)
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))

	def _clear_history_filters(self) -> None:
		self.history_panel.reset_filters()
		self._load_all_history()

	def _show_record_activated(self, record_id: int) -> None:
		self.statusBar().showMessage(
			f"Opened record #{record_id} (display not connected yet)"
		)

	def _update_rerun_enabled(self, record_id: object) -> None:
		self.action_panel.set_rerun_enabled(record_id is not None)
