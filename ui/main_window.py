"""Main window layout for the ZY-Path application."""

import logging
import tempfile
import json
from datetime import datetime, time, timezone
from pathlib import Path
from uuid import uuid4

from PyQt5.QtCore import QSettings, QSize, QTimer, Qt, QRect, QEvent
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QPixmap
from PyQt5.QtWidgets import (
	QLabel,
	QFileDialog,
	QCheckBox,
	QApplication,
	QMainWindow,
	QMessageBox,
	QProgressBar,
	QSplitter,
	QTabWidget,
	QToolButton,
	QHBoxLayout,
	QVBoxLayout,
	QWidget,
	QScrollArea,
	QSizePolicy,
	QLayout,
)
from PIL import Image

from ui.action_panel import ActionPanel
from ui.history_panel import HistoryPanel
from ui.inference_panel import InferencePanel
from ui.result_panel import ResultPanel
from ui.theme import splitter_style, style_panel_scroll
from data.database_manager import DatabaseError, DatabaseManager
from data.export_manager import ExportError, ExportManager
from core.inference_engine import InferenceEngine, ModelValidationThread
from core.model_loader import LoadedModel, ModelLoader, ModelValidationError, ValidationResult
from core.large_image_segmentation import SEGMENTATION_COLORS, SEGMENTATION_LABELS
from utils.paths import app_data_dir, resource_path
from ui.settings_dialog import SettingsDialog
from ui.window_geometry import bounded_frame


logger = logging.getLogger(__name__)


def _gear_icon() -> QIcon:
	"""Load the complete platform-independent gear SVG from bundled assets."""
	return QIcon(str(resource_path(Path("assets") / "settings_gear.svg")))


class MainWindow(QMainWindow):
	"""Show the three-region application shell."""

	_DEFAULT_MODEL_PATH = Path("models") / "crc_dn21_seed42_best.pth"
	_DEFAULT_BUILTIN_MODEL_PATHS = {
		"classification": Path("models") / "crc_dn21_seed42_best.pth",
		"segmentation": Path("models") / "UPerNet_TME_tissue-panoptils_best_model_100ep.pth",
	}
	_EXPORT_REMINDER_KEYS = {
		"PNG": "export/pngReminderEnabled",
		"PDF": "export/pdfReminderEnabled",
	}

	def __init__(
		self,
		parent: QWidget | None = None,
		db_path: str | Path | None = None,
		builtin_model_path: str | Path | None = None,
		results_dir: str | Path | None = None,
		settings: QSettings | None = None,
	) -> None:
		super().__init__(parent)
		self.setWindowTitle("ZY-Path")
		logo_path = resource_path(Path("assets") / "logo.png")
		logo_pixmap = QPixmap(str(logo_path)) if logo_path.is_file() else QPixmap()
		if not logo_pixmap.isNull():
			self.setWindowIcon(QIcon(logo_pixmap))
		self._screen_fit_ready = False
		self._screen_fit_pending = False
		self._fitting_screen = False
		self._observed_screen = None
		self._first_show = True
		self._restore_as_maximized = False
		self._normal_geometry = QRect()
		self._normal_geometry_timer = QTimer(self)
		self._normal_geometry_timer.setSingleShot(True)
		self._normal_geometry_timer.setInterval(100)
		self._normal_geometry_timer.timeout.connect(self._remember_normal_geometry)
		self.setMinimumSize(320, 240)
		self.layout().setSizeConstraint(QLayout.SetNoConstraint)
		self.settings = settings or QSettings("ZY-Path", "ZY-Path")
		self.builtin_model_paths = {
			task_type: (
				Path(builtin_model_path)
				if builtin_model_path is not None and task_type == "classification"
				else resource_path(path)
			)
			for task_type, path in self._DEFAULT_BUILTIN_MODEL_PATHS.items()
		}
		self._has_builtin_path_override = builtin_model_path is not None
		self.builtin_model_path = self.builtin_model_paths["classification"]
		self.results_dir = (
			Path(results_dir)
			if results_dir is not None
			else app_data_dir() / "results"
		)
		self.export_manager = ExportManager()
		self._current_result: dict | None = None
		self._inference_engine: InferenceEngine | None = None
		self._active_use_builtin = False
		self._builtin_model_statuses: dict[str, tuple[str, bool] | None] = {
			"classification": None,
			"segmentation": None,
		}
		self._builtin_model_tasks: dict[str, str | None] = {
			"classification": None,
			"segmentation": None,
		}
		self._builtin_model_status: tuple[str, bool] | None = None
		self._builtin_model_task: str | None = None
		self._builtin_validation_generation = 0
		self._selected_builtin_task = "classification"
		self._validated_builtin_model: tuple[Path, LoadedModel] | None = None
		self._custom_model_status: tuple[str, bool] | None = None
		self._custom_model_task: str | None = None
		self._selected_history_record_id: int | None = None
		self.current_record_id: int | None = None
		self._settings_dialog: SettingsDialog | None = None
		self._model_validation_thread: ModelValidationThread | None = None
		self._progress_bar = QProgressBar(self)
		self._progress_bar.setRange(0, 100)
		self._progress_bar.setVisible(False)
		self._progress_bar.setFormat("%v/%m tiles")
		self.statusBar().addPermanentWidget(self._progress_bar, 1)

		central_widget = QWidget(self)
		central_layout = QVBoxLayout(central_widget)
		central_layout.setContentsMargins(0, 0, 0, 0)
		central_layout.setSpacing(0)
		central_layout.setSizeConstraint(QLayout.SetNoConstraint)

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
		title_row = QHBoxLayout()
		title_row.setContentsMargins(0, 0, 0, 0)
		title_row.setSpacing(10)
		if not logo_pixmap.isNull():
			logo_label = QLabel(header)
			logo_label.setObjectName("logoImage")
			logo_label.setFixedSize(title.minimumHeight(), title.minimumHeight())
			logo_label.setAlignment(Qt.AlignCenter)
			logo_label.setPixmap(
				logo_pixmap.scaled(
					logo_label.size(),
					Qt.KeepAspectRatio,
					Qt.SmoothTransformation,
				)
			)
			title_row.addWidget(logo_label)
		title_row.addWidget(title)
		title_row.addStretch()
		self.settings_button = QToolButton(header)
		self.settings_button.setObjectName("settingsButton")
		self.settings_button.setIcon(_gear_icon())
		self.settings_button.setIconSize(QSize(22, 22))
		self.settings_button.setFixedSize(40, 40)
		self.settings_button.setToolTip("Settings")
		self.settings_button.setAccessibleName("Settings")
		self.settings_button.setFocusPolicy(Qt.StrongFocus)
		self.settings_button.clicked.connect(self._show_settings)
		title_row.addWidget(self.settings_button)
		subtitle = QLabel("Histopathology image analysis", header)
		subtitle.setObjectName("subtitleText")
		subtitle_font = QFont("Segoe UI", 10)
		subtitle.setFont(subtitle_font)
		subtitle.setAlignment(Qt.AlignVCenter)
		subtitle.ensurePolished()
		subtitle.updateGeometry()
		subtitle.setMinimumHeight(QFontMetrics(subtitle_font).height() + 4)
		header_layout.addLayout(title_row)
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
			splitter_style(str(self._application_theme()))
		)
		self.inference_panel = InferencePanel(self.splitter)
		self.inference_panel.set_model_ready(False)
		self.inference_panel.setMaximumWidth(420)
		self._refresh_classification_parameters()

		self.tabs = QTabWidget(self.splitter)
		# Preserve readable result controls inside the horizontally scrollable body.
		self.tabs.setMinimumWidth(320)
		self.tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.tabs.setObjectName("tabRegion")
		self.result_panel = ResultPanel(self.tabs)
		self.history_panel = HistoryPanel(self.tabs)
		self.tabs.addTab(self.result_panel, "Inference")
		self.tabs.addTab(self.history_panel, "History")

		self.action_panel = ActionPanel(self.splitter)
		self.action_panel.setMinimumWidth(160)
		self.action_panel.setMaximumWidth(360)

		self.splitter.addWidget(self.inference_panel)
		self.splitter.addWidget(self.tabs)
		self.splitter.addWidget(self.action_panel)
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)
		self.splitter.setStretchFactor(2, 0)
		self.splitter.setSizes([280, 500, 240])
		self.splitter.splitterMoved.connect(self.inference_panel._refresh_thumbnail)
		# Rare very narrow logical screens can scroll the body horizontally; the
		# top-level window must never inherit the sum of child minimum widths.
		self.body_scroll = QScrollArea(central_widget)
		self.body_scroll.setWidgetResizable(True)
		self.body_scroll.setFrameShape(QScrollArea.NoFrame)
		self.body_scroll.setMinimumSize(0, 0)
		self.body_scroll.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.body_scroll.setWidget(self.splitter)
		style_panel_scroll(self.body_scroll)
		central_layout.addWidget(self.body_scroll, 1)

		self.setCentralWidget(central_widget)
		self.reset_export_reminders_action = self.menuBar().addAction(
			"Reset Export Reminders"
		)
		self.reset_export_reminders_action.setVisible(False)
		self.reset_export_reminders_action.triggered.connect(self._reset_export_reminders)
		status_bar = self.statusBar()
		status_bar.showMessage("Ready")
		self.inference_panel.run_requested.connect(self._show_run_requested)
		self.inference_panel.custom_model_chosen.connect(self._validate_custom_model)
		self.inference_panel.use_builtin_changed.connect(
			self._handle_use_builtin_changed
		)
		self.inference_panel.task_changed.connect(self._handle_task_changed)
		self.history_panel.search_requested.connect(self._search_history)
		self.history_panel.clear_requested.connect(self._clear_history_filters)
		self.history_panel.record_activated.connect(self._show_record_activated)
		self.history_panel.selection_changed.connect(self._update_rerun_enabled)
		self.history_panel.delete_requested.connect(self._confirm_delete_records)
		self.action_panel.rerun_requested.connect(self._handle_rerun_requested)
		self.action_panel.export_png_requested.connect(self._export_current_png)
		self.action_panel.export_pdf_requested.connect(self._export_current_pdf)
		self.result_panel.segmentation_page.presentation_changed.connect(self._save_result_presentation)
		self.result_panel.tile_page.presentation_changed.connect(self._save_result_presentation)

		self.database_manager: DatabaseManager | None = None
		try:
			self.database_manager = DatabaseManager(db_path)
			self._load_all_history()
		except DatabaseError as error:
			self.statusBar().showMessage(str(error))
		QTimer.singleShot(0, self._load_builtin_model)
		saved_geometry = self.settings.value("window/geometry")
		restored_geometry = bool(saved_geometry) and self.restoreGeometry(saved_geometry)
		self._restore_as_maximized = self.isMaximized() or self.settings.value("window/maximized", False, type=bool)
		# Restore a normal rectangle while still hidden. Fullscreen is not an app
		# startup mode; do not confuse a stale fullscreen flag with maximization.
		self.setWindowState(self.windowState() & ~(Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized))
		saved_normal = self.settings.value("window/normalGeometry")
		if self._restore_as_maximized and isinstance(saved_normal, QRect) and saved_normal.isValid():
			self.setGeometry(saved_normal)
		elif not restored_geometry:
			# Only choose a default when there is no usable saved geometry. QScreen
			# already reports logical pixels, including the user's display scaling.
			available = self._available_geometry()
			width, height = round(available.width() * 0.8), round(available.height() * 0.8)
			initial = QRect(available.x() + (available.width() - width) // 2,
				available.y() + (available.height() - height) // 2, width, height)
			self.setGeometry(initial)
		self._normal_geometry = QRect(self.geometry())
		self._screen_fit_ready = True
		self._fit_to_available_screen()

	def _available_geometry(self) -> QRect:
		"""QScreen returns logical coordinates already; never divide/multiply by DPR."""
		screen = self.windowHandle().screen() if self.windowHandle() is not None else None
		if screen is None:
			screen = QApplication.screenAt(self.frameGeometry().center())
		screen = screen or QApplication.primaryScreen()
		return QRect(screen.availableGeometry()) if screen is not None else QRect(0, 0, 800, 600)

	def _schedule_screen_fit(self, *unused) -> None:
		if not getattr(self, "_screen_fit_ready", False) or self._fitting_screen or self._screen_fit_pending:
			return
		self._screen_fit_pending = True
		QTimer.singleShot(0, self._fit_to_available_screen)

	def _fit_to_available_screen(self) -> None:
		"""One-shot correction of NORMAL geometry, never an interactive size cap."""
		self._screen_fit_pending = False
		if not self._screen_fit_ready or self._fitting_screen:
			return
		if self.isMinimized() or self.isMaximized() or self.isFullScreen():
			self._log_window_geometry("screen-fit-deferred-to-normal")
			return
		self._fitting_screen = True
		try:
			available = self._available_geometry()
			frame, client = self.frameGeometry(), self.geometry()
			left, top = max(0, client.x() - frame.x()), max(0, client.y() - frame.y())
			dw, dh = max(0, frame.width() - client.width()), max(0, frame.height() - client.height())
			max_width, max_height = max(1, available.width() - dw), max(1, available.height() - dh)
			minimum = QSize(min(320, max_width), min(240, max_height))
			if self.minimumSize() != minimum:
				self.setMinimumSize(minimum)
			target = bounded_frame(self.frameGeometry(), available)
			geometry = QRect(target.x() + left, target.y() + top,
				max(1, target.width() - dw), max(1, target.height() - dh))
			if geometry != self.geometry():
				self.setGeometry(geometry)
			self._remember_normal_geometry()
			self._log_window_geometry("screen-fit-normal")
		finally:
			self._fitting_screen = False

	def _bind_screen(self, screen=None) -> None:
		if self._observed_screen is not None:
			try:
				self._observed_screen.availableGeometryChanged.disconnect(self._schedule_screen_fit)
			except (TypeError, RuntimeError):
				pass
		self._observed_screen = screen or self.windowHandle().screen()
		self._observed_screen.availableGeometryChanged.connect(self._schedule_screen_fit)
		self._schedule_screen_fit()

	def showEvent(self, event) -> None:
		super().showEvent(event)
		if self._first_show:
			self._first_show = False
			self.windowHandle().screenChanged.connect(self._bind_screen)
			self._bind_screen()
			QTimer.singleShot(0, self._finish_first_show)
			# Native decorations can arrive after showEvent (X11/Windows WM roundtrip).
			QTimer.singleShot(80, self._schedule_screen_fit)
		self._log_window_geometry("show")

	def _finish_first_show(self) -> None:
		# Native frame margins are now known. Bound the restore rectangle BEFORE
		# asking the window manager to maximize; leave it untouched while maximized.
		self._fit_to_available_screen()
		if self._restore_as_maximized:
			self._restore_as_maximized = False
			self.showMaximized()

	def resizeEvent(self, event) -> None:
		super().resizeEvent(event)
		self._log_window_geometry("resize")
		self._queue_normal_geometry()

	def moveEvent(self, event) -> None:
		super().moveEvent(event)
		self._log_window_geometry("move")
		self._queue_normal_geometry()

	def _queue_normal_geometry(self) -> None:
		# Record only after the WM transaction settles: native maximize can resize
		# the client BEFORE Qt receives its maximized flag. No geometry is applied.
		if getattr(self, "_screen_fit_ready", False) and not self.windowState() & (Qt.WindowMinimized | Qt.WindowMaximized | Qt.WindowFullScreen):
			self._normal_geometry_timer.start()

	def _remember_normal_geometry(self) -> None:
		if not self.windowState() & (Qt.WindowMinimized | Qt.WindowMaximized | Qt.WindowFullScreen):
			self._normal_geometry = QRect(self.geometry())

	def changeEvent(self, event) -> None:
		super().changeEvent(event)
		if event.type() == QEvent.WindowStateChange:
			self._log_window_geometry("state-change")
			# Only constrain a restored NORMAL window, after Qt/WM restore events.
			managed_states = Qt.WindowMinimized | Qt.WindowMaximized | Qt.WindowFullScreen
			if self.windowState() & managed_states:
				self._normal_geometry_timer.stop()
			if event.oldState() & managed_states and not self.windowState() & managed_states:
				# A 0ms timer can still see maximized frame margins while the WM is
				# restoring decorations. Wait for that transaction, not every resize.
				QTimer.singleShot(80, self._schedule_screen_fit)
				self._queue_normal_geometry()

	def _log_window_geometry(self, reason: str) -> None:
		"""Diagnostic evidence also emitted by the Windows application's INFO log."""
		if not getattr(self, "_screen_fit_ready", False) or not logger.isEnabledFor(logging.INFO):
			return
		logger.info("Window geometry %s", json.dumps({
			"reason": reason, "platform": QApplication.platformName(),
			"state": int(self.windowState()), "flags": int(self.windowFlags()),
			"maximized": self.isMaximized(), "fullscreen": self.isFullScreen(), "minimized": self.isMinimized(),
			"geometry": self.geometry().getRect(), "frame": self.frameGeometry().getRect(),
			"normalGeometry": self.normalGeometry().getRect(),
			"savedNormalGeometry": self._normal_geometry.getRect(),
			"available": self._available_geometry().getRect(), "dpr": self.devicePixelRatioF(),
			"minimum": [self.minimumWidth(), self.minimumHeight()],
			"maximum": [self.maximumWidth(), self.maximumHeight()],
		}))

	def closeEvent(self, event) -> None:
		super().closeEvent(event)
		if event.isAccepted():
			self._normal_geometry_timer.stop()
			self._remember_normal_geometry()
			qt_normal = self.normalGeometry()
			if qt_normal.isValid() and qt_normal != self.geometry():
				# Qt API maximization retains a useful restore rectangle; native WM
				# actions can return the current maximized rectangle instead.
				self._normal_geometry = QRect(qt_normal)
			self.settings.setValue("window/geometry", self.saveGeometry())
			self.settings.setValue("window/normalGeometry", self._normal_geometry)
			self.settings.setValue("window/maximized", self.isMaximized())
			self.settings.sync()

	def _refresh_classification_parameters(self) -> None:
		self.inference_panel.set_classification_parameters({
			"tile_size": [self.settings.value("classificationTiles/width", 512, type=int),
						  self.settings.value("classificationTiles/height", 512, type=int)],
			"resize_backend": self.settings.value("classification/resizeBackend", "pillow_bilinear", type=str),
		})

	def _show_settings(self) -> None:
		"""Show the shared settings dialog without creating duplicates."""
		if self._settings_dialog is None:
			self._settings_dialog = SettingsDialog(self.settings, self)
			self._settings_dialog.tile_width.valueChanged.connect(self._refresh_classification_parameters)
			self._settings_dialog.tile_height.valueChanged.connect(self._refresh_classification_parameters)
			self._settings_dialog.resize_method.currentIndexChanged.connect(self._refresh_classification_parameters)
			self._settings_dialog.reset_export_reminders_requested.connect(
				self._reset_export_reminders
			)
			self._settings_dialog.reset_panel_layout_requested.connect(
				self._reset_panel_layout
			)
			self._settings_dialog.theme_changed.connect(self._apply_widget_theme)
		self._settings_dialog.show()
		self._settings_dialog.raise_()
		self._settings_dialog.activateWindow()

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
		classification_parameters: dict | None = None,
	) -> bool:
		"""Start one inference request through the shared worker path."""
		if self._inference_engine is not None:
			self.statusBar().showMessage(busy_message)
			return False
		if use_builtin:
			selected_model_path = self.builtin_model_paths.get(task_type)
			status = self._builtin_model_statuses.get(task_type)
			if selected_model_path is None or status is None or not status[1]:
				self.statusBar().showMessage(
					f"Built-in {task_type.capitalize()} model is not ready."
				)
				return False
		else:
			selected_model_path = Path(model_path)
			if (
				self._custom_model_status is None
				or not self._custom_model_status[1]
				or self._custom_model_task != task_type
			):
				self.statusBar().showMessage("The selected custom model is not ready for this task.")
				return False
		print(f"Inference model: {self._display_model_path(selected_model_path)}", flush=True)
		logger.info(
			"Inference thread starting: model=%s task=%s builtin=%s",
			selected_model_path,
			task_type,
			use_builtin,
		)
		loaded_model = None
		if use_builtin and self._validated_builtin_model is not None:
			cached_path, cached_model = self._validated_builtin_model
			if cached_path == selected_model_path:
				loaded_model = cached_model
		self._active_use_builtin = use_builtin
		self.inference_panel.set_running(True)
		self.statusBar().showMessage(status_message)
		engine = InferenceEngine(
			selected_model_path,
			image_path,
			task_type,
			class_labels=None,
			loaded_model=loaded_model,
		)
		if task_type == "classification":
			from core.classification_tiles import exploratory_metadata
			parameters = classification_parameters if classification_parameters is not None else self.inference_panel.classification_parameters()
			engine.classification_mode = parameters.get("classification_mode", self.inference_panel.classification_mode())
			engine.classification_resize_backend = parameters.get("resize_backend", self.settings.value(
				"classification/resizeBackend", "pillow_bilinear", type=str))
			if engine.classification_mode == "tiled_analysis":
				size = parameters.get("tile_size", [self.settings.value("classificationTiles/width", 512, type=int),
												self.settings.value("classificationTiles/height", 512, type=int)])
				engine.classification_tile_metadata = dict(parameters) if "classes" in parameters else exploratory_metadata(
					size[0], size[1], engine.classification_resize_backend)
				if engine.classification_tile_metadata.get("classes") and isinstance(engine.classification_tile_metadata["classes"][0], dict):
					items = engine.classification_tile_metadata["classes"]
					engine.classification_tile_metadata["classes"] = [item["label"] for item in items]
					engine.classification_tile_metadata["colors"] = [item["color"] for item in items]
			self.statusBar().showMessage(status_message + " " + engine.classification_mode.replace("_", " "))
		self._inference_engine = engine
		engine.result_ready.connect(self._show_inference_result)
		engine.error_occurred.connect(self._show_inference_error)
		engine.progress_changed.connect(self._show_inference_progress)
		engine.status_changed.connect(self.statusBar().showMessage)
		engine.finished.connect(self._inference_finished)
		engine.finished.connect(engine.deleteLater)
		engine.start()
		return True

	def _load_builtin_model(self) -> None:
		"""Validate only the default classification built-in model at startup."""
		self._request_builtin_validation("classification")

	def _request_builtin_validation(self, task_type: str) -> None:
		self._builtin_validation_generation += 1
		generation = self._builtin_validation_generation
		model_path = self.builtin_model_paths[task_type]
		logger.info("Built-in validation requested: task=%s path=%s", task_type, model_path)
		self._selected_builtin_task = task_type
		self._builtin_model_status = None
		self._builtin_model_task = None
		self._validated_builtin_model = None
		self.inference_panel.set_model_ready(False)
		if not model_path.is_file():
			status = (
				f"Built-in model file not found ({task_type.capitalize()}): {model_path.name}. "
				f"Place it at {self._display_model_path(model_path)}. "
				"Untick the box (Use Built-in Model) to use Browse.",
				False,
			)
			self._store_builtin_status(task_type, status)
			self.statusBar().showMessage("Ready")
			return

		self._store_builtin_status(
			task_type,
			(f"Built-in {task_type.capitalize()}: loading and validating...", False),
		)
		self.statusBar().showMessage(
			f"Loading built-in {task_type.capitalize()} model..."
		)
		if task_type == "segmentation" or model_path.stat().st_size > 100 * 1024 * 1024:
			if self._model_validation_thread is not None:
				return
			thread = ModelValidationThread(model_path, self)
			self._model_validation_thread = thread
			thread.validation_ready.connect(
				lambda loaded, validation: self._finish_builtin_validation(
					task_type, model_path, generation, loaded, validation
				)
			)
			thread.validation_error.connect(
				lambda message: self._fail_builtin_validation(
					task_type, model_path, generation, message
				)
			)
			thread.finished.connect(self._model_validation_finished)
			thread.finished.connect(thread.deleteLater)
			thread.start()
			return

		try:
			loaded_model = ModelLoader().load_with_info(model_path)
			validation = ModelLoader.validate(loaded_model.model)
			self._finish_builtin_validation(
				task_type, model_path, generation, loaded_model, validation
			)
		except (ModelValidationError, ValueError) as error:
			logger.exception("Built-in validation raised an exception: %s", model_path)
			self._fail_builtin_validation(task_type, model_path, generation, str(error))

	def _finish_builtin_validation(
		self,
		task_type: str,
		model_path: Path,
		generation: int,
		loaded_model: LoadedModel,
		validation: ValidationResult,
	) -> None:
		if (
			generation != self._builtin_validation_generation
			or not self.inference_panel.built_in_checkbox.isChecked()
			or self._selected_builtin_task != task_type
			or model_path != self.builtin_model_paths[task_type]
		):
			return
		try:
			if validation.task_type != task_type:
				raise ModelValidationError(
					f"Built-in {task_type.capitalize()} model outputs {validation.task_type}."
				)
			architecture = loaded_model.arch or "PyTorch model"
			status_text = (
				f"Built-in model: ready ({validation.num_classes} classes)"
				if self._has_builtin_path_override and task_type == "classification"
				else f"Built-in {task_type.capitalize()}: ready ({architecture}, "
				f"{validation.num_classes} classes)"
			)
			status = (status_text, True)
			self._store_builtin_status(task_type, status)
			self._validated_builtin_model = (model_path, loaded_model)
			logger.info("Built-in validation accepted: task=%s path=%s", task_type, model_path)
			self._builtin_model_task = validation.task_type
			self.inference_panel.set_model_ready(True)
			self.statusBar().showMessage("Ready")
		except (AttributeError, ModelValidationError, TypeError, ValueError) as error:
			self._fail_builtin_validation(task_type, model_path, generation, str(error))

	def _fail_builtin_validation(
		self, task_type: str, model_path: Path, generation: int, message: str
	) -> None:
		if generation != self._builtin_validation_generation:
			return
		self._store_builtin_status(
			task_type,
			(f"Built-in {task_type.capitalize()} validation failed: {message}", False),
		)
		logger.error("Built-in validation rejected: task=%s path=%s message=%s", task_type, model_path, message)
		self.inference_panel.set_model_ready(False)
		self.statusBar().showMessage(message)

	def _store_builtin_status(
		self, task_type: str, status: tuple[str, bool]
	) -> None:
		self._builtin_model_statuses[task_type] = status
		if task_type == self._selected_builtin_task:
			self._builtin_model_status = status
			self.inference_panel.set_model_status(*status)

	def _validate_custom_model(self, model_path: str) -> None:
		"""Validate a selected custom model and select its detected task."""
		self.inference_panel.set_model_ready(False)
		if self._start_large_model_validation(Path(model_path), False):
			return
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
			self.inference_panel.set_model_ready(True)
		except (ModelValidationError, ValueError) as error:
			logger.exception("Custom model validation raised an exception: %s", model_path)
			self._custom_model_status = (str(error), False)
			self._custom_model_task = None
			self.inference_panel.set_model_status(*self._custom_model_status)
			self.inference_panel.set_model_ready(False)

	def _start_large_model_validation(self, model_path: Path, use_builtin: bool) -> bool:
		try:
			is_large = model_path.is_file() and model_path.stat().st_size > 100 * 1024 * 1024
		except OSError:
			is_large = False
		if not is_large or self._model_validation_thread is not None:
			return False
		self.statusBar().showMessage("Loading and validating model...")
		self.inference_panel.set_model_status("Loading model...", False)
		thread = ModelValidationThread(model_path, self)
		self._model_validation_thread = thread
		thread.validation_ready.connect(
			lambda loaded, validation: self._apply_model_validation(
				model_path, use_builtin, loaded, validation
			)
		)
		thread.validation_error.connect(
			lambda message: self._model_validation_failed(model_path, use_builtin, message)
		)
		thread.finished.connect(self._model_validation_finished)
		thread.finished.connect(thread.deleteLater)
		thread.start()
		return True

	def _apply_model_validation(
		self, model_path: Path, use_builtin: bool, loaded_model: object, validation: object
	) -> None:
		if use_builtin is False and self.inference_panel.built_in_checkbox.isChecked():
			return
		if not use_builtin and Path(self.inference_panel._custom_model_path) != model_path:
			return
		try:
			loaded = loaded_model
			result = validation
			status = (
				f"{'Built-in' if use_builtin else 'Custom'} model: ready"
				f" ({result.num_classes} classes)"
			)
			if use_builtin:
				self._builtin_model_status = (status, True)
				self._builtin_model_task = result.task_type
			else:
				self._custom_model_status = (
					f"Custom model: valid, {result.task_type.capitalize()} ({result.num_classes} classes)",
					True,
				)
				self._custom_model_task = result.task_type
			self.inference_panel.set_model_status(
				*(self._builtin_model_status if use_builtin else self._custom_model_status)
			)
			self.inference_panel.set_task(result.task_type)
			self.inference_panel.set_model_ready(True)
			self.statusBar().showMessage("Ready")
		except (AttributeError, TypeError, ValueError):
			self._model_validation_failed(model_path, use_builtin, "The model validation result was invalid.")

	def _model_validation_failed(self, model_path: Path, use_builtin: bool, message: str) -> None:
		status = (message, False)
		if use_builtin:
			self._builtin_model_status = status
			self._builtin_model_task = None
		else:
			self._custom_model_status = status
			self._custom_model_task = None
		self.inference_panel.set_model_status(*status)
		self.inference_panel.set_model_ready(False)
		self.statusBar().showMessage(message)

	def _model_validation_finished(self) -> None:
		self._model_validation_thread = None
		if self.inference_panel.built_in_checkbox.isChecked():
			status = self._builtin_model_statuses[self._selected_builtin_task]
			if status is not None and status[0].endswith("loading and validating..."):
				self._request_builtin_validation(self._selected_builtin_task)

	def _handle_use_builtin_changed(self, use_builtin: bool) -> None:
		"""Switch between the task-specific built-in model and custom selection."""
		self._builtin_validation_generation += 1
		if use_builtin:
			self._handle_task_changed(self._selected_builtin_task)
			return
		status = self._custom_model_status or ("No custom model selected", False)
		self.inference_panel.set_model_status(*status)
		self.inference_panel.set_model_ready(
			bool(status[1]) and self._custom_model_task == self._current_task()
		)

	def _handle_task_changed(self, task_type: str) -> None:
		"""Select the matching built-in model without changing custom task detection."""
		if task_type not in self.builtin_model_paths:
			return
		self._selected_builtin_task = task_type
		if self.inference_panel.built_in_checkbox.isChecked():
			status = self._builtin_model_statuses[task_type]
			if status is not None and status[1]:
				self._builtin_model_status = status
				self._builtin_model_task = task_type
				self.inference_panel.set_model_status(*status)
				self.inference_panel.set_model_ready(True)
				return
			self._request_builtin_validation(task_type)
		else:
			self.inference_panel.set_model_ready(
				self._custom_model_task == task_type
				and self._custom_model_status is not None
				and self._custom_model_status[1]
			)

	def _current_task(self) -> str:
		return (
			"classification"
			if self.inference_panel.classification_radio.isChecked()
			else "segmentation"
		)

	@staticmethod
	def _segmentation_display_data(result: dict) -> tuple[dict, Image.Image, list]:
		"""Describe the supplied segmentation, retaining its actual class IDs/colors."""
		if result.get("source_format") == "upernet_state_dict":
			classes = [{"index": i, "label": label, "color": list(SEGMENTATION_COLORS[i])}
				for i, label in enumerate(SEGMENTATION_LABELS)]
			color_mask = result["color_mask"]
		else:
			# The parser legend contains present classes, not necessarily IDs 0..N.
			indices = result.get("classes_present", range(len(result["legend_items"])))
			classes = [{"index": int(i), "label": label, "color": [int(v) for v in color]}
				for i, (label, color) in zip(indices, result["legend_items"])]
			# The parser's RGBA layer carries the colors used in its supplied blend.
			# Retain those instead of assuming the built-in model's palette.
			layer = result.get("overlay")
			color_mask = layer.convert("RGB") if layer is not None and layer.mode == "RGBA" else result["color_mask"]
		analysis = {
			"classes": classes, "pixel_counts": [int(v) for v in result["counts"]],
			"area_denominator": "full_image_pixels", "image_size": list(color_mask.size),
			"model_name": str(result["model_name"]), "model_path": str(result["model_path"]),
			"source_format": result.get("source_format", "unknown"),
			"preprocess": result.get("preprocess_profile", "unknown"),
			"overlay_default_opacity": result.get("overlay_alpha", .2 if result.get("source_format") == "upernet_state_dict" else .4),
		}
		for key in ("tile", "stride", "input_size", "device", "elapsed_seconds"):
			if key in result:
				analysis[key] = result[key]
		return analysis, color_mask, [(item["label"], tuple(item["color"])) for item in classes]

	def _is_segmentation_display_active(self) -> bool:
		return bool(self._current_result and self._current_result["metadata"].get("task_type") == "segmentation"
			and self.result_panel.result_stack.currentWidget() is self.result_panel.segmentation_page
			and self.result_panel.segmentation_page.analysis is not None)

	def _save_result_presentation(self) -> None:
		if self._current_result is None:
			return
		metadata = self._current_result["metadata"]
		if metadata.get("task_type") == "segmentation":
			page, key = self.result_panel.segmentation_page, "segmentation_analysis"
		elif metadata.get("classification_mode") == "tiled_analysis":
			page, key = self.result_panel.tile_page, "classification_analysis"
		else:
			return
		if self.result_panel.result_stack.currentWidget() is not page or page.analysis is None:
			return
		analysis = metadata.get(key)
		if analysis is None:
			return
		analysis["presentation"] = page.presentation()
		if self.database_manager is not None and self.current_record_id is not None:
			try:
				self.database_manager.update_analysis_metadata(self.current_record_id, analysis)
			except DatabaseError as error:
				self.statusBar().showMessage(str(error))

	def _show_inference_result(self, result: dict) -> None:
		"""Display an inference result, save its image, and add its history row."""
		logger.info(
			"Inference result signal received: task=%s model=%s",
			result.get("task_type"),
			result.get("model_path"),
		)
		image_path = str(result["image_path"])
		self.result_panel.show_image(image_path)
		if result.get("analysis_mode") == "classification_tiles":
			with Image.open(image_path) as original_source:
				original = original_source.convert("RGB").copy()
			self.result_panel.show_classification_tiles(result["color_map"], result["classification_analysis"], original)
			result_image = self.result_panel.tile_page.render_image()
		elif result["task_type"] == "classification":
			self.result_panel.show_classification(
				result["label"],
				result["confidence"],
				result["probabilities"],
				result["class_labels"],
			)
			result_image = self.result_panel.get_result_figure()
		else:
			segmentation_analysis, display_mask, legend_items = self._segmentation_display_data(result)
			with Image.open(image_path) as source:
				original = source.convert("RGB").copy()
			self.result_panel.show_segmentation(
				result["blended"], legend_items, original_pil=original,
				color_mask=display_mask, counts=result.get("counts"), analysis=segmentation_analysis,
				default_opacity=segmentation_analysis["overlay_default_opacity"],
			)
			result_image = self.result_panel.segmentation_page.render_image()
		logger.info("Inference result displayed: task=%s", result["task_type"])

		self.action_panel.set_metadata(
			str(result["model_name"]),
			Path(image_path).name,
			self._local_timestamp(str(result["timestamp"])),
			None,
		)
		self.current_record_id = None
		local_timestamp = self._local_timestamp(str(result["timestamp"]))
		result_path: str | None = None
		labels_path: str | None = None
		color_mask_path: str | None = None
		overlay_path: str | None = None
		analysis_metadata: dict | None = (
			result.get("classification_parameters", {"mode": "single_image", "classification_mode": "single_image",
				"resize_backend": "pillow_bilinear", "preprocess": result.get("preprocess_profile", "imagenet"), "input_size": [224, 224]})
			if result["task_type"] == "classification" else None
		)
		metadata_path: str | None = None
		try:
			self.results_dir.mkdir(parents=True, exist_ok=True)
			result_path = self._new_result_path(str(result["timestamp"]))
			self.export_manager.export_png(result_image, result_path)
			result_path = str(result_path.resolve())
			if result["task_type"] == "segmentation":
				labels_file = Path(result_path).with_name(Path(result_path).stem + "_labels.png")
				color_file = Path(result_path).with_name(Path(result_path).stem + "_mask.png")
				overlay_file = Path(result_path).with_name(Path(result_path).stem + "_overlay.png")
				Image.fromarray(result["mask"]).save(labels_file)
				display_mask.save(color_file)
				result_image.save(overlay_file)
				labels_path = str(labels_file.resolve())
				color_mask_path = str(color_file.resolve())
				overlay_path = str(overlay_file.resolve())
				analysis_metadata = dict(segmentation_analysis)
				analysis_metadata["presentation"] = self.result_panel.segmentation_page.presentation()
				metadata_file = Path(result_path).with_suffix(".json")
				metadata_file.write_text(json.dumps(analysis_metadata, ensure_ascii=True, indent=2), encoding="utf-8")
				metadata_path = str(metadata_file.resolve())
			if result.get("analysis_mode") == "classification_tiles":
				analysis_metadata = dict(result["classification_analysis"])
				analysis_metadata["classification_mode"] = "tiled_analysis"
				analysis_metadata["presentation"] = self.result_panel.tile_page.presentation()
				color_file = Path(result_path).with_name(Path(result_path).stem + "_classes.png")
				result["color_map"].save(color_file)
				color_mask_path = str(color_file.resolve())
				overlay_path = result_path
				Path(result_path).with_suffix(".json").write_text(
					json.dumps(analysis_metadata, indent=2), encoding="utf-8"
				)
			logger.info("Inference result files saved: overlay=%s", result_path)
		except (ExportError, OSError, ValueError) as error:
			logger.exception("Inference result saving failed")
			result_path = None
			labels_path = None
			color_mask_path = None
			overlay_path = None
			analysis_metadata = (result.get("classification_analysis") or result.get("classification_parameters")
				if result["task_type"] == "classification" else None)
			metadata_path = None
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
				"model_path": str(result["model_path"]),
				"task_type": str(result["task_type"]),
				"timestamp": local_timestamp,
				"image_path": str(Path(image_path).resolve()),
				"result_label": result_label,
				"confidence": confidence,
			}
			if analysis_metadata is not None:
				metadata["classification_analysis" if result["task_type"] == "classification" else "segmentation_analysis"] = analysis_metadata
			if result["task_type"] == "classification":
				metadata["classification_mode"] = "tiled_analysis" if result.get("analysis_mode") == "classification_tiles" else "single_image"
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
		model_path = str(Path(str(result["model_path"])).resolve())
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
				labels_path,
				color_mask_path,
				overlay_path,
				analysis_metadata,
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
			selected_ids = self.history_panel.selected_record_ids()
			if not selected_ids:
				self.statusBar().showMessage("Select a history record first")
				return
			if len(selected_ids) > 1:
				self.statusBar().showMessage("Select exactly one record to re-run")
				return
			record_id = selected_ids[0]
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
			if not use_builtin:
				try:
					resolved_model = Path(model_path).resolve()
					use_builtin = any(
						resolved_model == path.resolve()
						for path in self.builtin_model_paths.values()
					)
				except OSError:
					use_builtin = False
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
				builtin_status = self._builtin_model_statuses.get(task_type)
				if builtin_status is None or not builtin_status[1]:
					message = (
						builtin_status[0]
						if builtin_status is not None
						else f"Built-in {task_type.capitalize()} model is not ready."
					)
					QMessageBox.warning(self, "Re-run unavailable", message)
					self.statusBar().showMessage(message)
					return
				model_task = self._builtin_model_task
			else:
				model_task = None

			self.inference_panel.set_task(task_type)
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

			parameters = self._record_classification_parameters(record) if task_type == "classification" else None
			if parameters is not None:
				self.inference_panel.set_classification_mode(parameters["classification_mode"])
				self.inference_panel.set_classification_parameters(parameters)
			self.inference_panel.set_image(image_path)
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
				classification_parameters=parameters,
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

	def _show_inference_progress(self, done: int, total: int) -> None:
		logger.info("GUI progress received: %s/%s", done, total)
		self._progress_bar.setRange(0, total)
		self._progress_bar.setValue(done)
		self._progress_bar.setVisible(True)
		self.statusBar().showMessage(f"Segmentation tiles: {done}/{total}")

	def _inference_finished(self) -> None:
		"""Restore the inference controls after the worker stops."""
		self.inference_panel.set_running(False)
		self._progress_bar.setVisible(False)
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

	def _display_model_path(self, model_path: Path) -> str:
		"""Return a project-relative path for bundled models when possible."""
		try:
			return model_path.resolve().relative_to(resource_path(".").resolve()).as_posix()
		except ValueError:
			return str(model_path)

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

	def _confirm_delete_records(self, record_ids: list[int]) -> None:
		if not record_ids:
			return
		if self.database_manager is None:
			message = "The history database is not available."
			QMessageBox.warning(self, "Delete failed", message)
			self.statusBar().showMessage(message)
			return

		confirmation = QMessageBox.question(
			self,
			"Delete records",
			f"Delete {len(record_ids)} record(s)? This cannot be undone. "
			"Saved result images will also be removed. Your original image files are not touched.",
			QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No,
		)
		if confirmation != QMessageBox.Yes:
			return

		try:
			records = [
				record
				for record_id in record_ids
				if (record := self.database_manager.get_record_by_id(record_id))
				is not None
			]
			deleted_count = self.database_manager.delete_records(record_ids)
		except DatabaseError:
			logger.exception("Could not delete the selected history records.")
			message = "The selected history records could not be deleted."
			QMessageBox.warning(self, "Delete failed", message)
			self.statusBar().showMessage(message)
			return

		self._delete_saved_result_images(records)
		if any(
			record.get("id") == self.current_record_id for record in records
		):
			self.current_record_id = None
			self._current_result = None
			self.result_panel.clear()
			self.action_panel.clear()

		try:
			self._reload_history_with_current_filters()
		except DatabaseError:
			logger.exception("Could not refresh history after deleting records.")
			QMessageBox.warning(
				self,
				"History refresh failed",
				"The records were deleted, but the history list could not be refreshed.",
			)
		self._update_rerun_enabled(None)
		self.statusBar().showMessage(f"Deleted {deleted_count} record(s)")

	def _delete_saved_result_images(self, records: list[dict]) -> None:
		try:
			results_root = self.results_dir.resolve()
		except (OSError, RuntimeError):
			logger.exception("Could not resolve the results folder for image cleanup.")
			return

		for record in records:
			for field in (
				"result_image_path",
				"result_labels_path",
				"result_color_mask_path",
				"result_overlay_path",
			):
				result_path = record.get(field)
				if not result_path:
					continue
				try:
					resolved_path = Path(str(result_path)).resolve()
					if not resolved_path.is_relative_to(results_root):
						continue
					if resolved_path.is_file():
						resolved_path.unlink()
				except (OSError, RuntimeError):
					logger.exception("Could not remove a saved result image.")

	def _reload_history_with_current_filters(self) -> None:
		if self.database_manager is None:
			return
		panel = self.history_panel
		start = None
		end = None
		if panel.date_filter_checkbox.isChecked():
			start_date = panel.from_date_edit.date().toPyDate()
			end_date = panel.to_date_edit.date().toPyDate()
			start = panel._local_date_to_utc_iso(start_date, time.min)
			end = panel._local_date_to_utc_iso(end_date, time(23, 59, 59))
		records = self.database_manager.search(
			panel.search_input.text().strip(),
			start=start,
			end=end,
		)
		panel.set_records(records)

	@staticmethod
	def _record_classification_parameters(record: dict) -> dict:
		try:
			analysis = json.loads(record.get("analysis_json") or "{}")
			if not isinstance(analysis, dict):
				raise ValueError("Invalid analysis metadata")
		except (TypeError, ValueError):
			analysis = {}
		mode = "tiled_analysis" if analysis.get("mode") == "classification_tiles" else "single_image"
		return {**analysis, "classification_mode": mode,
				"resize_backend": analysis.get("resize_backend", "pillow_bilinear")}

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
		artifact_path = record.get("result_color_mask_path")
		analysis_json = record.get("analysis_json")
		classification_analysis = None
		segmentation_analysis = None
		self.result_panel.tile_page.clear()
		if task_type == "classification" and analysis_json:
			try:
				stored_analysis = json.loads(str(analysis_json))
				if stored_analysis.get("mode") == "classification_tiles":
					with Image.open(artifact_path or result_image_path) as source:
						color_map = source.convert("RGB").copy()
					with Image.open(image_path) as source:
						original = source.convert("RGB").copy()
					self.result_panel.show_classification_tiles(color_map, stored_analysis, original, stored_analysis.get("presentation"))
					classification_analysis = stored_analysis
			except (OSError, ValueError, KeyError, TypeError):
				logger.exception("Could not restore classification tiles")
		if classification_analysis is not None:
			pass
		elif task_type == "segmentation" and artifact_path and analysis_json:
			try:
				analysis = json.loads(str(analysis_json))
				classes = analysis.get("classes", [])
				legend_items = [
					(str(item["label"]), tuple(int(value) for value in item["color"]))
					for item in classes
					if isinstance(item, dict) and "label" in item and "color" in item
				]
				with Image.open(image_path) as original_source:
					original = original_source.convert("RGB").copy()
				with Image.open(artifact_path) as color_source:
					color_mask = color_source.convert("RGB").copy()
				with Image.open(result_image_path) as overlay_source:
					overlay = overlay_source.convert("RGBA").copy()
				self.result_panel.show_segmentation(
					overlay,
					legend_items,
					original_pil=original,
					color_mask=color_mask,
					counts=analysis.get("pixel_counts"), analysis=analysis,
					presentation=analysis.get("presentation"),
					default_opacity=analysis.get("overlay_default_opacity", .2),
				)
				segmentation_analysis = analysis
			except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
				self.result_panel.show_stored_result(
					result_image_path,
					task_type,
					str(label) if label is not None else None,
					float(confidence) if confidence is not None else None,
				)
		else:
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
		self._current_result["metadata"]["model_path"] = model_path
		if segmentation_analysis is not None:
			self._current_result["metadata"]["segmentation_analysis"] = segmentation_analysis
		if task_type == "classification":
			parameters = self._record_classification_parameters(record)
			self._current_result["metadata"]["classification_mode"] = parameters["classification_mode"]
			self._current_result["metadata"]["classification_analysis"] = classification_analysis or parameters
			self.inference_panel.set_classification_mode(parameters["classification_mode"])
			self.inference_panel.set_classification_parameters(parameters)
		self.action_panel.set_result_available(True)
		self.statusBar().showMessage(f"Showing record #{record_id}")

	def _export_current_png(self) -> None:
		"""Export the saved result image to a user-selected PNG path."""
		if not self._validate_export_sources(include_original=False):
			return
		if not self._show_export_explanation("PNG"):
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
				image = opened_image.copy()
			if self._current_result["metadata"].get("classification_mode") == "tiled_analysis" and self.result_panel.tile_page.analysis is not None:
				image = self.result_panel.tile_page.render_image()
				self._current_result["metadata"]["classification_analysis"]["presentation"] = self.result_panel.tile_page.presentation()
			if self._is_segmentation_display_active():
				image = self.result_panel.segmentation_page.render_image()
				self._save_result_presentation()
			self.export_manager.export_png(image, output_path)
			if self._current_result["metadata"].get("classification_analysis") or self._current_result["metadata"].get("segmentation_analysis"):
				Path(output_path).with_suffix(Path(output_path).suffix + ".json").write_text(
					json.dumps(self._current_result["metadata"], indent=2), encoding="utf-8"
				)
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
		if not self._validate_export_sources(include_original=True):
			return
		if not self._show_export_explanation("PDF"):
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
			with tempfile.TemporaryDirectory(prefix="zy-path-export-") as directory:
				if self._current_result["metadata"].get("classification_mode") == "tiled_analysis" and self.result_panel.tile_page.analysis is not None:
					result_path = Path(directory) / "classification-view.png"
					self.result_panel.tile_page.render_image().save(result_path)
					self._current_result["metadata"]["classification_analysis"]["presentation"] = self.result_panel.tile_page.presentation()
				if self._is_segmentation_display_active():
					result_path = Path(directory) / "segmentation-view.png"
					self.result_panel.segmentation_page.render_image().save(result_path)
					self._save_result_presentation()
				self.export_manager.export_pdf(output_path, original_path, result_path, self._current_result["metadata"])
		except (ExportError, OSError, RuntimeError, TypeError, ValueError):
			QMessageBox.warning(
				self,
				"Export failed",
				"The PDF report could not be created. Check the files and selected path, then try again.",
			)
			return
		self.statusBar().showMessage(f"Saved to {output_path}")

	def _validate_export_sources(self, include_original: bool) -> bool:
		if self._current_result is None:
			return False

		result_path = Path(self._current_result["result_image_path"])
		if not result_path.is_file():
			QMessageBox.warning(
				self,
				"Export failed",
				f"Stored result image not found: {result_path}",
			)
			return False

		if include_original:
			original_path = Path(self._current_result["original_image_path"])
			if not original_path.is_file():
				QMessageBox.warning(
					self,
					"Export failed",
					f"Original image not found: {original_path}",
				)
				return False
		return True

	def _show_export_explanation(self, export_format: str) -> bool:
		key = self._EXPORT_REMINDER_KEYS[export_format]
		if not self.settings.value(key, True, type=bool):
			return True

		messages = {
			"PNG": (
				"PNG exports the result image only. Choose PDF if you need a full report.",
				"Don't show this again for PNG exports",
			),
			"PDF": (
				"PDF exports a report containing the original image, result image, and analysis details.",
				"Don't show this again for PDF exports",
			),
		}
		message, checkbox_text = messages[export_format]
		dialog = QMessageBox(self)
		dialog.setWindowTitle(f"Export {export_format}")
		dialog.setText(message)
		checkbox = QCheckBox(checkbox_text, dialog)
		dialog.setCheckBox(checkbox)
		cancel_button = dialog.addButton(QMessageBox.Cancel)
		continue_button = dialog.addButton("Continue", QMessageBox.AcceptRole)
		dialog.setDefaultButton(continue_button)
		dialog.setEscapeButton(cancel_button)
		dialog.exec_()
		if dialog.clickedButton() is not continue_button:
			return False
		if checkbox.isChecked():
			self.settings.setValue(key, False)
			self.settings.sync()
			if self._settings_dialog is not None:
				self._settings_dialog.refresh_preferences()
		return True

	def _reset_export_reminders(self) -> None:
		for key in self._EXPORT_REMINDER_KEYS.values():
			self.settings.setValue(key, True)
		self.settings.sync()
		if self._settings_dialog is not None:
			self._settings_dialog.refresh_preferences()
		QMessageBox.information(
			self,
			"Export Reminders",
			"PNG and PDF export reminders have been restored.",
		)

	def _reset_panel_layout(self) -> None:
		"""Restore panel proportions without clearing any application data."""
		self.splitter.setSizes([280, 500, 240])
		self.result_panel.reset_layout()
		self.statusBar().showMessage("Panel layout restored")

	def _apply_widget_theme(self, theme_name: str) -> None:
		"""Refresh widget-local styles after the application theme changes."""
		self.splitter.setStyleSheet(splitter_style(theme_name))
		self.result_panel.set_splitter_theme(theme_name)

	def _application_theme(self) -> str:
		application = QApplication.instance()
		if application is None:
			return "Light"
		return str(application.property("zyTheme") or "Light")

	def _update_rerun_enabled(self, record_id: object) -> None:
		self._selected_history_record_id = (
			record_id if isinstance(record_id, int) else None
		)
		self.action_panel.set_rerun_enabled(
			record_id is not None,
			self._selected_history_record_id,
		)
