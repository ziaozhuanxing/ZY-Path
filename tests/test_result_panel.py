"""Tests for result display states and image rendering."""

from PIL import Image
from PyQt5.QtWidgets import QLabel

from ui.result_panel import ResultPanel


def test_empty_state_and_clear(qtbot) -> None:
	panel = ResultPanel()
	qtbot.addWidget(panel)

	assert panel.image_label.text() == "Upload an image and run inference"
	assert panel.result_stack.currentWidget() is panel.empty_page
	assert panel.get_result_figure() is None

	panel.show_classification("benign", 0.947, [0.02, 0.947, 0.033], ["a", "benign", "c"])
	panel.clear()

	assert panel.result_stack.currentWidget() is panel.empty_page
	assert panel.image_label.text() == "Upload an image and run inference"
	assert panel.get_result_figure() is None


def test_classification_handles_three_and_nine_classes(qtbot) -> None:
	panel = ResultPanel()
	qtbot.addWidget(panel)

	for count in (3, 9):
		labels = [f"class-{index}" for index in range(count)]
		probabilities = [1 / count] * count
		panel.show_classification(labels[0], probabilities[0], probabilities, labels)
		figure = panel.get_result_figure()

		assert figure is not None
		assert len(figure.axes[0].patches) == count
		assert panel.result_stack.currentWidget() is panel.classification_page


def test_segmentation_displays_pil_overlay_and_legend(qtbot) -> None:
	panel = ResultPanel()
	qtbot.addWidget(panel)
	image = Image.new("RGBA", (12, 8), (30, 120, 210, 128))

	panel.show_segmentation(image, [("tumor", (30, 120, 210)), ("background", (0, 0, 0))])

	assert panel.result_stack.currentWidget() is panel.segmentation_page
	assert not panel.overlay_label.pixmap().isNull()
	assert panel.get_result_figure() is None
	legend_names = [
		label.text()
		for label in panel.segmentation_page.findChildren(QLabel)
		if label.text()
	]
	assert "tumor" in legend_names
	assert "background" in legend_names


def test_show_image_loads_and_preserves_source(qtbot, tmp_path) -> None:
	panel = ResultPanel()
	qtbot.addWidget(panel)
	image_path = tmp_path / "sample.png"
	Image.new("RGB", (20, 10), "white").save(image_path)

	panel.show_image(image_path)

	assert not panel._source_pixmap.isNull()