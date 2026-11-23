"""Overlapping-tile inference for the verified UPerNet tissue model."""

from collections.abc import Callable
import logging

import numpy as np
import torch
from PIL import Image

from core.model_loader import ModelLoader, ModelValidationError
from core.sampling_plan import segmentation_grid


logger = logging.getLogger(__name__)


SEGMENTATION_LABELS = (
    "Exclude",
    "Cancerous epithelium",
    "Stroma",
    "TILs",
    "Normal epithelium",
    "Junk/Debris",
    "Blood",
    "Other",
    "Whitespace/Empty",
)
SEGMENTATION_COLORS = (
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 255),
    (255, 165, 0),
    (255, 255, 255),
)

ProgressCallback = Callable[[int, int], None]
CancelCallback = Callable[[], bool]


def tile_positions(length: int, tile: int, stride: int) -> list[int]:
    """Return positions that cover an axis, including its final edge."""
    if length <= tile:
        return [0]
    positions = list(range(0, length - tile + 1, stride))
    if positions[-1] != length - tile:
        positions.append(length - tile)
    return positions


def validate_tile_settings(tile: int, stride: int, input_size: int) -> None:
    """Validate the dimensions used by overlapping tile inference."""
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value <= 0
        for value in (tile, stride, input_size)
    ):
        raise ValueError("Tile, stride, and input size must be positive integers.")
    if stride > tile:
        raise ValueError("Stride must be no greater than tile size so every pixel is covered.")


def predict_large_image(
    image: Image.Image,
    model: torch.nn.Module,
    device: torch.device,
    tile: int | tuple[int, int] = 1000,
    stride: int | tuple[int, int] = 512,
    input_size: int = 224,
    batch_size: int = 1,
    progress_callback: ProgressCallback | None = None,
    cancel_callback: CancelCallback | None = None,
) -> dict[str, object]:
    """Predict a large RGB image by fusing overlapping UPerNet probabilities."""
    if batch_size != 1:
        raise ValueError("The verified CPU path supports batch_size=1.")

    if not isinstance(tile, tuple) and not isinstance(stride, tuple):
        validate_tile_settings(tile, stride, input_size)
    tile_size = tile if isinstance(tile, tuple) else (tile, tile)
    tile_stride = stride if isinstance(stride, tuple) else (stride, stride)
    grid = segmentation_grid(image.size, tile_size, tile_stride, (input_size, input_size), len(SEGMENTATION_LABELS))
    tile_w, tile_h = tile_size
    if tile_w * tile_h > 25_000_000:
        raise ValueError("Source tiles above 25 million pixels are not supported.")
    width, height = image.size
    array = np.asarray(image.convert("RGB"))
    xs = tile_positions(width, tile_w, tile_stride[0])
    ys = tile_positions(height, tile_h, tile_stride[1])
    scale_x, scale_y = input_size / tile_w, input_size / tile_h
    low_w, low_h = grid.output_size
    probabilities = np.zeros((len(SEGMENTATION_LABELS), low_h, low_w), dtype=np.float32)
    weights = np.zeros((low_h, low_w), dtype=np.float32)
    hann = np.hanning(input_size + 2)[1:-1].astype(np.float32)
    window = np.outer(hann, hann) + 1e-3
    mean = torch.tensor((0.485, 0.456, 0.406), device=device).view(1, 3, 1, 1)
    std = torch.tensor((0.229, 0.224, 0.225), device=device).view(1, 3, 1, 1)
    total = len(ys) * len(xs)
    done = 0

    with torch.inference_mode():
        for y in ys:
            for x in xs:
                if cancel_callback is not None and cancel_callback():
                    raise InterruptedError("Inference was cancelled.")
                crop = array[y:y + tile_h, x:x + tile_w]
                if crop.shape[:2] != (tile_h, tile_w):
                    crop = np.pad(crop, ((0, tile_h - crop.shape[0]), (0, tile_w - crop.shape[1]), (0, 0)), mode="reflect")
                patch = Image.fromarray(crop).resize(
                    (input_size, input_size), Image.Resampling.BILINEAR
                )
                tensor = torch.from_numpy(np.asarray(patch, dtype=np.float32)).permute(2, 0, 1)
                tensor = tensor.unsqueeze(0).to(device)
                tensor = (tensor / 255.0 - mean) / std
                logits = ModelLoader.forward(model, tensor)
                expected_shape = (1, len(SEGMENTATION_LABELS), input_size, input_size)
                if tuple(logits.shape) != expected_shape:
                    raise ModelValidationError(
                        f"UPerNet output shape must be {expected_shape}, got {tuple(logits.shape)}."
                    )
                if not bool(torch.isfinite(logits).all().item()):
                    raise ModelValidationError("Segmentation output contains NaN or infinite values; no class map was created.")
                probability = logits.softmax(dim=1)[0].cpu().numpy()
                low_y = round(y * scale_y)
                low_x = round(x * scale_x)
                probabilities[:, low_y:low_y + input_size, low_x:low_x + input_size] += probability * window
                weights[low_y:low_y + input_size, low_x:low_x + input_size] += window
                done += 1
                logger.info("Large-image tile finished: %s/%s", done, total)
                if progress_callback is not None:
                    progress_callback(done, total)
                if cancel_callback is not None and cancel_callback():
                    raise InterruptedError("Segmentation cancelled")

    probabilities /= np.maximum(weights, 1e-6)[None, :, :]
    low_mask = probabilities.argmax(axis=0).astype(np.uint8)
    restored_size = (max(width, round(low_w / scale_x)), max(height, round(low_h / scale_y)))
    restored_mask = Image.fromarray(low_mask).resize(restored_size, Image.Resampling.NEAREST)
    mask = np.asarray(restored_mask, dtype=np.uint8)[:height, :width]
    counts = np.bincount(mask.ravel(), minlength=len(SEGMENTATION_LABELS)).astype(np.int64)
    color_mask = np.asarray(SEGMENTATION_COLORS, dtype=np.uint8)[mask]
    return {
        "mask": mask,
        "color_mask": Image.fromarray(color_mask, mode="RGB"),
        "counts": counts,
        "classes_present": [int(value) for value in np.flatnonzero(counts)],
        "width": width,
        "height": height,
        "tile": list(tile_size) if isinstance(tile, tuple) else tile,
        "stride": list(tile_stride) if isinstance(stride, tuple) else stride,
        "input_size": input_size,
        "total_tiles": total,
    }


def make_overlay(image: Image.Image, color_mask: Image.Image, alpha: float = 0.2) -> Image.Image:
    """Blend a fresh color mask with the original image at the requested opacity."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("Overlay alpha must be between 0 and 1.")
    original = np.asarray(image.convert("RGB"), dtype=np.float32)
    colors = np.asarray(color_mask.convert("RGB"), dtype=np.float32)
    blended = np.clip((1.0 - alpha) * original + alpha * colors, 0, 255).astype(np.uint8)
    return Image.fromarray(blended, mode="RGB")
