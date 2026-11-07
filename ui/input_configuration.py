"""Image calibration and declarative model-input editing."""

import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QPushButton, QRadioButton, QScrollArea, QVBoxLayout, QWidget,
)
from PyQt5.QtCore import Qt, QSaveFile, QIODevice, QEvent

from core.model_profile import ModelInputProfile, SCHEMA, palette, read_profile, validate_known_contract, file_sha256
from ui.explicit_spin_box import ExplicitSpinBox
from ui.explicit_combo_box import forward_wheel_to_page


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
        self.setWindowTitle("Image physical scale")
        layout = QVBoxLayout(self)
        message = QLabel("MPP is micrometres per pixel of the image used for analysis. Enter known calibration values; image dimensions or print DPI do not establish MPP.")
        message.setWordWrap(True)
        layout.addWidget(message)
        self.auto = QRadioButton("Use image metadata", self)
        self.manual = QRadioButton("Enter known MPP for the displayed image", self)
        layout.addWidget(self.auto)
        values = calibration.mpp if calibration is not None else None
        description = (f"{values[0]:g} x {values[1]:g} um/px — {calibration.source}"
                       if values else "No reliable MPP metadata was found. Pixel mode remains available.")
        label = QLabel(description, self)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(self.manual)
        row, self.mpp_boxes = numeric_pair(self, manual or (0, 0))
        form = QFormLayout()
        form.addRow("MPP X / Y (um/px)", row)
        layout.addLayout(form)
        self.same_axes = QCheckBox("Same MPP on both axes", self)
        self.same_axes.setChecked(manual is None or manual[0] == manual[1])
        layout.addWidget(self.same_axes)
        self.mpp_boxes[0].valueChanged.connect(self._copy_axis)
        self.same_axes.toggled.connect(self._copy_axis)
        self.manual.setChecked(manual is not None)
        self.auto.setChecked(manual is None)
        self.manual.toggled.connect(row.setEnabled)
        row.setEnabled(self.manual.isChecked())
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.resize(510, self.sizeHint().height())

    def _copy_axis(self, *unused):
        if self.same_axes.isChecked():
            self.mpp_boxes[1].setValue(self.mpp_boxes[0].value())

    def values(self):
        return [box.value() for box in self.mpp_boxes] if self.manual.isChecked() else None

    def accept(self):
        if self.manual.isChecked() and min(self.values()) <= 0:
            QMessageBox.warning(self, "MPP required", "Enter positive, known values for both image axes.")
            return
        super().accept()


class ModelInputDialog(QDialog):
    """Edit a profile for a validated model without changing its weights."""

    def __init__(self, path, loaded, validation, parent=None):
        super().__init__(parent)
        self.path, self.loaded, self.validation = Path(path), loaded, validation
        self.saved = False
        self.setWindowTitle("Model input configuration")
        outer = QVBoxLayout(self)
        intro = QLabel("Use the model's training or inference specification. Unknown physical fields stay unspecified. These settings are saved beside this model and checked against its SHA-256.")
        intro.setWordWrap(True)
        outer.addWidget(intro)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget(scroll)
        form = QFormLayout(content)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        self.labels = QPlainTextEdit(content)
        self.labels.setMaximumHeight(110)
        form.addRow("Class labels (one per line, output order)", self.labels)
        host, self.input_size = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Network input width / height (px)", host)
        self.normalization = QComboBox(content)
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
        self.decoder, self.resize_method, self.scope, self.output_kind, self.edge, self.pixel_edge = [QComboBox(content) for _ in range(6)]
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
        form.addRow("Documented tissue field X / Y (um)", host)
        host, self.tile = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Reference source tile width / height (px)", host)
        host, self.stride = numeric_pair(content, (224, 224), integer=True)
        form.addRow("Reference stride X / Y (px)", host)
        self.note = QLineEdit(content)
        form.addRow("Specification/source note", self.note)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        import_button = QPushButton("Import model profile JSON…", self)
        import_button.clicked.connect(self._import)
        outer.addWidget(import_button)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        outer.addWidget(self.buttons)
        self.current_profile = loaded.input_profile
        if self.current_profile:
            self._populate(self.current_profile)
        else:
            self.labels.setPlainText("\n".join(loaded.classes or [f"Class {i}" for i in range(validation.num_classes)]))
            self.normalization.setCurrentText(loaded.preprocess_profile or "imagenet")
            self._normalization_changed()
        if self.current_profile and self.current_profile.source in ("verified_crc_checkpoint", "upernet_reference_code"):
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
            import_button.setEnabled(False)
            self.buttons.button(QDialogButtonBox.Save).setEnabled(False)
            intro.setText("This built-in profile follows its supplied reference code. Physical scale matching is available only when its tissue field is established. Its weights are unchanged.")
        available = self.screen().availableGeometry()
        self.resize(min(680, max(320, available.width() - 40)), min(680, max(300, available.height() - 80)))

    def _normalization_changed(self, *unused):
        custom = self.normalization.currentText() == "custom"
        for box in (self.mean, self.std, self.input_scale):
            box.setEnabled(custom)

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
