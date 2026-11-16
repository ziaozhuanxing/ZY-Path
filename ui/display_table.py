"""Read-only result tables: no cell selection/focus painting, keyboard scrolling."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QAbstractSlider, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTableWidget


class _DisplayDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Qt parenting does not keep the Python top-level owner alive. Python
        # allocations in this virtual callback can collect an unreachable window
        # and delete the native table/painter while drawControl is still running.
        owner = self.parent().window()
        try:
            option = QStyleOptionViewItem(option)
            self.initStyleOption(option, index)
            option.state &= ~(QStyle.State_Selected | QStyle.State_HasFocus | QStyle.State_MouseOver)
            # Views may already have painted a current/selection background. Repaint
            # the model's swatch or themed base before text, including legacy states.
            brush = option.backgroundBrush
            if brush.style() == Qt.NoBrush:
                brush = option.palette.brush(QPalette.Base)
            painter.fillRect(option.rect, brush)
            style = option.widget.style() if option.widget else QApplication.style()
            style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)
            if index.row() == getattr(self.parent(), "inspection_row", -1):
                painter.save()
                painter.setPen(option.palette.color(QPalette.Highlight))
                painter.drawLine(option.rect.topLeft(), option.rect.topRight())
                painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
                painter.restore()
        finally:
            del owner


class DisplayTable(QTableWidget):
    """Enabled and focusable so users can scroll without selecting result cells."""
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.setProperty("displayOnly", True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setItemDelegate(_DisplayDelegate(self))
        self.inspection_row = -1

    def set_inspection_row(self, row=-1):
        self.inspection_row = row
        self.viewport().update()

    def clear_display_state(self):
        self.clearSelection()
        self.setCurrentItem(None)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clear_display_state()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clear_display_state()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.clear_display_state()

    def keyPressEvent(self, event):
        actions = {
            Qt.Key_Up: (self.verticalScrollBar(), QAbstractSlider.SliderSingleStepSub),
            Qt.Key_Down: (self.verticalScrollBar(), QAbstractSlider.SliderSingleStepAdd),
            Qt.Key_PageUp: (self.verticalScrollBar(), QAbstractSlider.SliderPageStepSub),
            Qt.Key_PageDown: (self.verticalScrollBar(), QAbstractSlider.SliderPageStepAdd),
            Qt.Key_Home: (self.verticalScrollBar(), QAbstractSlider.SliderToMinimum),
            Qt.Key_End: (self.verticalScrollBar(), QAbstractSlider.SliderToMaximum),
            Qt.Key_Left: (self.horizontalScrollBar(), QAbstractSlider.SliderSingleStepSub),
            Qt.Key_Right: (self.horizontalScrollBar(), QAbstractSlider.SliderSingleStepAdd),
        }
        if event.key() in actions:
            scrollbar, action = actions[event.key()]
            scrollbar.triggerAction(action)
            event.accept()
        else:
            super().keyPressEvent(event)
