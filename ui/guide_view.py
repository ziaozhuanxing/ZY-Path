"""A readable guide with fixed contents controls and scroll-aware section state."""
from html import escape

from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtGui import QTextCursor, QTextOption
from PyQt5.QtWidgets import (
    QActionGroup, QHBoxLayout, QLabel, QLayout, QMenu, QSizePolicy,
    QTextBrowser, QToolButton, QVBoxLayout, QWidget,
)

from ui.help_content import GUIDE_SECTIONS


class GuideView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._jumping = False
        self._heading_positions = []
        self.current_section = 0
        self._sync_timer = QTimer(self)
        self._sync_timer.setSingleShot(True)
        self._sync_timer.timeout.connect(self._sync_section)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        toolbar = QHBoxLayout()
        self.contents_button = QToolButton(self)
        self.contents_button.setText("Contents")
        self.contents_button.setToolTip("Jump to a guide section; the checked item follows your reading position.")
        self.contents_button.setPopupMode(QToolButton.InstantPopup)
        self.contents_menu = QMenu(self.contents_button)
        self.contents_group = QActionGroup(self)
        self.contents_group.setExclusive(True)
        self.section_actions = []
        for index, (title, _) in enumerate(GUIDE_SECTIONS):
            action = self.contents_menu.addAction(f"{index + 1:02d}. {title}")
            action.setCheckable(True)
            self.contents_group.addAction(action)
            action.triggered.connect(lambda checked=False, i=index: self.go_to_section(i))
            self.section_actions.append(action)
        self.contents_button.setMenu(self.contents_menu)
        toolbar.addWidget(self.contents_button)
        self.previous_button = QToolButton(self)
        self.previous_button.setArrowType(Qt.LeftArrow)
        self.previous_button.setToolTip("Previous section")
        self.previous_button.setAccessibleName("Previous section")
        self.next_button = QToolButton(self)
        self.next_button.setArrowType(Qt.RightArrow)
        self.next_button.setToolTip("Next section")
        self.next_button.setAccessibleName("Next section")
        self.previous_button.clicked.connect(lambda: self.go_to_section(self.current_section - 1))
        self.next_button.clicked.connect(lambda: self.go_to_section(self.current_section + 1))
        toolbar.addWidget(self.previous_button)
        toolbar.addWidget(self.next_button)
        self.section_label = QLabel(self)
        self.section_label.setWordWrap(True)
        self.section_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        toolbar.addWidget(self.section_label, 1)
        layout.addLayout(toolbar)
        self.browser = QTextBrowser(self)
        self.browser.setObjectName("guideBrowser")
        self.browser.setMinimumSize(0, 0)
        self.browser.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.browser.setStyleSheet("QTextBrowser#guideBrowser { border: none; padding: 0; }")
        self.browser.setOpenExternalLinks(True)
        self.browser.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.browser.document().setDefaultStyleSheet(
            "h2 { font-size: 115%; margin-top: 18px; margin-bottom: 8px; } "
            "p { margin-top: 0px; margin-bottom: 12px; } "
            "li { margin-bottom: 6px; } a { color: #3182CE; }")
        parts = []
        for index, (title, body) in enumerate(GUIDE_SECTIONS):
            parts.append(f'<h2><a name="section-{index}"></a>{index + 1:02d}. {escape(title)}</h2>')
            parts.extend(f"<p>{paragraph}</p>" for paragraph in body.split("<br><br>"))
        self.browser.setHtml("".join(parts))
        for index, (title, _) in enumerate(GUIDE_SECTIONS):
            cursor = self.browser.document().find(f"{index + 1:02d}. {title}")
            self._heading_positions.append(cursor.selectionStart())
        layout.addWidget(self.browser, 1)
        self.browser.verticalScrollBar().valueChanged.connect(self._sync_section)
        self.browser.verticalScrollBar().rangeChanged.connect(lambda *_: self._sync_timer.start(0))
        self.browser.viewport().installEventFilter(self)
        self._set_section(0)

    def _set_section(self, index):
        self.current_section = index
        self.section_label.setText(f"{index + 1} / {len(GUIDE_SECTIONS)} · {GUIDE_SECTIONS[index][0]}")
        self.section_actions[index].setChecked(True)
        self.previous_button.setEnabled(index > 0)
        self.next_button.setEnabled(index + 1 < len(GUIDE_SECTIONS))

    def go_to_section(self, index):
        index = max(0, min(len(GUIDE_SECTIONS) - 1, index))
        self._jumping = True
        try:
            self.browser.scrollToAnchor(f"section-{index}")
            self._set_section(index)
        finally:
            self._jumping = False

    def _sync_section(self, *unused):
        if self._jumping or not self._heading_positions:
            return
        bar = self.browser.verticalScrollBar()
        if bar.maximum() > 0 and bar.value() == bar.maximum():
            self._set_section(len(GUIDE_SECTIONS) - 1)
            return
        index = 0
        for position, offset in enumerate(self._heading_positions):
            cursor = QTextCursor(self.browser.document())
            cursor.setPosition(offset)
            if self.browser.cursorRect(cursor).top() <= 8:
                index = position
            else:
                break
        self._set_section(index)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Resize:
            self._sync_timer.start(0)
        return super().eventFilter(watched, event)

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_timer.start(0)
