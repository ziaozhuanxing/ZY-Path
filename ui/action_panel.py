"""Export, session metadata, and rerun controls."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.theme import MONO_FONT


class ActionPanel(QWidget):
    """Provide result export, session details, and rerun actions."""

    export_png_requested = pyqtSignal()
    export_pdf_requested = pyqtSignal()
    rerun_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ActionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        export_title = QLabel("Export", self)
        export_title.setObjectName("actionSectionTitle")
        export_title.setToolTip("Export the current inference result.")
        layout.addWidget(export_title)

        self.export_png_button = QPushButton("Export PNG", self)
        self.export_png_button.setObjectName("exportPngButton")
        self.export_png_button.setToolTip("Export the current result as a PNG image.")
        self.export_png_button.setEnabled(False)
        layout.addWidget(self.export_png_button)

        self.export_pdf_button = QPushButton("Export PDF", self)
        self.export_pdf_button.setObjectName("exportPdfButton")
        self.export_pdf_button.setToolTip("Export the current result as a PDF report.")
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
        self.metadata_labels: dict[str, QLabel] = {}
        for row, (key, title, tip) in enumerate(
            (
                ("model", "Model", "Model used for this inference session."),
                ("image", "Image", "Image used for this inference session."),
                ("time", "Time", "Time this inference session was created."),
            )
        ):
            name_label = QLabel(title, self)
            name_label.setObjectName("metadataNameLabel")
            name_label.setToolTip(tip)
            value_label = QLabel("-", self)
            value_label.setObjectName("metadataValueLabel")
            value_label.setFont(MONO_FONT)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value_label.setToolTip(tip)
            metadata_layout.addWidget(name_label, row, 0)
            metadata_layout.addWidget(value_label, row, 1)
            self.metadata_labels[key] = value_label
        layout.addLayout(metadata_layout)
        layout.addStretch()

        self.rerun_button = QPushButton("Re-run", self)
        self.rerun_button.setObjectName("rerunButton")
        self.rerun_button.setToolTip("Run inference again with the current session inputs.")
        self.rerun_button.setEnabled(False)
        layout.addWidget(self.rerun_button)

        self.export_png_button.clicked.connect(self.export_png_requested.emit)
        self.export_pdf_button.clicked.connect(self.export_pdf_requested.emit)
        self.rerun_button.clicked.connect(self.rerun_requested.emit)

    def set_metadata(
        self, model_name: str, image_filename: str, timestamp: str
    ) -> None:
        """Set the model, image, and time shown for the current session."""
        self.metadata_labels["model"].setText(model_name or "-")
        self.metadata_labels["image"].setText(image_filename or "-")
        self.metadata_labels["time"].setText(timestamp or "-")

    def set_result_available(self, available: bool) -> None:
        """Enable or disable both export buttons."""
        self.export_png_button.setEnabled(available)
        self.export_pdf_button.setEnabled(available)

    def set_rerun_enabled(self, enabled: bool) -> None:
        """Enable or disable the rerun button."""
        self.rerun_button.setEnabled(enabled)

    def clear(self) -> None:
        """Reset metadata and disable all actions."""
        self.set_metadata("-", "-", "-")
        self.set_result_available(False)
        self.set_rerun_enabled(False)