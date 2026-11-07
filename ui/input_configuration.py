"""Image calibration and declarative model-input editing."""

import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QPushButton, QRadioButton, QScrollArea, QVBoxLayout, QWidget,
)
from PyQt5.QtCore import Qt, QSaveFile, QIODevice, QEvent

from core.model_profile import ModelInputProfile, SCHEMA, palette, read_profile, validate_known_contract, file_sha256
from ui.explicit_spin_box import ExplicitSpinBox
from ui.explicit_combo_box import ExplicitComboBox, forward_wheel_to_page
from ui.input_help import configure_help_window, show_input_help


class ExplicitDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.lineEdit() and event.type() == QEvent.Wheel:
            forward_wheel_to_page(self, event)
            return True
        return super().eventFilter(watched, event)

    def wheelEvent(self, event):
        forward_wheel_to_page(self, event)


def numeric_pair(parent, values=(0, 0), *, integer=False):
    host = QWidget(parent)
    layout = QHBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    boxes = []
    for value in values:
        box = ExplicitSpinBox(host) if integer else ExplicitDoubleSpinBox(host)
        if not integer:
            box.setDecimals(6)
        box.setRange(1 if integer else 0, 100000)
        if not integer:
            box.setSpecialValueText("Not specified")
        box.setValue(value)
        layout.addWidget(box)
        boxes.append(box)
    return host, boxes


class ImageScaleDialog(QDialog):
    def __init__(self, calibration, manual=None, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowTitle("Image physical scale")
        layout = QVBoxLayout(self)
        message = QLabel("Image MPP tells how many micrometres one pixel covers. Use a recorded value, enter a known value, or leave it unknown. This does not change the image pixels.")
        message.setWordWrap(True)
        layout.addWidget(message)
        values = calibration.mpp if calibration is not None else None
        description = (f"File MPP: {values[0]:g} x {values[1]:g} um/px ({calibration.source})"
                       if values else "File MPP: not available. This file does not record a usable physical pixel size.")
        self.file_status = QLabel(description, self)
        self.file_status.setTextFormat(Qt.PlainText)
        self.file_status.setWordWrap(True)
        layout.addWidget(self.file_status)
        self.auto = QRadioButton("Use MPP from file", self)
        self.auto.setEnabled(values is not None)
        self.auto.setToolTip("Use the calibration shown above. This option is unavailable if no reliable file MPP was found.")
        self.manual = QRadioButton("Enter known MPP", self)
        self.manual.setToolTip("Use acquisition or export information for this exact image; do not guess a value.")
        self.unknown = QRadioButton("MPP unknown — keep pixel settings", self)
        self.unknown.setVisible(values is None)
        layout.addWidget(self.auto)
        layout.addWidget(self.manual)
        self.manual_row, self.mpp_boxes = numeric_pair(self, manual or (0, 0))
        for axis, box in zip(("horizontal X", "vertical Y"), self.mpp_boxes):
            box.setProperty("imageScaleInput", True)
            box.setSpecialValueText("Enter known MPP")
            box.setSingleStep(.001)
            box.setToolTip(f"Known micrometres per pixel along the {axis} axis. Select all text and type the number.")
        form = QFormLayout()
        form.addRow("MPP X / Y (um per pixel)", self.manual_row)
        layout.addLayout(form)
        self.same_axes = QCheckBox("Same MPP on X and Y (copy X to Y)", self)
        self.same_axes.setToolTip("When selected, Y follows X and cannot be edited independently. Uncheck only for documented unequal axis values.")
        self.same_axes.setChecked(manual is None or manual[0] == manual[1])
        layout.addWidget(self.same_axes)
        layout.addWidget(self.unknown)
        self.validation_label = QLabel(self)
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)
        note = QLabel("MPP records the image scale. Matching also needs a known model tissue field; MPP entry alone cannot enable it.", self)
        note.setWordWrap(True)
        layout.addWidget(note)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Ok).setText("Apply to this image")
        self.buttons.button(QDialogButtonBox.Ok).setToolTip("Apply this calibration selection to the current input; do not rewrite the image file.")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.helpRequested.connect(lambda: show_input_help(self, "image"))
        layout.addWidget(self.buttons)
        self.mpp_boxes[0].valueChanged.connect(self._sync_controls)
        self.mpp_boxes[1].valueChanged.connect(self._sync_controls)
        self.same_axes.toggled.connect(self._sync_controls)
        for button in (self.auto, self.manual, self.unknown):
            button.toggled.connect(self._sync_controls)
        (self.manual if manual is not None else self.auto if values else self.unknown).setChecked(True)
        self._sync_controls()
        available = self.screen().availableGeometry()
        self.resize(min(570, max(320, available.width() - 40)), min(self.sizeHint().height(), available.height() - 60))

    def _sync_controls(self, *unused):
        manual, linked = self.manual.isChecked(), self.same_axes.isChecked()
        self.manual_row.setEnabled(manual)
        self.same_axes.setEnabled(manual)
        self.mpp_boxes[1].setEnabled(manual and not linked)
        if linked and self.mpp_boxes[1].value() != self.mpp_boxes[0].value():
            self.mpp_boxes[1].setValue(self.mpp_boxes[0].value())
        valid = not manual or min(box.value() for box in self.mpp_boxes) > 0
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(valid)
        self.validation_label.setText("Enter a positive known MPP, or choose MPP unknown." if not valid else "")
        self.validation_label.setVisible(not valid)

    def values(self):
        if not self.manual.isChecked():
            return None
        first, second = (box.value() for box in self.mpp_boxes)
        return [first, first if self.same_axes.isChecked() else second]

    def accept(self):
        if self.manual.isChecked() and min(self.values()) <= 0:
            QMessageBox.warning(self, "MPP required", "Enter positive, known values for both image axes.")
            return
        super().accept()


class ModelInputDialog(QDialog):
    """Edit a profile for a validated model without changing its weights."""

    def __init__(self, path, loaded, validation, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.path, self.loaded, self.validation = Path(path), loaded, validation
        self.saved = False
        self.setWindowTitle("Model input configuration")
        outer = QVBoxLayout(self)
        intro = QLabel("These settings describe what the model expects. Use its training or inference instructions. The current image's MPP belongs in Image scale, not here. Saving writes a settings file without changing model weights.")
        intro.setWordWrap(True)
        outer.addWidget(intro)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget(scroll)
        form = QFormLayout(content)
        self.model_form = form
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        self.labels = QPlainTextEdit(content)
        self.labels.setMaximumHeight(110)
        form.addRow("Class labels (one per line, output order)", self.labels)
        host, self.input_size = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Network input width / height (px)", host)
        self.normalization = ExplicitComboBox(content)
        self.normalization.addItems(["raw255", "imagenet", "custom", "embedded"])
        self.normalization.setToolTip("raw255 keeps 0–255 values. imagenet divides by 255 and uses ImageNet mean/std. custom uses the declared multiplier, mean and std. embedded passes raw float32 pixels to a model that handles normalization itself.")
        form.addRow("Normalization", self.normalization)
        self.mean, self.std = QLineEdit(content), QLineEdit(content)
        self.mean.setPlaceholderText("e.g. 0.485, 0.456, 0.406")
        self.std.setPlaceholderText("e.g. 0.229, 0.224, 0.225")
        self.input_scale = ExplicitDoubleSpinBox(content)
        self.input_scale.setDecimals(12)
        self.input_scale.setRange(.000000000001, 100000)
        self.input_scale.setValue(1)
        form.addRow("Custom input multiplier", self.input_scale)
        form.addRow("Custom mean (R, G, B)", self.mean)
        form.addRow("Custom std (R, G, B)", self.std)
        self.normalization.currentTextChanged.connect(self._normalization_changed)
        self.decoder, self.resize_method, self.scope, self.output_kind, self.edge, self.pixel_edge = [ExplicitComboBox(content) for _ in range(6)]
        for box, items, title in (
            (self.decoder, ["pillow_rgb", "opencv_color"], "Image decoder"),
            (self.resize_method, ["pillow_bilinear", "opencv_linear"], "Resize method"),
            (self.scope, ["image", "patch"], "Model analysis unit"),
            (self.output_kind, ["logits", "probabilities"], "Model output"),
            (self.edge, ["skip", "reflect"], "Physical-mode classification edges"),
            (self.pixel_edge, ["crop_then_resize", "skip", "reflect"], "Pixel-mode classification edges"),
        ):
            box.addItems(items)
            form.addRow(title, box)
        host, self.field = numeric_pair(content)
        form.addRow("Expected tissue field width / height (um)", host)
        for box in self.field:
            box.setToolTip("Physical width/height of one model patch in micrometres. Leave unspecified if undocumented. This is not the source image MPP.")
        host, self.tile = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Reference source tile width / height (px)", host)
        host, self.stride = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Reference stride X / Y (px)", host)
        self.note = QLineEdit(content)
        form.addRow("Specification/source note", self.note)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        import_button = QPushButton("Import settings file (JSON)…", self)
        self.import_button = import_button
        import_button.setToolTip("Read an existing input configuration for these exact model weights; it does not import new weights.")
        import_button.clicked.connect(self._import)
        outer.addWidget(import_button)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Save).setText("Save model settings")
        self.buttons.button(QDialogButtonBox.Save).setToolTip("Validate and save this model's companion input settings file. Model weights are not changed.")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.helpRequested.connect(lambda: show_input_help(self, "model"))
        outer.addWidget(self.buttons)
        self.current_profile = loaded.input_profile
        if self.current_profile:
            self._populate(self.current_profile)
        else:
            self.labels.setPlainText("\n".join(loaded.classes or [f"Class {i}" for i in range(validation.num_classes)]))
            self.normalization.setCurrentText(loaded.preprocess_profile or "imagenet")
            self._normalization_changed()
        read_only = bool(self.current_profile and self.current_profile.source in ("verified_crc_checkpoint", "upernet_reference_code"))
        if read_only:
            summary = QWidget(scroll)
            summary_form = QFormLayout(summary)
            summary_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
            profile = self.current_profile
            items = [("Model", self.path.name), ("Task", profile.task_type),
                     ("Network input", f"{profile.input_size[0]} x {profile.input_size[1]} px, RGB float32"),
                     ("Normalization", profile.normalization), ("Image reader", profile.image_decoder),
                     ("Resize method", profile.resize_backend),
                     ("Tissue field", f"{profile.field_um[0]:g} x {profile.field_um[1]:g} um" if profile.field_um else "Not established; pixel mode"),
                     ("Class order", ", ".join(profile.classes)), ("Specification", profile.note)]
            if profile.adapter == "upernet_reference":
                items.insert(6, ("Processing regions", "1000 x 1000 px, stride 512; reflect small images"))
            for title, value in items:
                label = QLabel(value, summary)
                label.setTextFormat(Qt.PlainText)
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                summary_form.addRow(title, label)
            scroll.setWidget(summary)
            import_button.hide()
            self.buttons.setStandardButtons(QDialogButtonBox.Close | QDialogButtonBox.Help)
            intro.setText("Built-in model requirements — view only. You do not need to edit these settings to run an analysis. Use Image scale to describe your image; use Help to understand each item.")
            self.setWindowTitle("Built-in model input requirements")
        available = self.screen().availableGeometry()
        self.resize(min(680, max(320, available.width() - 40)), min(480 if read_only else 680, max(300, available.height() - 80)))

    def _normalization_changed(self, *unused):
        custom = self.normalization.currentText() == "custom"
        for box in (self.mean, self.std, self.input_scale):
            box.setEnabled(custom)
            box.setVisible(custom)
            self.model_form.labelForField(box).setVisible(custom)

    def _populate(self, profile):
        self.current_profile = profile
        self.labels.setPlainText("\n".join(profile.classes))
        for boxes, values in ((self.input_size, profile.input_size), (self.field, profile.field_um or (0, 0)),
                              (self.tile, profile.tile_size), (self.stride, profile.stride)):
            for box, value in zip(boxes, values):
                box.setValue(value)
        for box, value in ((self.normalization, profile.normalization), (self.decoder, profile.image_decoder),
                           (self.resize_method, profile.resize_backend), (self.scope, profile.input_scope),
                           (self.output_kind, profile.output_kind), (self.edge, profile.edge_policy), (self.pixel_edge, profile.pixel_edge_policy)):
            box.setCurrentText(value)
        self.mean.setText(", ".join(str(n) for n in profile.mean))
        self.std.setText(", ".join(str(n) for n in profile.std))
        self.input_scale.setValue(profile.input_scale)
        self.note.setText(profile.note)
        self._normalization_changed()

    def profile_data(self):
        if self.current_profile and self.current_profile.source in ("verified_crc_checkpoint", "upernet_reference_code"):
            return self.current_profile.to_dict()
        labels = self.labels.toPlainText().splitlines()
        field = [box.value() for box in self.field]
        custom = self.normalization.currentText() == "custom"
        previous = self.current_profile
        return {
            "schema": SCHEMA, "model_sha256": self.loaded.model_sha256,
            "task_type": self.validation.task_type, "classes": labels,
            "input_size": [box.value() for box in self.input_size],
            "normalization": self.normalization.currentText(), "image_decoder": self.decoder.currentText(),
            "resize_backend": self.resize_method.currentText(), "input_scope": self.scope.currentText(),
            "field_um": field if any(field) else None,
            "tile_size": [box.value() for box in self.tile], "stride": [box.value() for box in self.stride],
            "edge_policy": self.edge.currentText(), "pixel_edge_policy": self.pixel_edge.currentText(),
            "output_kind": self.output_kind.currentText(),
            "colors": [list(c) for c in previous.colors] if previous and len(previous.colors) == len(labels) else [list(c) for c in palette(len(labels))],
            "mean": [float(n.strip()) for n in self.mean.text().split(",")] if custom else [],
            "std": [float(n.strip()) for n in self.std.text().split(",")] if custom else [],
            "input_scale": self.input_scale.value() if custom else 1.0,
            "adapter": previous.adapter if previous else "standard", "note": self.note.text(),
        }

    def _import(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import model input profile", "", "JSON (*.json)")
        if filename:
            try:
                self._populate(read_profile(filename, self.loaded.model_sha256))
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, "Invalid model profile", str(error))

    def accept(self):
        try:
            if self.current_profile and self.current_profile.source in ("verified_crc_checkpoint", "upernet_reference_code"):
                super().accept()
                return
            if file_sha256(self.path) != self.loaded.model_sha256:
                raise ValueError("The model weights changed while this editor was open. Validate the model again before saving.")
            profile = ModelInputProfile.from_dict(self.profile_data(), expected_hash=self.loaded.model_sha256)
            validate_known_contract(profile)
            if len(profile.classes) != self.validation.num_classes:
                raise ValueError("Class labels must match the validated model output count.")
            # Validate the proposed boundary tensor before replacing an existing profile.
            from dataclasses import replace
            from core.model_loader import ModelLoader
            proposed = replace(self.loaded, input_profile=profile, classes=list(profile.classes))
            ModelLoader.validate_loaded(proposed)
            target = self.path.with_name(self.path.name + ".zypath-model.json")
            output = QSaveFile(str(target))
            if not output.open(QIODevice.WriteOnly):
                raise OSError(output.errorString())
            payload = json.dumps(profile.to_dict(), indent=2, ensure_ascii=False).encode("utf-8")
            if output.write(payload) != len(payload) or not output.commit():
                raise OSError(output.errorString())
            self.saved = True
        except Exception as error:
            QMessageBox.warning(self, "Model input configuration", str(error))
            return
        super().accept()


class ModelInputImportDialog(QDialog):
    """Explain the setup needed before a model can pass input validation."""

    def __init__(self, model_path, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowTitle("Import model input settings")
        self.model_path = Path(model_path)
        self.model_sha256 = file_sha256(self.model_path)
        self.filename = ""
        layout = QVBoxLayout(self)
        message = QLabel("This model has not passed input validation with its current settings. If you have its documented input settings JSON, import that file here. This selects settings, not a new model or image.", self)
        message.setWordWrap(True)
        layout.addWidget(message)
        model = QLabel("Model: " + self.model_path.name, self)
        model.setTextFormat(Qt.PlainText)
        model.setWordWrap(True)
        layout.addWidget(model)
        self.choose_button = QPushButton("Choose model settings file (JSON)…", self)
        self.choose_button.clicked.connect(self._choose)
        layout.addWidget(self.choose_button)
        self.file_status = QLabel("No settings file selected.", self)
        self.file_status.setTextFormat(Qt.PlainText)
        self.file_status.setWordWrap(True)
        layout.addWidget(self.file_status)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Ok).setText("Import and validate")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.helpRequested.connect(lambda: show_input_help(self, "model"))
        layout.addWidget(self.buttons)
        self.resize(540, self.sizeHint().height())

    def _choose(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choose input settings for this model", "", "JSON (*.json)")
        if not filename:
            return
        try:
            profile = read_profile(filename, self.model_sha256)
        except (OSError, ValueError) as error:
            self.filename = ""
            self.file_status.setText("Settings unavailable: " + str(error))
        else:
            self.filename = filename
            self.file_status.setText(f"{Path(filename).name}\n{profile.task_type.capitalize()}, {len(profile.classes)} classes, input {profile.input_size[0]} x {profile.input_size[1]} px. Checked against this model file.")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(bool(self.filename))

    def accept(self):
        if not self.filename:
            return
        try:
            unchanged = file_sha256(self.model_path) == self.model_sha256
        except OSError:
            unchanged = False
        if not unchanged:
            self.file_status.setText("The model file changed or is unavailable. Close this window and select the model again.")
            return
        super().accept()
