"""Controls for selecting an image, model, and inference task."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QPixmap
from PyQt5.QtWidgets import (
	QFileDialog,
	QGroupBox,
	QLabel,
	QPushButton,
	QRadioButton,
	QCheckBox,
	QVBoxLayout,
	QWidget,
)

from ui.theme import ERROR, SUCCESS


class InferencePanel(QWidget):
	"""Let the user choose model and image inputs for an inference request."""

	run_requested = pyqtSignal(str, bool, str, str)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("InferencePanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setFixedWidth(280)
		self._custom_model_path = ""
		self._image_path = ""
		self._source_pixmap = QPixmap()
		self._running = False

		layout = QVBoxLayout(self)
		layout.setContentsMargins(16, 16, 16, 16)
		layout.setSpacing(10)

		self.built_in_checkbox = QCheckBox("Use Built-in Model", self)
		self.built_in_checkbox.setChecked(True)
		self.built_in_checkbox.setToolTip("Use the built-in model for inference.")
		layout.addWidget(self.built_in_checkbox)

		self.browse_model_button = QPushButton("Browse Model...", self)
		self.browse_model_button.setToolTip("Choose a PyTorch model file.")
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
		self.thumbnail_label.setMaximumSize(248, 140)
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
		task_layout.addWidget(self.segmentation_radio)
		layout.addWidget(task_group)

		self.run_button = QPushButton("Run Inference", self)
		self.run_button.setObjectName("runInferenceButton")
		self.run_button.setToolTip("Send the selected inputs as an inference request.")
		self.run_button.setEnabled(False)
		layout.addWidget(self.run_button)
		layout.addStretch()

		self.built_in_checkbox.toggled.connect(self._on_built_in_toggled)
		self.browse_model_button.clicked.connect(self._browse_model)
		self.upload_image_button.clicked.connect(self._browse_image)
		self.run_button.clicked.connect(self._emit_run_requested)
		self._on_built_in_toggled(self.built_in_checkbox.isChecked())

	def set_image(self, path: str) -> None:
		"""Load an image preview and update whether inference can be requested."""
		self._image_path = ""
		self._source_pixmap = QPixmap()
		self.thumbnail_label.clear()
		self.thumbnail_label.hide()
		self.image_filename_label.hide()
		self.image_error_label.hide()

		pixmap = QPixmap(path)
		if not path or pixmap.isNull():
			self.image_error_label.setText("This image could not be opened. Please choose another file.")
			self.image_error_label.show()
			self._update_run_button()
			return

		self._image_path = str(path)
		self._source_pixmap = pixmap
		self._refresh_thumbnail()
		self.thumbnail_label.show()
		self.image_filename_label.setText(self._elided_filename(Path(path).name))
		self.image_filename_label.show()
		self._update_run_button()

	def set_custom_model(self, path: str) -> None:
		"""Select a custom model path without validating or loading it."""
		self._custom_model_path = str(path)
		if self._custom_model_path:
			self.built_in_checkbox.setChecked(False)
			self.model_filename_label.setText(
				self._elided_filename(Path(self._custom_model_path).name)
			)
			self.model_filename_label.show()
			self.set_model_status("Custom model selected (not yet validated)", False)
		else:
			self.model_filename_label.hide()
			self.built_in_checkbox.setChecked(True)
			self.set_model_status("Built-in model: not loaded yet", False)
		self._update_run_button()

	def set_model_status(self, text: str, ok: bool) -> None:
		"""Show model status with an icon and the matching status color."""
		icon = "✔" if ok else "⚠"
		color = SUCCESS if ok else ERROR
		self.model_status_label.setText(f"{icon} {text}")
		self.model_status_label.setStyleSheet(f"color: {color};")

	def set_running(self, running: bool) -> None:
		"""Disable the panel while a future inference request is running."""
		self._running = running
		self.run_button.setText("Running..." if running else "Run Inference")
		self.setEnabled(not running)
		self._update_controls()

	def _on_built_in_toggled(self, use_built_in: bool) -> None:
		self.trust_warning_label.setVisible(not use_built_in)
		self.browse_model_button.setEnabled(not use_built_in and not self._running)
		if use_built_in:
			self.set_model_status("Built-in model: not loaded yet", False)
		elif self._custom_model_path:
			self.set_model_status("Custom model selected (not yet validated)", False)
		self._update_run_button()

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
				140,
				Qt.KeepAspectRatio,
				Qt.SmoothTransformation,
			)
		)

	def _elided_filename(self, filename: str) -> str:
		metrics = QFontMetrics(self.font())
		return metrics.elidedText(filename, Qt.ElideMiddle, 248)

	def _update_controls(self) -> None:
		self.browse_model_button.setEnabled(
			not self._running and not self.built_in_checkbox.isChecked()
		)
		self._update_run_button()

	def _update_run_button(self) -> None:
		model_selected = self.built_in_checkbox.isChecked() or bool(
			self._custom_model_path
		)
		self.run_button.setEnabled(
			not self._running and bool(self._image_path) and model_selected
		)

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
