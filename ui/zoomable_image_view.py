"""Reusable zoomable image viewer for pathology images."""

from PyQt5.QtCore import QPointF, QSize, QTimer, Qt
from PyQt5.QtGui import QPixmap, QResizeEvent, QTransform
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
)


class _ImageGraphicsView(QGraphicsView):
	"""Graphics view that forwards pointer events to its image owner."""

	def __init__(self, owner: "ZoomableImageView") -> None:
		super().__init__(owner)
		self._owner = owner

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

	_MIN_ZOOM = 100
	_MAX_ZOOM = 1600
	_ZOOM_STEP = 1.25

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._source_pixmap = QPixmap()
		self._pixmap_item: QGraphicsPixmapItem | None = None
		self._zoom_percent = self._MIN_ZOOM
		self._scene_center = QPointF()
		self._placeholder_text = ""

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(4)

		controls = QHBoxLayout()
		controls.setContentsMargins(0, 0, 0, 0)
		controls.addStretch()
		self.zoom_out_button = QPushButton("Zoom Out", self)
		self.zoom_out_button.setObjectName("zoomOutButton")
		self.zoom_out_button.clicked.connect(self.zoom_out)
		self.zoom_out_button.setToolTip("Zoom out of the image.")
		controls.addWidget(self.zoom_out_button)
		self.zoom_in_button = QPushButton("Zoom In", self)
		self.zoom_in_button.setObjectName("zoomInButton")
		self.zoom_in_button.clicked.connect(self.zoom_in)
		self.zoom_in_button.setToolTip("Zoom in to the image.")
		controls.addWidget(self.zoom_in_button)
		self.fit_button = QPushButton("Fit", self)
		self.fit_button.setObjectName("fitImageButton")
		self.fit_button.clicked.connect(self.fit_to_view)
		self.fit_button.setToolTip("Fit the complete image in the view.")
		controls.addWidget(self.fit_button)
		self.zoom_indicator = QLabel("100%", self)
		self.zoom_indicator.setObjectName("zoomIndicator")
		self.zoom_indicator.setMinimumWidth(52)
		self.zoom_indicator.setAlignment(Qt.AlignCenter)
		self.zoom_indicator.setToolTip("Magnification relative to fit-to-view.")
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

		self.setMinimumSize(180, 150)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self._set_actions_enabled(False)

	def set_source_pixmap(self, pixmap: QPixmap) -> None:
		"""Set a new full-resolution source and reset the view to fit mode."""
		self.clear_source()
		if pixmap.isNull():
			return
		self._source_pixmap = pixmap.copy()
		self._pixmap_item = self.graphics_view.scene().addPixmap(self._source_pixmap)
		self.graphics_view.scene().setSceneRect(self._pixmap_item.boundingRect())
		self._set_actions_enabled(True)
		self.fit_to_view()
		QTimer.singleShot(0, self.fit_to_view)

	def clear_source(self) -> None:
		"""Remove the current image and disable zoom actions."""
		self._source_pixmap = QPixmap()
		self._pixmap_item = None
		self.graphics_view.scene().clear()
		self._zoom_percent = self._MIN_ZOOM
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

	def fit_to_view(self) -> None:
		"""Fit the complete source image and reset magnification to 100%."""
		if self._pixmap_item is None:
			return
		self._zoom_percent = self._MIN_ZOOM
		self.graphics_view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
		self._scene_center = self._pixmap_item.boundingRect().center()
		self._update_indicator()
		self._update_drag_mode()
		self._set_actions_enabled(True)

	def resizeEvent(self, event: QResizeEvent) -> None:
		"""Refit or preserve manual zoom when the viewport changes size."""
		manual_center = self._scene_center
		if self._pixmap_item is not None and self._zoom_percent > self._MIN_ZOOM:
			manual_center = self.graphics_view.mapToScene(
				self.graphics_view.viewport().rect().center()
			)
		super().resizeEvent(event)
		if self._pixmap_item is None:
			return
		if self._zoom_percent == self._MIN_ZOOM:
			self.fit_to_view()
		else:
			self._apply_zoom(manual_center)

	def showEvent(self, event) -> None:
		"""Fit once more after the viewer becomes visible in a stacked page."""
		super().showEvent(event)
		if self._pixmap_item is not None and self._zoom_percent == self._MIN_ZOOM:
			QTimer.singleShot(0, self.fit_to_view)

	def _zoom_by(
		self,
		factor: float,
		scene_center: QPointF | None = None,
		viewport_position=None,
	) -> None:
		if self._pixmap_item is None:
			return
		new_zoom = max(
			self._MIN_ZOOM,
			min(self._MAX_ZOOM, round(self._zoom_percent * factor)),
		)
		if new_zoom == self._zoom_percent:
			return
		if scene_center is None:
			scene_center = self.graphics_view.mapToScene(
				self.graphics_view.viewport().rect().center()
			)
		self._zoom_percent = new_zoom
		self._apply_zoom(scene_center)
		if viewport_position is not None:
			viewport_center = self.graphics_view.viewport().rect().center()
			view_scale = self.graphics_view.transform().m11()
			adjusted_center = scene_center + QPointF(
				(viewport_center.x() - viewport_position.x()) / view_scale,
				(viewport_center.y() - viewport_position.y()) / view_scale,
			)
			self.graphics_view.centerOn(adjusted_center)
			self._scene_center = adjusted_center

	def _apply_zoom(self, scene_center: QPointF) -> None:
		if self._pixmap_item is None:
			return
		self.graphics_view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
		fit_scale = self.graphics_view.transform().m11()
		zoom_scale = fit_scale * self._zoom_percent / self._MIN_ZOOM
		self.graphics_view.setTransform(QTransform.fromScale(zoom_scale, zoom_scale))
		self.graphics_view.centerOn(scene_center)
		self._scene_center = scene_center
		self._update_indicator()
		self._update_drag_mode()
		self._set_actions_enabled(True)

	def _update_indicator(self) -> None:
		self.zoom_indicator.setText(f"{self._zoom_percent}%")

	def _update_drag_mode(self) -> None:
		mode = (
			QGraphicsView.ScrollHandDrag
			if self._zoom_percent > self._MIN_ZOOM
			else QGraphicsView.NoDrag
		)
		self.graphics_view.setDragMode(mode)

	def _set_actions_enabled(self, enabled: bool) -> None:
		self.zoom_in_button.setEnabled(enabled and self._zoom_percent < self._MAX_ZOOM)
		self.zoom_out_button.setEnabled(enabled and self._zoom_percent > self._MIN_ZOOM)
		self.fit_button.setEnabled(enabled)

	def _handle_wheel_event(self, event) -> None:
		if self._pixmap_item is None:
			event.ignore()
			return
		anchor = self.graphics_view.mapToScene(event.pos())
		factor = self._ZOOM_STEP if event.angleDelta().y() > 0 else 1 / self._ZOOM_STEP
		self._zoom_by(factor, anchor, event.pos())
		event.accept()

	def _handle_mouse_press_event(self, event) -> None:
		QGraphicsView.mousePressEvent(self.graphics_view, event)

	def _handle_mouse_move_event(self, event) -> None:
		QGraphicsView.mouseMoveEvent(self.graphics_view, event)

	def _handle_mouse_release_event(self, event) -> None:
		QGraphicsView.mouseReleaseEvent(self.graphics_view, event)

	def _handle_mouse_double_click_event(self, event) -> None:
		if event.button() == Qt.LeftButton:
			self.fit_to_view()
			event.accept()
			return
		QGraphicsView.mouseDoubleClickEvent(self.graphics_view, event)
