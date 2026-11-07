"""Read physical sampling without treating print DPI or magnification as MPP."""

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image

from core.model_profile import file_sha256, positive_pair


@dataclass(frozen=True)
class ImageCalibration:
    mpp: tuple[float, float] | None
    source: str
    image_size: tuple[int, int]
    image_sha256: str | None = None

    def to_dict(self):
        return {"mpp": list(self.mpp) if self.mpp else None, "source": self.source,
                "image_size": list(self.image_size), "image_sha256": self.image_sha256}


def _metadata_calibration(data, size):
    if not isinstance(data, dict):
        raise ValueError("Image calibration must be a JSON object.")
    if data.get("schema") == "zypath.roi-calibration.v1":
        if data.get("image_role") != "native_resolution_roi" or data.get("resize_applied") is not False:
            raise ValueError("This calibration does not describe an unresized native ROI.")
        expected_size = data.get("roi_size_px")
        checksum = data.get("roi_png_sha256")
        source = "native ROI / " + str(data.get("calibration_source", "declared metadata"))
    elif data.get("schema") == "zypath.image-calibration.v1":
        expected_size = data.get("image_size_px")
        checksum = data.get("image_sha256")
        source = "image calibration / " + str(data.get("calibration_source", "declared metadata"))
    else:
        raise ValueError("Unsupported image calibration schema.")
    if list(size) != expected_size:
        raise ValueError("Calibration dimensions do not match this image; it may have been resized.")
    mpp = positive_pair(data.get("pixel_size_um"), "Image MPP")
    if checksum is not None and (not isinstance(checksum, str) or len(checksum) != 64
            or any(c not in "0123456789abcdef" for c in checksum)):
        raise ValueError("Invalid calibration image SHA-256.")
    return ImageCalibration(mpp, source, tuple(size), checksum)


def _ome_calibration(description, size):
    if "<OME" not in description and ":OME" not in description:
        return None
    if len(description) > 1024 * 1024 or "<!ENTITY" in description or "<!DOCTYPE" in description:
        raise ValueError("Unsupported OME metadata document.")
    try:
        root = ET.fromstring(description)
    except ET.ParseError as error:
        raise ValueError("Invalid OME physical-size metadata.") from error
    images = [element for element in root if element.tag.split("}")[-1] == "Image"]
    # Do not borrow calibration from a later series whose dimensions happen to match.
    pixels = next((e for e in images[0] if e.tag.split("}")[-1] == "Pixels"), None) if images else None
    if pixels is None:
        return None
    if (pixels.get("SizeX"), pixels.get("SizeY")) != tuple(str(n) for n in size):
        raise ValueError("OME calibration does not describe the first image series.")
    if pixels.get("PhysicalSizeX") is None or pixels.get("PhysicalSizeY") is None:
        return None
    units = {"µm": 1.0, "μm": 1.0, "um": 1.0, "nm": .001, "mm": 1000.0}
    try:
        values = tuple(float(pixels.get("PhysicalSize" + axis)) * units[pixels.get("PhysicalSize" + axis + "Unit", "µm")]
                       for axis in ("X", "Y"))
    except (ValueError, KeyError) as error:
        raise ValueError("Unsupported OME physical size or unit.") from error
    return ImageCalibration(positive_pair(values, "OME MPP"), "OME PhysicalSizeX/Y", tuple(size))


def read_image_calibration(path, decoder="pillow_rgb", *, verify=False, manual_mpp=None):
    """Return calibration in the selected decoder's image coordinates.

    GUI inspection reads headers only. Inference verifies any sidecar checksum
    and binds a snapshot to the actual input bytes. No pixel-based MPP guess is made.
    """
    path = Path(path)
    before = path.stat()
    with Image.open(path) as image:
        size = image.size
        orientation = image.getexif().get(274, 1)
        embedded = image.info.get("zypath.calibration")
        description = str(getattr(image, "tag_v2", {}).get(270, ""))
    candidates = []
    if embedded is not None:
        if not isinstance(embedded, str) or len(embedded) > 128 * 1024:
            raise ValueError("Invalid embedded image calibration.")
        candidates.append(_metadata_calibration(json.loads(embedded), size))
    sidecar = path.with_name(path.name + ".calibration.json")
    if sidecar.is_file():
        if sidecar.stat().st_size > 128 * 1024:
            raise ValueError("Image calibration exceeds 128 KiB.")
        data = json.loads(sidecar.read_text(encoding="utf-8-sig"))
        candidate = _metadata_calibration(data, size)
        if candidate.image_sha256 is None:
            raise ValueError("External image calibration requires an image SHA-256.")
        candidates.append(candidate)
    ome = _ome_calibration(description, size) if description else None
    if ome:
        candidates.append(ome)
    elif description.startswith("Aperio"):
        match = re.search(r"(?:\||\n)\s*MPP\s*=\s*([0-9.eE+-]+)(?:\s|\||$)", description)
        if match:
            value = float(match.group(1))
            candidates.append(ImageCalibration(positive_pair((value, value), "Aperio MPP"), "Aperio MPP", tuple(size)))
    if any(not all(math.isclose(a, b, rel_tol=1e-6) for a, b in zip(c.mpp, candidates[0].mpp)) for c in candidates[1:]):
        raise ValueError("Conflicting image MPP metadata; correct the calibration before analysis.")
    checksum = file_sha256(path) if verify else None
    for candidate in candidates:
        if verify and candidate.image_sha256 is not None and candidate.image_sha256 != checksum:
            raise ValueError("Calibration SHA-256 does not match this image; it may have been edited.")
    # IMREAD_COLOR applies EXIF orientation; the recorded Pillow decoder does not.
    swapped = decoder == "opencv_color" and orientation in (5, 6, 7, 8)
    decoded_size = tuple(reversed(size)) if swapped else tuple(size)
    if manual_mpp is not None:
        # Manual values explicitly refer to the displayed/decoded image axes.
        result = ImageCalibration(positive_pair(manual_mpp, "Manual image MPP"), "manual entry", decoded_size, checksum)
    elif candidates:
        result = ImageCalibration(tuple(reversed(candidates[0].mpp)) if swapped else candidates[0].mpp,
                                  candidates[0].source, decoded_size, checksum)
    else:
        result = ImageCalibration(None, "not recorded", decoded_size, checksum)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("The image changed while its calibration was being read.")
    return result


def recorded_calibration(path, data, decoder):
    """Reuse an immutable history snapshot, ignoring subsequently edited sidecars."""
    if not isinstance(data, dict) or not isinstance(data.get("source"), str):
        raise ValueError("Invalid recorded image calibration.")
    with Image.open(path) as image:
        size = image.size
        if decoder == "opencv_color" and image.getexif().get(274, 1) in (5, 6, 7, 8):
            size = tuple(reversed(size))
    checksum = file_sha256(path)
    if data.get("image_sha256") != checksum or list(size) != data.get("image_size"):
        raise ValueError("The input image differs from the recorded analysis; start a new run.")
    values = data.get("mpp")
    return ImageCalibration(positive_pair(values, "Recorded image MPP") if values is not None else None,
                            data["source"], size, checksum)
