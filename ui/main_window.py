"""Main window layout for the ZY-Path application."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QSplitter,
	QTabWidget,
	QVBoxLayout,
	QWidget,
)

from ui.action_panel import ActionPanel
from ui.history_panel import HistoryPanel
from ui.inference_panel import InferencePanel
from ui.result_panel import ResultPanel


class MainWindow(QMainWindow):
	"""Show the three-region application shell."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setWindowTitle("ZY-Path")
		self.setMinimumSize(1366, 768)

		central_widget = QWidget(self)
		central_layout = QVBoxLayout(central_widget)
		central_layout.setContentsMargins(0, 0, 0, 0)
		central_layout.setSpacing(0)

		header = QWidget(central_widget)
		header.setObjectName("titleBar")
		header.setAttribute(Qt.WA_StyledBackground, True)
		header.setFixedHeight(88)
		header_layout = QVBoxLayout(header)
		header_layout.setContentsMargins(24, 10, 24, 10)
		header_layout.setSpacing(2)
		title = QLabel("ZY-Path", header)
		title.setObjectName("titleText")
		subtitle = QLabel("Histopathology image analysis", header)
		subtitle.setObjectName("subtitleText")
		header_layout.addWidget(title)
		header_layout.addWidget(subtitle)
		header_layout.addStretch()
		central_layout.addWidget(header)

		self.splitter = QSplitter(Qt.Horizontal, central_widget)
		self.splitter.setHandleWidth(8)
		self.inference_panel = InferencePanel(self.splitter)
		self.inference_panel.setFixedWidth(280)

		self.tabs = QTabWidget(self.splitter)
		self.tabs.setMinimumWidth(500)
		self.tabs.setObjectName("tabRegion")
		self.result_panel = ResultPanel(self.tabs)
		self.history_panel = HistoryPanel(self.tabs)
		self.tabs.addTab(self.result_panel, "Inference")
		self.tabs.addTab(self.history_panel, "History")

		self.action_panel = ActionPanel(self.splitter)
		self.action_panel.setFixedWidth(240)

		self.splitter.addWidget(self.inference_panel)
		self.splitter.addWidget(self.tabs)
		self.splitter.addWidget(self.action_panel)
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)
		self.splitter.setStretchFactor(2, 0)
		central_layout.addWidget(self.splitter, 1)

		self.setCentralWidget(central_widget)
		status_bar = self.statusBar()
		status_bar.showMessage("Ready")
		self.inference_panel.run_requested.connect(self._show_run_requested)

	def _show_run_requested(
		self, model_path: str, use_builtin: bool, image_path: str, task_type: str
	) -> None:
		"""Show that inference is not connected yet."""
		self.statusBar().showMessage("Run requested (inference not connected yet)")
