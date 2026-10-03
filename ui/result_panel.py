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
	QScrollArea,
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
		self._result_figure: Figure | None = None

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
		layout.addWidget(self.result_stack, 3)

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
		self._clear_page(self.classification_page)
		page_layout = QVBoxLayout(self.classification_page)
		page_layout.setContentsMargins(8, 8, 8, 8)
		page_layout.setSpacing(8)

		label_widget = QLabel(label, self.classification_page)
		label_widget.setObjectName("predictedClassLabel")
		label_widget.setToolTip("Predicted class label.")
		page_layout.addWidget(label_widget)

		confidence_widget = QLabel(
			f"Confidence: {confidence * 100:.1f} %", self.classification_page
		)
		confidence_widget.setObjectName("confidenceLabel")
		confidence_widget.setToolTip("Confidence score for the predicted class.")
		page_layout.addWidget(confidence_widget)

		chart_labels = list(class_labels)
		chart_values = [
			float(probabilities[index]) * 100
			if index < len(probabilities)
			else 0.0
			for index in range(len(chart_labels))
		]
		figure_height = max(2.5, min(5.5, 0.38 * len(chart_labels) + 0.9))
		figure = Figure(figsize=(6.2, figure_height), tight_layout=True)
		axis = figure.add_subplot(111)
		colors = [ACCENT if item == label else "#CBD5E0" for item in chart_labels]
		bars = axis.barh(chart_labels, chart_values, color=colors)
		axis.invert_yaxis()
		axis.set_xlim(0, 110)
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

		canvas = FigureCanvasQTAgg(figure)
		canvas.setMinimumHeight(int(figure_height * figure.dpi))
		canvas.setToolTip("Class probability chart.")
		scroll_area = QScrollArea(self.classification_page)
		scroll_area.setWidgetResizable(True)
		scroll_area.setFrameShape(QScrollArea.NoFrame)
		scroll_area.setWidget(canvas)
		page_layout.addWidget(scroll_area, 1)
		self._result_figure = figure
		self.result_stack.setCurrentWidget(self.classification_page)

	def show_segmentation(
		self,
		overlay_pil: Image.Image,
		legend_items: list[tuple[str, tuple[int, int, int]]],
	) -> None:
		"""Display a PIL overlay and its class color legend."""
		self._clear_page(self.segmentation_page)
		page_layout = QHBoxLayout(self.segmentation_page)
		page_layout.setContentsMargins(8, 8, 8, 8)
		page_layout.setSpacing(16)

		overlay = overlay_pil.convert("RGBA")
		image = QImage(
			overlay.tobytes(),
			overlay.width,
			overlay.height,
			overlay.width * 4,
			QImage.Format_RGBA8888,
		).copy()
		self._overlay_pixmap = QPixmap.fromImage(image)
		self.overlay_label = QLabel(self.segmentation_page)
		self.overlay_label.setObjectName("segmentationOverlayLabel")
		self.overlay_label.setAlignment(Qt.AlignCenter)
		self.overlay_label.setMinimumSize(120, 120)
		self.overlay_label.setToolTip("Segmentation overlay image.")
		page_layout.addWidget(self.overlay_label, 3)

		legend_widget = QWidget(self.segmentation_page)
		legend_widget.setObjectName("segmentationLegend")
		legend_layout = QVBoxLayout(legend_widget)
		legend_layout.setContentsMargins(0, 4, 0, 4)
		legend_layout.setSpacing(8)
		for name, color in legend_items:
			row = QHBoxLayout()
			swatch = QLabel(legend_widget)
			swatch.setObjectName("legendColorSwatch")
			swatch.setFixedSize(18, 18)
			swatch.setStyleSheet(
				"background-color: rgb(" + ", ".join(str(value) for value in color) + ");"
			)
			swatch.setToolTip(f"Color for {name}.")
			name_label = QLabel(name, legend_widget)
			name_label.setToolTip(f"Segmentation class: {name}.")
			row.addWidget(swatch)
			row.addWidget(name_label, 1)
			legend_layout.addLayout(row)
		legend_layout.addStretch()
		page_layout.addWidget(legend_widget, 2)
		self._refresh_overlay()
		self.result_stack.setCurrentWidget(self.segmentation_page)

	def clear(self) -> None:
		"""Clear the source image and return the result area to its empty page."""
		self._source_pixmap = QPixmap()
		self._overlay_pixmap = QPixmap()
		self.image_label.setPixmap(QPixmap())
		self.image_label.setText("Upload an image and run inference")
		self._clear_page(self.classification_page)
		self._clear_page(self.segmentation_page)
		self._result_figure = None
		self.result_stack.setCurrentWidget(self.empty_page)

	def get_result_figure(self) -> Figure | None:
		"""Return the current classification figure, if one is displayed."""
		if self.result_stack.currentWidget() is self.classification_page:
			return self._result_figure
		return None

	def resizeEvent(self, event: QResizeEvent) -> None:
		"""Rescale displayed images when the panel changes size."""
		super().resizeEvent(event)
		self._refresh_image()
		self._refresh_overlay()

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
		if self._overlay_pixmap.isNull() or not hasattr(self, "overlay_label"):
			return
		self.overlay_label.setPixmap(
			self._overlay_pixmap.scaled(
				self.overlay_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
			)
		)

	def _clear_page(self, page: QWidget) -> None:
		layout = page.layout()
		if layout is None:
			return
		while layout.count():
			item = layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()
			elif item.layout() is not None:
				self._clear_layout(item.layout())
		if page is self.classification_page:
			self._result_figure = None

	def _clear_layout(self, layout: QVBoxLayout | QHBoxLayout) -> None:
		while layout.count():
			item = layout.takeAt(0)
			if item.widget() is not None:
				item.widget().deleteLater()
			elif item.layout() is not None:
				self._clear_layout(item.layout())
