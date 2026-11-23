"""Translate model fields in micrometres into source-image sampling plans."""

import math
from core.model_profile import positive_pair


def source_tile_size(profile, calibration):
    field_um = profile.matching_field_um if profile else None
    if field_um is None:
        raise ValueError("This model has no established physical field. Use pixel mode or supply a documented model input profile.")
    if calibration is None or calibration.mpp is None:
        raise ValueError("Image MPP is unknown. Supply calibrated metadata or enter the image's known MPP.")
    if profile.input_scope != "patch":
        raise ValueError("Physical tile matching requires a patch-based model input profile.")
    ideal = tuple(field / mpp for field, mpp in zip(field_um, calibration.mpp))
    if any(not math.isfinite(n) or n < .5 or n > 100000 for n in ideal):
        raise ValueError("The requested physical field cannot be represented within source-tile limits.")
    result = tuple(max(1, round(n)) for n in ideal)
    if result[0] * result[1] > 25_000_000:
        raise ValueError("The calibrated source tile exceeds 25 million pixels; check MPP and the model field.")
    return result


def nominal_scale_description(mpp, field, translate=None):
    text = translate or str
    try:
        x_mpp, y_mpp = positive_pair(mpp, "Nominal model input MPP")
        width, height = positive_pair(field, "Nominal model tissue field")
    except ValueError:
        return ""
    return text("Nominal model input: {x:.3f} × {y:.3f} µm/px. Nominal tissue field: {width:g} × {height:g} µm.").format(
        x=x_mpp, y=y_mpp, width=width, height=height)


def scale_description(context, translate=None):
    text = translate or str
    if not isinstance(context, dict):
        return text("Source MPP unconfirmed.")
    calibration = context.get("calibration", {})
    mpp = calibration.get("mpp")
    nominal = nominal_scale_description(context.get("nominal_model_input_mpp"),
                                       context.get("nominal_model_field_um"), text)
    if not mpp:
        return " ".join(filter(None, (text("Source MPP unconfirmed. Pixel mode."), nominal)))
    prefix = text("Source MPP: {width:g} x {height:g} um/px.").format(width=mpp[0], height=mpp[1])
    effective = context.get("effective_input_mpp")
    model_scale = ""
    if nominal:
        model_scale = " " + nominal
        if effective:
            model_scale += " " + text("Effective model input: {x:.3f} × {y:.3f} µm/px.").format(x=effective[0], y=effective[1])
    if context.get("mode") == "physical":
        field = context.get("actual_field_um", [])
        detail = (text(" Matched field: {width:g} x {height:g} um.").format(width=field[0], height=field[1])
                  if len(field) == 2 else text(" Physical scale matched."))
        if any(context.get("source_coarser_than_model", [])):
            detail += text(" Source sampling is coarser than the model reference; resizing cannot recover missing detail.")
        return prefix + detail + model_scale
    return prefix + text(" Pixel mode; physical scale not matched.") + model_scale
