"""Controls for selecting an image, model, and inference task."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (
	QFileDialog,
	QComboBox,
	QScrollArea,
	QLayout,
	QSizePolicy,
	QGroupBox,
	QLabel,
	QPushButton,
	QRadioButton,
	QCheckBox,
	QVBoxLayout,
	QWidget,
)

from ui.theme import ERROR, SUCCESS, style_panel_scroll


class InferencePanel(QWidget):
	"""Let the user choose model and image inputs for an inference request."""

	run_requested = pyqtSignal(str, bool, str, str)
	cancel_requested = pyqtSignal()
	custom_model_chosen = pyqtSignal(str)
	use_builtin_changed = pyqtSignal(bool)
	task_changed = pyqtSignal(str)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("InferencePanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._custom_model_path = ""
		self._image_path = ""
		self._image_filename = ""
		self._source_pixmap = QPixmap()
		self._running = False
		self._model_ready = True
		self._builtin_model_names = {
			"classification": "crc_dn21_seed42_best.pth",
			"segmentation": "UPerNet_TME_tissue-panoptils_best_model_100ep.pth",
		}

		outer = QVBoxLayout(self)
		outer.setContentsMargins(16, 16, 16, 16)
		outer.setSpacing(10)
		outer.setSizeConstraint(QLayout.SetMinimumSize)
		content = QWidget(self)
		layout = QVBoxLayout(content)
		layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(10)

		self.built_in_checkbox = QCheckBox("Use Built-in Model", self)
		self.built_in_checkbox.setChecked(True)
		self.built_in_checkbox.setToolTip(
			"Checked: use the built-in model for this task. Unchecked: return to the last local model "
			"selected in this session, or browse for one. Startup defaults are set in Settings > Models."
		)
		layout.addWidget(self.built_in_checkbox)

		self.browse_model_button = QPushButton("Browse Model...", self)
		self.browse_model_button.setToolTip(
			"Choose a local PyTorch model for this session. This does not save a startup default."
		)
		layout.addWidget(self.browse_model_button)

		self.model_filename_label = QLabel(self)
		self.model_filename_label.setToolTip("Selected custom model filename.")
		self.model_filename_label.setWordWrap(False)
		self.model_filename_label.hide()
		layout.addWidget(self.model_filename_label)

		self.trust_warning_label = QLabel(
			"Only load model files from sources you trust.", self
		)
		self.trust_warning_label.setToolTip("Model files can contain executable code.")
		self.trust_warning_label.setWordWrap(True)
		self.trust_warning_label.hide()
		layout.addWidget(self.trust_warning_label)

		self.model_status_label = QLabel(
			"⚠ Built-in model: not loaded yet", self
		)
		self.model_status_label.setToolTip("Current model selection status.")
		self.model_status_label.setWordWrap(True)
		self.model_status_label.setStyleSheet(f"color: {ERROR};")
		layout.addWidget(self.model_status_label)

		self.upload_image_button = QPushButton("Upload Image...", self)
		self.upload_image_button.setToolTip("Choose an image for inference.")
		layout.addWidget(self.upload_image_button)

		self.thumbnail_label = QLabel(self)
		self.thumbnail_label.setAlignment(Qt.AlignCenter)
		self.thumbnail_label.setMaximumSize(248, 100)
		self.thumbnail_label.setToolTip("Preview of the selected image.")
		self.thumbnail_label.hide()
		layout.addWidget(self.thumbnail_label, alignment=Qt.AlignHCenter)

		self.image_filename_label = QLabel(self)
		self.image_filename_label.setToolTip("Selected image filename.")
		self.image_filename_label.setWordWrap(False)
		self.image_filename_label.hide()
		layout.addWidget(self.image_filename_label)

		self.image_error_label = QLabel(self)
		self.image_error_label.setToolTip("Image loading status.")
		self.image_error_label.setWordWrap(True)
		self.image_error_label.hide()
		layout.addWidget(self.image_error_label)

		task_group = QGroupBox("Task", self)
		task_group.setToolTip("Choose the type of inference task.")
		task_layout = QVBoxLayout(task_group)
		task_layout.setContentsMargins(8, 8, 8, 8)
		task_layout.setSpacing(4)
		self.classification_radio = QRadioButton("Classification", task_group)
		self.classification_radio.setToolTip("Predict one label for the whole image.")
		self.classification_radio.setChecked(True)
		self.segmentation_radio = QRadioButton("Segmentation", task_group)
		self.segmentation_radio.setToolTip("Predict a label for each image pixel.")
		task_layout.addWidget(self.classification_radio)
		self.classification_mode_combo = QComboBox(task_group)
		self.classification_mode_combo.setObjectName("classificationMode")
		self.classification_mode_combo.addItem("Single image", "single_image")
		self.classification_mode_combo.addItem("Tiled analysis", "tiled_analysis")
		self.classification_mode_combo.setToolTip("Single image classifies the whole image. Tiled analysis uses the configured original-image tile width and height, even for one tile.")
		task_layout.addWidget(self.classification_mode_combo)
		task_layout.addWidget(self.segmentation_radio)
		layout.addWidget(task_group)

		self.mode_summary = QLabel(self)
		self.mode_summary.setWordWrap(True)
		self._classification_parameters = {"tile_size": [512, 512], "resize_backend": "pillow_bilinear"}
		layout.addWidget(self.mode_summary)
		self.classification_mode_combo.currentIndexChanged.connect(self._refresh_mode_summary)
		self._refresh_mode_summary()

		self.run_button = QPushButton("Run Inference", self)
		self.run_button.setObjectName("runInferenceButton")
		self.run_button.setToolTip("Send the selected inputs as an inference request.")
		self.run_button.setEnabled(False)
		layout.addStretch()
		self.controls_scroll = QScrollArea(self)
		self.controls_scroll.setWidgetResizable(True)
		self.controls_scroll.setFrameShape(QScrollArea.NoFrame)
		self.controls_scroll.setMinimumSize(0, 0)
		self.controls_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
		self.controls_scroll.setWidget(content)
		style_panel_scroll(self.controls_scroll)
		outer.addWidget(self.controls_scroll, 1)
		outer.addWidget(self.run_button)
		self.cancel_button = QPushButton("Cancel inference", self)
		self.cancel_button.setToolTip("Stop after the current model operation finishes. Partial results are discarded.")
		self.cancel_button.hide()
		self.cancel_button.clicked.connect(self.cancel_requested)
		outer.addWidget(self.cancel_button)
		for label in (self.model_status_label, self.trust_warning_label, self.image_error_label, self.mode_summary):
			label.setMinimumWidth(0)
			label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
		left_margin, _, right_margin, _ = layout.getContentsMargins()
		outer_left, _, outer_right, _ = outer.getContentsMargins()
		content_width = max(
			widget.sizeHint().width()
			for widget in (
				self.built_in_checkbox,
				self.browse_model_button,
				self.upload_image_button,
				task_group,
				self.run_button,
			)
		)
		# Keep the calculated readable width when the outer layout reapplies its
		# minimum height for the pinned Run/Cancel buttons.
		self.controls_scroll.setMinimumWidth(
			max(240 - outer_left - outer_right, content_width + left_margin + right_margin)
		)
		self.setMinimumWidth(
			max(240, content_width + left_margin + right_margin + outer_left + outer_right)
		)

		self.built_in_checkbox.toggled.connect(self._on_built_in_toggled)
		self.browse_model_button.clicked.connect(self._browse_model)
		self.upload_image_button.clicked.connect(self._browse_image)
		self.run_button.clicked.connect(self._emit_run_requested)
		self.classification_radio.toggled.connect(self._task_toggled)
		self.segmentation_radio.toggled.connect(self._task_toggled)
		self._on_built_in_toggled(self.built_in_checkbox.isChecked())

	def clear_image(self) -> None:
		"""Remove the current input without changing model or analysis settings."""
		self._image_path = ""
		self._image_filename = ""
		self._source_pixmap = QPixmap()
		self.thumbnail_label.clear()
		self.thumbnail_label.hide()
		self.image_filename_label.clear()
		self.image_filename_label.hide()
		self.image_filename_label.setToolTip("")
		self.image_error_label.clear()
		self.image_error_label.hide()
		self._update_run_button()

	def set_image(self, path: str) -> None:
		"""Load an image preview and update whether inference can be requested."""
		self.clear_image()
		pixmap = QPixmap(path)
		if not path or pixmap.isNull():
			self.image_error_label.setText("This image could not be opened. Please choose another file.")
			self.image_error_label.show()
			self._update_run_button()
			return

		self._image_path = str(path)
		self._image_filename = Path(path).name
		self._source_pixmap = pixmap
		self._refresh_thumbnail()
		self.thumbnail_label.show()
		self.image_filename_label.setToolTip(self._image_filename)
		self.image_filename_label.show()
		self._refresh_filename_labels()
		self._update_run_button()

	def set_custom_model(self, path: str) -> None:
		"""Select a custom model path without validating or loading it."""
		self._custom_model_path = str(path)
		self.built_in_checkbox.setChecked(not bool(self._custom_model_path))
		self._refresh_filename_labels()
		self._update_run_button()
		if self._custom_model_path:
			self.custom_model_chosen.emit(self._custom_model_path)

	def set_use_builtin(self, use_builtin: bool) -> None:
		"""Select the built-in model or a custom model."""
		if self.built_in_checkbox.isChecked() == use_builtin:
			self._on_built_in_toggled(use_builtin)
		else:
			self.built_in_checkbox.setChecked(use_builtin)

	def set_task(self, task_type: str) -> None:
		"""Select the matching task radio button."""
		if task_type == "classification":
			self.classification_radio.setChecked(True)
		elif task_type == "segmentation":
			self.segmentation_radio.setChecked(True)
		else:
			raise ValueError("Task type must be 'classification' or 'segmentation'.")

	def classification_mode(self) -> str:
		return str(self.classification_mode_combo.currentData())

	def set_classification_mode(self, mode: str) -> None:
		index = self.classification_mode_combo.findData(mode)
		if index < 0:
			raise ValueError("Unknown classification mode.")
		self.classification_mode_combo.setCurrentIndex(index)

	def classification_parameters(self) -> dict:
		return {**self._classification_parameters, "classification_mode": self.classification_mode()}

	def set_classification_parameters(self, parameters: dict) -> None:
		self._classification_parameters = dict(parameters)
		self._refresh_mode_summary()

	def _refresh_mode_summary(self) -> None:
		classification = self.classification_radio.isChecked()
		self.classification_mode_combo.setEnabled(classification)
		task = "classification" if classification else "segmentation"
		model = (self._builtin_model_names.get(task, "Not selected")
				 if self.built_in_checkbox.isChecked()
				 else Path(self._custom_model_path).name or "Not selected")
		text = f"Classification: {self.classification_mode_combo.currentText()}" if classification else "Selected task: Segmentation"
		text += f"\nModel: {model}"
		if not self._source_pixmap.isNull():
			width, height = self._source_pixmap.width(), self._source_pixmap.height()
			text += f"\nImage: {width} x {height} px"
		else:
			width = height = 0
			text += "\nImage: not selected"
		parameters = self._classification_parameters
		if classification and self.classification_mode() == "tiled_analysis":
			w, h = parameters.get("tile_size", [512, 512])
			text += f"\nOriginal tiles: {w} x {h} px. Training scale unconfirmed."
			if width and height and w > 0 and h > 0:
				columns, rows = (width + w - 1) // w, (height + h - 1) // h
				text += f"\nPlanned tiles: {columns * rows} ({columns} columns x {rows} rows)"
		if classification:
			text += "\nResize: " + parameters.get("resize_backend", "pillow_bilinear")
		self.mode_summary.setTextFormat(Qt.PlainText)
		self.mode_summary.setText(text)
		if hasattr(self, "run_button"):
			self.run_button.setToolTip(text)

	def set_builtin_model_names(self, paths) -> None:
		self._builtin_model_names = {task: Path(path).name for task, path in paths.items()}
		self._refresh_mode_summary()

	def set_model_ready(self, ready: bool) -> None:
		"""Allow inference only after the selected model is validated."""
		self._model_ready = bool(ready)
		self._update_run_button()

	def set_model_status(self, text: str, ok: bool) -> None:
		"""Show model status with an icon and the matching status color."""
		icon = "✔" if ok else "⚠"
		color = SUCCESS if ok else ERROR
		self.model_status_label.setText(f"{icon} {text}")
		self.model_status_label.setStyleSheet(f"color: {color};")

	def set_running(self, running: bool) -> None:
		"""Keep cancellation reachable while input controls are locked."""
		self._running = running
		self.run_button.setText("Running..." if running else "Run Inference")
		self.controls_scroll.setEnabled(not running)
		self.run_button.setVisible(not running)
		self.cancel_button.setVisible(running)
		self.cancel_button.setEnabled(running)
		self.cancel_button.setText("Cancel inference")
		self._update_controls()

	def set_cancelling(self) -> None:
		self.cancel_button.setText("Cancelling…")
		self.cancel_button.setEnabled(False)

	def _on_built_in_toggled(self, use_built_in: bool) -> None:
		self.trust_warning_label.setVisible(not use_built_in)
		self._refresh_filename_labels()
		self._update_controls()
		self.use_builtin_changed.emit(use_built_in)

	def _browse_model(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self, "Select Model", "", "PyTorch models (*.pt *.pth)"
		)
		if path:
			self.set_custom_model(path)

	def _browse_image(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self,
			"Select Image",
			"",
			"Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp)",
		)
		if path:
			self.set_image(path)

	def _refresh_thumbnail(self) -> None:
		if self._source_pixmap.isNull():
			return
		available_width = max(1, self.contentsRect().width() - 32)
		self.thumbnail_label.setMaximumWidth(available_width)
		self.thumbnail_label.setPixmap(
			self._source_pixmap.scaled(
				available_width,
				100,
				Qt.KeepAspectRatio,
				Qt.SmoothTransformation,
			)
		)

	def resizeEvent(self, event: QResizeEvent) -> None:
		"""Refresh previews and filenames after the panel changes size."""
		super().resizeEvent(event)
		self._refresh_wrapped_label_widths()
		self._refresh_thumbnail()
		self._refresh_filename_labels()

	def _refresh_wrapped_label_widths(self) -> None:
		left_margin, _, right_margin, _ = self.layout().getContentsMargins()
		available_width = max(
			1, self.width() - left_margin - right_margin
		)
		for label in (
			self.trust_warning_label,
			self.model_status_label,
			self.image_error_label,
			self.mode_summary,
		):
			label.setMaximumWidth(available_width)

	def _refresh_filename_labels(self) -> None:
		if self._image_filename:
			self.image_filename_label.setText(
				self._elided_filename(
					self._image_filename, self.image_filename_label
				)
			)
		show_custom = bool(self._custom_model_path) and not self.built_in_checkbox.isChecked()
		self.model_filename_label.setVisible(show_custom)
		if show_custom:
			filename = Path(self._custom_model_path).name
			self.model_filename_label.setToolTip(filename)
			self.model_filename_label.setText(
				self._elided_filename(filename, self.model_filename_label)
			)
		else:
			self.model_filename_label.clear()
			self.model_filename_label.setToolTip("")

	def _elided_filename(self, filename: str, label: QLabel) -> str:
		width = label.width()
		if width <= 0:
			left_margin, _, right_margin, _ = self.layout().getContentsMargins()
			width = self.width() - left_margin - right_margin
		metrics = QFontMetrics(label.font())
		return metrics.elidedText(filename, Qt.ElideMiddle, max(1, width))

	def _update_controls(self) -> None:
		self.browse_model_button.setEnabled(
			not self._running and not self.built_in_checkbox.isChecked()
		)
		self._update_run_button()

	def _update_run_button(self) -> None:
		self._refresh_mode_summary()
		model_selected = self.built_in_checkbox.isChecked() or bool(
			self._custom_model_path
		)
		self.run_button.setEnabled(
			not self._running
		and self._model_ready
		and bool(self._image_path)
		and model_selected
		)

	def _task_toggled(self, checked: bool) -> None:
		if not checked:
			return
		task_type = "classification" if self.classification_radio.isChecked() else "segmentation"
		self._refresh_mode_summary()
		self.task_changed.emit(task_type)

	def _emit_run_requested(self) -> None:
		use_built_in = self.built_in_checkbox.isChecked()
		model_path = "" if use_built_in else self._custom_model_path
		task_type = (
			"classification"
			if self.classification_radio.isChecked()
			else "segmentation"
		)
		self.run_requested.emit(
			model_path, use_built_in, self._image_path, task_type
		)
