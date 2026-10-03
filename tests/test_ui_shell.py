"""Tests for the layout-only user interface shell."""

from PyQt5.QtCore import Qt
import re

from PyQt5.QtWidgets import QApplication, QLabel, QSplitter, QTabWidget, QWidget

from ui.action_panel import ActionPanel
from ui.history_panel import HistoryPanel
from ui.inference_panel import InferencePanel
from ui.main_window import MainWindow
from ui.result_panel import ResultPanel
from ui.theme import apply_theme


def test_main_window_has_expected_shell(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.windowTitle() == "ZY-Path"
    assert window.minimumSize().width() == 1366
    assert window.minimumSize().height() == 768
    assert window.statusBar().currentMessage() == "Ready"

    splitter = window.splitter
    assert isinstance(splitter, QSplitter)
    assert splitter.count() == 3
    assert isinstance(splitter.widget(0), InferencePanel)
    assert isinstance(splitter.widget(1), QTabWidget)
    assert isinstance(splitter.widget(2), ActionPanel)
    assert splitter.widget(0).width() == 280
    assert splitter.widget(2).width() == 240

    tabs = window.tabs
    assert tabs.count() == 2
    assert tabs.tabText(0) == "Inference"
    assert tabs.tabText(1) == "History"
    assert isinstance(tabs.widget(0), ResultPanel)
    assert isinstance(tabs.widget(1), HistoryPanel)


def test_window_can_be_shown_without_crashing(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    window.show()
    qtbot.waitExposed(window)
    assert window.isVisible()


def test_main_window_contains_all_panels_in_expected_tabs(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    for panel_type in (InferencePanel, ResultPanel, HistoryPanel, ActionPanel):
        assert len(window.findChildren(panel_type)) == 1

    assert isinstance(window.tabs.widget(0), ResultPanel)
    assert isinstance(window.tabs.widget(1), HistoryPanel)


def test_global_label_background_is_transparent(qtbot) -> None:
    application = QApplication.instance()
    assert application is not None
    previous_stylesheet = application.styleSheet()

    apply_theme(application)
    stylesheet = application.styleSheet()
    application.setStyleSheet(previous_stylesheet)

    assert re.search(
        r"QLabel,\s*QCheckBox,\s*QRadioButton,\s*QGroupBox\s*\{\s*"
        r"background:\s*transparent;",
        stylesheet,
    )


def test_title_bar_sizes_labels_from_font_metrics(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    title_bar = window.findChild(QWidget, "titleBar")
    title = window.findChild(QLabel, "titleText")
    subtitle = window.findChild(QLabel, "subtitleText")

    assert title_bar is not None
    assert title is not None
    assert subtitle is not None
    assert title.height() >= title.fontMetrics().height()
    assert subtitle.height() >= subtitle.fontMetrics().height()
    assert title_bar.layout().getContentsMargins() == (24, 10, 24, 10)
    assert title_bar.minimumHeight() == (
        title.minimumHeight()
        + subtitle.minimumHeight()
        + 10
        + 10
        + 2
    )


def test_all_panels_enable_styled_background(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    panels = [
        window.inference_panel,
        window.action_panel,
        window.result_panel,
        window.history_panel,
    ]

    assert all(panel.testAttribute(Qt.WA_StyledBackground) for panel in panels)