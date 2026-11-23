"""Exercise user choices, cancel/apply, and preview/inference agreement."""
from ui_test_helpers import wait_for_history_idle
from ui_test_helpers import wait_for_model_idle

import json
from pathlib import Path

import pytest
from PIL import Image, PngImagePlugin
from PyQt5.QtCore import QSettings, QTimer, Qt, QPoint, QPointF
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
import torch
from torch import nn

from core.image_calibration import ImageCalibration
from core.model_profile import ModelInputProfile, SCHEMA, CRC_SHA256, UPERNET_SHA256, known_profile, file_sha256
from core.model_loader import ModelLoader
from core.inference_engine import InferenceEngine
from core.sampling_plan import classification_grid, segmentation_grid
from core.classification_tiles import validate_classification_workload, ClassificationWorkloadError
from core.large_image_segmentation import predict_large_image, tile_positions
from ui.inference_panel import InferencePanel
from ui.input_setup import InputSetupDialog
from ui.input_configuration import ModelFieldCalculator, ModelInputDialog
from ui.input_plan import input_preview
from ui.main_window import MainWindow
from ui.theme import apply_theme


class MeanClassifier(nn.Module):
    def forward(self, value):
        return value.mean((2, 3))


def profile(**changes):
    return ModelInputProfile.from_dict({"schema": SCHEMA, "model_sha256": "2" * 64,
        "task_type": "classification", "classes": ["a", "b", "c"], "input_size": [8, 8],
        "normalization": "raw255", "input_scope": "patch", "field_um": [4, 4],
        "tile_size": [8, 8], "stride": [8, 8], **changes})


def panel_image(qtbot, tmp_path, model_profile=None, size=(888, 888), mpp=None):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_active_input_profile(model_profile or known_profile(CRC_SHA256))
    path = tmp_path / "image.png"
    meta = PngImagePlugin.PngInfo()
    if mpp:
        meta.add_text("zypath.calibration", json.dumps({"schema": "zypath.image-calibration.v1",
            "image_size_px": list(size), "pixel_size_um": mpp}))
    Image.new("RGB", size, (150, 80, 100)).save(path, pnginfo=meta)
    panel.set_image(str(path))
    return panel, path


def modal_action(panel, action):
    def interact():
        dialog = panel._input_setup_dialog
        try:
            action(dialog)
        finally:
            if dialog.isVisible():
                dialog.reject()
    QTimer.singleShot(0, interact)
    panel.image_scale_button.click()


def test_unknown_mpp_to_live_crop_preview_to_tiled_matching(qtbot, tmp_path):
    panel, path = panel_image(qtbot, tmp_path)
    before = panel.input_options()
    def choose(dialog):
        assert dialog.pixel_mode.isChecked()
        assert dialog.apply_button.isEnabled()
        dialog.physical_mode.click()
        assert not dialog.apply_button.isEnabled()
        assert dialog.editor.manual.isChecked()
        dialog.editor.mpp_boxes[0].setFocus()
        dialog.editor.mpp_boxes[0].selectAll()
        qtbot.keyClicks(dialog.editor.mpp_boxes[0], "0.252")
        assert dialog.editor.values() == [.252, .252]
        assert dialog.preview.tile == (444, 444)
        assert dialog.planned_mode == "tiled_analysis"
        assert panel.input_options() == before  # Edits are staged until Apply.
        assert dialog.preview.count == 4
        assert "444 × 444" in dialog.preview_label.text()
        assert dialog.apply_button.isEnabled()
        dialog.apply_button.click()
    modal_action(panel, choose)
    assert panel.input_options() == {"match_scale": True, "manual_mpp": [.252, .252], "expected_image_identity": panel._image_snapshot}
    assert panel.classification_mode() == "tiled_analysis"
    assert panel.run_button.isEnabled()
    assert "4 tiles" in panel.plan_compact_label.text()
    assert "444 x 444" in panel.run_button.toolTip()
    assert not path.with_name(path.name + ".calibration.json").exists()


def test_file_calibration_requires_no_typing_and_cancel_preserves_input(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, mpp=[.252, .252])
    original = panel.input_options()
    def cancel(dialog):
        assert dialog.editor.auto.isChecked()
        dialog.physical_mode.click()
        assert dialog.preview.tile == (444, 444)
        dialog.editor.manual.click()
        dialog.editor.mpp_boxes[0].setValue(.5)
        dialog.reject()
    modal_action(panel, cancel)
    assert panel.input_options() == original
    assert panel.classification_mode() == "single_image"
    assert not panel.match_scale_checkbox.isChecked()
    def apply(dialog):
        assert dialog.editor.auto.isChecked()
        dialog.physical_mode.click()
        dialog.apply_button.click()
    modal_action(panel, apply)
    assert panel.match_scale_checkbox.isChecked()
    assert panel.input_options()["manual_mpp"] is None
    assert panel._image_calibration.source != "manual entry"


def test_upernet_sampling_shows_nominal_scale_and_uses_fixed_pixel_crop(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, known_profile(UPERNET_SHA256, upernet=True), size=(3552, 3536), mpp=[.5, .5])
    panel.set_task("segmentation")
    panel.set_active_input_profile(known_profile(UPERNET_SHA256, upernet=True))
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    assert dialog.physical_mode.isEnabled()
    assert dialog.pixel_mode.isChecked()
    assert "0.300" in dialog.model_info.text()
    assert "67.2" in dialog.model_info.text()
    assert dialog.preview.tile == (1000, 1000)
    assert dialog.preview.stride == (512, 512)
    assert dialog.preview.network == (224, 224)
    assert dialog.preview.count == 36
    assert dialog.apply_button.isEnabled()
    assert dialog.choices()["match_scale"] is False


def test_upernet_matching_from_unrecorded_mpp_applies_and_reopens(qtbot, tmp_path):
    model_profile = known_profile(UPERNET_SHA256, upernet=True)
    panel, _ = panel_image(qtbot, tmp_path, model_profile, size=(480, 279))
    panel.set_task("segmentation")
    panel.set_active_input_profile(model_profile)

    def apply(dialog):
        assert dialog.pixel_mode.isChecked()
        dialog.physical_mode.click()
        assert dialog.editor.manual.isChecked()
        assert not dialog.image_group.isHidden()
        assert not dialog.apply_button.isEnabled()
        dialog.editor.mpp_boxes[0].setValue(.252)
        assert dialog.preview.tile == (267, 267)
        assert dialog.preview.stride == (137, 137)
        assert dialog.preview.grid == (3, 2)
        assert dialog.apply_button.isEnabled()
        dialog.apply_button.click()

    modal_action(panel, apply)
    assert panel.task_type() == "segmentation"
    assert panel.input_options()["match_scale"] is True
    assert panel.input_options()["manual_mpp"] == [.252, .252]
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    assert dialog.physical_mode.isChecked()
    assert dialog.preview.tile == (267, 267)
    dialog.pixel_mode.click()
    assert dialog.preview.tile == (1000, 1000)
    assert dialog.preview.stride == (512, 512)


def test_matching_typing_is_sufficient_and_reopening_keeps_the_choice(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, size=(2035, 1061))
    def apply(dialog):
        assert not panel.match_scale_checkbox.isVisible()
        dialog.physical_mode.click()
        assert dialog.editor.manual.isChecked()
        dialog.editor.mpp_boxes[0].setValue(.121)
        assert dialog.preview.tile == (926, 926)
        assert dialog.preview.count == 2
        assert dialog.planned_mode == 'tiled_analysis'
        assert "switches the task to Tiled analysis" in dialog.issues.text()
        assert dialog.apply_button.isEnabled()
        dialog.apply_button.click()
    modal_action(panel, apply)
    assert panel.match_scale_checkbox.isChecked()
    def reopen(dialog):
        assert dialog.physical_mode.isChecked()
        assert dialog.editor.values() == [.121, .121]
        assert dialog.preview.count == 2
        dialog.pixel_mode.click()
        assert dialog.tile_row.isVisible()
        assert dialog.tile_boxes[0].value() == 224
        assert '0.121' in dialog.calibration_summary.text()
        assert dialog.preview.count == 50
        dialog.apply_button.click()
    modal_action(panel, reopen)
    assert not panel.match_scale_checkbox.isChecked()
    assert panel.input_options()['manual_mpp'] == [.121, .121]
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    assert dialog.pixel_mode.isChecked()
    assert dialog.editor.values() == [.121, .121]


def test_run_and_history_restore_manual_mpp_with_the_verified_image(qtbot, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(MainWindow, '_load_builtin_model', lambda self: None)
    window = MainWindow(settings=QSettings(str(tmp_path / 'prefs.ini'), QSettings.IniFormat),
        db_path=tmp_path / 'history.db', results_dir=tmp_path / 'results')
    qtbot.addWidget(window)
    model = tmp_path / 'mean.pt'
    torch.jit.script(MeanClassifier()).save(str(model))
    model.with_name(model.name + '.zypath-model.json').write_text(json.dumps(profile(model_sha256=file_sha256(model)).to_dict()))
    panel = window.inference_panel
    panel.set_custom_model(str(model))
    wait_for_model_idle(qtbot, panel)
    qtbot.waitUntil(lambda: model in window._model_input_cache, timeout=10000)
    source = tmp_path / 'image.png'
    Image.new('RGB', (16, 16), (150, 80, 100)).save(source)
    panel.set_image('image.png')
    def apply(dialog):
        dialog.physical_mode.click()
        dialog.editor.mpp_boxes[0].setValue(.5)
        dialog.apply_button.click()
    modal_action(panel, apply)
    panel.run_button.click()
    qtbot.waitUntil(lambda: window._inference_engine is None and window.current_record_id is not None, timeout=10000)
    record_id = window.current_record_id
    assert panel._manual_mpp == (.5, .5)
    assert panel.match_scale_checkbox.isChecked()
    panel.set_image(str(source.resolve()))
    assert panel._manual_mpp == (.5, .5)
    assert panel.match_scale_checkbox.isChecked()
    other = tmp_path / 'other.png'
    Image.new('RGB', (16, 16), (100, 20, 30)).save(other)
    panel.set_image(str(other))
    assert panel._manual_mpp is None
    window._show_record_activated(record_id)
    wait_for_history_idle(qtbot, window)
    assert panel._manual_mpp == (.5, .5)
    assert panel.match_scale_checkbox.isChecked()
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    assert dialog.editor.values() == [.5, .5]
    assert dialog.preview.count == 4


def test_setup_pixel_tiles_are_transactional_and_ordinary_run_uses_them(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    window = MainWindow(settings=settings, db_path=tmp_path / "db.sqlite", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    model = tmp_path / "model.pth"
    torch.jit.script(MeanClassifier()).save(str(model))
    model.with_name(model.name + ".zypath-model.json").write_text(json.dumps(profile(model_sha256=file_sha256(model)).to_dict()))
    panel = window.inference_panel
    panel.set_custom_model(str(model))
    wait_for_model_idle(qtbot, panel)
    image = tmp_path / "small.png"
    Image.new("RGB", (16, 12), (150, 80, 100)).save(image)
    panel.set_image(str(image))
    window._show_settings()
    window._settings_dialog.hide()
    previous = window._classification_preferences()
    panel.set_classification_mode("tiled_analysis")

    def cancel(dialog):
        dialog.pixel_mode.click()
        dialog.tile_boxes[0].setValue(8)
        dialog.tile_boxes[1].setValue(6)
        dialog.reject()
    modal_action(panel, cancel)
    assert window._classification_preferences() == previous
    def apply(dialog):
        dialog.pixel_mode.click()
        dialog.tile_boxes[0].setValue(8)
        dialog.tile_boxes[1].setValue(6)
        assert dialog.preview.count == 4
        dialog.apply_button.click()
    modal_action(panel, apply)
    assert window._classification_preferences() == previous
    assert panel.classification_parameters()["tile_size"] == [8, 6]
    assert window._settings_dialog.tile_width.value() == previous["tile_size"][0]
    assert window._settings_dialog.tile_height.value() == previous["tile_size"][1]
    panel.run_button.click()
    qtbot.waitUntil(lambda: window._inference_engine is None and window.current_record_id is not None, timeout=10000)
    record = window.database_manager.get_record_by_id(window.current_record_id)
    assert json.loads(record["analysis_json"])["tile_size"] == [8, 6]
    assert len(json.loads(record["analysis_json"])["tiles"]) == 4
    assert panel.image_scale_button.isEnabled()
    assert panel.classification_parameters()["tile_size"] == [8, 6]
    other_image = tmp_path / "another-image.png"
    Image.new("RGB", (16, 12), (150, 80, 100)).save(other_image)
    panel.set_image(str(other_image))
    assert panel.classification_parameters()["tile_size"] == previous["tile_size"]

    # Persistent dimensions are changed in Preferences only.
    window._settings_dialog.tile_width.setValue(8)
    window._settings_dialog.tile_height.setValue(6)
    assert window._classification_preferences()["tile_size"] == [8, 6]


def test_too_small_matched_field_has_explicit_pixel_mode_recovery(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, size=(224, 224), mpp=[.252, .252])
    dialog = InputSetupDialog(panel, prefer_matching=True)
    qtbot.addWidget(dialog)
    assert not dialog.apply_button.isEnabled()
    assert "no complete field fits" in dialog.issues.text()
    dialog.pixel_mode.click()
    assert dialog.apply_button.isEnabled()
    assert dialog.preview.count == 1


def test_model_requirements_opens_above_the_guided_modal(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    window = MainWindow(settings=QSettings(str(tmp_path / "prefs.ini"), QSettings.IniFormat),
                        db_path=tmp_path / "history.sqlite", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    model = tmp_path / "model.pth"
    torch.jit.script(MeanClassifier()).save(str(model))
    panel = window.inference_panel
    panel.set_custom_model(str(model))
    wait_for_model_idle(qtbot, panel)
    qtbot.waitUntil(lambda: model.resolve() in window._model_input_cache, timeout=10000)
    image = tmp_path / "image.png"
    Image.new("RGB", (16, 16)).save(image)
    panel.set_image(str(image))
    parents = []
    class CancelModelEditor(ModelInputDialog):
        def exec_(self):
            parents.append(self.parentWidget())
            return self.Rejected
    monkeypatch.setattr("ui.input_configuration.ModelInputDialog", CancelModelEditor)
    def check_parent(dialog):
        assert QApplication.activeModalWidget() is dialog
        dialog.model_button.click()
        assert parents == [dialog]
        dialog.reject()
    modal_action(panel, check_parent)


def test_coarse_image_is_explained_without_claiming_detail_is_restored(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, profile(), size=(16, 16), mpp=[1, 1])
    panel.set_classification_mode("tiled_analysis")
    dialog = InputSetupDialog(panel, prefer_matching=True)
    qtbot.addWidget(dialog)
    assert dialog.apply_button.isEnabled()
    assert "cannot recover missing tissue detail" in dialog.issues.text()


def test_same_filename_replacement_clears_manual_calibration(qtbot, tmp_path):
    panel, path = panel_image(qtbot, tmp_path)
    panel._manual_mpp = [.252, .252]
    panel._refresh_scale_information()
    panel.match_scale_checkbox.setChecked(True)
    Image.new("RGB", (32, 16), (200, 50, 70)).save(path)
    panel.set_image(str(path))
    assert panel.input_options() == {"match_scale": False, "manual_mpp": None, "expected_image_identity": panel._image_snapshot}
    assert (panel._source_pixmap.width(), panel._source_pixmap.height()) == (32, 16)


def test_changing_reader_reloads_exif_axes_and_clears_manual_mpp(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_active_input_profile(profile(image_decoder="pillow_rgb"))
    image = tmp_path / "rotated.jpg"
    exif = Image.Exif(); exif[274] = 6
    Image.new("RGB", (12, 8), (150, 80, 100)).save(image, exif=exif)
    panel.set_image(str(image))
    assert (panel._source_pixmap.width(), panel._source_pixmap.height()) == (12, 8)
    panel._manual_mpp = [.252, .5]
    panel._refresh_scale_information()
    panel.set_active_input_profile(profile(image_decoder="opencv_color"))
    assert panel.input_options() == {"match_scale": False, "manual_mpp": None, "expected_image_identity": panel._image_snapshot}
    assert (panel._source_pixmap.width(), panel._source_pixmap.height()) == (8, 12)
    assert panel._image_calibration.image_size == (8, 12)


def test_changing_task_without_a_profile_updates_the_preview_reader(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    image = tmp_path / "rotated.jpg"
    exif = Image.Exif(); exif[274] = 6
    Image.new("RGB", (12, 8), (150, 80, 100)).save(image, exif=exif)
    panel.set_image(str(image))
    assert (panel._source_pixmap.width(), panel._source_pixmap.height()) == (8, 12)
    panel._manual_mpp = [.252, .5]
    panel._refresh_scale_information()
    panel.set_task("segmentation")
    assert panel.input_options()["manual_mpp"] is None
    assert (panel._source_pixmap.width(), panel._source_pixmap.height()) == (12, 8)
    assert panel._image_calibration.image_size == (12, 8)


def test_setup_rejects_an_image_changed_while_open(qtbot, tmp_path):
    panel, path = panel_image(qtbot, tmp_path)
    before = panel.input_options()
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    dialog.pixel_mode.click()
    Image.new("RGB", (32, 16)).save(path)
    dialog.accept()
    assert dialog.result() != dialog.Accepted
    assert not dialog.apply_button.isEnabled()
    assert "changed on disk" in dialog.issues.text()
    assert panel.input_options() == before


def test_live_pixel_workload_limit_can_be_fixed_in_the_same_dialog(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path, profile(), size=(128, 128))
    panel.set_classification_mode("tiled_analysis")
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    for box in dialog.tile_boxes: box.setValue(1)
    assert not dialog.apply_button.isEnabled()
    assert "10,000" in dialog.issues.text()
    for box in dialog.tile_boxes: box.setValue(2)
    assert dialog.preview.count == 4096
    assert dialog.apply_button.isEnabled()


def test_wheel_over_mpp_edits_scrolls_instead_of_changing_calibration(qtbot, tmp_path):
    panel, _ = panel_image(qtbot, tmp_path)
    dialog = InputSetupDialog(panel)
    qtbot.addWidget(dialog)
    dialog.resize(500, 480)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog.physical_mode.click()
    dialog.editor.mpp_boxes[0].setValue(.252)
    edit = dialog.editor.mpp_boxes[0].lineEdit()
    before = dialog.choices()
    point = edit.rect().center()
    event = QWheelEvent(QPointF(point), QPointF(edit.mapToGlobal(point)), QPoint(), QPoint(0, -120),
                        Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(edit, event)
    assert dialog.choices() == before


@pytest.mark.parametrize("theme", ["Light", "Dark"])
@pytest.mark.parametrize("size", [(440, 430), (680, 560)])
def test_setup_keeps_apply_reachable_and_has_no_horizontal_scroll(qtbot, tmp_path, theme, size):
    app = QApplication.instance()
    previous_theme = app.property("zyTheme") or "Light"
    apply_theme(app, theme)
    try:
        panel, _ = panel_image(qtbot, tmp_path)
        dialog = InputSetupDialog(panel)
        qtbot.addWidget(dialog)
        dialog.resize(*size)
        dialog.show()
        qtbot.waitExposed(dialog)
        dialog.physical_mode.click()
        dialog.editor.same_axes.setChecked(False)
        dialog.editor.mpp_boxes[0].setValue(.252)
        dialog.editor.mpp_boxes[1].setValue(.5)
        qtbot.waitUntil(lambda: dialog.scroll.viewport().width() > 0)
        assert dialog.rect().contains(dialog.buttons.geometry())
        assert dialog.apply_button.isVisible()
        assert dialog.scroll.horizontalScrollBar().maximum() == 0
        assert dialog.scroll.viewport().height() >= 100
        if dialog.diagram.isVisible():
            assert dialog.diagram.geometry().bottom() < dialog.preview_label.geometry().top()
            assert dialog.apply_button.isEnabled()
        assert dialog.preview.tile == (444, 224)
    finally:
        apply_theme(app, previous_theme)


def test_crop_field_calculator_does_not_use_network_size_or_suggest_mpp(qtbot):
    dialog = ModelFieldCalculator()
    qtbot.addWidget(dialog)
    assert [b.value() for b in dialog.mpp] == [0, 0]
    assert [b.value() for b in dialog.crop] == [0, 0]
    assert not dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    for b in dialog.crop: b.setValue(1000)
    dialog.mpp[0].setValue(.5)
    assert dialog.values() == [500, 500]
    assert "500 × 500" in dialog.preview.text()
    dialog.same_axes.setChecked(False)
    dialog.mpp[1].setValue(.25)
    assert dialog.values() == [500, 250]
    dialog.accept()
    assert dialog.result() == dialog.Accepted


def test_classification_skip_preview_matches_real_inference(qtbot, tmp_path):
    model = tmp_path / "model.pth"
    torch.jit.script(MeanClassifier()).save(str(model))
    p = profile(model_sha256=file_sha256(model), input_size=[2, 2], tile_size=[2, 2], stride=[2, 2], pixel_edge_policy="skip")
    model.with_name(model.name + ".zypath-model.json").write_text(json.dumps(p.to_dict()))
    loaded = ModelLoader().load_with_info(model)
    image = tmp_path / "five.png"
    Image.new("RGB", (5, 5), (150, 80, 100)).save(image)
    preview = input_preview(p, ImageCalibration(None, "fixture", (5, 5)), (5, 5), classification_mode="tiled_analysis", pixel_tile=(2, 2))
    result = InferenceEngine(model, image, "classification", loaded_model=loaded, classification_mode="tiled_analysis").run_pipeline()
    assert preview.count == len(result["classification_analysis"]["tiles"]) == 4
    assert "Incomplete borders" in preview.notes[0]
    assert validate_classification_workload((1001, 1001), (10, 10), "skip") == 10000
    with pytest.raises(ClassificationWorkloadError):
        validate_classification_workload((1001, 1001), (10, 10))


def test_unloaded_profile_skip_edges_do_not_get_a_false_workload_rejection(tmp_path, monkeypatch):
    monkeypatch.setattr("core.classification_tiles.MAX_CLASSIFICATION_TILES", 100)
    model = tmp_path / "model.pth"
    torch.jit.script(MeanClassifier()).save(str(model))
    p = profile(model_sha256=file_sha256(model), input_size=[2, 2], tile_size=[2, 2],
                stride=[2, 2], pixel_edge_policy="skip")
    model.with_name(model.name + ".zypath-model.json").write_text(json.dumps(p.to_dict()))
    image = tmp_path / "image.png"
    Image.new("RGB", (21, 21), (150, 80, 100)).save(image)
    result = InferenceEngine(model, image, "classification", classification_mode="tiled_analysis",
                             classification_tile_metadata={"tile_size": [2, 2]}).run_pipeline()
    assert len(result["classification_analysis"]["tiles"]) == 100


@pytest.mark.parametrize("size,tile,stride,network", [
    ((3552, 3536), (1000, 1000), (512, 512), (224, 224)),
    ((40, 20), (1000, 1000), (512, 512), (224, 224)),
    ((103, 99), (20, 30), (7, 9), (8, 12)),
])
def test_segmentation_preview_uses_the_inference_edge_grid(size, tile, stride, network):
    plan = segmentation_grid(size, tile, stride, network, 9)
    xs = tile_positions(max(size[0], tile[0]), tile[0], stride[0])
    ys = tile_positions(max(size[1], tile[1]), tile[1], stride[1])
    assert (plan.columns, plan.rows) == (len(xs), len(ys))
    assert plan.output_size == (round(xs[-1] * (network[0] / tile[0])) + network[0], round(ys[-1] * (network[1] / tile[1])) + network[1])


@pytest.mark.parametrize("size,message", [((1_000_000, 1_000_000), "10,000"), ((80_000, 80_000), "512 MiB")])
def test_reference_segmentation_rejects_work_before_reading_or_allocating(size, message):
    class HeaderOnlyImage:
        def __init__(self): self.size = size
        def convert(self, mode): pytest.fail("Raster allocation was reached")
    with pytest.raises(ValueError, match=message):
        predict_large_image(HeaderOnlyImage(), nn.Identity(), torch.device("cpu"), stride=1000)
