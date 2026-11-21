"""Cancellable background verification, rendering and paired PNG export."""
from copy import deepcopy
import logging
from pathlib import Path
from PIL import Image
from PyQt5.QtCore import pyqtSignal
from core.inference_engine import _OwnedWorkerThread
from data.artifact_integrity import verify_saved_artifacts
from data.export_manager import ExportCancelled
from data.png_bundle import export_png_bundle
from ui.result_rendering import render_snapshot

logger = logging.getLogger(__name__)


class PngExportWorker(_OwnedWorkerThread):
    progress = pyqtSignal(str, int)

    def __init__(self, destination, result_path, metadata, *, presentation=None, parent=None):
        super().__init__(parent)
        self.destination, self.result_path = str(destination), str(result_path)
        self.metadata = deepcopy(metadata)
        self.presentation = presentation
        self.outcome = self.error_message = None

    def cancel(self):
        self.requestInterruption()

    def _progress(self, message, percent):
        if self.isInterruptionRequested():
            raise ExportCancelled('PNG export cancelled.')
        self.progress.emit(message, percent)

    def run(self):
        try:
            self._progress('Verifying saved result', 5)
            analysis = self.metadata.get('classification_analysis') or self.metadata.get('segmentation_analysis') or {}
            verify_saved_artifacts(analysis, {'result': self.result_path},
                check_cancelled=lambda: self._progress('Verifying saved result', 5))
            self._progress('Rendering PNG presentation', 15)
            if self.presentation is not None:
                image = render_snapshot(self.presentation)
            else:
                with Image.open(self.result_path) as saved:
                    image = saved.copy()
            verify_saved_artifacts(analysis, {'result': self.result_path},
                check_cancelled=lambda: self._progress('Verifying saved result', 20))
            self._progress('Preparing PNG bundle', 25)
            export_png_bundle(image, self.destination, self.metadata, progress=self._progress)
            self.outcome = 'saved'
        except ExportCancelled:
            self.outcome = 'cancelled'
        except Exception as error:
            logger.exception('Background PNG bundle export failed')
            self.outcome = 'error'
            self.error_message = str(error) or 'The PNG bundle could not be saved. Previous files were kept.'
