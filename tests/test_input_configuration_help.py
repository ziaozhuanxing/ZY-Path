"""Exercise real help/scale controls without inventing model calibration."""

import json
from pathlib import Path

from PIL import Image
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QScrollArea
import pytest
import torch
from torch import nn

from core.image_calibration import ImageCalibration
from core.model_loader import LoadedModel, ModelLoader, ValidationResult
from core.model_profile import CRC_SHA256, UPERNET_SHA256, ModelInputProfile, SCHEMA, file_sha256, known_profile
from ui.inference_panel import InferencePanel
from ui.input_configuration import ImageScaleDialog, ModelInputDialog, ModelInputImportDialog
from ui.input_help import scale_readiness


class FixtureClassifier(nn.Module):
    def forward(self, value):
        return value.mean((2, 3))


def patch_profile(**changes):
    return ModelInputProfile.from_dict({
        "schema": SCHEMA, "model_sha256": "2" * 64, "task_type": "classification",
        "classes": ["a", "b", "c"], "input_size": [8, 8], "normalization": "raw255",
        "input_scope": "patch", "field_um": [4, 4], "tile_size": [8, 8], "stride": [8, 8], **changes})


def panel_with_image(qtbot, tmp_path, model_profile, size=(16, 16)):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    panel.set_task(model_profile.task_type)
    panel.set_active_input_profile(model_profile)
    path = tmp_path / "uncalibrated.png"
    Image.new("RGB", size).save(path)
    panel.set_image(str(path))
    return panel


def test_screenshot_case_lists_both_blockers_and_help_explains_without_enabling(qtbot, tmp_path):
    panel = panel_with_image(qtbot, tmp_path, known_profile(UPERNET_SHA256, upernet=True))
    message = panel.scale_availability_label.text()
    assert "physical tissue field is not specified" in message
    assert "Image MPP is unknown" in message
    assert not panel.match_scale_checkbox.isEnabled()
    before = panel.input_options()
    panel.scale_help_button.click()
    help_dialog = panel._input_help_dialog
    qtbot.waitUntil(help_dialog.isVisible)
    help_dialog.language.setCurrentIndex(help_dialog.language.findData("zh"))
    assert "只填写图片 MPP" in help_dialog.browser.toPlainText()
    assert "当前状态" in help_dialog.browser.toPlainText()
    help_dialog.buttons.button(QDialogButtonBox.Close).click()
    assert panel.input_options() == before
    panel._manual_mpp = [.252, .252]
    panel._refresh_scale_information()
    assert not panel.match_scale_checkbox.isEnabled()
    assert "Image MPP is unknown" not in panel.scale_availability_label.text()
    assert "entering image MPP alone cannot enable matching" in panel.scale_availability_label.text()


def test_crc_matching_explains_ready_then_shows_actual_source_crop(qtbot, tmp_path):
    panel = panel_with_image(qtbot, tmp_path, known_profile(CRC_SHA256), size=(888, 888))
    assert "Use Image scale" in panel.scale_availability_label.text()
    panel._manual_mpp = [.252, .252]
    panel._refresh_scale_information()
    assert panel.match_scale_checkbox.isEnabled()
    assert "Ready:" in panel.scale_availability_label.text()
    panel.set_classification_mode("tiled_analysis")
    panel.match_scale_checkbox.setChecked(True)
    assert "444 x 444" in panel.scale_availability_label.text()
    assert "4 (2 columns x 2 rows)" in panel.mode_summary.text()
    assert panel.run_button.isEnabled()


def test_wrong_single_image_field_has_actionable_run_state_and_recovers(qtbot, tmp_path):
    panel = panel_with_image(qtbot, tmp_path, patch_profile())
    panel._manual_mpp = [.5, .5]
    panel._refresh_scale_information()
    panel.match_scale_checkbox.setChecked(True)
    assert not panel.run_button.isEnabled()
    assert "Choose Tiled analysis" in panel.scale_availability_label.text()
    panel._manual_mpp = [.25, .25]  # The same image now covers exactly one declared field.
    panel._refresh_scale_information()
    assert panel.run_button.isEnabled()
    panel._manual_mpp = [.5, .5]
    panel._refresh_scale_information()
    assert not panel.run_button.isEnabled()
    panel.set_classification_mode("tiled_analysis")
    assert panel.run_button.isEnabled()


def test_incomplete_field_is_explained_before_starting_a_worker(qtbot, tmp_path):
    panel = panel_with_image(qtbot, tmp_path, patch_profile(), size=(4, 4))
    panel._manual_mpp = [.5, .5]
    panel._refresh_scale_information()
    panel.set_classification_mode("tiled_analysis")
    panel.match_scale_checkbox.setChecked(True)
    assert not panel.run_button.isEnabled()
    assert "no complete field fits" in panel.scale_availability_label.text()
    panel.match_scale_checkbox.setChecked(False)
    assert panel.run_button.isEnabled()  # Explicit legacy pixel mode remains available.


@pytest.mark.parametrize("profile,calibration,reason", [
    (None, ImageCalibration((.5, .5), "fixture", (16, 16)), "no_profile"),
    (patch_profile(input_scope="image", field_um=None), ImageCalibration((.5, .5), "fixture", (16, 16)), "whole_image"),
    (patch_profile(), ImageCalibration((.000001, .000001), "fixture", (16, 16)), "geometry"),
])
def test_availability_does_not_offer_invalid_matching(profile, calibration, reason):
    state = scale_readiness(profile, calibration, has_image=True)
    assert not state.available
    assert reason in state.reasons
    assert state.explanation() and state.explanation("zh")


def test_image_dialog_unknown_is_explicit_and_invalid_mpp_has_visible_guidance(qtbot):
    dialog = ImageScaleDialog(None)
    qtbot.addWidget(dialog)
    assert not dialog.windowFlags() & Qt.WindowContextHelpButtonHint
    assert dialog.unknown.isChecked() and not dialog.auto.isEnabled()
    assert dialog.values() is None
    assert dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    dialog.manual.setChecked(True)
    assert not dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    assert not dialog.validation_label.isHidden()
    dialog.show()
    qtbot.waitExposed(dialog)
    first, second = dialog.mpp_boxes
    first.setFocus()
    first.selectAll()
    qtbot.keyClicks(first, "0.252")
    assert dialog.values() == [.252, .252]
    assert not second.isEnabled()
    assert dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    dialog.same_axes.setChecked(False)
    assert second.isEnabled()
    second.setValue(.5)
    assert dialog.values() == [.252, .5]
    dialog.same_axes.setChecked(True)
    assert dialog.values() == [.252, .252] and second.value() == .252


def test_image_help_and_cancel_do_not_change_manual_values(qtbot):
    dialog = ImageScaleDialog(None, [.252, .5])
    qtbot.addWidget(dialog)
    before = dialog.values()
    dialog.buttons.button(QDialogButtonBox.Help).click()
    help_dialog = dialog._input_help_dialog
    qtbot.waitUntil(help_dialog.isVisible)
    assert not help_dialog.windowFlags() & Qt.WindowContextHelpButtonHint
    help_dialog.language.setCurrentIndex(help_dialog.language.findData("zh"))
    assert "只裁剪、不缩放" in help_dialog.browser.toPlainText()
    help_dialog.buttons.button(QDialogButtonBox.Close).click()
    assert dialog.values() == before
    dialog.buttons.button(QDialogButtonBox.Cancel).click()
    assert dialog.result() == dialog.Rejected


def test_file_mpp_is_readonly_and_manual_override_can_be_cleared(qtbot):
    calibration = ImageCalibration((.252, .252), "file fixture", (444, 444))
    dialog = ImageScaleDialog(calibration, [.5, .5])
    qtbot.addWidget(dialog)
    assert "0.252 x 0.252" in dialog.file_status.text()
    assert not dialog.auto.isChecked() and dialog.manual.isChecked()
    dialog.auto.setChecked(True)
    assert dialog.values() is None
    assert not any(box.isEnabled() for box in dialog.mpp_boxes)
    assert not dialog.same_axes.isEnabled()


@pytest.mark.parametrize("checksum,upernet,task", [(CRC_SHA256, False, "classification"), (UPERNET_SHA256, True, "segmentation")])
def test_builtin_view_has_help_close_and_no_dead_save_or_import(qtbot, tmp_path, checksum, upernet, task):
    # The contract is displayed with an in-memory fixture; no genuine weights are loaded.
    profile = known_profile(checksum, upernet=upernet)
    loaded = LoadedModel(nn.Identity(), "checkpoint", list(profile.classes), "fixture", profile.normalization, input_profile=profile)
    dialog = ModelInputDialog(tmp_path / "not-a-real-weight-file.pth", loaded, ValidationResult(task, 9, (1, 9)))
    qtbot.addWidget(dialog)
    assert not dialog.windowFlags() & Qt.WindowContextHelpButtonHint
    assert dialog.import_button.isHidden()
    assert dialog.buttons.button(QDialogButtonBox.Save) is None
    assert dialog.buttons.button(QDialogButtonBox.Close) is not None
    original = dialog.profile_data()
    dialog.buttons.button(QDialogButtonBox.Help).click()
    help_dialog = dialog._input_help_dialog
    qtbot.waitUntil(help_dialog.isVisible)
    help_dialog.language.setCurrentIndex(help_dialog.language.findData("zh"))
    assert "这里描述模型需要什么" in help_dialog.browser.toPlainText()
    help_dialog.close()
    assert dialog.profile_data() == original
    dialog.buttons.button(QDialogButtonBox.Close).click()
    assert not dialog.saved


def test_local_editor_hides_unused_custom_normalisation_fields(qtbot, tmp_path):
    model = tmp_path / "fixture.pth"
    torch.save(FixtureClassifier(), model)
    loaded = ModelLoader().load_with_info(model)
    dialog = ModelInputDialog(model, loaded, ModelLoader.validate_loaded(loaded))
    qtbot.addWidget(dialog)
    assert dialog.mean.isHidden() and dialog.std.isHidden() and dialog.input_scale.isHidden()
    assert dialog.model_form.labelForField(dialog.mean).isHidden()
    dialog.normalization.setCurrentText("custom")
    assert not any(box.isHidden() for box in (dialog.mean, dialog.std, dialog.input_scale))
    dialog.normalization.setCurrentText("embedded")
    assert all(box.isHidden() for box in (dialog.mean, dialog.std, dialog.input_scale))
    assert dialog.import_button.isEnabled()
    assert dialog.buttons.button(QDialogButtonBox.Save).text() == "Save model settings"


@pytest.mark.parametrize("control_name", ["normalization", "decoder", "resize_method", "scope", "output_kind", "edge", "pixel_edge"])
def test_scrolling_a_local_model_form_does_not_change_closed_dropdowns(qtbot, tmp_path, control_name):
    model = tmp_path / "fixture.pth"
    torch.save(FixtureClassifier(), model)
    loaded = ModelLoader().load_with_info(model)
    dialog = ModelInputDialog(model, loaded, ModelLoader.validate_loaded(loaded))
    qtbot.addWidget(dialog)
    dialog.resize(680, 330)
    dialog.show()
    qtbot.waitExposed(dialog)
    scroll = dialog.findChild(QScrollArea)
    combo = getattr(dialog, control_name)
    scroll.ensureWidgetVisible(combo)
    combo.setFocus()
    original = dialog.profile_data()
    position = combo.rect().center()
    event = QWheelEvent(QPointF(position), QPointF(combo.mapToGlobal(position)), QPoint(), QPoint(0, -120),
                        Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(combo, event)
    assert dialog.profile_data() == original
    # Explicit keyboard selection still works; the control is not merely disabled.
    before = combo.currentIndex()
    qtbot.keyClick(combo, Qt.Key_Up if before else Qt.Key_Down)
    assert combo.currentIndex() != before


def test_settings_import_explains_its_purpose_and_rejects_wrong_weights(qtbot, tmp_path, monkeypatch):
    model = tmp_path / "fixture.pth"
    torch.save(FixtureClassifier(), model)
    dialog = ModelInputImportDialog(model)
    qtbot.addWidget(dialog)
    assert not dialog.windowFlags() & Qt.WindowContextHelpButtonHint
    assert not dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps(patch_profile().to_dict()))
    monkeypatch.setattr("ui.input_configuration.QFileDialog.getOpenFileName", lambda *a: (str(settings_file), ""))
    dialog.choose_button.click()
    assert not dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    assert "SHA-256" in dialog.file_status.text()
    settings_file.write_text(json.dumps(patch_profile(model_sha256=file_sha256(model)).to_dict()))
    dialog.choose_button.click()
    assert dialog.buttons.button(QDialogButtonBox.Ok).isEnabled()
    assert dialog.filename == str(settings_file)
    model.unlink()
    dialog.buttons.button(QDialogButtonBox.Ok).click()
    assert dialog.result() != dialog.Accepted
    assert "unavailable" in dialog.file_status.text()
