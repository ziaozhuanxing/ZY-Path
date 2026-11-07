import json

from PIL import Image
import pytest
import torch
from torch import nn
from PyQt5.QtCore import QSettings

from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel, ModelLoader
from core.model_profile import ModelInputProfile, SCHEMA, UPERNET_SHA256, file_sha256, known_profile
from ui.inference_panel import InferencePanel
from ui.input_configuration import ImageScaleDialog, ModelInputDialog
from ui.main_window import MainWindow


class ThreeClassClassifier(nn.Module):
    def forward(self, value):
        return value.mean((2, 3))


def profile(**updates):
    return ModelInputProfile.from_dict({"schema": SCHEMA, "model_sha256": "1" * 64,
        "task_type": "classification", "classes": ["one", "two", "three"],
        "normalization": "raw255", "input_scope": "patch", "input_size": [8, 8],
        "tile_size": [8, 8], "stride": [8, 8], "field_um": [4, 4], **updates})


def test_image_and_model_changes_do_not_inherit_mpp_or_scale_matching(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    first, second = tmp_path / "first.png", tmp_path / "second.png"
    Image.new("RGB", (16, 16)).save(first)
    Image.new("RGB", (32, 32)).save(second)
    panel.set_active_input_profile(profile())
    panel.set_image(str(first))
    assert not panel.match_scale_checkbox.isEnabled()
    panel._manual_mpp = [.5, .5]
    panel._refresh_scale_information()
    panel.match_scale_checkbox.setChecked(True)
    assert panel.input_options() == {"manual_mpp": [.5, .5], "match_scale": True}
    panel.set_classification_mode("tiled_analysis")
    assert "4 (2 columns x 2 rows)" in panel.mode_summary.text()
    panel.set_image(str(first))
    assert panel.match_scale_checkbox.isChecked()  # Refresh of the same input preserves its calibration.
    panel.set_active_input_profile(profile(field_um=[8, 8]))
    assert not panel.match_scale_checkbox.isChecked()
    panel.set_image(str(second))
    assert panel.input_options() == {"manual_mpp": None, "match_scale": False}
    panel.clear_image()
    assert not panel.image_scale_button.isEnabled()


def test_segmentation_reference_cannot_enable_unfounded_physical_matching(qtbot, tmp_path):
    panel = InferencePanel()
    qtbot.addWidget(panel)
    path = tmp_path / "source.png"
    Image.new("RGB", (80, 80)).save(path)
    panel.set_task("segmentation")
    panel.set_active_input_profile(known_profile(UPERNET_SHA256, upernet=True))
    panel.set_image(str(path))
    panel._manual_mpp = [.252, .252]
    panel._refresh_scale_information()
    assert not panel.match_scale_checkbox.isEnabled()
    assert "not established" in panel.scale_summary.text()
    assert "0.5" not in panel.scale_summary.text()


def test_manual_scale_dialog_requires_values_instead_of_suggesting_guessed_mpp(qtbot):
    dialog = ImageScaleDialog(None)
    qtbot.addWidget(dialog)
    assert dialog.values() is None
    assert [box.value() for box in dialog.mpp_boxes] == [0, 0]
    dialog.manual.setChecked(True)
    dialog.mpp_boxes[0].setValue(.252)
    assert dialog.values() == [.252, .252]
    dialog.accept()
    assert dialog.result() == dialog.Accepted


def test_local_model_profile_can_be_saved_without_modifying_weights(qtbot, tmp_path):
    path = tmp_path / "local-classifier.pth"
    torch.save(ThreeClassClassifier(), path)
    checksum = file_sha256(path)
    loaded = ModelLoader().load_with_info(path)
    validation = ModelLoader.validate_loaded(loaded)
    dialog = ModelInputDialog(path, loaded, validation)
    qtbot.addWidget(dialog)
    dialog.labels.setPlainText("one\ntwo\nthree")
    dialog.normalization.setCurrentText("raw255")
    dialog.scope.setCurrentText("patch")
    for box in dialog.field:
        box.setValue(112)
    for box in dialog.input_size:
        box.setValue(128)
    dialog.accept()
    assert dialog.saved
    assert file_sha256(path) == checksum
    profile_path = path.with_name(path.name + ".zypath-model.json")
    data = json.loads(profile_path.read_text())
    assert data["model_sha256"] == checksum
    reloaded = ModelLoader().load_with_info(path)
    assert reloaded.input_profile.input_size == (128, 128)
    assert reloaded.input_profile.field_um == (112., 112.)
    assert reloaded.classes == ["one", "two", "three"]


def test_profile_editor_does_not_save_against_replaced_weights(qtbot, tmp_path, monkeypatch):
    path = tmp_path / "changing.pth"
    torch.save(ThreeClassClassifier(), path)
    loaded = ModelLoader().load_with_info(path)
    dialog = ModelInputDialog(path, loaded, ModelLoader.validate_loaded(loaded))
    qtbot.addWidget(dialog)
    messages = []
    monkeypatch.setattr("ui.input_configuration.QMessageBox.warning", lambda *args: messages.append(args[-1]))
    with path.open("ab") as stream:
        stream.write(b"changed")
    dialog.accept()
    assert not dialog.saved
    assert "weights changed" in messages[0]
    assert not path.with_name(path.name + ".zypath-model.json").exists()


def test_result_history_pdf_and_rerun_keep_the_frozen_input_contract(qtbot, tmp_path, monkeypatch):
    from pypdf import PdfReader
    path = tmp_path / "source.png"
    Image.new("RGB", (16, 16), (200, 100, 50)).save(path)
    model = tmp_path / "test.pth"
    torch.save(ThreeClassClassifier(), model)
    model_profile = profile(model_sha256=file_sha256(model))
    model.with_name(model.name + ".zypath-model.json").write_text(json.dumps(model_profile.to_dict()))
    loaded = ModelLoader().load_with_info(model)
    result = InferenceEngine(model, path, "classification", loaded_model=loaded,
        classification_mode="tiled_analysis", input_options={"match_scale": True, "manual_mpp": [.5, .5]}).run_pipeline()
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    window = MainWindow(settings=QSettings(str(tmp_path / "app.ini"), QSettings.IniFormat),
        db_path=tmp_path / "history.db", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    assert window._show_inference_result(result)
    record_id = window.current_record_id
    assert "Source MPP: 0.5 x 0.5" in window.result_panel.tile_page.summary.text()
    assert "Matched field: 4 x 4" in window.result_panel.tile_page.summary.text()
    record = window.database_manager.get_record_by_id(record_id)
    recorded = MainWindow._record_classification_parameters(record, for_rerun=True)
    assert recorded["input_profile"]["model_sha256"] == file_sha256(model)
    assert recorded["spatial_context"]["calibration"]["source"] == "manual entry"
    window._show_record_activated(record_id)
    assert "Matched field: 4 x 4" in window.result_panel.tile_page.summary.text()
    current = window._current_result
    pdf = tmp_path / "calibrated-report.pdf"
    window.export_manager.export_pdf(pdf, current["original_image_path"], current["result_image_path"], current["metadata"])
    text = "\n".join(page.extract_text() for page in PdfReader(pdf).pages)
    assert "Image MPP X/Y" in text and "manual entry" in text
    assert "zypath.model-profile.v1" in text
    assert "not been verified" not in text
    options = {"recorded_input_profile": recorded["input_profile"], "recorded_spatial_context": recorded["spatial_context"]}
    again = InferenceEngine(model, path, "classification", loaded_model=loaded,
        classification_mode="tiled_analysis", input_options=options).run_pipeline()
    assert again["classification_analysis"]["tile_size"] == result["classification_analysis"]["tile_size"]
    assert again["probabilities"] == pytest.approx(result["probabilities"])


def test_run_button_and_history_rerun_use_the_correct_scale_snapshot(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    settings = QSettings(str(tmp_path / "app.ini"), QSettings.IniFormat)
    settings.setValue("classificationTiles/width", 1)
    settings.setValue("classificationTiles/height", 1)
    window = MainWindow(settings=settings, db_path=tmp_path / "history.db", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    path, model = tmp_path / "source.png", tmp_path / "local.pth"
    Image.new("RGB", (101, 101), (200, 100, 50)).save(path)
    torch.save(ThreeClassClassifier(), model)
    model.with_name(model.name + ".zypath-model.json").write_text(json.dumps(profile(model_sha256=file_sha256(model)).to_dict()))
    window.inference_panel.set_custom_model(str(model))
    window.inference_panel.set_image(str(path))
    window.inference_panel.set_classification_mode("tiled_analysis")
    window.inference_panel._manual_mpp = [.5, .5]
    window.inference_panel._refresh_scale_information()
    window.inference_panel.match_scale_checkbox.setChecked(True)
    window.inference_panel.run_button.click()
    qtbot.waitUntil(lambda: window._inference_engine is None and window.current_record_id is not None, timeout=10000)
    first_id = window.current_record_id
    first = window.database_manager.get_record_by_id(first_id)
    assert json.loads(first["analysis_json"])["tile_size"] == [8, 8]
    window.inference_panel._manual_mpp = [1., 1.]
    window.inference_panel._refresh_scale_information()
    window._handle_rerun_requested(first_id)
    qtbot.waitUntil(lambda: window._inference_engine is None and window.current_record_id != first_id, timeout=10000)
    second = window.database_manager.get_record_by_id(window.current_record_id)
    analysis = json.loads(second["analysis_json"])
    assert analysis["tile_size"] == [8, 8]
    assert analysis["spatial_context"]["calibration"]["mpp"] == [.5, .5]
    assert settings.value("classificationTiles/width", type=int) == 1
