"""Image calibration and declarative model-input editing."""

import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QPushButton, QRadioButton, QScrollArea, QToolButton, QVBoxLayout, QWidget,
)
from PyQt5.QtCore import Qt, QSaveFile, QIODevice, QEvent, pyqtSignal

from ui.language import tr
from core.model_profile import ModelInputProfile, SCHEMA, palette, read_profile, validate_known_contract, file_sha256
from ui.choice_check_box import ChoiceCheckBox
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
    host.setLayoutDirection(Qt.LeftToRight)
    layout = QHBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    boxes = []
    for value in values:
        box = ExplicitSpinBox(host) if integer else ExplicitDoubleSpinBox(host)
        if not integer:
            box.setDecimals(6)
        box.setRange(1 if integer else 0, 100000)
        if not integer:
            box.setSpecialValueText(tr("Not specified"))
        box.setValue(value)
        layout.addWidget(box)
        boxes.append(box)
    return host, boxes


class ImageScaleEditor(QWidget):
    """Image-only calibration editor shared by the standalone and guided views."""

    changed = pyqtSignal()

    def __init__(self, calibration, manual=None, parent=None, *, compact=False):
        super().__init__(parent)
        self.compact = compact
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        message = QLabel(tr("Pixel size (MPP) is the real distance covered by one image pixel. Use the value recorded for this exact image, or leave it unknown."), self)
        message.setWordWrap(True)
        message.setVisible(not compact)
        layout.addWidget(message)
        values = calibration.mpp if calibration is not None else None
        description = (tr("File MPP: {width:g} x {height:g} um/px ({source})").format(
                           width=values[0], height=values[1], source=tr(calibration.source))
                       if values else tr("File MPP: not available. This file does not record a usable physical pixel size."))
        self.file_status = QLabel(description, self)
        self.file_status.setTextFormat(Qt.PlainText)
        self.file_status.setWordWrap(True)
        layout.addWidget(self.file_status)
        self.auto = QRadioButton(tr("Use MPP from file"), self)
        self.auto.setEnabled(values is not None)
        self.auto.setVisible(not compact or values is not None)
        self.auto.setToolTip(tr("Use the calibration shown above. This option is unavailable if no reliable file MPP was found."))
        self.manual = QRadioButton(tr("Enter known MPP"), self)
        self.manual.setToolTip(tr("Use acquisition or export information for this exact image; do not guess a value."))
        self.manual.setVisible(not compact or values is not None)
        self.unknown = QRadioButton(tr("MPP unknown — keep pixel settings"), self)
        self.unknown.setVisible(values is None)
        layout.addWidget(self.auto)
        layout.addWidget(self.manual)
        self.manual_row, self.mpp_boxes = numeric_pair(self, manual or (0, 0))
        for axis, box in zip(("horizontal X", "vertical Y"), self.mpp_boxes):
            box.setProperty("imageScaleInput", True)
            box.setSpecialValueText(tr("Enter known MPP"))
            box.setSingleStep(.001)
            box.setToolTip(f"Known micrometres per pixel along the {axis} axis. Select all text and type the number.")
        self.manual_form = QFormLayout()
        self.manual_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        self.manual_form.addRow(tr("MPP X / Y (um per pixel)"), self.manual_row)
        layout.addLayout(self.manual_form)
        self.same_axes = ChoiceCheckBox(tr("Same MPP on both axes"), self)
        self.same_axes.setToolTip(tr("When selected, Y follows X and cannot be edited independently. Uncheck only for documented unequal axis values."))
        self.same_axes.setChecked(manual is None or manual[0] == manual[1])
        layout.addWidget(self.same_axes)
        self.axes_hint = QLabel(self)
        self.axes_hint.setWordWrap(True)
        layout.addWidget(self.axes_hint)
        layout.addWidget(self.unknown)
        self.validation_label = QLabel(self)
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)
        self.mpp_boxes[0].valueChanged.connect(self._sync_controls)
        self.mpp_boxes[1].valueChanged.connect(self._sync_controls)
        self.same_axes.toggled.connect(self._sync_controls)
        for button in (self.auto, self.manual, self.unknown):
            button.toggled.connect(self._sync_controls)
        (self.manual if manual is not None else self.auto if values else self.unknown).setChecked(True)
        self._sync_controls()

    def _sync_controls(self, *unused):
        manual, linked = self.manual.isChecked(), self.same_axes.isChecked()
        self.manual_row.setEnabled(manual)
        self.manual_row.setVisible(manual)
        self.manual_form.labelForField(self.manual_row).setVisible(manual)
        self.same_axes.setEnabled(manual)
        self.same_axes.setVisible(manual)
        self.axes_hint.setVisible(manual and (not self.compact or not linked))
        self.mpp_boxes[1].setEnabled(manual and not linked)
        self.mpp_boxes[1].setVisible(not linked)
        self.axes_hint.setText(tr("One value is used for both X and Y.") if linked else tr("Left: horizontal X. Right: vertical Y."))
        if linked and self.mpp_boxes[1].value() != self.mpp_boxes[0].value():
            self.mpp_boxes[1].setValue(self.mpp_boxes[0].value())
        valid = self.is_valid()
        self.validation_label.setText(tr("Enter a positive known MPP, or choose MPP unknown.") if not valid else "")
        self.validation_label.setVisible(not valid)
        self.changed.emit()

    def is_valid(self):
        return not self.manual.isChecked() or min(box.value() for box in self.mpp_boxes) > 0

    def values(self):
        if not self.manual.isChecked():
            return None
        first, second = (box.value() for box in self.mpp_boxes)
        return [first, first if self.same_axes.isChecked() else second]


class ImageScaleDialog(QDialog):
    def __init__(self, calibration, manual=None, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowTitle(tr("Image physical scale"))
        layout = QVBoxLayout(self)
        self.editor = ImageScaleEditor(calibration, manual, self)
        layout.addWidget(self.editor)
        for name in ("file_status", "auto", "manual", "unknown", "manual_row", "mpp_boxes", "same_axes", "validation_label"):
            setattr(self, name, getattr(self.editor, name))
        note = QLabel(tr("Matching also needs a documented model tissue field. Image MPP alone does not establish that field."), self)
        note.setWordWrap(True)
        layout.addWidget(note)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Ok).setText(tr("Apply to this image"))
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.helpRequested.connect(lambda: show_input_help(self, "image"))
        layout.addWidget(self.buttons)
        self.editor.changed.connect(self._sync_controls)
        self._sync_controls()
        available = self.screen().availableGeometry()
        self.resize(min(570, max(320, available.width() - 40)), min(self.sizeHint().height(), available.height() - 60))

    def _sync_controls(self):
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(self.editor.is_valid())

    def values(self):
        return self.editor.values()

    def accept(self):
        if not self.editor.is_valid():
            QMessageBox.warning(self, tr("MPP required"), tr("Enter positive, known values for both image axes."))
            return
        super().accept()


class ModelFieldCalculator(QDialog):
    """Derive a tissue field only from user-supplied original crop calibration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowTitle(tr("Calculate model tissue field"))
        layout = QVBoxLayout(self)
        note = QLabel(tr("Use the original training crop BEFORE resizing, and the known MPP of those original pixels. The final network input size alone cannot establish a tissue field."), self)
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        host, self.crop = numeric_pair(self, integer=True)
        for box in self.crop:
            box.setMinimum(0)
            box.setSpecialValueText(tr("Original crop pixels"))
            box.setValue(0)
        form.addRow(tr("Original crop width / height (px)"), host)
        host, self.mpp = numeric_pair(self)
        for box in self.mpp:
            box.setSpecialValueText(tr("Known training MPP"))
        form.addRow(tr("Training image MPP X / Y (µm/px)"), host)
        layout.addLayout(form)
        self.same_axes = ChoiceCheckBox("Same training MPP on both axes", self)
        self.same_axes.setChecked(True)
        layout.addWidget(self.same_axes)
        self.preview = QLabel(self)
        self.preview.setWordWrap(True)
        layout.addWidget(self.preview)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.button(QDialogButtonBox.Ok).setText(tr("Use this field"))
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        for box in self.crop + self.mpp:
            box.valueChanged.connect(self.refresh)
        self.same_axes.toggled.connect(self.refresh)
        self.refresh()
        available = self.screen().availableGeometry()
        self.resize(min(580, available.width() - 40), min(self.sizeHint().height(), available.height() - 60))

    def values(self):
        return [crop.value() * mpp.value() for crop, mpp in zip(self.crop, self.mpp)]

    def refresh(self, *unused):
        linked = self.same_axes.isChecked()
        self.mpp[1].setEnabled(not linked)
        if linked and self.mpp[1].value() != self.mpp[0].value():
            self.mpp[1].setValue(self.mpp[0].value())
        values = self.values()
        self._valid = all(0 < value <= 100000 for value in values)
        text = (f"{self.crop[0].value()} × {self.crop[1].value()} px at {self.mpp[0].value():g} × {self.mpp[1].value():g} µm/px\n"
                f"Tissue field: {values[0]:g} × {values[1]:g} µm") if self._valid else "Enter both crop dimensions and a positive known MPP. Fields above 100,000 µm are not supported by this editor."
        self.preview.setText(text)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(self._valid)

    def accept(self):
        self.refresh()
        if self._valid:
            super().accept()


class ModelInputDialog(QDialog):
    """Edit a profile for a validated model without changing its weights."""

    def __init__(self, path, loaded, validation, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.path, self.loaded, self.validation = Path(path), loaded, validation
        self.saved = False
        self.setWindowTitle(tr("Model input configuration"))
        outer = QVBoxLayout(self)
        intro = QLabel(tr("These settings describe what the model expects. Use its training or inference instructions. Enter the current image's MPP in Image sampling. Saving writes a settings file next to the model."))
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
        form.addRow(tr("Class labels (one per line, output order)"), self.labels)
        host, self.input_size = numeric_pair(content, (224, 224), integer=True)
        form.addRow(tr("Network input width / height (px)"), host)
        self.normalization = ExplicitComboBox(content)
        self.normalization.addItems(["raw255", "imagenet", "custom", "embedded"])
        self.normalization.setToolTip(tr("raw255 keeps 0–255 values. imagenet divides by 255 and uses ImageNet mean/std. custom uses the declared multiplier, mean and std. embedded passes raw float32 pixels to a model that handles normalization itself."))
        form.addRow(tr("Normalization"), self.normalization)
        self.mean, self.std = QLineEdit(content), QLineEdit(content)
        self.mean.setPlaceholderText(tr("e.g. 0.485, 0.456, 0.406"))
        self.std.setPlaceholderText(tr("e.g. 0.229, 0.224, 0.225"))
        self.input_scale = ExplicitDoubleSpinBox(content)
        self.input_scale.setDecimals(12)
        self.input_scale.setRange(.000000000001, 100000)
        self.input_scale.setValue(1)
        form.addRow(tr("Custom input multiplier"), self.input_scale)
        form.addRow(tr("Custom mean (R, G, B)"), self.mean)
        form.addRow(tr("Custom std (R, G, B)"), self.std)
        self.normalization.currentTextChanged.connect(self._normalization_changed)
        self.advanced = QWidget(content)
        advanced_form = QFormLayout(self.advanced)
        advanced_form.setContentsMargins(0, 0, 0, 0)
        advanced_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
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
            (form if box is self.scope else advanced_form).addRow(tr(title), box)
        host, self.field = numeric_pair(content)
        form.addRow(tr("Expected tissue field width / height (um)"), host)
        for box in self.field:
            box.setToolTip(tr("Physical width/height of one model patch in micrometres. Leave unspecified if undocumented. This is not the source image MPP."))
        field_hint = QLabel(tr("Optional: real tissue width and height in one training patch. Leave unspecified when unknown."), content)
        field_hint.setWordWrap(True)
        form.addRow(field_hint)
        self.calculate_field_button = QPushButton(tr("Calculate from original training crop…"), content)
        self.calculate_field_button.setProperty("secondary", True)
        self.calculate_field_button.clicked.connect(self._calculate_field)
        form.addRow(self.calculate_field_button)
        host, self.tile = numeric_pair(content, (224, 224), integer=True)
        advanced_form.addRow(tr("Reference source tile width / height (px)"), host)
        host, self.stride = numeric_pair(content, (224, 224), integer=True)
        advanced_form.addRow(tr("Reference stride X / Y (px)"), host)
        self.note = QLineEdit(content)
        form.addRow(tr("Specification/source note"), self.note)
        self.advanced_toggle = QToolButton(content)
        self.advanced_toggle.setText(tr("Advanced preprocessing & tiling"))
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.advanced_toggle.setArrowType(Qt.RightArrow)
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.toggled.connect(self.advanced.setVisible)
        self.advanced_toggle.toggled.connect(lambda checked: self.advanced_toggle.setArrowType(Qt.DownArrow if checked else Qt.RightArrow))
        form.addRow(self.advanced_toggle)
        form.addRow(self.advanced)
        self.advanced.hide()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        import_button = QPushButton(tr("Import settings file (JSON)…"), self)
        self.import_button = import_button
        import_button.setToolTip(tr("Read an existing input configuration for these exact model weights; it does not import new weights."))
        import_button.clicked.connect(self._import)
        outer.addWidget(import_button)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Save).setText(tr("Save model settings"))
        self.buttons.button(QDialogButtonBox.Save).setToolTip(tr("Validate and save this model's companion input settings file. Model weights are not changed."))
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
            items = [("Model", self.path.name), ("Task", tr(profile.task_type.capitalize())),
                     ("Network input", f"{profile.input_size[0]} x {profile.input_size[1]} px, RGB float32"),
                     ("Normalization", profile.normalization), ("Image reader", profile.image_decoder),
                     ("Resize method", profile.resize_backend),
                     ("Tissue field", f"{profile.field_um[0]:g} x {profile.field_um[1]:g} um" if profile.field_um else tr("Not established; pixel mode")),
                     ("Class order", ", ".join(profile.classes)), ("Specification", tr(profile.note))]
            if profile.adapter == "upernet_reference":
                items.insert(6, ("Processing regions", tr("1000 x 1000 px, stride 512; reflect small images")))
            for title, value in items:
                label = QLabel(value, summary)
                label.setTextFormat(Qt.PlainText)
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                summary_form.addRow(tr(title), label)
            scroll.setWidget(summary)
            import_button.hide()
            self.buttons.setStandardButtons(QDialogButtonBox.Close | QDialogButtonBox.Help)
            intro.setText(tr("Built-in model requirements — view only. You do not need to edit these settings to run an analysis. Use Image scale to describe your image; use Help to understand each item."))
            self.setWindowTitle(tr("Built-in model input requirements"))
        available = self.screen().availableGeometry()
        self.resize(min(680, max(320, available.width() - 40)), min(480 if read_only else 680, max(300, available.height() - 80)))

    def _calculate_field(self):
        dialog = ModelFieldCalculator(self)
        if dialog.exec_():
            for box, value in zip(self.field, dialog.values()):
                box.setValue(value)
            if not self.note.text():
                self.note.setText(f"Field calculated from user-entered original training crop {dialog.crop[0].value()} x {dialog.crop[1].value()} px at {dialog.mpp[0].value():g} x {dialog.mpp[1].value():g} um/px.")

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
        filename, _ = QFileDialog.getOpenFileName(self, tr("Import model input profile"), "", "JSON (*.json)")
        if filename:
            try:
                self._populate(read_profile(filename, self.loaded.model_sha256))
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, tr("Invalid model profile"), str(error))

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
            QMessageBox.warning(self, tr("Model input configuration"), str(error))
            return
        super().accept()


class ModelInputImportDialog(QDialog):
    """Explain the setup needed before a model can pass input validation."""

    def __init__(self, model_path, parent=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowTitle(tr("Import model input settings"))
        self.model_path = Path(model_path)
        self.model_sha256 = file_sha256(self.model_path)
        self.filename = ""
        layout = QVBoxLayout(self)
        message = QLabel(tr("This model has not passed input validation with its current settings. If you have its documented input settings JSON, import that file here. This selects settings, not a new model or image."), self)
        message.setWordWrap(True)
        layout.addWidget(message)
        model = QLabel(tr("Model: ") + self.model_path.name, self)
        model.setTextFormat(Qt.PlainText)
        model.setWordWrap(True)
        layout.addWidget(model)
        self.choose_button = QPushButton(tr("Choose model settings file (JSON)…"), self)
        self.choose_button.clicked.connect(self._choose)
        layout.addWidget(self.choose_button)
        self.file_status = QLabel(tr("No settings file selected."), self)
        self.file_status.setTextFormat(Qt.PlainText)
        self.file_status.setWordWrap(True)
        layout.addWidget(self.file_status)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self)
        self.buttons.button(QDialogButtonBox.Ok).setText(tr("Import and validate"))
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.helpRequested.connect(lambda: show_input_help(self, "model"))
        layout.addWidget(self.buttons)
        self.resize(540, self.sizeHint().height())

    def _choose(self):
        filename, _ = QFileDialog.getOpenFileName(self, tr("Choose input settings for this model"), "", "JSON (*.json)")
        if not filename:
            return
        try:
            profile = read_profile(filename, self.model_sha256)
        except (OSError, ValueError) as error:
            self.filename = ""
            self.file_status.setText(tr("Settings unavailable: ") + str(error))
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
            self.file_status.setText(tr("The model file changed or is unavailable. Close this window and select the model again."))
            return
        super().accept()
