"""Non-overlapping classification tiles with model-declared geometry and colors."""

from dataclasses import dataclass
from typing import Callable

import numpy as np
from PIL import Image
import torch

from core.model_loader import ModelLoader
from core.output_parser import OutputParser
from core.preprocessor import Preprocessor

CLASSIFICATION_LABELS = ("ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM")
# Application display palette, not a claim about training labels or segmentation.
CLASSIFICATION_COLORS = (
    (230, 159, 0), (210, 210, 210), (86, 180, 233),
    (0, 158, 115), (240, 228, 66), (0, 114, 178),
    (213, 94, 0), (204, 121, 167), (120, 60, 140),
)


def exploratory_metadata(width: int, height: int, resize_backend: str = "pillow_bilinear") -> dict:
    """Explicit user-selected geometry; network input is known, physical scale is not."""
    return {"tile_size": [width, height], "input_size": [224, 224],
            "classes": list(CLASSIFICATION_LABELS), "colors": [list(c) for c in CLASSIFICATION_COLORS],
            "preprocess": "raw255", "scale_status": "unconfirmed_exploratory",
            "palette": "classification_display_v1", "resize_backend": resize_backend}


@dataclass(frozen=True)
class ClassificationTileSpec:
    tile_size: tuple[int, int]
    input_size: tuple[int, int]
    classes: tuple[str, ...]
    colors: tuple[tuple[int, int, int], ...]
    preprocess: str
    scale_status: str = "unconfirmed_exploratory"
    resize_backend: str = "pillow_bilinear"

    @classmethod
    def from_metadata(cls, metadata: dict, classes: list[str], profile: str):
        """Require explicit original-image geometry, preprocessing and ordered colors."""
        def size(name):
            value = metadata.get(name)
            if (not isinstance(value, (list, tuple)) or len(value) != 2
                    or any(type(n) is not int or n <= 0 for n in value)):
                raise ValueError(f"Classification tiles require explicit {name}=[width, height].")
            return tuple(value)

        if len(classes) != 9 or len(set(classes)) != 9 or any(not s for s in classes):
            raise ValueError("Classification tiles require nine distinct model class labels.")
        if metadata.get("classes") != list(classes):
            raise ValueError("Classification tile class order must match the model exactly.")
        if metadata.get("preprocess") != profile or profile not in ("raw255", "imagenet"):
            raise ValueError("Classification tile preprocessing must match the model metadata.")
        colors = metadata.get("colors")
        if (not isinstance(colors, (list, tuple)) or len(colors) != 9
                or any(not isinstance(c, (list, tuple)) or len(c) != 3
                       or any(type(v) is not int or not 0 <= v <= 255 for v in c)
                       for c in colors)):
            raise ValueError("Classification tiles require nine ordered RGB colors.")
        colors = tuple(tuple(c) for c in colors)
        if len(set(colors)) != 9:
            raise ValueError("Classification tile colors must be distinct.")
        backend = metadata.get("resize_backend", "pillow_bilinear")
        if backend not in ("pillow_bilinear", "opencv_linear"):
            raise ValueError("Unknown classification resize backend.")
        return cls(size("tile_size"), size("input_size"), tuple(classes), colors, profile,
                   str(metadata.get("scale_status", "unconfirmed_exploratory")), backend)


def predict_classification_tiles(image: Image.Image, model, spec: ClassificationTileSpec,
                                 progress_callback: Callable | None = None,
                                 cancel_callback: Callable | None = None) -> dict:
    """Classify each crop once; resize partial edge crops without padding or overlap."""
    width, height = image.size
    tw, th = spec.tile_size
    preprocessor = Preprocessor(spec.preprocess, spec.input_size, spec.resize_backend)
    color_map = np.zeros((height, width, 3), dtype=np.uint8)
    tile_counts = [0] * 9
    pixel_counts = [0] * 9
    probabilities = np.zeros(9, dtype=np.float64)
    tiles = []
    total = ((width + tw - 1) // tw) * ((height + th - 1) // th)
    for y in range(0, height, th):
        for x in range(0, width, tw):
            if cancel_callback and cancel_callback():
                raise InterruptedError("Classification tiles cancelled.")
            box = (x, y, min(x + tw, width), min(y + th, height))
            with torch.inference_mode():
                output = ModelLoader.forward(model, preprocessor.transform(image.crop(box)))
            parsed = OutputParser.parse_classification(output, list(spec.classes))
            index = spec.classes.index(parsed["label"])
            area = (box[2] - x) * (box[3] - y)
            tile_counts[index] += 1
            pixel_counts[index] += area
            probabilities += np.asarray(parsed["probabilities"]) * area
            color_map[y:box[3], x:box[2]] = spec.colors[index]
            tiles.append({"box": list(box), "class_index": index,
                          "label": parsed["label"], "confidence": float(parsed["confidence"]),
                          "probabilities": list(parsed["probabilities"])})
            if progress_callback:
                progress_callback(len(tiles), total)
    probabilities /= width * height
    dominant = int(probabilities.argmax())
    analysis = {
        "mode": "classification_tiles", "classification_mode": "tiled_analysis", "task_type": "classification",
        "resize_backend": spec.resize_backend,
        "classes": [{"index": i, "label": label, "color": list(spec.colors[i])}
                    for i, label in enumerate(spec.classes)],
        "tile_size": list(spec.tile_size), "input_size": list(spec.input_size),
        "preprocess": spec.preprocess, "image_size": [width, height],
        "edge_policy": "crop_then_resize", "stride": list(spec.tile_size),
        "tile_counts": tile_counts, "pixel_counts": pixel_counts,
        "area_ratios": [n / (width * height) for n in pixel_counts],
        "area_denominator": "full_image_pixels", "tiles": tiles,
        "summary": "area_weighted_mean_probabilities",
        "scale_status": spec.scale_status,
    }
    return {"analysis_mode": "classification_tiles", "classification_analysis": analysis,
            "color_map": Image.fromarray(color_map), "label": spec.classes[dominant],
            "confidence": float(probabilities[dominant]), "probabilities": probabilities.tolist()}


def render_classification_map(original: Image.Image, color_map: Image.Image, analysis: dict,
                              opacity: float = .4, color_only: bool = False,
                              boundaries: bool = False) -> Image.Image:
    """Render at source coordinates; display settings never change class statistics."""
    from PIL import ImageDraw
    if original.size != color_map.size or list(original.size) != analysis["image_size"]:
        raise ValueError("Classification map and original image must share pixel coordinates.")
    if not 0 <= opacity <= 1:
        raise ValueError("Overlay opacity must be between zero and one.")
    image = (color_map.convert("RGB").copy() if color_only else
             Image.blend(original.convert("RGB"), color_map.convert("RGB"), opacity))
    if boundaries:
        draw = ImageDraw.Draw(image)
        for tile in analysis["tiles"]:
            x0, y0, x1, y1 = tile["box"]
            draw.rectangle((x0, y0, x1 - 1, y1 - 1), outline="white", width=1)
    return image
