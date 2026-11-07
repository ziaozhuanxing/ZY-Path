import hashlib
import json

from PIL import Image, PngImagePlugin, TiffImagePlugin
import pytest

from core.image_calibration import read_image_calibration, recorded_calibration


def calibrated_png(path, *, mpp=(.252, .252), size=(444, 444), sidecar=True):
    data = {"schema": "zypath.roi-calibration.v1", "image_role": "native_resolution_roi",
            "resize_applied": False, "roi_size_px": list(size), "pixel_size_um": list(mpp),
            "calibration_source": "test calibrated fixture"}
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("zypath.calibration", json.dumps(data))
    Image.new("RGB", size).save(path, pnginfo=metadata)
    if sidecar:
        data["roi_png_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        path.with_name(path.name + ".calibration.json").write_text(json.dumps(data))
    return data


def test_roi_embedded_metadata_and_sidecar_are_consistent_and_bound_to_pixels(tmp_path):
    path = tmp_path / "roi.png"
    data = calibrated_png(path)
    result = read_image_calibration(path, verify=True)
    assert result.mpp == (.252, .252)
    assert result.image_size == (444, 444)
    assert result.image_sha256 == data["roi_png_sha256"]
    with path.open("ab") as stream:
        stream.write(b"image changed")
    with pytest.raises(ValueError, match="SHA-256"):
        read_image_calibration(path, verify=True)


def test_conflicting_sidecar_or_resized_image_is_not_silently_accepted(tmp_path):
    path = tmp_path / "roi.png"
    data = calibrated_png(path)
    sidecar = path.with_name(path.name + ".calibration.json")
    sidecar.write_text(json.dumps({**data, "pixel_size_um": [.5, .5]}))
    with pytest.raises(ValueError, match="Conflicting"):
        read_image_calibration(path)
    sidecar.write_text(json.dumps({**data, "roi_size_px": [224, 224]}))
    with pytest.raises(ValueError, match="dimensions"):
        read_image_calibration(path)


def test_unknown_calibration_is_not_guessed_from_dpi_or_image_size(tmp_path):
    path = tmp_path / "print-resolution.png"
    Image.new("RGB", (224, 224)).save(path, dpi=(50800, 50800))
    assert read_image_calibration(path).mpp is None
    result = read_image_calibration(path, manual_mpp=(.25, .5), verify=True)
    assert result.mpp == (.25, .5)
    assert result.source == "manual entry"


def test_anisotropic_mpp_axes_follow_opencv_exif_orientation(tmp_path):
    path = tmp_path / "rotated.jpg"
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (60, 40)).save(path, exif=exif)
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_name(path.name + ".calibration.json").write_text(json.dumps({
        "schema": "zypath.image-calibration.v1", "image_size_px": [60, 40],
        "pixel_size_um": [.25, .5], "image_sha256": checksum}))
    raw = read_image_calibration(path, "pillow_rgb", verify=True)
    rotated = read_image_calibration(path, "opencv_color", verify=True)
    assert raw.image_size == (60, 40) and raw.mpp == (.25, .5)
    assert rotated.image_size == (40, 60) and rotated.mpp == (.5, .25)


def test_ome_units_and_series_identity(tmp_path):
    path = tmp_path / "physical.ome.tif"
    description = '<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"><Image><Pixels SizeX="60" SizeY="40" PhysicalSizeX="250" PhysicalSizeY="500" PhysicalSizeXUnit="nm" PhysicalSizeYUnit="nm"/></Image></OME>'
    tags = TiffImagePlugin.ImageFileDirectory_v2()
    tags[270] = description
    Image.new("RGB", (60, 40)).save(path, tiffinfo=tags)
    assert read_image_calibration(path).mpp == (.25, .5)
    tags[270] = description.replace('SizeX="60"', 'SizeX="61"')
    Image.new("RGB", (60, 40)).save(path, tiffinfo=tags)
    with pytest.raises(ValueError, match="first image series"):
        read_image_calibration(path)


def test_history_uses_recorded_calibration_not_later_sidecar_edits(tmp_path):
    path = tmp_path / "roi.png"
    calibrated_png(path)
    snapshot = read_image_calibration(path, verify=True).to_dict()
    path.with_name(path.name + ".calibration.json").write_text("a later invalid sidecar")
    result = recorded_calibration(path, snapshot, "pillow_rgb")
    assert result.mpp == (.252, .252)
    Image.new("RGB", (444, 444), (255, 0, 0)).save(path)
    with pytest.raises(ValueError, match="differs"):
        recorded_calibration(path, snapshot, "pillow_rgb")
