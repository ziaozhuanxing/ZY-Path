"""Persistent classification image and summary with optional detailed tables."""
from bisect import bisect_right

from PyQt5.QtCore import QEvent, QTimer, QSignalBlocker, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QImage, QPainter, QTransform
from PIL import Image
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QScrollArea, QToolButton, QLayout,
    QGridLayout, QSplitter, QToolTip, QStyle,
)
from core.classification_tiles import render_classification_map
from ui.image_comparison import ImageComparison
from ui.result_check_box import ResultCheckBox
from ui.display_table import DisplayTable
from ui.theme import style_panel_scroll
from ui.tile_annotations import draw_tile_numbers


class ClassificationResult(QWidget):
    presentation_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("panelSurface", True)
        self.original = self.color_map = self.analysis = None
        self._tile_rows = {}
        self._row_starts = []
        self._column_starts = {}
        self._hover_tooltip_active = False
        self.selected_tile_index = None
        self._legend_layout_timer = QTimer(self)
        self._legend_layout_timer.setSingleShot(True)
        self._legend_layout_timer.timeout.connect(self._layout_class_summary)
        self._inspection_scroll_timer = QTimer(self)
        self._inspection_scroll_timer.setSingleShot(True)
        self._inspection_scroll_timer.timeout.connect(self._scroll_inspected_tile)
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
        self.details_button.setText("Parameters")
        self.details_button.setCheckable(True)
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
        self.content_splitter = QSplitter(Qt.Vertical, self)
        self.content_splitter.setMinimumSize(0, 0)
        self.content_splitter.setChildrenCollapsible(False)
        self.content_splitter.setHandleWidth(6)
        layout.addWidget(self.content_splitter, 1)
        # Let controls and the legend scroll on short, large-font pages instead
        # of squeezing the image navigation below a complete button's height.
        self.image_page_scroll = QScrollArea(self.content_splitter)
        self.image_page_scroll.setWidgetResizable(True)
        self.image_page_scroll.setMinimumSize(0, 0)
        style_panel_scroll(self.image_page_scroll)
        image_page = QWidget()
        image_page.setProperty("panelSurface", True)
        image_page.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        image_layout = QVBoxLayout(image_page)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(3)
        image_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.image_page_scroll.setWidget(image_page)
        self.content_splitter.addWidget(self.image_page_scroll)
        self.tabs = QTabWidget(self.content_splitter)
        self.tabs.setMinimumSize(0, 0)
        self.tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.tabs.setMinimumHeight(110)
        self.tabs.setUsesScrollButtons(True)
        self.content_splitter.addWidget(self.tabs)
        self.content_splitter.setStretchFactor(0, 3)
        self.content_splitter.setStretchFactor(1, 1)
        self.comparison = ImageComparison(image_page)
        self.compare = self.comparison.compare
        self.link_views = self.comparison.link_views
        self.original_view = self.comparison.original_view
        self.original_pane = self.comparison.original_pane
        self.comparison_splitter = self.comparison.splitter
        toolbar = self.comparison.primary_layout
        self.toolbar = toolbar
        self.view_mode = QComboBox(image_page)
        self.view_mode.setMinimumContentsLength(8)
        self.view_mode.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        for title, value in (("Overlay", "overlay"), ("Class color map", "color_map"), ("Original image", "original")):
            self.view_mode.addItem(title, value)
        toolbar.addWidget(self.view_mode)
        self.boundaries = ResultCheckBox("Tile boundaries", image_page)
        self.boundaries.setToolTip("Show boundaries between the actual source-image tiles.")
        toolbar.addWidget(self.boundaries)
        self.tile_numbers = ResultCheckBox("Tile numbers", image_page)
        self.tile_numbers.setToolTip("Number crops from 1 in the recorded Tile details order, left to right then top to bottom.")
        toolbar.addWidget(self.tile_numbers)
        alpha_row = QHBoxLayout()
        self.opacity_label = QLabel("Opacity: 40%", image_page)
        alpha_row.addWidget(self.opacity_label)
        self.opacity = QSlider(Qt.Horizontal, image_page)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(40)
        alpha_row.addWidget(self.opacity, 1)
        alpha_row.addWidget(self.details_button)
        self.comparison.add_controls_layout(alpha_row)
        self.image = self.comparison.image
        image_layout.addWidget(self.comparison, 1)
        for view in (self.image, self.original_view):
            view.graphics_view.viewport().installEventFilter(self)
            view.graphics_view.setMouseTracking(True)
            view.view_changed.connect(self._hide_tile_tooltip)
            view.source_clicked.connect(self._inspect_at_source)
        self.tile_inspector = QWidget(image_page)
        inspector_layout = QHBoxLayout(self.tile_inspector)
        inspector_layout.setContentsMargins(4, 4, 4, 4)
        self.tile_preview = QLabel(self.tile_inspector)
        self.tile_preview.setFixedSize(80, 80)
        self.tile_preview.setAlignment(Qt.AlignCenter)
        inspector_layout.addWidget(self.tile_preview)
        self.tile_inspection_text = QLabel(self.tile_inspector)
        self.tile_inspection_text.setWordWrap(True)
        self.tile_inspection_text.setTextFormat(Qt.PlainText)
        self.tile_inspection_text.setMinimumWidth(0)
        self.tile_inspection_text.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.inspection_scroll = QScrollArea(self.tile_inspector)
        self.inspection_scroll.setWidgetResizable(True)
        self.inspection_scroll.setMinimumWidth(0)
        self.inspection_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.inspection_scroll.setWidget(self.tile_inspection_text)
        style_panel_scroll(self.inspection_scroll)
        inspector_layout.addWidget(self.inspection_scroll, 1)
        actions = QVBoxLayout()
        for name, text, callback in (
            ("previous_tile_button", "Previous", lambda: self.inspect_tile(max(0, self.selected_tile_index - 1), True)),
            ("next_tile_button", "Next", lambda: self.inspect_tile(min(len(self.analysis["tiles"]) - 1, self.selected_tile_index + 1), True)),
            ("clear_tile_button", "Clear", self.clear_tile_inspection),
        ):
            button = QToolButton(self.tile_inspector)
            button.setText(text if name == "clear_tile_button" else "")
            if name != "clear_tile_button":
                button.setArrowType(Qt.LeftArrow if name == "previous_tile_button" else Qt.RightArrow)
            button.setToolTip(text + " tile" if name != "clear_tile_button" else "Clear tile inspection")
            button.setAccessibleName(text + " tile" if name != "clear_tile_button" else "Clear tile inspection")
            button.clicked.connect(callback)
            setattr(self, name, button)
            actions.addWidget(button)
        inspector_layout.addLayout(actions)
        self.tile_inspector.hide()
        image_layout.addWidget(self.tile_inspector)
        summary_title = QLabel("Estimated coverage", image_page)
        summary_title.setWordWrap(True)
        summary_title.setToolTip("Coverage is estimated from tile classes and actual crop areas, not pixel segmentation.")
        summary_header = QHBoxLayout()
        summary_header.addWidget(summary_title, 1)
        image_layout.addLayout(summary_header)
        self.legend_scroll = QScrollArea(image_page)
        self.legend_scroll.setWidgetResizable(True)
        self.legend_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.legend_content = QWidget()
        self.legend_grid = QGridLayout(self.legend_content)
        self.legend_grid.setContentsMargins(2, 2, 2, 2)
        self.legend_grid.setHorizontalSpacing(10)
        self.legend_grid.setVerticalSpacing(6)
        self.legend_grid.setSizeConstraint(QLayout.SetNoConstraint)
        self.legend_grid.setAlignment(Qt.AlignTop)
        self.legend_scroll.setWidget(self.legend_content)
        style_panel_scroll(self.legend_scroll)
        self.class_cards, self.class_swatches, self.class_labels = [], [], []
        self.legend_columns = 1
        self.legend_scroll.viewport().installEventFilter(self)
        image_layout.addWidget(self.legend_scroll)
        self.tile_details_button = QToolButton(self)
        self.tile_details_button.setText("Tile details")
        self.tile_details_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tile_details_button.setCheckable(True)
        self.tile_details_button.setArrowType(Qt.RightArrow)
        self.tile_details_button.toggled.connect(self._toggle_tile_details)
        header.addWidget(self.tile_details_button)
        self.legend = DisplayTable(0, 4, self.tabs)
        self.legend.setObjectName("classificationLegendTable")
        self.legend.setHorizontalHeaderLabels(["Class", "Tiles", "Estimated coverage", "Color (RGB)"])
        self.legend.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.legend.horizontalHeader().setStretchLastSection(True)
        self.legend.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table = DisplayTable(0, 4, self.tabs)
        self.table.setObjectName("classificationTileTable")
        self.table.setHorizontalHeaderLabels(["Tile #", "Tile (x0, y0, x1, y1)", "Class", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(lambda row, column: self.inspect_tile(row, focus=True))
        self.tabs.addTab(self.table, "Tiles")
        self.tabs.addTab(self.legend, "Class details (RGB)")
        self.tabs.hide()
        self.tabs.currentChanged.connect(self._clear_table_states)
        self.view_mode.currentIndexChanged.connect(self._refresh)
        self.boundaries.toggled.connect(self._refresh)
        self.tile_numbers.toggled.connect(self._refresh)
        self.opacity.valueChanged.connect(self._refresh)
        self.comparison.presentation_changed.connect(self.presentation_changed)
        self.compare.toggled.connect(lambda: self._legend_layout_timer.start(0))

    def show_result(self, original, color_map, analysis, presentation=None):
        guard = QSignalBlocker(self)
        self.image.clear_source()
        self.original = original.convert("RGB").copy()
        self.color_map = color_map.convert("RGB").copy()
        self.analysis = analysis
        self.clear_tile_inspection()
        # Verify dimensions before displaying a potentially misleading map.
        render_classification_map(self.original, self.color_map, analysis)
        parameters = presentation or {}
        controls = (self.view_mode, self.opacity, self.boundaries, self.tile_numbers)
        for control in controls:
            control.blockSignals(True)
        view_index = self.view_mode.findData(parameters.get("view", "overlay"))
        self.view_mode.setCurrentIndex(max(0, view_index))
        self.opacity.setValue(round(float(parameters.get("opacity", .4)) * 100))
        self.boundaries.setChecked(bool(parameters.get("boundaries", False)))
        self.tile_numbers.setChecked(bool(parameters.get("tile_numbers", False)))
        for control in controls:
            control.blockSignals(False)
        width, height = analysis["tile_size"]
        self._update_caption()
        self.caption.setToolTip("Training scale unconfirmed. Estimated coverage uses tile classes.")
        self.details_button.setToolTip(f"{len(analysis['tiles'])} tiles; original crops {width} x {height} px. Training scale unconfirmed.")
        self.summary.setText(
            f"Tiled analysis | {len(analysis['tiles'])} tiles | Original tiles: {width} x {height} px | "
            f"Input: {analysis['input_size']} | {analysis['preprocess']} | "
            f"Resize: {analysis.get('resize_backend', 'pillow_bilinear')}\n"
            "Training scale unconfirmed. Coverage is estimated from tile classes, not pixel segmentation.")
        self._update_class_summary(analysis)
        self._tile_rows = {}
        for index, tile in enumerate(analysis["tiles"]):
            x0, y0, _, _ = tile["box"]
            self._tile_rows.setdefault(y0, []).append((x0, index, tile))
        for row in self._tile_rows.values():
            row.sort(key=lambda entry: entry[0])
        self._row_starts = sorted(self._tile_rows)
        self._column_starts = {y: [entry[0] for entry in row] for y, row in self._tile_rows.items()}
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
        self.table.setVerticalHeaderLabels([""] * len(analysis["tiles"]))
        for row, tile in enumerate(analysis["tiles"]):
            for column, text in enumerate((str(row + 1), str(tile["box"]), tile["label"], f"{tile['confidence']:.2%}")):
                self.table.setItem(row, column, QTableWidgetItem(text))
        self.tabs.setCurrentIndex(0)
        self.tile_details_button.setChecked(False)
        self._clear_table_states()
        image = self.render_image(include_boundaries=False, include_numbers=False)
        self.comparison.set_images(self._pixmap(self.original), self._pixmap(image), parameters)
        self._refresh()
        del guard

    @staticmethod
    def _pixmap(image):
        rgb = image.convert("RGB")
        return QPixmap.fromImage(QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888).copy())

    def _update_class_summary(self, analysis):
        if len(self.class_cards) != len(analysis["classes"]):
            for card in self.class_cards:
                self.legend_grid.removeWidget(card)
                card.deleteLater()
            self.class_cards, self.class_swatches, self.class_labels = [], [], []
            for _ in analysis["classes"]:
                card = QWidget(self.legend_content)
                card.setProperty("panelSurface", True)
                card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(0, 0, 0, 0)
                card_layout.setSpacing(6)
                swatch = QLabel(card)
                swatch.setFixedSize(14, 14)
                text = QLabel(card)
                text.setTextFormat(Qt.PlainText)
                text.setWordWrap(True)
                text.setMinimumWidth(0)
                text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                card_layout.addWidget(swatch)
                card_layout.addWidget(text, 1)
                self.class_cards.append(card)
                self.class_swatches.append(swatch)
                self.class_labels.append(text)
        for i, item in enumerate(analysis["classes"]):
            count, ratio = analysis["tile_counts"][i], analysis["area_ratios"][i]
            color = QColor(*item["color"])
            self.class_swatches[i].setStyleSheet(f"background-color: {color.name()}; border: 1px solid rgba(128,128,128,100);")
            self.class_labels[i].setText(f"{item['label']} · {count} tiles\n{ratio:.2%} coverage")
            tip = (f"{item['label']} | {count} tiles | Estimated coverage: {ratio:.2%}\n"
                   f"RGB: {tuple(item['color'])}\nCoverage uses tile classes and actual crop areas.")
            for widget in (self.class_cards[i], self.class_swatches[i], self.class_labels[i]):
                widget.setToolTip(tip)
            self.class_cards[i].show()
        self._layout_class_summary()

    def _update_caption(self):
        if self.analysis is not None:
            width, height = self.analysis["tile_size"]
            prefix = "Tiled analysis | " if self.width() >= 700 else ""
            self.caption.setText(f"{prefix}{len(self.analysis['tiles'])} tiles | {width} x {height} px")

    def _layout_class_summary(self):
        if not self.class_cards:
            return
        # Reserve a usable image in this scrolling content widget. This minimum
        # never propagates through image_page_scroll to the application window.
        self.comparison.setMinimumHeight(max(240, self.fontMetrics().height() * 8 + 96))
        self.inspection_scroll.setFixedHeight(max(80, self.fontMetrics().height() * 5 + 6))
        spacing = self.legend_grid.horizontalSpacing()
        preferred = max(self.fontMetrics().horizontalAdvance(line)
                        for label in self.class_labels for line in label.text().splitlines()) + 24
        # Reserve a scrollbar's width even before it appears to avoid reflow loops.
        width = max(1, self.legend_scroll.width() - self.legend_scroll.verticalScrollBar().sizeHint().width() - 6)
        columns = max(1, min(3, (width + spacing) // (preferred + spacing)))
        while self.legend_grid.count():
            self.legend_grid.takeAt(0)
        for i, card in enumerate(self.class_cards):
            self.legend_grid.addWidget(card, i // columns, i % columns)
        self.legend_columns = columns
        self.legend_grid.activate()
        cell_width = max(1, (width - spacing * (columns - 1)) // columns)
        row_heights = []
        for start in range(0, len(self.class_cards), columns):
            row_heights.append(max(max(card.layout().heightForWidth(cell_width), card.sizeHint().height())
                                   for card in self.class_cards[start:start + columns]))
        height = sum(row_heights) + self.legend_grid.verticalSpacing() * (len(row_heights) - 1) + 4
        self.legend_content.setMinimumHeight(height)
        expanded = self.tile_details_button.isChecked()
        if (expanded or self.compare.isChecked() or self.selected_tile_index is not None) and self.height() < 550:
            # On short panels keep one complete summary row and let it scroll,
            # reserving room for both the image and a readable tile-table row.
            cap = max(row_heights) + 2
        else:
            cap = max(50, min(160, self.height() // (4 if expanded else 3)))
        self.legend_scroll.setFixedHeight(min(height + 2, cap))

    def _toggle_tile_details(self, expanded):
        self._clear_table_states()
        self.tile_details_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        if expanded:
            # Include the styled tab/header, a complete data row, and the
            # horizontal scrollbar when choosing a readable initial drawer size.
            minimum = self.tabs.tabBar().sizeHint().height() + 2 * self.tabs.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
            minimum += max(table.horizontalHeader().sizeHint().height() + table.rowHeight(0)
                           + table.horizontalScrollBar().sizeHint().height() + 2 * table.frameWidth()
                           for table in (self.table, self.legend))
            self.tabs.setMinimumHeight(minimum)
        self.tabs.setVisible(expanded)
        self._layout_class_summary()
        if expanded:
            height = max(1, self.content_splitter.height())
            table_height = max(self.tabs.minimumHeight(), round(height * .25)) if self.height() >= 500 else self.tabs.minimumHeight()
            self.content_splitter.setSizes([max(1, height - table_height), table_height])
            self._inspection_scroll_timer.start(0)

    def tile_at_source(self, point):
        """Find a crop using its recorded half-open source box, independent of zoom."""
        row_index = bisect_right(self._row_starts, point.y()) - 1
        if row_index < 0:
            return None
        y = self._row_starts[row_index]
        column = bisect_right(self._column_starts[y], point.x()) - 1
        if column < 0:
            return None
        _, index, tile = self._tile_rows[y][column]
        x0, y0, x1, y1 = tile["box"]
        return (index, tile) if x0 <= point.x() < x1 and y0 <= point.y() < y1 else None

    def _inspect_at_source(self, point):
        found = self.tile_at_source(point)
        if found is not None:
            self.inspect_tile(found[0])

    def inspect_tile(self, index, focus=False):
        """Link actual crop, read-only table row and source-coordinate highlight."""
        if self.analysis is None or not 0 <= index < len(self.analysis["tiles"]):
            return
        self.selected_tile_index = index
        tile = self.analysis["tiles"][index]
        x0, y0, x1, y1 = tile["box"]
        crop = self.original.crop((x0, y0, x1, y1))
        self.tile_preview.setPixmap(self._pixmap(crop).scaled(
            self.tile_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tile_inspection_text.setText(
            f"Tile {index + 1}: {tile['label']} | Confidence: {tile['confidence']:.2%}\n"
            f"Crop: ({x0}, {y0}, {x1}, {y1}) | {x1 - x0} x {y1 - y0} px\nOriginal pixels")
        self.tile_inspector.show()
        self.previous_tile_button.setEnabled(index > 0)
        self.next_tile_button.setEnabled(index + 1 < len(self.analysis["tiles"]))
        self.table.set_inspection_row(index)
        self._scroll_inspected_tile()
        for view in (self.image, self.original_view):
            view.highlight_source_box(tile["box"], focus=focus)
        self._legend_layout_timer.start(0)

    def _scroll_inspected_tile(self):
        if self.selected_tile_index is not None:
            self.table.scrollToItem(self.table.item(self.selected_tile_index, 0))

    def clear_tile_inspection(self):
        self.selected_tile_index = None
        self.tile_inspector.hide()
        self.tile_preview.clear()
        self.tile_inspection_text.clear()
        self.table.set_inspection_row()
        for view in (self.image, self.original_view):
            view.highlight_source_box()

    def tile_tooltip_at(self, position, view=None):
        found = self.tile_at_source((view or self.image).graphics_view.mapToScene(position))
        if found is None:
            return ""
        index, tile = found
        x0, y0, x1, y1 = tile["box"]
        return (f"Tile {index + 1}: {tile['label']}\nConfidence: {tile['confidence']:.2%}\n"
                f"Source crop: ({x0}, {y0}, {x1}, {y1})\nSize: {x1 - x0} x {y1 - y0} px")

    def eventFilter(self, watched, event):
        legend_scroll = getattr(self, "legend_scroll", None)
        if legend_scroll is not None and watched is legend_scroll.viewport() and event.type() == QEvent.Resize:
            self._legend_layout_timer.start(0)
        view = next((v for v in (self.image, self.original_view) if watched is v.graphics_view.viewport()), None)
        if view is not None:
            if event.type() == QEvent.ToolTip:
                text = self.tile_tooltip_at(event.pos(), view)
                if text:
                    QToolTip.showText(event.globalPos(), text, watched)
                    self._hover_tooltip_active = True
                else:
                    self._hide_tile_tooltip()
                return True
            if event.type() in (QEvent.Leave, QEvent.Hide, QEvent.Wheel, QEvent.Resize, QEvent.MouseButtonPress):
                self._hide_tile_tooltip()
            elif event.type() == QEvent.MouseMove and self._hover_tooltip_active:
                if event.buttons() != Qt.NoButton:
                    self._hide_tile_tooltip()
                else:
                    text = self.tile_tooltip_at(event.pos(), view)
                    if text:
                        QToolTip.showText(event.globalPos(), text, watched)
                    else:
                        self._hide_tile_tooltip()
        return super().eventFilter(watched, event)

    def _hide_tile_tooltip(self):
        if self._hover_tooltip_active:
            QToolTip.hideText()
            self._hover_tooltip_active = False

    def _clear_table_states(self, *unused):
        self.legend.clear_display_state()
        self.table.clear_display_state()
        self._inspection_scroll_timer.start(0)

    def presentation(self):
        return {"view": self.view_mode.currentData(),
                "opacity": self.opacity.value() / 100, "boundaries": self.boundaries.isChecked(),
                "tile_numbers": self.tile_numbers.isChecked(),
                **self.comparison.presentation()}

    def render_image(self, include_boundaries=True, include_numbers=True):
        p = self.presentation()
        image = render_classification_map(self.original, self.color_map, self.analysis,
                                         0 if p["view"] == "original" else p["opacity"],
                                         p["view"] == "color_map", p["boundaries"] and include_boundaries)
        if p["tile_numbers"] and include_numbers:
            qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format_RGB888).copy()
            painter = QPainter(qimage)
            try:
                # Exports retain readable identifiers at full source resolution.
                font_size = max(12, min(160, min(self.analysis["tile_size"]) // 5))
                draw_tile_numbers(painter, [tile["box"] for tile in self.analysis["tiles"]], QTransform(), font_size)
            finally:
                painter.end()
            image = Image.frombytes("RGB", image.size, qimage.bits().asstring(qimage.byteCount()),
                                    "raw", "RGB", qimage.bytesPerLine())
        return image

    def _refresh(self):
        self._hide_tile_tooltip()
        self.opacity_label.setText(f"Opacity: {self.opacity.value()}%")
        self.view_mode.setToolTip(self.view_mode.currentText())
        self.opacity.setEnabled(self.view_mode.currentIndex() == 0)
        if self.analysis is None:
            return
        # Display boundaries are vector foreground lines, not downsampled image pixels.
        image = self.render_image(include_boundaries=False, include_numbers=False)
        qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format_RGB888).copy()
        self.image.update_source_pixmap(QPixmap.fromImage(qimage))
        boxes = [tile["box"] for tile in self.analysis["tiles"]] if self.boundaries.isChecked() else []
        self.image.set_tile_grid(boxes)
        self.original_view.set_tile_grid(boxes)
        numbered_boxes = [tile["box"] for tile in self.analysis["tiles"]] if self.tile_numbers.isChecked() else []
        self.image.set_tile_numbers(numbered_boxes)
        self.original_view.set_tile_numbers(numbered_boxes)
        self.comparison.result_title.setText(self.view_mode.currentText())
        self.presentation_changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # On short result panes keep the duplicate parameter line in Parameters,
        # leaving the image, coverage summary and tile details readable together.
        self.caption.setVisible(self.height() >= 500)
        self.boundaries.setText("Grid" if self.width() < 500 else "Tile boundaries")
        self.tile_numbers.setText("Numbers" if self.width() < 500 else "Tile numbers")
        self._update_caption()
        self._legend_layout_timer.start(0)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange) and hasattr(self, "_legend_layout_timer"):
            self._legend_layout_timer.start(0)

    def clear(self):
        self._hide_tile_tooltip()
        self.clear_tile_inspection()
        self._clear_table_states()
        self.original = self.color_map = self.analysis = None
        self._tile_rows, self._column_starts, self._row_starts = {}, {}, []
        self.tile_details_button.setChecked(False)
        self.comparison.clear()
        self.legend.setRowCount(0)
        self.table.setRowCount(0)
        self.summary.clear()
        self.caption.clear()
        for card in self.class_cards:
            card.hide()
