"""Tile identifiers drawn after image scaling, without changing prediction data."""
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter


def draw_tile_numbers(painter, boxes, transform, pixel_size=12):
    """Use recorded crop centres and the image transform; text stays screen-sized."""
    painter.save()
    font = QFont(painter.font())
    font.setPixelSize(pixel_size)
    font.setBold(True)
    painter.setFont(font)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    metrics = painter.fontMetrics()
    for number, (x0, y0, x1, y1) in enumerate(boxes, 1):
        crop = transform.mapRect(QRectF(x0, y0, x1 - x0, y1 - y0))
        if painter.hasClipping() and not painter.clipBoundingRect().intersects(crop):
            continue
        text = str(number)
        badge = QRectF(0, 0, metrics.horizontalAdvance(text) + 10, metrics.height() + 4)
        badge.moveCenter(crop.center())
        painter.save()
        painter.setClipRect(crop, Qt.IntersectClip)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(15, 23, 42, 240))
        painter.drawRoundedRect(badge, 3, 3)
        painter.setPen(QColor("white"))
        painter.drawText(badge, Qt.AlignCenter, text)
        painter.restore()
    painter.restore()
