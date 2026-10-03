from pathlib import Path

import pytest
from fpdf import FPDF
from matplotlib.figure import Figure
from PIL import Image

from data.export_manager import ExportError, ExportManager


def create_test_image(image_path: Path, color: str) -> None:
    Image.new("RGB", (40, 30), color).save(image_path, format="PNG")


def assert_pdf_contains_both_images(pdf_path: Path) -> None:
    pdf_bytes = pdf_path.read_bytes()
    assert pdf_bytes.startswith(b"%PDF")
    assert pdf_bytes.count(b"/Subtype /Image") >= 2


def test_export_png_accepts_matplotlib_figure(tmp_path: Path) -> None:
    figure = Figure()
    figure.subplots().plot([0, 1], [0, 1])
    output_path = tmp_path / "nested" / "figure.png"

    saved_path = ExportManager().export_png(figure, output_path)

    assert saved_path == output_path
    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_export_png_accepts_pillow_image(tmp_path: Path) -> None:
    source = Image.new("RGB", (20, 15), "red")
    output_path = tmp_path / "image.png"

    saved_path = ExportManager().export_png(source, output_path)

    assert saved_path == output_path
    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_export_pdf_creates_report_with_optional_fields(tmp_path: Path) -> None:
    original_path = tmp_path / "original.png"
    result_path = tmp_path / "result.png"
    create_test_image(original_path, "white")
    create_test_image(result_path, "green")
    output_path = tmp_path / "reports" / "report.pdf"

    saved_path = ExportManager().export_pdf(
        output_path,
        original_path,
        result_path,
        {
            "model_name": "demo-model",
            "task_type": "classification",
            "timestamp": "2026-10-03T12:00:00+00:00",
            "image_path": str(original_path),
            "result_label": "tissue",
            "confidence": 0.875,
        },
    )

    assert saved_path == output_path
    assert_pdf_contains_both_images(output_path)


def test_export_pdf_works_without_optional_fields(tmp_path: Path) -> None:
    original_path = tmp_path / "original.png"
    result_path = tmp_path / "result.png"
    create_test_image(original_path, "white")
    create_test_image(result_path, "blue")

    output_path = ExportManager().export_pdf(
        tmp_path / "report.pdf",
        original_path,
        result_path,
        {
            "model_name": "demo-model",
            "task_type": "segmentation",
            "timestamp": "2026-10-03T12:00:00+00:00",
            "image_path": str(original_path),
        },
    )

    assert_pdf_contains_both_images(output_path)


def test_export_pdf_keeps_metadata_labels_inside_left_margin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_path = tmp_path / "original.png"
    result_path = tmp_path / "result.png"
    create_test_image(original_path, "white")
    create_test_image(result_path, "blue")

    labels = {"Model name", "Task type", "Timestamp", "Image path"}
    label_positions: dict[str, float] = {}
    original_cell = FPDF.cell

    def record_cell_position(
        pdf: FPDF,
        width: float,
        height: float,
        text: str = "",
        *args: object,
        **kwargs: object,
    ) -> None:
        if text in labels:
            label_positions[text] = pdf.get_x()
        original_cell(pdf, width, height, text, *args, **kwargs)

    monkeypatch.setattr(FPDF, "cell", record_cell_position)
    ExportManager().export_pdf(
        tmp_path / "report.pdf",
        original_path,
        result_path,
        {
            "model_name": "demo-model",
            "task_type": "segmentation",
            "timestamp": "2026-10-03T12:00:00+00:00",
            "image_path": str(original_path),
        },
    )

    assert set(label_positions) == labels
    assert all(position == pytest.approx(15) for position in label_positions.values())


def test_export_pdf_replaces_unsupported_unicode(tmp_path: Path) -> None:
    original_path = tmp_path / "原图.png"
    result_path = tmp_path / "结果图.png"
    create_test_image(original_path, "white")
    create_test_image(result_path, "red")

    output_path = ExportManager().export_pdf(
        tmp_path / "报告.pdf",
        original_path,
        result_path,
        {
            "model_name": "模型名称",
            "task_type": "classification",
            "timestamp": "2026-10-03T12:00:00+00:00",
            "image_path": str(original_path),
            "result_label": "组织",
        },
    )

    assert output_path.read_bytes().startswith(b"%PDF")


def test_export_pdf_raises_for_missing_original_image(tmp_path: Path) -> None:
    result_path = tmp_path / "result.png"
    create_test_image(result_path, "blue")

    with pytest.raises(ExportError, match="image file could not be found"):
        ExportManager().export_pdf(
            tmp_path / "report.pdf",
            tmp_path / "missing.png",
            result_path,
            {},
        )


def test_export_pdf_raises_for_missing_result_image(tmp_path: Path) -> None:
    original_path = tmp_path / "original.png"
    create_test_image(original_path, "white")

    with pytest.raises(ExportError, match="image file could not be found"):
        ExportManager().export_pdf(
            tmp_path / "report.pdf",
            original_path,
            tmp_path / "missing-result.png",
            {},
        )