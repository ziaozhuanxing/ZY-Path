"""Tests for action panel state and emitted requests."""

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy

from ui.action_panel import ActionPanel


def test_buttons_start_disabled(qtbot) -> None:
	panel = ActionPanel()
	qtbot.addWidget(panel)

	assert panel.width() == 240
	assert not panel.export_png_button.isEnabled()
	assert not panel.export_pdf_button.isEnabled()
	assert not panel.rerun_button.isEnabled()
	assert [panel.metadata_labels[key].text() for key in ("model", "image", "time")] == [
		"-",
		"-",
		"-",
	]


def test_state_methods_update_buttons_and_metadata(qtbot) -> None:
	panel = ActionPanel()
	qtbot.addWidget(panel)

	panel.set_metadata("Built-in", "sample.png", "2026-10-03 10:00")
	panel.set_result_available(True)
	panel.set_rerun_enabled(True)

	assert [panel.metadata_labels[key].text() for key in ("model", "image", "time")] == [
		"Built-in",
		"sample.png",
		"2026-10-03 10:00",
	]
	assert panel.export_png_button.isEnabled()
	assert panel.export_pdf_button.isEnabled()
	assert panel.rerun_button.isEnabled()

	panel.clear()
	assert not panel.export_png_button.isEnabled()
	assert not panel.export_pdf_button.isEnabled()
	assert not panel.rerun_button.isEnabled()


def test_clicks_emit_requested_signals(qtbot) -> None:
	panel = ActionPanel()
	qtbot.addWidget(panel)
	panel.set_result_available(True)
	panel.set_rerun_enabled(True)
	png_spy = QSignalSpy(panel.export_png_requested)
	pdf_spy = QSignalSpy(panel.export_pdf_requested)
	rerun_spy = QSignalSpy(panel.rerun_requested)

	qtbot.mouseClick(panel.export_png_button, Qt.LeftButton)
	qtbot.mouseClick(panel.export_pdf_button, Qt.LeftButton)
	qtbot.mouseClick(panel.rerun_button, Qt.LeftButton)

	assert len(png_spy) == 1
	assert len(pdf_spy) == 1
	assert len(rerun_spy) == 1