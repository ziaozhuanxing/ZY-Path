import numpy as np
import pytest
import torch
from PIL import Image

from core.preprocessor import Preprocessor


def test_raw255_returns_float32_nchw_without_scaling() -> None:
    image = Image.new("RGB", (2, 1))
    image.putdata([(10, 20, 30), (255, 128, 0)])

    tensor = Preprocessor(profile="raw255", size=(2, 1)).transform(image)

    assert tensor.shape == (1, 3, 1, 2)
    assert tensor.dtype == torch.float32
    assert tensor[0, :, 0, 0].tolist() == [10.0, 20.0, 30.0]
    assert tensor[0, :, 0, 1].tolist() == [255.0, 128.0, 0.0]


def test_imagenet_uses_expected_channel_normalization() -> None:
    image = Image.new("RGB", (1, 1), (255, 0, 128))

    tensor = Preprocessor(size=(1, 1)).transform(image)

    expected = torch.tensor(
        [
            (1.0 - 0.485) / 0.229,
            (0.0 - 0.456) / 0.224,
            ((128.0 / 255.0) - 0.406) / 0.225,
        ],
        dtype=torch.float32,
    )
    assert tensor.shape == (1, 3, 1, 1)
    assert tensor.dtype == torch.float32
    torch.testing.assert_close(tensor[0, :, 0, 0], expected)


@pytest.mark.parametrize(
    ("image", "expected_rgb"),
    [
        (Image.new("L", (1, 1), 37), (37.0, 37.0, 37.0)),
        (Image.new("RGBA", (1, 1), (11, 22, 33, 0)), (11.0, 22.0, 33.0)),
        (Image.new("P", (1, 1), 1), (40.0, 80.0, 120.0)),
    ],
)
def test_converts_grayscale_rgba_and_palette_images_to_rgb(
    image: Image.Image,
    expected_rgb: tuple[float, float, float],
) -> None:
    if image.mode == "P":
        palette = [0, 0, 0, 40, 80, 120] + [0] * (256 * 3 - 6)
        image.putpalette(palette)

    tensor = Preprocessor(profile="raw255", size=(1, 1)).transform(image)

    assert tensor.shape == (1, 3, 1, 1)
    assert tensor[0, :, 0, 0].tolist() == list(expected_rgb)


def test_resizes_only_to_the_requested_width_and_height() -> None:
    image = Image.new("RGB", (2, 3), (80, 100, 120))

    tensor = Preprocessor(profile="raw255", size=(4, 5)).transform(image)

    assert tensor.shape == (1, 3, 5, 4)
    assert torch.all(tensor == torch.tensor([80.0, 100.0, 120.0]).view(1, 3, 1, 1))


@pytest.mark.parametrize("profile", ["", "raw", "ImageNet", None])
def test_rejects_unknown_profiles(profile: str | None) -> None:
    with pytest.raises(ValueError, match="Profile must"):
        Preprocessor(profile=profile)  # type: ignore[arg-type]


@pytest.mark.parametrize("size", [(0, 224), (224, -1), (224,), (True, 224), [224, 224]])
def test_rejects_invalid_sizes(size: object) -> None:
    with pytest.raises(ValueError, match="Size must"):
        Preprocessor(size=size)  # type: ignore[arg-type]


def test_rejects_non_pillow_input() -> None:
    with pytest.raises(ValueError, match="Pillow image"):
        Preprocessor().transform(np.zeros((2, 2, 3)))  # type: ignore[arg-type]