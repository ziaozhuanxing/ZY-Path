"""Background PDF export: immutable inputs, cooperative cancellation and no GUI calls."""
from copy import deepcopy
from pathlib import Path
import logging
import tempfile
import time

from PyQt5.QtCore import pyqtSignal
from core.inference_engine import _OwnedWorkerThread
from core.image_source import analysis_identity, verify_image_source
from data.artifact_integrity import verify_saved_artifacts
from ui.result_rendering import render_snapshot

from data.export_manager import ExportCancelled, ExportError


logger = logging.getLogger(__name__)


class PdfExportWorker(_OwnedWorkerThread):
    progress = pyqtSignal(str, int)

    def __init__(self, manager, destination, original_path, result_path, metadata,
                 *, result_image=None, color_map=None, options=None, presentation=None, require_verified_source=False, parent=None):
        super().__init__(parent)
        self.presentation = presentation
        self.require_verified_source = require_verified_source
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
            self._progress("Verifying report sources", 1)
            analysis = self.metadata.get('classification_analysis') or self.metadata.get('segmentation_analysis') or {}
            verify_saved_artifacts(analysis, {'result': self.result_path},
                check_cancelled=lambda: self._progress('Verifying saved result', 2))
            if self.require_verified_source:
                if not Path(self.original_path).is_file():
                    raise ExportError(f'Original image not found: {self.original_path}')
                verify_image_source(self.original_path, analysis_identity(analysis),
                    check_cancelled=lambda: self._progress('Verifying original image', 3))
            if self.presentation is not None:
                self.result_image = render_snapshot(self.presentation)
                self.color_map = self.presentation['color_map']
            self._progress("Preparing result presentation", 4)
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
        except (ExportError, ValueError, OSError) as error:
            logger.exception("Background PDF export failed")
            self.outcome = "error"
            self.error_message = f"The PDF report could not be saved. {error}"
        except Exception:
            logger.exception("Background PDF export failed")
            self.outcome = "error"
            self.error_message = "The PDF report could not be saved. Check the files and destination, then try again."
