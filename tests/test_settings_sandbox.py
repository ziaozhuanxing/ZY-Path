"""Verify test isolation without changing production preference persistence."""
from pathlib import Path
from PyQt5.QtCore import QSettings


def test_default_preferences_use_per_test_store(tmp_path):
    settings = QSettings("ZY-Path", "ZY-Path")
    assert QSettings.defaultFormat() == QSettings.IniFormat
    assert Path(settings.fileName()).resolve().is_relative_to(tmp_path.resolve())
    assert settings.value("classification/defaultMode", "single_image") == "single_image"


def test_preferences_still_persist_between_instances_in_own_store():
    settings = QSettings("ZY-Path", "ZY-Path")
    settings.setValue("classification/defaultMode", "tiled_analysis")
    settings.sync()
    reopened = QSettings("ZY-Path", "ZY-Path")
    assert reopened.value("classification/defaultMode") == "tiled_analysis"
