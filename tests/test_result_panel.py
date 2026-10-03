"""Tests for result display states and image rendering."""

import pytest
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PIL import Image
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget

from ui.main_window import MainWindow
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


def assert_classification_layout(panel: ResultPanel) -> None:
	canvases = panel.findChildren(FigureCanvasQTAgg)
	assert len(canvases) == 1
	assert panel.classification_label.isVisible()
	assert panel.confidence_label.isVisible()
	assert panel.classification_label.height() > 0
	assert panel.confidence_label.height() > 0
	assert panel.classification_label.y() < panel.confidence_label.y()
	assert panel.confidence_label.y() < panel.result_canvas.y()
	assert panel.classification_label.geometry().bottom() < panel.confidence_label.y()
	assert panel.confidence_label.geometry().bottom() < panel.result_canvas.y()
	assert panel.result_canvas.height() >= 150
	assert panel.result_canvas.width() >= 300


def test_classification_and_segmentation_reuse_result_controls(qtbot) -> None:
	panel = ResultPanel()
	qtbot.addWidget(panel)
	panel.resize(900, 650)
	panel.show()
	qtbot.waitExposed(panel)
	labels = [f"Class {index}" for index in range(9)]
	figure = panel._result_figure

	for count, prediction in ((9, "MUS"), (9, "MUS"), (3, "MUS")):
		current_labels = labels[:count]
		panel.show_classification(
			prediction,
			0.5,
			[1 / count] * count,
			current_labels,
		)
		qtbot.wait(20)
		assert_classification_layout(panel)
		assert panel.classification_label.text() == prediction
		assert len(panel.get_result_figure().axes[0].patches) == count
		assert panel.get_result_figure() is figure

	panel.show_segmentation(
		Image.new("RGBA", (40, 30), (10, 20, 30, 102)),
		[("Class 0", (10, 20, 30)), ("Class 1", (220, 30, 60))],
	)
	qtbot.wait(20)
	assert panel.result_stack.currentWidget() is panel.segmentation_page
	assert panel.get_result_figure() is None

	panel.show_classification("MUS", 0.5, [0.5, 0.3, 0.2], ["MUS", "ADI", "TUM"])
	qtbot.wait(20)
	assert_classification_layout(panel)
	assert panel.get_result_figure() is figure
	assert len(panel.get_result_figure().axes[0].patches) == 3


@pytest.mark.parametrize("count", [3, 9])
def test_classification_layout_fills_result_area(qtbot, tmp_path, count) -> None:
	window = MainWindow(
		db_path=tmp_path / "history.db",
		builtin_model_path=tmp_path / "missing-model.pth",
		results_dir=tmp_path / "results",
	)
	qtbot.addWidget(window)
	window.resize(1366, 768)
	window.show()
	qtbot.waitExposed(window)

	labels = [f"Class {index}" for index in range(count)]
	window.result_panel.show_classification(
		labels[0],
		1 / count,
		[1 / count] * count,
		labels,
	)
	qtbot.wait(50)

	page = window.result_panel.classification_page
	canvas = page.findChild(FigureCanvasQTAgg)
	name_label = page.findChild(QLabel, "predictedClassLabel")
	confidence_label = page.findChild(QLabel, "confidenceLabel")
	assert canvas is not None
	assert canvas.isVisible()
	assert canvas.width() >= 300
	assert canvas.height() >= 150
	assert name_label is not None and name_label.isVisible() and name_label.height() > 0
	assert confidence_label is not None
	assert confidence_label.isVisible() and confidence_label.height() > 0
	assert window.result_panel.result_stack.height() >= 260
	assert window.result_panel.image_label.height() / window.result_panel.result_stack.height() == pytest.approx(
		2 / 3,
		rel=0.1,
	)
	assert [tick.get_text() for tick in window.result_panel.get_result_figure().axes[0].get_yticklabels()] == labels


def test_segmentation_image_and_legend_expand_side_by_side(qtbot, tmp_path) -> None:
	window = MainWindow(
		db_path=tmp_path / "history.db",
		builtin_model_path=tmp_path / "missing-model.pth",
		results_dir=tmp_path / "results",
	)
	qtbot.addWidget(window)
	window.resize(1366, 768)
	window.show()
	qtbot.waitExposed(window)
	window.result_panel.show_segmentation(
		Image.new("RGBA", (200, 120), (50, 100, 150, 102)),
		[("Class 0", (50, 100, 150)), ("Class 1", (220, 50, 80))],
	)
	qtbot.wait(50)

	page = window.result_panel.segmentation_page
	overlay_label = page.findChild(QLabel, "segmentationOverlayLabel")
	legend = page.findChild(QWidget, "segmentationLegend")
	assert overlay_label is not None and overlay_label.isVisible()
	assert legend is not None and legend.isVisible()
	assert overlay_label.width() > 300
	assert legend.width() > 100
	assert overlay_label.sizePolicy().horizontalPolicy() == QSizePolicy.Expanding
	assert overlay_label.sizePolicy().verticalPolicy() == QSizePolicy.Expanding


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