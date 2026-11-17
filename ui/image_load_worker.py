"""Decode and verify selected images outside the Qt GUI thread."""
from PyQt5.QtCore import pyqtSignal
from core.inference_engine import _OwnedWorkerThread
from core.image_source import load_verified_image
from core.image_budget import PREVIEW_MAX_SIDE
from PIL import Image


class ImageLoadWorker(_OwnedWorkerThread):
    ready = pyqtSignal(object, object)
    failed = pyqtSignal(str)

    def __init__(self, path, decoder, parent):
        super().__init__(parent)
        self.path, self.decoder = str(path), decoder

    def run(self):
        try:
            image, identity = load_verified_image(self.path, decoder=self.decoder)
            if self.isInterruptionRequested():
                return
            image.thumbnail((PREVIEW_MAX_SIDE, PREVIEW_MAX_SIDE), Image.Resampling.LANCZOS)
            self.ready.emit(image, identity)
        except Exception as error:
            self.failed.emit(str(error) or "This image could not be opened.")
