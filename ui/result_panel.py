"""Display original images and inference results."""

from pathlib import Path

from PIL import Image
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (
	QHBoxLayout,
	QLabel,
	QSizePolicy,
	QStackedWidget,
	QVBoxLayout,
	QWidget,
)

from ui.theme import ACCENT


class ResultPanel(QWidget):
	"""Show the source image and classification or segmentation results."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("ResultPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._source_pixmap = QPixmap()
		self._overlay_pixmap = QPixmap()
		self._result_figure = Figure(figsize=(6.2, 4.0), constrained_layout=True)
		self._has_classification_result = False

		layout = QVBoxLayout(self)
		layout.setContentsMargins(16, 16, 16, 16)
		layout.setSpacing(12)

		self.image_label = QLabel("Upload an image and run inference", self)
		self.image_label.setObjectName("sourceImageLabel")
		self.image_label.setAlignment(Qt.AlignCenter)
		self.image_label.setMinimumHeight(180)
		self.image_label.setToolTip("Preview of the original image.")
		layout.addWidget(self.image_label, 2)

		self.result_stack = QStackedWidget(self)
		self.result_stack.setObjectName("resultStack")
		self.empty_page = self._create_empty_page()
		self.classification_page = QWidget(self.result_stack)
		self.segmentation_page = QWidget(self.result_stack)
		self.result_stack.addWidget(self.empty_page)
		self.result_stack.addWidget(self.classification_page)
		self.result_stack.addWidget(self.segmentation_page)
		self.result_stack.setMinimumHeight(260)
		layout.addWidget(self.result_stack, 3)

		classification_layout = QVBoxLayout(self.classification_page)
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
		self.result_canvas = FigureCanvasQTAgg(self._result_figure)
		self.result_canvas.setMinimumSize(300, 150)
		self.result_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.result_canvas.setToolTip("Class probability chart.")
		classification_layout.addWidget(self.result_canvas, 1)

		segmentation_layout = QHBoxLayout(self.segmentation_page)
		segmentation_layout.setContentsMargins(8, 8, 8, 8)
		segmentation_layout.setSpacing(16)
		self.overlay_label = QLabel(self.segmentation_page)
		self.overlay_label.setObjectName("segmentationOverlayLabel")
		self.overlay_label.setAlignment(Qt.AlignCenter)
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
		segmentation_layout.addWidget(self.legend_widget, 2)

	def show_image(self, path: str | Path) -> None:
		"""Load and display an original image, preserving its aspect ratio."""
		self._source_pixmap = QPixmap(str(path))
		if self._source_pixmap.isNull():
			self.image_label.setText("Upload an image and run inference")
			self.image_label.setPixmap(QPixmap())
			return
		self._refresh_image()

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
	) -> None:
		"""Display a PIL overlay and its class color legend."""
		overlay = overlay_pil.convert("RGBA")
		image = QImage(
			overlay.tobytes(),
			overlay.width,
			overlay.height,
			overlay.width * 4,
			QImage.Format_RGBA8888,
		).copy()
		self._overlay_pixmap = QPixmap.fromImage(image)
		self._update_legend(legend_items)
		self._refresh_overlay()
		self._has_classification_result = False
		self.result_stack.setCurrentWidget(self.segmentation_page)

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
		self._result_figure.clear()
		axis = self._result_figure.add_subplot(111)
		try:
			with Image.open(result_image_path) as stored_image:
				axis.imshow(stored_image.convert("RGB"))
		except (OSError, TypeError, ValueError):
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
		self._source_pixmap = QPixmap()
		self._overlay_pixmap = QPixmap()
		self._result_figure.clear()
		self.result_canvas.draw_idle()
		self._has_classification_result = False
		self.image_label.setPixmap(QPixmap())
		self.image_label.setText("Upload an image and run inference")
		self.classification_label.clear()
		self.confidence_label.clear()
		self._update_legend([])
		self.overlay_label.setPixmap(QPixmap())
		self.result_stack.setCurrentWidget(self.empty_page)

	def get_result_figure(self) -> Figure | None:
		"""Return the current classification figure, if one is displayed."""
		if self._has_classification_result and self.result_stack.currentWidget() is self.classification_page:
			return self._result_figure
		return None

	def resizeEvent(self, event: QResizeEvent) -> None:
		"""Rescale displayed images when the panel changes size."""
		super().resizeEvent(event)
		self._refresh_image()
		self._refresh_overlay()
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

	def _refresh_image(self) -> None:
		if self._source_pixmap.isNull():
			return
		self.image_label.setText("")
		self.image_label.setPixmap(
			self._source_pixmap.scaled(
				self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
			)
		)

	def _refresh_overlay(self) -> None:
		if self._overlay_pixmap.isNull():
			return
		self.overlay_label.setPixmap(
			self._overlay_pixmap.scaled(
				self.overlay_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
			)
		)

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
