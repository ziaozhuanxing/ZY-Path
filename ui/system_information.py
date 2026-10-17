"""Inspectable runtime information without loading models or exposing file paths."""
import importlib.metadata
import platform
import sqlite3
import struct
import sys
from pathlib import Path

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt5.QtWidgets import QApplication

from utils.version import APP_VERSION

TECHNOLOGIES = (
    ("PyQt5", "Desktop interface"),
    ("torch", "PyTorch inference"),
    ("torchvision", "Model architectures and image transforms"),
    ("transformers", "UPerNet architecture support"),
    ("Pillow", "Image loading, resizing and compositing"),
    ("opencv-python-headless", "Optional classification INTER_LINEAR resizing"),
    ("numpy", "Image arrays and statistics"),
    ("matplotlib", "Classification probability charts"),
    ("fpdf2", "PDF reports"),
)


def system_information(settings, app_version=APP_VERSION):
    app = QApplication.instance()
    lines = [f"ZY-Path version: {app_version}", "", "Runtime",
             f"OS: {platform.system()} {platform.release()}",
             f"Architecture: {platform.machine()} ({struct.calcsize('P') * 8}-bit Python)",
             f"Python: {sys.version.split()[0]} ({platform.python_implementation()})",
             f"Qt: {QT_VERSION_STR}", f"PyQt: {PYQT_VERSION_STR}",
             f"Qt platform: {app.platformName() if app else 'unavailable'}"]
    if app and app.primaryScreen():
        screen = app.primaryScreen()
        area = screen.availableGeometry()
        lines.extend([f"Primary screen available: {area.width()} x {area.height()} logical pixels",
                      f"Primary screen device pixel ratio: {screen.devicePixelRatio():g}"])
    lines.extend(["", "Technology stack"])
    for package, purpose in TECHNOLOGIES:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = "not installed"
        lines.append(f"{package}: {version} — {purpose}")
    lines.extend([f"SQLite: {sqlite3.sqlite_version} — Local history and analysis metadata",
                  "Built-in classification: DenseNet (9 classes)",
                  "Built-in segmentation: UPerNet (separate segmentation labels)",
                  "Model loading: CPU; large-image segmentation inference: CPU", "", "Saved configuration",
                  f"Theme: {settings.value('appearance/theme', 'Light', type=str)}",
                  f"Classification startup mode: {settings.value('classification/defaultMode', 'single_image', type=str)}",
                  f"Classification original-image tiles: {settings.value('classificationTiles/width', 512, type=int)} x "
                  f"{settings.value('classificationTiles/height', 512, type=int)} px",
                  "Training scale / magnification: unconfirmed",
                  f"Classification resize method: {settings.value('classification/resizeBackend', 'pillow_bilinear', type=str)}"])
    for task in ("classification", "segmentation"):
        path = settings.value(f"models/{task}/defaultPath", "", type=str)
        state = ("custom (file available)" if Path(path).is_file() else "custom (file unavailable)") if path else "built-in"
        lines.append(f"{task.capitalize()} default model: {state}")
    lines.extend(["", "Image/model paths, usernames and hostnames are not included.",
                  "Inspect this displayed information before copying. Nothing is sent automatically."])
    return "\n".join(lines)
