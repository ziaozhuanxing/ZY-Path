"""Numeric preferences accept typing and arrow input, never wheel changes."""
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QSpinBox

from ui.explicit_combo_box import forward_wheel_to_page


class ExplicitSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.lineEdit() and event.type() == QEvent.Wheel:
            forward_wheel_to_page(self, event)
            return True
        return super().eventFilter(watched, event)

    def wheelEvent(self, event):
        forward_wheel_to_page(self, event)
