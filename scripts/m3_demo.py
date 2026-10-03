"""Generate sample images and export a demo PDF report."""

import sys
from pathlib import Path

from PIL import Image, ImageDraw


project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from data.export_manager import ExportManager


def main() -> None:
    """Create demo images and export them to the project output folder."""
    output_dir = project_root / "demo_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    original_path = output_dir / "demo_original.png"
    result_path = output_dir / "demo_result.png"

    original = Image.new("RGB", (480, 320), "#f4eee6")
    original_draw = ImageDraw.Draw(original)
    original_draw.ellipse((90, 55, 255, 220), fill="#d28b72")
    original_draw.ellipse((220, 125, 395, 290), fill="#86a9a2")
    original.save(original_path, format="PNG")

    result = original.copy()
    result_draw = ImageDraw.Draw(result)
    result_draw.ellipse((90, 55, 255, 220), outline="#bd3f35", width=6)
    result_draw.ellipse((220, 125, 395, 290), outline="#336f68", width=6)
    result.save(result_path, format="PNG")

    manager = ExportManager()
    png_path = manager.export_png(result, output_dir / "demo_export.png")
    pdf_path = manager.export_pdf(
        output_dir / "demo_report.pdf",
        original_path,
        result_path,
        {
            "model_name": "Demo model",
            "task_type": "segmentation",
            "timestamp": "2026-10-03T12:00:00+00:00",
            "image_path": str(original_path),
            "result_label": "Demo regions",
            "confidence": 0.92,
        },
    )

    print(png_path)
    print(pdf_path)


if __name__ == "__main__":
    main()