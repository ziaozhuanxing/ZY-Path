"""Reusable zoomable image viewer for pathology images."""

from PyQt5.QtCore import QPointF, QLineF, QRectF, QSize, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QTransform, QPainter, QPen, QColor
from PyQt5.QtWidgets import (
	QGraphicsPixmapItem,
	QGraphicsScene,
	QGraphicsView,
	QHBoxLayout,
	QLabel,
	QPushButton,
	QSizePolicy,
	QVBoxLayout,
	QWidget,
	QApplication,
)

from ui.tile_annotations import draw_tile_numbers


class _ImageGraphicsView(QGraphicsView):
	"""Graphics view that forwards pointer events to its image owner."""

	def __init__(self, owner: "ZoomableImageView") -> None:
		super().__init__(owner)
		self._owner = owner

	def resizeEvent(self, event) -> None:
		owner = self._owner
		if getattr(owner, "_pixmap_item", None) is None:
			super().resizeEvent(event)
			return
		# Qt has already changed the viewport rectangle at this point. Mapping
		# its new center through the old transform would shift the source center.
		center = QPointF(owner._scene_center)
		previous = owner._applying_view
		owner._applying_view = True
		try:
			super().resizeEvent(event)
			owner._viewport_resized(center)
		finally:
			owner._applying_view = previous

	def drawForeground(self, painter, rect) -> None:
		"""Draw source-coordinate grid AFTER the pixmap, at a fixed logical width."""
		super().drawForeground(painter, rect)
		owner = self._owner
		if owner._pixmap_item is None or not (owner._grid_lines or owner._numbered_tiles or owner._highlight_box):
			return
		# viewportTransform maps the same scene coordinates as the image. Reset only
		# the scene transform; QPainter's device/DPR mapping remains in effect.
		transform = self.viewportTransform()
		lines = [QLineF(transform.map(line.p1()), transform.map(line.p2())) for line in owner._grid_lines]
		painter.save()
		painter.resetTransform()
		painter.setClipRect(transform.mapRect(owner._pixmap_item.sceneBoundingRect()))
		painter.setRenderHint(QPainter.Antialiasing, True)
		for color, width in ((QColor(0, 0, 0, 200), 3.0), (QColor(255, 255, 255), 2.0)):
			pen = QPen(color)
			pen.setWidthF(width)
			pen.setCapStyle(Qt.FlatCap)
			painter.setPen(pen)
			painter.drawLines(lines)
		draw_tile_numbers(painter, owner._numbered_tiles, transform)
		if owner._highlight_box is not None:
			x0, y0, x1, y1 = owner._highlight_box
			box = transform.mapRect(QRectF(x0, y0, x1 - x0, y1 - y0))
			for color, width in ((QColor(0, 0, 0), 5), (QColor("#FFD166"), 3)):
				painter.setPen(QPen(color, width))
				painter.setBrush(Qt.NoBrush)
				painter.drawRect(box.adjusted(1, 1, -1, -1))
		painter.restore()

	def wheelEvent(self, event) -> None:
		self._owner._handle_wheel_event(event)

	def mousePressEvent(self, event) -> None:
		self._owner._handle_mouse_press_event(event)

	def mouseMoveEvent(self, event) -> None:
		self._owner._handle_mouse_move_event(event)

	def mouseReleaseEvent(self, event) -> None:
		self._owner._handle_mouse_release_event(event)

	def mouseDoubleClickEvent(self, event) -> None:
		self._owner._handle_mouse_double_click_event(event)


class ZoomableImageView(QWidget):
	"""Show a full-resolution pixmap with fit, zoom, and pan controls."""
	view_changed = pyqtSignal()
	viewport_resized = pyqtSignal()
	source_clicked = pyqtSignal(QPointF)

	_MIN_ZOOM = 1.0
	_MAX_ZOOM = 1600
	_ZOOM_STEP = 1.25

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setProperty("panelSurface", True)
		self._source_pixmap = QPixmap()
		self._pixmap_item: QGraphicsPixmapItem | None = None
		self._zoom_percent = 100.0
		self._fit_mode = True
		self._grid_lines: list[QLineF] = []
		self._numbered_tiles = []
		self._highlight_box = None
		self._press_position = None
		self._pointer_dragged = False
		self._scene_center = QPointF()
		self._placeholder_text = ""
		self._applying_view = False
		self._view_change_timer = QTimer(self)
		self._view_change_timer.setSingleShot(True)
		self._view_change_timer.timeout.connect(self.view_changed.emit)

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(4)

		controls = QHBoxLayout()
		controls.setContentsMargins(0, 0, 0, 0)
		controls.addStretch()
		self.zoom_out_button = QPushButton("-", self)
		self.zoom_out_button.setObjectName("zoomOutButton")
		self.zoom_out_button.setAccessibleName("Zoom Out")
		self.zoom_out_button.clicked.connect(self.zoom_out)
		self.zoom_out_button.setToolTip("Zoom out of the image.")
		controls.addWidget(self.zoom_out_button)
		self.zoom_in_button = QPushButton("+", self)
		self.zoom_in_button.setObjectName("zoomInButton")
		self.zoom_in_button.setAccessibleName("Zoom In")
		self.zoom_in_button.clicked.connect(self.zoom_in)
		self.zoom_in_button.setToolTip("Zoom in to the image.")
		controls.addWidget(self.zoom_in_button)
		self.fit_button = QPushButton("Fit", self)
		self.fit_button.setObjectName("fitImageButton")
		self.fit_button.clicked.connect(self.fit_to_view)
		self.fit_button.setToolTip("Fit the complete image in the view.")
		controls.addWidget(self.fit_button)
		self.actual_size_button = QPushButton("1:1", self)
		self.actual_size_button.setToolTip("100%: one image pixel per physical display pixel")
		self.actual_size_button.clicked.connect(self.actual_size)
		controls.addWidget(self.actual_size_button)
		self.zoom_indicator = QLabel("--", self)
		self.zoom_indicator.setObjectName("zoomIndicator")
		self.zoom_indicator.setMinimumWidth(52)
		self.zoom_indicator.setAlignment(Qt.AlignCenter)
		self.zoom_indicator.setToolTip("Actual image-to-display pixel ratio. 100% = one source pixel per physical display pixel; Fit is not necessarily 100%.")
		controls.addWidget(self.zoom_indicator)
		layout.addLayout(controls)

		self.graphics_view = _ImageGraphicsView(self)
		self.graphics_view.setObjectName("imageGraphicsView")
		self.graphics_view.setScene(QGraphicsScene(self.graphics_view))
		self.graphics_view.setAlignment(Qt.AlignCenter)
		self.graphics_view.setTransformationAnchor(QGraphicsView.NoAnchor)
		self.graphics_view.setResizeAnchor(QGraphicsView.NoAnchor)
		self.graphics_view.setDragMode(QGraphicsView.NoDrag)
		self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.graphics_view.setToolTip(
			"Use the mouse wheel to zoom, drag with the left button to pan, "
			"and double-click to reset the view."
		)
		layout.addWidget(self.graphics_view, 1)

		self.setMinimumSize(0, 0)
		self.graphics_view.setMinimumSize(0, 0)
		for scrollbar in (self.graphics_view.horizontalScrollBar(), self.graphics_view.verticalScrollBar()):
			scrollbar.valueChanged.connect(self._notify_view_change)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self._set_actions_enabled(False)

	def set_source_pixmap(self, pixmap: QPixmap) -> None:
		"""Set a new full-resolution source and reset the view to fit mode."""
		self.clear_source()
		if pixmap.isNull():
			return
		self._source_pixmap = pixmap.copy()
		self._source_pixmap.setDevicePixelRatio(1.0)
		self._pixmap_item = self.graphics_view.scene().addPixmap(self._source_pixmap)
		self.graphics_view.scene().setSceneRect(self._pixmap_item.boundingRect())
		self._set_actions_enabled(True)
		self.fit_to_view()
		QTimer.singleShot(0, self._refit_if_active)

	def update_source_pixmap(self, pixmap: QPixmap) -> None:
		"""Replace pixels without resetting zoom when coordinates are unchanged."""
		if self._pixmap_item is None or pixmap.size() != self._source_pixmap.size():
			self.set_source_pixmap(pixmap)
			return
		self._source_pixmap = pixmap.copy()
		self._source_pixmap.setDevicePixelRatio(1.0)
		self._pixmap_item.setPixmap(self._source_pixmap)

	def clear_source(self) -> None:
		"""Remove the current image and disable zoom actions."""
		self._source_pixmap = QPixmap()
		self._view_change_timer.stop()
		self.graphics_view.setSceneRect(0, 0, 0, 0)
		self._pixmap_item = None
		self.graphics_view.scene().clear()
		self._zoom_percent = 100.0
		self._fit_mode = True
		self._grid_lines = []
		self._numbered_tiles = []
		self._highlight_box = None
		self._press_position = None
		self._scene_center = QPointF()
		self._update_indicator()
		self._set_actions_enabled(False)
		if self._placeholder_text:
			self.graphics_view.scene().addText(self._placeholder_text)

	def setText(self, text: str) -> None:
		"""Keep QLabel-like placeholder compatibility for existing callers."""
		self._placeholder_text = text
		if self._source_pixmap.isNull():
			self.clear_source()

	def text(self) -> str:
		"""Return the current placeholder text."""
		return self._placeholder_text

	def pixmap(self) -> QPixmap:
		"""Return the unscaled source pixmap for compatibility and inspection."""
		return self._source_pixmap

	def displayed_size(self) -> QSize:
		"""Return the current on-screen size of the image item."""
		if self._pixmap_item is None:
			return QSize()
		return self.graphics_view.mapFromScene(
			self._pixmap_item.sceneBoundingRect()
		).boundingRect().size()

	def zoom_in(self) -> None:
		"""Increase magnification by one step."""
		self._zoom_by(self._ZOOM_STEP)

	def zoom_out(self) -> None:
		"""Decrease magnification by one step."""
		self._zoom_by(1 / self._ZOOM_STEP)

	def minimumSizeHint(self) -> QSize:
		return QSize(80, 60)

	def sizeHint(self) -> QSize:
		return QSize(360, 240)

	def set_tile_grid(self, boxes) -> None:
		"""Merge actual tile edges into scene-coordinate lines; never modify pixels."""
		vertical, horizontal = {}, {}
		for x0, y0, x1, y1 in boxes:
			if self._pixmap_item is None or not (0 <= x0 < x1 <= self._source_pixmap.width() and 0 <= y0 < y1 <= self._source_pixmap.height()):
				raise ValueError("Tile grid coordinates must lie within the source image.")
			for x in (x0, x1):
				vertical.setdefault(x, []).append((y0, y1))
			for y in (y0, y1):
				horizontal.setdefault(y, []).append((x0, x1))
		def merged(intervals):
			result = []
			for start, end in sorted(set(intervals)):
				if result and start <= result[-1][1]:
					result[-1][1] = max(end, result[-1][1])
				else:
					result.append([start, end])
			return result
		self._grid_lines = [QLineF(x, a, x, b) for x, intervals in vertical.items() for a, b in merged(intervals)]
		self._grid_lines += [QLineF(a, y, b, y) for y, intervals in horizontal.items() for a, b in merged(intervals)]
		self.graphics_view.viewport().update()

	def set_tile_numbers(self, boxes) -> None:
		"""Number actual source crops in their recorded order, starting at one."""
		boxes = [tuple(box) for box in boxes]
		for x0, y0, x1, y1 in boxes:
			if self._pixmap_item is None or not (0 <= x0 < x1 <= self._source_pixmap.width() and 0 <= y0 < y1 <= self._source_pixmap.height()):
				raise ValueError("Tile number coordinates must lie within the source image.")
		self._numbered_tiles = boxes
		self.graphics_view.viewport().update()

	def zoom_percent(self) -> float:
		return self.graphics_view.transform().m11() * self.graphics_view.viewport().devicePixelRatioF() * 100

	def highlight_source_box(self, box=None, focus=False):
		"""Transient inspection only; never changes source pixels or exports."""
		self._highlight_box = tuple(box) if box is not None else None
		if box is not None and focus and self._pixmap_item is not None:
			x0, y0, x1, y1 = box
			viewport = self.graphics_view.viewport()
			zoom = min(viewport.width() / (x1 - x0), viewport.height() / (y1 - y0)) * 80 * viewport.devicePixelRatioF()
			self.apply_view_state(min(self._MAX_ZOOM, max(self._MIN_ZOOM, zoom)),
								  QPointF((x0 + x1) / 2, (y0 + y1) / 2))
			self._publish_view_change()
		self.graphics_view.viewport().update()

	def actual_size(self) -> None:
		if self._pixmap_item is None:
			return
		self._fit_mode = False
		self._zoom_percent = 100.0
		self._apply_zoom(self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center()))
		self._publish_view_change()

	def fit_zoom_percent(self) -> float:
		"""Return the physical pixel ratio that fits this viewport."""
		if self._pixmap_item is None:
			return 0.0
		viewport = self.graphics_view.viewport()
		return min(max(1, viewport.width() - 4) / self._source_pixmap.width(),
			max(1, viewport.height() - 4) / self._source_pixmap.height()) * viewport.devicePixelRatioF() * 100

	def view_state(self) -> dict:
		"""Describe navigation in original-image coordinates."""
		return {"zoom": self.zoom_percent(), "fit": self._fit_mode,
			"center": self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())}

	def apply_view_state(self, zoom: float, center: QPointF, fit: bool = False) -> None:
		"""Apply an absolute linked view without emitting another navigation change."""
		if self._pixmap_item is None:
			return
		self._view_change_timer.stop()
		previous = self._applying_view
		self._applying_view = True
		try:
			self._fit_mode = fit
			self._zoom_percent = zoom
			self._apply_zoom(center)
		finally:
			self._applying_view = previous

	def _notify_view_change(self, *unused) -> None:
		if not self._applying_view:
			self._scene_center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
			self._view_change_timer.start(0)

	def _publish_view_change(self) -> None:
		"""Commit explicit navigation before a following resize can use old state."""
		self._view_change_timer.stop()
		if not self._applying_view:
			self.view_changed.emit()

	def fit_to_view(self) -> None:
		"""Fit the full image; show its actual pixel ratio, not a relative 100%."""
		if self._pixmap_item is None:
			return
		self.apply_view_state(self.fit_zoom_percent(), self._pixmap_item.boundingRect().center(), fit=True)
		self._publish_view_change()

	def _refit_if_active(self) -> None:
		if self._fit_mode:
			self.fit_to_view()

	def _viewport_resized(self, center: QPointF) -> None:
		if self._fit_mode:
			self.fit_to_view()
		else:
			self._apply_zoom(center)
		self.viewport_resized.emit()

	def showEvent(self, event) -> None:
		super().showEvent(event)
		QTimer.singleShot(0, self._refit_if_active)

	def _zoom_by(self, factor: float, scene_center=None, viewport_position=None) -> None:
		if self._pixmap_item is None:
			return
		current = self.zoom_percent()
		if factor > 1 and current >= self._MAX_ZOOM:
			return
		new_zoom = max(self._MIN_ZOOM, current * factor)
		if factor > 1:
			new_zoom = min(self._MAX_ZOOM, new_zoom)
		if scene_center is None:
			scene_center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
		self._fit_mode = False
		self._zoom_percent = new_zoom
		self._apply_zoom(scene_center)
		if viewport_position is not None:
			viewport_center = self.graphics_view.viewport().rect().center()
			scale = self.graphics_view.transform().m11()
			adjusted = scene_center + QPointF((viewport_center.x() - viewport_position.x()) / scale,
											 (viewport_center.y() - viewport_position.y()) / scale)
			self.graphics_view.centerOn(adjusted)
			self._scene_center = adjusted
		self._publish_view_change()

	def _apply_zoom(self, scene_center: QPointF) -> None:
		if self._pixmap_item is None:
			return
		# Absolute scale from source pixels, never fit-scale multiplied repeatedly.
		scale = self._zoom_percent / (100 * self.graphics_view.viewport().devicePixelRatioF())
		previous = self._applying_view
		self._applying_view = True
		try:
			# Equal source centers must also be possible near image edges and in
			# unequal panes. Recompute padding for the actual viewport and zoom.
			pad_x = self.graphics_view.viewport().width() / scale
			pad_y = self.graphics_view.viewport().height() / scale
			self.graphics_view.setSceneRect(self._pixmap_item.boundingRect().adjusted(-pad_x, -pad_y, pad_x, pad_y))
			self.graphics_view.setTransform(QTransform.fromScale(scale, scale))
			self.graphics_view.centerOn(scene_center)
			self._scene_center = QPointF(scene_center)
			self._update_indicator()
			self._update_drag_mode()
			self._set_actions_enabled(True)
		finally:
			self._applying_view = previous

	def _update_indicator(self) -> None:
		if self._pixmap_item is None:
			self.zoom_indicator.setText("--")
			return
		value = f"{self.zoom_percent():.1f}".removesuffix(".0")
		self.zoom_indicator.setText(f"Fit ({value}%)" if self._fit_mode else f"{value}%")

	def _update_drag_mode(self) -> None:
		self.graphics_view.setDragMode(QGraphicsView.NoDrag if self._fit_mode else QGraphicsView.ScrollHandDrag)

	def _set_actions_enabled(self, enabled: bool) -> None:
		self.zoom_in_button.setEnabled(enabled and self._zoom_percent < self._MAX_ZOOM)
		self.zoom_out_button.setEnabled(enabled and self._zoom_percent > self._MIN_ZOOM)
		self.actual_size_button.setEnabled(enabled)
		self.fit_button.setEnabled(enabled)

	def _handle_wheel_event(self, event) -> None:
		if self._pixmap_item is None:
			event.ignore()
			return
		# High-resolution wheels/trackpads send fractions of a 120-unit notch.
		# Scroll phase markers and horizontal-only gestures must not zoom out.
		steps = event.angleDelta().y() / 120
		if not steps:
			steps = event.pixelDelta().y() / 120
		if not steps:
			event.accept()
			return
		anchor = self.graphics_view.mapToScene(event.pos())
		factor = self._ZOOM_STEP ** steps
		self._zoom_by(factor, anchor, event.pos())
		event.accept()

	def _handle_mouse_press_event(self, event) -> None:
		self._press_position = event.pos() if event.button() == Qt.LeftButton else None
		self._pointer_dragged = False
		QGraphicsView.mousePressEvent(self.graphics_view, event)

	def _handle_mouse_move_event(self, event) -> None:
		if self._press_position is not None and (event.pos() - self._press_position).manhattanLength() >= QApplication.startDragDistance():
			self._pointer_dragged = True
		QGraphicsView.mouseMoveEvent(self.graphics_view, event)

	def _handle_mouse_release_event(self, event) -> None:
		QGraphicsView.mouseReleaseEvent(self.graphics_view, event)
		if event.button() == Qt.LeftButton and self._press_position is not None:
			if not self._pointer_dragged and (event.pos() - self._press_position).manhattanLength() < QApplication.startDragDistance():
				point = self.graphics_view.mapToScene(event.pos())
				if self._pixmap_item is not None and self._pixmap_item.boundingRect().contains(point):
					self.source_clicked.emit(point)
			self._press_position = None

	def _handle_mouse_double_click_event(self, event) -> None:
		if event.button() == Qt.LeftButton:
			self.fit_to_view()
			event.accept()
			return
		QGraphicsView.mouseDoubleClickEvent(self.graphics_view, event)
