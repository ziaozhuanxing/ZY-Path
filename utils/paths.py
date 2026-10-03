"""Resolve bundled resource and per-user data paths."""

import os
import sys
from pathlib import Path


def resource_path(relative_path: str | Path) -> Path:
    """Return a path to a bundled resource in source or frozen mode."""
    bundle_root = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    )
    return bundle_root / relative_path


def app_data_dir() -> Path:
    """Create and return the current user's ZY-Path data directory."""
    app_data_root = Path(
        os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
    )
    data_dir = app_data_root / "ZY-Path"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir