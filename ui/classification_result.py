"""Classification overlay controls with image space independent from long tables."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QLabel, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QScrollArea, QToolButton, QBoxLayout, QLayout,
)
from core.classification_tiles import render_classification_map
from ui.zoomable_image_view import ZoomableImageView
from ui.display_table import DisplayTable
from ui.theme import style_panel_scroll


class ClassificationResult(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("panelSurface", True)
        self.original = self.color_map = self.analysis = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        header = QHBoxLayout()
        self.caption = QLabel(self)
        self.caption.setWordWrap(True)
        self.caption.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        header.addWidget(self.caption, 1)
        self.details_button = QToolButton(self)
        self.details_button.setText("Details")
        self.details_button.setCheckable(True)
        header.addWidget(self.details_button)
        layout.addLayout(header)
        self.details_scroll = QScrollArea(self)
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setMaximumHeight(110)
        self.details_scroll.setMinimumSize(0, 0)
        self.summary = QLabel(self)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.details_scroll.setWidget(self.summary)
        style_panel_scroll(self.details_scroll)
        self.details_scroll.hide()
        self.details_button.toggled.connect(self.details_scroll.setVisible)
        layout.addWidget(self.details_scroll)
        self.tabs = QTabWidget(self)
        self.tabs.setMinimumSize(0, 0)
        self.tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.tabs.setUsesScrollButtons(True)
        layout.addWidget(self.tabs, 1)
        image_page = QWidget(self.tabs)
        image_page.setProperty("panelSurface", True)
        image_layout = QVBoxLayout(image_page)
        toolbar = QHBoxLayout()
        self.toolbar = toolbar
        self.view_mode = QComboBox(image_page)
        self.view_mode.addItems(["Overlay", "Class color map"])
        toolbar.addWidget(self.view_mode)
        self.boundaries = QCheckBox("Tile boundaries", image_page)
        toolbar.addWidget(self.boundaries)
        toolbar.addStretch()
        image_layout.addLayout(toolbar)
        alpha_row = QHBoxLayout()
        self.opacity_label = QLabel("Opacity: 40%", image_page)
        alpha_row.addWidget(self.opacity_label)
        self.opacity = QSlider(Qt.Horizontal, image_page)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(40)
        alpha_row.addWidget(self.opacity, 1)
        image_layout.addLayout(alpha_row)
        self.image = ZoomableImageView(image_page)
        image_layout.addWidget(self.image, 1)
        self.tabs.addTab(image_page, "Image")
        self.legend = DisplayTable(0, 4, self.tabs)
        self.legend.setObjectName("classificationLegendTable")
        self.legend.setHorizontalHeaderLabels(["Class", "Tiles", "Estimated coverage", "Color (RGB)"])
        self.legend.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.legend.horizontalHeader().setStretchLastSection(True)
        self.legend.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabs.addTab(self.legend, "Legend and statistics")
        self.table = DisplayTable(0, 3, self.tabs)
        self.table.setObjectName("classificationTileTable")
        self.table.setHorizontalHeaderLabels(["Tile (x0, y0, x1, y1)", "Class", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabs.addTab(self.table, "Tiles")
        self.tabs.currentChanged.connect(self._clear_table_states)
        self.view_mode.currentIndexChanged.connect(self._refresh)
        self.boundaries.toggled.connect(self._refresh)
        self.opacity.valueChanged.connect(self._refresh)

    def show_result(self, original, color_map, analysis, presentation=None):
        self.image.clear_source()
        self.original = original.convert("RGB").copy()
        self.color_map = color_map.convert("RGB").copy()
        self.analysis = analysis
        # Verify dimensions before displaying a potentially misleading map.
        render_classification_map(self.original, self.color_map, analysis)
        parameters = presentation or {}
        controls = (self.view_mode, self.opacity, self.boundaries)
        for control in controls:
            control.blockSignals(True)
        self.view_mode.setCurrentIndex(int(parameters.get("view") == "color_map"))
        self.opacity.setValue(round(float(parameters.get("opacity", .4)) * 100))
        self.boundaries.setChecked(bool(parameters.get("boundaries", False)))
        for control in controls:
            control.blockSignals(False)
        width, height = analysis["tile_size"]
        self.caption.setText(f"Tiled analysis | {len(analysis['tiles'])} tiles | {width} x {height} px")
        self.caption.setToolTip("Training scale unconfirmed. Estimated coverage uses tile classes.")
        self.summary.setText(
            f"Tiled analysis | Original tiles: {width} x {height} px | "
            f"Input: {analysis['input_size']} | {analysis['preprocess']} | "
            f"Resize: {analysis.get('resize_backend', 'pillow_bilinear')}\n"
            "Training scale unconfirmed. Coverage is estimated from tile classes, not pixel segmentation.")
        self.legend.setRowCount(len(analysis["classes"]))
        for i, item in enumerate(analysis["classes"]):
            values = (item["label"], str(analysis["tile_counts"][i]),
                      f"{analysis['area_ratios'][i]:.2%}", str(tuple(item["color"])))
            for column, text in enumerate(values):
                cell = QTableWidgetItem(text)
                if column == 3:
                    color = QColor(*item["color"])
                    cell.setBackground(color)
                    cell.setForeground(QColor("black" if color.lightness() > 130 else "white"))
                self.legend.setItem(i, column, cell)
        self.table.setRowCount(len(analysis["tiles"]))
        for row, tile in enumerate(analysis["tiles"]):
            for column, text in enumerate((str(tile["box"]), tile["label"], f"{tile['confidence']:.2%}")):
                self.table.setItem(row, column, QTableWidgetItem(text))
        self.tabs.setCurrentIndex(0)
        self._clear_table_states()
        self._refresh()

    def _clear_table_states(self, *unused):
        self.legend.clear_display_state()
        self.table.clear_display_state()

    def presentation(self):
        return {"view": "color_map" if self.view_mode.currentIndex() else "overlay",
                "opacity": self.opacity.value() / 100, "boundaries": self.boundaries.isChecked()}

    def render_image(self, include_boundaries=True):
        p = self.presentation()
        return render_classification_map(self.original, self.color_map, self.analysis,
                                         p["opacity"], p["view"] == "color_map", p["boundaries"] and include_boundaries)

    def _refresh(self):
        self.opacity_label.setText(f"Opacity: {self.opacity.value()}%")
        self.opacity.setEnabled(self.view_mode.currentIndex() == 0)
        if self.analysis is None:
            return
        # Display boundaries are vector foreground lines, not downsampled image pixels.
        image = self.render_image(include_boundaries=False)
        qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format_RGB888).copy()
        self.image.update_source_pixmap(QPixmap.fromImage(qimage))
        self.image.set_tile_grid([tile["box"] for tile in self.analysis["tiles"]] if self.boundaries.isChecked() else [])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toolbar.setDirection(QBoxLayout.TopToBottom if self.width() < 380 else QBoxLayout.LeftToRight)

    def clear(self):
        self._clear_table_states()
        self.original = self.color_map = self.analysis = None
        self.image.clear_source()
        self.legend.setRowCount(0)
        self.table.setRowCount(0)
        self.summary.clear()
        self.caption.clear()
