"""Export inference results as PNG images and task-aware PDF reports."""

import logging
import os
import tempfile
from pathlib import Path

from fpdf.errors import FPDFException
from matplotlib.figure import Figure
from PIL import Image

from data.pdf_report import (
    DISCLAIMER,
    _ReportPDF,
    _add_metadata_table,
    _safe_pdf_text,
    write_report,
)


logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Report an export failure with a user-friendly message."""


class ExportCancelled(ExportError):
    """A cooperative cancellation; the destination remains untouched."""


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
        *,
        options: dict | None = None,
        color_map: Image.Image | None = None,
        progress=None,
    ) -> Path:
        """Create an A4 PDF without changing recorded analysis data."""
        destination = Path(output_path)
        original_path = Path(original_image_path)
        result_path = Path(result_image_path)
        try:
            if not original_path.is_file() or not result_path.is_file():
                raise ExportError("The selected image file could not be found.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".zy-path-", suffix=".pdf", dir=destination.parent
            )
            os.close(descriptor)
            temporary = Path(temporary_name)
            try:
                write_report(
                    temporary, original_path, result_path, metadata,
                    options=options, color_map=color_map, progress=progress,
                )
                if progress is not None:
                    progress("Finishing export", 98)
                # Replace only after a complete, successful generation.
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
            return destination
        except ExportError:
            raise
        except (
            AttributeError,
            FPDFException,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            logger.exception("Could not export a PDF report.")
            raise ExportError(
                "The PDF report could not be created. Check the files and try again."
            ) from error
