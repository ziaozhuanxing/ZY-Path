"""PDF layout and evidence-preservation tests without production weights."""

import copy
from pathlib import Path

import pytest
from PIL import Image
from PyQt5.QtCore import QSettings
from fpdf import FPDF
from pypdf import PdfReader

from data.export_manager import ExportError, ExportManager
from ui.settings_dialog import SettingsDialog


def save_image(path: Path, size=(120, 80), color=(90, 120, 150)) -> Path:
    Image.new("RGB", size, color).save(path)
    return path


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def segmentation_metadata(image_path: str, model_path: str = "") -> dict:
    labels = ("Exclude", "Cancerous epithelium", "Stroma", "TILs",
              "Normal epithelium", "Junk/Debris", "Blood", "Other",
              "Whitespace/Empty")
    colors = ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
              (255, 255, 0), (128, 0, 128), (0, 255, 255),
              (255, 165, 0), (255, 255, 255))
    counts = [7440, 100, 1800, 20, 30, 40, 50, 60, 60]
    return {
        "model_name": "segmenter.pth",
        "model_path": model_path,
        "task_type": "segmentation",
        "timestamp": "2026-10-23T14:47:31+08:00",
        "image_path": image_path,
        "segmentation_analysis": {
            "image_size": [120, 80],
            "classes": [
                {"index": index, "label": label, "color": list(color)}
                for index, (label, color) in enumerate(zip(labels, colors))
            ],
            "pixel_counts": counts,
            "area_denominator": "full_image_pixels",
            "presentation": {"view": "overlay", "opacity": .2},
        },
    }


def tiled_metadata(image_path: str, tile_count=100) -> dict:
    tiles = [
        {
            "box": [index, index + 1, index + 2, index + 3],
            "label": "STR" if index % 2 == 0 else "TUM",
            "confidence": .9 if index % 2 == 0 else .8,
        }
        for index in range(tile_count)
    ]
    return {
        "model_name": "classifier.pth",
        "task_type": "classification",
        "classification_mode": "tiled_analysis",
        "image_path": image_path,
        "classification_analysis": {
            "mode": "classification_tiles",
            "image_size": [120, 80],
            "tile_size": [12, 8],
            "input_size": [224, 224],
            "preprocess": "rgb_float32_raw255",
            "resize_backend": "pillow_bilinear",
            "classes": [
                {"index": 0, "label": "STR", "color": [0, 170, 0]},
                {"index": 1, "label": "TUM", "color": [220, 20, 60]},
            ],
            "tile_counts": [(tile_count + 1) // 2, tile_count // 2],
            "area_ratios": [.55, .45],
            "tiles": tiles,
            "presentation": {"view": "overlay", "opacity": .4, "tile_numbers": True},
        },
    }


def test_pdf_uses_equal_image_panels_and_actual_color_map(tmp_path, monkeypatch):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png", color=(120, 80, 90))
    color_map = Image.new("RGB", (120, 80), (0, 255, 0))
    calls = []
    real_image = FPDF.image

    def record_image(pdf, name, *args, **kwargs):
        if isinstance(name, Image.Image) and name.size == (120, 80):
            calls.append((kwargs.get("w"), kwargs.get("h")))
        return real_image(pdf, name, *args, **kwargs)

    monkeypatch.setattr(FPDF, "image", record_image)
    metadata = segmentation_metadata(str(original))
    ExportManager().export_pdf(
        tmp_path / "report.pdf", original, result,
        metadata, color_map=color_map,
    )

    assert len(calls) == 3
    assert calls[0] == pytest.approx(calls[1])
    assert calls[1] == pytest.approx(calls[2])
    assert calls[0][0] / calls[0][1] == pytest.approx(120 / 80)

    calls.clear()
    metadata["segmentation_analysis"]["presentation"]["view"] = "segmentation_map"
    ExportManager().export_pdf(
        tmp_path / "map-selected.pdf", original, result, metadata, color_map=color_map,
    )
    assert len(calls) == 2


def test_pdf_preserves_all_segmentation_classes_counts_colors_and_denominator(tmp_path):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png")
    output = ExportManager().export_pdf(
        tmp_path / "report.pdf", original, result,
        segmentation_metadata(str(original)),
        color_map=Image.new("RGB", (120, 80), "black"),
    )
    text = " ".join(pdf_text(output).split())

    for label in ("Exclude", "Cancerous epithelium", "Stroma", "TILs",
                  "Normal epithelium", "Junk/Debris", "Blood", "Other",
                  "Whitespace/Empty"):
        assert label in text
    assert "RGB=[0, 0, 0]" in text and "7,440" in text and "77.50%" in text
    assert "RGB=[0, 255, 0]" in text and "1,800" in text and "18.75%" in text
    assert "background and excluded labels included" in text


def test_pdf_full_paths_are_private_by_default_and_unicode_is_preserved(tmp_path):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png")
    metadata = segmentation_metadata(
        r"E:\病理资料\原图.png", r"E:\模型资料\分割模型.pth"
    )
    default_pdf = ExportManager().export_pdf(
        tmp_path / "default.pdf", original, result, metadata,
        color_map=Image.new("RGB", (120, 80), "black"),
    )
    full_pdf = ExportManager().export_pdf(
        tmp_path / "full.pdf", original, result, metadata,
        options={"include_full_paths": True},
        color_map=Image.new("RGB", (120, 80), "black"),
    )
    default_text = pdf_text(default_pdf)
    full_text = pdf_text(full_pdf)

    assert "原图.png" in default_text
    assert "E:\\病理资料" not in default_text
    assert r"E:\病理资料\原图.png" in full_text
    assert r"E:\模型资料\分割模型.pth" in full_text


def test_pdf_rejects_coordinate_mismatch_without_changing_metadata(tmp_path):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png")
    metadata = segmentation_metadata(str(original))
    before = copy.deepcopy(metadata)

    with pytest.raises(ExportError, match="could not be created"):
        ExportManager().export_pdf(
            tmp_path / "bad.pdf", original, result, metadata,
            color_map=Image.new("RGB", (100, 80), "black"),
        )

    assert metadata == before


def test_tile_appendix_is_optional_but_statistics_are_not(tmp_path):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png")
    metadata = tiled_metadata(str(original))
    color_map = Image.new("RGB", (120, 80), "green")
    detailed = ExportManager().export_pdf(
        tmp_path / "detailed.pdf", original, result, metadata,
        color_map=color_map,
    )
    compact = ExportManager().export_pdf(
        tmp_path / "compact.pdf", original, result, metadata,
        options={"include_tile_details": False}, color_map=color_map,
    )
    detailed_pages = [page.extract_text() or "" for page in PdfReader(detailed).pages]
    detailed_text = "\n".join(detailed_pages)
    compact_text = pdf_text(compact)

    assert len(detailed_pages) > 2
    assert sum("Source crop (x0, y0, x1, y1)" in page for page in detailed_pages) > 1
    assert "[0, 1, 2, 3]" in detailed_text
    assert "[99, 100, 101, 102]" in detailed_text
    assert "Source crop (x0, y0, x1, y1)" not in compact_text
    assert "Per-tile details were omitted" in compact_text
    for text in (detailed_text, compact_text):
        assert "STR" in text and "50" in text and "55.00%" in text
        assert "TUM" in text and "45.00%" in text


def test_legacy_spatial_report_states_that_separate_map_is_unavailable(tmp_path):
    original = save_image(tmp_path / "original.png")
    result = save_image(tmp_path / "overlay.png")
    output = ExportManager().export_pdf(
        tmp_path / "legacy.pdf", original, result,
        segmentation_metadata(str(original)),
    )
    assert "separate class color map is unavailable" in pdf_text(output)


def test_pdf_preferences_persist_independently_from_reminders(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    assert not dialog.pdf_paths_checkbox.isChecked()
    assert dialog.pdf_tile_details_checkbox.isChecked()
    dialog.pdf_paths_checkbox.click()
    dialog.pdf_tile_details_checkbox.click()
    dialog.reset_reminders_button.click()

    assert settings.value("export/pdfIncludeFullPaths", False, type=bool) is True
    assert settings.value("export/pdfIncludeTileDetails", True, type=bool) is False
    reopened = SettingsDialog(QSettings(settings.fileName(), QSettings.IniFormat))
    qtbot.addWidget(reopened)
    assert reopened.pdf_paths_checkbox.isChecked()
    assert not reopened.pdf_tile_details_checkbox.isChecked()
