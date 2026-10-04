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
	assert [panel.metadata_labels[key].text() for key in ("model", "image", "time", "record")] == [
		"-",
		"-",
		"-",
		"-",
	]
	assert panel.rerun_button.toolTip() == "Select a history record first"


def test_state_methods_update_buttons_and_metadata(qtbot) -> None:
	panel = ActionPanel()
	qtbot.addWidget(panel)

	panel.set_metadata("Built-in", "sample.png", "2026-10-03 10:00", 27)
	panel.set_result_available(True)
	panel.set_rerun_enabled(True, 27)

	assert [panel.metadata_labels[key].text() for key in ("model", "image", "time", "record")] == [
		"Built-in",
		"sample.png",
		"2026-10-03 10:00",
		"#27",
	]
	assert panel.export_png_button.isEnabled()
	assert panel.export_pdf_button.isEnabled()
	assert panel.rerun_button.isEnabled()
	assert panel.rerun_button.toolTip() == (
		"Re-run record #27 with the same image, model and task"
	)

	panel.clear()
	assert not panel.export_png_button.isEnabled()
	assert not panel.export_pdf_button.isEnabled()
	assert not panel.rerun_button.isEnabled()
	assert panel.metadata_labels["record"].text() == "-"
	assert panel.rerun_button.toolTip() == "Select a history record first"


def test_session_values_wrap_and_keep_full_text_in_tooltips(qtbot) -> None:
	panel = ActionPanel()
	qtbot.addWidget(panel)
	panel.resize(240, 700)
	values = {
		"model": "builtin_model.pth",
		"image": "sample_" + "unbrokenfilename" * 8 + ".png",
		"time": "2026-10-03 23:24:44",
	}

	panel.set_metadata(values["model"], values["image"], values["time"])
	panel.show()
	qtbot.waitExposed(panel)
	qtbot.wait(20)

	for key, value in values.items():
		label = panel.metadata_labels[key]
		assert label.wordWrap()
		assert label.toolTip() == value
		required_height = label.fontMetrics().boundingRect(
			0,
			0,
			label.width(),
			10000,
			Qt.TextWordWrap,
			value,
		).height()
		assert label.height() >= required_height


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