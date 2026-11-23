"""Blend patch-class probabilities on the original image grid."""

import numpy as np


_SCORES_PER_BLOCK = 1_048_576
FUSION_WORK_BYTES = 48 * 1024 * 1024


def _neighbors(centers, coordinates):
    right = np.searchsorted(centers, coordinates, side="right").clip(max=len(centers) - 1)
    left = (right - 1).clip(min=0)
    distance = np.maximum(1., centers[right] - centers[left])
    weight = ((coordinates - centers[left]) / distance).clip(0., 1.).astype(np.float32)
    return left, right, weight[:, None]


def fuse_classification_tiles(image_size, tile_size, xs, ys, tiles, colors, cancel_callback=None):
    """Interpolate scores between crop centers and count each source pixel once.

    Between centers both full crops cover the interpolation interval. Outside
    the center grid use the nearest edge crop. Work on bounded blocks so the
    number of classes does not multiply the memory for the entire image.
    """
    width, height = image_size
    tw, th = tile_size
    count = len(colors)
    centers_x = np.asarray(xs, dtype=np.float64) + (tw - 1) / 2
    centers_y = np.asarray(ys, dtype=np.float64) + (th - 1) / 2
    grid = np.asarray([tile["probabilities"] for tile in tiles], dtype=np.float32)
    grid = grid.reshape(len(ys), len(xs), count)
    color_array = np.asarray(colors, dtype=np.uint8)
    color_map = np.empty((height * width, 3), dtype=np.uint8)
    pixel_counts = np.zeros(count, dtype=np.int64)
    score_sums = np.zeros(count, dtype=np.float64)
    total = width * height
    block = max(1, _SCORES_PER_BLOCK // count)
    for start in range(0, total, block):
        if cancel_callback and cancel_callback():
            raise InterruptedError("Classification cancelled")
        end = min(total, start + block)
        rows, columns = np.divmod(np.arange(start, end), width)
        x0, x1, wx = _neighbors(centers_x, columns)
        y0, y1, wy = _neighbors(centers_y, rows)
        scores = grid[y0, x0]
        scores *= 1 - wx
        scores += grid[y0, x1] * wx
        scores *= 1 - wy
        bottom = grid[y1, x0]
        bottom *= 1 - wx
        bottom += grid[y1, x1] * wx
        scores += bottom * wy
        labels = scores.argmax(axis=1)
        color_map[start:end] = color_array[labels]
        pixel_counts += np.bincount(labels, minlength=count)
        score_sums += scores.sum(axis=0, dtype=np.float64)
    return color_map.reshape(height, width, 3), pixel_counts.tolist(), score_sums / total
