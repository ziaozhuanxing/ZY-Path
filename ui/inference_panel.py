"""Placeholder for inference controls."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class InferencePanel(QWidget):
	"""Display the inference panel placeholder."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setObjectName("InferencePanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		layout = QVBoxLayout(self)
		label = QLabel("InferencePanel (placeholder)", self)
		label.setObjectName("placeholderLabel")
		label.setAlignment(Qt.AlignCenter)
		label.setWordWrap(True)
		layout.addWidget(label)
