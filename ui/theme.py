"""Shared light/dark palettes and styling for every application window."""

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import QApplication

from ui.interactions import install_interactions
from utils.paths import resource_path

PRIMARY = "#2C5282"
ACCENT = "#3182CE"
SUCCESS = "#38A169"
ERROR = "#E53E3E"
BACKGROUND = "#F7FAFC"
TEXT = "#1A202C"

UI_FONT = QFont("Segoe UI", 10)
MONO_FONT = QFont("Consolas", 9)
THEME_SETTING = "appearance/theme"


def theme_colors(theme_name: str) -> dict[str, str]:
    """Return semantic colors without changing the application's blue identity."""
    if theme_name.casefold() == "dark":
        return dict(
            background="#151C27", surface="#1E2836", field="#182230",
            raised="#263548", border="#3D5067", text="#E6EDF5",
            muted="#A8B8CC", selection="#294D73", hover="#2D4057",
            disabled="#283646", disabled_text="#96A7BB", divider="#35475C",
            danger="#B92F3D", danger_hover="#CD3B49", danger_pressed="#962632",
        )
    return dict(
        background=BACKGROUND, surface="#FFFFFF", field="#FFFFFF",
        raised="#EDF2F7", border="#CBD5E0", text=TEXT,
        muted="#596B80", selection="#BEE3F8", hover="#EBF8FF",
        disabled="#E2E8F0", disabled_text="#617185", divider="#E2E8F0",
        danger="#C53030", danger_hover="#B72727", danger_pressed="#9B2525",
    )


def current_theme() -> str:
    """Read the active theme without creating settings or a second application."""
    app = QApplication.instance()
    return str(app.property("zyTheme") or "Light") if app else "Light"


def splitter_style(theme_name: str) -> str:
    """Keep both splitter orientations consistent with the active theme."""
    colors = theme_colors(theme_name)
    return f"""
        QSplitter::handle {{ background-color: {colors['border']}; border-radius: 3px; }}
        QSplitter::handle:hover, QSplitter::handle:pressed {{ background-color: {ACCENT}; }}
    """


def _palette(colors: dict[str, str]) -> QPalette:
    palette = QPalette()
    roles = {
        QPalette.Window: colors["background"], QPalette.WindowText: colors["text"],
        QPalette.Base: colors["field"], QPalette.AlternateBase: colors["raised"],
        QPalette.Text: colors["text"], QPalette.Button: PRIMARY,
        QPalette.ButtonText: "#FFFFFF", QPalette.Highlight: colors["selection"],
        QPalette.HighlightedText: colors["text"], QPalette.ToolTipBase: colors["surface"],
        QPalette.ToolTipText: colors["text"], QPalette.Link: ACCENT,
        QPalette.Light: colors["border"], QPalette.Midlight: colors["raised"],
        QPalette.Mid: colors["border"], QPalette.Dark: colors["divider"],
        QPalette.Shadow: colors["background"], QPalette.PlaceholderText: colors["muted"],
    }
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        for role, color in roles.items():
            palette.setColor(group, role, QColor(color))
    for role in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
        palette.setColor(QPalette.Disabled, role, QColor(colors["disabled_text"]))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor(colors["disabled"]))
    return palette


def apply_theme(app: QApplication, theme_name: str | None = None) -> None:
    """Apply the same palette, states, and interactions to main and popup windows."""
    if theme_name is None:
        theme_name = str(QSettings("ZY-Path", "ZY-Path").value(THEME_SETTING, "Light"))
    theme_name = "Dark" if theme_name.casefold() == "dark" else "Light"
    colors = theme_colors(theme_name)
    if not app.property("zyFusionStyle"):
        app.setStyle("Fusion")
        app.setProperty("zyFusionStyle", True)
    # Native OS dialogs cannot inherit the application's palette or animations.
    app.setAttribute(Qt.AA_DontUseNativeDialogs, True)
    app.setProperty("zyTheme", theme_name)
    app.setFont(UI_FONT)
    app.setPalette(_palette(colors))
    check = resource_path("assets/theme/check.svg").as_posix()
    down = resource_path("assets/theme/down.svg").as_posix()
    up = resource_path("assets/theme/up.svg").as_posix()
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {colors['background']}; color: {colors['text']};
            font-family: "Segoe UI";
            selection-background-color: {colors['selection']};
            selection-color: {colors['text']};
        }}
        QLabel, QCheckBox, QRadioButton, QGroupBox {{
            background: transparent;
        }}
        QWidget:disabled {{ color: {colors['disabled_text']}; }}
        QDialog, QMessageBox, QFileDialog {{ background-color: {colors['surface']}; }}
        QDialogButtonBox, QStackedWidget, QStackedWidget > QWidget {{ background-color: transparent; }}
        #InferencePanel, #ActionPanel {{
            background-color: {colors['surface']}; border: 1px solid {colors['border']};
            border-radius: 8px;
        }}
        #ResultPanel, #HistoryPanel {{ background-color: {colors['surface']}; border: none; }}
        QWidget#titleBar {{ background-color: {PRIMARY}; }}
        QLabel#titleText {{ color: white; border: none; }}
        QLabel#subtitleText {{ color: #BEE3F8; border: none; }}
        QLabel#predictedClassLabel {{ font-size: 14pt; font-weight: bold; }}
        QLabel#confidenceLabel, QLabel#zoomIndicator {{ font-family: Consolas; }}
        QLabel#actionSectionTitle, QLabel#settingsTitle {{ font-size: 12pt; font-weight: bold; }}
        QLabel#historyEmptyLabel, QLabel#emptyResultLabel, QLabel#settingsHint {{ color: {colors['muted']}; }}
        QLabel#historyValidationLabel {{ color: {ERROR}; }}
        QLabel#legendColorSwatch {{ border: 1px solid {colors['border']}; border-radius: 3px; }}
        QGroupBox {{
            border: 1px solid {colors['border']}; border-radius: 8px;
            margin-top: 12px; padding: 12px 8px 8px;
        }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
        QLineEdit, QAbstractSpinBox, QComboBox {{
            background-color: {colors['field']}; color: {colors['text']};
            border: 1px solid {colors['border']}; border-radius: 6px;
            padding: 7px 9px; min-height: 18px;
        }}
        QLineEdit:hover:enabled, QAbstractSpinBox:hover:enabled, QComboBox:hover:enabled {{ border-color: {ACCENT}; }}
        QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus, QComboBox:on {{
            background-color: {colors['field']}; border-color: {ACCENT}; color: {colors['text']};
        }}
        QLineEdit:disabled, QAbstractSpinBox:disabled, QComboBox:disabled {{
            background-color: {colors['disabled']}; color: {colors['disabled_text']};
        }}
        QComboBox, QAbstractSpinBox {{ padding-right: 26px; }}
        QComboBox::drop-down, QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
            width: 22px; border: none; background: transparent;
        }}
        QComboBox::down-arrow, QAbstractSpinBox::down-arrow {{ image: url("{down}"); width: 12px; height: 12px; }}
        QAbstractSpinBox::up-arrow {{ image: url("{up}"); width: 12px; height: 12px; }}
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']}; color: {colors['text']};
            border: 1px solid {colors['border']}; padding: 4px; outline: none;
        }}
        QCheckBox, QRadioButton {{ spacing: 8px; padding: 4px 0; }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px; height: 16px; background-color: {colors['field']};
            border: 1px solid {colors['border']}; border-radius: 4px;
        }}
        QRadioButton::indicator {{ border-radius: 9px; }}
        QCheckBox::indicator:hover:enabled, QRadioButton::indicator:hover:enabled {{ border-color: {ACCENT}; }}
        QCheckBox::indicator:checked, QCheckBox::indicator:indeterminate {{
            background-color: {ACCENT}; border-color: {ACCENT}; image: url("{check}");
        }}
        QRadioButton::indicator:checked {{
            width: 10px; height: 10px; border: 4px solid {ACCENT}; background-color: #FFFFFF;
        }}
        QCheckBox:focus, QRadioButton:focus {{ color: {ACCENT}; }}
        QCheckBox::indicator:pressed, QRadioButton::indicator:pressed {{ border-color: {PRIMARY}; }}
        QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{ border-color: {colors['disabled_text']}; }}
        QPushButton, QToolButton {{
            background-color: {PRIMARY}; color: #FFFFFF;
            border: 1px solid transparent; border-radius: 6px; padding: 7px 12px;
        }}
        QPushButton:hover:enabled, QToolButton:hover:enabled {{ background-color: {ACCENT}; }}
        QPushButton:focus, QToolButton:focus {{ border-color: #90CDF4; }}
        QPushButton:default {{ border-color: {ACCENT}; }}
        QPushButton:checked, QToolButton:checked {{ background-color: {ACCENT}; color: #FFFFFF; }}
        QPushButton:pressed:enabled, QToolButton:pressed:enabled {{
            background-color: #23456E; color: #FFFFFF; border-color: #63B3ED;
            padding-top: 8px; padding-bottom: 6px;
        }}
        QPushButton#runInferenceButton {{ font-weight: bold; background-color: {ACCENT}; }}
        QPushButton#runInferenceButton:hover:enabled {{ background-color: {PRIMARY}; }}
        QPushButton#runInferenceButton:pressed:enabled {{ background-color: #23456E; }}
        QPushButton#deleteSelectedButton {{ background-color: {colors['danger']}; color: #FFFFFF; }}
        QPushButton#deleteSelectedButton:hover:enabled {{ background-color: {colors['danger_hover']}; }}
        QPushButton#deleteSelectedButton:pressed:enabled {{ background-color: {colors['danger_pressed']}; }}
        QToolButton#settingsButton {{ background: transparent; border: 1px solid #6385AF; padding: 6px; }}
        QToolButton#settingsButton:hover:enabled {{ background-color: #3B669A; border-color: #90CDF4; }}
        QToolButton#settingsButton:pressed:enabled {{ background-color: #23456E; }}
        QPushButton:disabled, QToolButton:disabled,
        QPushButton#runInferenceButton:disabled, QPushButton#deleteSelectedButton:disabled {{
            background-color: {colors['disabled']}; color: {colors['disabled_text']}; border-color: {colors['border']};
        }}
        QTabWidget::pane {{ border: 1px solid {colors['border']}; background-color: {colors['surface']}; border-radius: 6px; }}
        QTabBar::tab {{
            background-color: {colors['raised']}; color: {colors['text']};
            padding: 9px 20px; border: 1px solid {colors['border']};
            border-bottom: 2px solid transparent; border-top-left-radius: 6px; border-top-right-radius: 6px;
        }}
        QTabBar::tab:hover:!selected {{ background-color: {colors['hover']}; border-bottom-color: {ACCENT}; }}
        QTabBar::tab:selected {{ background-color: {PRIMARY}; color: #FFFFFF; border-bottom-color: #63B3ED; }}
        QTabBar::tab:focus {{ border-color: {ACCENT}; }}
        QAbstractItemView {{
            background-color: {colors['field']}; alternate-background-color: {colors['raised']};
            color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 6px;
            selection-background-color: {colors['selection']}; selection-color: {colors['text']}; outline: none;
        }}
        QAbstractItemView::item {{ padding: 5px; }}
        QAbstractItemView::item:hover {{ background-color: {colors['hover']}; }}
        QAbstractItemView::item:selected, QAbstractItemView::item:selected:!active {{
            background-color: {colors['selection']}; color: {colors['text']};
        }}
        QTableWidget#historyTable {{ gridline-color: {colors['divider']}; }}
        QHeaderView, QTableCornerButton::section {{ background-color: {colors['raised']}; }}
        QHeaderView::section {{
            background-color: {colors['raised']}; color: {colors['text']};
            font-weight: bold; padding: 8px; border: none; border-bottom: 1px solid {colors['border']};
        }}
        QGraphicsView#imageGraphicsView {{
            background-color: {colors['field']}; border: 1px solid {colors['border']}; border-radius: 8px;
        }}
        QCalendarWidget QWidget {{ background-color: {colors['surface']}; color: {colors['text']}; }}
        QCalendarWidget QAbstractItemView {{ selection-background-color: {colors['selection']}; }}
        QCalendarWidget QToolButton {{ color: {colors['text']}; background-color: {colors['raised']}; padding: 5px; }}
        QCalendarWidget QToolButton:hover {{ background-color: {colors['hover']}; }}
        QMenu, QMenuBar {{ background-color: {colors['surface']}; color: {colors['text']}; }}
        QMenu {{ border: 1px solid {colors['border']}; padding: 5px; }}
        QMenu::item {{ padding: 7px 24px; border-radius: 4px; }}
        QMenu::item:selected, QMenuBar::item:selected {{ background-color: {colors['selection']}; color: {colors['text']}; }}
        QMenu::separator {{ height: 1px; background-color: {colors['border']}; margin: 4px; }}
        QToolTip {{ background-color: {colors['surface']}; color: {colors['text']}; border: 1px solid {colors['border']}; padding: 6px; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
        QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
        QScrollBar::handle {{ background-color: {colors['border']}; border-radius: 3px; min-width: 18px; min-height: 18px; }}
        QScrollBar::handle:hover {{ background-color: {ACCENT}; }}
        QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
        QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
        QStatusBar {{ background-color: {colors['raised']}; border-top: 1px solid {colors['border']}; }}
        QStatusBar::item {{ border: none; }}
        QStatusBar QLabel {{ margin-left: 8px; }}
    """)
    install_interactions(app)
