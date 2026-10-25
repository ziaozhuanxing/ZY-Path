"""Report image encoding and data preservation, using synthetic fixtures only."""

from copy import deepcopy
import hashlib
import math

import numpy as np
from PIL import Image
from pypdf import PdfReader
import pytest
from PyQt5.QtCore import QPoint, QPointF, QSettings, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication

from core.classification_tiles import CLASSIFICATION_COLORS, CLASSIFICATION_LABELS
from core.large_image_segmentation import SEGMENTATION_COLORS, SEGMENTATION_LABELS
from data.export_manager import ExportManager
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


def raster_objects(reader):
    objects = {}
    for page in reader.pages:
        for ref in page["/Resources"]["/XObject"].values():
            obj = ref.get_object()
            if obj.get("/Subtype") == "/Image" and obj["/Width"] > 96:
                objects[ref.idnum] = obj
    return list(objects.values())


@pytest.fixture(params=["classification", "segmentation"])
def spatial_report(tmp_path, request):
    size = (2100, 1500)
    original = Image.fromarray(np.random.default_rng(42).integers(
        0, 256, (size[1], size[0], 3), dtype=np.uint8))
    labels, colors = ((CLASSIFICATION_LABELS, CLASSIFICATION_COLORS)
                      if request.param == "classification"
                      else (SEGMENTATION_LABELS, SEGMENTATION_COLORS))
    color_map = Image.new("RGB", size)
    tiles = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        x, y = i % 3 * 700, i // 3 * 500
        box = [x, y, x + 700, y + 500]
        color_map.paste(color, box)
        tiles.append({"box": box, "label": label, "confidence": .9})
    overlay = Image.blend(original, color_map, .4)
    paths = [tmp_path / "source.png", tmp_path / "overlay.png"]
    original.save(paths[0])
    overlay.save(paths[1])
    analysis = {
        "image_size": list(size),
        "classes": [{"index": i, "label": label, "color": list(color)}
                    for i, (label, color) in enumerate(zip(labels, colors))],
        "presentation": {"view": "overlay", "opacity": .4},
    }
    metadata = {"model_name": "synthetic-fixture.pth", "task_type": request.param,
                "image_path": str(paths[0]), "timestamp": "2026-10-25T12:00:00+08:00"}
    if request.param == "classification":
        analysis.update(mode="classification_tiles", tile_size=[700, 500],
                        tile_counts=[1] * 9, area_ratios=[1 / 9] * 9, tiles=tiles,
                        resize_backend="pillow_bilinear", input_size=[224, 224])
        metadata.update(classification_mode="tiled_analysis", classification_analysis=analysis)
    else:
        analysis.update(pixel_counts=[350000] * 9, area_denominator="full_image_pixels")
        metadata["segmentation_analysis"] = analysis
    return paths, metadata, original, overlay, color_map


def test_standard_reduces_embedded_images_but_preserves_analysis_and_sources(tmp_path, spatial_report):
    paths, metadata, original, overlay, color_map = spatial_report
    before = deepcopy(metadata)
    source_hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    map_bytes = color_map.tobytes()
    reports = {}
    for quality in ("standard", "original_resolution"):
        reports[quality] = ExportManager().export_pdf(
            tmp_path / f"{quality}.pdf", *paths, metadata,
            options={"image_quality": quality}, color_map=color_map)
    standard, full = (PdfReader(reports[q]) for q in reports)
    small_images, full_images = raster_objects(standard), raster_objects(full)
    assert len(small_images) == len(full_images) == 3
    # Three equal A4 panels have at most 58 mm of usable image width/height.
    for obj in small_images:
        assert obj["/Width"] <= math.ceil(58 / 25.4 * 300)
        assert obj["/Height"] <= math.ceil(58 / 25.4 * 300)
        assert obj["/Width"] / obj["/Height"] == pytest.approx(2100 / 1500, abs=.004)
    photos = [obj for obj in small_images if obj["/Filter"] == "/DCTDecode"]
    maps = [obj for obj in small_images if obj["/Filter"] == "/FlateDecode"]
    assert len(photos) == 2 and len(maps) == 1
    embedded_map = Image.frombytes("RGB", (maps[0]["/Width"], maps[0]["/Height"]), maps[0].get_data())
    assert set(embedded_map.getdata()) == set(color_map.getdata())
    # Original resolution preserves the actual raster pixels, not just a DPI label.
    assert all((obj["/Width"], obj["/Height"]) == original.size for obj in full_images)
    assert all(obj["/Filter"] == "/FlateDecode" for obj in full_images)
    assert {obj.get_data() for obj in full_images} == {
        original.tobytes(), overlay.tobytes(), color_map.tobytes()}
    assert reports["standard"].stat().st_size < reports["original_resolution"].stat().st_size * .2
    texts = ["\n".join(page.extract_text() or "" for page in reader.pages)
             for reader in (standard, full)]
    analysis = before.get("classification_analysis", before.get("segmentation_analysis"))
    for text in texts:
        assert "2100 x 1500 pixels" in text
        for item in analysis["classes"]:
            assert item["label"] in text and f"RGB={item['color']}" in text
        assert "11.11%" in text
        if metadata["task_type"] == "classification":
            for tile in analysis["tiles"]:
                assert str(tile["box"]) in text
            assert text.count("90.00%") == 9
        else:
            assert text.count("350,000") == 9
    assert "Standard" in texts[0] and "300 DPI" in texts[0]
    assert "Original resolution" in texts[1]
    assert metadata == before and color_map.tobytes() == map_bytes
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths] == source_hashes


@pytest.mark.parametrize("quality", ["standard", "original_resolution"])
def test_selected_class_map_remains_lossless_without_duplicate_panel(tmp_path, spatial_report, quality):
    paths, metadata, original, _, color_map = spatial_report
    analysis = metadata.get("classification_analysis", metadata.get("segmentation_analysis"))
    analysis["presentation"]["view"] = ("color_map" if metadata["task_type"] == "classification"
                                         else "segmentation_map")
    color_map.save(paths[1])
    output = ExportManager().export_pdf(tmp_path / "map.pdf", *paths, metadata,
                                       options={"image_quality": quality}, color_map=color_map)
    images = raster_objects(PdfReader(output))
    assert len(images) == 2
    maps = [obj for obj in images if obj["/Filter"] == "/FlateDecode"
            and len(set(obj.get_data())) < 100]
    assert len(maps) == 1
    obj = maps[0]
    embedded = Image.frombytes("RGB", (obj["/Width"], obj["/Height"]), obj.get_data())
    assert set(embedded.getdata()) == set(color_map.getdata())
    if quality == "original_resolution":
        assert embedded.size == original.size and embedded.tobytes() == color_map.tobytes()


@pytest.mark.parametrize("saved", [None, "unknown-setting"])
def test_default_and_unrecognised_quality_use_standard(tmp_path, spatial_report, saved):
    paths, metadata, _, _, color_map = spatial_report
    options = {} if saved is None else {"image_quality": saved}
    output = ExportManager().export_pdf(tmp_path / "default.pdf", *paths, metadata,
                                       options=options, color_map=color_map)
    images = raster_objects(PdfReader(output))
    assert len(images) == 3 and all(obj["/Width"] < 1000 for obj in images)


def test_standard_keeps_classification_chart_lossless_and_does_not_enlarge_small_sources(tmp_path):
    source = tmp_path / "small.png"
    chart = tmp_path / "chart.png"
    Image.new("RGB", (120, 80), "pink").save(source)
    chart_image = Image.new("RGB", (1600, 1200), "white")
    chart_image.paste("blue", (100, 100, 1200, 200))
    chart_image.save(chart)
    output = ExportManager().export_pdf(tmp_path / "single.pdf", source, chart,
                                       {"task_type": "classification", "classification_mode": "single_image"})
    images = raster_objects(PdfReader(output))
    assert len(images) == 2 and all(obj["/Filter"] == "/FlateDecode" for obj in images)
    assert any((obj["/Width"], obj["/Height"]) == (120, 80) for obj in images)
    obj = next(obj for obj in images if obj["/Width"] != 120)
    assert obj["/Width"] < 1600 and obj["/Height"] < 1200


def test_quality_preference_persists_refreshes_and_ignores_wheel(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "preferences.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.navigation.setCurrentRow(1)
    dialog.show()
    combo = dialog.pdf_image_quality
    assert combo.currentData() == "standard"
    assert [combo.itemText(i) for i in range(combo.count())] == ["Standard", "Original resolution"]
    combo.setCurrentIndex(combo.findData("original_resolution"))
    assert settings.value("export/pdfImageQuality") == "original_resolution"
    combo.setFocus()
    event = QWheelEvent(QPointF(combo.rect().center()), QPointF(combo.mapToGlobal(combo.rect().center())),
                        QPoint(), QPoint(0, 120), Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(combo, event)
    assert combo.currentData() == "original_resolution"
    dialog.reset_reminders_button.click()
    reopened = SettingsDialog(QSettings(settings.fileName(), QSettings.IniFormat))
    qtbot.addWidget(reopened)
    assert reopened.pdf_image_quality.currentData() == "original_resolution"
    settings.setValue("export/pdfImageQuality", "standard")
    dialog.refresh_preferences()
    assert combo.currentData() == "standard"
    settings.setValue("export/pdfImageQuality", "unsupported")
    dialog.refresh_preferences()
    assert combo.currentData() == "standard"


@pytest.mark.parametrize("quality", [None, "standard", "original_resolution"])
def test_main_window_passes_quality_as_export_option_without_changing_record(qtbot, tmp_path, monkeypatch, quality):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    settings.setValue("export/pdfReminderEnabled", False)
    if quality is not None:
        settings.setValue("export/pdfImageQuality", quality)
    window = MainWindow(settings=settings, builtin_model_path=tmp_path / "absent.pth",
                        db_path=tmp_path / "db.sqlite", results_dir=tmp_path / "results")
    qtbot.addWidget(window)
    source = tmp_path / "small.png"
    Image.new("RGB", (120, 80), "white").save(source)
    window._current_result = {"original_image_path": str(source), "result_image_path": str(source),
                              "metadata": {"task_type": "classification", "result_label": "TUM"}}
    before = deepcopy(window._current_result)
    received = []

    def capture(output, original, result, metadata, **kwargs):
        received.append((deepcopy(metadata), deepcopy(kwargs["options"])))

    monkeypatch.setattr(window.export_manager, "export_pdf", capture)
    monkeypatch.setattr("ui.main_window.QFileDialog.getSaveFileName",
                        lambda *a, **kw: (str(tmp_path / "result.pdf"), ""))
    window._export_current_pdf()
    qtbot.waitUntil(lambda: window._pdf_export_worker is None, timeout=5000)
    assert len(received) == 1
    assert received[0][1]["image_quality"] == (quality or "standard")
    assert received[0][0] == before["metadata"]
    assert window._current_result == before
