"""Shared appearance, layout, and export preferences dialog."""

from PyQt5.QtCore import QSettings, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.theme import THEME_SETTING, apply_theme, current_theme


class SettingsDialog(QDialog):
    """Update appearance immediately and preserve the existing preference hooks."""

    theme_changed = pyqtSignal(str)
    reset_export_reminders_requested = pyqtSignal()
    reset_panel_layout_requested = pyqtSignal()

    def __init__(self, settings: QSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings — ZY-Path")
        self.setObjectName("settingsDialog")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Settings", self)
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        appearance = QGroupBox("Appearance", self)
        appearance_layout = QFormLayout(appearance)
        appearance_layout.setSpacing(12)
        self.theme_combo = QComboBox(appearance)
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(current_theme())
        self.theme_combo.setToolTip("Choose the appearance for all windows.")
        self.theme_combo.setAccessibleName("Theme")
        appearance_layout.addRow("Theme", self.theme_combo)
        layout.addWidget(appearance)

        exports = QGroupBox("Export reminders", self)
        export_layout = QVBoxLayout(exports)
        export_layout.setSpacing(10)
        self.png_reminder_checkbox = QCheckBox("Explain PNG exports", exports)
        self.pdf_reminder_checkbox = QCheckBox("Explain PDF exports", exports)
        for export_format, checkbox in (
            ("png", self.png_reminder_checkbox), ("pdf", self.pdf_reminder_checkbox)
        ):
            checkbox.setToolTip(f"Show a reminder before exporting {export_format.upper()}.")
            checkbox.toggled.connect(
                lambda enabled, name=export_format: self._save_reminder(name, enabled)
            )
            export_layout.addWidget(checkbox)
        reset_reminders = QPushButton("Restore Export Reminders", exports)
        reset_reminders.setToolTip("Enable both export explanations again.")
        reset_reminders.clicked.connect(self.reset_export_reminders_requested.emit)
        export_layout.addWidget(reset_reminders)
        layout.addWidget(exports)

        reset_layout = QPushButton("Reset Panel Layout", self)
        reset_layout.setToolTip("Restore the original panel proportions.")
        reset_layout.clicked.connect(self.reset_panel_layout_requested.emit)
        layout.addWidget(reset_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh_preferences()
        self.theme_combo.currentTextChanged.connect(self._change_theme)

    def refresh_preferences(self) -> None:
        """Reflect reminders changed by an export explanation or reset."""
        for name, checkbox in (
            ("png", self.png_reminder_checkbox), ("pdf", self.pdf_reminder_checkbox)
        ):
            checkbox.blockSignals(True)
            checkbox.setChecked(self.settings.value(f"export/{name}ReminderEnabled", True, type=bool))
            checkbox.blockSignals(False)

    def _save_reminder(self, name: str, enabled: bool) -> None:
        self.settings.setValue(f"export/{name}ReminderEnabled", enabled)
        self.settings.sync()

    def _change_theme(self, theme_name: str) -> None:
        apply_theme(QApplication.instance(), theme_name)
        self.settings.setValue(THEME_SETTING, theme_name)
        self.settings.sync()
        self.theme_changed.emit(theme_name)
