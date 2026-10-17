"""Segmentation views and pixel statistics, independent of inference."""

from PIL import Image
from PyQt5.QtCore import QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QBoxLayout, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QScrollArea, QSizePolicy, QSlider, QSplitter, QToolButton,
    QVBoxLayout, QWidget,
)

from core.large_image_segmentation import make_overlay
from ui.theme import style_panel_scroll
from ui.zoomable_image_view import ZoomableImageView


class SegmentationResult(QWidget):
    """Keep a segmentation image and its own legend visible together."""

    presentation_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("panelSurface", True)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.original = self.color_mask = self.overlay = self.analysis = None
        self._initial_opacity = .2
        self.cards = []
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.timeout.connect(self._adapt_layout)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.toolbar = QHBoxLayout()
        self.view_mode = QComboBox(self)
        for title, value in (("Overlay", "overlay"), ("Segmentation map", "segmentation_map"), ("Original image", "original")):
            self.view_mode.addItem(title, value)
        self.toolbar.addWidget(self.view_mode)
        self.compare = QCheckBox("Compare with original", self)
        self.compare.setToolTip("Show the original beside the result. Each image has independent zoom and pan controls.")
        self.toolbar.addWidget(self.compare)
        self.toolbar.addStretch()
        layout.addLayout(self.toolbar)
        alpha_row = QHBoxLayout()
        self.opacity_label = QLabel(self)
        alpha_row.addWidget(self.opacity_label)
        self.opacity = QSlider(Qt.Horizontal, self)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(20)
        alpha_row.addWidget(self.opacity, 1)
        self.details_button = QToolButton(self)
        self.details_button.setText("Details")
        self.details_button.setCheckable(True)
        alpha_row.addWidget(self.details_button)
        layout.addLayout(alpha_row)
        self.details_scroll = QScrollArea(self)
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setMinimumSize(0, 0)
        self.details_scroll.setMaximumHeight(110)
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setTextFormat(Qt.PlainText)
        self.details_scroll.setWidget(self.details)
        style_panel_scroll(self.details_scroll)
        self.details_scroll.hide()
        self.details_button.toggled.connect(self.details_scroll.setVisible)
        layout.addWidget(self.details_scroll)

        self.content = QHBoxLayout()
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)
        self.comparison_splitter = QSplitter(Qt.Horizontal, self)
        self.comparison_splitter.setHandleWidth(6)
        self.comparison_splitter.setChildrenCollapsible(False)
        self.comparison_splitter.setMinimumSize(0, 0)
        self.content.addWidget(self.comparison_splitter, 3)
        self.original_pane = QWidget()
        original_layout = QVBoxLayout(self.original_pane)
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.addWidget(QLabel("Original image", self.original_pane))
        self.original_view = ZoomableImageView(self.original_pane)
        original_layout.addWidget(self.original_view, 1)
        self.comparison_splitter.addWidget(self.original_pane)
        self.original_pane.hide()
        result_pane = QWidget()
        result_layout = QVBoxLayout(result_pane)
        result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_title = QLabel("Overlay", result_pane)
        self.result_title.hide()
        result_layout.addWidget(self.result_title)
        self.image = ZoomableImageView(result_pane)
        self.image.setObjectName("segmentationOverlayLabel")
        result_layout.addWidget(self.image, 1)
        self.comparison_splitter.addWidget(result_pane)
        for pane in (self.original_pane, result_pane):
            pane.setProperty("panelSurface", True)
            pane.setMinimumSize(0, 0)
            pane.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.legend_scroll = QScrollArea(self)
        self.legend_scroll.setWidgetResizable(True)
        self.legend_scroll.setMinimumSize(0, 0)
        self.legend_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.legend_content = QWidget()
        self.legend_content.setObjectName("segmentationLegend")
        self.legend_layout = QVBoxLayout(self.legend_content)
        self.legend_layout.setContentsMargins(4, 4, 4, 4)
        self.area_label = QLabel("Pixel coverage (full image)", self.legend_content)
        self.area_label.setWordWrap(True)
        self.area_label.setToolTip("Each class's predicted pixels divided by the full original-image pixel count. Background and excluded labels remain in the denominator.")
        self.legend_layout.addWidget(self.area_label)
        self.legend_grid = QGridLayout()
        self.legend_grid.setAlignment(Qt.AlignTop)
        self.legend_layout.addLayout(self.legend_grid)
        self.legend_layout.addStretch()
        self.legend_scroll.setWidget(self.legend_content)
        style_panel_scroll(self.legend_scroll)
        self.content.addWidget(self.legend_scroll, 1)
        self.legend_scroll.viewport().installEventFilter(self)
        self.view_mode.currentIndexChanged.connect(self._changed)
        self.opacity.valueChanged.connect(self._changed)
        self.compare.toggled.connect(self._compare_changed)

    @staticmethod
    def _pixmap(image):
        rgba = image.convert("RGBA")
        return QPixmap.fromImage(QImage(rgba.tobytes(), rgba.width, rgba.height,
                                       rgba.width * 4, QImage.Format_RGBA8888).copy())

    def show_result(self, overlay, legend_items, original=None, color_mask=None,
                    counts=None, analysis=None, presentation=None, default_opacity=.2):
        self.overlay = overlay.copy()
        self.original = original.convert("RGB") if original is not None else None
        self.color_mask = color_mask.convert("RGB") if color_mask is not None else None
        self.analysis = dict(analysis or {})
        self._initial_opacity = round(default_opacity * 100) / 100
        parameters = presentation or {}
        for control in (self.view_mode, self.opacity, self.compare):
            control.blockSignals(True)
        self.view_mode.model().item(1).setEnabled(self.color_mask is not None)
        self.view_mode.model().item(2).setEnabled(self.original is not None)
        index = self.view_mode.findData(parameters.get("view", "overlay"))
        if index < 0 or not self.view_mode.model().item(index).isEnabled():
            index = 0
        self.view_mode.setCurrentIndex(index)
        self.opacity.setValue(round(float(parameters.get("opacity", self._initial_opacity)) * 100))
        self.compare.setEnabled(self.original is not None)
        self.compare.setChecked(bool(parameters.get("compare", False)) and self.original is not None)
        for control in (self.view_mode, self.opacity, self.compare):
            control.blockSignals(False)
        self.details_button.setChecked(False)
        self.details.setText("\n".join(f"{key.replace('_', ' ').title()}: {self.analysis[key]}"
                                     for key in ("model_name", "model_path", "preprocess", "source_format", "image_size", "tile", "stride", "input_size", "device", "elapsed_seconds")
                                     if key in self.analysis) or "Stored segmentation result; inference parameters are unavailable.")
        self._update_legend(legend_items, counts)
        self.original_view.clear_source()
        if self.original is not None:
            self.original_view.set_source_pixmap(self._pixmap(self.original))
        self.image.clear_source()
        self.original_pane.setVisible(self.compare.isChecked())
        self.result_title.setVisible(self.compare.isChecked())
        self._refresh()
        self._layout_timer.start(0)

    def _update_legend(self, legend_items, counts):
        for card, *_ in self.cards:
            self.legend_grid.removeWidget(card)
            card.deleteLater()
        self.cards = []
        values = [int(value) for value in counts] if counts is not None else []
        indices = [item.get("index", i) for i, item in enumerate(self.analysis.get("classes", []))]
        width, height = (self.original or self.overlay).size
        total = width * height
        self.area_label.setText("Pixel coverage (full image)" if values else "Segmentation legend · pixel counts unavailable")
        for i, (name, color) in enumerate(legend_items):
            card = QWidget(self.legend_content)
            card.setProperty("panelSurface", True)
            row = QHBoxLayout(card)
            row.setContentsMargins(0, 0, 0, 0)
            swatch = QLabel(card)
            swatch.setFixedSize(16, 16)
            swatch.setStyleSheet(f"background-color: rgb({color[0]}, {color[1]}, {color[2]}); border: 1px solid #808080;")
            row.addWidget(swatch)
            text = QVBoxLayout()
            name_label = QLabel(name, card)
            name_label.setTextFormat(Qt.PlainText)
            name_label.setWordWrap(True)
            text.addWidget(name_label)
            class_index = indices[i] if i < len(indices) else i
            count = values[class_index] if 0 <= class_index < len(values) else 0
            stat = QLabel(f"{count / total:.2%} · {count:,} pixels" if values else "Count unavailable", card)
            stat.setWordWrap(True)
            text.addWidget(stat)
            row.addLayout(text, 1)
            card.setToolTip(f"{name} | RGB: {tuple(color)}\nFull-image denominator: {total:,} pixels (all labels included).")
            card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            self.cards.append((card, swatch, name_label, stat))
        self._adapt_layout()

    def _adapt_layout(self):
        wide = self.width() >= 900
        self.toolbar.setDirection(QBoxLayout.TopToBottom if self.width() < 520 else QBoxLayout.LeftToRight)
        self.content.setDirection(QBoxLayout.LeftToRight if wide else QBoxLayout.TopToBottom)
        self.comparison_splitter.setOrientation(Qt.Horizontal if self.width() >= 700 else Qt.Vertical)
        self.legend_scroll.setMaximumHeight(16777215 if wide else max(90, min(150, self.height() // 3)))
        self.legend_scroll.setMaximumWidth(280 if wide else 16777215)
        width = max(1, self.legend_scroll.viewport().width() - 12)
        preferred = max(180, self.fontMetrics().horizontalAdvance("Normal epithelium") + 32)
        columns = 1 if wide else max(1, min(3, width // preferred))
        while self.legend_grid.count():
            self.legend_grid.takeAt(0)
        for i, (card, *_) in enumerate(self.cards):
            self.legend_grid.addWidget(card, i // columns, i % columns)
        self.legend_grid.activate()

    def presentation(self):
        return {"view": self.view_mode.currentData(), "opacity": self.opacity.value() / 100,
                "compare": self.compare.isChecked()}

    def render_image(self):
        mode = self.view_mode.currentData()
        if mode == "original" and self.original is not None:
            return self.original.copy()
        if mode == "segmentation_map" and self.color_mask is not None:
            return self.color_mask.copy()
        if self.original is None or self.color_mask is None or self.opacity.value() == round(self._initial_opacity * 100):
            return self.overlay.copy()
        return make_overlay(self.original, self.color_mask, self.opacity.value() / 100)

    def _refresh(self):
        self.opacity_label.setText(f"Opacity: {self.opacity.value()}%")
        self.opacity.setEnabled(self.view_mode.currentData() == "overlay" and self.original is not None and self.color_mask is not None)
        self.result_title.setText(self.view_mode.currentText())
        if self.overlay is not None:
            self.image.update_source_pixmap(self._pixmap(self.render_image()))

    def _changed(self):
        self._refresh()
        if self.analysis is not None:
            self.presentation_changed.emit()

    def _compare_changed(self):
        self.original_pane.setVisible(self.compare.isChecked())
        self.result_title.setVisible(self.compare.isChecked())
        self._layout_timer.start(0)
        if self.analysis is not None:
            self.presentation_changed.emit()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Resize:
            self._layout_timer.start(0)
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_timer.start(0)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange) and hasattr(self, "_layout_timer"):
            self._layout_timer.start(0)

    def clear(self):
        self.original = self.color_mask = self.overlay = self.analysis = None
        self.image.clear_source()
        self.original_view.clear_source()
        self.compare.setChecked(False)
        self.original_pane.hide()
        self.details_button.setChecked(False)
        for card, *_ in self.cards:
            card.hide()
        self.area_label.clear()
        self.details.clear()
