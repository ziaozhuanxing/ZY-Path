"""Guided, transactional image/model scale setup with a live sampling preview."""

from pathlib import Path
from PIL import Image

from PyQt5.QtCore import Qt, QRectF, QPointF, QEvent, QSignalBlocker
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget,
)

from ui.language import tr
from core.image_calibration import ImageCalibration, read_image_calibration
from ui.choice_check_box import ChoiceCheckBox
from ui.explicit_spin_box import square_dimensions_button
from ui.input_configuration import ImageScaleEditor, numeric_pair
from ui.input_help import configure_help_window, scale_readiness, show_input_help
from ui.input_plan import input_preview
from ui.theme import ACCENT, ERROR, DARK_COLORS, LIGHT_COLORS, style_panel_scroll


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
        self.image_size = None
        self.setFixedHeight(120)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setAccessibleName(tr("Source image region and model input preview"))

    def set_plan(self, pixmap, plan, image_size=None):
        self.source_pixmap, self.plan = QPixmap(pixmap), plan
        self.image_size = image_size
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
        painter.drawText(QRectF(12, 3, left.width(), 20), Qt.AlignLeft, tr("Source image"))
        painter.drawText(QRectF(right.x(), 3, right.width(), 20), Qt.AlignLeft, tr("Model input"))
        if self.source_pixmap.isNull():
            painter.end()
            self.setPixmap(canvas)
            return
        size = self.source_pixmap.size()
        thumbnail_size = self.source_pixmap.size()
        if self.image_size:
            from PyQt5.QtCore import QSize
            size = QSize(*self.image_size)
        plan = self.plan
        tw, th = plan.tile if plan and plan.tile else (size.width(), size.height())
        fits = tw <= size.width() and th <= size.height()
        # A partial pixel tile is cropped and resized; reflected regions are
        # padded by inference. Neither is an invalid physical field request.
        partial = bool(plan and not plan.problem and not fits and plan.edge == "crop_then_resize")
        padded = bool(plan and not plan.problem and not fits and plan.edge == "reflect")
        region_w, region_h = (min(tw, size.width()), min(th, size.height())) if partial else (tw, th)
        bound_w, bound_h = max(size.width(), region_w), max(size.height(), region_h)
        scale = min(left.width() / bound_w, left.height() / bound_h)
        shown = QRectF(left.center().x() - bound_w * scale / 2,
                       left.center().y() - bound_h * scale / 2,
                       size.width() * scale, size.height() * scale)
        self.source_rect = QRectF(shown)
        self.region_rect = QRectF(shown.x(), shown.y(), region_w * scale, region_h * scale)
        self.region_fits = fits
        painter.drawPixmap(shown, self.source_pixmap, QRectF(self.source_pixmap.rect()))
        if plan and plan.tile:
            painter.setPen(QPen(QColor(ACCENT if fits or partial or padded else ERROR), 2,
                                Qt.SolidLine if fits or partial else Qt.DashLine))
            painter.drawRect(self.region_rect)
            if plan.network:
                iw, ih = plan.network
                factor = min(right.width() / iw, right.height() / ih)
                target = QRectF(right.center().x() - iw * factor / 2,
                                right.center().y() - ih * factor / 2, iw * factor, ih * factor)
                # An outlined sample, not a predicted mask or a calibrated ruler.
                if fits or partial:
                    painter.drawPixmap(target, self.source_pixmap, QRectF(0, 0, region_w * thumbnail_size.width() / size.width(), region_h * thumbnail_size.height() / size.height()))
                    painter.drawRect(target)
                else:
                    painter.drawText(right, Qt.AlignCenter | Qt.TextWordWrap,
                                     tr("Reflected padding required") if padded else tr("Requested region exceeds image"))
                painter.setPen(QColor(colors['text']))
                painter.drawText(QRectF(right.x(), height - 24, right.width(), 20), Qt.AlignCenter, f"{iw} × {ih} px")
            painter.setPen(QColor(colors['text']))
            label = "Edge crop" if partial else "Padded region" if padded else "Region" if fits else "Requested"
            painter.drawText(QRectF(12, height - 24, left.width(), 20), Qt.AlignCenter, f"{tr(label)}: {region_w} × {region_h} px")
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
        self._pixel_tile = tuple(panel.classification_parameters()["tile_size"])
        self.setWindowTitle(tr("Image sampling"))
        self.setWindowModality(Qt.WindowModal)
        outer = QVBoxLayout(self)
        header = QHBoxLayout()
        title = _text(tr("Choose how much tissue each prediction should cover."), self)
        header.addWidget(title, 1)
        help_button = QToolButton(self)
        help_button.setText(tr("Help"))
        help_button.clicked.connect(self._help)
        header.addWidget(help_button)
        outer.addLayout(header)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        content = QWidget(self.scroll)
        body = QVBoxLayout(content)
        body.setContentsMargins(4, 4, 4, 4)

        image_group = self.image_group = QGroupBox(tr("Image scale"), content)
        image_layout = QVBoxLayout(image_group)
        self.image_name = _text(Path(self._path).name, image_group)
        self.image_name.setToolTip(self._path)
        self.image_name.hide()
        image_layout.addWidget(self.image_name)
        self._file_error = ""
        try:
            self._file_calibration = read_image_calibration(self._path, self._decoder)
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            self._file_calibration = None
            self._file_error = str(error)
        self.editor = ImageScaleEditor(self._file_calibration, panel._manual_mpp, image_group, compact=True)
        image_layout.addWidget(self.editor)
        body.addWidget(image_group)

        model_group = QGroupBox(tr("Model reference"), content)
        model_layout = QHBoxLayout(model_group)
        self.model_info = _text(parent=model_group)
        model_layout.addWidget(self.model_info, 1)
        self.model_button = QPushButton(tr("Model requirements…"), model_group)
        self.model_button.setProperty("secondary", True)
        self.model_button.clicked.connect(self._edit_model)
        model_layout.addWidget(self.model_button)
        body.addWidget(model_group)

        selector = QGroupBox(tr("Sampling method"), self)
        radio_layout = QHBoxLayout(selector)
        self.pixel_mode = QRadioButton(tr("Pixel settings"), selector)
        self.physical_mode = QRadioButton(tr("Match tissue scale"), selector)
        radio_layout.addWidget(self.pixel_mode)
        radio_layout.addWidget(self.physical_mode)
        outer.insertWidget(1, selector)
        self.mode_explanation = _text(parent=content)
        body.insertWidget(0, self.mode_explanation)
        self.calibration_summary = _text(parent=content)
        body.insertWidget(0, self.calibration_summary)
        mode_group = self.mode_group = QGroupBox(tr("Pixel settings"), content)
        mode_layout = QVBoxLayout(mode_group)
        self.tile_label = _text(tr("Pixel tile width / height (px)"), mode_group)
        mode_layout.addWidget(self.tile_label)
        self.tile_row, self.tile_boxes = numeric_pair(mode_group, self._pixel_tile, integer=True)
        mode_layout.addWidget(self.tile_row)
        self.square_button = square_dimensions_button(self.tile_row, *self.tile_boxes)
        self.tile_row.layout().addWidget(self.square_button)
        body.addWidget(mode_group)
        body.addStretch()
        self.scroll.setWidget(content)
        style_panel_scroll(self.scroll)
        outer.addWidget(self.scroll, 1)

        self.edge_options = QWidget(content)
        edge_layout = QVBoxLayout(self.edge_options)
        edge_layout.setContentsMargins(0, 0, 0, 0)
        self.edge_toggle = QToolButton(self.edge_options)
        self.edge_toggle.setCheckable(True)
        self.edge_toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.edge_toggle.setArrowType(Qt.RightArrow)
        self.edge_toggle.setText(tr("Edge handling"))
        self.edge_toggle.setToolTip(tr("Optional controls for incomplete crops at the image borders."))
        edge_layout.addWidget(self.edge_toggle, alignment=Qt.AlignLeft)
        # Keep a draft for each mode. Applying the dialog commits both drafts.
        self._border_coverage = panel._border_coverage.copy()
        self.cover_borders = ChoiceCheckBox(tr("Cover borders with full-sized regions"), self.edge_options)
        self.cover_borders.setToolTip(tr("Overlaps full crops at the edges. Each source pixel contributes to the area statistics once. The image must fit one full crop."))
        self.cover_borders.hide()
        self.cover_borders.toggled.connect(self._set_border_coverage)
        self.edge_toggle.toggled.connect(self.cover_borders.setVisible)
        self.edge_toggle.toggled.connect(lambda checked: self.edge_toggle.setArrowType(Qt.DownArrow if checked else Qt.RightArrow))
        edge_layout.addWidget(self.cover_borders)
        body.insertWidget(body.count() - 1, self.edge_options)
        self.diagram = SamplingDiagram(self)
        outer.addWidget(self.diagram)
        self.preview_label = _text(parent=self)
        self.preview_label.setObjectName("samplingPreviewSummary")
        outer.addWidget(self.preview_label)
        self.short_preview = _text(parent=self)
        outer.addWidget(self.short_preview)
        self.issues = _text(parent=self)
        self.issues.setObjectName("inputSetupIssues")
        body.insertWidget(body.count() - 1, self.issues)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        cancel_button = self.buttons.button(QDialogButtonBox.Cancel)
        cancel_button.setProperty("secondary", True)
        # QDialogButtonBox polishes its standard buttons before they are shown.
        cancel_button.style().unpolish(cancel_button)
        cancel_button.style().polish(cancel_button)
        self.apply_button = self.buttons.button(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        outer.addWidget(self.buttons)
        profile = panel._active_input_profile
        known_field = profile and profile.input_scope == "patch" and profile.field_um is not None
        (self.physical_mode if known_field and (panel.match_scale_checkbox.isChecked() or prefer_matching) else self.pixel_mode).setChecked(True)
        self.editor.changed.connect(self.refresh)
        self.editor.unknown.clicked.connect(lambda: self.pixel_mode.setChecked(True))
        for box in self.tile_boxes:
            box.valueChanged.connect(self.refresh)
        self.pixel_mode.toggled.connect(self.refresh)
        self.physical_mode.toggled.connect(self._matching_requested)
        self.physical_mode.toggled.connect(self.refresh)
        panel.input_profile_changed.connect(self.refresh)
        self.refresh()
        self._matching_requested(self.physical_mode.isChecked())
        available = self.screen().availableGeometry()
        self.setMinimumSize(320, 300)
        self.resize(min(720, available.width() - 40), min(610, available.height() - 70))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep form controls usable on a short screen. The live numerical
        # preview remains pinned even when there is no room for the diagram.
        self.diagram.setVisible(self.height() >= 560)
        self.preview_label.setVisible(self.height() >= 520)
        self.short_preview.setVisible(self.height() < 520)

    def _help(self):
        show_input_help(self, "scale", readiness=scale_readiness(self.panel._active_input_profile,
                        self._calibration(), has_image=bool(self._path), calibration_error=self._file_error))

    def _edit_model(self):
        self.panel.model_input_requested.emit()
        self.refresh()

    def _matching_requested(self, checked):
        if checked and not self._calibration().mpp:
            self.editor.manual.setChecked(True)
            self.editor.mpp_boxes[0].setFocus()
            self.editor.mpp_boxes[0].selectAll()

    def _calibration(self):
        values = self.editor.values()
        size = self.panel.source_image_size()
        if values and self.editor.is_valid():
            return ImageCalibration(tuple(values), "manual entry", size)
        return self._file_calibration or ImageCalibration(None, "not recorded", size)

    def _set_border_coverage(self, checked):
        self._border_coverage[self.physical_mode.isChecked()] = checked
        self.refresh()

    def refresh(self, *unused):
        profile = self.panel._active_input_profile
        classification = self.panel.classification_radio.isChecked()
        known_field = bool(profile and profile.input_scope == "patch" and profile.field_um)
        self.physical_mode.setEnabled(known_field)
        if not known_field and self.physical_mode.isChecked():
            self.pixel_mode.setChecked(True)
        matched = self.physical_mode.isChecked()
        if profile:
            field = (tr("{width:g} × {height:g} µm per region").format(width=profile.field_um[0], height=profile.field_um[1])
                     if profile.field_um else tr("Physical tissue field: not documented"))
            normalization = {"raw255": "pixel values 0–255", "imagenet": "ImageNet normalization",
                             "embedded": "normalization inside the model", "custom": "documented custom normalization"}[profile.normalization]
            self.model_info.setText(f"{field}\n{tr('Model input')}: {profile.input_size[0]} × {profile.input_size[1]} px")
            self.model_info.setToolTip(normalization)
        else:
            self.model_info.setText(tr("No validated model input profile. You can keep pixel settings or configure the model requirements."))
        self.model_button.setVisible(not known_field and (profile is None or profile.input_scope == "patch"))
        calibration = self._calibration()
        current_mode = self.panel.classification_mode()
        self.planned_mode = current_mode
        if matched and classification and calibration.mpp and known_field:
            from core.spatial_sampling import source_tile_size
            try:
                if calibration.image_size != source_tile_size(profile, calibration):
                    self.planned_mode = "tiled_analysis"
            except ValueError:
                pass  # The preview below explains invalid geometry.
        tiled = classification and self.planned_mode == "tiled_analysis"
        self.edge_available = tiled and bool(profile and profile.input_scope == "patch")
        self.edge_options.setVisible(self.edge_available)
        cover = self.edge_available and self._border_coverage[matched]
        blocker = QSignalBlocker(self.cover_borders)
        self.cover_borders.setChecked(cover)
        del blocker
        self.image_group.setVisible(matched)
        self.mode_group.setVisible(tiled and not matched)
        self.calibration_summary.setVisible(not matched)
        if calibration.mpp:
            self.calibration_summary.setText(tr("Image MPP: {width:g} × {height:g} µm/px. Tissue matching is off; this MPP is retained.")
                .format(width=calibration.mpp[0], height=calibration.mpp[1]))
        else:
            self.calibration_summary.setText(tr("Image MPP is unknown. Pixel sizes can be used without it."))
        if matched:
            explanation = "Enter this image's measured MPP. Source pixels = model tissue field / MPP."
        elif classification and not tiled:
            explanation = "Single image resizes the whole image. Choose Tiled analysis under Task to set crop sizes."
        elif tiled:
            explanation = "Set the crop size for this image. Defaults for new images are in Settings → Preferences."
        else:
            explanation = "Pixel sampling uses the dimensions documented by the segmentation model."
        self.mode_explanation.setText(tr(explanation))
        self.preview = input_preview(profile, calibration, calibration.image_size,
            task="classification" if classification else "segmentation", classification_mode=self.planned_mode,
            matched=matched, pixel_tile=tuple(box.value() for box in self.tile_boxes), calibration_error=self._file_error, cover_borders=cover)
        preview = self.preview
        self.edge_toggle.setText(tr({
            "cover": "Edge handling · Full-sized crops",
            "crop_then_resize": "Edge handling · Resize partial crops",
            "skip": "Edge handling · Skip incomplete crops",
            "reflect": "Edge handling · Reflective padding",
        }.get(preview.edge, "Edge handling · Model default")))
        self.diagram.set_plan(self.panel._source_pixmap, preview, self.panel.source_image_size())
        if preview.tile and preview.network:
            text = tr("{source} source px → {target} model px").format(
                source=" × ".join(map(str, preview.tile)), target=" × ".join(map(str, preview.network)))
            if preview.grid:
                text += "   ·   " + tr("{count:,} region(s), {columns} columns × {rows} rows").format(
                    count=preview.count, columns=preview.grid[0], rows=preview.grid[1])
            if preview.stride:
                text += "\n" + tr("Stride: {width} × {height} px").format(width=preview.stride[0], height=preview.stride[1])
            if calibration.mpp:
                field = tuple(n * m for n, m in zip(preview.tile, calibration.mpp))
                text += "\n" + tr("Tissue per region: {width:g} × {height:g} µm").format(width=field[0], height=field[1])
        else:
            text = tr("Enter image scale information to preview matching.") if matched else tr("Pixel mode · physical scale is not matched.")
        self.preview_label.setText(text)
        self.preview_label.setToolTip(text)
        if preview.count is not None and preview.tile:
            short = tr("{count:,} region(s) · {width} × {height} source px").format(
                count=preview.count, width=preview.tile[0], height=preview.tile[1])
        else:
            short = tr("Enter known MPP above to calculate matching.") if matched else tr("Pixel sampling")
        self.short_preview.setText(short)
        self.short_preview.setToolTip(text)
        problem = preview.problem
        if matched and not self.editor.is_valid():
            problem = tr("Enter a positive known MPP above, or choose MPP unknown and pixel mode.")
        if (self.panel._image_path != self._path or self.panel._image_decoder() != self._decoder
                or self.panel._image_identity != self._image_identity):
            problem = tr("The image or its reader changed. Close and reopen this setup to review the current image axes.")
        self._problem = problem
        try:
            stat = Path(self._path).stat()
            if (stat.st_size, stat.st_mtime_ns) != self._image_identity:
                self._problem = tr("The image changed on disk. Reopen the image before configuring its scale.")
        except OSError:
            self._problem = tr("This image is no longer available. Choose an existing image first.")
        notes = list(preview.notes)
        if classification and self.planned_mode != current_mode:
            notes.insert(0, tr("Applying this plan switches the task to Tiled analysis."))
        self.issues.setText(self._problem or "\n".join(notes))
        self.issues.setVisible(bool(self.issues.text()))
        self.apply_button.setEnabled(not self._problem)
        self.apply_button.setText(tr("Apply matching") if matched else tr("Use pixel settings"))
        # Mode changes hide entire sections. Settle their layout together so a
        # temporarily stale height cannot leave the editor squeezed to a sliver.
        self.scroll.widget().layout().activate()
        self.layout().activate()

    def choices(self):
        classification = self.panel.classification_radio.isChecked()
        tiled = classification and self.planned_mode == "tiled_analysis"
        pixel_tile = [box.value() for box in self.tile_boxes] if tiled and self.pixel_mode.isChecked() else None
        return {
            "border_coverage": self._border_coverage.copy(),
            "manual_mpp": self.editor.values() if self.editor.is_valid() else self.panel._manual_mpp,
            "match_scale": self.physical_mode.isChecked(),
            "classification_mode": self.planned_mode,
            "pixel_tile": pixel_tile,
        }

    def accept(self):
        self.refresh()
        if not self._problem:
            from core.image_source import verify_image_source
            try:
                verify_image_source(self._path, self.panel._image_snapshot)
            except (OSError, ValueError) as error:
                self._problem = str(error)
                self.issues.setText(self._problem)
                self.issues.show()
                self.apply_button.setEnabled(False)
        if not self._problem:
            super().accept()
