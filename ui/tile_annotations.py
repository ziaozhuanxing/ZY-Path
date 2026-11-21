"""Tile identifiers drawn after image scaling, without changing prediction data."""
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QTransform


def snapshot_number_style(font, pixel_size):
    """Resolve ten digit outlines on the GUI thread, once per export snapshot.

    Qt font engines have thread-local caches. Passing outlines and scalar
    metrics avoids resolving/rasterizing a different font in export workers.
    """
    font = QFont(font)
    font.setPixelSize(pixel_size)
    font.setBold(True)
    metrics = QFontMetricsF(font)
    digits = {}
    for digit in '0123456789':
        path = QPainterPath()
        path.addText(0, 0, font, digit)
        digits[digit] = (path, metrics.horizontalAdvance(digit))
    return dict(digits=digits, height=metrics.height(), ascent=metrics.ascent())


def draw_tile_numbers(painter, boxes, transform, pixel_size=12, *, style=None):
    """Use recorded crop centres and the image transform; text stays screen-sized."""
    painter.save()
    if style is None:
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
        width = sum(style['digits'][digit][1] for digit in text) if style else metrics.horizontalAdvance(text)
        height = style['height'] if style else metrics.height()
        badge = QRectF(0, 0, width + 10, height + 4)
        badge.moveCenter(crop.center())
        painter.save()
        painter.setClipRect(crop, Qt.IntersectClip)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(15, 23, 42, 240))
        painter.drawRoundedRect(badge, 3, 3)
        if style is None:
            painter.setPen(QColor("white"))
            painter.drawText(badge, Qt.AlignCenter, text)
        else:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setBrush(QColor('white'))
            x = badge.center().x() - width / 2
            baseline = badge.top() + 2 + style['ascent']
            for digit in text:
                path, advance = style['digits'][digit]
                painter.drawPath(QTransform().translate(x, baseline).map(path))
                x += advance
        painter.restore()
    painter.restore()
