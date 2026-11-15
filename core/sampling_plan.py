"""Small, allocation-free sampling plans shared by inference and its preview."""

from dataclasses import dataclass

MAX_PROCESSING_REGIONS = 10_000
MAX_FUSION_BYTES = 512 * 1024 * 1024


def _pair(value, name):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(type(n) is not int or n <= 0 for n in value)):
        raise ValueError(f"{name} must contain two positive integer dimensions.")
    return tuple(value)


def classification_grid(image_size, tile_size, edge_policy="crop_then_resize"):
    width, height = _pair(image_size, "Image size")
    tw, th = _pair(tile_size, "Tile size")
    if edge_policy not in ("skip", "reflect", "crop_then_resize"):
        raise ValueError("Unknown classification edge policy.")
    if edge_policy == "skip":
        return width // tw, height // th
    return (width + tw - 1) // tw, (height + th - 1) // th


@dataclass(frozen=True)
class SegmentationGrid:
    columns: int
    rows: int
    output_size: tuple[int, int]
    fusion_bytes: int

    @property
    def count(self):
        return self.columns * self.rows


def segmentation_grid(image_size, tile_size, stride, input_size, classes, *, edge_policy="reflect"):
    """Match the final-edge-covering grid without allocating positions or maps."""
    image_size = _pair(image_size, "Image size")
    tile_size = _pair(tile_size, "Tile size")
    stride = _pair(stride, "Stride")
    input_size = _pair(input_size, "Model input size")
    if type(classes) is not int or classes <= 0:
        raise ValueError("Class count must be a positive integer.")
    if any(s > t for s, t in zip(stride, tile_size)):
        raise ValueError("Stride must not exceed tile size.")
    if edge_policy not in ("skip", "reflect"):
        raise ValueError("Tiled segmentation requires skip or reflect edges.")
    if edge_policy == "skip" and any(n < t for n, t in zip(image_size, tile_size)):
        raise ValueError("No complete segmentation field fits in this image.")
    counts, output = [], []
    for length, tile, step, network in zip(image_size, tile_size, stride, input_size):
        last = max(0, length - tile)
        counts.append((last + step - 1) // step + 1)
        output.append(round(last * (network / tile)) + network)
    count = counts[0] * counts[1]
    if count > MAX_PROCESSING_REGIONS:
        raise ValueError("Segmentation exceeds 10,000 processing regions; select a smaller image region.")
    memory = output[0] * output[1] * (classes + 1) * 4
    if memory > MAX_FUSION_BYTES:
        raise ValueError("Segmentation probability fusion exceeds 512 MiB; select a smaller image region.")
    return SegmentationGrid(*counts, tuple(output), memory)
