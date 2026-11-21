"""Bind previews, calibration, saved predictions and exports to the same image."""

from pathlib import Path

from core.classification_input import decoded_image_size, load_rgb_image, CLASSIFICATION_DECODERS
from core.model_profile import file_sha256


def image_checksum(path, *, check_cancelled=None):
    """Hash a stable file, without allocating its decoded pixels."""
    path = Path(path)
    try:
        before = path.stat()
        checksum = file_sha256(path, check_cancelled=check_cancelled) if check_cancelled else file_sha256(path)
        after = path.stat()
    except InterruptedError:
        raise
    except OSError as error:
        raise ValueError("The image could not be found or read. Reopen an existing image before running analysis.") from error
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError("The image changed while being read. Reopen the image and confirm its scale again.")
    return checksum


def validate_identity(identity):
    if not isinstance(identity, dict):
        raise ValueError("The saved image identity is invalid.")
    checksum = identity.get("image_sha256")
    size = identity.get("image_size")
    decoder = identity.get("image_decoder")
    if (not isinstance(checksum, str) or len(checksum) != 64
            or any(c not in "0123456789abcdef" for c in checksum)
            or not isinstance(size, (list, tuple)) or len(size) != 2
            or any(type(n) is not int or n <= 0 for n in size)
            or decoder not in CLASSIFICATION_DECODERS):
        raise ValueError("The saved image identity is invalid.")
    return {"image_sha256": checksum, "image_size": list(size), "image_decoder": decoder}


def analysis_identity(analysis):
    """Read new identities and older calibrated records; never invent a legacy hash."""
    if "source_image" in analysis:
        return validate_identity(analysis["source_image"])
    calibration = (analysis.get("spatial_context") or {}).get("calibration") or {}
    if calibration.get("image_sha256") is not None:
        return validate_identity({"image_sha256": calibration["image_sha256"],
            "image_size": calibration.get("image_size"),
            "image_decoder": analysis.get("image_decoder", (analysis.get("input_profile") or {}).get("image_decoder", "pillow_rgb"))})
    return None


def verify_image_source(path, identity, *, check_cancelled=None):
    if identity is None:
        raise ValueError("This older record has no image checksum. Only its stored result can be verified as the saved artifact; run a new analysis to create an original-image comparison.")
    identity = validate_identity(identity)
    if image_checksum(path, check_cancelled=check_cancelled) != identity["image_sha256"]:
        raise ValueError("The original image has changed. The saved result has been kept; reopen the image and confirm its scale before running a new analysis.")
    if list(decoded_image_size(path, identity["image_decoder"])) != identity["image_size"]:
        raise ValueError("The original image dimensions no longer match the saved analysis.")
    return identity


def load_verified_image(path, identity=None, *, decoder="pillow_rgb", require_identity=False, check_cancelled=None):
    """Return pixels and their identity, rejecting changes around decoding."""
    if identity is not None or require_identity:
        identity = verify_image_source(path, identity, check_cancelled=check_cancelled)
        decoder = identity["image_decoder"]
        checksum = identity["image_sha256"]
    else:
        checksum = image_checksum(path, check_cancelled=check_cancelled)
    image = load_rgb_image(path, decoder)
    if image_checksum(path, check_cancelled=check_cancelled) != checksum:
        raise ValueError("The image changed while being decoded. Reopen the image and confirm its scale again.")
    current = {"image_sha256": checksum, "image_size": list(image.size), "image_decoder": decoder}
    if identity is not None and current != identity:
        raise ValueError("The image reader or dimensions differ from the saved analysis.")
    return image, current
