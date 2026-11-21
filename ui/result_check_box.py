"""Compact result controls with matching visual and mouse hit areas."""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from ui.choice_check_box import ChoiceCheckBox


class ResultCheckBox(ChoiceCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setProperty("keyboardFocus", False)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

    def _keyboard_focus(self, visible):
        if self.property("keyboardFocus") != visible:
            self.setProperty("keyboardFocus", visible)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

    def focusInEvent(self, event):
        self._keyboard_focus(event.reason() in (
            Qt.TabFocusReason, Qt.BacktabFocusReason, Qt.ShortcutFocusReason))
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._keyboard_focus(False)
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        self._keyboard_focus(False)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Space, Qt.Key_Select):
            self._keyboard_focus(True)
        super().keyPressEvent(event)
