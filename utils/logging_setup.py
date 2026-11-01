"""Persistent diagnostics for source execution and windowed Windows releases."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from utils.paths import app_data_dir


def configure_logging(directory: Path | None = None, *, logger: logging.Logger | None = None) -> Path | None:
    """Keep console output where available and a bounded per-user UTF-8 log."""
    target = logger if logger is not None else logging.getLogger()
    target.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    stream = sys.stderr
    if stream is not None and not any(
        isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler)
        and handler.stream is stream for handler in target.handlers
    ):
        console = logging.StreamHandler(stream)
        console.setFormatter(formatter)
        target.addHandler(console)
    try:
        folder = Path(directory) if directory is not None else app_data_dir() / "logs"
        folder.mkdir(parents=True, exist_ok=True)
        path = (folder / "zy-path.log").resolve()
        if not any(isinstance(handler, RotatingFileHandler) and Path(handler.baseFilename) == path
                   for handler in target.handlers):
            handler = RotatingFileHandler(path, maxBytes=2 * 1024 * 1024, backupCount=2, encoding="utf-8")
            handler.setFormatter(formatter)
            target.addHandler(handler)
        return path
    except OSError:
        # Diagnostics must not prevent startup when the log folder is unwritable.
        target.warning("Persistent logging could not be opened.", exc_info=True)
        return None
