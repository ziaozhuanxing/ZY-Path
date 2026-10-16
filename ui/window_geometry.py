"""Window bounds in Qt logical coordinates (QScreen.availableGeometry units)."""
from PyQt5.QtCore import QRect


def bounded_frame(rect: QRect, available: QRect) -> QRect:
    """Clamp size and position without any DPR conversion or screen-origin assumption."""
    width = max(1, min(rect.width(), available.width()))
    height = max(1, min(rect.height(), available.height()))
    x = min(max(rect.x(), available.x()), available.x() + available.width() - width)
    y = min(max(rect.y(), available.y()), available.y() + available.height() - height)
    return QRect(x, y, width, height)
