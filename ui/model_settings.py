"""Task-specific model preferences, validated before they are persisted."""
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox

from core.inference_engine import ModelValidationThread


def default_model_key(task: str) -> str:
    return f"models/{task}/defaultPath"


class ModelSettingsPage(QWidget):
    default_changed = pyqtSignal(str)
    validation_finished = pyqtSignal()

    def __init__(self, settings, builtin_paths, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.builtin_paths = builtin_paths
        self._worker = None
        self._busy = False
        self.rows = {}
        layout = QVBoxLayout(self)
        explanation = QLabel("Defaults apply at startup and when selecting a task. History Re-run keeps its recorded model. Only load model files from sources you trust; model files can contain executable code.")
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        compatibility = QLabel(
            "Validation checks supported model loading, a 224 x 224 RGB test forward pass, finite output and the selected output task. "
            "It does not measure accuracy or verify tissue labels or training-scale matching. "
            "Tiled classification also requires compatible nine-class and preprocessing metadata at run time.")
        compatibility.setWordWrap(True)
        layout.addWidget(compatibility)
        for task in ("classification", "segmentation"):
            group = QGroupBox(task.capitalize(), self)
            box = QVBoxLayout(group)
            path = QLineEdit(group)
            path.setPlaceholderText("Select a trusted local model (.pt / .pth)")
            browse = QPushButton("Browse model…", group)
            save = QPushButton("Validate and use as default", group)
            restore = QPushButton("Restore built-in default", group)
            status = QLabel(group)
            status.setWordWrap(True)
            for widget in (path, browse, save, restore, status):
                box.addWidget(widget)
            self.rows[task] = dict(path=path, browse=browse, save=save, restore=restore, status=status)
            browse.clicked.connect(lambda checked=False, t=task: self._browse(t))
            save.clicked.connect(lambda checked=False, t=task: self.validate_default(t))
            restore.clicked.connect(lambda checked=False, t=task: self.restore_default(t))
            layout.addWidget(group)
            self.refresh(task)
        layout.addStretch()

    @property
    def is_validating(self):
        return self._worker is not None

    def set_busy(self, busy):
        self._busy = busy
        for row in self.rows.values():
            for key in ("path", "browse", "save", "restore"):
                row[key].setEnabled(not busy and not self.is_validating)

    def refresh(self, task):
        row = self.rows[task]
        saved = self.settings.value(default_model_key(task), "", type=str)
        row["path"].setText(saved)
        if saved:
            state = "Custom default" if Path(saved).is_file() else "Custom default unavailable (no automatic fallback)"
            text = f"{state}: {saved}"
        else:
            text = f"Built-in default: {self.builtin_paths[task]}"
        row["status"].setText(text)

    def _browse(self, task):
        path, _ = QFileDialog.getOpenFileName(self, "Select trusted model", "", "PyTorch models (*.pt *.pth)")
        if path:
            self.rows[task]["path"].setText(path)

    def validate_default(self, task):
        if self._busy or self.is_validating:
            return
        path = Path(self.rows[task]["path"].text().strip()).expanduser()
        if not path.is_file():
            self.rows[task]["status"].setText("Model file is unavailable. The saved default has not changed.")
            return
        path = path.resolve()
        worker = ModelValidationThread(path, self)
        self._worker = worker
        self.set_busy(self._busy)
        self.rows[task]["status"].setText("Loading and validating model…")
        worker.validation_request = (task, path)
        worker.validation_ready.connect(self._validation_ready)
        worker.validation_error.connect(self._validation_error)
        worker.finished.connect(self._finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _validation_ready(self, loaded, validation):
        task, path = self.sender().validation_request
        self._validated(task, path, validation)

    def _validation_error(self, message):
        task, _ = self.sender().validation_request
        self.rows[task]["status"].setText(f"{message} Saved default unchanged.")

    def _validated(self, task, path, validation):
        if validation.task_type != task:
            self.rows[task]["status"].setText(f"This model produces {validation.task_type} output. The {task} default has not changed.")
            return
        self.settings.setValue(default_model_key(task), str(path))
        self.settings.sync()
        self.refresh(task)
        self.default_changed.emit(task)

    def _finished(self):
        self._worker = None
        self.set_busy(self._busy)
        self.validation_finished.emit()

    def restore_default(self, task):
        if self._busy or self.is_validating:
            return
        # Keep an explicit built-in selection so task changes honor a restore.
        self.settings.setValue(default_model_key(task), "")
        self.settings.sync()
        self.refresh(task)
        self.default_changed.emit(task)
