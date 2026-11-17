"""Shared button feedback and protection against accidental wheel selection."""

from PyQt5.QtCore import QEasingCurve, QEvent, QObject, Qt, QVariantAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractSlider, QAbstractSpinBox, QApplication, QComboBox,
    QPushButton, QScrollBar, QTabBar, QToolButton, QWidget,
)

from ui.explicit_combo_box import forward_wheel_to_page


class _ButtonFeedback(QObject):
    """Animate a button's background without replacing its native painting."""

    def __init__(self, button: QAbstractButton, colors: dict[str, str]) -> None:
        super().__init__(button)
        self.setObjectName("clickFeedback")
        self._button = button
        self._colors = colors
        self._hovered = False
        self._current = self._target()
        self._selector = "QPushButton" if isinstance(button, QPushButton) else "QToolButton"
        self._own_style = ""
        self.animation = QVariantAnimation(self)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._show_color)
        self.animation.finished.connect(self._restore_style)
        button.pressed.connect(self._press)
        button.released.connect(self._release)

    def _target(self, pressed: bool = False) -> QColor:
        colors = self._colors
        name = self._button.objectName()
        if self._button.property("secondary") or isinstance(self._button, QToolButton):
            if name == "settingsButton":
                return QColor("#23456E" if pressed else colors["accent"] if self._hovered else colors["primary"])
            return QColor(colors["selection"] if pressed or self._hovered or self._button.isChecked() else colors["soft"])
        if name == "deleteSelectedButton":
            return QColor("#9B2C2C" if pressed else "#C53030" if self._hovered else colors["error"])
        if pressed:
            return QColor("#23456E")
        if name == "runInferenceButton":
            return QColor(colors["primary"] if self._hovered else colors["accent"])
        return QColor(colors["accent"] if self._hovered or self._button.isChecked() else colors["primary"])

    def _show_color(self, color: QColor) -> None:
        self._current = QColor(color)
        self._own_style = f"{self._selector} {{ background-color: {color.name()}; }}"
        self._button.setStyleSheet(self._own_style)

    def _restore_style(self) -> None:
        if self._own_style and self._button.styleSheet() == self._own_style:
            self._button.setStyleSheet("")
        self._own_style = ""

    def _animate(self, duration: int) -> None:
        self.animation.stop()
        self.animation.setDuration(duration)
        self.animation.setStartValue(self._current)
        self.animation.setEndValue(self._target())
        self.animation.start()

    def set_hovered(self, hovered: bool) -> None:
        self._hovered = hovered
        if self._button.isEnabled() and not self._button.isDown():
            self._animate(140)

    def _press(self) -> None:
        self.animation.stop()
        self._show_color(self._target(pressed=True))

    def _release(self) -> None:
        self._animate(280)

    def stop(self) -> None:
        self.animation.stop()
        self._restore_style()
        self._current = self._target()


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
            feedback._button.pressed.disconnect(feedback._press)
            feedback._button.released.disconnect(feedback._release)
            feedback.setParent(None)
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
        elif kind in (QEvent.Enter, QEvent.Leave, QEvent.Hide, QEvent.EnabledChange):
            feedback = self._feedbacks.get(id(watched))
            if feedback is not None:
                if kind in (QEvent.Hide, QEvent.EnabledChange):
                    feedback.stop()
                else:
                    feedback.set_hovered(kind == QEvent.Enter)
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
        if isinstance(widget, (QPushButton, QToolButton)) and id(widget) not in self._feedbacks:
            # Preserve any deliberate widget-local styling owned by another component.
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
    """Restore shared styles before a palette change."""
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
