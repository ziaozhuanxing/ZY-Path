"""Preferences shared with the main window's export and layout actions."""

from PyQt5.QtCore import QSettings, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QPushButton, QVBoxLayout, QWidget,
)


class SettingsDialog(QDialog):
    """Edit export reminders and request a panel layout reset."""

    reset_export_reminders_requested = pyqtSignal()
    reset_panel_layout_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)

    def __init__(self, settings: QSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        self.png_reminder = QCheckBox("Show PNG export reminder", self)
        self.pdf_reminder = QCheckBox("Show PDF export reminder", self)
        for checkbox, key in (
            (self.png_reminder, "export/pngReminderEnabled"),
            (self.pdf_reminder, "export/pdfReminderEnabled"),
        ):
            layout.addWidget(checkbox)
            checkbox.toggled.connect(
                lambda checked, key=key: self._save_preference(key, checked)
            )
        reset_reminders = QPushButton("Reset Export Reminders", self)
        reset_reminders.clicked.connect(self.reset_export_reminders_requested.emit)
        layout.addWidget(reset_reminders)
        reset_layout = QPushButton("Reset Panel Layout", self)
        reset_layout.clicked.connect(self.reset_panel_layout_requested.emit)
        layout.addWidget(reset_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh_preferences()

    def _save_preference(self, key: str, checked: bool) -> None:
        self.settings.setValue(key, checked)
        self.settings.sync()

    def refresh_preferences(self) -> None:
        """Reflect preferences changed by the main window without writing them."""
        for checkbox, key in (
            (self.png_reminder, "export/pngReminderEnabled"),
            (self.pdf_reminder, "export/pdfReminderEnabled"),
        ):
            previous = checkbox.blockSignals(True)
            checkbox.setChecked(self.settings.value(key, True, type=bool))
            checkbox.blockSignals(previous)
