"""Combo boxes require an explicit choice rather than a stray scroll gesture."""
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QAbstractScrollArea, QComboBox


class ExplicitComboBox(QComboBox):
    """Retain popup/keyboard input and route closed-combo wheels to the page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
            return
        parent = self.parentWidget()
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
