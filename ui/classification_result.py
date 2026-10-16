"""Classification overlay controls with image space independent from long tables."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QLabel, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
)
from core.classification_tiles import render_classification_map
from ui.zoomable_image_view import ZoomableImageView


class ClassificationResult(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original = self.color_map = self.analysis = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.summary = QLabel(self)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        layout.addWidget(self.summary)
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs, 1)
        image_page = QWidget(self.tabs)
        image_layout = QVBoxLayout(image_page)
        toolbar = QHBoxLayout()
        self.view_mode = QComboBox(image_page)
        self.view_mode.addItems(["Overlay", "Class color map"])
        toolbar.addWidget(self.view_mode)
        self.boundaries = QCheckBox("Tile boundaries", image_page)
        toolbar.addWidget(self.boundaries)
        toolbar.addStretch()
        image_layout.addLayout(toolbar)
        alpha_row = QHBoxLayout()
        self.opacity_label = QLabel("Overlay opacity: 40%", image_page)
        alpha_row.addWidget(self.opacity_label)
        self.opacity = QSlider(Qt.Horizontal, image_page)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(40)
        alpha_row.addWidget(self.opacity, 1)
        image_layout.addLayout(alpha_row)
        self.image = ZoomableImageView(image_page)
        image_layout.addWidget(self.image, 1)
        self.tabs.addTab(image_page, "Image")
        self.legend = QTableWidget(0, 4, self.tabs)
        self.legend.setHorizontalHeaderLabels(["Class", "Tiles", "Estimated coverage", "Color (RGB)"])
        self.legend.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.legend.horizontalHeader().setStretchLastSection(True)
        self.legend.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabs.addTab(self.legend, "Legend and statistics")
        self.table = QTableWidget(0, 3, self.tabs)
        self.table.setHorizontalHeaderLabels(["Tile (x0, y0, x1, y1)", "Class", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabs.addTab(self.table, "Tiles")
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
        self._refresh()

    def presentation(self):
        return {"view": "color_map" if self.view_mode.currentIndex() else "overlay",
                "opacity": self.opacity.value() / 100, "boundaries": self.boundaries.isChecked()}

    def render_image(self):
        p = self.presentation()
        return render_classification_map(self.original, self.color_map, self.analysis,
                                         p["opacity"], p["view"] == "color_map", p["boundaries"])

    def _refresh(self):
        self.opacity_label.setText(f"Overlay opacity: {self.opacity.value()}%")
        self.opacity.setEnabled(self.view_mode.currentIndex() == 0)
        if self.analysis is None:
            return
        image = self.render_image()
        qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format_RGB888).copy()
        self.image.update_source_pixmap(QPixmap.fromImage(qimage))

    def clear(self):
        self.original = self.color_map = self.analysis = None
        self.image.clear_source()
        self.legend.setRowCount(0)
        self.table.setRowCount(0)
        self.summary.clear()
