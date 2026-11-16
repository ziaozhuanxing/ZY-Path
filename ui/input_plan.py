"""A header-only preview of the same crop geometry used by inference."""

from dataclasses import dataclass

from core.sampling_plan import classification_grid, segmentation_grid, MAX_PROCESSING_REGIONS
from core.spatial_sampling import source_tile_size
from ui.input_help import scale_readiness


@dataclass(frozen=True)
class InputPreview:
    tile: tuple[int, int] | None = None
    network: tuple[int, int] | None = None
    grid: tuple[int, int] | None = None
    stride: tuple[int, int] | None = None
    edge: str = ""
    problem: str = ""
    can_use_tiles: bool = False
    notes: tuple[str, ...] = ()

    @property
    def count(self):
        return self.grid[0] * self.grid[1] if self.grid else None


def input_preview(profile, calibration, image_size, *, task="classification",
                  classification_mode="single_image", matched=False,
                  pixel_tile=(224, 224), calibration_error=""):
    if not image_size:
        return InputPreview(problem="Choose an image first.")
    network = profile.input_size if profile else (224, 224)
    if calibration_error and profile is not None:
        return InputPreview(network=network, problem="Image calibration needs correction: " + calibration_error)
    tile = None
    notes = []
    if matched:
        ready = scale_readiness(profile, calibration, has_image=True, calibration_error=calibration_error)
        if not ready.available:
            return InputPreview(network=network, problem=ready.explanation())
        tile = source_tile_size(profile, calibration)
        if any(mpp > field / size for mpp, field, size in zip(calibration.mpp, profile.field_um, network)):
            notes.append("This image has coarser pixels than the model reference. Resizing cannot recover missing tissue detail.")
    if task == "classification":
        if classification_mode == "single_image":
            if matched and tuple(image_size) != tile:
                return InputPreview(tile, network, problem="Choose Tiled analysis for this image. Matched Single image must contain exactly one model field.", can_use_tiles=True)
            if profile and profile.input_scope == "patch" and tuple(image_size) != network and not matched:
                notes.append("The whole picture will be resized into one model input. Tiled analysis preserves local tissue regions.")
            return InputPreview(tuple(image_size), network, (1, 1), notes=tuple(notes))
        tile = tile or tuple(pixel_tile)
        edge = (profile.edge_policy if matched else profile.pixel_edge_policy) if profile else "crop_then_resize"
        try:
            if edge == "reflect" and tile[0] * tile[1] > 25_000_000:
                raise ValueError("Reflect-padded tiles must not exceed 25 million pixels. Reduce the pixel tile dimensions.")
            columns, rows = classification_grid(image_size, tile, edge)
            count = columns * rows
            if not count:
                raise ValueError("This image is smaller than one model field; no complete field fits. Use a larger calibrated region or keep pixel settings.")
            if count > MAX_PROCESSING_REGIONS:
                action = "Choose a smaller calibrated image region." if matched else "Choose a smaller image region or larger pixel tiles."
                raise ValueError(f"This plan has {count:,} tiles; the limit is 10,000. " + action)
        except ValueError as error:
            return InputPreview(tile, network, edge=edge, problem=str(error))
        if edge == "skip" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append(f"Incomplete borders are left out: {image_size[0] % tile[0]} px on the right and {image_size[1] % tile[1]} px at the bottom.")
        elif edge == "reflect" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append("Incomplete border tiles use reflected pixels for padding.")
        elif edge == "crop_then_resize" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append("Partial edge tiles are resized separately in pixel mode.")
        return InputPreview(tile, network, (columns, rows), edge=edge, notes=tuple(notes))
    if profile is None:
        return InputPreview(notes=("Model input details are not supplied. Configure the requirements to preview segmentation sampling.",))
    if profile.input_scope == "image":
        return InputPreview(tuple(image_size), network, (1, 1))
    tile = tile or profile.tile_size
    stride = tuple(max(1, min(n, round(step * n / base))) for n, step, base in zip(tile, profile.stride, profile.tile_size))
    try:
        grid = segmentation_grid(image_size, tile, stride, network, len(profile.classes), edge_policy=profile.edge_policy)
    except ValueError as error:
        return InputPreview(tile, network, stride=stride, problem=str(error))
    if any(n < crop for n, crop in zip(image_size, tile)):
        notes.append("The small image is reflect-padded to one complete processing region.")
    if any(step < crop for step, crop in zip(stride, tile)):
        notes.append("Segmentation regions overlap; their predictions are blended back onto the original image.")
    return InputPreview(tile, network, (grid.columns, grid.rows), stride, profile.edge_policy, notes=tuple(notes))
