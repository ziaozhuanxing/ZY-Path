"""Interaction and preflight regressions using explicit synthetic predictions."""
from copy import deepcopy

from PIL import Image
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QFont
import pytest

from ui.classification_result import ClassificationResult
from ui.inference_panel import InferencePanel
from test_screen_fit_and_tile_grid import synthetic_result


def test_click_and_table_locate_real_edge_crop_without_changing_analysis(qtbot, tmp_path):
    result = synthetic_result(tmp_path)
    analysis = result["classification_analysis"]
    before = deepcopy(analysis)
    original = Image.open(result["image_path"]).copy()
    original.paste((220, 30, 40), (3072, 3072, 3552, 3536))
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(1050, 900)
    page.show_result(original, result["color_map"], analysis)
    page.show()
    qtbot.wait(50)
    exported_before = page.render_image().tobytes()
    view = page.image.graphics_view
    point = view.mapFromScene(QPointF(3300, 3300))
    qtbot.mouseClick(view.viewport(), Qt.LeftButton, pos=point)
    assert page.selected_tile_index == 48
    assert "Tile 49: MUC" in page.tile_inspection_text.text()
    assert "480 x 464 px" in page.tile_inspection_text.text()
    assert page.tile_preview.pixmap().toImage().pixelColor(30, 30).getRgb()[:3] == (220, 30, 40)
    assert page.table.inspection_row == 48
    assert not page.table.selectedItems()
    assert page.image._highlight_box == (3072, 3072, 3552, 3536)
    assert page.original_view._highlight_box == page.image._highlight_box
    assert page.render_image().tobytes() == exported_before
    page.tile_details_button.setChecked(True)
    qtbot.wait(30)
    assert page.table.viewport().rect().intersects(page.table.visualItemRect(page.table.item(48, 0)))
    page.table.scrollToItem(page.table.item(24, 0))
    qtbot.wait(30)
    qtbot.mouseClick(page.table.viewport(), Qt.LeftButton,
                     pos=page.table.visualItemRect(page.table.item(24, 0)).center())
    assert page.selected_tile_index == 24
    assert "Tile 25: NORM" in page.tile_inspection_text.text()
    assert not page.image.view_state()["fit"]
    assert page.image._highlight_box == tuple(analysis["tiles"][24]["box"])
    assert not page.table.selectedItems()
    page.next_tile_button.click()
    assert page.selected_tile_index == 25
    page.previous_tile_button.click()
    assert page.selected_tile_index == 24
    for mode in ("color_map", "original", "overlay"):
        page.view_mode.setCurrentIndex(page.view_mode.findData(mode))
        page.image.zoom_in()
        page.image.zoom_out()
        page.image.fit_to_view()
        assert page.image._highlight_box == tuple(analysis["tiles"][24]["box"])
    assert analysis == before
    page.clear_tile_button.click()
    assert page.selected_tile_index is None
    assert page.image._highlight_box is None
    assert page.table.inspection_row == -1
    page.inspect_tile(1)
    page.show_result(original, result["color_map"], analysis)
    assert page.selected_tile_index is None
    assert page.tile_inspector.isHidden()


def test_pan_does_not_activate_tile_and_original_pane_can_inspect(qtbot, tmp_path):
    result = synthetic_result(tmp_path)
    page = ClassificationResult()
    qtbot.addWidget(page)
    page.resize(1100, 900)
    page.show_result(Image.open(result["image_path"]), result["color_map"],
                     result["classification_analysis"])
    page.show()
    page.compare.setChecked(True)
    qtbot.wait(50)
    view = page.original_view.graphics_view
    center = view.mapFromScene(QPointF(256, 256))
    qtbot.mouseClick(view.viewport(), Qt.LeftButton, pos=center)
    assert page.selected_tile_index == 0
    page.clear_tile_inspection()
    viewport = page.image.graphics_view.viewport()
    point = viewport.rect().center()
    qtbot.mousePress(viewport, Qt.LeftButton, pos=point)
    qtbot.mouseMove(viewport, point + QPoint(60, 30))
    qtbot.mouseRelease(viewport, Qt.LeftButton, pos=point + QPoint(60, 30))
    assert page.selected_tile_index is None
    page.clear()
    assert page.image._highlight_box is None


def test_preflight_summary_tracks_model_size_mode_and_actual_grid(qtbot, tmp_path):
    image = tmp_path / "source.png"
    Image.new("RGB", (3552, 3536)).save(image)
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_builtin_model_names({"classification": "chosen-classifier.pth",
                                   "segmentation": "chosen-segmenter.pth"})
    panel.set_image(str(image))
    panel.set_classification_mode("tiled_analysis")
    text = panel.mode_summary.text()
    for value in ("chosen-classifier.pth", "3552 x 3536", "49 (7 columns x 7 rows)",
                  "512 x 512", "pillow_bilinear"):
        assert value in text
    panel.set_classification_parameters({"tile_size": [1024, 512], "resize_backend": "opencv_linear"})
    assert "28 (4 columns x 7 rows)" in panel.mode_summary.text()
    assert "opencv_linear" in panel.mode_summary.text()
    panel.set_classification_mode("single_image")
    assert "Single image" in panel.mode_summary.text()
    assert "Planned tiles" not in panel.mode_summary.text()
    panel.set_custom_model(str(tmp_path / "custom.pth"))
    assert "Model: custom.pth" in panel.mode_summary.text()
    panel.set_use_builtin(True)
    panel.set_task("segmentation")
    assert "chosen-segmenter.pth" in panel.mode_summary.text()
    assert "Resize:" not in panel.mode_summary.text()
    assert "Planned tiles:" not in panel.mode_summary.text()
    panel.set_image(str(tmp_path / "missing.png"))
    assert "Image: not selected" in panel.mode_summary.text()


@pytest.mark.parametrize("points", [10, 20])
def test_inspection_keeps_image_visible_in_small_scrollable_result(qtbot, tmp_path, points):
    result = synthetic_result(tmp_path)
    page = ClassificationResult()
    qtbot.addWidget(page)
    font = QFont(page.font())
    font.setPointSize(points)
    page.setFont(font)
    page.resize(360, 400)
    page.show_result(Image.open(result["image_path"]), result["color_map"],
                     result["classification_analysis"])
    page.show()
    page.inspect_tile(48)
    qtbot.wait(40)
    assert page.width() == 360 and page.height() == 400
    assert page.image.graphics_view.viewport().height() >= 60
    assert page.image_page_scroll.verticalScrollBar().maximum() > 0
    page.image_page_scroll.ensureWidgetVisible(page.tile_inspector)
    qtbot.wait(20)
    assert page.tile_preview.isVisible()
    assert page.inspection_scroll.viewport().height() >= 60
    assert "480 x 464" in page.tile_inspection_text.text()
