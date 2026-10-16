"""Display original images and inference results."""

from pathlib import Path

from PIL import Image
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (
	QHBoxLayout,
	QLabel,
	QSlider,
	QSizePolicy,
	QSplitter,
	QStackedWidget,
	QVBoxLayout,
	QWidget,
	QLayout,
	QScrollArea,
)

from ui.theme import ACCENT, splitter_style, style_panel_scroll
from ui.classification_result import ClassificationResult
from ui.zoomable_image_view import ZoomableImageView


class _ResultCanvas(FigureCanvasQTAgg):
	"""Keep the Qt owner alive while Matplotlib renders a queued redraw."""

	def draw(self) -> None:
		# The callback retains the canvas, but Qt parenting does not retain the
		# Python window. GC during figure rendering must not delete its children.
		owner = self.window()
		try:
			super().draw()
		finally:
			del owner


class ResultPanel(QWidget):
	"""Show the source image and classification or segmentation results."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("ResultPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._source_pixmap = QPixmap()
		self._result_figure = Figure(figsize=(6.2, 4.0), constrained_layout=True)
		self._has_classification_result = False
		self._segmentation_original: Image.Image | None = None
		self._segmentation_color_mask: Image.Image | None = None

		layout = QVBoxLayout(self)
		layout.setSizeConstraint(QLayout.SetNoConstraint)
		self.setMinimumSize(0, 0)
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		layout.setContentsMargins(16, 16, 16, 16)
		layout.setSpacing(12)

		self.image_label = ZoomableImageView(self)
		self.image_label.setObjectName("sourceImageLabel")
		self.image_label.setText("Upload an image and run inference")
		self.image_label.setToolTip("Preview of the original image.")

		self.result_stack = QStackedWidget(self)
		self.result_stack.setObjectName("resultStack")
		self.empty_page = self._create_empty_page()
		self.classification_page = QWidget(self.result_stack)
		self.segmentation_page = QWidget(self.result_stack)
		self.result_stack.addWidget(self.empty_page)
		self.result_stack.addWidget(self.classification_page)
		self.result_stack.addWidget(self.segmentation_page)
		self.tile_page = ClassificationResult(self.result_stack)
		self.tile_image = self.tile_page.image
		self.tile_summary = self.tile_page.summary
		self.tile_table = self.tile_page.table
		self.result_stack.addWidget(self.tile_page)
		self.result_stack.setMinimumSize(0, 0)
		self.result_stack.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

		self.vertical_splitter = QSplitter(Qt.Vertical, self)
		self.vertical_splitter.setObjectName("resultVerticalSplitter")
		self.vertical_splitter.setHandleWidth(8)
		self.vertical_splitter.setChildrenCollapsible(False)
		self.vertical_splitter.setStyleSheet(splitter_style("Light"))
		self.image_pane = QWidget(self.vertical_splitter)
		image_pane_layout = QVBoxLayout(self.image_pane)
		image_pane_layout.setContentsMargins(0, 0, 0, 0)
		image_pane_layout.addWidget(self.image_label)
		self.image_pane.setMinimumHeight(0)
		self.result_pane = QWidget(self.vertical_splitter)
		result_pane_layout = QVBoxLayout(self.result_pane)
		result_pane_layout.setContentsMargins(0, 0, 0, 0)
		result_pane_layout.addWidget(self.result_stack)
		self.result_pane.setMinimumHeight(0)
		self.vertical_splitter.addWidget(self.image_pane)
		self.vertical_splitter.addWidget(self.result_pane)
		for pane in (self.image_pane, self.result_pane, self.empty_page,
					 self.classification_page, self.segmentation_page, self.tile_page):
			pane.setProperty("panelSurface", True)
		self.vertical_splitter.setStretchFactor(0, 2)
		self.vertical_splitter.setStretchFactor(1, 3)
		# Keep image controls readable on short screens, scrolling this pane rather
		# than propagating its content height into the top-level window.
		self.vertical_splitter.setMinimumHeight(400)
		self.content_scroll = QScrollArea(self)
		self.content_scroll.setWidgetResizable(True)
		self.content_scroll.setFrameShape(QScrollArea.NoFrame)
		self.content_scroll.setMinimumSize(0, 0)
		self.content_scroll.setWidget(self.vertical_splitter)
		style_panel_scroll(self.content_scroll)
		layout.addWidget(self.content_scroll, 1)
		QTimer.singleShot(0, self._set_initial_splitter_sizes)

		classification_outer = QVBoxLayout(self.classification_page)
		classification_outer.setContentsMargins(0, 0, 0, 0)
		self.classification_scroll = QScrollArea(self.classification_page)
		self.classification_scroll.setWidgetResizable(True)
		self.classification_scroll.setFrameShape(QScrollArea.NoFrame)
		classification_outer.addWidget(self.classification_scroll)
		classification_content = QWidget()
		self.classification_scroll.setWidget(classification_content)
		style_panel_scroll(self.classification_scroll)
		classification_layout = QVBoxLayout(classification_content)
		classification_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		classification_layout.setContentsMargins(8, 8, 8, 8)
		classification_layout.setSpacing(8)
		self.classification_label = QLabel(self.classification_page)
		self.classification_label.setObjectName("predictedClassLabel")
		self.classification_label.setToolTip("Predicted class label.")
		classification_layout.addWidget(self.classification_label)
		self.confidence_label = QLabel(self.classification_page)
		self.confidence_label.setObjectName("confidenceLabel")
		self.confidence_label.setToolTip("Confidence score for the predicted class.")
		classification_layout.addWidget(self.confidence_label)
		self.stored_result_label = ZoomableImageView(self.classification_page)
		self.stored_result_label.setObjectName("storedResultLabel")
		self.stored_result_label.setToolTip("Stored inference result image.")
		self.stored_result_label.hide()
		classification_layout.addWidget(self.stored_result_label, 1)
		self.result_canvas = _ResultCanvas(self._result_figure)
		self.result_canvas.setMinimumSize(300, 150)
		self.result_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.result_canvas.setToolTip("Class probability chart.")
		classification_layout.addWidget(self.result_canvas, 1)

		segmentation_outer = QVBoxLayout(self.segmentation_page)
		segmentation_outer.setContentsMargins(0, 0, 0, 0)
		self.segmentation_scroll = QScrollArea(self.segmentation_page)
		self.segmentation_scroll.setWidgetResizable(True)
		self.segmentation_scroll.setFrameShape(QScrollArea.NoFrame)
		segmentation_outer.addWidget(self.segmentation_scroll)
		segmentation_content = QWidget()
		segmentation_content.setMinimumWidth(600)
		self.segmentation_scroll.setWidget(segmentation_content)
		style_panel_scroll(self.segmentation_scroll)
		segmentation_layout = QHBoxLayout(segmentation_content)
		segmentation_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
		segmentation_layout.setContentsMargins(8, 8, 8, 8)
		segmentation_layout.setSpacing(16)
		self.overlay_label = ZoomableImageView(self.segmentation_page)
		self.overlay_label.setObjectName("segmentationOverlayLabel")
		self.overlay_label.setMinimumSize(120, 120)
		self.overlay_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.overlay_label.setToolTip("Segmentation overlay image.")
		segmentation_layout.addWidget(self.overlay_label, 3)

		self.legend_widget = QWidget(self.segmentation_page)
		self.legend_widget.setObjectName("segmentationLegend")
		self.legend_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.legend_layout = QVBoxLayout(self.legend_widget)
		self.legend_layout.setContentsMargins(0, 4, 0, 4)
		self.legend_layout.setSpacing(8)
		self.legend_rows: list[tuple[QHBoxLayout, QLabel, QLabel]] = []
		self.legend_layout.addStretch()
		self.area_label = QLabel(self.segmentation_page)
		self.area_label.setWordWrap(True)
		self.area_label.setToolTip("Predicted area percentage uses the full image as denominator.")
		self.legend_layout.insertWidget(0, self.area_label)
		self.alpha_slider = QSlider(Qt.Horizontal, self.segmentation_page)
		self.alpha_slider.setRange(0, 100)
		self.alpha_slider.setValue(20)
		self.alpha_slider.setToolTip("Overlay opacity")
		self.alpha_slider.valueChanged.connect(self._update_overlay_alpha)
		self.legend_layout.insertWidget(1, self.alpha_slider)
		segmentation_layout.addWidget(self.legend_widget, 2)

	def show_image(self, path: str | Path) -> None:
		"""Load and display an original image, preserving its aspect ratio."""
		pixmap = QPixmap(str(path))
		self._source_pixmap = pixmap
		if pixmap.isNull():
			self.image_label.clear_source()
			self.image_label.setText("Upload an image and run inference")
			return
		self.image_label.set_source_pixmap(pixmap)

	def show_classification_tiles(self, color_map: Image.Image, analysis: dict,
							  original: Image.Image | None = None, presentation: dict | None = None) -> None:
		"""Display a source-coordinate overlay; statistics have independent tabs."""
		if original is None:
			original = color_map
		self.tile_page.show_result(original, color_map, analysis, presentation)
		self._has_classification_result = False
		self.result_stack.setCurrentWidget(self.tile_page)

	def show_classification(
		self,
		label: str,
		confidence: float,
		probabilities: list[float],
		class_labels: list[str],
	) -> None:
		"""Display the predicted class, confidence, and probability chart."""
		self.classification_label.setText(label)
		self.confidence_label.setText(f"Confidence: {confidence * 100:.1f} %")

		chart_labels = list(class_labels)
		chart_values = [
			float(probabilities[index]) * 100
			if index < len(probabilities)
			else 0.0
			for index in range(len(chart_labels))
		]
		self._draw_classification(chart_labels, chart_values, label)

	def show_segmentation(
		self,
		overlay_pil: Image.Image,
		legend_items: list[tuple[str, tuple[int, int, int]]],
		original_pil: Image.Image | None = None,
		color_mask: Image.Image | None = None,
		counts: object | None = None,
	) -> None:
		"""Display a PIL overlay and its class color legend."""
		overlay = overlay_pil.convert("RGBA")
		self._segmentation_original = (
			original_pil.convert("RGB") if original_pil is not None else None
		)
		self._segmentation_color_mask = (
			color_mask.convert("RGB") if color_mask is not None else None
		)
		self.alpha_slider.setValue(20)
		image = QImage(
			overlay.tobytes(),
			overlay.width,
			overlay.height,
			overlay.width * 4,
			QImage.Format_RGBA8888,
		).copy()
		self.overlay_label.set_source_pixmap(QPixmap.fromImage(image))
		self._update_legend(legend_items)
		self._update_area_text(legend_items, counts)
		self._has_classification_result = False
		self.result_stack.setCurrentWidget(self.segmentation_page)

	def _update_overlay_alpha(self, value: int) -> None:
		if self._segmentation_original is None or self._segmentation_color_mask is None:
			return
		from core.large_image_segmentation import make_overlay

		overlay = make_overlay(
			self._segmentation_original,
			self._segmentation_color_mask,
			value / 100.0,
		)
		image = QImage(
			overlay.tobytes(),
			overlay.width,
			overlay.height,
			overlay.width * 3,
			QImage.Format_RGB888,
		).copy()
		self.overlay_label.set_source_pixmap(QPixmap.fromImage(image))

	def _update_area_text(
		self,
		legend_items: list[tuple[str, tuple[int, int, int]]],
		counts: object | None,
	) -> None:
		if counts is None:
			self.area_label.clear()
			return
		try:
			values = [int(value) for value in counts]
		except (TypeError, ValueError):
			self.area_label.clear()
			return
		total = sum(values)
		if total <= 0:
			self.area_label.clear()
			return
		lines = ["Predicted area percentage (full image denominator):"]
		for index, (label, _color) in enumerate(legend_items):
			count = values[index] if index < len(values) else 0
			lines.append(f"{label}: {count / total:.2%}")
		self.area_label.setText("\n".join(lines))

	def show_stored_result(
		self,
		result_image_path: str | Path,
		task_type: str,
		label: str | None,
		confidence: float | None,
	) -> None:
		"""Display a saved result image and its stored classification details."""
		self.classification_label.setText(label or "")
		self.confidence_label.setText(
			f"Confidence: {confidence * 100:.1f} %"
			if task_type == "classification" and confidence is not None
			else ""
		)
		self.result_canvas.hide()
		self.stored_result_label.show()
		self._result_figure.clear()
		self._result_figure.patch.set_facecolor("white")
		axis = self._result_figure.add_subplot(111)
		axis.set_facecolor("white")
		axis.tick_params(colors="#1A202C")
		axis.xaxis.label.set_color("#1A202C")
		axis.yaxis.label.set_color("#1A202C")
		stored_pixmap = QPixmap(str(result_image_path))
		if stored_pixmap.isNull():
			self.stored_result_label.clear_source()
			self.stored_result_label.setText("Stored result image not found")
		else:
			self.stored_result_label.set_source_pixmap(stored_pixmap)
		try:
			with Image.open(result_image_path) as stored_image:
				axis.imshow(stored_image.convert("RGB"))
		except (OSError, TypeError, ValueError):
			self.stored_result_label.clear_source()
			self.stored_result_label.setText("Stored result image not found")
			axis.text(
				0.5,
				0.5,
				"Stored result image not found",
				ha="center",
				va="center",
				transform=axis.transAxes,
			)
		axis.set_axis_off()
		self.result_canvas.draw_idle()
		self._has_classification_result = False
		self.result_stack.setCurrentWidget(self.classification_page)

	def clear(self) -> None:
		"""Clear the source image and return the result area to its empty page."""
		self._result_figure.clear()
		self.result_canvas.draw_idle()
		self._has_classification_result = False
		self.image_label.clear_source()
		self._source_pixmap = QPixmap()
		self.image_label.setText("Upload an image and run inference")
		self.tile_page.clear()
		self.classification_label.clear()
		self.confidence_label.clear()
		self._update_legend([])
		self.area_label.clear()
		self._segmentation_original = None
		self._segmentation_color_mask = None
		self.overlay_label.clear_source()
		self.stored_result_label.clear_source()
		self.stored_result_label.hide()
		self.result_canvas.show()
		self.result_stack.setCurrentWidget(self.empty_page)

	def get_result_figure(self) -> Figure | None:
		"""Return the current classification figure, if one is displayed."""
		if self._has_classification_result and self.result_stack.currentWidget() is self.classification_page:
			return self._result_figure
		return None

	def _set_initial_splitter_sizes(self) -> None:
		if self.vertical_splitter.height() <= 0:
			return
		total_height = self.vertical_splitter.height()
		self.vertical_splitter.setSizes(
			[round(total_height * 0.4), round(total_height * 0.6)]
		)

	def reset_layout(self) -> None:
		"""Restore the original image/result split and fit every image view."""
		self._set_initial_splitter_sizes()
		for image_view in (
			self.image_label,
			self.tile_image,
			self.overlay_label,
			self.stored_result_label,
		):
			image_view.fit_to_view()

	def set_splitter_theme(self, theme_name: str) -> None:
		"""Apply the selected theme to the internal image/result splitter."""
		self.vertical_splitter.setStyleSheet(splitter_style(theme_name))

	def resizeEvent(self, event: QResizeEvent) -> None:
		"""Rescale displayed images when the panel changes size."""
		super().resizeEvent(event)
		if self._has_classification_result:
			self.result_canvas.draw_idle()

	def _draw_classification(
		self,
		chart_labels: list[str],
		chart_values: list[float],
		predicted_label: str,
	) -> None:
		self._result_figure.clear()
		axis = self._result_figure.add_subplot(111)
		colors = [
			ACCENT if item == predicted_label else "#CBD5E0"
			for item in chart_labels
		]
		bars = axis.barh(chart_labels, chart_values, color=colors)
		axis.invert_yaxis()
		axis.set_xlim(0, 110)
		axis.set_xticks(range(0, 101, 20))
		axis.set_xlabel("Probability (%)")
		axis.set_axisbelow(True)
		axis.xaxis.grid(True, color="#E2E8F0", linewidth=0.7)
		axis.spines["top"].set_visible(False)
		axis.spines["right"].set_visible(False)
		axis.spines["left"].set_visible(False)
		for bar, value in zip(bars, chart_values):
			axis.text(
				min(value + 1, 104),
				bar.get_y() + bar.get_height() / 2,
				f"{value:.1f}%",
				va="center",
				fontsize=8,
			)

		self._has_classification_result = True
		self.stored_result_label.clear_source()
		self.stored_result_label.hide()
		self.result_canvas.show()
		self.result_stack.setCurrentWidget(self.classification_page)
		self.result_canvas.draw_idle()

	def _create_empty_page(self) -> QWidget:
		page = QWidget(self.result_stack)
		layout = QVBoxLayout(page)
		label = QLabel("Run inference to see results", page)
		label.setObjectName("emptyResultLabel")
		label.setAlignment(Qt.AlignCenter)
		label.setToolTip("Inference results will appear here.")
		layout.addWidget(label)
		return page

	def _update_legend(
		self,
		legend_items: list[tuple[str, tuple[int, int, int]]],
	) -> None:
		while len(self.legend_rows) < len(legend_items):
			row = QHBoxLayout()
			swatch = QLabel(self.legend_widget)
			swatch.setObjectName("legendColorSwatch")
			swatch.setFixedSize(18, 18)
			name_label = QLabel(self.legend_widget)
			row.addWidget(swatch)
			row.addWidget(name_label, 1)
			self.legend_layout.insertLayout(self.legend_layout.count() - 1, row)
			self.legend_rows.append((row, swatch, name_label))

		for index, (row, swatch, name_label) in enumerate(self.legend_rows):
			if index >= len(legend_items):
				swatch.hide()
				name_label.hide()
				continue
			name, color = legend_items[index]
			swatch.setStyleSheet(
				"background-color: rgb(" + ", ".join(str(value) for value in color) + ");"
			)
			swatch.setToolTip(f"Color for {name}.")
			name_label.setText(name)
			name_label.setToolTip(f"Segmentation class: {name}.")
			swatch.show()
			name_label.show()
