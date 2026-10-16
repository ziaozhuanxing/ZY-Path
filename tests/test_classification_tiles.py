"""Classification tiles use in-memory simulated logits, never production weights."""
import json
import re
import zlib

import numpy as np
from PIL import Image
import pytest
import torch
from torch import nn
from PyQt5.QtCore import QSettings, Qt

from core.classification_tiles import (
    ClassificationTileSpec, CLASSIFICATION_LABELS, CLASSIFICATION_COLORS,
    exploratory_metadata, predict_classification_tiles,
)
from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel
from ui.main_window import MainWindow


class SimulatedLogits(nn.Module):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def forward(self, value):
        self.inputs.append(value.detach().clone())
        result = torch.zeros((1, 9))
        result[0, 8 if value[0, 0].mean() > 100 else 0] = 5
        return result


def sample():
    image = Image.new("RGB", (5, 3))
    image.paste((255, 0, 0), (0, 0, 2, 3))
    return image


def spec():
    return ClassificationTileSpec.from_metadata(
        exploratory_metadata(2, 2), list(CLASSIFICATION_LABELS), "raw255")


def test_tiles_cover_edges_once_preserve_rgb_and_compute_area_statistics():
    model = SimulatedLogits()
    progress = []
    result = predict_classification_tiles(sample(), model, spec(), lambda *args: progress.append(args))
    analysis = result["classification_analysis"]
    assert [t["box"] for t in analysis["tiles"]] == [
        [0, 0, 2, 2], [2, 0, 4, 2], [4, 0, 5, 2],
        [0, 2, 2, 3], [2, 2, 4, 3], [4, 2, 5, 3]]
    assert analysis["tile_counts"] == [4, 0, 0, 0, 0, 0, 0, 0, 2]
    assert analysis["pixel_counts"] == [9, 0, 0, 0, 0, 0, 0, 0, 6]
    assert analysis["area_ratios"] == [.6, 0, 0, 0, 0, 0, 0, 0, .4]
    pixels = np.asarray(result["color_map"])
    assert pixels.shape == (3, 5, 3)
    assert np.all(pixels[:, :2] == CLASSIFICATION_COLORS[8])
    assert np.all(pixels[:, 2:] == CLASSIFICATION_COLORS[0])
    assert progress == [(i, 6) for i in range(1, 7)]
    assert all(x.shape == (1, 3, 224, 224) and x.dtype == torch.float32 for x in model.inputs)
    assert model.inputs[0][0, 0].min() == 255
    assert model.inputs[0][0, 1:].max() == 0
    assert result["label"] == "ADI"
    expected = torch.softmax(torch.tensor([5.] + [0.] * 8), 0)
    assert result["confidence"] == pytest.approx(.6 * expected[0].item() + .4 * expected[1].item())
    assert sum(result["probabilities"]) == pytest.approx(1)
    assert all(t["confidence"] == pytest.approx(torch.softmax(torch.tensor([5.] + [0.] * 8), 0)[0].item()) for t in analysis["tiles"])


def test_tiles_reject_unconfirmed_missing_metadata_and_respect_order():
    metadata = exploratory_metadata(2, 2)
    for key in ("tile_size", "colors", "preprocess", "input_size", "classes"):
        invalid = dict(metadata)
        invalid.pop(key)
        with pytest.raises(ValueError):
            ClassificationTileSpec.from_metadata(invalid, list(CLASSIFICATION_LABELS), "raw255")
    with pytest.raises(ValueError, match="order"):
        ClassificationTileSpec.from_metadata(metadata, list(reversed(CLASSIFICATION_LABELS)), "raw255")
    with pytest.raises(InterruptedError):
        predict_classification_tiles(sample(), SimulatedLogits(), spec(), cancel_callback=lambda: True)


def test_engine_small_image_stays_classification_large_image_uses_tiles(tmp_path):
    path = tmp_path / "image.png"
    loaded = LoadedModel(SimulatedLogits(), "checkpoint", list(CLASSIFICATION_LABELS), "test", "raw255")
    engine = InferenceEngine(tmp_path / "selected.pth", path, "classification", loaded_model=loaded,
                             classification_tile_metadata=exploratory_metadata(2, 2))
    Image.new("RGB", (2, 2), (255, 0, 0)).save(path)
    small = engine.run_pipeline()
    assert small["task_type"] == "classification"
    assert "classification_analysis" not in small
    assert small["label"] == "TUM"
    sample().save(path)
    large = engine.run_pipeline()
    assert large["analysis_mode"] == "classification_tiles"
    assert large["task_type"] == "classification"
    assert large["classification_analysis"]["model_path"] == str((tmp_path / "selected.pth").resolve())
    assert large["classification_analysis"]["scale_status"] == "unconfirmed_exploratory"
    engine.classification_tile_metadata = None
    assert "classification_analysis" not in engine.run_pipeline()


def test_result_history_and_exports_keep_classification_metadata(qtbot, tmp_path, monkeypatch):
    image_path = tmp_path / "image.png"
    sample().save(image_path)
    result = predict_classification_tiles(sample(), SimulatedLogits(), spec())
    model_path = str(tmp_path / "selected-classifier.pth")
    result.update(task_type="classification", model_path=model_path, model_name="selected-classifier.pth",
                  image_path=str(image_path), elapsed_seconds=0.1, timestamp="2026-10-16T08:00:00+00:00", class_labels=list(CLASSIFICATION_LABELS))
    result["classification_analysis"].update(model_path=model_path, model_name="selected-classifier.pth")
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("export/pngReminderEnabled", False)
    settings.setValue("export/pdfReminderEnabled", False)
    window = MainWindow(db_path=tmp_path / "history.db", results_dir=tmp_path / "results",
                        settings=settings, builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    window._show_inference_result(result)
    panel = window.result_panel
    assert panel.result_stack.currentWidget() is panel.tile_page
    assert panel.tile_table.rowCount() == 6
    assert all(label in panel.tile_summary.text() for label in CLASSIFICATION_LABELS)
    assert "unconfirmed_exploratory" in panel.tile_summary.text()
    record = window.database_manager.get_all_records()[0]
    assert record["task_type"] == "classification"
    assert record["model_path"] == model_path
    assert json.loads(record["analysis_json"])["tile_counts"] == [4, 0, 0, 0, 0, 0, 0, 0, 2]
    window._show_record_activated(record["id"])
    assert panel.result_stack.currentWidget() is panel.tile_page
    assert panel.tile_table.item(0, 1).text() == "TUM"
    assert window._current_result["metadata"]["task_type"] == "classification"
    destination = tmp_path / "export.png"
    monkeypatch.setattr("ui.main_window.QFileDialog.getSaveFileName", lambda *a, **k: (str(destination), ""))
    window._export_current_png()
    assert destination.is_file()
    metadata = json.loads((tmp_path / "export.png.json").read_text())
    assert metadata["model_path"] == model_path
    assert len(metadata["classification_analysis"]["tiles"]) == 6
    pdf = tmp_path / "report.pdf"
    window.export_manager.export_pdf(pdf, image_path, destination, metadata)
    pdf_bytes = pdf.read_bytes()
    assert pdf_bytes.startswith(b"%PDF")
    streams = []
    for stream in re.findall(rb"stream\n(.*?)\nendstream", pdf_bytes, re.S):
        try:
            streams.append(zlib.decompress(stream))
        except zlib.error:
            pass  # JPEG streams are not text pages.
    text = b"\n".join(streams)
    assert b"Classification tiles" in text
    assert b"selected-classifier.pth" in text
    assert b"raw255" in text
    assert all(label.encode() in text for label in CLASSIFICATION_LABELS)


def test_tile_settings_are_explicit_persistent_and_show_classification_palette(qtbot, tmp_path):
    from ui.settings_dialog import SettingsDialog
    from PyQt5.QtWidgets import QLabel
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert not dialog.classification_tiles_enabled.isChecked()
    assert (dialog.tile_width.value(), dialog.tile_height.value()) == (512, 512)
    dialog.navigation.setCurrentRow(1)
    dialog.show()
    qtbot.waitExposed(dialog)
    for spin, value in ((dialog.tile_width, "300"), (dialog.tile_height, "400")):
        assert spin.isVisible()
        spin.setFocus()
        spin.selectAll()
        qtbot.keyClicks(spin, value)
        qtbot.keyClick(spin, Qt.Key_Tab)
    dialog.classification_tiles_enabled.setChecked(True)
    assert settings.value("classificationTiles/width", type=int) == 300
    assert settings.value("classificationTiles/height", type=int) == 400
    assert settings.value("classificationTiles/enabled", type=bool)
    text = " ".join(label.text() for label in dialog.findChildren(QLabel))
    assert "训练尺度/倍率待确认" in text
    assert all(label in text for label in CLASSIFICATION_LABELS)
    reopened = SettingsDialog(QSettings(settings.fileName(), QSettings.IniFormat))
    qtbot.addWidget(reopened)
    assert reopened.tile_width.value() == 300
    assert reopened.tile_height.value() == 400


@pytest.mark.parametrize("size, tiled", [((256, 256), False), ((512, 512), False),
                                        ((513, 512), True), ((512, 513), True)])
def test_visible_run_button_uses_settings_and_routes_to_correct_result(qtbot, tmp_path, size, tiled):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("classificationTiles/enabled", True)
    selected_path = tmp_path / "in-memory-classifier.pth"
    image_path = tmp_path / "source.png"
    Image.new("RGB", size, (255, 0, 0)).save(image_path)
    window = MainWindow(db_path=tmp_path / "history.db", results_dir=tmp_path / "results",
                        settings=settings, builtin_model_path=selected_path)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    # Supply only the validated model cache, as production validation would.
    # No weight file is written and the real worker/UI path runs unchanged.
    qtbot.waitUntil(lambda: window._builtin_model_statuses["classification"] is not None)
    model = LoadedModel(SimulatedLogits(), "checkpoint", list(CLASSIFICATION_LABELS), "test", "raw255")
    window._validated_builtin_model = (selected_path, model)
    window._builtin_model_statuses["classification"] = ("In-memory test classifier", True)
    window.inference_panel.set_model_ready(True)
    window.inference_panel.set_image(str(image_path))
    assert window.inference_panel.run_button.isEnabled()
    qtbot.mouseClick(window.inference_panel.run_button, Qt.LeftButton)
    qtbot.waitUntil(lambda: window._inference_engine is None, timeout=10000)
    record = window.database_manager.get_all_records()[0]
    assert record["task_type"] == "classification"
    assert record["model_path"] == str(selected_path)
    panel = window.result_panel
    if tiled:
        assert panel.result_stack.currentWidget() is panel.tile_page
        assert panel.tile_image.isVisible()
        assert panel.tile_table.isVisible()
        assert panel.tile_table.rowCount() == 2
        assert all(label in panel.tile_summary.text() for label in CLASSIFICATION_LABELS)
        assert all("#%02x%02x%02x" % color in panel.tile_summary.text()
                   for color in CLASSIFICATION_COLORS)
        assert "训练尺度待确认" in panel.tile_summary.text()
        analysis = json.loads(record["analysis_json"])
        assert analysis["tile_size"] == [512, 512]
        assert sum(analysis["tile_counts"]) == 2
        assert sum(analysis["pixel_counts"]) == size[0] * size[1]
    else:
        assert panel.result_stack.currentWidget() is panel.classification_page
        assert panel.classification_label.text() == "TUM"
        assert panel.get_result_figure() is not None
        assert not record.get("analysis_json")
