"""Classification regions with model-declared geometry and unique pixel ownership."""

from dataclasses import dataclass
from typing import Callable

import numpy as np
from PIL import Image
import torch

from core.model_loader import ModelLoader
from core.output_parser import OutputParser
from core.preprocessor import Preprocessor
from core.classification_input import DEFAULT_CLASSIFICATION_RESIZE
from core.sampling_plan import classification_grid, classification_stride, border_positions, MAX_PROCESSING_REGIONS
from core.classification_fusion import FUSION_WORK_BYTES, fuse_classification_tiles

CLASSIFICATION_LABELS = ("ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM")
# Application display palette, not a claim about training labels or segmentation.
CLASSIFICATION_COLORS = (
    (230, 159, 0), (210, 210, 210), (86, 180, 233),
    (0, 158, 115), (240, 228, 66), (0, 114, 178),
    (213, 94, 0), (204, 121, 167), (120, 60, 140),
)

# Each tile retains predictions and a row in the interactive details table.
# Bound the work before allocating maps or scheduling model calls.
MAX_CLASSIFICATION_TILES = MAX_PROCESSING_REGIONS


class ClassificationWorkloadError(ValueError):
    """A tiled request exceeds the interactive application's work budget."""


def validate_tile_count(count: int) -> None:
    if count > MAX_CLASSIFICATION_TILES:
        raise ClassificationWorkloadError(
            f"Tiled analysis would contain {count:,} tiles; the limit is "
            f"{MAX_CLASSIFICATION_TILES:,} tiles per image. Increase the tile width "
            "and height, or use a smaller image."
        )


def validate_classification_workload(image_size, tile_size, edge_policy="crop_then_resize", *,
                                     overlap=False, classes=0) -> int:
    """Return the exact crop count, rejecting unsafe or invalid requests."""
    for name, size in (("Image size", image_size), ("Tile size", tile_size)):
        if (not isinstance(size, (list, tuple)) or len(size) != 2
                or any(type(value) is not int or value <= 0 for value in size)):
            raise ValueError(f"{name} must contain two positive integer dimensions.")
    columns, rows = classification_grid(image_size, tile_size, edge_policy, overlap=overlap)
    count = columns * rows
    validate_tile_count(count)
    if not count:
        raise ValueError("No complete model field fits in this image. Select a larger region or an explicitly supported padding policy.")
    from core.image_budget import validate_raster_budget
    validate_raster_budget(image_size, extra_bytes=count * classes * 40 + (FUSION_WORK_BYTES if overlap else 0))
    return count


def exploratory_metadata(width: int, height: int, resize_backend: str = DEFAULT_CLASSIFICATION_RESIZE) -> dict:
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
    resize_backend: str = DEFAULT_CLASSIFICATION_RESIZE
    edge_policy: str = "crop_then_resize"
    output_kind: str = "logits"
    input_profile: object | None = None
    overlap: bool = False

    @classmethod
    def from_metadata(cls, metadata: dict, classes: list[str], profile: str):
        """Require explicit original-image geometry, preprocessing and ordered colors."""
        def size(name):
            value = metadata.get(name)
            if (not isinstance(value, (list, tuple)) or len(value) != 2
                    or any(type(n) is not int or n <= 0 for n in value)):
                raise ValueError(f"Classification tiles require explicit {name}=[width, height].")
            return tuple(value)

        count = len(classes)
        if not 2 <= count <= 65536 or len(set(classes)) != count or any(not isinstance(s, str) or not s for s in classes):
            raise ValueError("Classification tiles require distinct ordered model class labels.")
        if metadata.get("classes") != list(classes):
            raise ValueError("Classification tile class order must match the model exactly.")
        if metadata.get("preprocess") != profile or profile not in ("raw255", "imagenet", "custom", "embedded"):
            raise ValueError("Classification tile preprocessing must match the model metadata.")
        colors = metadata.get("colors")
        if (not isinstance(colors, (list, tuple)) or len(colors) != count
                or any(not isinstance(c, (list, tuple)) or len(c) != 3
                       or any(type(v) is not int or not 0 <= v <= 255 for v in c)
                       for c in colors)):
            raise ValueError("Classification tiles require one ordered RGB color per class.")
        colors = tuple(tuple(c) for c in colors)
        if len(set(colors)) != count:
            raise ValueError("Classification tile colors must be distinct.")
        backend = metadata.get("resize_backend", "pillow_bilinear")
        if backend not in ("pillow_bilinear", "opencv_linear"):
            raise ValueError("Unknown classification resize backend.")
        edge = metadata.get("edge_policy", "crop_then_resize")
        if edge not in ("crop_then_resize", "skip", "reflect", "cover"):
            raise ValueError("Unknown classification edge policy.")
        overlap = metadata.get("overlap", False)
        if type(overlap) is not bool:
            raise ValueError("Tile overlap must be explicitly enabled or disabled.")
        output_kind = metadata.get("output_kind", "logits")
        if output_kind not in ("logits", "probabilities"):
            raise ValueError("Unknown classification output kind.")
        input_profile = None
        if metadata.get("input_profile") is not None:
            from core.model_profile import ModelInputProfile
            input_profile = ModelInputProfile.from_dict(metadata["input_profile"])
            if (input_profile.classes != tuple(classes) or input_profile.input_size != size("input_size")
                    or input_profile.normalization != profile or input_profile.output_kind != output_kind
                    or input_profile.resize_backend != backend or input_profile.colors != colors):
                raise ValueError("Classification tile settings conflict with the model input profile.")
        tile_size = size("tile_size")
        if edge == "reflect" and tile_size[0] * tile_size[1] > 25_000_000:
            raise ValueError("Reflect-padded source tiles must not exceed 25 million pixels.")
        return cls(tile_size, size("input_size"), tuple(classes), colors, profile,
                   str(metadata.get("scale_status", "unconfirmed_exploratory")), backend,
                   "cover" if overlap else edge, output_kind, input_profile, overlap)


def predict_classification_tiles(image: Image.Image, model, spec: ClassificationTileSpec,
                                 progress_callback: Callable | None = None,
                                 cancel_callback: Callable | None = None) -> dict:
    """Apply the declared edge policy and classify each retained crop once."""
    width, height = image.size
    tw, th = spec.tile_size
    edge = "cover" if spec.overlap else spec.edge_policy
    total = validate_classification_workload(image.size, spec.tile_size, edge,
                                             overlap=spec.overlap, classes=len(spec.classes))
    step_x, step_y = classification_stride(spec.tile_size, spec.overlap)
    stop_x = width - tw + 1 if edge == "skip" else width
    stop_y = height - th + 1 if edge == "skip" else height
    xs, ys = range(0, max(0, stop_x), tw), range(0, max(0, stop_y), th)
    if edge == "cover":
        xs, ys = border_positions(width, tw, step_x), border_positions(height, th, step_y)
    # Partition overlap at its midpoint. Prediction crops remain full-sized;
    # ownership boxes cover each real source pixel exactly once.
    def boundaries(positions, length, tile):
        return [0] + [(a + tile + b) // 2 for a, b in zip(positions, positions[1:])] + [length]
    x_edges = boundaries(xs, width, tw) if edge == "cover" else None
    y_edges = boundaries(ys, height, th) if edge == "cover" else None
    preprocessor = spec.input_profile.preprocessor() if spec.input_profile else Preprocessor(spec.preprocess, spec.input_size, spec.resize_backend)
    color_map = None if spec.overlap else np.full((height, width, 3), 128, dtype=np.uint8)
    count = len(spec.classes)
    tile_counts = [0] * count
    pixel_counts = [0] * count
    probabilities = np.zeros(count, dtype=np.float64)
    tiles = []
    for row, y in enumerate(ys):
        for column, x in enumerate(xs):
            if cancel_callback and cancel_callback():
                raise InterruptedError("Classification tiles cancelled.")
            box = (x, y, min(x + tw, width), min(y + th, height))
            patch = image.crop(box)
            if edge == "reflect" and patch.size != (tw, th):
                patch = Image.fromarray(np.pad(np.asarray(patch.convert("RGB")),
                    ((0, th - patch.height), (0, tw - patch.width), (0, 0)), mode="reflect"))
            with torch.inference_mode():
                output = ModelLoader.forward(model, preprocessor.transform(patch))
            parsed = OutputParser.parse_classification(output, list(spec.classes), output_kind=spec.output_kind)
            index = spec.classes.index(parsed["label"])
            area_box = (x_edges[column], y_edges[row], x_edges[column + 1], y_edges[row + 1]) if x_edges else box
            ax, ay, bx, by = area_box
            area = (bx - ax) * (by - ay)
            tile_counts[index] += 1
            if color_map is not None:
                pixel_counts[index] += area
                probabilities += np.asarray(parsed["probabilities"]) * area
                color_map[ay:by, ax:bx] = spec.colors[index]
            tiles.append({"box": list(box), "area_box": list(area_box), "class_index": index,
                          "label": parsed["label"], "confidence": float(parsed["confidence"]),
                          "probabilities": list(parsed["probabilities"])})
            if progress_callback:
                progress_callback(len(tiles), total)
            if cancel_callback and cancel_callback():
                raise InterruptedError("Classification cancelled")
    if spec.overlap:
        color_map, pixel_counts, probabilities = fuse_classification_tiles(
            image.size, spec.tile_size, xs, ys, tiles, spec.colors, cancel_callback)
    analysed = sum(pixel_counts)
    if not spec.overlap:
        probabilities /= analysed
    dominant = int(probabilities.argmax())
    analysis = {
        "mode": "classification_tiles", "classification_mode": "tiled_analysis", "task_type": "classification",
        "resize_backend": spec.resize_backend,
        "classes": [{"index": i, "label": label, "color": list(spec.colors[i])}
                    for i, label in enumerate(spec.classes)],
        "tile_size": list(spec.tile_size), "input_size": list(spec.input_size),
        "preprocess": spec.preprocess, "image_size": [width, height],
        "edge_policy": edge, "stride": [step_x, step_y],
        "analysed_pixels": analysed, "unanalysed_pixels": width * height - analysed,
        "tile_counts": tile_counts, "pixel_counts": pixel_counts,
        "area_ratios": [n / (width * height) for n in pixel_counts],
        "area_denominator": "full_image_pixels", "tiles": tiles,
        "overlap_assignment": "center_weighted_probabilities" if spec.overlap else
                              "midpoint_partition" if edge == "cover" else "none",
        "summary": "area_weighted_mean_probabilities",
        "scale_status": spec.scale_status,
    }
    if spec.overlap:
        analysis.update(overlap=True, summary="mean_fused_probabilities")
    if spec.input_profile:
        analysis["input_profile"] = spec.input_profile.to_dict()
        analysis["output_kind"] = spec.output_kind
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
    if not color_only and analysis.get("unanalysed_pixels", 0):
        covered = image
        image = original.convert("RGB").copy()
        for tile in analysis["tiles"]:
            box = tuple(tile["box"])
            image.paste(covered.crop(box), box[:2])
    if boundaries:
        draw = ImageDraw.Draw(image)
        for tile in analysis["tiles"]:
            x0, y0, x1, y1 = tile.get("area_box", tile["box"])
            draw.rectangle((x0, y0, x1 - 1, y1 - 1), outline="white", width=1)
    return image
