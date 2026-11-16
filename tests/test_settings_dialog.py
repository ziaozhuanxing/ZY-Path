"""Focused tests for settings persistence and layout actions."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

from PIL import Image
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton

from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.theme import apply_theme, splitter_style


def isolated_settings(tmp_path: Path) -> QSettings:
    return QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)


def test_settings_button_and_dialog_chrome_are_complete(qtbot, tmp_path: Path) -> None:
    settings = isolated_settings(tmp_path)
    window = MainWindow(
        settings=settings,
        db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "missing.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    window.settings_button.click()
    dialog = window._settings_dialog

    assert dialog is not None
    assert not bool(dialog.windowFlags() & Qt.WindowContextHelpButtonHint)
    assert not window.settings_button.icon().isNull()
    assert window.settings_button.width() == 40
    assert window.settings_button.height() == 40
    assert window.settings_button.iconSize().width() == 22
    assert window.settings_button.iconSize().height() == 22

    for size in (1366, 1708, 2050):
        window.resize(size, 900)
        qtbot.wait(20)
        assert window.settings_button.width() == 40
        assert window.settings_button.height() == 40
    window.showMaximized()
    qtbot.wait(50)
    window.showNormal()
    qtbot.wait(50)
    assert window.settings_button.width() == 40


def test_theme_selection_persists_and_applies_immediately(qtbot, tmp_path: Path) -> None:
    settings = isolated_settings(tmp_path)
    window = MainWindow(
        settings=settings,
        db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "missing.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    dialog = SettingsDialog(settings, window)
    qtbot.addWidget(dialog)

    dialog.dark_radio.click()
    assert settings.value("appearance/theme", "Light", type=str) == "Dark"
    application = QApplication.instance()
    assert application is not None
    assert application.property("zyTheme") == "Dark"

    restarted = SettingsDialog(settings, window)
    qtbot.addWidget(restarted)
    assert restarted.dark_radio.isChecked()
    apply_theme(application, "Light")


def test_reminder_checkboxes_use_existing_keys_and_reset_syncs(qtbot, tmp_path: Path, monkeypatch) -> None:
    settings = isolated_settings(tmp_path)
    settings.setValue("export/pngReminderEnabled", True)
    settings.setValue("export/pdfReminderEnabled", True)
    window = MainWindow(
        settings=settings,
        db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "missing.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    dialog = SettingsDialog(settings, window)
    qtbot.addWidget(dialog)

    dialog.png_reminder_checkbox.click()
    assert settings.value("export/pngReminderEnabled", True, type=bool) is False
    assert settings.value("export/pdfReminderEnabled", False, type=bool) is True

    monkeypatch.setattr(QMessageBox, "information", lambda *_args: None)
    window._settings_dialog = dialog
    window._reset_export_reminders()
    assert dialog.png_reminder_checkbox.isChecked()
    assert dialog.pdf_reminder_checkbox.isChecked()
    assert settings.value("export/pngReminderEnabled", False, type=bool) is True
    assert settings.value("export/pdfReminderEnabled", False, type=bool) is True


def test_reset_panel_layout_preserves_result_and_fits_images(qtbot, tmp_path: Path) -> None:
    settings = isolated_settings(tmp_path)
    window = MainWindow(
        settings=settings,
        db_path=tmp_path / "history.db",
        builtin_model_path=tmp_path / "missing.pth",
        results_dir=tmp_path / "results",
    )
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    initial_sizes = window.splitter.sizes()
    image_path = tmp_path / "source.png"
    Image.new("RGB", (300, 200), "white").save(image_path)
    window.result_panel.show_image(image_path)
    window.result_panel.image_label.zoom_in()
    marker = {"result": "kept"}
    window._current_result = marker
    window.splitter.setSizes([400, 400, 200])

    window._reset_panel_layout()

    assert window._current_result is marker
    assert window.result_panel.image_label.zoom_indicator.text().startswith("Fit (")
    assert window.result_panel.image_label.displayed_size().width() <= window.result_panel.image_label.graphics_view.viewport().width()
    assert window.splitter.sizes() == initial_sizes


def test_settings_persist_and_refresh_export_preferences(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert dialog.png_reminder_checkbox.isChecked()
    dialog.png_reminder_checkbox.setChecked(False)
    assert not settings.value("export/pngReminderEnabled", True, type=bool)
    settings.setValue("export/pngReminderEnabled", True)
    dialog.refresh_preferences()
    assert dialog.png_reminder_checkbox.isChecked()
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
