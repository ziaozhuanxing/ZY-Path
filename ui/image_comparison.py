"""Shared original/result comparison with source-coordinate navigation."""
from PyQt5.QtCore import QEvent, QPointF, QSignalBlocker, QTimer, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLayout, QSizePolicy,
    QScrollArea, QSlider, QSplitter, QVBoxLayout, QWidget,
)

from ui.language import tr
from ui.explicit_combo_box import ExplicitComboBox
from ui.zoomable_image_view import ZoomableImageView
from ui.result_check_box import ResultCheckBox
from ui.theme import style_panel_scroll


class ImageComparison(QWidget):
    """Host page-specific controls and equal, optionally linked image views."""

    presentation_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setProperty("panelSurface", True)
        self._ratio = .5
        self._ratio_pending = False
        self._syncing = False
        self._resize_state = None
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.timeout.connect(self._adapt_layout)
        self._navigation_timer = QTimer(self)
        self._navigation_timer.setSingleShot(True)
        self._navigation_timer.timeout.connect(self._settle_views)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.primary = QWidget(self)
        self.primary.setProperty("panelSurface", True)
        self.primary.setMinimumWidth(0)
        view_controls = QFormLayout(self.primary)
        view_controls.setContentsMargins(0, 0, 0, 0)
        view_controls.setSpacing(6)
        view_controls.setRowWrapPolicy(QFormLayout.WrapLongRows)
        view_controls.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        view_controls.setSizeConstraint(QLayout.SetNoConstraint)
        self.view_mode = ExplicitComboBox(self.primary)
        self.view_mode.setMinimumContentsLength(8)
        self.view_mode.setSizeAdjustPolicy(ExplicitComboBox.AdjustToMinimumContentsLengthWithIcon)
        opacity_controls = QWidget(self.primary)
        opacity_controls.setProperty("panelSurface", True)
        opacity_row = QHBoxLayout(opacity_controls)
        opacity_row.setContentsMargins(0, 0, 0, 0)
        self.opacity_label = QLabel(opacity_controls)
        self.opacity = QSlider(Qt.Horizontal, opacity_controls)
        self.opacity.setMinimumWidth(96)
        self.opacity.setRange(0, 100)
        self.opacity.setAccessibleName(tr("Overlay opacity"))
        opacity_row.addWidget(self.opacity_label)
        opacity_row.addWidget(self.opacity, 1)
        view_controls.addRow(self.view_mode, opacity_controls)
        # View mode and opacity need the full row. The comparison controls
        # below can wrap without taking width from the slider.
        layout.addWidget(self.primary)
        self.options = QBoxLayout(QBoxLayout.LeftToRight)
        self.options.setSpacing(8)
        self.annotations = QHBoxLayout()
        self.options.addLayout(self.annotations)
        self.controls = QWidget(self)
        self.controls.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.controls.setMinimumWidth(0)
        controls = QHBoxLayout(self.controls)
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(5)
        self.compare = ResultCheckBox(tr("Compare with original"), self.controls)
        self.compare.setToolTip(tr("Show the original and result together. Drag the divider to resize the panes."))
        self.link_views = ResultCheckBox(tr("Link views"), self.controls)
        self.link_views.setToolTip(tr("Synchronize Fit, zoom and pan using original-image coordinates."))
        self.link_views.setChecked(True)
        self.link_views.hide()
        controls.addWidget(self.compare)
        controls.addWidget(self.link_views)
        self.options.addWidget(self.controls)
        self.options.addStretch()
        layout.addLayout(self.options)
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setHandleWidth(6)
        # Preview the divider while dragging; resize both image viewports once
        # on release instead of repeatedly refitting during the gesture.
        self.splitter.setOpaqueResize(False)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setMinimumSize(0, 0)
        self.image_scroll = QScrollArea(self)
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setMinimumSize(0, 0)
        self.image_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.image_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_scroll.setWidget(self.splitter)
        style_panel_scroll(self.image_scroll)
        layout.addWidget(self.image_scroll, 1)
        self.original_pane, self.original_title, self.original_view = self._pane("Original image")
        self.result_pane, self.result_title, self.image = self._pane("Overlay")
        self.splitter.handle(1).setToolTip(tr("Drag to resize the original and result views."))
        self.original_pane.hide()
        self.result_title.hide()
        for index in range(2):
            self.splitter.setStretchFactor(index, 1)
        self.compare.toggled.connect(self._compare_changed)
        self.link_views.toggled.connect(self._link_changed)
        self.splitter.splitterMoved.connect(self._splitter_moved)
        for view in (self.original_view, self.image):
            view.view_changed.connect(lambda view=view: self._view_changed(view))
            view.viewport_resized.connect(self._viewport_resized)

    def _pane(self, title):
        pane = QWidget(self.splitter)
        pane.setProperty("panelSurface", True)
        pane.setMinimumSize(0, 0)
        pane.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        label = QLabel(tr(title), pane)
        layout.addWidget(label)
        view = ZoomableImageView(pane)
        layout.addWidget(view, 1)
        self.splitter.addWidget(pane)
        return pane, label, view

    def set_images(self, original, result, presentation=None):
        """Reset navigation for a new result, accepting older presentation records."""
        guard = QSignalBlocker(self)
        params = presentation or {}
        self._syncing = True
        try:
            self.original_view.set_source_pixmap(original)
            self.image.set_source_pixmap(result)
            self._ratio = max(.01, min(.99, float(params.get("split_ratio", .5))))
            available = not original.isNull()
            self.compare.setEnabled(available)
            self.compare.setChecked(bool(params.get("compare", False)) and available)
            self.link_views.setChecked(bool(params.get("link_views", True)))
            self.link_views.setEnabled(available and original.size() == result.size())
            if not self.link_views.isEnabled():
                self.link_views.setChecked(False)
            self._update_visibility()
            self._ratio_pending = self.compare.isChecked()
            self._resize_state = None
        finally:
            self._syncing = False
        self._layout_timer.start(0)
        del guard

    def presentation(self):
        return {"compare": self.compare.isChecked(), "link_views": self.link_views.isChecked(),
                "split_ratio": self._ratio}

    def linked(self):
        return self.compare.isChecked() and self.link_views.isChecked() and self.link_views.isEnabled()

    def _update_visibility(self):
        visible = self.compare.isChecked()
        self.original_pane.setVisible(visible)
        self.result_title.setVisible(visible)
        self.link_views.setVisible(visible)
        self._update_zoom_controls()

    def _update_zoom_controls(self):
        shared = self.linked()
        self.original_view.navigation.setVisible(not shared)
        navigation = self.image.navigation
        if shared and navigation.parentWidget() is not self:
            self.layout().insertWidget(self.layout().indexOf(self.image_scroll), navigation)
        elif not shared and navigation.parentWidget() is self:
            self.image.layout().insertWidget(0, navigation)
        navigation.show()
        navigation.setToolTip("Zoom controls apply to both linked images." if shared else "")

    def _compare_changed(self):
        self._update_visibility()
        if not self._syncing:
            self._ratio_pending = self.compare.isChecked()
            self._layout_timer.start(0)
            self.presentation_changed.emit()

    def _link_changed(self):
        self._update_zoom_controls()
        if not self._syncing:
            if self.linked():
                self._resize_state = self.image.view_state()
                self._navigation_timer.start(0)
            self._layout_timer.start(0)
            self.presentation_changed.emit()

    def _splitter_moved(self, *unused):
        sizes = self.splitter.sizes()
        if self.compare.isChecked() and sum(sizes) and not self._syncing:
            self._ratio = sizes[0] / sum(sizes)
            self.presentation_changed.emit()

    def _adapt_layout(self):
        full = self.fontMetrics().horizontalAdvance(tr("Compare with original")) + 28
        link = self.link_views.sizeHint().width() + 6 if self.compare.isChecked() else 0
        annotations = self.annotations.sizeHint().width()
        self.compare.setText(tr("Compare") if self.width() < annotations + full + link + 12 else tr("Compare with original"))
        options_width = annotations + self.controls.sizeHint().width() + 12
        self.options.setDirection(QBoxLayout.TopToBottom if self.width() < options_width else QBoxLayout.LeftToRight)
        orientation = Qt.Horizontal if self.width() >= 700 else Qt.Vertical
        if self.splitter.orientation() != orientation:
            self.splitter.setOrientation(orientation)
            self._ratio_pending = self.compare.isChecked()
        # Keep navigation and an image strip readable when a small page also
        # has expanded result tables. The scroll area absorbs this minimum;
        # it must not become a minimum size for the application window.
        heights = []
        for pane, title, view in ((self.original_pane, self.original_title, self.original_view),
                                  (self.result_pane, self.result_title, self.image)):
            controls_height = view.navigation.sizeHint().height() if (
                view.navigation.parentWidget() is view and not view.navigation.isHidden()) else 0
            height = controls_height + (32 if self.compare.isChecked() else 60) + 6
            height += title.sizeHint().height() + 3 if self.compare.isChecked() else 0
            heights.append(height)
        minimum = (sum(heights) + self.splitter.handleWidth()) if self.compare.isChecked() and orientation == Qt.Vertical else max(heights)
        self.splitter.setMinimumHeight(minimum)
        navigation_height = max(view.zoom_in_button.sizeHint().height()
                                for view in (self.original_view, self.image))
        self.image_scroll.setMinimumHeight(navigation_height + 2 * self.image_scroll.frameWidth())
        if self._ratio_pending and self.compare.isChecked():
            total = max(2, (self.splitter.width() if orientation == Qt.Horizontal else self.splitter.height()) - self.splitter.handleWidth())
            self._syncing = True
            self.splitter.setSizes([round(total * self._ratio), round(total * (1 - self._ratio))])
            self._syncing = False
            self._ratio_pending = False
        self._navigation_timer.start(0)

    def _viewport_resized(self):
        if self.linked() and not self._syncing:
            # Keep the last settled source center; individual resize events may
            # temporarily clamp each graphics view differently.
            self._navigation_timer.start(0)

    def _view_changed(self, view):
        if self.linked() and not self._syncing:
            self._navigation_timer.stop()
            state = view.view_state()
            self._resize_state = state
            self._synchronize(state, driver=view)

    def _settle_views(self):
        if self.linked() and self.isVisible():
            self._synchronize(self._resize_state or self.image.view_state())

    def _synchronize(self, state, driver=None):
        views = (self.original_view, self.image)
        if any(view.pixmap().isNull() for view in views):
            return
        fit = state["fit"]
        zoom = min(view.fit_zoom_percent() for view in views) if fit else state["zoom"]
        center = QPointF(self.image.pixmap().width() / 2, self.image.pixmap().height() / 2) if fit else state["center"]
        self._syncing = True
        try:
            for view in views:
                # Reapplying a transform to QGraphicsView's active hand drag
                # changes its scrollbar origin and fights the next pointer move.
                if view is driver and not fit:
                    continue
                view.apply_view_state(zoom, center, fit)
            self._resize_state = {"zoom": zoom, "fit": fit, "center": center}
        finally:
            self._syncing = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_timer.start(0)

    def showEvent(self, event):
        super().showEvent(event)
        self._layout_timer.start(0)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange) and hasattr(self, "_layout_timer"):
            self._layout_timer.start(0)

    def clear(self):
        self._navigation_timer.stop()
        self.original_view.clear_source()
        self.image.clear_source()
        guard = QSignalBlocker(self)
        self._ratio = .5
        self._resize_state = None
        self.compare.setChecked(False)
        self.link_views.setChecked(True)
        self._update_visibility()
        del guard
