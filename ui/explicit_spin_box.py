"""Numeric preferences accept typing and arrow input, never wheel changes."""
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QSpinBox, QToolButton

from ui.explicit_combo_box import forward_wheel_to_page


def square_dimensions_button(parent, width, height):
    button = QToolButton(parent)
    button.setText("Square")
    button.setToolTip("Copy the width to the height once. Both dimensions remain editable.")
    button.setAccessibleName("Set tile height equal to width")
    button.clicked.connect(lambda: height.setValue(width.value()))
    return button


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
