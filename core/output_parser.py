"""Convert model outputs into display-ready results."""

from collections.abc import Sequence

import numpy as np
import torch
from PIL import Image


class OutputParser:
    """Parse classification and segmentation model outputs."""

    _DEFAULT_COLORS = (
        (230, 25, 75),
        (60, 180, 75),
        (0, 130, 200),
        (245, 130, 48),
        (145, 30, 180),
        (70, 240, 240),
        (240, 50, 230),
        (210, 245, 60),
        (250, 190, 212),
        (0, 128, 128),
        (220, 190, 255),
        (170, 110, 40),
        (255, 250, 200),
        (128, 0, 0),
        (170, 255, 195),
        (128, 128, 0),
    )

    @staticmethod
    def parse_classification(
        output_tensor: torch.Tensor,
        class_labels: Sequence[str],
    ) -> dict[str, object]:
        """Return the predicted label and softmax probabilities."""
        if (
            output_tensor.ndim != 2
            or output_tensor.shape[0] != 1
            or output_tensor.shape[1] < 1
        ):
            raise ValueError("Classification output must have shape (1, C).")
        if isinstance(class_labels, (str, bytes)) or len(class_labels) != output_tensor.shape[1]:
            raise ValueError("The number of class labels must match the output classes.")

        probabilities_tensor = torch.softmax(output_tensor, dim=1)[0]
        class_index = int(torch.argmax(probabilities_tensor).item())
        probabilities = [float(value) for value in probabilities_tensor.detach().cpu().tolist()]

        return {
            "label": class_labels[class_index],
            "class_index": class_index,
            "confidence": probabilities[class_index],
            "probabilities": probabilities,
        }

    @staticmethod
    def parse_segmentation(
        output_tensor: torch.Tensor,
        original_size: tuple[int, int],
        class_labels: Sequence[str] | None = None,
        class_colors: Sequence[tuple[int, int, int]] | None = None,
    ) -> dict[str, object]:
        """Return a resized class mask, RGBA overlay, and class legend."""
        if (
            output_tensor.ndim != 4
            or output_tensor.shape[0] != 1
            or output_tensor.shape[1] < 1
            or output_tensor.shape[2] < 1
            or output_tensor.shape[3] < 1
        ):
            raise ValueError("Segmentation output must have shape (1, C, H, W).")
        if (
            not isinstance(original_size, tuple)
            or len(original_size) != 2
            or any(
                not isinstance(dimension, int)
                or isinstance(dimension, bool)
                or dimension <= 0
                for dimension in original_size
            )
        ):
            raise ValueError("Original size must contain positive integers (width, height).")

        num_classes = output_tensor.shape[1]
        if class_labels is not None and (
            isinstance(class_labels, (str, bytes)) or len(class_labels) != num_classes
        ):
            raise ValueError("The number of class labels must match the output classes.")

        colors = OutputParser._validate_colors(class_colors)
        mask = output_tensor.detach().argmax(dim=1)[0].cpu().numpy().astype(np.int32)
        mask_image = Image.fromarray(mask)
        resized_mask = np.asarray(
            mask_image.resize(original_size, Image.Resampling.NEAREST),
            dtype=np.int64,
        )
        classes_present = [int(value) for value in np.unique(resized_mask)]

        rgba_array = np.empty((*resized_mask.shape, 4), dtype=np.uint8)
        legend_items: list[tuple[str, tuple[int, int, int]]] = []
        for class_index in classes_present:
            color = colors[class_index % len(colors)]
            rgba_array[resized_mask == class_index] = (*color, 102)
            label = (
                class_labels[class_index]
                if class_labels is not None
                else f"Class {class_index}"
            )
            legend_items.append((label, color))

        return {
            "mask": resized_mask,
            "overlay": Image.fromarray(rgba_array, mode="RGBA"),
            "classes_present": classes_present,
            "legend_items": legend_items,
        }

    @staticmethod
    def blend_overlay(
        original_pil: Image.Image,
        overlay_pil: Image.Image,
    ) -> Image.Image:
        """Composite an RGBA overlay over an image and return an RGB image."""
        if not isinstance(original_pil, Image.Image) or not isinstance(overlay_pil, Image.Image):
            raise ValueError("Both inputs must be Pillow images.")
        if original_pil.size != overlay_pil.size:
            raise ValueError("The original image and overlay must have the same size.")

        original_rgb = original_pil.convert("RGB")
        overlay_rgba = overlay_pil.convert("RGBA")
        return Image.alpha_composite(original_rgb.convert("RGBA"), overlay_rgba).convert("RGB")

    @staticmethod
    def _validate_colors(
        class_colors: Sequence[tuple[int, int, int]] | None,
    ) -> tuple[tuple[int, int, int], ...]:
        if class_colors is None:
            return OutputParser._DEFAULT_COLORS
        if isinstance(class_colors, (str, bytes)) or not class_colors:
            raise ValueError("Class colors must contain at least one RGB color.")

        colors: list[tuple[int, int, int]] = []
        for color in class_colors:
            if (
                not isinstance(color, (tuple, list))
                or len(color) != 3
                or any(
                    not isinstance(channel, int)
                    or isinstance(channel, bool)
                    or not 0 <= channel <= 255
                    for channel in color
                )
            ):
                raise ValueError("Each class color must be an RGB tuple with values from 0 to 255.")
            colors.append((color[0], color[1], color[2]))
        return tuple(colors)