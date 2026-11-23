"""Shared popup styling, click feedback and wheel safety on the complete UI."""

import gc
import subprocess
import sys
from pathlib import Path

import pytest
from PyQt5.QtCore import QAbstractAnimation, QObject, QPoint, QPointF, Qt
from PyQt5.QtGui import QPalette, QWheelEvent
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFileDialog, QLineEdit, QMessageBox, QPushButton,
    QRadioButton, QScrollArea, QSlider, QSpinBox, QTabBar, QToolButton, QVBoxLayout, QWidget,
)

from ui.choice_check_box import ChoiceCheckBox
from ui.explicit_combo_box import ExplicitComboBox
from ui.theme import apply_theme


@pytest.fixture
def dark_app(qapp):
    old_theme = qapp.property("zyTheme") or "Light"
    apply_theme(qapp, "Dark")
    yield qapp
    apply_theme(qapp, old_theme)


def wheel(widget, delta=-120, pixel=False):
    position = widget.rect().center()
    event = QWheelEvent(
        QPointF(position), QPointF(widget.mapToGlobal(position)),
        QPoint(0, delta) if pixel else QPoint(),
        QPoint() if pixel else QPoint(0, delta), Qt.NoButton, Qt.NoModifier,
        Qt.ScrollUpdate if pixel else Qt.NoScrollPhase, False,
    )
    QApplication.sendEvent(widget, event)


@pytest.mark.parametrize("pixel", [False, True])
@pytest.mark.parametrize("focused", [False, True])
def test_every_choice_ignores_wheel_including_unprotected_controls(dark_app, qtbot, pixel, focused):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    combo = QComboBox()
    combo.addItems(["Light", "Dark", "Third"])
    combo.setCurrentIndex(1)
    combo.setEditable(True)
    spin, decimal, date = QSpinBox(), QDoubleSpinBox(), QDateEdit()
    spin.setValue(30)
    decimal.setValue(3.5)
    slider = QSlider(Qt.Horizontal)
    slider.setValue(50)
    tabs = QTabBar()
    tabs.addTab("Inference")
    tabs.addTab("History")
    controls = [combo, spin, decimal, date, slider, tabs]
    for control in controls:
        layout.addWidget(control)
    spies = [QSignalSpy(signal) for signal in (
        combo.currentIndexChanged, spin.valueChanged, decimal.valueChanged,
        date.dateChanged, slider.valueChanged, tabs.currentChanged,
    )]
    host.show()
    qtbot.waitExposed(host)
    for control in controls + [combo.lineEdit(), spin.lineEdit(), date.lineEdit()]:
        control.setFocus() if focused else control.clearFocus()
        for delta in (-120, 120):
            wheel(control, delta, pixel)
    assert all(len(spy) == 0 for spy in spies)
    qtbot.keyClick(spin, Qt.Key_Up)
    assert spin.value() == 31
    qtbot.mouseClick(tabs, Qt.LeftButton, pos=tabs.tabRect(1).center())
    assert tabs.currentIndex() == 1


def test_open_popup_still_requires_an_explicit_choice(dark_app, qtbot):
    combo = QComboBox()
    qtbot.addWidget(combo)
    combo.addItems(["Light", "Dark", "Third"])
    combo.show()
    qtbot.waitExposed(combo)
    combo.showPopup()
    spy = QSignalSpy(combo.currentIndexChanged)
    wheel(combo.view().viewport())
    assert not spy
    index = combo.model().index(1, 0)
    target = combo.view().visualRect(index).intersected(combo.view().viewport().rect())
    qtbot.mouseClick(combo.view().viewport(), Qt.LeftButton, pos=target.center())
    assert combo.currentText() == "Dark"


def test_dropdown_fade_keeps_hit_targets_and_allows_fast_reopen(dark_app, qtbot):
    combo = ExplicitComboBox()
    qtbot.addWidget(combo)
    combo.addItems(["First", "Second", "Third"])
    combo.show()
    qtbot.waitExposed(combo)
    combo.showPopup()
    view = combo.view()
    fade = combo._popup_fade
    assert fade.state() == QAbstractAnimation.Running
    original_rect = view.window().geometry()
    qtbot.waitUntil(lambda: fade.state() == QAbstractAnimation.Stopped)
    assert view.window().geometry() == original_rect
    assert not fade.targetObject().isEnabled()

    combo.hidePopup()
    combo.showPopup()
    assert fade.state() == QAbstractAnimation.Running
    index = view.model().index(1, 0)
    qtbot.mouseClick(view.viewport(), Qt.LeftButton, pos=view.visualRect(index).center())
    assert combo.currentIndex() == 1
    assert not view.isVisible()
    assert not fade.targetObject().isEnabled()

    combo.showPopup()
    qtbot.keyClick(view, Qt.Key_Escape)
    assert not view.isVisible()
    assert combo.currentIndex() == 1


def test_scroll_over_a_choice_moves_its_page_once(dark_app, qtbot):
    scroll = QScrollArea()
    qtbot.addWidget(scroll)
    content = QWidget()
    content.setMinimumHeight(1800)
    layout = QVBoxLayout(content)
    combo = QComboBox(content)
    combo.addItems(["A", "B"])
    layout.addWidget(combo)
    layout.addStretch()
    scroll.setWidget(content)
    scroll.setWidgetResizable(True)
    scroll.resize(300, 200)
    scroll.show()
    qtbot.waitExposed(scroll)
    wheel(combo)
    assert combo.currentIndex() == 0
    assert scroll.verticalScrollBar().value() > 0
    before = scroll.verticalScrollBar().value()
    wheel(scroll.viewport())
    assert scroll.verticalScrollBar().value() - before == before


@pytest.mark.parametrize("kind", [QDialog, QMessageBox, QFileDialog])
def test_popup_buttons_never_turn_white_after_click_or_focus(dark_app, qtbot, kind):
    dialog = kind()
    qtbot.addWidget(dialog)
    if isinstance(dialog, QMessageBox):
        dialog.setText("Export this result?")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    elif isinstance(dialog, QFileDialog):
        # Exercise the styled fallback without disabling native pickers app-wide.
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    else:
        layout = QVBoxLayout(dialog)
        layout.addWidget(QPushButton("Continue"))
        layout.addWidget(QLineEdit("Filename"))
    dialog.show()
    qtbot.waitExposed(dialog)
    gc.collect()
    for button in dialog.findChildren(QPushButton):
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
            assert min(color.red(), color.green(), color.blue()) < 170, (kind, state)
    for field in dialog.findChildren(QLineEdit):
        assert field.palette().color(QPalette.Base).lightness() < 170
    assert not dark_app.testAttribute(Qt.AA_DontUseNativeDialogs)


def test_click_feedback_preserves_native_buttons_and_repeated_theme_changes(dark_app, qtbot):
    dialog = QDialog()
    qtbot.addWidget(dialog)
    layout = QVBoxLayout(dialog)
    button = QPushButton("Continue")
    layout.addWidget(button)
    box = QDialogButtonBox(QDialogButtonBox.Close)
    box.rejected.connect(dialog.reject)
    layout.addWidget(box)
    dialog.show()
    qtbot.waitExposed(dialog)
    size = button.size()
    spy = QSignalSpy(button.clicked)
    for _ in range(3):
        qtbot.mouseClick(button, Qt.LeftButton)
    assert len(spy) == 3
    effect = button.findChild(QObject, "clickFeedback")
    assert effect.animation.state() == QAbstractAnimation.Running
    qtbot.waitUntil(lambda: effect.animation.state() == QAbstractAnimation.Stopped, timeout=700)
    assert button.size() == size
    button.setFocus()
    qtbot.keyClick(button, Qt.Key_Space)
    assert len(spy) == 4
    for name in ("Light", "Dark") * 3:
        apply_theme(dark_app, name)
    gc.collect()
    assert button.findChild(QObject, "clickFeedback") is effect
    close = box.button(QDialogButtonBox.Close)
    image = close.grab().toImage()
    color = image.pixelColor(10, image.height() // 2)
    assert color.blue() > color.red() + 30
    qtbot.mouseClick(close, Qt.LeftButton)
    assert not dialog.isVisible()


@pytest.mark.parametrize("kind", [ChoiceCheckBox, QRadioButton])
def test_framed_choice_clicks_at_far_edge_and_pulse_does_not_block_input(dark_app, qtbot, kind):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    choice = kind("Option")
    layout.addWidget(choice)
    host.resize(290, 80)
    host.show()
    qtbot.waitExposed(host)
    edge = QPoint(choice.width() - 5, choice.height() // 2)
    size = choice.sizeHint()
    spy = QSignalSpy(choice.clicked)
    qtbot.mouseClick(choice, Qt.LeftButton, pos=edge)
    assert choice.isChecked() and len(spy) == 1
    effect = choice.findChild(QWidget, "clickFeedback")
    assert effect.isVisible() and effect.animation.state() == QAbstractAnimation.Running
    assert host.childAt(choice.mapTo(host, edge)) is choice
    assert choice.sizeHint() == size
    choice.setEnabled(False)
    assert not effect.isVisible()
    qtbot.mouseClick(choice, Qt.LeftButton, pos=edge)
    assert len(spy) == 1


@pytest.mark.parametrize("name", ["", "runInferenceButton", "cancelInferenceButton", "deleteSelectedButton", "secondary"])
def test_special_buttons_keep_themed_pressed_states(dark_app, qtbot, name):
    button = QPushButton("Action")
    qtbot.addWidget(button)
    button.setObjectName(name)
    button.setProperty("secondary", name == "secondary")
    button.show()
    button.setDown(True)
    image = button.grab().toImage()
    color = image.pixelColor(10, image.height() // 2)
    assert min(color.red(), color.green(), color.blue()) < 170


def test_run_and_cancel_use_subtle_blue_gradients(dark_app, qtbot):
    for name in ("runInferenceButton", "cancelInferenceButton"):
        button = QPushButton("Action")
        qtbot.addWidget(button)
        button.setObjectName(name)
        button.resize(240, 42)
        button.show()
        for enabled, pressed in ((True, False), (True, True), (False, False)):
            if not enabled and name == "runInferenceButton":
                continue
            button.setEnabled(enabled)
            button.setDown(pressed)
            image = button.grab().toImage()
            left = image.pixelColor(image.width() // 10, image.height() // 2)
            right = image.pixelColor(image.width() * 9 // 10, image.height() // 2)
            assert all(color.blue() > color.green() > color.red() for color in (left, right))
            assert right.blue() > left.blue() + 8


def test_complete_application_closes_cleanly_after_rendering_popups(tmp_path):
    code = r'''
import sys
from pathlib import Path
from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from ui.theme import apply_theme
root = Path(sys.argv[1])
app = QApplication([])
apply_theme(app, "Dark")
window = MainWindow(settings=QSettings(str(root / "settings.ini"), QSettings.IniFormat),
    db_path=root / "history.db", results_dir=root / "results", builtin_model_path=root / "missing.pth")
window.show()
window._show_settings()
window._settings_dialog.navigation.setCurrentRow(window._settings_dialog._PAGE_NAMES.index("Preferences"))
window.grab()
window._settings_dialog.grab()
message = QMessageBox(QMessageBox.Information, "Export", "Result", QMessageBox.Ok, window)
message.show()
message.button(QMessageBox.Ok).setDown(True)
message.grab()
message.close()
QTimer.singleShot(120, window.close)
app.exec_()
'''
    result = subprocess.run(
        [sys.executable, "-X", "faulthandler", "-c", code, str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
