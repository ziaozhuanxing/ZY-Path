"""Export inference results as PNG images and PDF reports."""

import logging
from pathlib import Path

from fpdf import FPDF
from fpdf.errors import FPDFException
from matplotlib.figure import Figure
from PIL import Image

from utils.paths import resource_path


logger = logging.getLogger(__name__)
DISCLAIMER = "For educational and research use only. Not a clinical diagnosis."


class ExportError(Exception):
    """Report an export failure with a user-friendly message."""


class _ReportPDF(FPDF):
    """Draw the common header and footer on report pages."""

    def __init__(self, logo_path: Path | None) -> None:
        super().__init__(format="A4")
        self.logo_path = logo_path
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=18)

    def header(self) -> None:
        title_x = self.l_margin
        if self.logo_path is not None:
            self.image(
                str(self.logo_path),
                x=self.l_margin,
                y=8,
                h=10,
                keep_aspect_ratio=True,
            )
            title_x += 16

        self.set_xy(title_x, 9)
        self.set_font("Helvetica", "B", 16)
        self.cell(
            self.w - self.r_margin - title_x,
            10,
            _safe_pdf_text("ZY-Path Report"),
        )
        self.set_draw_color(44, 82, 130)
        self.set_line_width(0.4)
        self.line(self.l_margin, 23, self.w - self.r_margin, 23)
        self.set_y(27)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.cell(
            0,
            5,
            _safe_pdf_text(f"Page {self.page_no()} | {DISCLAIMER}"),
            align="C",
        )


class ExportManager:
    """Save result images and create educational-use PDF reports."""

    def export_png(self, source: Figure | Image.Image, output_path: str | Path) -> Path:
        """Save a Matplotlib figure or Pillow image as a PNG file."""
        destination = Path(output_path)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(source, Figure):
                source.savefig(destination, dpi=150, format="png")
            elif isinstance(source, Image.Image):
                source.save(destination, format="PNG")
            else:
                raise ExportError(
                    "The source must be a Matplotlib figure or a Pillow image."
                )
            return destination
        except ExportError:
            raise
        except (FPDFException, KeyError, OSError, RuntimeError, ValueError) as error:
            logger.exception("Could not export a PNG image.")
            raise ExportError("The PNG image could not be saved.") from error

    def export_pdf(
        self,
        output_path: str | Path,
        original_image_path: str | Path,
        result_image_path: str | Path,
        metadata: dict,
    ) -> Path:
        """Create an A4 PDF report with images, metadata, and a disclaimer."""
        destination = Path(output_path)
        original_path = Path(original_image_path)
        result_path = Path(result_image_path)
        try:
            if not original_path.is_file() or not result_path.is_file():
                raise ExportError("The selected image file could not be found.")

            destination.parent.mkdir(parents=True, exist_ok=True)
            logo_path = resource_path(Path("assets") / "logo.png")
            pdf = _ReportPDF(logo_path if logo_path.is_file() else None)
            pdf.add_page()

            _add_report_image(pdf, original_path, "Original image")
            _add_report_image(pdf, result_path, "Result image")
            _add_metadata_table(pdf, metadata)
            pdf.output(str(destination))
            return destination
        except ExportError:
            raise
        except (
            AttributeError,
            FPDFException,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            logger.exception("Could not export a PDF report.")
            raise ExportError(
                "The PDF report could not be created. Check the files and try again."
            ) from error


def _safe_pdf_text(value: object) -> str:
    return str(value).encode("latin-1", errors="replace").decode("latin-1")


def _add_report_image(pdf: _ReportPDF, image_path: Path, title: str) -> None:
    if pdf.get_y() + 18 > pdf.page_break_trigger:
        pdf.add_page()

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, _safe_pdf_text(title))
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 8)
    with Image.open(image_path) as image:
        image_width, image_height = image.size

    available_height = pdf.page_break_trigger - pdf.get_y()
    scale = min(pdf.epw / image_width, available_height / image_height)
    displayed_width = image_width * scale
    displayed_height = image_height * scale
    image_x = pdf.l_margin + (pdf.epw - displayed_width) / 2
    image_y = pdf.get_y()
    pdf.image(
        str(image_path),
        x=image_x,
        y=image_y,
        w=displayed_width,
        h=displayed_height,
        keep_aspect_ratio=True,
    )
    pdf.set_y(image_y + displayed_height + 5)


def _add_metadata_table(pdf: _ReportPDF, metadata: dict) -> None:
    if pdf.get_y() + 18 > pdf.page_break_trigger:
        pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "Metadata")
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 9)

    rows = [
        ("Model name", metadata.get("model_name", "")),
        ("Task type", metadata.get("task_type", "")),
        ("Timestamp", metadata.get("timestamp", "")),
        ("Image path", metadata.get("image_path", "")),
    ]
    if metadata.get("result_label") is not None:
        rows.append(("Result label", metadata["result_label"]))
    if metadata.get("confidence") is not None:
        try:
            confidence = float(metadata["confidence"])
        except (TypeError, ValueError) as error:
            raise ExportError("Confidence must be a number between 0 and 1.") from error
        if not 0 <= confidence <= 1:
            raise ExportError("Confidence must be a number between 0 and 1.")
        rows.append(("Confidence", f"{confidence * 100:.1f}%"))

    for label, value in rows:
        pdf.set_xy(pdf.l_margin, pdf.get_y())
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 244, 248)
        pdf.cell(pdf.epw, 6, _safe_pdf_text(label), border=1, fill=True)
        pdf.set_xy(pdf.l_margin, pdf.get_y() + 6)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(pdf.epw, 6, _safe_pdf_text(value), border="LRB")
        pdf.set_xy(pdf.l_margin, pdf.get_y())