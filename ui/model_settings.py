"""Task-specific model preferences, validated before they are persisted."""
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox

from ui.language import tr
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
        self._validated_details = {}
        layout = QVBoxLayout(self)
        explanation = QLabel(tr("Defaults apply at startup and when selecting a task. History Re-run keeps its recorded model. Only load model files from sources you trust; model files can contain executable code."))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        compatibility = QLabel(
            tr("Validation uses the model's declared input size and preprocessing. Without an input profile, "
            "the compatibility probe uses 224 x 224 RGB pixels. Class counts and output task must agree "
            "with the supplied model metadata; local models are not restricted to nine classes. "
            "Single-logit binary models are not supported. Validation does not measure accuracy or "
            "establish suitability for a tissue, stain or physical scale."))
        compatibility.setWordWrap(True)
        layout.addWidget(compatibility)
        for task in ("classification", "segmentation"):
            group = QGroupBox(tr(task.capitalize()), self)
            box = QVBoxLayout(group)
            path = QLineEdit(group)
            path.setPlaceholderText(tr("Select a trusted local model (.pt / .pth)"))
            browse = QPushButton(tr("Browse model…"), group)
            save = QPushButton(tr("Validate and use as default"), group)
            restore = QPushButton(tr("Restore built-in default"), group)
            status = QLabel(group)
            status.setWordWrap(True)
            details = QLabel(group)
            details.setObjectName(task + 'ModelRequirementsSummary')
            details.setTextFormat(Qt.PlainText)
            details.setWordWrap(True)
            details.setTextInteractionFlags(Qt.TextSelectableByMouse)
            for widget in (path, browse, save, restore, status, details):
                box.addWidget(widget)
            self.rows[task] = dict(path=path, browse=browse, save=save, restore=restore, status=status, details=details)
            browse.clicked.connect(lambda checked=False, t=task: self._browse(t))
            save.clicked.connect(lambda checked=False, t=task: self.validate_default(t))
            restore.clicked.connect(lambda checked=False, t=task: self.restore_default(t))
            layout.addWidget(group)
            path.textChanged.connect(lambda _text, t=task: self._refresh_details(t))
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
            text = f"{tr(state)}: {saved}"
        else:
            text = f"{tr('Built-in default')}: {self.builtin_paths[task]}"
        row["status"].setText(text)
        self._refresh_details(task)

    def _refresh_details(self, task):
        path = self.rows[task]['path'].text().strip()
        try:
            key = str(Path(path or self.builtin_paths[task]).expanduser().resolve())
        except (OSError, RuntimeError):
            key = ''
        text = self._validated_details.get((task, key),
            tr('Input requirements have not been checked for this selection. Validate the model to see its actual input, output classes and preprocessing. No tissue field is inferred from the filename.'))
        self.rows[task]['details'].setText(text)

    def remember_validated_model(self, path, loaded, validation):
        task = validation.task_type
        self._validated_details[(task, str(Path(path).resolve()))] = model_requirements_summary(loaded, validation)
        self._refresh_details(task)

    def _browse(self, task):
        path, _ = QFileDialog.getOpenFileName(self, tr("Select trusted model"), "", "PyTorch models (*.pt *.pth)")
        if path:
            self.rows[task]["path"].setText(path)

    def validate_default(self, task):
        if self._busy or self.is_validating:
            return
        path = Path(self.rows[task]["path"].text().strip()).expanduser()
        if not path.is_file():
            self.rows[task]["status"].setText(tr("Model file is unavailable. The saved default has not changed."))
            return
        path = path.resolve()
        worker = ModelValidationThread(path, self)
        self._worker = worker
        self.set_busy(self._busy)
        self.rows[task]["status"].setText(tr("Loading and validating model…"))
        worker.validation_request = (task, path)
        worker.validation_ready.connect(self._validation_ready)
        worker.validation_error.connect(self._validation_error)
        worker.finished.connect(self._finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _validation_ready(self, loaded, validation):
        task, path = self.sender().validation_request
        self._validated(task, path, validation, loaded)

    def _validation_error(self, message):
        task, _ = self.sender().validation_request
        self.rows[task]["status"].setText(tr("{message} Saved default unchanged.").format(message=message))

    def _validated(self, task, path, validation, loaded=None):
        if validation.task_type != task:
            self.rows[task]["status"].setText(tr("This model produces {output} output. The {task} default has not changed.")
                .format(output=tr(validation.task_type), task=tr(task)))
            return
        self._validated_details[(task, str(path))] = model_requirements_summary(loaded, validation)
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


def model_requirements_summary(loaded, validation):
    """Describe observed output and the declared contract; never infer tissue labels."""
    profile = getattr(loaded, 'input_profile', None)
    size = profile.input_size if profile else (224, 224)
    input_size = tr("Input: {width} x {height} RGB pixels").format(width=size[0], height=size[1])
    if profile is None:
        input_size += tr(" (fallback probe; no input profile)")
    task = tr(validation.task_type)
    lines = [tr("Last validated requirements:"), input_size,
             tr("Output: {task}, {count} classes").format(task=task, count=validation.num_classes)]
    labels = getattr(profile, 'classes', None) or getattr(loaded, 'classes', None)
    if labels:
        shown = ', '.join(str(label) for label in labels[:8])
        lines.append(tr("Declared class order") + ": " + shown + (tr(", ... ({count} total)").format(count=len(labels)) if len(labels) > 8 else ""))
    else:
        lines.append(tr("Class names/order: not supplied; output channels do not establish tissue labels."))
    normalization = profile.normalization if profile else getattr(loaded, 'preprocess_profile', None)
    lines.append(tr("Declared preprocessing") + ": " + str(normalization or tr("not documented")))
    if profile and profile.normalization == 'custom':
        lines.append(tr("Input multiplier: {scale:g}; mean: {mean}; std: {std}")
                     .format(scale=profile.input_scale, mean=profile.mean, std=profile.std))
    if profile:
        lines.append(tr("Reader: {decoder}; resize: {resize}").format(decoder=profile.image_decoder, resize=profile.resize_backend))
    field = getattr(profile, 'field_um', None)
    lines.append(tr("Declared tissue field: {width:g} x {height:g} um; matching also requires known image MPP.")
                 .format(width=field[0], height=field[1]) if field
                 else tr("Physical tissue field: not documented; no target MPP is assumed."))
    lines.append(tr("Loading/output compatibility checked. Prediction accuracy and tissue suitability are not established by this check."))
    return '\n'.join(lines)
