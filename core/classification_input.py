"""Deterministic input operations used by the CRC validation pipeline."""

from pathlib import Path

import numpy as np
from PIL import Image

CLASSIFICATION_INPUT_SIZE = 224
DEFAULT_CLASSIFICATION_TILE_SIZE = 224
DEFAULT_CLASSIFICATION_RESIZE = "opencv_linear"
DEFAULT_CLASSIFICATION_DECODER = "opencv_color"
CLASSIFICATION_DECODERS = ("opencv_color", "pillow_rgb")


def decoded_image_size(path, decoder="pillow_rgb"):
    """Read dimensions in decoder coordinates without decoding raster pixels."""
    with Image.open(path) as image:
        size = image.size
        if decoder == "opencv_color" and image.getexif().get(274, 1) in (5, 6, 7, 8):
            size = tuple(reversed(size))
        return size


def load_rgb_image(path: str | Path, decoder: str = "pillow_rgb") -> Image.Image:
    """Decode like the training script, or preserve a recorded legacy reader.

    IMREAD_COLOR also specifies eight-bit, three-channel data and the decoder's
    orientation handling. Do not replace it with Pillow convert followed by an
    OpenCV resize: those operations can already disagree before resizing.
    """
    if decoder == "pillow_rgb":
        with Image.open(path) as image:
            image.seek(0)
            return image.convert("RGB").copy()
    if decoder != "opencv_color":
        raise ValueError("Unknown classification image decoder.")
    import cv2

    filename = str(path)
    try:
        image = cv2.imread(filename, cv2.IMREAD_COLOR)
        if image is None and Path(path).is_file():
            # OpenCV's filename API does not handle every Windows Unicode path.
            # Decode the same bytes with the same flags instead of changing readers.
            encoded = np.fromfile(path, dtype=np.uint8)
            if encoded.size:
                image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    except cv2.error as error:
        raise OSError("The image could not be decoded by OpenCV.") from error
    if image is None:
        raise OSError("The image could not be decoded by OpenCV.")
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
