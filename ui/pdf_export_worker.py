"""Background PDF export: immutable inputs, cooperative cancellation and no GUI calls."""
from copy import deepcopy
from pathlib import Path
import logging
import tempfile
import time

from PyQt5.QtCore import QThread, pyqtSignal

from data.export_manager import ExportCancelled


logger = logging.getLogger(__name__)


class PdfExportWorker(QThread):
    progress = pyqtSignal(str, int)

    def __init__(self, manager, destination, original_path, result_path, metadata,
                 *, result_image=None, color_map=None, options=None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.destination = str(destination)
        self.original_path = str(original_path)
        self.result_path = str(result_path)
        self.metadata = deepcopy(metadata)
        self.options = deepcopy(options or {})
        self.result_image = result_image.copy() if result_image is not None else None
        self.color_map = color_map.copy() if color_map is not None else None
        self.outcome = None
        self.error_message = None
        self._last_progress = None
        self._last_emit = 0

    def cancel(self):
        self.requestInterruption()

    def _progress(self, message, percent):
        if self.isInterruptionRequested():
            raise ExportCancelled("PDF export cancelled.")
        now = time.monotonic()
        if (message, percent) != self._last_progress or now - self._last_emit >= .1:
            self.progress.emit(message, percent)
            self._last_progress = (message, percent)
            self._last_emit = now

    def run(self):
        try:
            self._progress("Preparing result presentation", 1)
            with tempfile.TemporaryDirectory(prefix="zy-path-pdf-") as directory:
                result_path = self.result_path
                if self.result_image is not None:
                    result_path = Path(directory) / "presentation.png"
                    self.result_image.save(result_path)
                self._progress("Preparing report", 5)
                self.manager.export_pdf(
                    self.destination, self.original_path, result_path, self.metadata,
                    options=self.options, color_map=self.color_map, progress=self._progress,
                )
            # Completion after the atomic destination replacement wins over a
            # late cancel click. Never label a successfully saved PDF cancelled.
            self.outcome = "saved"
        except ExportCancelled:
            self.outcome = "cancelled"
        except Exception:
            logger.exception("Background PDF export failed")
            self.outcome = "error"
            self.error_message = "The PDF report could not be saved. Check the files and destination, then try again."
