"""Shared button feedback and protection against accidental wheel selection."""

from PyQt5.QtCore import QEasingCurve, QEvent, QObject, QRectF, Qt, QVariantAnimation
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractSlider, QAbstractSpinBox, QApplication, QComboBox,
    QCheckBox, QPushButton, QRadioButton, QScrollBar, QStyle, QTabBar, QToolButton, QWidget,
)

from ui.explicit_combo_box import forward_wheel_to_page


class _ButtonFeedback(QWidget):
    """Paint a short click pulse without changing the control's style or size."""

    def __init__(self, button: QAbstractButton, colors: dict[str, str]) -> None:
        super().__init__(button)
        self.setObjectName("clickFeedback")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFocusPolicy(Qt.NoFocus)
        self._button = button
        self._colors = colors
        self.hide()
        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(260)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._update_pulse)
        self.animation.finished.connect(self.hide)
        button.clicked.connect(self.play)

    def play(self) -> None:
        if not self._button.isVisible() or not self._button.isEnabled():
            return
        if self._button.style().styleHint(QStyle.SH_Widget_Animation_Duration, None, self._button) == 0:
            return
        self.animation.stop()
        self.setGeometry(self._button.rect())
        self.raise_()
        self.show()
        self.animation.start()

    def _update_pulse(self, _value) -> None:
        self.update()

    def paintEvent(self, event) -> None:
        phase = self.animation.currentValue()
        if phase is None or phase >= 1:
            return
        color = QColor(self._colors["pulse"])
        color.setAlphaF(0.85 * (1 - phase))
        inset = 1.5 + phase * 2.5
        box = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(color, 2))
        radius = 15 if self._button.objectName() == "settingsButton" else 6
        painter.drawRoundedRect(box, radius, radius)
        painter.end()

    def stop(self) -> None:
        self.animation.stop()
        self.hide()


class _InteractionPolicy(QObject):
    """Apply the same click and wheel rules to current and future windows."""

    def __init__(self, app: QApplication, colors: dict[str, str]) -> None:
        super().__init__(app)
        self.colors = dict(colors)
        self._feedbacks: dict[int, _ButtonFeedback] = {}
        self._app = app
        app.aboutToQuit.connect(self.dispose)

    def dispose(self) -> None:
        """Disconnect feedback while widgets still exist, before native teardown."""
        self._app.removeEventFilter(self)
        for feedback in list(self._feedbacks.values()):
            feedback.stop()
            feedback._button.clicked.disconnect(feedback.play)
        self._feedbacks.clear()

    def stop_feedback(self) -> None:
        for feedback in list(self._feedbacks.values()):
            feedback.stop()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if not isinstance(watched, QWidget):
            return False
        kind = event.type()
        if kind == QEvent.Polish:
            self.prepare(watched)
        elif kind in (QEvent.Hide, QEvent.EnabledChange, QEvent.Resize):
            feedback = self._feedbacks.get(id(watched))
            if feedback is not None:
                feedback.stop()
        elif kind == QEvent.Wheel:
            choice = self._choice_owner(watched)
            if choice is not None:
                if isinstance(choice, QComboBox) and choice.view().isVisible():
                    event.accept()
                else:
                    forward_wheel_to_page(choice, event)
                return True
        return False

    def prepare(self, widget: QWidget) -> None:
        if isinstance(widget, (QAbstractButton, QComboBox, QTabBar)):
            widget.setCursor(Qt.PointingHandCursor)
        if isinstance(widget, (QPushButton, QToolButton, QCheckBox, QRadioButton)) and id(widget) not in self._feedbacks:
            # Leave deliberately styled custom controls to their owner.
            if widget.styleSheet():
                return
            key = id(widget)
            self._feedbacks[key] = _ButtonFeedback(widget, self.colors)
            widget.destroyed.connect(lambda: self._feedbacks.pop(key, None))

    @staticmethod
    def _choice_owner(widget: QWidget) -> QWidget | None:
        while widget is not None:
            if isinstance(widget, QScrollBar):
                return None
            if isinstance(widget, (QAbstractButton, QComboBox, QAbstractSpinBox, QTabBar, QAbstractSlider)):
                return widget
            widget = widget.parentWidget()
        return None


def stop_feedback(app: QApplication) -> None:
    """Clear active click pulses before a palette change."""
    policy = getattr(app, "_zy_interaction_policy", None)
    if policy is not None:
        policy.stop_feedback()


def install_interactions(app: QApplication, colors: dict[str, str]) -> None:
    """Install one application policy without replacing existing widget behavior."""
    policy = getattr(app, "_zy_interaction_policy", None)
    if policy is None:
        policy = _InteractionPolicy(app, colors)
        app._zy_interaction_policy = policy
        app.installEventFilter(policy)
    else:
        policy.colors.clear()
        policy.colors.update(colors)
        policy.stop_feedback()
    for widget in app.allWidgets():
        policy.prepare(widget)
