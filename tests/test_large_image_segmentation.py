from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from torch import nn

from core.large_image_segmentation import (
    SEGMENTATION_LABELS,
    make_overlay,
    predict_large_image,
    tile_positions,
    validate_tile_settings,
)


class ConstantSegmenter(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        logits = torch.zeros(
            (inputs.shape[0], len(SEGMENTATION_LABELS), inputs.shape[2], inputs.shape[3])
        )
        logits[:, 2] = 1.0
        return logits


class BorderSensitiveSegmenter(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        logits = torch.zeros(
            (inputs.shape[0], len(SEGMENTATION_LABELS), inputs.shape[2], inputs.shape[3])
        )
        logits[:, 1, :, : inputs.shape[3] // 2] = 3.0
        logits[:, 3, :, inputs.shape[3] // 2 :] = 3.0
        return logits


def test_tile_positions_always_cover_the_final_edge() -> None:
    assert tile_positions(25, 10, 6) == [0, 6, 12, 15]
    assert tile_positions(8, 10, 6) == [0]


def test_tile_settings_reject_gaps() -> None:
    with pytest.raises(ValueError, match="no greater"):
        validate_tile_settings(10, 11, 4)


def test_small_and_non_multiple_images_return_full_size_statistics() -> None:
    image = Image.new("RGB", (17, 11), (120, 80, 40))
    result = predict_large_image(
        image,
        ConstantSegmenter(),
        torch.device("cpu"),
        tile=10,
        stride=6,
        input_size=4,
    )

    assert result["mask"].shape == (11, 17)
    assert int(result["counts"].sum()) == 17 * 11
    assert result["total_tiles"] == 6
    assert result["classes_present"] == [2]


def test_overlapping_probability_fusion_reports_progress_and_edge_classes() -> None:
    progress: list[tuple[int, int]] = []
    result = predict_large_image(
        Image.new("RGB", (23, 17)),
        BorderSensitiveSegmenter(),
        torch.device("cpu"),
        tile=10,
        stride=6,
        input_size=4,
        progress_callback=lambda done, total: progress.append((done, total)),
    )

    assert result["mask"].shape == (17, 23)
    assert progress[-1] == (result["total_tiles"], result["total_tiles"])
    assert set(np.unique(result["mask"])).issubset({1, 3})
    assert int(result["counts"].sum()) == 17 * 23


def test_overlay_is_recomputed_from_original_and_color_mask() -> None:
    original = Image.new("RGB", (2, 2), (100, 100, 100))
    colors = Image.new("RGB", (2, 2), (200, 0, 0))
    overlay = make_overlay(original, colors, alpha=0.2)

    assert overlay.getpixel((0, 0)) == (120, 80, 80)
    assert overlay.size == original.size
