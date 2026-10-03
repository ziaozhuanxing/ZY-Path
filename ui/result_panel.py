"""Placeholder for inference results."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class ResultPanel(QWidget):
	"""Display the result panel placeholder."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("ResultPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		layout = QVBoxLayout(self)
		label = QLabel("ResultPanel (placeholder)", self)
		label.setObjectName("placeholderLabel")
		label.setAlignment(Qt.AlignCenter)
		label.setWordWrap(True)
		layout.addWidget(label)
