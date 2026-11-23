"""Combo boxes require an explicit choice rather than a stray scroll gesture."""
from PyQt5.QtCore import QEasingCurve, QPoint, QPointF, QPropertyAnimation, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QAbstractScrollArea, QComboBox, QGraphicsOpacityEffect, QStyle


def forward_wheel_to_page(widget, event):
    """Route a control's wheel once to its enclosing scrollable page."""
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QAbstractScrollArea):
            viewport = parent.viewport()
            forwarded = QWheelEvent(
                QPointF(viewport.mapFromGlobal(event.globalPos())), event.globalPosF(),
                event.pixelDelta(), event.angleDelta(), event.buttons(), event.modifiers(),
                event.phase(), event.inverted(), event.source(),
            )
            QApplication.sendEvent(viewport, forwarded)
            # One route only: native parent propagation must not scroll twice.
            event.accept()
            return
        parent = parent.parentWidget()
    event.ignore()


class ExplicitComboBox(QComboBox):
    """Retain popup/keyboard input and route closed-combo wheels to the page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self._popup_fade = QPropertyAnimation(self)
        self._popup_fade.setPropertyName(b"opacity")
        self._popup_fade.setDuration(130)
        self._popup_fade.setStartValue(.72)
        self._popup_fade.setEndValue(1.0)
        self._popup_fade.setEasingCurve(QEasingCurve.OutCubic)
        self._popup_fade.finished.connect(self._stop_popup_fade)

    def showPopup(self):
        super().showPopup()
        view = self.view()
        if not view.isVisible():
            return
        popup = view.window()
        if popup.windowType() != Qt.Popup:
            return
        self._position_popup(popup, view)
        if not self.style().styleHint(QStyle.SH_Widget_Animation_Duration, None, self):
            return
        self._stop_popup_fade()
        effect = self._popup_fade.targetObject()
        if effect is None or effect.parent() is not popup:
            if popup.graphicsEffect() is not None:
                return
            effect = QGraphicsOpacityEffect(popup)
            popup.setGraphicsEffect(effect)
            self._popup_fade.setTargetObject(effect)
        # Keep the anchored geometry and native hit targets during the fade.
        effect.setOpacity(.72)
        effect.setEnabled(True)
        self._popup_fade.start()

    def _position_popup(self, popup, view):
        area = self.screen().availableGeometry()
        top = self.mapToGlobal(QPoint()).y()
        below_top = max(top + self.height(), area.top())
        above_bottom = min(top, area.bottom() + 1)
        below = max(0, area.bottom() + 1 - below_top)
        above = max(0, above_bottom - area.top())
        row = max(view.sizeHintForRow(max(0, self.currentIndex())), self.fontMetrics().height())
        one_row = row + popup.height() - view.viewport().height()
        # Prefer a scrollable list below. Use the space above when the
        # control is too close to the bottom to show a complete choice.
        open_below = below >= min(one_row, popup.height()) or below >= above
        height = max(1, min(popup.height(), below if open_below else above))
        width = min(popup.width(), area.width())
        left = max(area.left(), min(popup.x(), area.right() + 1 - width))
        popup.setGeometry(left, below_top if open_below else above_bottom - height, width, height)
        if view.currentIndex().isValid():
            view.scrollTo(view.currentIndex())

    def hidePopup(self):
        self._stop_popup_fade()
        super().hidePopup()

    def _stop_popup_fade(self):
        self._popup_fade.stop()
        effect = self._popup_fade.targetObject()
        if effect is not None:
            effect.setEnabled(False)

    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
            return
        forward_wheel_to_page(self, event)
