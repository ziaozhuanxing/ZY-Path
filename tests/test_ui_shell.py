"""Tests for the layout-only user interface shell."""

from PyQt5.QtCore import Qt
import re

from PyQt5.QtGui import QPixmap
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

    window.show()
    qtbot.waitExposed(window)
    assert splitter.widget(0).minimumWidth() >= 240
    assert splitter.widget(0).maximumWidth() == 420
    assert splitter.widget(1).minimumWidth() == 500
    assert splitter.widget(2).minimumWidth() == 200
    assert splitter.widget(2).maximumWidth() == 360
    assert splitter.widget(0).width() >= splitter.widget(0).minimumWidth()
    assert splitter.widget(2).width() == 240
    assert splitter.handleWidth() == 6
    assert not splitter.childrenCollapsible()
    assert splitter.handle(1).isVisible()
    assert splitter.handle(1).width() == 6
    assert "#CBD5E0" in splitter.styleSheet()
    assert "#3182CE" in splitter.styleSheet()

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


def test_splitter_drag_keeps_panel_contents_inside_bounds(qtbot, tmp_path) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    pixmap = QPixmap(900, 400)
    pixmap.fill(Qt.red)
    image_path = tmp_path / "preview.png"
    assert pixmap.save(str(image_path))
    window.inference_panel.set_image(str(image_path))
    window.action_panel.set_metadata(
        "A very long model name that needs to wrap safely",
        "A very long image filename that needs to wrap safely.png",
        "2026-10-04 12:34:56 UTC",
    )

    splitter = window.splitter
    left_panel = window.inference_panel
    _move_left_splitter(splitter, 420)
    qtbot.wait(50)
    assert left_panel.width() == 420
    assert left_panel.thumbnail_label.width() <= left_panel.contentsRect().width()
    assert left_panel.thumbnail_label.pixmap().width() <= left_panel.thumbnail_label.width()
    for control in (
        left_panel.built_in_checkbox,
        left_panel.browse_model_button,
        left_panel.upload_image_button,
        left_panel.run_button,
    ):
        assert control.geometry().right() <= left_panel.rect().right()

    _move_left_splitter(splitter, left_panel.minimumWidth())
    qtbot.wait(50)
    assert left_panel.width() == left_panel.minimumWidth()
    assert left_panel.thumbnail_label.width() <= left_panel.contentsRect().width()
    for control in (
        left_panel.built_in_checkbox,
        left_panel.browse_model_button,
        left_panel.upload_image_button,
        left_panel.run_button,
    ):
        assert control.geometry().right() <= left_panel.rect().right()

    splitter.setSizes([280, 500, 200])
    qtbot.wait(50)
    right_panel = window.action_panel
    assert right_panel.width() == 200
    for control in (
        right_panel.export_png_button,
        right_panel.export_pdf_button,
        right_panel.rerun_button,
        *right_panel.metadata_labels.values(),
    ):
        assert control.geometry().right() <= right_panel.rect().right()


def _move_left_splitter(splitter: QSplitter, target_width: int) -> None:
    splitter.moveSplitter(target_width, 1)
    QApplication.processEvents()