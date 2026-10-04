"""Main window layout for the ZY-Path application."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (
	QLabel,
	QFileDialog,
	QMainWindow,
	QMessageBox,
	QSplitter,
	QTabWidget,
	QVBoxLayout,
	QWidget,
)
from PIL import Image

from ui.action_panel import ActionPanel
from ui.history_panel import HistoryPanel
from ui.inference_panel import InferencePanel
from ui.result_panel import ResultPanel
from data.database_manager import DatabaseError, DatabaseManager
from data.export_manager import ExportError, ExportManager
from core.inference_engine import InferenceEngine
from core.model_loader import ModelLoader, ModelValidationError
from utils.paths import app_data_dir, resource_path


logger = logging.getLogger(__name__)


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
		self._current_result: dict | None = None
		self._inference_engine: InferenceEngine | None = None
		self._active_use_builtin = False
		self._builtin_model_status: tuple[str, bool] | None = None
		self._builtin_model_task: str | None = None
		self._custom_model_status: tuple[str, bool] | None = None
		self._custom_model_task: str | None = None
		self._selected_history_record_id: int | None = None
		self.current_record_id: int | None = None

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
		self.splitter.setHandleWidth(6)
		self.splitter.setChildrenCollapsible(False)
		self.splitter.setStyleSheet(
			"QSplitter::handle:horizontal { background-color: #CBD5E0; }"
			"QSplitter::handle:horizontal:hover { background-color: #3182CE; }"
		)
		self.inference_panel = InferencePanel(self.splitter)
		self.inference_panel.setMaximumWidth(420)

		self.tabs = QTabWidget(self.splitter)
		self.tabs.setMinimumWidth(500)
		self.tabs.setObjectName("tabRegion")
		self.result_panel = ResultPanel(self.tabs)
		self.history_panel = HistoryPanel(self.tabs)
		self.tabs.addTab(self.result_panel, "Inference")
		self.tabs.addTab(self.history_panel, "History")

		self.action_panel = ActionPanel(self.splitter)
		self.action_panel.setMinimumWidth(200)
		self.action_panel.setMaximumWidth(360)

		self.splitter.addWidget(self.inference_panel)
		self.splitter.addWidget(self.tabs)
		self.splitter.addWidget(self.action_panel)
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)
		self.splitter.setStretchFactor(2, 0)
		self.splitter.setSizes([280, 500, 240])
		self.splitter.splitterMoved.connect(self.inference_panel._refresh_thumbnail)
		central_layout.addWidget(self.splitter, 1)

		self.setCentralWidget(central_widget)
		status_bar = self.statusBar()
		status_bar.showMessage("Ready")
		self.inference_panel.run_requested.connect(self._show_run_requested)
		self.inference_panel.custom_model_chosen.connect(self._validate_custom_model)
		self.inference_panel.use_builtin_changed.connect(
			self._handle_use_builtin_changed
		)
		self.history_panel.search_requested.connect(self._search_history)
		self.history_panel.clear_requested.connect(self._clear_history_filters)
		self.history_panel.record_activated.connect(self._show_record_activated)
		self.history_panel.selection_changed.connect(self._update_rerun_enabled)
		self.action_panel.rerun_requested.connect(self._handle_rerun_requested)
		self.action_panel.export_png_requested.connect(self._export_current_png)
		self.action_panel.export_pdf_requested.connect(self._export_current_pdf)

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
		"""Start inference from the Run button request."""
		self._start_inference(
			model_path,
			use_builtin,
			image_path,
			task_type,
			"Running inference...",
			"Running inference...",
		)

	def _start_inference(
		self,
		model_path: str,
		use_builtin: bool,
		image_path: str,
		task_type: str,
		status_message: str,
		busy_message: str,
	) -> bool:
		"""Start one inference request through the shared worker path."""
		if self._inference_engine is not None:
			self.statusBar().showMessage(busy_message)
			return False
		selected_model_path = self.builtin_model_path if use_builtin else Path(model_path)
		self._active_use_builtin = use_builtin
		self.inference_panel.set_running(True)
		self.statusBar().showMessage(status_message)
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
		return True

	def _load_builtin_model(self) -> None:
		"""Validate the configured built-in model after the window is created."""
		self.statusBar().showMessage("Loading built-in model...")
		if not self.builtin_model_path.is_file():
			self._builtin_model_status = (
				"Built-in model file not found. Untick the box and use Browse to load your own model.",
				False,
			)
			self._builtin_model_task = None
			self.inference_panel.set_model_status(*self._builtin_model_status)
			self.statusBar().showMessage("Ready")
			return
		try:
			loaded_model = ModelLoader().load_with_info(self.builtin_model_path)
			validation = ModelLoader.validate(loaded_model.model)
			self._builtin_model_status = (
				f"Built-in model: ready ({validation.num_classes} classes)",
				True,
			)
			self._builtin_model_task = validation.task_type
			self.inference_panel.set_model_status(*self._builtin_model_status)
		except (ModelValidationError, ValueError) as error:
			self._builtin_model_status = (str(error), False)
			self._builtin_model_task = None
			self.inference_panel.set_model_status(*self._builtin_model_status)
		finally:
			self.statusBar().showMessage("Ready")

	def _validate_custom_model(self, model_path: str) -> None:
		"""Validate a selected custom model and select its detected task."""
		try:
			loaded_model = ModelLoader().load_with_info(model_path)
			validation = ModelLoader.validate(loaded_model.model)
			self._custom_model_status = (
				"Custom model: valid, "
				f"{validation.task_type.capitalize()} ({validation.num_classes} classes)",
				True,
			)
			self._custom_model_task = validation.task_type
			self.inference_panel.set_model_status(*self._custom_model_status)
			self.inference_panel.set_task(validation.task_type)
		except (ModelValidationError, ValueError) as error:
			self._custom_model_status = (str(error), False)
			self._custom_model_task = None
			self.inference_panel.set_model_status(*self._custom_model_status)

	def _handle_use_builtin_changed(self, use_builtin: bool) -> None:
		"""Restore the cached status and task for the selected model."""
		if use_builtin:
			status = self._builtin_model_status or (
				"Built-in model validation is not available yet.",
				False,
			)
			task_type = self._builtin_model_task
		else:
			status = self._custom_model_status or (
				"No custom model selected",
				False,
			)
			task_type = self._custom_model_task

		self.inference_panel.set_model_status(*status)
		if task_type is not None:
			self.inference_panel.set_task(task_type)

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
			None,
		)
		self.current_record_id = None
		local_timestamp = self._local_timestamp(str(result["timestamp"]))
		result_path: str | None = None
		try:
			self.results_dir.mkdir(parents=True, exist_ok=True)
			result_path = self._new_result_path(str(result["timestamp"]))
			self.export_manager.export_png(result_image, result_path)
			result_path = str(result_path.resolve())
		except (ExportError, OSError, ValueError) as error:
			result_path = None
			self.statusBar().showMessage(str(error))
		if result_path is not None:
			result_label = (
				str(result["label"])
				if result["task_type"] == "classification"
				else None
			)
			confidence = (
				float(result["confidence"])
				if result["task_type"] == "classification"
				else None
			)
			metadata = {
				"model_name": str(result["model_name"]),
				"task_type": str(result["task_type"]),
				"timestamp": local_timestamp,
				"image_path": str(Path(image_path).resolve()),
				"result_label": result_label,
				"confidence": confidence,
			}
			self._current_result = {
				"original_image_path": str(Path(image_path).resolve()),
				"result_image_path": result_path,
				"metadata": metadata,
			}
			self.action_panel.set_result_available(True)
		else:
			self._current_result = None
			self.action_panel.set_result_available(False)

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
			record_id = self.database_manager.insert_record(
				str(Path(image_path).resolve()),
				model_path,
				str(result["task_type"]),
				result_label,
				confidence,
				result_path,
			)
			self.history_panel.set_records(self.database_manager.get_all_records())
			self.history_panel.select_record(record_id)
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))
			return
		self.current_record_id = record_id
		self.action_panel.set_metadata(
			str(result["model_name"]),
			Path(image_path).name,
			local_timestamp,
			record_id,
		)
		if result_path is not None:
			self.statusBar().showMessage(f"Done in {float(result['elapsed_seconds']):.1f} s")

	def _handle_rerun_requested(self) -> None:
		"""Validate and immediately re-run the selected history record."""
		if self._inference_engine is not None:
			self.statusBar().showMessage("Inference is already running")
			return

		try:
			record_id = self.history_panel.selected_record_id()
			if record_id is None:
				record_id = self._selected_history_record_id
			if record_id is None:
				self.statusBar().showMessage("Select a history record first")
				return
			if self.database_manager is None:
				self.statusBar().showMessage("The history database is not available.")
				return

			record = self.database_manager.get_record_by_id(record_id)
			if record is None:
				self.statusBar().showMessage(
					f"Record #{record_id} could not be found."
				)
				return

			image_path = str(record.get("image_path") or "")
			if not Path(image_path).is_file():
				message = f"The original image file no longer exists: {image_path}"
				QMessageBox.warning(self, "Re-run unavailable", message)
				self.statusBar().showMessage(message)
				return

			model_path = str(record.get("model_path") or "")
			model_marker = model_path.replace("_", "-").casefold()
			use_builtin = model_marker in {
				"builtin",
				"built-in",
				"built-in-model",
				"__builtin__",
			}
			if not use_builtin and not Path(model_path).is_file():
				message = f"The model file no longer exists: {model_path}"
				QMessageBox.warning(self, "Re-run unavailable", message)
				self.statusBar().showMessage(message)
				return

			task_type = str(record.get("task_type") or "")
			if task_type not in {"classification", "segmentation"}:
				self.statusBar().showMessage(
					"The selected history record has an invalid task type."
				)
				return

			if use_builtin:
				builtin_status = self._builtin_model_status
				if builtin_status is None or not builtin_status[1]:
					message = (
						builtin_status[0]
						if builtin_status is not None
						else "The built-in model is not ready."
					)
					QMessageBox.warning(self, "Re-run unavailable", message)
					self.statusBar().showMessage(message)
					return
				model_task = self._builtin_model_task
			else:
				model_task = None

			self.inference_panel.set_use_builtin(use_builtin)
			if not use_builtin:
				self.inference_panel.set_custom_model(model_path)
				custom_status = self._custom_model_status
				if custom_status is None or not custom_status[1]:
					message = (
						custom_status[0]
						if custom_status is not None
						else "The selected model could not be validated."
					)
					QMessageBox.warning(self, "Re-run unavailable", message)
					self.statusBar().showMessage(message)
					return
				model_task = self._custom_model_task
			if model_task is not None and model_task != task_type:
				message = (
					f"This model produces {model_task} output; please select "
					f"{model_task.capitalize()}."
				)
				QMessageBox.warning(self, "Re-run unavailable", message)
				self.statusBar().showMessage(message)
				return

			self.inference_panel.set_image(image_path)
			self.inference_panel.set_task(task_type)
			self.tabs.setCurrentWidget(self.result_panel)
			self.result_panel.clear()
			self.result_panel.show_image(image_path)
			self._current_result = None
			self.action_panel.set_result_available(False)
			started = self._start_inference(
				model_path,
				use_builtin,
				image_path,
				task_type,
				f"Re-running record #{record_id}...",
				"Inference is already running",
			)
			if not started:
				return
		except Exception:
			logger.exception("Could not prepare the selected history record for re-run.")
			message = "The selected history record could not be re-run."
			QMessageBox.warning(self, "Re-run unavailable", message)
			self.statusBar().showMessage(message)

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
		if self.database_manager is None:
			self.statusBar().showMessage("The history database is not available.")
			return
		try:
			record = self.database_manager.get_record_by_id(record_id)
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))
			return
		if record is None:
			self.statusBar().showMessage(f"Record #{record_id} could not be found.")
			return
		self.history_panel.select_record(record_id)
		self.current_record_id = record_id

		image_path = str(record.get("image_path") or "")
		result_image_path = str(record.get("result_image_path") or "")
		model_path = str(record.get("model_path") or "")
		model_name = (
			"Built-in model"
			if model_path.replace("_", "-").casefold()
			in {"builtin", "built-in", "built-in-model", "__builtin__"}
			else Path(model_path).name or "-"
		)
		task_type = str(record.get("task_type") or "")
		label = record.get("result_label")
		confidence = record.get("confidence")
		timestamp = self._local_timestamp(str(record.get("timestamp") or ""))

		self.tabs.setCurrentWidget(self.result_panel)
		self.result_panel.show_image(image_path)
		if not image_path or not Path(image_path).is_file():
			self.result_panel.image_label.setText(
				f"Original image not found: {image_path or 'unknown file'}"
			)
		self.result_panel.show_stored_result(
			result_image_path,
			task_type,
			str(label) if label is not None else None,
			float(confidence) if confidence is not None else None,
		)
		self.action_panel.set_metadata(
			model_name,
			Path(image_path).name or "-",
			timestamp,
		record_id,
		)
		self._current_result = {
			"original_image_path": image_path,
			"result_image_path": result_image_path,
			"metadata": {
				"model_name": model_name,
				"task_type": task_type,
				"timestamp": timestamp,
				"image_path": image_path,
				"result_label": label,
				"confidence": confidence,
			},
		}
		self.action_panel.set_result_available(True)
		self.statusBar().showMessage(f"Showing record #{record_id}")

	def _export_current_png(self) -> None:
		"""Export the saved result image to a user-selected PNG path."""
		if self._current_result is None:
			return
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		output_path, _ = QFileDialog.getSaveFileName(
			self,
			"Export PNG",
			f"zypath_result_{timestamp}.png",
			"PNG files (*.png)",
		)
		if not output_path:
			return

		result_image_path = Path(self._current_result["result_image_path"])
		if not result_image_path.is_file():
			QMessageBox.warning(
				self,
				"Export failed",
				f"Stored result image not found: {result_image_path}",
			)
			return
		try:
			with Image.open(result_image_path) as opened_image:
				self.export_manager.export_png(opened_image.copy(), output_path)
		except (ExportError, OSError, RuntimeError, TypeError, ValueError):
			QMessageBox.warning(
				self,
				"Export failed",
				"The PNG image could not be saved. Check the selected path and try again.",
			)
			return
		self.statusBar().showMessage(f"Saved to {output_path}")

	def _export_current_pdf(self) -> None:
		"""Export the current source and saved result image as a PDF report."""
		if self._current_result is None:
			return
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		output_path, _ = QFileDialog.getSaveFileName(
			self,
			"Export PDF",
			f"zypath_report_{timestamp}.pdf",
			"PDF files (*.pdf)",
		)
		if not output_path:
			return

		original_path = Path(self._current_result["original_image_path"])
		result_path = Path(self._current_result["result_image_path"])
		for image_path, image_name in (
			(original_path, "Original image"),
			(result_path, "Stored result image"),
		):
			if not image_path.is_file():
				QMessageBox.warning(
					self,
					"Export failed",
					f"{image_name} not found: {image_path}",
				)
				return
		try:
			self.export_manager.export_pdf(
				output_path,
				original_path,
				result_path,
				self._current_result["metadata"],
			)
		except (ExportError, OSError, RuntimeError, TypeError, ValueError):
			QMessageBox.warning(
				self,
				"Export failed",
				"The PDF report could not be created. Check the files and selected path, then try again.",
			)
			return
		self.statusBar().showMessage(f"Saved to {output_path}")

	def _update_rerun_enabled(self, record_id: object) -> None:
		self._selected_history_record_id = (
			record_id if isinstance(record_id, int) else None
		)
		self.action_panel.set_rerun_enabled(
			record_id is not None,
			self._selected_history_record_id,
		)
