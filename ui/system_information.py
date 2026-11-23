"""Inspectable runtime information without loading models or exposing file paths."""
import importlib.metadata
import platform
import sqlite3
import struct
import sys
from pathlib import Path

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt5.QtWidgets import QApplication

from ui.language import tr
from utils.version import APP_VERSION
from core.classification_input import DEFAULT_CLASSIFICATION_RESIZE, DEFAULT_CLASSIFICATION_TILE_SIZE

TECHNOLOGIES = (
    ("PyQt5", "Desktop interface"),
    ("torch", "PyTorch inference"),
    ("torchvision", "Model architectures and image transforms"),
    ("transformers", "UPerNet architecture support"),
    ("Pillow", "Image loading, resizing and compositing"),
    ("opencv-python-headless", "Classification image decoding and INTER_LINEAR resizing"),
    ("numpy", "Image arrays and statistics"),
    ("matplotlib", "Classification probability charts"),
    ("fpdf2", "PDF reports"),
)


def system_information(settings, app_version=APP_VERSION):
    app = QApplication.instance()
    lines = ["ZY-Path " + tr("version: {version}").format(version=app_version), "", tr("Runtime"),
             f"OS: {platform.system()} {platform.release()}",
             f"{tr('Architecture')}: {platform.machine()} (" + tr("{bits}-bit Python").format(bits=struct.calcsize('P') * 8) + ")",
             f"Python: {sys.version.split()[0]} ({platform.python_implementation()})",
             f"Qt: {QT_VERSION_STR}", f"PyQt: {PYQT_VERSION_STR}",
             f"{tr('Qt platform')}: {app.platformName() if app else tr('unavailable')}"]
    if app and app.primaryScreen():
        screen = app.primaryScreen()
        area = screen.availableGeometry()
        lines.extend([tr("Primary screen available: {width} x {height} logical pixels").format(width=area.width(), height=area.height()),
                      f"{tr('Primary screen device pixel ratio')}: {screen.devicePixelRatio():g}"])
    lines.extend(["", tr("Technology stack")])
    for package, purpose in TECHNOLOGIES:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = tr("not installed")
        lines.append(f"{package}: {version} — {tr(purpose)}")
    lines.extend([f"SQLite: {sqlite3.sqlite_version} — {tr('Local history and analysis metadata')}",
                  tr("Built-in classification: DenseNet (9 classes)"),
                  tr("Built-in segmentation: UPerNet (separate segmentation labels)"),
                  tr("Model loading: CPU; large-image segmentation inference: CPU"), "", tr("Saved configuration"),
                  f"{tr('Theme')}: {tr(settings.value('appearance/theme', 'Light', type=str))}",
                  f"{tr('Classification startup mode')}: {settings.value('classification/defaultMode', 'single_image', type=str)}",
                  f"{tr('Classification original-image tiles')}: {settings.value('classificationTiles/width', DEFAULT_CLASSIFICATION_TILE_SIZE, type=int)} x "
                  f"{settings.value('classificationTiles/height', DEFAULT_CLASSIFICATION_TILE_SIZE, type=int)} px",
                  tr("Built-in classifier source dataset: NCT-CRC-HE-100K; 224 x 224 px at 0.5 micrometres/pixel"),
                  tr("Built-in classifier network input: RGB, float32, raw255 (0-255); 224 x 224 px"),
                  tr("Image MPP: inspect or enter the image calibration in Image sampling"),
                  tr("Physical-scale matching requires known image MPP and a documented model tissue field"),
                  tr("Built-in CRC tissue field: 112 x 112 micrometres; calibrated source crops depend on image MPP"),
                  tr("Built-in segmentation: reference pixel pipeline; no target MPP assumed"),
                  tr("Built-in classification image reader: OpenCV IMREAD_COLOR, BGR to RGB"),
                  f"{tr('Resize for classifiers without an input profile')}: {settings.value('classification/resizeBackend', DEFAULT_CLASSIFICATION_RESIZE, type=str)}"])
    for task in ("classification", "segmentation"):
        path = settings.value(f"models/{task}/defaultPath", "", type=str)
        state = ("custom (file available)" if Path(path).is_file() else "custom (file unavailable)") if path else "built-in"
        lines.append(tr("{task} default model: {state}").format(task=tr(task.capitalize()), state=tr(state)))
    lines.extend(["", tr("Image/model paths, usernames and hostnames are not included."),
                  tr("Inspect this displayed information before copying. Nothing is sent automatically.")])
    return "\n".join(lines)
