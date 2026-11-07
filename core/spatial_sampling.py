"""Translate model fields in micrometres into source-image sampling plans."""

import math


def source_tile_size(profile, calibration):
    if profile is None or profile.field_um is None:
        raise ValueError("This model has no established physical field. Use pixel mode or supply a documented model input profile.")
    if calibration is None or calibration.mpp is None:
        raise ValueError("Image MPP is unknown. Supply calibrated metadata or enter the image's known MPP.")
    if profile.input_scope != "patch":
        raise ValueError("Physical tile matching requires a patch-based model input profile.")
    ideal = tuple(field / mpp for field, mpp in zip(profile.field_um, calibration.mpp))
    if any(not math.isfinite(n) or n < .5 or n > 100000 for n in ideal):
        raise ValueError("The requested physical field cannot be represented within source-tile limits.")
    result = tuple(max(1, round(n)) for n in ideal)
    if result[0] * result[1] > 25_000_000:
        raise ValueError("The calibrated source tile exceeds 25 million pixels; check MPP and the model field.")
    return result


def scale_description(context):
    if not isinstance(context, dict):
        return "Source MPP unconfirmed."
    calibration = context.get("calibration", {})
    mpp = calibration.get("mpp")
    if not mpp:
        return "Source MPP unconfirmed. Pixel mode."
    prefix = f"Source MPP: {mpp[0]:g} x {mpp[1]:g} um/px."
    if context.get("mode") == "physical":
        field = context.get("actual_field_um", [])
        detail = (f" Matched field: {field[0]:g} x {field[1]:g} um." if len(field) == 2 else " Physical scale matched.")
        if any(context.get("source_coarser_than_model", [])):
            detail += " Source sampling is coarser than the model reference; resizing cannot recover missing detail."
        return prefix + detail
    return prefix + " Pixel mode; physical scale not matched."
