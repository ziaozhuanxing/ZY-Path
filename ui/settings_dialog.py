"""Application settings dialog."""

import importlib.metadata
import platform
import sys

from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QSpinBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ui.theme import apply_theme
from core.classification_tiles import CLASSIFICATION_LABELS, CLASSIFICATION_COLORS
from utils.paths import resource_path


class SettingsDialog(QDialog):
    """Provide one reusable dialog for application settings and help pages."""

    _PAGE_NAMES = ("Appearance", "Preferences", "Guide & Support", "About")
    _THEME_KEY = "appearance/theme"
    _PNG_REMINDER_KEY = "export/pngReminderEnabled"
    _PDF_REMINDER_KEY = "export/pdfReminderEnabled"
    theme_changed = pyqtSignal(str)
    reset_export_reminders_requested = pyqtSignal()
    reset_panel_layout_requested = pyqtSignal()

    def __init__(
        self,
        settings: QSettings,
        parent: QWidget | None = None,
        app_version: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.settings = settings
        self.app_version = app_version
        self.setWindowTitle("Settings")
        self.setMinimumSize(720, 480)
        self.resize(860, 560)

        layout = QHBoxLayout(self)
        self.navigation = QListWidget(self)
        self.navigation.setObjectName("settingsNavigation")
        self.navigation.setFixedWidth(180)
        self.navigation.setAccessibleName("Settings sections")
        self.pages = QStackedWidget(self)
        self.pages.setObjectName("settingsPages")
        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self._build_appearance_page()
        self._build_preferences_page()
        self._build_guide_page()
        self._build_about_page()
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def _add_page(self, page_name: str) -> QWidget:
        self.navigation.addItem(QListWidgetItem(page_name))
        page = QWidget(self.pages)
        self.pages.addWidget(page)
        return page

    def _build_appearance_page(self) -> None:
        page = self._add_page("Appearance")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Appearance", page))
        layout.addWidget(QLabel("Choose the interface theme. Changes apply immediately.", page))
        self.light_radio = QRadioButton("Light", page)
        self.dark_radio = QRadioButton("Dark", page)
        layout.addWidget(self.light_radio)
        layout.addWidget(self.dark_radio)
        layout.addStretch()
        theme = self.settings.value(self._THEME_KEY, "Light", type=str)
        self.dark_radio.setChecked(theme.casefold() == "dark")
        self.light_radio.setChecked(not self.dark_radio.isChecked())
        self.light_radio.toggled.connect(self._theme_toggled)
        self.dark_radio.toggled.connect(self._theme_toggled)

    def _build_preferences_page(self) -> None:
        page = self._add_page("Preferences")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Preferences", page))
        self.png_reminder_checkbox = QCheckBox("Show PNG export explanation", page)
        self.pdf_reminder_checkbox = QCheckBox("Show PDF export explanation", page)
        for checkbox, key in (
            (self.png_reminder_checkbox, self._PNG_REMINDER_KEY),
            (self.pdf_reminder_checkbox, self._PDF_REMINDER_KEY),
        ):
            checkbox.setChecked(self.settings.value(key, True, type=bool))
            checkbox.toggled.connect(
                lambda checked, setting_key=key: self._set_bool(setting_key, checked)
            )
            layout.addWidget(checkbox)
        self.classification_tiles_enabled = QCheckBox("Enable large-image classification tiles", page)
        self.classification_tiles_enabled.setChecked(self.settings.value("classificationTiles/enabled", False, type=bool))
        self.classification_tiles_enabled.toggled.connect(lambda value: self._set_bool("classificationTiles/enabled", value))
        layout.addWidget(self.classification_tiles_enabled)
        warning = QLabel("原图 tile 尺寸（像素）：探索性配置，训练尺度/倍率待确认。512 仅为可编辑起始值，不代表训练尺寸。边缘裁块缩放到网络 224×224；小图仍单图分类。", page)
        warning.setWordWrap(True)
        layout.addWidget(warning)
        for name, label in (("width", "Tile width (px)"), ("height", "Tile height (px)")):
            row = QHBoxLayout()
            row.addWidget(QLabel(label, page))
            spin = QSpinBox(page)
            spin.setRange(1, 100000)
            spin.setValue(self.settings.value(f"classificationTiles/{name}", 512, type=int))
            spin.valueChanged.connect(lambda value, key=name: self._set_bool(f"classificationTiles/{key}", value))
            setattr(self, f"tile_{name}", spin)
            row.addWidget(spin)
            layout.addLayout(row)
        palette = QLabel("Classification palette v1 (display only):<br>" + " | ".join(
            f'<span style="color:rgb{color}">■</span> {label} RGB{color}'
            for label, color in zip(CLASSIFICATION_LABELS, CLASSIFICATION_COLORS)
        ), page)
        palette.setWordWrap(True)
        layout.addWidget(palette)
        layout.addWidget(QLabel("Changes take effect immediately.", page))
        self.reset_reminders_button = QPushButton("Reset Export Reminders", page)
        self.reset_reminders_button.clicked.connect(
            self.reset_export_reminders_requested.emit
        )
        layout.addWidget(self.reset_reminders_button)
        self.reset_layout_button = QPushButton("Reset Panel Layout", page)
        self.reset_layout_button.clicked.connect(self.reset_panel_layout_requested.emit)
        layout.addWidget(self.reset_layout_button)
        layout.addStretch()

    def _build_guide_page(self) -> None:
        page = self._add_page("Guide & Support")
        layout = QVBoxLayout(page)
        browser = QTextBrowser(page)
        browser.setOpenExternalLinks(False)
        browser.setHtml(
            "<h2>Quick Start</h2>"
            "<ol><li>Select the built-in model or browse for a supported custom model.</li>"
            "<li>Select Classification or Segmentation. The task must match the model output.</li>"
            "<li>Upload an image and run inference.</li>"
            "<li>Read the class and confidence, or inspect the segmentation overlay and legend.</li>"
            "<li>Use the mouse wheel to zoom, drag to pan, and Fit to fit the image.</li>"
            "<li>Drag the splitter to resize the original and result areas.</li>"
            "<li>Search history and select a record to rerun it.</li>"
            "<li>PNG saves the result image. PDF saves the full report.</li></ol>"
            "<p>The selected task must match the model output. Dummy models are for testing the UI; trained models are models trained for a real dataset. "
            "ZY-Path does not promise support for every .pt or .pth file.</p>"
            "<h2>Troubleshooting</h2>"
            "<p><b>Task/model mismatch:</b> choose the task detected for the model.</p>"
            "<p><b>Missing model or source image:</b> select files that still exist and can be read.</p>"
            "<p><b>Export failure:</b> check that the source and result exist and choose a writable destination.</p>"
            "<h2>Support</h2><p>Support contact is not configured yet.</p>"
        )
        layout.addWidget(browser)
        self.copy_system_info_button = QPushButton("Copy System Info", page)
        self.copy_system_info_button.clicked.connect(self._copy_system_info)
        layout.addWidget(self.copy_system_info_button)

    def _build_about_page(self) -> None:
        page = self._add_page("About")
        layout = QVBoxLayout(page)
        logo_path = resource_path("assets/logo.png")
        logo = QLabel(page)
        if logo_path.is_file():
            logo.setPixmap(
                QPixmap(str(logo_path)).scaled(
                    96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        layout.addWidget(logo)
        layout.addWidget(QLabel("ZY-Path", page))
        layout.addWidget(
            QLabel(
                "Histopathology image classification, segmentation, and local history.",
                page,
            )
        )
        layout.addWidget(QLabel(f"Version: {self.app_version or 'Not configured'}", page))
        layout.addWidget(QLabel("Developer: Li Zi Yao", page))
        layout.addWidget(
            QLabel(
                "For education and exploratory research only.<br>Not intended for clinical diagnosis.",
                page,
            )
        )
        layout.addStretch()

    def _theme_toggled(self, checked: bool) -> None:
        if not checked:
            return
        theme = "Dark" if self.dark_radio.isChecked() else "Light"
        self.settings.setValue(self._THEME_KEY, theme)
        self.settings.sync()
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, theme)
        self.theme_changed.emit(theme)

    def _set_bool(self, key: str, value: bool) -> None:
        self.settings.setValue(key, value)
        self.settings.sync()

    def refresh_preferences(self) -> None:
        """Refresh controls after preferences are changed elsewhere."""
        self.png_reminder_checkbox.setChecked(
            self.settings.value(self._PNG_REMINDER_KEY, True, type=bool)
        )
        self.pdf_reminder_checkbox.setChecked(
            self.settings.value(self._PDF_REMINDER_KEY, True, type=bool)
        )

    def _copy_system_info(self) -> None:
        versions = []
        for package_name in ("PyQt5", "torch", "Pillow", "numpy", "matplotlib", "fpdf2"):
            try:
                versions.append(
                    f"{package_name}: {importlib.metadata.version(package_name)}"
                )
            except importlib.metadata.PackageNotFoundError:
                continue
        text = "\n".join(
            [
                f"ZY-Path version: {self.app_version or 'Not configured'}",
                f"OS: {platform.system()} {platform.release()}",
                f"Python: {sys.version.split()[0]}",
                *versions,
            ]
        )
        QApplication.clipboard().setText(text)
