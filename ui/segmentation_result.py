"""Segmentation views and pixel statistics, independent of inference."""

from PyQt5.QtCore import QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QBoxLayout, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QScrollArea, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget,
)

from ui.language import tr
from ui.theme import style_panel_scroll
from ui.image_comparison import ImageComparison


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
        self.comparison = ImageComparison(self)
        self.compare = self.comparison.compare
        self.link_views = self.comparison.link_views
        self.comparison_splitter = self.comparison.splitter
        self.original_pane = self.comparison.original_pane
        self.original_view = self.comparison.original_view
        self.result_title = self.comparison.result_title
        self.image = self.comparison.image
        self.image.setObjectName("segmentationOverlayLabel")
        self.view_mode = self.comparison.view_mode
        for title, value in (("Overlay", "overlay"), ("Segmentation map", "segmentation_map"), ("Original image", "original")):
            self.view_mode.addItem(tr(title), value)
        self.opacity_label = self.comparison.opacity_label
        self.opacity = self.comparison.opacity
        self.opacity.setValue(20)
        self.details_button = QToolButton(self)
        self.details_button.setText(tr("Run parameters"))
        self.details_button.setCheckable(True)
        self.details_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.details_button.setArrowType(Qt.RightArrow)
        layout.addWidget(self.details_button, alignment=Qt.AlignRight)
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
        self.details_button.toggled.connect(lambda expanded: self.details_button.setArrowType(
            Qt.DownArrow if expanded else Qt.RightArrow))
        layout.addWidget(self.details_scroll)

        self.content = QHBoxLayout()
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)
        self.content.addWidget(self.comparison, 3)
        self.legend_scroll = QScrollArea(self)
        self.legend_scroll.setWidgetResizable(True)
        self.legend_scroll.setMinimumSize(0, 0)
        self.legend_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.legend_content = QWidget()
        self.legend_content.setObjectName("segmentationLegend")
        self.legend_layout = QVBoxLayout(self.legend_content)
        self.legend_layout.setContentsMargins(4, 4, 4, 4)
        self.area_label = QLabel(tr("Pixel coverage (full image)"), self.legend_content)
        self.area_label.setWordWrap(True)
        self.area_label.setToolTip(tr("Each class's predicted pixels divided by the full original-image pixel count. Background and excluded labels remain in the denominator."))
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
        self.comparison.presentation_changed.connect(self._presentation_changed)

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
        from core.spatial_sampling import scale_description
        detail_lines = [f"{tr(key.replace('_', ' ').title())}: {self.analysis[key]}"
                        for key in ("model_name", "model_path", "preprocess", "source_format", "image_size", "tile", "stride", "input_size", "device", "elapsed_seconds")
                        if key in self.analysis]
        if self.analysis.get("spatial_context"):
            detail_lines.append(scale_description(self.analysis["spatial_context"], tr))
        if self.analysis.get("input_profile") and not (self.analysis.get("spatial_context") or {}).get("nominal_model_field_um"):
            field = self.analysis["input_profile"].get("field_um")
            detail_lines.append(f"{tr('Model tissue field (um)')}: {field}" if field else tr("Model physical field: not established."))
        self.details.setText("\n".join(detail_lines) or tr("Stored segmentation result; inference parameters are unavailable."))
        self._update_legend(legend_items, counts)
        self.comparison.set_images(self._pixmap(self.original) if self.original is not None else QPixmap(),
                                   self._pixmap(self.render_image()), parameters)
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
        self.area_label.setText(tr("Pixel coverage (full image)") if values else tr("Segmentation legend · pixel counts unavailable"))
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
            stat = QLabel(f"{count / total:.2%} · {count:,} pixels" if values else tr("Count unavailable"), card)
            stat.setWordWrap(True)
            text.addWidget(stat)
            row.addLayout(text, 1)
            card.setToolTip(f"{name} | RGB: {tuple(color)}\nFull-image denominator: {total:,} pixels (all labels included).")
            card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            self.cards.append((card, swatch, name_label, stat))
        self._adapt_layout()

    def _adapt_layout(self):
        wide = self.width() >= 900
        self.content.setDirection(QBoxLayout.LeftToRight if wide else QBoxLayout.TopToBottom)
        cap = max(90, min(150, self.height() // 3))
        self.legend_scroll.setMaximumHeight(16777215 if wide else cap)
        # Reserve enough width for horizontal comparison even with a side legend.
        side_width = self.width() - self.comparison.SIDE_BY_SIDE_WIDTH - self.content.spacing()
        self.legend_scroll.setMaximumWidth(min(280, side_width) if wide else 16777215)
        width = max(1, self.legend_scroll.viewport().width() - 12)
        preferred = max(180, self.fontMetrics().horizontalAdvance("Normal epithelium") + 32)
        columns = 1 if wide else max(1, min(3, width // preferred))
        while self.legend_grid.count():
            self.legend_grid.takeAt(0)
        for i, (card, *_) in enumerate(self.cards):
            self.legend_grid.addWidget(card, i // columns, i % columns)
        self.legend_grid.activate()
        # A complete legend card must fit in the viewport at the current font
        # size. A fixed fraction of the page can be smaller than a wrapped card.
        cell_width = max(1, (width - self.legend_grid.horizontalSpacing() * (columns - 1)) // columns)
        card_height = max((max(card.layout().heightForWidth(cell_width), card.minimumSizeHint().height())
                           for card, *_ in self.cards), default=0)
        minimum = card_height + 2 * self.legend_scroll.frameWidth()
        self.legend_scroll.setMinimumHeight(minimum)
        if not wide:
            self.legend_scroll.setMaximumHeight(max(cap, minimum))

    def presentation(self):
        return {"view": self.view_mode.currentData(), "opacity": self.opacity.value() / 100,
                **self.comparison.presentation()}

    def render_image(self):
        from ui.result_rendering import presentation_snapshot, render_snapshot
        return render_snapshot(presentation_snapshot(self, 'segmentation', copy_metadata=False))

    def _refresh(self):
        self.opacity_label.setText(tr("Opacity: {percent}%").format(percent=self.opacity.value()))
        self.view_mode.setToolTip(self.view_mode.currentText())
        self.opacity.setEnabled(self.view_mode.currentData() == "overlay" and self.original is not None and self.color_mask is not None)
        self.result_title.setText(self.view_mode.currentText())
        if self.overlay is not None:
            self.image.update_source_pixmap(self._pixmap(self.render_image()))

    def _changed(self):
        self._refresh()
        if self.analysis is not None:
            self.presentation_changed.emit()

    def _presentation_changed(self):
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
        self.comparison.clear()
        self.details_button.setChecked(False)
        for card, *_ in self.cards:
            card.hide()
        self.area_label.clear()
        self.details.clear()
