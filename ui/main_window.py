"""Main window layout for the ZY-Path application."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QMessageBox,
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
from data.export_manager import ExportError, ExportManager
from core.inference_engine import InferenceEngine
from core.model_loader import ModelLoader, ModelValidationError
from utils.paths import app_data_dir, resource_path


class MainWindow(QMainWindow):
	"""Show the three-region application shell."""

	def __init__(
		self,
		parent: QWidget | None = None,
		db_path: str | Path | None = None,
		builtin_model_path: str | Path | None = None,
		results_dir: str | Path | None = None,
	) -> None:
		super().__init__(parent)
		self.setWindowTitle("ZY-Path")
		self.setMinimumSize(1366, 768)
		self.builtin_model_path = (
			Path(builtin_model_path)
			if builtin_model_path is not None
			else resource_path("models/builtin_model.pth")
		)
		self.results_dir = (
			Path(results_dir)
			if results_dir is not None
			else app_data_dir() / "results"
		)
		self.export_manager = ExportManager()
		self._inference_engine: InferenceEngine | None = None
		self._active_use_builtin = False

		central_widget = QWidget(self)
		central_layout = QVBoxLayout(central_widget)
		central_layout.setContentsMargins(0, 0, 0, 0)
		central_layout.setSpacing(0)

		header = QWidget(central_widget)
		header.setObjectName("titleBar")
		header.setAttribute(Qt.WA_StyledBackground, True)
		header_layout = QVBoxLayout(header)
		header_layout.setContentsMargins(24, 10, 24, 10)
		header_layout.setSpacing(2)
		title = QLabel("ZY-Path", header)
		title.setObjectName("titleText")
		title_font = QFont("Segoe UI", 20, QFont.Bold)
		title.setFont(title_font)
		title.setAlignment(Qt.AlignVCenter)
		title.ensurePolished()
		title.updateGeometry()
		title.setMinimumHeight(QFontMetrics(title_font).height() + 4)
		subtitle = QLabel("Histopathology image analysis", header)
		subtitle.setObjectName("subtitleText")
		subtitle_font = QFont("Segoe UI", 10)
		subtitle.setFont(subtitle_font)
		subtitle.setAlignment(Qt.AlignVCenter)
		subtitle.ensurePolished()
		subtitle.updateGeometry()
		subtitle.setMinimumHeight(QFontMetrics(subtitle_font).height() + 4)
		header_layout.addWidget(title)
		header_layout.addWidget(subtitle)
		_, top_margin, _, bottom_margin = header_layout.getContentsMargins()
		header.setMinimumHeight(
			title.minimumHeight()
			+ subtitle.minimumHeight()
			+ top_margin
			+ bottom_margin
			+ header_layout.spacing()
		)
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
		self.inference_panel.custom_model_chosen.connect(self._validate_custom_model)
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
		QTimer.singleShot(0, self._load_builtin_model)

	def _show_run_requested(
		self, model_path: str, use_builtin: bool, image_path: str, task_type: str
	) -> None:
		"""Start inference unless another request is still running."""
		if self._inference_engine is not None:
			return
		selected_model_path = self.builtin_model_path if use_builtin else Path(model_path)
		self._active_use_builtin = use_builtin
		self.inference_panel.set_running(True)
		self.statusBar().showMessage("Running inference...")
		engine = InferenceEngine(
			selected_model_path,
			image_path,
			task_type,
			class_labels=None,
		)
		self._inference_engine = engine
		engine.result_ready.connect(self._show_inference_result)
		engine.error_occurred.connect(self._show_inference_error)
		engine.finished.connect(self._inference_finished)
		engine.start()

	def _load_builtin_model(self) -> None:
		"""Validate the configured built-in model after the window is created."""
		self.statusBar().showMessage("Loading built-in model...")
		if not self.builtin_model_path.is_file():
			self.inference_panel.set_model_status(
				"Built-in model file not found. Untick the box and use Browse to load your own model.",
				False,
			)
			self.statusBar().showMessage("Ready")
			return
		try:
			loaded_model = ModelLoader().load_with_info(self.builtin_model_path)
			validation = ModelLoader.validate(loaded_model.model)
			self.inference_panel.set_model_status(
				f"Built-in model: ready ({validation.num_classes} classes)",
				True,
			)
		except (ModelValidationError, ValueError) as error:
			self.inference_panel.set_model_status(str(error), False)
		finally:
			self.statusBar().showMessage("Ready")

	def _validate_custom_model(self, model_path: str) -> None:
		"""Validate a selected custom model and select its detected task."""
		try:
			loaded_model = ModelLoader().load_with_info(model_path)
			validation = ModelLoader.validate(loaded_model.model)
			self.inference_panel.set_model_status(
				"Custom model: valid, "
				f"{validation.task_type.capitalize()} ({validation.num_classes} classes)",
				True,
			)
			self.inference_panel.set_task(validation.task_type)
		except (ModelValidationError, ValueError) as error:
			self.inference_panel.set_model_status(str(error), False)

	def _show_inference_result(self, result: dict) -> None:
		"""Display an inference result, save its image, and add its history row."""
		image_path = str(result["image_path"])
		self.result_panel.show_image(image_path)
		if result["task_type"] == "classification":
			self.result_panel.show_classification(
				result["label"],
				result["confidence"],
				result["probabilities"],
				result["class_labels"],
			)
			result_image = self.result_panel.get_result_figure()
		else:
			self.result_panel.show_segmentation(
				result["blended"].convert("RGBA"),
				result["legend_items"],
			)
			result_image = result["blended"]

		self.action_panel.set_metadata(
			str(result["model_name"]),
			Path(image_path).name,
			self._local_timestamp(str(result["timestamp"])),
		)
		result_path: str | None = None
		try:
			self.results_dir.mkdir(parents=True, exist_ok=True)
			result_path = self._new_result_path(str(result["timestamp"]))
			self.export_manager.export_png(result_image, result_path)
			result_path = str(result_path.resolve())
		except (ExportError, OSError, ValueError) as error:
			result_path = None
			self.statusBar().showMessage(str(error))

		if self.database_manager is None:
			self.statusBar().showMessage("The history database is not available.")
			return
		model_path = (
			"builtin"
			if self._active_use_builtin
			else str(Path(str(result["model_path"])).resolve())
		)
		result_label = result["label"] if result["task_type"] == "classification" else None
		confidence = result["confidence"] if result["task_type"] == "classification" else None
		try:
			self.database_manager.insert_record(
				str(Path(image_path).resolve()),
				model_path,
				str(result["task_type"]),
				result_label,
				confidence,
				result_path,
			)
			self.history_panel.set_records(self.database_manager.get_all_records())
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))
			return
		if result_path is not None:
			self.statusBar().showMessage(f"Done in {float(result['elapsed_seconds']):.1f} s")

	def _show_inference_error(self, message: str) -> None:
		"""Show a friendly inference error and keep it in the status bar."""
		QMessageBox.warning(self, "Inference failed", message)
		self.statusBar().showMessage(message)

	def _inference_finished(self) -> None:
		"""Restore the inference controls after the worker stops."""
		self.inference_panel.set_running(False)
		self._inference_engine = None

	def _new_result_path(self, timestamp: str) -> Path:
		"""Create a unique PNG path using the result's UTC timestamp."""
		utc_timestamp = datetime.fromisoformat(timestamp).astimezone(timezone.utc)
		filename = f"{utc_timestamp:%Y%m%dT%H%M%S%fZ}_{uuid4().hex[:8]}.png"
		return self.results_dir / filename

	@staticmethod
	def _local_timestamp(timestamp: str) -> str:
		"""Format a UTC ISO timestamp in local time for the session panel."""
		return datetime.fromisoformat(timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S")

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
