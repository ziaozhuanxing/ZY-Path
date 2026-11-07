"""Prepare images for model inference."""

import numpy as np
import torch
from PIL import Image

from core.classification_input import DEFAULT_CLASSIFICATION_RESIZE


class Preprocessor:
    """Convert a Pillow image to a model-ready tensor."""

    _MEAN = (0.485, 0.456, 0.406)
    _STD = (0.229, 0.224, 0.225)

    def __init__(
        self,
        profile: str = "imagenet",
        size: tuple[int, int] = (224, 224),
        resize_backend: str | None = None,
        *, mean=(), std=(), input_scale: float = 1.0,
    ) -> None:
        """Create a preprocessor with a scaling profile and output size."""
        if profile not in ("raw255", "imagenet", "custom", "embedded"):
            raise ValueError("Profile must be raw255, imagenet, custom or embedded.")
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

        if resize_backend is None:
            resize_backend = DEFAULT_CLASSIFICATION_RESIZE if profile == "raw255" else "pillow_bilinear"
        if resize_backend not in ("pillow_bilinear", "opencv_linear"):
            raise ValueError("Unknown resize backend.")
        self.resize_backend = resize_backend
        self.profile = profile
        self.size = size
        self.mean, self.std, self.input_scale = mean, std, input_scale
        if profile == "custom" and (len(mean) != 3 or len(std) != 3
                or not np.isfinite([*mean, *std, input_scale]).all() or min(std) <= 0 or input_scale <= 0):
            raise ValueError("Custom normalization requires three finite means, positive standard deviations and a positive input scale.")

    def transform(self, pil_image: Image.Image) -> torch.Tensor:
        """Convert and resize an image, then return a float32 NCHW tensor."""
        if not isinstance(pil_image, Image.Image):
            raise ValueError("Input must be a Pillow image.")

        image = pil_image.convert("RGB")
        if self.resize_backend == "opencv_linear":
            import cv2
            # Albumentations Resize uses OpenCV. Keep the uint8 rounding before float().
            image_array = cv2.resize(np.asarray(image), self.size, interpolation=cv2.INTER_LINEAR).astype(np.float32)
        else:
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
        elif self.profile == "custom":
            tensor.mul_(self.input_scale)
            mean = torch.tensor(self.mean, dtype=torch.float32).view(1, 3, 1, 1)
            std = torch.tensor(self.std, dtype=torch.float32).view(1, 3, 1, 1)
            tensor.sub_(mean).div_(std)

        return tensor
