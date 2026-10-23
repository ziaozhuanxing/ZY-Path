"""Application settings dialog."""

from PyQt5.QtCore import QSettings, QSize, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QGroupBox,
    QGridLayout,
    QPlainTextEdit,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QSpinBox,
    QScrollArea,
    QSizePolicy,
    QLayout,
    QComboBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ui.explicit_combo_box import ExplicitComboBox
from ui.explicit_spin_box import ExplicitSpinBox
from ui.model_settings import ModelSettingsPage
from ui.guide_view import GuideView
from ui.system_information import system_information
from utils.version import APP_VERSION
from ui.theme import apply_theme, style_panel_scroll
from core.classification_tiles import CLASSIFICATION_LABELS, CLASSIFICATION_COLORS
from core.large_image_segmentation import SEGMENTATION_LABELS, SEGMENTATION_COLORS
from utils.paths import resource_path


class SettingsPage(QWidget):
    def minimumSizeHint(self):
        # Wrapped text must be measured at the viewport width, rather than at
        # its theoretical minimum width. QScrollArea handles height-for-width.
        return QSize(0, 0)


class SettingsDialog(QDialog):
    """Provide one reusable dialog for application settings and help pages."""

    _PAGE_NAMES = ("Appearance", "Preferences", "Models", "Guide & Support", "System Information", "About")
    _THEME_KEY = "appearance/theme"
    _PNG_REMINDER_KEY = "export/pngReminderEnabled"
    _PDF_REMINDER_KEY = "export/pdfReminderEnabled"
    theme_changed = pyqtSignal(str)
    classification_mode_changed = pyqtSignal(str)
    reset_export_reminders_requested = pyqtSignal()
    reset_panel_layout_requested = pyqtSignal()

    def __init__(
        self,
        settings: QSettings,
        parent: QWidget | None = None,
        app_version: str | None = None,
        builtin_paths: dict | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags((self.windowFlags() | Qt.WindowMinMaxButtonsHint) & ~Qt.WindowContextHelpButtonHint)
        self.setSizeGripEnabled(True)
        self.settings = settings
        self.app_version = app_version or APP_VERSION
        self._copy_feedback_timer = QTimer(self)
        self._copy_feedback_timer.setSingleShot(True)
        self._copy_feedback_timer.setInterval(2500)
        self._copy_feedback_timer.timeout.connect(self._clear_copy_feedback)
        self.setWindowTitle("Settings")
        self.setMinimumSize(620, 400)
        self.resize(860, 560)

        layout = QHBoxLayout(self)
        self.navigation = QListWidget(self)
        self.navigation.setObjectName("settingsNavigation")
        self.navigation.setFixedWidth(180)
        self.navigation.setWordWrap(True)
        self.navigation.setAccessibleName("Settings sections")
        self.pages = QStackedWidget(self)
        self.pages.setObjectName("settingsPages")
        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self._build_appearance_page()
        self._build_preferences_page()
        page = self._add_page("Models")
        models_layout = QVBoxLayout(page)
        self.models_page = ModelSettingsPage(settings, builtin_paths or {
            "classification": resource_path("models/crc_dn21_seed42_best.pth"),
            "segmentation": resource_path("models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth"),
        }, page)
        models_layout.addWidget(self.models_page)
        self._build_guide_page()
        self._build_system_page()
        self._build_about_page()
        # Settings are saved on change. Return in an editor must never invoke
        # QDialog's first/default push button (Reset Export Reminders).
        for button in self.findChildren(QPushButton):
            button.setAutoDefault(False)
            button.setDefault(False)
        for label in self.pages.findChildren(QLabel):
            if label.minimumWidth() != label.maximumWidth():
                label.setWordWrap(True)
                policy = label.sizePolicy()
                policy.setHorizontalPolicy(QSizePolicy.Ignored)
                policy.setVerticalPolicy(QSizePolicy.Preferred)
                policy.setHeightForWidth(True)
                label.setSizePolicy(policy)
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.currentRowChanged.connect(lambda row: self._refresh_system_info()
            if row == self._PAGE_NAMES.index("System Information") else None)
        self.navigation.setCurrentRow(0)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused = self.focusWidget()
            if isinstance(focused, (QPushButton, QToolButton)) and focused.isEnabled():
                focused.click()
            event.accept()
            return
        super().keyPressEvent(event)

    def _add_page(self, page_name: str) -> QWidget:
        item = QListWidgetItem(page_name)
        metrics = self.navigation.fontMetrics()
        text_rect = metrics.boundingRect(0, 0, self.navigation.width() - 24, 1000, Qt.TextWordWrap, page_name)
        item.setSizeHint(QSize(0, text_rect.height() + 12))
        self.navigation.addItem(item)
        page = SettingsPage(self.pages)
        scroll = QScrollArea(self.pages)
        scroll.setObjectName("settingsScroll" + page_name.replace(" ", ""))
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidget(page)
        style_panel_scroll(scroll)
        self.pages.addWidget(scroll)
        return page

    def _build_appearance_page(self) -> None:
        page = self._add_page("Appearance")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Appearance", page))
        layout.addWidget(QLabel("Choose the interface theme. Changes apply immediately.", page))
        self.light_radio = QRadioButton("Light", page)
        self.dark_radio = QRadioButton("Dark", page)
        layout.addWidget(self.light_radio)
        layout.addWidget(self.dark_radio)
        layout.addStretch()
        theme = self.settings.value(self._THEME_KEY, "Light", type=str)
        self.dark_radio.setChecked(theme.casefold() == "dark")
        self.light_radio.setChecked(not self.dark_radio.isChecked())
        self.light_radio.toggled.connect(self._theme_toggled)
        self.dark_radio.toggled.connect(self._theme_toggled)

    @staticmethod
    def _section(layout, title):
        group = QGroupBox(title)
        group.setMinimumWidth(0)
        group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        box = QVBoxLayout(group)
        box.setContentsMargins(12, 20, 12, 12)
        box.setSpacing(8)
        layout.addWidget(group)
        return group, box

    @staticmethod
    def _note(layout, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        layout.addWidget(label)
        return label

    def _build_preferences_page(self) -> None:
        page = self._add_page("Preferences")
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        self._note(layout, "Preferences are saved automatically. Analysis defaults affect new runs; history Re-run keeps its recorded parameters. Model defaults are in Models.")
        export_group, export_box = self._section(layout, "Export")
        self._note(export_box, "Show an explanation before exporting. PNG saves the result presentation; PDF creates a report with the available analysis metadata.")
        self.png_reminder_checkbox = QCheckBox("PNG export reminder", export_group)
        self.pdf_reminder_checkbox = QCheckBox("PDF export reminder", export_group)
        for checkbox, key in (
            (self.png_reminder_checkbox, self._PNG_REMINDER_KEY),
            (self.pdf_reminder_checkbox, self._PDF_REMINDER_KEY),
        ):
            checkbox.setChecked(self.settings.value(key, True, type=bool))
            checkbox.toggled.connect(lambda checked, setting_key=key: self._set_value(setting_key, checked))
            export_box.addWidget(checkbox)
        self.reset_reminders_button = QPushButton("Reset Export Reminders", export_group)
        self.reset_reminders_button.clicked.connect(self.reset_export_reminders_requested.emit)
        export_box.addWidget(self.reset_reminders_button)

        classification_group, classification_box = self._section(layout, "Classification")
        self._note(classification_box, "Classification mode. Changing this selection updates the main panel immediately and saves the startup default. The main panel also lets you choose a mode. Historical results keep their recorded mode.")
        self.startup_mode = ExplicitComboBox(classification_group)
        self.startup_mode.addItem("Single image", "single_image")
        self.startup_mode.addItem("Tiled analysis", "tiled_analysis")
        self.startup_mode.setCurrentIndex(max(0, self.startup_mode.findData(
            self.settings.value("classification/defaultMode", "single_image", type=str))))
        self.startup_mode.currentIndexChanged.connect(self._classification_mode_selected)
        self.startup_mode.activated[int].connect(self._confirm_classification_mode)
        classification_box.addWidget(self.startup_mode)
        self.mode_default_note = self._note(classification_box, "")
        self._refresh_mode_default_note()
        self._note(classification_box, "Original-image tile dimensions (pixels), used only in Tiled analysis. "
                   "The built-in classifier's source dataset uses 224 x 224 patches at 0.5 micrometres/pixel. "
                   "Uploaded-image resolution and physical-scale matching are not verified. "
                   "512 x 512 remains an editable starting value; training-scale matching and optimality have not been established. "
                   "Partial edge tiles contain real pixels only and are resized to the 224 x 224 network input.")
        dimensions = QGridLayout()
        dimensions.setColumnStretch(0, 1)
        dimensions.setColumnStretch(1, 1)
        for row, (name, label) in enumerate((("width", "Tile width (px)"), ("height", "Tile height (px)"))):
            dimensions.addWidget(QLabel(label, classification_group), row, 0)
            spin = ExplicitSpinBox(classification_group)
            spin.setToolTip("Type a pixel value or use the arrow keys/buttons. The mouse wheel scrolls this page.")
            spin.setRange(1, 100000)
            spin.setValue(self.settings.value(f"classificationTiles/{name}", 512, type=int))
            spin.valueChanged.connect(lambda value, key=name: self._set_value(f"classificationTiles/{key}", value))
            setattr(self, f"tile_{name}", spin)
            dimensions.addWidget(spin, row, 1)
            if name == "width":
                self.sync_tile_height_button = QToolButton(classification_group)
                self.sync_tile_height_button.setText("Square")
                self.sync_tile_height_button.setToolTip("Set tile height to the current width once. Both dimensions remain independently editable.")
                self.sync_tile_height_button.setAccessibleName("Set tile height equal to width")
                self.sync_tile_height_button.clicked.connect(lambda: self.tile_height.setValue(self.tile_width.value()))
                dimensions.addWidget(self.sync_tile_height_button, row, 2)
        classification_box.addLayout(dimensions)
        self._note(classification_box, "Classification resize method (both modes)")
        self.resize_method = ExplicitComboBox(classification_group)
        self.resize_method.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.resize_method.setMinimumWidth(0)
        self.resize_method.setToolTip("The original classifier evaluation used Albumentations 1.3.1 Resize with OpenCV 4.8.1 INTER_LINEAR. "
                                     "This option selects INTER_LINEAR in the installed OpenCV version; it does not reproduce every part of that environment.")
        self.resize_method.addItem("Pillow bilinear (legacy)", "pillow_bilinear")
        self.resize_method.addItem("OpenCV linear", "opencv_linear")
        self.resize_method.setCurrentIndex(max(0, self.resize_method.findData(
            self.settings.value("classification/resizeBackend", "pillow_bilinear", type=str))))
        self.resize_method.currentIndexChanged.connect(lambda: self._set_value("classification/resizeBackend", self.resize_method.currentData()))
        classification_box.addWidget(self.resize_method)
        self.resize_advice_button = QToolButton(classification_group)
        self.resize_advice_button.setText("Resize method guide")
        self.resize_advice_button.setToolTip("Expand recommendations for choosing Pillow bilinear or OpenCV linear.")
        self.resize_advice_button.setCheckable(True)
        self.resize_advice_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.resize_advice_button.setArrowType(Qt.RightArrow)
        classification_box.addWidget(self.resize_advice_button)
        self.resize_advice = self._note(classification_box,
            "Pillow bilinear: keep this for continuity with earlier application runs or experiments that used this backend. "
            "It remains the default.\n\n"
            "OpenCV linear (INTER_LINEAR): choose this when aligning the resize operation with the original "
            "classifier's Albumentations Resize pipeline. Matching this operation does not reproduce all training transforms "
            "or the complete evaluation environment.\n\n"
            "For comparisons, keep the same model, source image, tile dimensions and backend, and record them. "
            "The 7,180 external test patches were already 224 x 224; agreement on those patches does not prove "
            "agreement when resizing 512 x 512 crops. Neither backend is guaranteed to be more accurate. "
            "A custom model should use its own documented preprocessing. History Re-run uses the recorded backend.")
        self.resize_advice.hide()
        self.resize_advice_button.toggled.connect(self.resize_advice.setVisible)
        self.resize_advice_button.toggled.connect(lambda expanded: self.resize_advice_button.setArrowType(
            Qt.DownArrow if expanded else Qt.RightArrow))
        self._note(classification_box, "Pillow bilinear remains the default for compatibility with earlier application runs. "
                   "OpenCV linear uses INTER_LINEAR, as in the original classifier's Albumentations Resize pipeline. "
                   "Resizing can produce different pixel values and predictions; neither method is guaranteed to be more accurate. "
                   "The resize method is recorded for classification runs; tile dimensions are also recorded for Tiled analysis. "
                   "These controls do not change segmentation parameters.")
        self.reset_classification_button = QPushButton("Reset Classification", classification_group)
        self.reset_classification_button.setToolTip("Restore current/default Single image, 512 x 512 source tiles and Pillow bilinear. Keep model defaults, theme, export preferences and history.")
        self.reset_classification_button.clicked.connect(self._reset_classification_preferences)
        classification_box.addWidget(self.reset_classification_button)

        palette_group, palette_box = self._section(layout, "Classification palette")
        self._note(palette_box, "Fixed display palette v1. These are classification classes, independent of segmentation labels. "
                   "Colours aid display; they do not validate a prediction. Estimated coverage uses actual crop area, including partial edge tiles.")
        self.palette_labels = []
        for label, color in zip(CLASSIFICATION_LABELS, CLASSIFICATION_COLORS):
            row = QHBoxLayout()
            swatch = QLabel(palette_group)
            swatch.setFixedSize(20, 20)
            swatch.setStyleSheet("background-color: rgb%s; border: 1px solid #718096;" % (color,))
            text = QLabel(f"{label} - RGB {color}", palette_group)
            text.setWordWrap(True)
            self.palette_labels.append(text)
            row.addWidget(swatch)
            row.addWidget(text, 1)
            palette_box.addLayout(row)

        segmentation_group, segmentation_box = self._section(layout, "Built-in segmentation palette")
        self._note(segmentation_box, "Read-only reference for the built-in UPerNet segmentation model. "
                   "Classification and segmentation have independent class orders and colour meanings. "
                   "For custom models, use the legend in that result; this reference does not override model labels or colours.")
        self.segmentation_palette_labels = []
        self.segmentation_palette_swatches = []
        for index, (label, color) in enumerate(zip(SEGMENTATION_LABELS, SEGMENTATION_COLORS)):
            row = QHBoxLayout()
            swatch = QLabel(segmentation_group)
            swatch.setFixedSize(20, 20)
            swatch.setStyleSheet("background-color: rgb%s; border: 1px solid #718096;" % (color,))
            text = QLabel(f"{index}: {label} - RGB {color}", segmentation_group)
            text.setWordWrap(True)
            self.segmentation_palette_labels.append(text)
            self.segmentation_palette_swatches.append(swatch)
            row.addWidget(swatch)
            row.addWidget(text, 1)
            segmentation_box.addLayout(row)

        layout_group, layout_box = self._section(layout, "Results and layout")
        self._note(layout_box, "Overlay, opacity, tile boundaries, comparison and linked views are controlled beside the result image. "
                   "Spatial results start without a duplicate source preview. View choices are saved with each history record; they do not change predictions. "
                   "Reset Panel Layout restores panel proportions and fits images while preserving completed results and history.")
        self.reset_layout_button = QPushButton("Reset Panel Layout", layout_group)
        self.reset_layout_button.clicked.connect(self.reset_panel_layout_requested.emit)
        layout_box.addWidget(self.reset_layout_button)
        layout.setAlignment(Qt.AlignTop)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        for kind in (QSpinBox, QComboBox, QPushButton):
            for control in page.findChildren(kind):
                control.setMinimumHeight(control.sizeHint().height())

    def _refresh_mode_default_note(self):
        mode = self.settings.value("classification/defaultMode", "single_image", type=str)
        name = "Tiled analysis" if mode == "tiled_analysis" else "Single image"
        self.mode_default_note.setText(f"Saved startup default: {name}. Loading history does not change this default.")

    def _confirm_classification_mode(self, *unused):
        if self.settings.value("classification/defaultMode", "single_image", type=str) != self.startup_mode.currentData():
            self._classification_mode_selected()

    def _classification_mode_selected(self):
        mode = self.startup_mode.currentData()
        self._set_value("classification/defaultMode", mode)
        self._refresh_mode_default_note()
        self.classification_mode_changed.emit(mode)

    def show_classification_mode(self, mode):
        """Reflect the current main-panel mode without rewriting a history/default."""
        index = self.startup_mode.findData(mode)
        if index >= 0:
            previous = self.startup_mode.blockSignals(True)
            try:
                self.startup_mode.setCurrentIndex(index)
            finally:
                self.startup_mode.blockSignals(previous)
        self._refresh_mode_default_note()

    def set_inference_running(self, running):
        self.startup_mode.setEnabled(not running)
        self.reset_classification_button.setEnabled(not running)
        self.startup_mode.setToolTip("Wait for inference to finish before changing mode." if running
            else "Select explicitly to update the main panel and saved default. Scrolling does not change the mode.")

    def _reset_classification_preferences(self):
        for key, value in (("classification/defaultMode", "single_image"),
                           ("classificationTiles/width", 512), ("classificationTiles/height", 512),
                           ("classification/resizeBackend", "pillow_bilinear")):
            self.settings.setValue(key, value)
        self.settings.sync()
        self.startup_mode.setCurrentIndex(0)
        self.tile_width.setValue(512)
        self.tile_height.setValue(512)
        self.resize_method.setCurrentIndex(0)
        self._refresh_mode_default_note()
        self.classification_mode_changed.emit("single_image")

    def _build_guide_page(self) -> None:
        page = self._add_page("Guide & Support")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.guide_view = GuideView(page)
        layout.addWidget(self.guide_view, 1)

    def _build_system_page(self):
        page = self._add_page("System Information")
        layout = QVBoxLayout(page)
        self._note(layout, "Inspect runtime, technology versions and saved configuration below. Copy copies exactly the displayed text; nothing is sent automatically.")
        self.system_info_view = QPlainTextEdit(page)
        self.system_info_view.setObjectName("systemInformation")
        self.system_info_view.setReadOnly(True)
        self.system_info_view.setMinimumSize(0, 240)
        self.system_info_view.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        layout.addWidget(self.system_info_view, 1)
        buttons = QHBoxLayout()
        self.refresh_system_info_button = QPushButton("Refresh", page)
        self.copy_system_info_button = QPushButton("Copy System Info", page)
        self.refresh_system_info_button.clicked.connect(self._refresh_system_info)
        self.copy_system_info_button.clicked.connect(self._copy_system_info)
        buttons.addWidget(self.refresh_system_info_button)
        buttons.addWidget(self.copy_system_info_button)
        layout.addLayout(buttons)
        self.system_info_feedback = QLabel(page)
        self.system_info_feedback.setWordWrap(True)
        layout.addWidget(self.system_info_feedback)
        self._refresh_system_info()

    def _refresh_system_info(self):
        self.system_info_view.setPlainText(system_information(self.settings, self.app_version))
        self._clear_copy_feedback()

    def _clear_copy_feedback(self):
        self._copy_feedback_timer.stop()
        self.system_info_feedback.clear()

    def hideEvent(self, event):
        self._clear_copy_feedback()
        super().hideEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_system_info()

    def _build_about_page(self) -> None:
        page = self._add_page("About")
        layout = QVBoxLayout(page)
        logo_path = resource_path("assets/logo.png")
        logo = QLabel(page)
        if logo_path.is_file():
            logo.setPixmap(
                QPixmap(str(logo_path)).scaled(
                    96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        layout.addWidget(logo)
        layout.addWidget(QLabel("ZY-Path", page))
        layout.addWidget(
            QLabel(
                "Histopathology image classification, segmentation, and local history.",
                page,
            )
        )
        layout.addWidget(QLabel(f"Version: {self.app_version}", page))
        layout.addWidget(QLabel("Developer: Li Zi Yao", page))
        contact = self._note(layout, "Email: <a href='mailto:ziyao604502@gmail.com'>ziyao604502@gmail.com</a><br>"
                             "Telephone: +601123612318")
        contact.setOpenExternalLinks(True)
        self._note(layout, "A local desktop workflow for single-image classification, tiled classification, segmentation, linked comparison, history and export.")
        self._note(layout, "Built with Python, PyQt5, PyTorch, torchvision, transformers, Pillow, OpenCV, NumPy, Matplotlib, SQLite and fpdf2. See System Information for installed versions.")
        layout.addWidget(
            QLabel(
                "For education and exploratory research only.<br>Not intended for clinical diagnosis.",
                page,
            )
        )
        layout.addStretch()

    def _theme_toggled(self, checked: bool) -> None:
        if not checked:
            return
        theme = "Dark" if self.dark_radio.isChecked() else "Light"
        self.settings.setValue(self._THEME_KEY, theme)
        self.settings.sync()
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, theme)
        self.theme_changed.emit(theme)

    def _set_value(self, key: str, value) -> None:
        self.settings.setValue(key, value)
        self.settings.sync()

    def refresh_preferences(self) -> None:
        """Refresh controls after preferences are changed elsewhere."""
        self.png_reminder_checkbox.setChecked(
            self.settings.value(self._PNG_REMINDER_KEY, True, type=bool)
        )
        self.pdf_reminder_checkbox.setChecked(
            self.settings.value(self._PDF_REMINDER_KEY, True, type=bool)
        )

    def _copy_system_info(self) -> None:
        QApplication.clipboard().setText(self.system_info_view.toPlainText())
        self.system_info_feedback.setText("Copied to clipboard.")
        self._copy_feedback_timer.start()
