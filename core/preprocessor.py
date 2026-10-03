"""Prepare images for model inference."""

import numpy as np
import torch
from PIL import Image


class Preprocessor:
    """Convert a Pillow image to a model-ready tensor."""

    _MEAN = (0.485, 0.456, 0.406)
    _STD = (0.229, 0.224, 0.225)

    def __init__(
        self,
        profile: str = "imagenet",
        size: tuple[int, int] = (224, 224),
    ) -> None:
        """Create a preprocessor with a scaling profile and output size."""
        if profile not in ("raw255", "imagenet"):
            raise ValueError("Profile must be 'raw255' or 'imagenet'.")
        if (
            not isinstance(size, tuple)
            or len(size) != 2
            or any(
                not isinstance(dimension, int)
                or isinstance(dimension, bool)
                or dimension <= 0
                for dimension in size
            )
        ):
            raise ValueError("Size must contain two positive integers (width, height).")

        self.profile = profile
        self.size = size

    def transform(self, pil_image: Image.Image) -> torch.Tensor:
        """Convert and resize an image, then return a float32 NCHW tensor."""
        if not isinstance(pil_image, Image.Image):
            raise ValueError("Input must be a Pillow image.")

        image = pil_image.convert("RGB")
        if image.size != self.size:
            image = image.resize(self.size, Image.Resampling.BILINEAR)

        image_array = np.asarray(image, dtype=np.float32).copy()
        tensor = (
            torch.from_numpy(image_array)
            .permute(2, 0, 1)
            .contiguous()
            .unsqueeze(0)
        )

        if self.profile == "imagenet":
            tensor.div_(255.0)
            mean = torch.tensor(self._MEAN, dtype=torch.float32).view(1, 3, 1, 1)
            std = torch.tensor(self._STD, dtype=torch.float32).view(1, 3, 1, 1)
            tensor.sub_(mean).div_(std)

        return tensor