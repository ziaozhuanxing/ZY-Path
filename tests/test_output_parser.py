import numpy as np
import pytest
import torch
from PIL import Image

from core.output_parser import OutputParser


@pytest.mark.parametrize("num_classes", [3, 9])
def test_parse_classification_returns_probabilities_and_prediction(
    num_classes: int,
) -> None:
    labels = [f"Label {index}" for index in range(num_classes)]
    logits = torch.zeros((1, num_classes), dtype=torch.float32)
    logits[0, num_classes - 1] = 4.0

    result = OutputParser.parse_classification(logits, labels)

    assert result["label"] == labels[-1]
    assert result["class_index"] == num_classes - 1
    assert result["confidence"] == pytest.approx(max(result["probabilities"]))
    assert sum(result["probabilities"]) == pytest.approx(1.0)
    assert len(result["probabilities"]) == num_classes
    assert all(0.0 <= probability <= 1.0 for probability in result["probabilities"])


@pytest.mark.parametrize(
    "logits",
    [torch.zeros(3), torch.zeros((2, 3)), torch.zeros((1, 2, 3)), torch.zeros((1, 0))],
)
def test_parse_classification_rejects_invalid_output_shape(logits: torch.Tensor) -> None:
    with pytest.raises(ValueError, match=r"shape \(1, C\)"):
        OutputParser.parse_classification(logits, ["A", "B", "C"])


def test_parse_classification_rejects_label_count_mismatch() -> None:
    with pytest.raises(ValueError, match="number of class labels"):
        OutputParser.parse_classification(torch.zeros((1, 3)), ["A", "B"])


@pytest.mark.parametrize("num_classes", [3, 9])
def test_parse_segmentation_resizes_mask_and_builds_legend(num_classes: int) -> None:
    logits = torch.zeros((1, num_classes, 2, 2), dtype=torch.float32)
    logits[0, 0, 0, 0] = 1.0
    logits[0, 1, 0, 1] = 1.0
    logits[0, num_classes - 1, 1, 0] = 1.0
    logits[0, 1, 1, 1] = 1.0
    labels = [f"Label {index}" for index in range(num_classes)]

    result = OutputParser.parse_segmentation(
        logits,
        (4, 4),
        class_labels=labels,
    )

    mask = result["mask"]
    overlay = result["overlay"]
    assert isinstance(mask, np.ndarray)
    assert np.issubdtype(mask.dtype, np.integer)
    assert mask.shape == (4, 4)
    assert mask.tolist() == [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [num_classes - 1, num_classes - 1, 1, 1],
        [num_classes - 1, num_classes - 1, 1, 1],
    ]
    assert result["classes_present"] == sorted({0, 1, num_classes - 1})
    assert result["legend_items"] == [
        (labels[index], OutputParser._DEFAULT_COLORS[index])
        for index in sorted({0, 1, num_classes - 1})
    ]
    assert isinstance(overlay, Image.Image)
    assert overlay.mode == "RGBA"
    assert overlay.size == (4, 4)
    assert np.all(np.asarray(overlay)[..., 3] == 102)


def test_segmentation_uses_default_labels_and_cycles_default_colors() -> None:
    logits = torch.zeros((1, 17, 1, 2), dtype=torch.float32)
    logits[0, 0, 0, 0] = 1.0
    logits[0, 16, 0, 1] = 1.0

    result = OutputParser.parse_segmentation(logits, (2, 1))

    assert result["legend_items"] == [
        ("Class 0", OutputParser._DEFAULT_COLORS[0]),
        ("Class 16", OutputParser._DEFAULT_COLORS[0]),
    ]
    assert len(OutputParser._DEFAULT_COLORS) >= 10


def test_segmentation_accepts_custom_colors() -> None:
    logits = torch.tensor([[[[0]], [[1]]]], dtype=torch.float32)

    result = OutputParser.parse_segmentation(
        logits,
        (1, 1),
        class_colors=[(1, 2, 3), (4, 5, 6)],
    )

    assert result["legend_items"] == [("Class 1", (4, 5, 6))]
    assert result["overlay"].getpixel((0, 0)) == (4, 5, 6, 102)


@pytest.mark.parametrize(
    ("logits", "size", "labels", "colors"),
    [
        (torch.zeros((3, 2, 2)), (2, 2), None, None),
        (torch.zeros((1, 0, 2, 2)), (2, 2), None, None),
        (torch.zeros((1, 2, 2, 2)), (0, 2), None, None),
        (torch.zeros((1, 2, 2, 2)), (2, 2), ["Only one"], None),
        (torch.zeros((1, 2, 2, 2)), (2, 2), None, []),
        (torch.zeros((1, 2, 2, 2)), (2, 2), None, [(256, 0, 0)]),
    ],
)
def test_segmentation_rejects_invalid_arguments(
    logits: torch.Tensor,
    size: tuple[int, int],
    labels: list[str] | None,
    colors: list[tuple[int, int, int]] | None,
) -> None:
    with pytest.raises(ValueError):
        OutputParser.parse_segmentation(logits, size, labels, colors)


def test_blend_overlay_returns_rgb_image_with_same_size() -> None:
    original = Image.new("RGB", (2, 3), (0, 0, 0))
    overlay = Image.new("RGBA", (2, 3), (255, 0, 0, 102))

    blended = OutputParser.blend_overlay(original, overlay)

    assert blended.mode == "RGB"
    assert blended.size == original.size
    assert blended.getpixel((0, 0)) == (102, 0, 0)


def test_blend_overlay_rejects_different_sizes() -> None:
    with pytest.raises(ValueError, match="same size"):
        OutputParser.blend_overlay(
            Image.new("RGB", (2, 2)),
            Image.new("RGBA", (3, 2)),
        )