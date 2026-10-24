"""Export, session metadata, and rerun controls."""

from math import ceil

from PyQt5.QtCore import QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent, QTextOption
from PyQt5.QtWidgets import (
    QGridLayout,
    QScrollArea,
    QLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ui.theme import MONO_FONT, style_panel_scroll


class _MetadataValue(QTextBrowser):
    """Selectable plain text that wraps even unbroken model/file names."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.setFrameShape(self.NoFrame)
        self.setLineWrapMode(self.WidgetWidth)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.document().setDocumentMargin(0)
        self.setStyleSheet("QTextBrowser { background: transparent; border: none; padding: 0; }")
        self.viewport().setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

    def setText(self, value):
        """Keep metadata literal, including names containing HTML characters."""
        self.setPlainText(value)

    def text(self):
        """Expose the original plain value to existing session-panel callers."""
        return self.toPlainText()

    def wordWrap(self):
        return self.lineWrapMode() != self.NoWrap


class ActionPanel(QWidget):
    """Provide result export, session details, and rerun actions."""

    export_png_requested = pyqtSignal()
    export_pdf_requested = pyqtSignal()
    rerun_requested = pyqtSignal()
    clear_view_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ActionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(240)
        self._metadata_layout_timer = QTimer(self)
        self._metadata_layout_timer.setSingleShot(True)
        self._metadata_layout_timer.timeout.connect(self._update_metadata_label_heights)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)
        outer.setSizeConstraint(QLayout.SetNoConstraint)
        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        export_title = QLabel("Export", self)
        export_title.setObjectName("actionSectionTitle")
        export_title.setToolTip("Export the current inference result.")
        layout.addWidget(export_title)

        self.export_png_button = QPushButton("Export PNG", self)
        self.export_png_button.setObjectName("exportPngButton")
        self.export_png_button.setToolTip("Export the result image only.")
        self.export_png_button.setEnabled(False)
        layout.addWidget(self.export_png_button)

        self.export_pdf_button = QPushButton("Export PDF", self)
        self.export_pdf_button.setObjectName("exportPdfButton")
        self.export_pdf_button.setToolTip(
            "Export a full report with the original image, results, and analysis details."
        )
        self.export_pdf_button.setEnabled(False)
        layout.addWidget(self.export_pdf_button)

        session_title = QLabel("Session", self)
        session_title.setObjectName("actionSectionTitle")
        session_title.setToolTip("Details for the current inference session.")
        layout.addSpacing(12)
        layout.addWidget(session_title)

        metadata_layout = QGridLayout()
        metadata_layout.setHorizontalSpacing(8)
        metadata_layout.setVerticalSpacing(8)
        metadata_layout.setColumnStretch(1, 1)
        self.metadata_labels: dict[str, _MetadataValue] = {}
        for row, (key, title, tip) in enumerate(
            (
                ("model", "Model", "Model used for this inference session."),
                ("image", "Image", "Image used for this inference session."),
                ("time", "Time", "Time this inference session was created."),
                ("record", "Record", "History record for the current result."),
            )
        ):
            name_label = QLabel(title, self)
            name_label.setObjectName("metadataNameLabel")
            name_label.setToolTip(tip)
            value_label = _MetadataValue(self)
            value_label.setText("-")
            value_label.setObjectName("metadataValueLabel")
            value_label.setFont(MONO_FONT)
            value_label.setMinimumWidth(0)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            value_label.setToolTip(tip)
            metadata_layout.addWidget(name_label, row, 0)
            metadata_layout.addWidget(value_label, row, 1)
            self.metadata_labels[key] = value_label
            value_label.installEventFilter(self)
            value_label.viewport().installEventFilter(self)
        layout.addLayout(metadata_layout)
        layout.addStretch()

        self.rerun_button = QPushButton("Re-run", self)
        self.rerun_button.setObjectName("rerunButton")
        self.rerun_button.setToolTip("Select a history record first")
        self.rerun_button.setEnabled(False)
        self.controls_scroll = QScrollArea(self)
        self.controls_scroll.setWidgetResizable(True)
        self.controls_scroll.setFrameShape(QScrollArea.NoFrame)
        self.controls_scroll.setMinimumSize(0, 0)
        # Only the pinned Re-run button and panel padding need a minimum
        # height. Native scrollbar hints belong inside the scrolling content,
        # otherwise this panel stretches the whole horizontal splitter.
        self.controls_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.controls_scroll.setWidget(content)
        self.controls_scroll.viewport().installEventFilter(self)
        style_panel_scroll(self.controls_scroll)
        outer.addWidget(self.controls_scroll, 1)
        outer.addWidget(self.rerun_button)
        self.clear_view_button = QPushButton("Clear view", self)
        self.clear_view_button.setObjectName("clearViewButton")
        self.clear_view_button.setToolTip(
            "Clear the input image, displayed result and history selection. "
            "Saved history, files and model settings are kept."
        )
        outer.addWidget(self.clear_view_button)

        self.export_png_button.clicked.connect(self.export_png_requested.emit)
        self.export_pdf_button.clicked.connect(self.export_pdf_requested.emit)
        self.rerun_button.clicked.connect(self.rerun_requested.emit)
        self.clear_view_button.clicked.connect(self.clear_view_requested.emit)

    def set_metadata(
        self,
        model_name: str,
        image_filename: str,
        timestamp: str,
        record_id: int | None = None,
    ) -> None:
        """Set the model, image, and time shown for the current session."""
        for key, value in (
            ("model", model_name),
            ("image", image_filename),
            ("time", timestamp),
            ("record", f"#{record_id}" if record_id is not None else "-"),
        ):
            full_text = value or "-"
            self.metadata_labels[key].setText(full_text)
            self.metadata_labels[key].setToolTip(full_text)
        self._update_metadata_label_heights()
        self._metadata_layout_timer.start(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Recalculate wrapped session label heights after a width change."""
        super().resizeEvent(event)
        self._metadata_layout_timer.start(0)

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Resize, QEvent.FontChange, QEvent.StyleChange):
            self._metadata_layout_timer.start(0)
        return super().eventFilter(watched, event)

    def set_result_available(self, available: bool) -> None:
        """Enable or disable both export buttons."""
        self.export_png_button.setEnabled(available)
        self.export_pdf_button.setEnabled(available)

    def set_rerun_enabled(
        self, enabled: bool, record_id: int | None = None
    ) -> None:
        """Enable or disable the rerun button."""
        self.rerun_button.setEnabled(enabled)
        self.rerun_button.setToolTip(
            f"Re-run record #{record_id} with the same image, model and task"
            if enabled and record_id is not None
            else "Select a history record first"
        )

    def clear(self) -> None:
        """Reset metadata and disable all actions."""
        self.set_metadata("-", "-", "-")
        self.set_result_available(False)
        self.set_rerun_enabled(False)

    def _update_metadata_label_heights(self) -> None:
        for label in self.metadata_labels.values():
            width = label.viewport().width()
            if width <= 0:
                continue
            label.document().setTextWidth(width)
            required_height = ceil(label.document().size().height()) + 2 * label.frameWidth()
            label.setFixedHeight(required_height)
