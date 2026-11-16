"""Display a decoded RGB source without running a second image decoder."""

from PyQt5.QtGui import QImage, QPixmap


def rgb_pixmap(image):
    rgb = image.convert("RGB")
    pixels = QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888)
    return QPixmap.fromImage(pixels.copy())
