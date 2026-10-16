"""Regression coverage for the main window's previously missing interfaces."""

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QPushButton

from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.theme import splitter_style


def test_settings_persist_and_refresh_export_preferences(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert dialog.png_reminder.isChecked()
    dialog.png_reminder.setChecked(False)
    assert not settings.value("export/pngReminderEnabled", True, type=bool)
    settings.setValue("export/pngReminderEnabled", True)
    dialog.refresh_preferences()
    assert dialog.png_reminder.isChecked()
    with qtbot.waitSignal(dialog.reset_panel_layout_requested):
        button = next(b for b in dialog.findChildren(QPushButton)
                      if b.text() == "Reset Panel Layout")
        qtbot.mouseClick(button, Qt.LeftButton)


def test_window_settings_and_splitter_theme_callbacks(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    window = MainWindow(db_path=tmp_path / "history.db", settings=settings,
                        builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window.show()
    qtbot.mouseClick(window.settings_button, Qt.LeftButton)
    assert window._settings_dialog.isVisible()
    window._settings_dialog.theme_changed.emit("Dark")
    assert window.splitter.styleSheet() == splitter_style("Dark")
    assert window.result_panel.vertical_splitter.styleSheet() == splitter_style("Dark")
    assert window.splitter.handleWidth() == 6
    assert window.result_panel.vertical_splitter.handleWidth() == 8
    window._settings_dialog.reset_panel_layout_requested.emit()
    assert window.statusBar().currentMessage() == "Panel layout restored"
