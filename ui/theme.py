"""Shared colors, fonts, and application styling."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QScrollArea

from ui.interactions import install_interactions, stop_feedback
from utils.paths import resource_path

PRIMARY = "#254F96"
ACCENT = "#2569C3"
SPLITTER_HOVER = "#3182CE"
SUCCESS = "#38A169"
ERROR = "#E53E3E"

UI_FONT = QFont("Segoe UI", 10)
MONO_FONT = QFont("Consolas", 9)

LIGHT_COLORS = {
    "background": "#EFF4FB",
    "surface": "#FFFFFF",
    "text": "#172842",
    "muted": "#536781",
    "border": "#CBD5E0",
    "soft": "#E8F0FB",
    "selection": "#CEDFFE",
    "choice_border": "#839ABC",
    "focus": "#1C57B0",
    "pulse": "#1688A7",
    "grid": "#E2E8F0",
    "progress_start": "#7BABF1",
    "progress_end": "#6BCDCA",
}
DARK_COLORS = {
    "background": "#0C1525",
    "surface": "#152238",
    "text": "#EAF2FF",
    "muted": "#B8C4D4",
    "border": "#374C6A",
    "soft": "#22334F",
    "selection": "#294B7A",
    "choice_border": "#6880A5",
    "focus": "#79C7FF",
    "pulse": "#74E6F4",
    "grid": "#52647C",
    "progress_start": "#245AC0",
    "progress_end": "#0E687D",
}


def _theme_palette(colors: dict[str, str]) -> QPalette:
    """Give native controls and popup states the same colors as styled widgets."""
    palette = QPalette()
    roles = {
        QPalette.Window: colors["background"], QPalette.WindowText: colors["text"],
        QPalette.Base: colors["surface"], QPalette.AlternateBase: colors["soft"],
        QPalette.Text: colors["text"], QPalette.Button: PRIMARY,
        QPalette.ButtonText: "#FFFFFF", QPalette.Highlight: colors["selection"],
        QPalette.HighlightedText: colors["text"], QPalette.PlaceholderText: colors["muted"],
        QPalette.ToolTipBase: colors["surface"], QPalette.ToolTipText: colors["text"],
        QPalette.Link: ACCENT, QPalette.Light: colors["border"],
        QPalette.Midlight: colors["soft"], QPalette.Mid: colors["border"],
        QPalette.Dark: colors["grid"], QPalette.Shadow: colors["background"],
    }
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        for role, color in roles.items():
            palette.setColor(group, role, QColor(color))
    for role in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
        palette.setColor(QPalette.Disabled, role, QColor(colors["muted"]))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor(colors["soft"]))
    return palette


def apply_theme(app: QApplication, theme_name: str = "Light") -> None:
    """Apply the selected theme to all current and future application widgets."""
    colors = DARK_COLORS if theme_name.casefold() == "dark" else LIGHT_COLORS
    stop_feedback(app)
    if not app.property("zyFusionStyle"):
        app.setStyle("Fusion")
        app.setProperty("zyFusionStyle", True)
    # Keep the system file picker (including Windows thumbnail browsing).
    # Clear the previous theme policy too when changing themes in this process.
    app.setAttribute(Qt.AA_DontUseNativeDialogs, False)
    app.setProperty("zyTheme", "Dark" if theme_name.casefold() == "dark" else "Light")
    app.setFont(UI_FONT)
    app.setPalette(_theme_palette(colors))
    up_arrow = resource_path("assets/spin-up.svg").as_posix()
    down_arrow = resource_path("assets/spin-down.svg").as_posix()
    check_mark = resource_path("assets/choice-check.svg").as_posix()
    radio_dot = resource_path("assets/choice-radio.svg").as_posix()
    partial_mark = resource_path("assets/choice-partial.svg").as_posix()
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
        QScrollBar:vertical {{ width: 9px; margin: 12px 0; }}
        QScrollBar:horizontal {{ height: 12px; margin: 0 12px; }}
        QTableWidget#historyTable QScrollBar:horizontal {{ height: 9px; }}
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
        #InferencePanel, #ActionPanel {{ background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 8px; }}
        #ResultPanel, #HistoryPanel {{ background-color: {colors['surface']}; border: none; }}
        QWidget#titleBar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #111F38, stop:0.55 #234C90, stop:1 #14606E);
            border-bottom: 2px solid #36B7CE;
        }}
        QLabel#titleText {{ border: none; color: white; }}
        QLabel#subtitleText {{ border: none; color: #BEE3F8; }}
        QToolButton#settingsButton {{ background: rgba(13, 30, 52, 120); border: 1px solid rgba(179, 222, 246, 130); border-radius: 19px; padding: 5px; }}
        QToolButton#settingsButton:hover {{ background: rgba(255, 255, 255, 35); border-color: rgba(255, 255, 255, 110); }}
        QToolButton#settingsButton:pressed {{ background: rgba(0, 0, 0, 45); }}
        QToolButton#settingsButton:focus {{ border: 2px solid #FFFFFF; }}
        QLabel#placeholderLabel {{ border: none; }}
        QLabel#sourceImageLabel, QGraphicsView {{ background-color: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 7px; color: {colors['muted']}; }}
        QLabel#predictedClassLabel {{ font-size: 14pt; font-weight: bold; }}
        QLabel#confidenceLabel {{ font-family: Consolas; font-size: 10pt; }}
        QLabel#actionSectionTitle {{ font-size: 12pt; font-weight: bold; }}
        QLabel#legendColorSwatch {{ border: 1px solid {colors['border']}; }}
        QLineEdit, QDateEdit, QComboBox, QListWidget, QTextBrowser {{ background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 6px; padding: 5px 7px; selection-background-color: {colors['selection']}; selection-color: {colors['text']}; }}
        QTableWidget#historyTable {{ background-color: {colors['surface']}; alternate-background-color: {colors['background']}; gridline-color: {colors['grid']}; border: 1px solid {colors['border']}; selection-background-color: {colors['selection']}; selection-color: {colors['text']}; }}
        QTableWidget[displayOnly="true"] {{ background-color: {colors['surface']}; alternate-background-color: {colors['background']}; gridline-color: {colors['grid']}; border: 1px solid {colors['border']}; outline: none; }}
        QHeaderView::section {{ background-color: {colors['soft']}; color: {colors['text']}; font-weight: bold; padding: 7px; border: none; border-bottom: 1px solid {colors['border']}; }}
        QTableCornerButton::section {{ background: {colors['soft']}; border: none; border-bottom: 1px solid {colors['border']}; }}
        QLabel#historyEmptyLabel {{ background: transparent; color: {colors['muted']}; }}
        QLabel#historyValidationLabel {{ background: transparent; color: {ERROR}; }}
        QSplitter::handle:horizontal, QSplitter::handle:vertical {{ background-color: {colors['border']}; }}
        QSplitter::handle:hover {{ background-color: {SPLITTER_HOVER}; }}
        QPushButton {{ background-color: {PRIMARY}; color: white; border: 2px solid transparent; border-radius: 8px; padding: 7px 12px; }}
        QPushButton:hover:!disabled {{ background-color: {ACCENT}; }}
        QPushButton:disabled {{ background-color: {colors['border']}; color: {colors['muted']}; }}
        QPushButton:focus {{ outline: none; border-color: #87CFFF; }}
        QPushButton[secondary="true"] {{ background-color: {colors['soft']}; color: {colors['text']}; border: 1px solid {colors['border']}; }}
        QPushButton[secondary="true"]:hover:!disabled {{ background-color: {colors['selection']}; }}
        QGroupBox {{
            border: 1px solid {colors['border']}; border-radius: 8px; margin-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin; subcontrol-position: top left; left: 8px;
            background: {colors['surface']}; padding: 0 5px; font-weight: 600;
        }}
        QLabel#scaleModeBadge {{
            background: {colors['selection']}; color: {colors['text']}; border-radius: 5px;
            padding: 4px 7px; font-weight: 600;
        }}
        QLabel#samplingPreviewSummary {{ font-weight: 600; }}
        QLabel#runPlanSummary {{
            background: {colors['soft']}; color: {colors['text']};
            border: 1px solid {colors['border']}; border-radius: 7px; padding: 6px 8px;
        }}
        QCheckBox, QRadioButton {{
            outline: none; spacing: 7px; padding: 4px 6px;
            border: 1px solid {colors['choice_border']}; border-radius: 7px;
            background: {colors['soft']};
        }}
        QCheckBox:checked, QRadioButton:checked {{
            background: {colors['selection']}; border-color: {ACCENT};
        }}
        QCheckBox:hover:enabled, QRadioButton:hover:enabled,
        QCheckBox:pressed:enabled, QRadioButton:pressed:enabled {{
            background: {colors['selection']}; border-color: {colors['focus']};
        }}
        QCheckBox:pressed:enabled, QRadioButton:pressed:enabled {{
            background: {colors['surface']};
        }}
        QCheckBox:disabled, QRadioButton:disabled {{
            background: {colors['background']}; border-color: {colors['border']}; color: {colors['muted']};
        }}
        QCheckBox:focus, QRadioButton:focus, QCheckBox[keyboardFocus="true"],
        QListWidget:focus, QLineEdit:focus {{
            outline: none; border-color: {colors['focus']};
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 13px; height: 13px; background: {colors['surface']};
            border: 1px solid {colors['choice_border']};
        }}
        QCheckBox::indicator {{ border-radius: 4px; }}
        QRadioButton::indicator {{ border-radius: 7px; }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background: {ACCENT}; border-color: {ACCENT};
        }}
        QCheckBox::indicator:checked {{ image: url("{check_mark}"); }}
        QRadioButton::indicator:checked {{ image: url("{radio_dot}"); }}
        QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
            background: {colors['border']}; border-color: {colors['choice_border']};
        }}
        QCheckBox::indicator:indeterminate {{
            image: url("{partial_mark}"); background: {ACCENT}; border-color: {ACCENT};
        }}
        QDoubleSpinBox[imageScaleInput="true"]:disabled {{ color: {colors['muted']}; background-color: {colors['soft']}; }}
        QPushButton#deleteSelectedButton {{ background-color: {ERROR}; color: #FFFFFF; font-weight: bold; }}
        QPushButton#deleteSelectedButton:hover:!disabled {{ background-color: #C53030; }}
        QPushButton#deleteSelectedButton:disabled {{ background-color: #FEB2B2; color: #FFFFFF; }}
        QPushButton#runInferenceButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #245AC0, stop:1 #0E687D);
            font-weight: bold; padding: 9px 12px;
        }}
        QPushButton#runInferenceButton:hover:enabled {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2866D1, stop:1 #117287);
        }}
        QTabWidget::pane {{ border: 1px solid {colors['border']}; background-color: {colors['surface']}; }}
        QTabBar::tab {{
            background: {colors['soft']}; color: {colors['text']}; padding: 8px 16px;
            border: 1px solid {colors['choice_border']}; border-top-left-radius: 7px;
            border-top-right-radius: 7px; margin-right: 3px;
        }}
        QTabBar::tab:selected {{ background-color: {PRIMARY}; color: white; border-bottom-color: #55D1E7; }}
        QTabBar::tab:focus {{ border-color: {colors['focus']}; }}
        QTabBar::tab:hover:!selected {{ background-color: {colors['selection']}; }}
        QStatusBar {{ background: {colors['surface']}; border-top: 1px solid {colors['border']}; }}
        QStatusBar::item {{ border: none; }}
        QStatusBar QLabel {{ margin-left: 8px; }}
        QProgressBar {{
            background: {colors['background']}; border: 1px solid {colors['border']};
            border-radius: 6px; text-align: center;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors['progress_start']}, stop:1 {colors['progress_end']});
            border-radius: 5px;
        }}
        QListWidget#settingsNavigation::item {{
            border: 1px solid {colors['border']}; border-radius: 5px; padding-left: 6px;
            background: {colors['soft']}; color: {colors['text']};
        }}
        QListWidget#settingsNavigation::item:selected, QListWidget#settingsNavigation::item:hover {{
            background: {colors['selection']}; border-color: {colors['focus']}; color: {colors['text']};
        }}
        QDialog, QMessageBox, QFileDialog {{ background-color: {colors['surface']}; }}
        QDialogButtonBox {{ background: transparent; }}
        QPushButton:default {{ border-color: {ACCENT}; }}
        QPushButton:checked {{ background-color: {ACCENT}; color: #FFFFFF; }}
        QPushButton:pressed:enabled {{
            background-color: #23456E; color: #FFFFFF; border-color: #63B3ED;
            padding-top: 8px; padding-bottom: 6px;
        }}
        QPushButton[secondary="true"]:checked,
        QPushButton[secondary="true"]:pressed:enabled {{
            background-color: {colors['selection']}; color: {colors['text']}; border-color: {ACCENT};
        }}
        QPushButton#runInferenceButton:pressed:enabled {{
            background-color: #23456E; color: #FFFFFF; padding-top: 10px; padding-bottom: 8px;
        }}
        QPushButton#deleteSelectedButton:pressed:enabled {{ background-color: #9B2C2C; color: #FFFFFF; }}
        QPushButton:disabled, QPushButton[secondary="true"]:disabled,
        QPushButton#runInferenceButton:disabled, QPushButton#deleteSelectedButton:disabled {{
            background-color: {colors['soft']}; color: {colors['muted']};
        }}
        QToolButton {{
            background-color: {colors['soft']}; color: {colors['text']};
            border: 1px solid {colors['choice_border']}; border-radius: 7px; padding: 4px;
        }}
        QToolButton:hover:enabled, QToolButton:checked {{ background-color: {colors['selection']}; border-color: {colors['focus']}; }}
        QToolButton:pressed:enabled {{ background-color: {PRIMARY}; color: #FFFFFF; border-color: #63B3ED; }}
        QToolButton:focus {{ border-color: {ACCENT}; }}
        QToolButton:disabled {{ background-color: {colors['soft']}; color: {colors['muted']}; }}
        QAbstractSpinBox {{ background-color: {colors['surface']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 6px; }}
        QAbstractSpinBox {{ padding-right: 22px; }}
        QComboBox, QLineEdit, QAbstractSpinBox {{ border-color: {colors['choice_border']}; }}
        QComboBox {{ padding-right: 27px; }}
        QComboBox::drop-down {{
            subcontrol-origin: padding; subcontrol-position: top right; width: 23px;
            background: {colors['soft']}; border-left: 1px solid {colors['choice_border']};
            border-top-right-radius: 6px; border-bottom-right-radius: 6px;
        }}
        QComboBox::drop-down:hover:enabled, QComboBox::drop-down:on {{
            background: {colors['selection']};
        }}
        QComboBox::down-arrow {{ image: url("{down_arrow}"); width: 10px; height: 7px; }}
        QAbstractSpinBox::up-button {{ subcontrol-origin: border; subcontrol-position: top right; width: 20px; background: {colors['soft']}; border: none; border-left: 1px solid {colors['border']}; border-bottom: 1px solid {colors['border']}; }}
        QAbstractSpinBox::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; background: {colors['soft']}; border: none; border-left: 1px solid {colors['border']}; }}
        QAbstractSpinBox::up-button:hover:enabled, QAbstractSpinBox::down-button:hover:enabled {{ background: {colors['selection']}; }}
        QAbstractSpinBox::up-arrow {{ image: url("{up_arrow}"); width: 10px; height: 7px; }}
        QAbstractSpinBox::down-arrow {{ image: url("{down_arrow}"); width: 10px; height: 7px; }}
        QLineEdit:hover:enabled, QAbstractSpinBox:hover:enabled, QComboBox:hover:enabled {{ border-color: {ACCENT}; }}
        QAbstractSpinBox:focus, QComboBox:focus, QComboBox:on {{
            background-color: {colors['surface']}; color: {colors['text']}; border-color: {ACCENT};
        }}
        QComboBox QLineEdit, QAbstractSpinBox QLineEdit {{ background: transparent; border: none; padding: 0; }}
        QLineEdit:disabled, QAbstractSpinBox:disabled, QComboBox:disabled {{ background-color: {colors['soft']}; color: {colors['muted']}; }}
        QComboBox QAbstractItemView, QFileDialog QAbstractItemView {{
            background-color: {colors['surface']}; color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['selection']}; selection-color: {colors['text']};
        }}
        QComboBox QAbstractItemView::item:selected, QFileDialog QAbstractItemView::item:selected {{
            background-color: {colors['selection']}; color: {colors['text']};
        }}
        QMenu, QMenuBar {{ background-color: {colors['surface']}; color: {colors['text']}; }}
        QMenu {{ border: 1px solid {colors['border']}; padding: 4px; }}
        QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
        QMenu::item:selected, QMenuBar::item:selected {{ background-color: {colors['selection']}; color: {colors['text']}; }}
        QMenu::separator {{ height: 1px; background-color: {colors['border']}; margin: 4px; }}
        QToolTip {{ background-color: {colors['surface']}; color: {colors['text']}; border: 1px solid {colors['border']}; padding: 5px; }}
        """
    )
    install_interactions(app, colors)


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
        f"QSplitter::handle:hover {{ background-color: {SPLITTER_HOVER}; }}"
    )
