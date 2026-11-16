"""Application-wide click feedback and protection against wheel selection."""

from math import hypot

from PyQt5.QtCore import QEasingCurve, QEvent, QObject, QPointF, Qt, QVariantAnimation
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAbstractSlider,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QGraphicsEffect,
    QPushButton,
    QScrollBar,
    QTabBar,
    QToolButton,
    QWidget,
)


class _ClickFeedback(QGraphicsEffect):
    """Paint a brief, clipped ripple without moving or blocking the button."""

    def __init__(self, button: QAbstractButton) -> None:
        super().__init__(button)
        self.setObjectName("clickFeedback")
        self._button = button
        self._progress = 1.0
        self._origin = QPointF()
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(280)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._advance)
        button.pressed.connect(self._start)
        button.setGraphicsEffect(self)

    def _start(self) -> None:
        button = self._button
        if not button.isEnabled():
            return
        self.animation.stop()
        self._progress = 0.0
        self._origin = QPointF(button.mapFromGlobal(button.cursor().pos()))
        if not button.rect().contains(self._origin.toPoint()):
            self._origin = QPointF(button.rect().center())
        self.animation.start()

    def _advance(self, value: float) -> None:
        self._progress = float(value)
        self.update()

    def draw(self, painter: QPainter) -> None:
        self.drawSource(painter)
        if self._progress >= 1 or not self._button.isEnabled():
            return
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        bounds = self.sourceBoundingRect(Qt.LogicalCoordinates)
        clip = QPainterPath()
        clip.addRoundedRect(bounds.adjusted(1, 1, -1, -1), 5, 5)
        painter.setClipPath(clip)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(144, 205, 244, round(55 * (1 - self._progress))))
        radius = hypot(bounds.width(), bounds.height()) * self._progress
        painter.drawEllipse(self._origin, radius, radius)
        painter.restore()


class _InteractionPolicy(QObject):
    """Keep choices intentional while retaining scrolling in content views."""

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        # Retain Python paint overrides even for buttons created internally by Qt.
        self._feedbacks: dict[int, _ClickFeedback] = {}

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if not isinstance(watched, QWidget):
            return False
        if event.type() == QEvent.Polish:
            self.prepare(watched)
        elif event.type() == QEvent.Wheel and self._is_choice(watched):
            # Both mouse wheels and touchpad pixel scrolling arrive as Wheel events.
            event.ignore()
            return True
        return False

    def prepare(self, widget: QWidget) -> None:
        if isinstance(widget, (QAbstractButton, QComboBox, QTabBar)):
            widget.setCursor(Qt.PointingHandCursor)
        if isinstance(widget, (QPushButton, QToolButton)) and widget.graphicsEffect() is None:
            key = id(widget)
            self._feedbacks[key] = _ClickFeedback(widget)
            widget.destroyed.connect(lambda: self._feedbacks.pop(key, None))

    @staticmethod
    def _is_choice(widget: QWidget) -> bool:
        while widget is not None:
            if isinstance(widget, QScrollBar):
                return False
            if isinstance(widget, (QAbstractButton, QComboBox, QAbstractSpinBox, QTabBar, QAbstractSlider)):
                return True
            widget = widget.parentWidget()
        return False


def install_interactions(app: QApplication) -> None:
    """Install one policy, including for controls created in later dialogs."""
    if getattr(app, "_zy_interaction_policy", None) is None:
        app._zy_interaction_policy = _InteractionPolicy(app)
        app.installEventFilter(app._zy_interaction_policy)
    for widget in app.allWidgets():
        app._zy_interaction_policy.prepare(widget)
