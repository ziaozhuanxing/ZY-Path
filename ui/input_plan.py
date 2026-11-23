"""A header-only preview of the same crop geometry used by inference."""

from dataclasses import dataclass


from ui.language import tr
from core.sampling_plan import classification_grid, classification_stride, segmentation_grid, segmentation_stride, MAX_PROCESSING_REGIONS
from core.classification_fusion import FUSION_WORK_BYTES
from ui.input_help import scale_readiness


@dataclass(frozen=True)
class InputPreview:
    tile: tuple[int, int] | None = None
    network: tuple[int, int] | None = None
    grid: tuple[int, int] | None = None
    stride: tuple[int, int] | None = None
    edge: str = ""
    problem: str = ""
    notes: tuple[str, ...] = ()

    @property
    def count(self):
        return self.grid[0] * self.grid[1] if self.grid else None


def input_preview(profile, calibration, image_size, *, task="classification",
                  classification_mode="single_image", matched=False,
                  pixel_tile=(224, 224), calibration_error="", cover_borders=False, overlap=False):
    if not image_size:
        return InputPreview(problem=tr("Choose an image first."))
    network = profile.input_size if profile else (224, 224)
    if calibration_error and profile is not None:
        return InputPreview(network=network, problem="Image calibration needs correction: " + calibration_error)
    tile = None
    notes = []
    if matched:
        ready = scale_readiness(profile, calibration, has_image=True, calibration_error=calibration_error)
        if not ready.available:
            return InputPreview(network=network, problem=ready.explanation())
        tile = ready.tile_size
        if any(mpp > field / size for mpp, field, size in zip(calibration.mpp, profile.matching_field_um, network)):
            notes.append(tr("This image has coarser pixels than the model reference. Resizing cannot recover missing tissue detail."))
    if task == "classification":
        if classification_mode == "single_image":
            if matched and tuple(image_size) != tile:
                return InputPreview(tile, network, problem=tr("Choose Tiled analysis for this image. Matched Single image must contain exactly one model field."))
            if profile and profile.input_scope == "patch" and tuple(image_size) != network and not matched:
                notes.append(tr("The whole picture will be resized into one model input. Tiled analysis preserves local tissue regions."))
            return InputPreview(tuple(image_size), network, (1, 1), notes=tuple(notes))
        tile = tile or tuple(pixel_tile)
        edge = "cover" if cover_borders or overlap else (profile.edge_policy if matched else profile.pixel_edge_policy) if profile else "crop_then_resize"
        stride = classification_stride(tile, True) if overlap else None
        try:
            if edge == "reflect" and tile[0] * tile[1] > 25_000_000:
                raise ValueError(tr("Reflect-padded tiles must not exceed 25 million pixels. Reduce the pixel tile dimensions."))
            columns, rows = classification_grid(image_size, tile, edge, overlap=overlap)
            count = columns * rows
            from core.image_budget import validate_raster_budget
            memory = count * (len(profile.classes) if profile else 9) * 40 + (FUSION_WORK_BYTES if overlap else 0)
            validate_raster_budget(image_size, extra_bytes=memory)
            if not count:
                if overlap:
                    raise ValueError(tr("Overlap needs room for one full crop. Choose a larger image or turn off overlap."))
                raise ValueError(tr("This image is smaller than one model field; no complete field fits. Use a larger calibrated region or keep pixel settings."))
            if count > MAX_PROCESSING_REGIONS:
                action = tr("Choose a smaller calibrated image region.") if matched else tr("Choose a smaller image region or larger pixel tiles.")
                raise ValueError(tr("This plan has {count:,} tiles; the limit is 10,000. ").format(count=count) + action)
        except ValueError as error:
            return InputPreview(tile, network, edge=edge, problem=str(error))
        if overlap:
            notes.append(tr("Full crops cover the borders. The map blends class scores from nearby crop centers."))
        elif edge == "cover":
            notes.append(tr("Full-sized border regions overlap. Each source pixel is counted once, using the nearest region centre on each axis."))
        if edge == "skip" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append(tr("Incomplete borders are left out: {right} px on the right and {bottom} px at the bottom.")
                         .format(right=image_size[0] % tile[0], bottom=image_size[1] % tile[1]))
        elif edge == "reflect" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append(tr("Incomplete border tiles use reflected pixels for padding."))
        elif edge == "crop_then_resize" and (image_size[0] % tile[0] or image_size[1] % tile[1]):
            notes.append(tr("The whole image is analysed. Smaller edge crops are resized separately."))
        return InputPreview(tile, network, (columns, rows), stride=stride, edge=edge, notes=tuple(notes))
    if profile is None:
        return InputPreview(notes=(tr("Model input details are not supplied. Configure the requirements to preview segmentation sampling."),))
    if profile.input_scope == "image":
        return InputPreview(tuple(image_size), network, (1, 1))
    tile = tile or profile.tile_size
    stride = segmentation_stride(profile, tile)
    try:
        grid = segmentation_grid(image_size, tile, stride, network, len(profile.classes), edge_policy=profile.edge_policy)
    except ValueError as error:
        return InputPreview(tile, network, stride=stride, problem=str(error))
    if any(n < crop for n, crop in zip(image_size, tile)):
        notes.append(tr("The small image is reflect-padded to one complete processing region."))
    if any(step < crop for step, crop in zip(stride, tile)):
        notes.append(tr("Segmentation regions overlap; their predictions are blended back onto the original image."))
    return InputPreview(tile, network, (grid.columns, grid.rows), stride, profile.edge_policy, notes=tuple(notes))
