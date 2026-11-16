"""Regression checks for consistent dark states and intentional option changes."""

import gc

import pytest
from matplotlib.colors import to_hex
from PyQt5.QtCore import QAbstractAnimation, QPoint, QPointF, QSettings, Qt
from PyQt5.QtGui import QPalette, QPixmap, QWheelEvent
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDateEdit, QDialog, QDoubleSpinBox,
    QDialogButtonBox, QFileDialog, QLineEdit, QMessageBox, QPushButton, QRadioButton, QScrollArea,
    QSlider, QSpinBox, QTabBar, QToolButton, QVBoxLayout, QWidget,
)

from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.theme import THEME_SETTING, apply_theme, theme_colors
from ui.zoomable_image_view import ZoomableImageView


@pytest.fixture
def themed_app(qapp):
    previous_stylesheet = qapp.styleSheet()
    previous_palette = qapp.palette()
    previous_theme = qapp.property("zyTheme")
    previous_font = qapp.font()
    apply_theme(qapp, "Dark")
    yield qapp
    qapp.setProperty("zyTheme", previous_theme)
    qapp.setPalette(previous_palette)
    qapp.setStyleSheet(previous_stylesheet)
    qapp.setFont(previous_font)


def _wheel(widget, delta=120, pixel=False):
    position = widget.rect().center()
    event = QWheelEvent(
        QPointF(position), QPointF(widget.mapToGlobal(position)),
        QPoint(0, delta) if pixel else QPoint(),
        QPoint() if pixel else QPoint(0, delta),
        Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate if pixel else Qt.NoScrollPhase, False,
    )
    QApplication.sendEvent(widget, event)


@pytest.mark.parametrize("pixel", [False, True])
@pytest.mark.parametrize("focused", [False, True])
def test_wheel_cannot_change_choices_including_editor_children(themed_app, qtbot, pixel, focused):
    window = QWidget()
    qtbot.addWidget(window)
    layout = QVBoxLayout(window)
    combo = QComboBox()
    combo.addItems(["Light", "Dark", "Third"])
    combo.setCurrentIndex(1)
    combo.setEditable(True)
    spin = QSpinBox()
    spin.setValue(30)
    decimal = QDoubleSpinBox()
    decimal.setValue(3.5)
    date = QDateEdit()
    slider = QSlider(Qt.Horizontal)
    slider.setValue(50)
    tabs = QTabBar()
    tabs.addTab("Inference")
    tabs.addTab("History")
    tabs.setCurrentIndex(1)
    controls = [combo, spin, decimal, date, slider, tabs]
    for control in controls:
        layout.addWidget(control)
    signals = [
        QSignalSpy(combo.currentIndexChanged), QSignalSpy(spin.valueChanged),
        QSignalSpy(decimal.valueChanged), QSignalSpy(date.dateChanged),
        QSignalSpy(slider.valueChanged), QSignalSpy(tabs.currentChanged),
    ]
    window.show()
    qtbot.waitExposed(window)
    for control in controls + [combo.lineEdit(), spin.lineEdit(), date.lineEdit()]:
        if focused:
            control.setFocus()
        else:
            control.clearFocus()
        for delta in (-120, 120):
            _wheel(control, delta, pixel)
    assert all(len(spy) == 0 for spy in signals)
    qtbot.keyClick(spin, Qt.Key_Up)
    assert spin.value() == 31
    qtbot.mouseClick(tabs, Qt.LeftButton, pos=tabs.tabRect(0).center())
    assert tabs.currentIndex() == 0


def test_open_combo_requires_click_to_select(themed_app, qtbot):
    combo = QComboBox()
    qtbot.addWidget(combo)
    combo.addItems(["Light", "Dark", "Third"])
    combo.show()
    qtbot.waitExposed(combo)
    combo.showPopup()
    qtbot.waitUntil(lambda: combo.view().isVisible())
    spy = QSignalSpy(combo.currentIndexChanged)
    _wheel(combo.view().viewport(), -120)
    assert not spy
    index = combo.model().index(1, 0)
    target = combo.view().visualRect(index).intersected(combo.view().viewport().rect())
    qtbot.mouseClick(combo.view().viewport(), Qt.LeftButton, pos=target.center())
    assert combo.currentText() == "Dark"


@pytest.mark.parametrize("button_type", [QPushButton, QToolButton, QCheckBox, QRadioButton])
def test_button_wheel_never_activates_and_clicks_still_work(themed_app, qtbot, button_type):
    button = button_type()
    button.setText("Select")
    qtbot.addWidget(button)
    button.show()
    spy = QSignalSpy(button.clicked)
    _wheel(button)
    assert not spy
    qtbot.mouseClick(button, Qt.LeftButton)
    assert len(spy) == 1


@pytest.mark.parametrize("dialog_type", [QDialog, QMessageBox, QFileDialog])
def test_dark_dialog_buttons_keep_their_color_in_every_state(themed_app, qtbot, dialog_type):
    dialog = dialog_type()
    qtbot.addWidget(dialog)
    if isinstance(dialog, QMessageBox):
        dialog.setText("Export the current result?")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    elif isinstance(dialog, QFileDialog):
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    else:
        layout = QVBoxLayout(dialog)
        layout.addWidget(QPushButton("Continue", dialog))
        layout.addWidget(QLineEdit("Filename", dialog))
    dialog.show()
    qtbot.waitExposed(dialog)
    buttons = dialog.findChildren(QPushButton)
    assert buttons
    for button in buttons:
        if not button.isVisible():
            continue
        button.setCheckable(True)
        for state in ("normal", "focus", "pressed", "checked", "disabled"):
            button.setEnabled(state != "disabled")
            button.setChecked(state == "checked")
            button.setDown(state == "pressed")
            if state == "focus":
                button.setFocus()
            image = button.grab().toImage()
            color = image.pixelColor(max(2, image.width() - 12), image.height() // 2)
            assert min(color.red(), color.green(), color.blue()) < 160, (dialog_type, state, color.name())
    for field in dialog.findChildren(QLineEdit):
        assert field.palette().color(QPalette.Base).lightness() < 160
    assert themed_app.testAttribute(Qt.AA_DontUseNativeDialogs)


def test_feedback_is_short_and_does_not_block_repeated_or_keyboard_clicks(themed_app, qtbot):
    button = QPushButton("Run")
    qtbot.addWidget(button)
    button.show()
    qtbot.waitExposed(button)
    geometry = button.geometry()
    feedback = button.graphicsEffect()
    assert feedback is not None
    spy = QSignalSpy(button.clicked)
    for _ in range(3):
        qtbot.mouseClick(button, Qt.LeftButton)
    assert len(spy) == 3
    assert feedback.animation.state() == QAbstractAnimation.Running
    qtbot.waitUntil(lambda: feedback.animation.state() == QAbstractAnimation.Stopped, timeout=700)
    button.setFocus()
    qtbot.keyClick(button, Qt.Key_Space)
    assert len(spy) == 4
    assert button.geometry() == geometry
    apply_theme(themed_app, "Light")
    apply_theme(themed_app, "Dark")
    assert button.graphicsEffect() is feedback


def test_content_scrolling_and_image_zoom_are_preserved(themed_app, qtbot):
    scroll = QScrollArea()
    qtbot.addWidget(scroll)
    content = QWidget()
    content.setMinimumHeight(2000)
    scroll.setWidget(content)
    scroll.resize(300, 200)
    scroll.show()
    qtbot.waitExposed(scroll)
    _wheel(scroll.viewport(), -120)
    assert scroll.verticalScrollBar().value() > 0
    viewer = ZoomableImageView()
    qtbot.addWidget(viewer)
    image = QPixmap(400, 400)
    image.fill(Qt.red)
    viewer.set_source_pixmap(image)
    viewer.show()
    qtbot.waitExposed(viewer)
    _wheel(viewer.graphics_view.viewport(), 120)
    assert viewer._zoom_percent > 100


def test_standard_dialog_buttons_keep_painting_after_garbage_collection(themed_app, qtbot, tmp_path):
    dialog = SettingsDialog(QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat))
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    gc.collect()
    button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Close)
    image = button.grab().toImage()
    color = image.pixelColor(10, image.height() // 2)
    assert color.blue() > color.red() + 30
    qtbot.mouseClick(button, Qt.LeftButton)
    assert not dialog.isVisible()


def test_settings_theme_updates_existing_windows_charts_and_persists(themed_app, qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    window = MainWindow(
        db_path=tmp_path / "history.db", results_dir=tmp_path / "results",
        settings=settings, builtin_model_path=tmp_path / "absent.pth",
    )
    qtbot.addWidget(window)
    window.result_panel.show_classification("A", .8, [.8, .2], ["A", "B"])
    window._show_settings()
    dialog = window._settings_dialog
    assert isinstance(dialog, SettingsDialog)
    for theme_name in ("Light", "Dark") * 3:
        dialog.theme_combo.setCurrentText(theme_name)
        assert settings.value(THEME_SETTING) == theme_name
        assert themed_app.property("zyTheme") == theme_name
        colors = theme_colors(theme_name)
        assert colors["border"] in window.splitter.styleSheet()
        assert colors["border"] in window.result_panel.vertical_splitter.styleSheet()
        assert to_hex(window.result_panel.get_result_figure().get_facecolor()).upper() == colors["surface"]
        scene_text = window.result_panel.image_label.graphics_view.scene().items()[0]
        assert scene_text.defaultTextColor().name().upper() == colors["muted"]
    dialog.png_reminder_checkbox.setChecked(False)
    dialog.refresh_preferences()
    assert settings.value("export/pngReminderEnabled", type=bool) is False
    assert dialog.png_reminder_checkbox.isChecked() is False
    window._show_settings()
    assert window._settings_dialog is dialog
