"""Sampling units, honest region previews, square linking and visible arrows."""

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QStyle, QStyleOptionSpinBox

from test_guided_input_setup import panel_image
from ui.input_setup import InputSetupDialog, SamplingDiagram
from ui.input_plan import InputPreview
from ui.theme import apply_theme


def test_mpp_inverse_relationship_and_preview_ratios(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, size=(2240, 2240), mpp=[.1, .1])
    dialog = InputSetupDialog(panel, prefer_matching=True)
    qtbot.addWidget(dialog)
    dialog.resize(720, 680)
    dialog.show()
    for mpp, expected in ((.1, 1120), (.5, 224)):
        dialog.editor.manual.setChecked(True)
        dialog.editor.mpp_boxes[0].setValue(mpp)
        assert dialog.preview.tile == (expected, expected)
        diagram = dialog.diagram
        assert diagram.region_rect.width() / diagram.source_rect.width() == pytest.approx(expected / 2240)
    assert "model tissue field / MPP" in dialog.mode_explanation.text()


def test_oversized_region_is_not_silently_clipped(qtbot):
    diagram = SamplingDiagram()
    qtbot.addWidget(diagram)
    diagram.resize(700, 120)
    image = QPixmap(800, 600)
    image.fill(Qt.red)
    diagram.set_plan(image, InputPreview(tile=(1120, 1120), network=(224, 224), problem="No complete field fits"))
    assert not diagram.region_fits
    assert diagram.region_rect.height() > diagram.source_rect.height()
    assert diagram.region_rect.width() / diagram.source_rect.width() == pytest.approx(1120 / 800)


def test_valid_partial_pixel_tile_previews_the_crop_that_will_be_resized(qtbot):
    diagram = SamplingDiagram()
    qtbot.addWidget(diagram)
    diagram.resize(700, 120)
    image = QPixmap(80, 60)
    image.fill(Qt.red)
    diagram.set_plan(image, InputPreview(tile=(224, 224), network=(224, 224),
                                        grid=(1, 1), edge="crop_then_resize"))
    assert diagram.region_rect == diagram.source_rect
    # The model preview contains the valid small crop, rather than an error.
    rendered = diagram.pixmap().toImage()
    ratio = rendered.devicePixelRatio()
    assert rendered.pixelColor(round(550 * ratio), round(60 * ratio)).name() == "#ff0000"


def test_square_links_both_axes_and_cancel_preserves_panel(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path)
    before = dict(panel._classification_parameters)
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    dialog.pixel_mode.setChecked(True)
    dialog.analysis_mode.setCurrentIndex(dialog.analysis_mode.findData("tiled_analysis"))
    width, height = dialog.tile_boxes
    width.setValue(300)
    height.setValue(200)
    dialog.square_checkbox.setChecked(True)
    assert width.value() == height.value() == 300
    height.setValue(128)
    assert width.value() == height.value() == 128
    width.setValue(256)
    assert width.value() == height.value() == 256
    assert dialog.choices()["pixel_tile"] == [256, 256]
    dialog.square_checkbox.setChecked(False)
    height.setValue(192)
    assert dialog.choices()["pixel_tile"] == [256, 192]
    dialog.reject()
    assert panel._classification_parameters == before


@pytest.mark.parametrize("theme", ["Light", "Dark"])
def test_spin_arrows_are_rendered_and_clickable(qtbot, qapp, tmp_path, theme):
    previous = qapp.property("zyTheme") or "Light"
    apply_theme(qapp, theme)
    try:
        panel, _ = panel_image(qtbot, tmp_path)
        dialog = InputSetupDialog(panel)
        qtbot.addWidget(dialog)
        dialog.pixel_mode.setChecked(True)
        dialog.analysis_mode.setCurrentIndex(dialog.analysis_mode.findData("tiled_analysis"))
        dialog.show()
        box = dialog.tile_boxes[0]
        dialog.scroll.ensureWidgetVisible(box)
        qtbot.wait(20)
        option = QStyleOptionSpinBox()
        box.initStyleOption(option)
        for control, change in ((QStyle.SC_SpinBoxUp, 1), (QStyle.SC_SpinBoxDown, -1)):
            rect = box.style().subControlRect(QStyle.CC_SpinBox, option, control, box)
            image = box.grab().toImage()
            ratio = image.devicePixelRatio()
            colors = {image.pixelColor(round(x * ratio), round(y * ratio)).name()
                      for x in range(rect.left()+3, rect.right()-2)
                      for y in range(rect.top()+1, rect.bottom())}
            assert len(colors) > 3  # The SVG stroke and antialiased edges are painted.
            value = box.value()
            qtbot.mouseClick(box, Qt.LeftButton, pos=rect.center())
            assert box.value() == value + change
    finally:
        apply_theme(qapp, previous)
