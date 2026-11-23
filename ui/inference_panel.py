"""Controls for selecting an image, model, and inference task."""

from pathlib import Path
from PIL import Image

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (
	QApplication,
	QStyle,
	QFileDialog,
	QScrollArea,
	QLayout,
	QSizePolicy,
	QGroupBox,
	QLabel,
	QPushButton,
	QVBoxLayout,
	QHBoxLayout,
	QToolButton,
	QWidget,
)

from ui.language import tr
from ui.choice_check_box import ChoiceCheckBox
from ui.explicit_combo_box import ExplicitComboBox
from ui.theme import ERROR, SUCCESS, style_panel_scroll
from ui.image_pixels import rgb_pixmap
from core.classification_input import DEFAULT_CLASSIFICATION_RESIZE, DEFAULT_CLASSIFICATION_TILE_SIZE


class InferencePanel(QWidget):
	"""Let the user choose model and image inputs for an inference request."""

	run_requested = pyqtSignal(str, bool, str, str)
	cancel_requested = pyqtSignal()
	custom_model_chosen = pyqtSignal(str)
	use_builtin_changed = pyqtSignal(bool)
	task_changed = pyqtSignal(str)
	model_input_requested = pyqtSignal()
	input_profile_changed = pyqtSignal()
	image_loading_changed = pyqtSignal(bool)
	image_preview_changed = pyqtSignal(QPixmap, bool)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("InferencePanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._custom_model_path = ""
		self._image_path = ""
		self._image_worker = None
		self._image_load_generation = 0
		self._pending_image_load = None
		self._image_filename = ""
		self._image_identity = None
		self._image_snapshot = None
		self._preview_decoder = None
		self._source_pixmap = QPixmap()
		self._running = False
		self._model_ready = True
		self._active_input_profile = None
		self._pending_model_input = None
		self._border_coverage = {False: False, True: False}
		self._pixel_tile_override = None
		self._manual_mpp = None
		self._manual_mpp_decoder = None
		self._image_calibration = None
		self._calibration_error = ""
		self._matched_run_problem = ""
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

		self.built_in_checkbox = ChoiceCheckBox(tr("Use Built-in Model"), self)
		self.built_in_checkbox.setChecked(True)
		self.built_in_checkbox.setToolTip(
			tr("Checked: use the built-in model for this task. Unchecked: return to the last local model "
			"selected in this session, or browse for one. Startup defaults are set in Settings > Models.")
		)
		layout.addWidget(self.built_in_checkbox)

		self.browse_model_button = QPushButton(tr("Browse Model..."), self)
		self.browse_model_button.setToolTip(
			tr("Choose a local PyTorch model for this session. This does not save a startup default.")
		)
		layout.addWidget(self.browse_model_button)

		self.model_filename_label = QLabel(self)
		self.model_filename_label.setTextFormat(Qt.PlainText)
		self.model_filename_label.setToolTip(tr("Selected custom model filename."))
		self.model_filename_label.setWordWrap(False)
		self.model_filename_label.hide()
		layout.addWidget(self.model_filename_label)

		self.trust_warning_label = QLabel(
			tr("Only load model files from sources you trust."), self
		)
		self.trust_warning_label.setToolTip(tr("Model files can contain executable code."))
		self.trust_warning_label.setWordWrap(True)
		self.trust_warning_label.hide()
		layout.addWidget(self.trust_warning_label)

		self.model_status_label = QLabel(
			tr("⚠ Built-in model: not loaded yet"), self
		)
		self.model_status_label.setToolTip(tr("Current model selection status."))
		self.model_status_label.setWordWrap(True)
		self.model_status_label.setTextFormat(Qt.PlainText)
		self.model_status_label.setStyleSheet(f"color: {ERROR};")

		self.upload_image_button = QPushButton(tr("Upload Image..."), self)
		self.upload_image_button.setToolTip(tr("Choose an image for inference."))
		layout.addWidget(self.upload_image_button)
		# Keep primary input controls above potentially tall model-status text.
		layout.addWidget(self.model_status_label)

		self.thumbnail_label = QLabel(self)
		self.thumbnail_label.setAlignment(Qt.AlignCenter)
		self.thumbnail_label.setMaximumSize(248, 100)
		self.thumbnail_label.setToolTip(tr("Preview of the selected image."))
		self.thumbnail_label.hide()
		layout.addWidget(self.thumbnail_label, alignment=Qt.AlignHCenter)

		self.image_filename_label = QLabel(self)
		self.image_filename_label.setTextFormat(Qt.PlainText)
		self.image_filename_label.setToolTip(tr("Selected image filename."))
		self.image_filename_label.setWordWrap(False)
		self.image_filename_label.hide()
		layout.addWidget(self.image_filename_label)

		self.image_error_label = QLabel(self)
		self.image_error_label.setToolTip(tr("Image loading status."))
		self.image_error_label.setWordWrap(True)
		self.image_error_label.hide()
		layout.addWidget(self.image_error_label)

		task_group = QGroupBox(tr("Task"), self)
		task_group.setToolTip(tr("Choose the type of inference task."))
		task_layout = QVBoxLayout(task_group)
		task_layout.setContentsMargins(8, 8, 8, 8)
		self.task_combo = ExplicitComboBox(task_group)
		self.task_combo.setObjectName("inferenceTask")
		self.task_combo.setAccessibleName(tr("Task"))
		self.task_combo.addItem(tr("Single-image classification"), "single_image")
		self.task_combo.addItem(tr("Tiled classification"), "tiled_analysis")
		self.task_combo.addItem(tr("Segmentation"), "segmentation")
		self.task_combo.setToolTip(tr("Choose whole-image classification, tile-by-tile classification, or pixel-level segmentation."))
		self._task_type = "classification"
		self._classification_mode = "single_image"
		task_layout.addWidget(self.task_combo)
		layout.addWidget(task_group)
		self.input_setup_group = QGroupBox(tr("Input and scale"), self)
		self.input_setup_group.setObjectName("inputSetupCard")
		scale_layout = QVBoxLayout(self.input_setup_group)
		scale_layout.setContentsMargins(10, 14, 10, 10)
		self.scale_mode_label = QLabel(tr("Pixel settings"), self.input_setup_group)
		self.scale_mode_label.setObjectName("scaleModeBadge")
		scale_layout.addWidget(self.scale_mode_label)
		self.model_input_button = QPushButton(tr("Model requirements…"), self)
		self.model_input_button.setProperty("secondary", True)
		self.model_input_button.setToolTip(tr("View built-in model requirements, or configure a local model. The setup button above handles the current image's MPP and sampling."))
		self.model_input_button.clicked.connect(self.model_input_requested)
		self.image_scale_button = QPushButton(tr("Image sampling…"), self)
		self.image_scale_button.setToolTip(tr("Set crop sizes or known MPP for this image and preview the result."))
		self.image_scale_button.clicked.connect(self._configure_image_scale)
		scale_layout.addWidget(self.image_scale_button)
		self.match_scale_checkbox = ChoiceCheckBox(tr("Match tissue scale"), self)
		self.match_scale_checkbox.setObjectName("matchPhysicalScale")
		self.match_scale_checkbox.setToolTip(tr("Use this image's MPP and the model's documented tissue field. Pixel mode keeps explicit source-tile dimensions."))
		match_controls = QWidget(self)
		match_row = QHBoxLayout(match_controls)
		match_row.setContentsMargins(0, 0, 0, 0)
		match_row.setSpacing(4)
		match_row.addWidget(self.match_scale_checkbox)
		match_row.addStretch()
		self.scale_help_button = QToolButton(match_controls)
		self.scale_help_button.setText(tr("Help"))
		self.scale_help_button.setAccessibleName(tr("Physical scale matching help"))
		self.scale_help_button.setToolTip(tr("What matching does, why it may be unavailable, and how to enable it."))
		self.scale_help_button.clicked.connect(self._show_scale_help)
		# The dialog is the only visible sampling selector. Keep the checkbox as
		# the internal state used by inference, without a second confirmation step.
		match_controls.hide()
		self.scale_availability_label = QLabel(self)
		self.scale_availability_label.setTextFormat(Qt.PlainText)
		self.scale_availability_label.setWordWrap(True)
		self.scale_availability_label.setMinimumWidth(0)
		self.scale_availability_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
		scale_layout.addWidget(self.scale_availability_label)
		self.scale_summary = QLabel(self)
		self.scale_summary.setTextFormat(Qt.PlainText)
		self.scale_summary.setWordWrap(True)
		self.scale_summary.setMinimumWidth(0)
		self.scale_summary.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
		scale_layout.addWidget(self.scale_summary)
		more = QHBoxLayout()
		more.addWidget(self.model_input_button, 1)
		more.addWidget(self.scale_help_button)
		scale_layout.addLayout(more)
		layout.addWidget(self.input_setup_group)
		self.plan_compact_label = QLabel(self)
		self.plan_compact_label.setObjectName("runPlanSummary")
		self.plan_compact_label.setWordWrap(True)
		self.plan_compact_label.setTextFormat(Qt.PlainText)
		self.plan_compact_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
		self.plan_compact_label.hide()
		self._classification_parameters = {"tile_size": [DEFAULT_CLASSIFICATION_TILE_SIZE] * 2,
			"resize_backend": DEFAULT_CLASSIFICATION_RESIZE}

		self.run_button = QPushButton(tr("Run Inference"), self)
		self.run_button.setObjectName("runInferenceButton")
		self.run_button.setToolTip(tr("Send the selected inputs as an inference request."))
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
		outer.addWidget(self.plan_compact_label)
		outer.addWidget(self.run_button)
		self.cancel_button = QPushButton(tr("Cancel inference"), self)
		self.cancel_button.setObjectName("cancelInferenceButton")
		self.cancel_button.setToolTip(tr("Stop after the current model operation finishes. Partial results are discarded."))
		self.cancel_button.hide()
		self.cancel_button.clicked.connect(self.cancel_requested)
		outer.addWidget(self.cancel_button)
		for label in (self.model_status_label, self.trust_warning_label, self.image_error_label):
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
				match_controls,
				self.run_button,
			)
		)
		# Keep the calculated readable width when the outer layout reapplies its
		# minimum height for the pinned Run/Cancel buttons.
		self.controls_scroll.setMinimumWidth(
			max(240 - outer_left - outer_right, content_width + left_margin + right_margin + self.style().pixelMetric(QStyle.PM_ScrollBarExtent))
		)
		self.setMinimumWidth(
			max(240, content_width + left_margin + right_margin + outer_left + outer_right + self.style().pixelMetric(QStyle.PM_ScrollBarExtent))
		)

		self.built_in_checkbox.toggled.connect(self._on_built_in_toggled)
		self.browse_model_button.clicked.connect(self._browse_model)
		self.upload_image_button.clicked.connect(self._browse_image)
		self.run_button.clicked.connect(self._emit_run_requested)
		self.task_combo.currentIndexChanged.connect(self._task_selection_changed)
		self._on_built_in_toggled(self.built_in_checkbox.isChecked())
		QApplication.instance().focusChanged.connect(self._ensure_focused_control_visible)
		self.match_scale_checkbox.toggled.connect(self._update_run_button)
		self._refresh_scale_information()
		self._ensure_input_card_width()

	def _ensure_input_card_width(self) -> None:
		if not hasattr(self, "controls_scroll"):
			return
		left, _, right, _ = self.layout().getContentsMargins()
		scrollbar = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
		content_width = max(self.input_setup_group.minimumSizeHint().width(),
			self.upload_image_button.sizeHint().width(), self.run_button.sizeHint().width())
		self.controls_scroll.setMinimumWidth(max(240 - left - right, content_width + scrollbar))
		self.setMinimumWidth(max(240, content_width + scrollbar + left + right))

	def _ensure_focused_control_visible(self, old, current) -> None:
		if current is not None and self.controls_scroll.widget().isAncestorOf(current):
			self.controls_scroll.ensureWidgetVisible(current, 0, 0)

	def clear_image(self, *, cancel_loading=True) -> None:
		"""Remove the current image and its image-specific settings."""
		if cancel_loading:
			self.cancel_image_load()
		self._image_path = ""
		self._image_filename = ""
		self._image_identity = None
		self._image_snapshot = None
		self._preview_decoder = None
		self._source_pixmap = QPixmap()
		self._border_coverage = {False: False, True: False}
		self._pixel_tile_override = None
		self._manual_mpp = None
		self._manual_mpp_decoder = None
		self._image_calibration = None
		self._calibration_error = ""
		self.match_scale_checkbox.setChecked(False)
		self._refresh_scale_information()
		self.thumbnail_label.clear()
		self.thumbnail_label.hide()
		self.image_filename_label.clear()
		self.image_filename_label.hide()
		self.image_filename_label.setToolTip("")
		self.image_error_label.clear()
		self.image_error_label.hide()
		self._update_run_button()
		self.image_preview_changed.emit(self._source_pixmap, False)

	def source_image_size(self):
		return tuple(self._image_snapshot["image_size"]) if self._image_snapshot else (0, 0)

	def image_loading(self):
		return self._image_worker is not None or self._pending_image_load is not None

	def load_image_async(self, path):
		self._image_load_generation += 1
		self._pending_image_load = (str(path), self._image_load_generation)
		self.clear_image(cancel_loading=False)
		self.image_error_label.setText(tr("Loading and verifying image…"))
		self.image_error_label.show()
		self.image_loading_changed.emit(True)
		if self._image_worker is not None:
			self._image_worker.requestInterruption()
			return
		self._start_pending_image_load()

	def _start_pending_image_load(self):
		if self._pending_image_load is None:
			self.image_loading_changed.emit(False)
			return
		from ui.image_load_worker import ImageLoadWorker
		path, generation = self._pending_image_load
		self._pending_image_load = None
		worker = ImageLoadWorker(path, self._image_decoder(), self)
		worker.generation = generation
		self._image_worker = worker
		worker.ready.connect(self._image_load_ready)
		worker.failed.connect(self._image_load_failed)
		worker.finished.connect(self._image_load_finished)
		worker.finished.connect(worker.deleteLater)
		worker.start()

	def _image_load_ready(self, image, identity):
		worker = self.sender()
		if worker.generation != self._image_load_generation:
			return
		if worker.decoder != self._image_decoder():
			self._pending_image_load = (worker.path, worker.generation)
			return
		self.set_image(worker.path, original_pil=image, source_identity=identity, _from_worker=True)

	def _image_load_failed(self, message):
		if self.sender().generation == self._image_load_generation:
			self.image_error_label.setText(message)
			self.image_error_label.show()

	def _image_load_finished(self):
		self._image_worker = None
		self._start_pending_image_load()

	def cancel_image_load(self):
		self._image_load_generation += 1
		self._pending_image_load = None
		if self._image_worker is not None:
			self._image_worker.requestInterruption()

	def set_image(self, path: str, *, original_pil=None, source_identity=None, _from_worker=False) -> None:
		"""Load an image preview and update whether inference can be requested."""
		if not _from_worker:
			self.cancel_image_load()
		try:
			stat = Path(path).stat() if path else None
			identity = (stat.st_size, stat.st_mtime_ns) if stat else None
		except OSError:
			identity = None
		previous = (self._manual_mpp, self.match_scale_checkbox.isChecked(), self._manual_mpp_decoder)
		previous_snapshot = getattr(self, "_image_snapshot", None)
		previous_coverage = self._border_coverage
		previous_path, previous_tile = self._image_path, self._pixel_tile_override
		self.clear_image(cancel_loading=False)
		try:
			from core.image_source import load_verified_image
			# Bind even manually entered MPP to the previewed bytes, not just a filename.
			if original_pil is not None and source_identity is not None:
				from core.image_source import validate_identity
				snapshot = validate_identity(source_identity)
				preview = original_pil.copy()
			else:
				preview, snapshot = load_verified_image(path, decoder=self._image_decoder()) if path else (None, None)
			if preview is not None:
				from core.image_budget import PREVIEW_MAX_SIDE
				preview.thumbnail((PREVIEW_MAX_SIDE, PREVIEW_MAX_SIDE), Image.Resampling.LANCZOS)
			pixmap = rgb_pixmap(preview) if preview is not None else QPixmap()
		except (OSError, ValueError, Image.DecompressionBombError) as error:
			self.image_error_label.setText(tr("This image could not be opened. ") + str(error))
			pixmap = QPixmap()
		if not path or pixmap.isNull():
			self.image_error_label.setText(self.image_error_label.text() or "This image could not be opened. Please choose another file.")
			self.image_error_label.show()
			self._update_run_button()
			return

		self._image_path = str(path)
		self._image_identity = identity
		self._image_snapshot = snapshot
		if previous_snapshot != snapshot:
			previous = (None, False, None)
		if previous_snapshot == snapshot:
			self._border_coverage = previous_coverage
		if previous_path == self._image_path and previous_snapshot == snapshot:
			self._pixel_tile_override = previous_tile
		self._manual_mpp = previous[0]
		self._manual_mpp_decoder = previous[2]
		self._image_filename = Path(path).name
		self._source_pixmap = pixmap
		self._preview_decoder = snapshot["image_decoder"]
		self._refresh_thumbnail()
		self.thumbnail_label.show()
		self.image_filename_label.setToolTip(self._image_filename)
		self.image_filename_label.show()
		self._refresh_filename_labels()
		self._refresh_scale_information()
		self.match_scale_checkbox.setChecked(previous[1] and self.match_scale_checkbox.isEnabled())
		self._update_run_button()
		reduced = self.source_image_size() != (pixmap.width(), pixmap.height())
		self.image_preview_changed.emit(pixmap, reduced)

	def set_active_input_profile(self, profile) -> None:
		previous = self._active_input_profile
		previous_decoder = self._preview_decoder or self._image_decoder()
		self._active_input_profile = profile
		decoder_changed = previous_decoder != self._image_decoder()
		if decoder_changed:
			self._border_coverage = {False: False, True: False}
			self._manual_mpp = None
			self._manual_mpp_decoder = None
		if previous != profile:
			self.match_scale_checkbox.setChecked(False)
		if decoder_changed and self._image_path:
			self.set_image(self._image_path)
		self._refresh_scale_information()
		self._refresh_mode_summary()
		self.input_profile_changed.emit()

	def begin_model_input_change(self, *, validating=True) -> None:
		"""Suspend a contract without turning the user's matching choice off."""
		if self._pending_model_input is None:
			identity = getattr(self, "_image_snapshot", None)
			self._pending_model_input = {
				"identity": dict(identity) if identity else None,
				"manual_mpp": self._manual_mpp,
				"border_coverage": self._border_coverage.copy(),
				"match_scale": self.match_scale_checkbox.isChecked(),
			}
		if validating:
			self.set_model_ready(False)
		self.set_active_input_profile(None)

	def finish_model_input_change(self, profile) -> None:
		state = self._pending_model_input
		self._pending_model_input = None
		self.set_active_input_profile(profile)
		if not state or not state["identity"] or state["identity"] != getattr(self, "_image_snapshot", None):
			return
		try:
			from core.image_source import verify_image_source
			verify_image_source(self._image_path, state["identity"])
		except (OSError, ValueError):
			return
		if profile and profile.task_type == "classification" and profile.input_scope == "patch":
			self._border_coverage = state["border_coverage"]
		self._manual_mpp = state["manual_mpp"]
		self._manual_mpp_decoder = self._image_decoder() if self._manual_mpp else None
		self._refresh_scale_information()
		# Geometry is recalculated from the NEW model. Never carry its predecessor's
		# field or tile size forward, or force matching on an undocumented field.
		self.match_scale_checkbox.setChecked(bool(state["match_scale"] and profile and self.match_scale_checkbox.isEnabled()))
		self._refresh_mode_summary()

	def cancel_model_input_change(self) -> None:
		self._pending_model_input = None
		self.set_active_input_profile(None)

	def cover_borders(self) -> bool:
		profile = self._active_input_profile
		return bool(profile and profile.task_type == "classification" and profile.input_scope == "patch"
			and self.task_type() == "classification" and self.classification_mode() == "tiled_analysis"
			and self._border_coverage[self.match_scale_checkbox.isChecked()])

	def input_options(self) -> dict:
		return {**({"cover_borders": True} if self.cover_borders() else {}),
				"match_scale": self.match_scale_checkbox.isChecked(),
				"manual_mpp": list(self._manual_mpp) if self._manual_mpp else None,
				"expected_image_identity": dict(self._image_snapshot) if getattr(self, "_image_snapshot", None) else None}

	def restore_input_context(self, analysis: dict, *, verified_identity=None) -> None:
		"""Restore a verified run's calibration without guessing from its model."""
		from core.image_source import analysis_identity, verify_image_source
		from core.model_profile import positive_pair
		context = analysis.get("spatial_context")
		if not isinstance(context, dict) or not self._image_path:
			return
		try:
			identity = analysis_identity(analysis)
			if verified_identity is None:
				identity = verify_image_source(self._image_path, identity)
			elif identity != verified_identity:
				return
			if identity != self._image_snapshot:
				return
			calibration = context.get("calibration") or {}
			if not isinstance(calibration, dict):
				return
			values = positive_pair(calibration["mpp"], "Recorded image MPP") if calibration.get("mpp") else None
		except (OSError, ValueError, TypeError, KeyError):
			return
		self._border_coverage[context.get("mode") == "physical"] = analysis.get("edge_policy") == "cover"
		# Recorded calibration belongs to these image bytes, including when the
		# image was opened from another path or revisited through History.
		self._manual_mpp = values if calibration.get("source") == "manual entry" else None
		self._manual_mpp_decoder = self._image_decoder() if self._manual_mpp else None
		profile = self._active_input_profile
		saved = analysis.get("input_profile")
		compatible = bool(profile and isinstance(saved, dict) and {**profile.to_dict(), "source": ""} == {**saved, "source": ""})
		self._refresh_scale_information()
		self.match_scale_checkbox.setChecked(bool(compatible and context.get("mode") == "physical" and self.match_scale_checkbox.isEnabled()))
		self._refresh_mode_summary()

	def _image_decoder(self):
		if self._active_input_profile:
			return self._active_input_profile.image_decoder
		return "opencv_color" if self.task_type() == "classification" else "pillow_rgb"

	def _refresh_scale_information(self) -> None:
		from core.image_calibration import read_image_calibration
		if self._manual_mpp is not None and self._manual_mpp_decoder not in (None, self._image_decoder()):
			self._border_coverage = {False: False, True: False}
			self._manual_mpp = None
			self._manual_mpp_decoder = None
		if self._manual_mpp is not None:
			self._manual_mpp_decoder = self._image_decoder()
		self._image_calibration, self._calibration_error = None, ""
		if self._image_path:
			try:
				self._image_calibration = read_image_calibration(self._image_path, self._image_decoder(), manual_mpp=self._manual_mpp)
			except (OSError, ValueError, Image.DecompressionBombError) as error:
				self._calibration_error = str(error)
		from ui.input_help import scale_readiness
		profile, calibration = self._active_input_profile, self._image_calibration
		known_mpp = calibration is not None and calibration.mpp is not None
		can_match = scale_readiness(profile, calibration, has_image=bool(self._image_path), calibration_error=self._calibration_error).available
		self.match_scale_checkbox.setEnabled(can_match)
		if not can_match:
			self.match_scale_checkbox.setChecked(False)
		text = (tr("Image MPP: {width:g} x {height:g} um/px ({source})").format(
				width=calibration.mpp[0], height=calibration.mpp[1], source=tr(calibration.source))
				if known_mpp else tr("Image MPP: not recorded"))
		if self._calibration_error:
			text = tr("Image calibration") + ": " + self._calibration_error
		if profile:
			text += ("\n" + tr("Model field: {width:g} x {height:g} um").format(
					width=profile.field_um[0], height=profile.field_um[1])
					 if profile.field_um else "\n" + tr("Model physical field: not established; pixel mode"))
		else:
			text += "\n" + tr("Model input profile: not supplied; legacy pixel settings")
		self.scale_summary.setText(text)
		self.image_scale_button.setText(tr("Image sampling…"))
		if hasattr(self, "run_button"):
			self._update_run_button()
		else:
			self._update_scale_explanation()

	def _update_scale_explanation(self):
		from ui.input_help import scale_readiness
		state = scale_readiness(self._active_input_profile, self._image_calibration,
			has_image=bool(self._image_path), calibration_error=self._calibration_error)
		message = state.explanation()
		self._matched_run_problem = ""
		if self.match_scale_checkbox.isChecked():
			if not state.available:
				self._matched_run_problem = message
			elif self.task_type() == "classification":
				tile = state.tile_size
				size = self._image_calibration.image_size
				if self.classification_mode() == "single_image" and size != tile:
					self._matched_run_problem = tr("Choose Tiled analysis for this image. Matched Single image must contain exactly one model field.")
				elif self.classification_mode() == "tiled_analysis" and self._active_input_profile.edge_policy == "skip" and any(n < crop for n, crop in zip(size, tile)):
					self._matched_run_problem = tr("This image is smaller than one model field. Use a larger calibrated region; no complete field fits.")
				message = (self._matched_run_problem or tr("Matching on: {width} x {height} source pixels per model field. Pixel tile preferences are not used.")
					.format(width=tile[0], height=tile[1]))
			else:
				message = tr("Matching on: processing regions are calculated from image MPP and the model's documented field.")
		elif state.available:
			message = tr("MPP is recorded. Open Image sampling to use tissue matching or keep pixel sizes.")
		from ui.input_plan import input_preview
		preview = input_preview(self._active_input_profile, self._image_calibration,
			self.source_image_size() if self._image_path else None,
			task=self.task_type(),
			classification_mode=self.classification_mode(), matched=self.match_scale_checkbox.isChecked(),
			pixel_tile=self.classification_parameters()["tile_size"], calibration_error=self._calibration_error, cover_borders=self.cover_borders())
		if preview.problem and self._image_path:
			self._matched_run_problem = preview.problem
			message = preview.problem
		mode_label = tr("Match tissue scale") if self.match_scale_checkbox.isChecked() else tr("Pixel settings")
		self.scale_mode_label.setText(mode_label)
		self.image_scale_button.setText(tr("Image sampling…"))
		if preview.problem:
			compact = tr("Review sampling settings")
		elif preview.tile and preview.network and preview.count is not None:
			tiled = self.task_type() == "classification" and self.classification_mode() == "tiled_analysis"
			if tiled:
				quantity = tr("1 tile") if preview.count == 1 else tr("{count:,} tiles").format(count=preview.count)
			elif self.task_type() == "classification":
				quantity = tr("Whole image")
			else:
				quantity = tr("{count:,} processing regions").format(count=preview.count)
			dimensions = tr("{source} source px → {target} model px").format(
				source=" × ".join(map(str, preview.tile)), target=" × ".join(map(str, preview.network)))
			compact = f"{mode_label} · {quantity}\n{dimensions}"
		else:
			compact = f"{mode_label} · {tr('model input details unavailable')}"
		self.plan_compact_label.setText(compact)
		self.plan_compact_label.setToolTip(preview.problem or "\n".join((compact, *preview.notes)))
		self._update_plan_visibility()
		self.scale_availability_label.setText(message)
		self.scale_availability_label.setVisible(not state.available or bool(self._matched_run_problem))
		self.match_scale_checkbox.setToolTip(message)
		self._ensure_input_card_width()
		return preview

	def _update_plan_visibility(self):
		show_summary = bool(self._image_path) and self.height() >= 260
		self.plan_compact_label.setVisible(show_summary)
		self.scale_mode_label.setVisible(not show_summary)

	def _show_scale_help(self) -> None:
		from ui.input_help import scale_readiness, show_input_help
		state = scale_readiness(self._active_input_profile, self._image_calibration,
			has_image=bool(self._image_path), calibration_error=self._calibration_error)
		show_input_help(self, "scale", readiness=state)

	def _configure_image_scale(self) -> None:
		if not self._image_path or self._running or not self._model_ready:
			return
		from ui.input_setup import InputSetupDialog
		dialog = InputSetupDialog(self)
		self._input_setup_dialog = dialog
		if dialog.exec_():
			choices = dialog.choices()
			self._border_coverage = choices["border_coverage"]
			self.match_scale_checkbox.setChecked(False)
			self._manual_mpp = choices["manual_mpp"]
			self._manual_mpp_decoder = self._image_decoder() if self._manual_mpp else None
			if choices["pixel_tile"] is not None:
				self._pixel_tile_override = tuple(choices["pixel_tile"])
			self.set_classification_mode(choices["classification_mode"])
			self._refresh_scale_information()
			self.match_scale_checkbox.setChecked(choices["match_scale"] and self.match_scale_checkbox.isEnabled())
			self._refresh_mode_summary()
		self._input_setup_dialog = None
		dialog.deleteLater()

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
		"""Select the task, restoring the last classification mode when needed."""
		if task_type not in ("classification", "segmentation"):
			raise ValueError("Task type must be 'classification' or 'segmentation'.")
		choice = self._classification_mode if task_type == "classification" else task_type
		self.task_combo.setCurrentIndex(self.task_combo.findData(choice))

	def task_type(self) -> str:
		return self._task_type

	def classification_mode(self) -> str:
		return self._classification_mode

	def set_classification_mode(self, mode: str) -> None:
		if mode not in ("single_image", "tiled_analysis"):
			raise ValueError("Unknown classification mode.")
		self._classification_mode = mode
		if self.task_type() == "classification":
			self.task_combo.setCurrentIndex(self.task_combo.findData(mode))

	def classification_parameters(self) -> dict:
		parameters = {**self._classification_parameters, "classification_mode": self.classification_mode()}
		if self._pixel_tile_override is not None:
			parameters["tile_size"] = list(self._pixel_tile_override)
		return parameters

	def set_classification_parameters(self, parameters: dict) -> None:
		self._classification_parameters = dict(parameters)
		self._update_run_button()

	def _refresh_mode_summary(self) -> None:
		task = self.task_type()
		classification = task == "classification"
		model = (self._builtin_model_names.get(task, tr("Not selected"))
				 if self.built_in_checkbox.isChecked()
				 else Path(self._custom_model_path).name or tr("Not selected"))
		mode = tr("Tiled analysis") if self.classification_mode() == "tiled_analysis" else tr("Single image")
		text = f"{tr('Classification')}: {mode}" if classification else tr("Selected task: Segmentation")
		text += f"\n{tr('Model')}: {model}"
		if not self._source_pixmap.isNull():
			width, height = self.source_image_size()
			text += f"\n{tr('Image')}: {width} x {height} px"
		else:
			width = height = 0
			text += f"\n{tr('Image')}: {tr('not selected')}"
		parameters = self.classification_parameters()
		preview = self._update_scale_explanation()
		if classification and self.classification_mode() == "tiled_analysis":
			w, h = preview.tile or parameters["tile_size"]
			if self.match_scale_checkbox.isChecked():
				note = tr(" Physical field matched.") if not preview.problem else tr(" Review physical matching.")
			else:
				note = tr(" Size set for this image.") if self._pixel_tile_override is not None else tr(" Default pixel size.")
			text += "\n" + tr("Original tiles: {width} x {height} px.").format(width=w, height=h) + note
			if preview.grid:
				columns, rows = preview.grid
				text += "\n" + tr("Planned tiles: {count} ({columns} columns x {rows} rows)").format(count=preview.count, columns=columns, rows=rows)
		if classification:
			profile = self._active_input_profile
			text += f"\n{tr('Resize')}: " + (profile.resize_backend if profile else parameters.get("resize_backend", DEFAULT_CLASSIFICATION_RESIZE))
			input_size = profile.input_size if profile else (224, 224)
			if self.classification_mode() == "single_image" and (width > input_size[0] or height > input_size[1]):
				text += "\n" + tr("Whole image resized to {width} x {height}. Use Tiled analysis for a patch-based model.").format(
					width=input_size[0], height=input_size[1])
		if hasattr(self, "run_button"):
			self.run_button.setToolTip(self._matched_run_problem or text)

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
		self.model_status_label.setText(f"{icon} {tr(text)}")
		self.model_status_label.setStyleSheet(f"color: {color};")

	def set_running(self, running: bool) -> None:
		"""Keep cancellation reachable while input controls are locked."""
		self._running = running
		self.run_button.setText(tr("Running...") if running else tr("Run Inference"))
		self.controls_scroll.setEnabled(not running)
		self.run_button.setVisible(not running)
		self.cancel_button.setVisible(running)
		self.cancel_button.setEnabled(running)
		self.cancel_button.setText(tr("Cancel inference"))
		self._update_controls()

	def set_cancelling(self) -> None:
		self.cancel_button.setText(tr("Cancelling…"))
		self.cancel_button.setEnabled(False)

	def _on_built_in_toggled(self, use_built_in: bool) -> None:
		self.browse_model_button.setVisible(not use_built_in)
		self.trust_warning_label.setVisible(not use_built_in)
		self._refresh_filename_labels()
		self._update_controls()
		self.use_builtin_changed.emit(use_built_in)

	def _browse_model(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self, tr("Select Model"), "", "PyTorch models (*.pt *.pth)"
		)
		if path:
			self.set_custom_model(path)

	def _browse_image(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self,
			tr("Select Image"),
			"",
			"Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp)",
		)
		if path:
			self.load_image_async(path)

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
		self._update_plan_visibility()
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
			self.scale_summary,
			self.scale_availability_label,
			self.plan_compact_label,
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
		ready = not self._running and self._model_ready and bool(self._image_path)
		self.image_scale_button.setEnabled(ready)
		model_selected = self.built_in_checkbox.isChecked() or bool(
			self._custom_model_path
		)
		self.run_button.setEnabled(ready and model_selected and not self._matched_run_problem)

	def _task_selection_changed(self) -> None:
		choice = self.task_combo.currentData()
		previous = self._task_type
		self._task_type = "segmentation" if choice == "segmentation" else "classification"
		if self._task_type == "classification":
			self._classification_mode = choice
		if self._task_type != previous:
			self.begin_model_input_change(validating=False)
			self.task_changed.emit(self._task_type)
		self._update_run_button()

	def _emit_run_requested(self) -> None:
		use_built_in = self.built_in_checkbox.isChecked()
		model_path = "" if use_built_in else self._custom_model_path
		self.run_requested.emit(model_path, use_built_in, self._image_path, self.task_type())
