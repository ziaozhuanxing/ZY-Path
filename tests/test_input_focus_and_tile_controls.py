"""Regressions for focus clipping, unintended dialog actions and tile inputs."""
import pytest
from PyQt5.QtCore import QPoint, QPointF, QRect, QSettings, Qt
from PyQt5.QtGui import QFont, QWheelEvent
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QStyle, QStyleOptionButton

from ui.inference_panel import InferencePanel
from ui.settings_dialog import SettingsDialog
from ui.theme import apply_theme


@pytest.fixture
def themed(qapp):
    style, font, theme = qapp.styleSheet(), QFont(qapp.font()), qapp.property("zyTheme")
    yield qapp
    qapp.setStyleSheet(style)
    qapp.setFont(font)
    qapp.setProperty("zyTheme", theme)


def content_rect(button):
    option = QStyleOptionButton()
    option.initFrom(button)
    option.text = button.text()
    return button.style().subElementRect(QStyle.SE_PushButtonContents, option, button)


@pytest.mark.parametrize("theme", ["Light", "Dark"])
@pytest.mark.parametrize("points", [10, 20])
def test_upload_text_fits_initial_focus_before_any_inference(qtbot, themed, theme, points):
    apply_theme(themed, theme)
    font = QFont(themed.font())
    font.setPointSize(points)
    themed.setFont(font)
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.resize(max(380, panel.minimumWidth()), 600)
    panel.set_model_status("Built-in Classification: ready (densenet, 9 classes)", True)
    panel.show()
    qtbot.wait(30)
    upload = panel.upload_image_button
    for focus in (panel.built_in_checkbox, upload, panel.browse_model_button, upload):
        focus.setFocus()
        qtbot.wait(10)
        contents = content_rect(upload)
        assert contents.height() >= upload.fontMetrics().height()
        assert contents.width() >= upload.fontMetrics().horizontalAdvance(upload.text())
        viewport = panel.controls_scroll.viewport()
        bounds = QRect(upload.mapTo(viewport, QPoint()), upload.size())
        assert viewport.rect().contains(bounds)
    assert not panel.run_button.isEnabled()  # No image/run needed to fix the layout.


@pytest.mark.parametrize("points", [10, 20])
def test_message_box_ok_text_and_button_fit_when_focused(qtbot, themed, points):
    apply_theme(themed, "Dark")
    font = QFont(themed.font())
    font.setPointSize(points)
    themed.setFont(font)
    box = QMessageBox(QMessageBox.Information, "Export Reminders",
                      "PNG and PDF export reminders have been restored.", QMessageBox.Ok)
    qtbot.addWidget(box)
    box.show()
    qtbot.wait(30)
    button = box.button(QMessageBox.Ok)
    button.setFocus()
    qtbot.wait(10)
    contents = content_rect(button)
    assert contents.height() >= button.fontMetrics().height()
    assert contents.width() >= button.fontMetrics().horizontalAdvance(button.text())
    assert box.rect().contains(QRect(button.mapTo(box, QPoint()), button.size()))
    qtbot.mouseClick(button, Qt.LeftButton)
    assert not box.isVisible()


def make_settings(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    settings.setValue("export/pngReminderEnabled", False)
    settings.setValue("export/pdfReminderEnabled", False)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.resize(620, 400)
    dialog.navigation.setCurrentRow(1)
    dialog.show()
    qtbot.wait(30)
    return dialog


@pytest.mark.parametrize("name", ["tile_width", "tile_height", "startup_mode", "resize_method"])
@pytest.mark.parametrize("key", [Qt.Key_Return, Qt.Key_Enter])
def test_enter_commits_only_focused_preference(qtbot, tmp_path, name, key):
    dialog = make_settings(qtbot, tmp_path)
    spy = QSignalSpy(dialog.reset_export_reminders_requested)
    control = getattr(dialog, name)
    scroll = dialog.pages.currentWidget()
    scroll.ensureWidgetVisible(control)
    qtbot.wait(20)
    control.setFocus()
    if name.startswith("tile_"):
        control.selectAll()
        qtbot.keyClicks(control, "640")
    else:
        qtbot.keyClick(control, Qt.Key_Down)
    qtbot.keyClick(control, key)
    assert len(spy) == 0
    assert dialog.isVisible()
    assert not dialog.settings.value("export/pngReminderEnabled", type=bool)
    assert not dialog.settings.value("export/pdfReminderEnabled", type=bool)
    if name.startswith("tile_"):
        assert control.value() == 640
        assert dialog.settings.value("classificationTiles/" + name.removeprefix("tile_"), type=int) == 640
    else:
        setting = "classification/defaultMode" if name == "startup_mode" else "classification/resizeBackend"
        assert dialog.settings.value(setting) == control.currentData()


def test_settings_buttons_remain_explicit_keyboard_actions(qtbot, tmp_path):
    dialog = make_settings(qtbot, tmp_path)
    assert all(not b.autoDefault() and not b.isDefault() for b in dialog.findChildren(QPushButton))
    spy = QSignalSpy(dialog.reset_export_reminders_requested)
    dialog.reset_reminders_button.setFocus()
    qtbot.keyClick(dialog.reset_reminders_button, Qt.Key_Return)
    assert len(spy) == 1
    qtbot.keyClick(dialog.reset_reminders_button, Qt.Key_Space)
    assert len(spy) == 2
    dialog.tile_width.setValue(768)
    dialog.tile_height.setValue(256)
    dialog.pages.currentWidget().ensureWidgetVisible(dialog.sync_tile_height_button)
    dialog.sync_tile_height_button.setFocus()
    qtbot.keyClick(dialog.sync_tile_height_button, Qt.Key_Return)
    assert dialog.tile_height.value() == 768
    assert len(spy) == 2


@pytest.mark.parametrize("name", ["tile_width", "tile_height"])
@pytest.mark.parametrize("focused", [False, True])
@pytest.mark.parametrize("editor", [False, True])
def test_tile_wheel_scrolls_page_without_changing_value(qtbot, tmp_path, name, focused, editor):
    dialog = make_settings(qtbot, tmp_path)
    spin = getattr(dialog, name)
    scroll = dialog.pages.currentWidget()
    scroll.ensureWidgetVisible(spin)
    qtbot.wait(20)
    target = spin.lineEdit() if editor else spin
    if focused:
        target.setFocus()
    else:
        dialog.navigation.setFocus()
    value = spin.value()
    position = scroll.verticalScrollBar().value()
    point = target.rect().center()
    event = QWheelEvent(QPointF(point), QPointF(target.mapToGlobal(point)), QPoint(), QPoint(0, -120),
                        Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(target, event)
    qtbot.wait(20)
    assert spin.value() == value
    assert scroll.verticalScrollBar().value() > position
    assert dialog.settings.value("classificationTiles/" + name.removeprefix("tile_"), value, type=int) == value


@pytest.mark.parametrize("points", [10, 15, 20])
def test_tile_fields_align_and_keep_manual_keyboard_and_arrow_input(qtbot, themed, tmp_path, points):
    apply_theme(themed, "Dark")
    font = QFont(themed.font())
    font.setPointSize(points)
    themed.setFont(font)
    dialog = make_settings(qtbot, tmp_path)
    for width in (620, 1000, 620):
        dialog.resize(width, 500)
        qtbot.wait(30)
        w, h = dialog.tile_width, dialog.tile_height
        assert w.mapTo(dialog, QPoint()).x() == h.mapTo(dialog, QPoint()).x()
        assert w.width() == h.width()
        assert w.height() == h.height()
        assert dialog.pages.currentWidget().horizontalScrollBar().maximum() == 0
        for label in dialog.findChildren(QLabel):
            if label.text() in ("Tile width (px)", "Tile height (px)"):
                assert label.width() >= label.fontMetrics().horizontalAdvance("Tile")
                text_bounds = label.fontMetrics().boundingRect(0, 0, label.width(), 1000,
                                                               Qt.TextWordWrap, label.text())
                assert label.height() >= text_bounds.height()
    dialog.pages.currentWidget().ensureWidgetVisible(w)
    w.setFocus()
    qtbot.keyClick(w, Qt.Key_Up)
    assert w.value() == 513
    dialog.sync_tile_height_button.click()
    assert h.value() == 513
    h.setFocus()
    qtbot.keyClick(h, Qt.Key_Down)
    assert h.value() == 512
