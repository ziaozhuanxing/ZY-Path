"""Shared colors, fonts, and application styling."""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QScrollArea

PRIMARY = "#2C5282"
ACCENT = "#3182CE"
SUCCESS = "#38A169"
ERROR = "#E53E3E"

UI_FONT = QFont("Segoe UI", 10)
MONO_FONT = QFont("Consolas", 9)

LIGHT_COLORS = {
    "background": "#F7FAFC",
    "surface": "#FFFFFF",
    "text": "#1A202C",
    "muted": "#718096",
    "border": "#CBD5E0",
    "soft": "#EDF2F7",
    "selection": "#BEE3F8",
    "grid": "#E2E8F0",
}
DARK_COLORS = {
    "background": "#182333",
    "surface": "#243247",
    "text": "#F7FAFC",
    "muted": "#B8C4D4",
    "border": "#4A5B73",
    "soft": "#30415A",
    "selection": "#2C5282",
    "grid": "#52647C",
}


def apply_theme(app: QApplication, theme_name: str = "Light") -> None:
    """Apply the selected theme to all current and future application widgets."""
    colors = DARK_COLORS if theme_name.casefold() == "dark" else LIGHT_COLORS
    app.setProperty("zyTheme", "Dark" if theme_name.casefold() == "dark" else "Light")
    app.setFont(UI_FONT)
    app.setStyleSheet(
        f"""
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
            font-family: "Segoe UI";
        }}
        QLabel, QCheckBox, QRadioButton, QGroupBox {{ background: transparent; }}
        QAbstractScrollArea {{ background-color: {colors['surface']}; }}
        QScrollArea[panelScroll="true"] {{ background: {colors['surface']}; border: none; }}
        QWidget[panelSurface="true"] {{ background-color: {colors['surface']}; border: none; }}
        QAbstractScrollArea::corner {{ background: {colors['soft']}; border: none; }}
        QScrollBar {{ background: {colors['soft']}; border: none; }}
        QScrollBar:vertical {{ width: 12px; margin: 12px 0; }}
        QScrollBar:horizontal {{ height: 12px; margin: 0 12px; }}
        QScrollBar::groove, QScrollBar::add-page, QScrollBar::sub-page {{ background: {colors['soft']}; border: none; }}
        QScrollBar::handle {{ background: {colors['muted']}; border-radius: 4px; }}
        QScrollBar::handle:vertical {{ min-height: 24px; }}
        QScrollBar::handle:horizontal {{ min-width: 24px; }}
        QScrollBar::handle:hover {{ background: {ACCENT}; }}
        QScrollBar::handle:pressed {{ background: {PRIMARY}; }}
        QScrollBar::handle:disabled {{ background: {colors['border']}; }}
        QScrollBar::add-line, QScrollBar::sub-line {{ background: {colors['soft']}; border: none; }}
        QScrollBar::add-line:hover, QScrollBar::sub-line:hover {{ background: {colors['selection']}; }}
        QScrollBar::add-line:pressed, QScrollBar::sub-line:pressed {{ background: {colors['border']}; }}
        QScrollBar::add-line:disabled, QScrollBar::sub-line:disabled {{ background: {colors['background']}; }}
        QScrollBar::sub-line:vertical {{ height: 12px; subcontrol-origin: margin; subcontrol-position: top; }}
        QScrollBar::add-line:vertical {{ height: 12px; subcontrol-origin: margin; subcontrol-position: bottom; }}
        QScrollBar::sub-line:horizontal {{ width: 12px; subcontrol-origin: margin; subcontrol-position: left; }}
        QScrollBar::add-line:horizontal {{ width: 12px; subcontrol-origin: margin; subcontrol-position: right; }}
        #InferencePanel, #ActionPanel {{ background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 4px; }}
        #ResultPanel, #HistoryPanel {{ background-color: {colors['surface']}; border: none; }}
        QWidget#titleBar {{ background-color: {PRIMARY}; }}
        QLabel#titleText {{ border: none; color: white; }}
        QLabel#subtitleText {{ border: none; color: #BEE3F8; }}
        QToolButton#settingsButton {{ background: transparent; border: 1px solid transparent; border-radius: 19px; padding: 5px; }}
        QToolButton#settingsButton:hover {{ background: rgba(255, 255, 255, 35); border-color: rgba(255, 255, 255, 110); }}
        QToolButton#settingsButton:pressed {{ background: rgba(0, 0, 0, 45); }}
        QToolButton#settingsButton:focus {{ border: 2px solid #FFFFFF; }}
        QLabel#placeholderLabel {{ border: none; }}
        QLabel#sourceImageLabel, QGraphicsView {{ background-color: {colors['background']}; border: 1px solid {colors['border']}; color: {colors['muted']}; }}
        QLabel#predictedClassLabel {{ font-size: 14pt; font-weight: bold; }}
        QLabel#confidenceLabel {{ font-family: Consolas; font-size: 10pt; }}
        QLabel#actionSectionTitle {{ font-size: 12pt; font-weight: bold; }}
        QLabel#legendColorSwatch {{ border: 1px solid {colors['border']}; }}
        QLineEdit#historySearchInput, QDateEdit, QComboBox, QListWidget, QTextBrowser {{ background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 3px; padding: 5px 7px; selection-background-color: {colors['selection']}; selection-color: {colors['text']}; }}
        QTableWidget#historyTable {{ background-color: {colors['surface']}; alternate-background-color: {colors['background']}; gridline-color: {colors['grid']}; border: 1px solid {colors['border']}; selection-background-color: {colors['selection']}; selection-color: {colors['text']}; }}
        QTableWidget[displayOnly="true"] {{ background-color: {colors['surface']}; alternate-background-color: {colors['background']}; gridline-color: {colors['grid']}; border: 1px solid {colors['border']}; outline: none; }}
        QHeaderView::section {{ background-color: {colors['soft']}; color: {colors['text']}; font-weight: bold; padding: 7px; border: none; border-bottom: 1px solid {colors['border']}; }}
        QTableCornerButton::section {{ background: {colors['soft']}; border: none; border-bottom: 1px solid {colors['border']}; }}
        QLabel#historyEmptyLabel {{ background: transparent; color: {colors['muted']}; }}
        QLabel#historyValidationLabel {{ background: transparent; color: {ERROR}; }}
        QSplitter::handle:horizontal, QSplitter::handle:vertical {{ background-color: {colors['border']}; }}
        QSplitter::handle:hover {{ background-color: {ACCENT}; }}
        QPushButton {{ background-color: {PRIMARY}; color: white; border: none; border-radius: 3px; padding: 7px 12px; }}
        QPushButton:hover:!disabled {{ background-color: {ACCENT}; }}
        QPushButton:disabled {{ background-color: {colors['border']}; color: {colors['muted']}; }}
        QPushButton:focus, QCheckBox:focus, QRadioButton:focus, QListWidget:focus, QLineEdit:focus {{ outline: none; border: 2px solid {ACCENT}; }}
        QPushButton#deleteSelectedButton {{ background-color: {ERROR}; color: #FFFFFF; font-weight: bold; }}
        QPushButton#deleteSelectedButton:hover:!disabled {{ background-color: #C53030; }}
        QPushButton#deleteSelectedButton:disabled {{ background-color: #FEB2B2; color: #FFFFFF; }}
        QPushButton#runInferenceButton {{ background-color: {ACCENT}; font-weight: bold; padding: 9px 12px; }}
        QPushButton#runInferenceButton:hover {{ background-color: {PRIMARY}; }}
        QTabWidget::pane {{ border: 1px solid {colors['border']}; background-color: {colors['surface']}; }}
        QTabBar::tab {{ background-color: {colors['soft']}; color: {colors['text']}; padding: 8px 18px; border: 1px solid {colors['border']}; }}
        QTabBar::tab:selected {{ background-color: {PRIMARY}; color: white; }}
        QTabBar::tab:hover:!selected {{ background-color: #EBF8FF; }}
        QStatusBar QLabel {{ margin-left: 8px; }}
        """
    )


def style_panel_scroll(scroll: QScrollArea) -> None:
    """Make borderless scrolling content share its panel's themed surface."""
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setProperty("panelScroll", True)
    scroll.viewport().setProperty("panelSurface", True)
    if scroll.widget() is not None:
        scroll.widget().setProperty("panelSurface", True)
    # Some contents (notably splitters with local QSS) were polished before
    # reparenting. Dynamic properties need an explicit style refresh then.
    for widget in (scroll, scroll.viewport(), scroll.widget()):
        if widget is not None:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()


def splitter_style(theme_name: str = "Light") -> str:
    """Return splitter handle styling for the selected theme."""
    colors = DARK_COLORS if theme_name.casefold() == "dark" else LIGHT_COLORS
    return (
        f"QSplitter::handle {{ background-color: {colors['border']}; }}"
        f"QSplitter::handle:hover {{ background-color: {ACCENT}; }}"
    )
