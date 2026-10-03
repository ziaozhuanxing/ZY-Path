"""Shared colors, fonts, and basic application styling."""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

PRIMARY = "#2C5282"
ACCENT = "#3182CE"
SUCCESS = "#38A169"
ERROR = "#E53E3E"
BACKGROUND = "#F7FAFC"
TEXT = "#1A202C"

UI_FONT = QFont("Segoe UI", 10)
MONO_FONT = QFont("Consolas", 9)


def apply_theme(app: QApplication) -> None:
	"""Apply the shared application font and basic widget styles."""
	app.setFont(UI_FONT)
	app.setStyleSheet(
		f"""
		QWidget {{
			background-color: {BACKGROUND};
			color: {TEXT};
			font-family: "Segoe UI";
			font-size: 10pt;
		}}
		#InferencePanel, #ActionPanel {{
			background-color: #FFFFFF;
			border: 1px solid #CBD5E0;
			border-radius: 4px;
		}}
		#ResultPanel, #HistoryPanel {{
			background-color: #FFFFFF;
			border: none;
		}}
		QWidget#titleBar {{ background-color: {PRIMARY}; }}
		QLabel#titleText {{
			background: transparent;
			border: none;
			color: white;
			font-size: 20pt;
			font-weight: bold;
		}}
		QLabel#subtitleText {{
			background: transparent;
			border: none;
			color: #BEE3F8;
			font-size: 10pt;
		}}
		QLabel#placeholderLabel {{
			background: transparent;
			border: none;
		}}
		QSplitter::handle:horizontal {{
			width: 8px;
			background-color: {BACKGROUND};
		}}
		QPushButton {{
			background-color: {PRIMARY};
			color: white;
			border: none;
			border-radius: 3px;
			padding: 7px 12px;
		}}
		QPushButton:hover {{ background-color: {ACCENT}; }}
		QPushButton:disabled {{ background-color: #A0AEC0; }}
		QTabWidget::pane {{
			border: 1px solid #CBD5E0;
			background-color: #FFFFFF;
		}}
		QTabBar::tab {{
			background-color: #E2E8F0;
			color: {TEXT};
			padding: 8px 18px;
			border: 1px solid #CBD5E0;
		}}
		QTabBar::tab:selected {{
			background-color: {PRIMARY};
			color: white;
		}}
		QTabBar::tab:hover:!selected {{ background-color: #EBF8FF; }}
		QStatusBar QLabel {{ margin-left: 8px; }}
		"""
	)
