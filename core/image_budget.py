"""Preflight decoded-raster working memory before allocating image buffers."""

# A conservative application work budget, not an estimate of free system RAM.
# Includes decoded RGB, overlays, Qt copies and temporary rendering buffers.
MAX_RASTER_WORKING_BYTES = 1536 * 1024 * 1024
RASTER_BYTES_PER_PIXEL = 48
PREVIEW_MAX_SIDE = 2048


def validate_raster_budget(size, *, extra_bytes=0):
    if (not isinstance(size, (tuple, list)) or len(size) != 2
            or any(type(n) is not int or n <= 0 for n in size)):
        raise ValueError("Image dimensions must be two positive integers.")
    estimated = size[0] * size[1] * RASTER_BYTES_PER_PIXEL + extra_bytes
    if estimated > MAX_RASTER_WORKING_BYTES:
        raise ValueError(f"This image needs an estimated {estimated / 1024**2:,.0f} MiB of raster working memory; the application budget is {MAX_RASTER_WORKING_BYTES / 1024**2:,.0f} MiB. Open a smaller native-resolution region (ROI). Do not resize merely to bypass this limit, because resizing changes MPP.")
    return estimated
