"""A framed checkbox whose entire visible surface is clickable."""

from PyQt5.QtWidgets import QCheckBox


class ChoiceCheckBox(QCheckBox):
    def hitButton(self, position):
        return self.rect().contains(position)
