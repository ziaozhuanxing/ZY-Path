"""Guided, transactional image/model scale setup with a live sampling preview."""

from pathlib import Path
from PIL import Image

from PyQt5.QtCore import Qt, QRectF, QPointF, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget,
)

from core.image_calibration import ImageCalibration, read_image_calibration
from ui.explicit_combo_box import ExplicitComboBox
from ui.input_configuration import ImageScaleEditor, numeric_pair
from ui.input_help import configure_help_window, scale_readiness, show_input_help
from ui.input_plan import input_preview
from ui.theme import ACCENT, DARK_COLORS, LIGHT_COLORS, style_panel_scroll


def _text(value="", parent=None):
    label = QLabel(value, parent)
    label.setTextFormat(Qt.PlainText)
    label.setWordWrap(True)
    label.setMinimumWidth(0)
    label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    return label


class SamplingDiagram(QLabel):
    """Draw one source region without allocating a crop on every keystroke."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_pixmap = QPixmap()
        self.plan = None
        self.setFixedHeight(145)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setAccessibleName("Source image region and model input preview")

    def set_plan(self, pixmap, plan):
        self.source_pixmap, self.plan = QPixmap(pixmap), plan
        self._redraw()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._redraw()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.StyleChange, QEvent.PaletteChange) and hasattr(self, "source_pixmap"):
            self._redraw()

    def _redraw(self):
        # Render to an owned image while updating the plan. QLabel performs
        # native painting, including queued repaints during modal close/teardown.
        ratio = self.devicePixelRatioF()
        canvas = QPixmap(round(self.width() * ratio), round(self.height() * ratio))
        canvas.setDevicePixelRatio(ratio)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = DARK_COLORS if QApplication.instance().property("zyTheme") == "Dark" else LIGHT_COLORS
        painter.fillRect(self.rect(), QColor(colors['soft']))
        painter.setPen(QColor(colors['text']))
        width, height = self.width(), self.height()
        left = QRectF(12, 25, max(50, width * .55 - 18), height - 52)
        right = QRectF(width * .67, 25, max(40, width * .33 - 12), height - 52)
        painter.drawText(QRectF(12, 3, left.width(), 20), Qt.AlignLeft, "Source image")
        painter.drawText(QRectF(right.x(), 3, right.width(), 20), Qt.AlignLeft, "Model input")
        if self.source_pixmap.isNull():
            painter.end()
            self.setPixmap(canvas)
            return
        size = self.source_pixmap.size()
        scale = min(left.width() / size.width(), left.height() / size.height())
        shown = QRectF(left.center().x() - size.width() * scale / 2,
                       left.center().y() - size.height() * scale / 2,
                       size.width() * scale, size.height() * scale)
        painter.drawPixmap(shown, self.source_pixmap, QRectF(self.source_pixmap.rect()))
        plan = self.plan
        if plan and plan.tile:
            tw, th = plan.tile
            region = QRectF(shown.x(), shown.y(), min(tw, size.width()) * scale, min(th, size.height()) * scale)
            painter.setPen(QPen(QColor(ACCENT), 2))
            painter.drawRect(region)
            if plan.network:
                iw, ih = plan.network
                factor = min(right.width() / iw, right.height() / ih)
                target = QRectF(right.center().x() - iw * factor / 2,
                                right.center().y() - ih * factor / 2, iw * factor, ih * factor)
                # An outlined sample, not a predicted mask or a calibrated ruler.
                painter.drawPixmap(target, self.source_pixmap, QRectF(0, 0, min(tw, size.width()), min(th, size.height())))
                painter.drawRect(target)
                painter.setPen(QColor(colors['text']))
                painter.drawText(QRectF(right.x(), height - 24, right.width(), 20), Qt.AlignCenter, f"{iw} × {ih} px")
            painter.setPen(QColor(colors['text']))
            painter.drawText(QRectF(12, height - 24, left.width(), 20), Qt.AlignCenter, f"Region: {tw} × {th} px")
        x1, x2, y = left.right() + 6, right.left() - 10, left.center().y()
        if x2 > x1:
            painter.setPen(QPen(QColor(ACCENT), 2))
            painter.drawLine(QPointF(x1, y), QPointF(x2, y))
            painter.drawLine(QPointF(x2 - 6, y - 4), QPointF(x2, y))
            painter.drawLine(QPointF(x2 - 6, y + 4), QPointF(x2, y))
        painter.end()
        self.setPixmap(canvas)


class InputSetupDialog(QDialog):
    """Stage all per-image choices; Apply commits them together, Cancel discards them."""

    def __init__(self, panel, *, prefer_matching=False):
        super().__init__(panel)
        configure_help_window(self)
        self.panel = panel
        self._path = panel._image_path
        self._decoder = panel._image_decoder()
        self._image_identity = panel._image_identity
        self._pixel_tile = tuple(panel._classification_parameters.get("tile_size", (224, 224)))
        self.setWindowTitle("Input & scale setup")
        self.setWindowModality(Qt.WindowModal)
        outer = QVBoxLayout(self)
        header = QHBoxLayout()
        title = _text("Match the amount of tissue seen by the model. Preview updates as you change the settings.", self)
        header.addWidget(title, 1)
        help_button = QToolButton(self)
        help_button.setText("Help")
        help_button.clicked.connect(self._help)
        header.addWidget(help_button)
        outer.addLayout(header)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        content = QWidget(self.scroll)
        body = QVBoxLayout(content)
        body.setContentsMargins(4, 4, 4, 4)

        image_group = QGroupBox("1 · This image's pixel size", content)
        image_layout = QVBoxLayout(image_group)
        self.image_name = _text(Path(self._path).name, image_group)
        image_layout.addWidget(self.image_name)
        self._file_error = ""
        try:
            self._file_calibration = read_image_calibration(self._path, self._decoder)
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            self._file_calibration = None
            self._file_error = str(error)
        self.editor = ImageScaleEditor(self._file_calibration, panel._manual_mpp, image_group)
        image_layout.addWidget(self.editor)
        body.addWidget(image_group)

        model_group = QGroupBox("2 · What the model expects", content)
        model_layout = QVBoxLayout(model_group)
        self.model_info = _text(parent=model_group)
        model_layout.addWidget(self.model_info)
        self.model_button = QPushButton("Model requirements…", model_group)
        self.model_button.setProperty("secondary", True)
        self.model_button.clicked.connect(self._edit_model)
        model_layout.addWidget(self.model_button)
        body.addWidget(model_group)

        selector = QGroupBox("Sampling method", self)
        radio_layout = QHBoxLayout(selector)
        self.pixel_mode = QRadioButton("Pixel settings", selector)
        self.physical_mode = QRadioButton("Match tissue scale", selector)
        for button in (self.pixel_mode, self.physical_mode):
            button.setProperty("inputChoice", True)
            button.setProperty("samplingChoice", True)
        radio_layout.addWidget(self.pixel_mode)
        radio_layout.addWidget(self.physical_mode)
        outer.insertWidget(1, selector)
        mode_group = QGroupBox("3 · Analysis mode & pixel tiles", content)
        mode_layout = QVBoxLayout(mode_group)
        self.match_hint = _text(parent=mode_group)
        mode_layout.addWidget(self.match_hint)
        self.analysis_mode = ExplicitComboBox(mode_group)
        self.analysis_mode.addItem("Single image", "single_image")
        self.analysis_mode.addItem("Tiled analysis", "tiled_analysis")
        self.analysis_mode.setCurrentIndex(max(0, self.analysis_mode.findData(panel.classification_mode())))
        self.analysis_mode.setAccessibleName("Classification analysis mode for this setup")
        mode_layout.addWidget(self.analysis_mode)
        self.tile_label = _text("Pixel tile width / height (px)", mode_group)
        mode_layout.addWidget(self.tile_label)
        self.tile_row, self.tile_boxes = numeric_pair(mode_group, self._pixel_tile, integer=True)
        mode_layout.addWidget(self.tile_row)
        self.tile_note = _text("Applying pixel-mode tiles also saves these dimensions in Preferences.", mode_group)
        mode_layout.addWidget(self.tile_note)
        self.use_tiles_button = QPushButton("Use tiled analysis for this image", self)
        self.use_tiles_button.clicked.connect(lambda: self.analysis_mode.setCurrentIndex(self.analysis_mode.findData("tiled_analysis")))
        body.addWidget(mode_group)
        body.addStretch()
        self.scroll.setWidget(content)
        style_panel_scroll(self.scroll)
        outer.addWidget(self.scroll, 1)

        self.diagram = SamplingDiagram(self)
        outer.addWidget(self.diagram)
        self.preview_label = _text(parent=self)
        self.preview_label.setObjectName("samplingPreviewSummary")
        outer.addWidget(self.preview_label)
        self.issues = _text(parent=self)
        self.issues.setObjectName("inputSetupIssues")
        outer.addWidget(self.issues)
        outer.addWidget(self.use_tiles_button)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.apply_button = self.buttons.button(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        outer.addWidget(self.buttons)
        profile = panel._active_input_profile
        known_field = profile and profile.input_scope == "patch" and profile.field_um is not None
        known_mpp = bool(panel._image_calibration and panel._image_calibration.mpp)
        (self.physical_mode if known_field and (panel.match_scale_checkbox.isChecked() or prefer_matching and known_mpp) else self.pixel_mode).setChecked(True)
        self.editor.changed.connect(self.refresh)
        self.editor.unknown.clicked.connect(lambda: self.pixel_mode.setChecked(True))
        for box in self.tile_boxes:
            box.valueChanged.connect(self.refresh)
        self.analysis_mode.currentIndexChanged.connect(self.refresh)
        self.pixel_mode.toggled.connect(self.refresh)
        self.physical_mode.toggled.connect(self.refresh)
        self.physical_mode.toggled.connect(self._matching_requested)
        panel.input_profile_changed.connect(self.refresh)
        self.refresh()
        available = self.screen().availableGeometry()
        self.setMinimumSize(320, 300)
        self.resize(min(740, available.width() - 40), min(730, available.height() - 70))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep form controls usable on a short screen. The live numerical
        # preview remains pinned even when there is no room for the diagram.
        self.diagram.setVisible(self.height() >= 560)

    def _help(self):
        show_input_help(self, "scale", readiness=scale_readiness(self.panel._active_input_profile,
                        self._calibration(), has_image=bool(self._path), calibration_error=self._file_error))

    def _edit_model(self):
        self.panel.model_input_requested.emit()
        self.refresh()

    def _matching_requested(self, checked):
        if checked and not self._calibration().mpp:
            self.editor.manual.setChecked(True)
            self.scroll.ensureWidgetVisible(self.editor.manual_row)
            self.editor.mpp_boxes[0].setFocus()
            self.editor.mpp_boxes[0].selectAll()

    def _calibration(self):
        values = self.editor.values()
        size = (self.panel._source_pixmap.width(), self.panel._source_pixmap.height())
        if values and self.editor.is_valid():
            return ImageCalibration(tuple(values), "manual entry", size)
        return self._file_calibration or ImageCalibration(None, "not recorded", size)

    def refresh(self, *unused):
        profile = self.panel._active_input_profile
        classification = self.panel.classification_radio.isChecked()
        known_field = bool(profile and profile.input_scope == "patch" and profile.field_um)
        self.physical_mode.setEnabled(known_field)
        if not known_field and self.physical_mode.isChecked():
            self.pixel_mode.setChecked(True)
        if profile:
            field = (f"{profile.field_um[0]:g} × {profile.field_um[1]:g} µm per region" if profile.field_um else "Physical tissue field: not documented")
            normalization = {"raw255": "pixel values 0–255", "imagenet": "ImageNet normalization",
                             "embedded": "normalization inside the model", "custom": "documented custom normalization"}[profile.normalization]
            self.model_info.setText(f"Input: {profile.input_size[0]} × {profile.input_size[1]} RGB pixels · {normalization}\n{field}")
        else:
            self.model_info.setText("No validated model input profile. You can keep pixel settings or configure the model requirements.")
        self.match_hint.setText("Uses image MPP to calculate source regions. Pixel tile preferences are not used." if known_field else
                               "Scale matching needs a documented model tissue field. Pixel settings remain available; entering an image MPP cannot establish the model field.")
        self.analysis_mode.setVisible(classification)
        pixel_tiles = classification and self.analysis_mode.currentData() == "tiled_analysis" and self.pixel_mode.isChecked()
        for widget in (self.tile_row, self.tile_label, self.tile_note):
            widget.setVisible(pixel_tiles)
        calibration = self._calibration()
        matched = self.physical_mode.isChecked()
        self.preview = input_preview(profile, calibration, calibration.image_size,
            task="classification" if classification else "segmentation", classification_mode=self.analysis_mode.currentData(),
            matched=matched, pixel_tile=tuple(box.value() for box in self.tile_boxes), calibration_error=self._file_error)
        preview = self.preview
        self.diagram.set_plan(self.panel._source_pixmap, preview)
        self.use_tiles_button.setVisible(preview.can_use_tiles)
        if preview.tile and preview.network:
            text = f"{preview.tile[0]} × {preview.tile[1]} source px → {preview.network[0]} × {preview.network[1]} model px"
            if preview.grid:
                text += f"   ·   {preview.count:,} region(s), {preview.grid[0]} columns × {preview.grid[1]} rows"
            if preview.stride:
                text += f"\nStride: {preview.stride[0]} × {preview.stride[1]} px"
            if calibration.mpp:
                field = tuple(n * m for n, m in zip(preview.tile, calibration.mpp))
                text += f"\nTissue per region: {field[0]:g} × {field[1]:g} µm"
        else:
            text = "Enter image scale information to preview matching." if matched else "Pixel mode · physical scale is not matched."
        self.preview_label.setText(text)
        problem = preview.problem
        if not self.editor.is_valid():
            problem = "Enter a positive known MPP above, or choose MPP unknown and pixel mode."
        if (self.panel._image_path != self._path or self.panel._image_decoder() != self._decoder
                or self.panel._image_identity != self._image_identity):
            problem = "The image or its reader changed. Close and reopen this setup to review the current image axes."
        self._problem = problem
        try:
            stat = Path(self._path).stat()
            if (stat.st_size, stat.st_mtime_ns) != self._image_identity:
                self._problem = "The image changed on disk. Reopen the image before configuring its scale."
        except OSError:
            self._problem = "This image is no longer available. Choose an existing image first."
        self.issues.setText(self._problem or "\n".join(preview.notes))
        self.issues.setVisible(bool(self.issues.text()))
        self.apply_button.setEnabled(not self._problem)
        self.apply_button.setText("Apply matching" if matched else "Use pixel settings")

    def choices(self):
        return {"manual_mpp": self.editor.values(), "match_scale": self.physical_mode.isChecked(),
                "classification_mode": self.analysis_mode.currentData(),
                "pixel_tile": [box.value() for box in self.tile_boxes] if self.pixel_mode.isChecked()
                and self.panel.classification_radio.isChecked() and self.analysis_mode.currentData() == "tiled_analysis" else None}

    def accept(self):
        self.refresh()
        if not self._problem:
            super().accept()
