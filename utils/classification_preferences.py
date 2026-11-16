"""Upgrade classification defaults once without rewriting saved analyses."""

from core.classification_input import DEFAULT_CLASSIFICATION_RESIZE


def ensure_training_resize_default(settings) -> None:
    """Move the former Pillow default to the documented CRC validation resize.

    Users can select legacy Pillow afterwards. Existing source-tile dimensions
    and every history record are kept; the new 224-pixel default only fills an
    absent preference or is chosen explicitly with Reset Classification.
    """
    if settings.value("classification/trainingResizeDefaultApplied", False, type=bool):
        return
    if settings.value("classification/resizeBackend", "pillow_bilinear", type=str) == "pillow_bilinear":
        settings.setValue("classification/resizeBackend", DEFAULT_CLASSIFICATION_RESIZE)
    settings.setValue("classification/trainingResizeDefaultApplied", True)
    settings.sync()
