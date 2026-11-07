"""Declarative input contracts, independent of model weights and image sources."""

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path


SCHEMA = "zypath.model-profile.v1"
CRC_SHA256 = "8f89bd825641fba276066b54432b5d73a62b11ed6c0d70bb94c9f0bc7e2fe325"
# The user's native Windows resource manifests on 27 Oct and 2 Nov agree on
# this file identity. It establishes the resource, not training MPP or accuracy.
UPERNET_SHA256 = "b4d8956856800fc44b274244713494f63e2791cd31a1b07b1d5223870b408486"
MAX_PROFILE_BYTES = 128 * 1024


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dimensions(value, name, maximum=8192):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(type(n) is not int or not 1 <= n <= maximum for n in value)):
        raise ValueError(f"{name} must contain two integers from 1 to {maximum} (width, height).")
    return tuple(value)


def positive_pair(value, name):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(isinstance(n, bool) or not isinstance(n, (int, float))
                   or not math.isfinite(n) or n <= 0 for n in value)):
        raise ValueError(f"{name} must contain two finite positive values (X, Y).")
    return tuple(float(n) for n in value)


def palette(count):
    # Multiplication by an odd number permutes 24-bit RGB values without collisions.
    return tuple(tuple((((i + 1) * 0x9E3779) & 0xFFFFFF) >> shift & 255
                       for shift in (16, 8, 0)) for i in range(count))


@dataclass(frozen=True)
class ModelInputProfile:
    model_sha256: str
    task_type: str
    classes: tuple[str, ...]
    input_size: tuple[int, int] = (224, 224)
    normalization: str = "imagenet"
    image_decoder: str = "pillow_rgb"
    resize_backend: str = "pillow_bilinear"
    input_scope: str = "image"
    field_um: tuple[float, float] | None = None
    tile_size: tuple[int, int] = (224, 224)
    stride: tuple[int, int] = (224, 224)
    edge_policy: str = "skip"
    pixel_edge_policy: str = "crop_then_resize"
    output_kind: str = "logits"
    colors: tuple[tuple[int, int, int], ...] = ()
    mean: tuple[float, ...] = ()
    std: tuple[float, ...] = ()
    input_scale: float = 1.0
    adapter: str = "standard"
    source: str = "sidecar"
    note: str = ""

    @classmethod
    def from_dict(cls, data, *, expected_hash=None, source="sidecar"):
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            raise ValueError("Unsupported model input profile schema.")
        allowed = set(cls.__dataclass_fields__) | {"schema"}
        if set(data) - allowed:
            raise ValueError("Unknown model profile fields: " + ", ".join(sorted(set(data) - allowed)))
        values = {k: v for k, v in data.items() if k not in ("schema", "source")}
        checksum = values.get("model_sha256", "")
        if (not isinstance(checksum, str) or len(checksum) != 64
                or any(c not in "0123456789abcdef" for c in checksum)):
            raise ValueError("Model profile requires the model file's lowercase SHA-256.")
        if expected_hash is not None and checksum != expected_hash:
            raise ValueError("Model profile SHA-256 does not match this model file.")
        if values.get("task_type") not in ("classification", "segmentation"):
            raise ValueError("Model profile must declare classification or segmentation.")
        labels = values.get("classes")
        if (not isinstance(labels, (list, tuple)) or not 2 <= len(labels) <= 65536
                or any(not isinstance(s, str) or not s.strip() or len(s) > 256 for s in labels)
                or len(set(labels)) != len(labels)):
            raise ValueError("Provide 2 to 65536 distinct ordered class labels.")
        values["classes"] = tuple(labels)
        for name in ("input_size", "tile_size", "stride"):
            if name in values:
                values[name] = dimensions(values[name], name, 8192 if name == "input_size" else 100000)
        if values.get("field_um") is not None:
            values["field_um"] = positive_pair(values["field_um"], "Physical field in micrometres")
        for name, choices in (
            ("normalization", ("raw255", "imagenet", "custom", "embedded")),
            ("image_decoder", ("pillow_rgb", "opencv_color")),
            ("resize_backend", ("pillow_bilinear", "opencv_linear")),
            ("input_scope", ("image", "patch")),
            ("edge_policy", ("skip", "reflect", "crop_then_resize")),
            ("pixel_edge_policy", ("skip", "reflect", "crop_then_resize")),
            ("output_kind", ("logits", "probabilities")),
            ("adapter", ("standard", "upernet_reference")),
        ):
            if name in values and values[name] not in choices:
                raise ValueError(f"Unsupported {name} in model profile.")
        for name in ("mean", "std"):
            if name in values:
                vector = values[name]
                if (not isinstance(vector, (list, tuple)) or len(vector) not in (0, 3)
                        or any(isinstance(n, bool) or not isinstance(n, (int, float))
                               or not math.isfinite(n) or (name == "std" and n <= 0) for n in vector)):
                    raise ValueError(f"{name} must contain three finite values (positive for std).")
                values[name] = tuple(vector)
        scale = values.get("input_scale", 1.0)
        if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
            raise ValueError("Input scale must be finite and positive.")
        if values.get("normalization") == "custom" and (len(values.get("mean", ())) != 3 or len(values.get("std", ())) != 3):
            raise ValueError("Custom normalization requires three means and standard deviations.")
        if values.get("normalization") != "custom" and (values.get("mean") or values.get("std") or scale != 1.0):
            raise ValueError("Mean, std and input_scale are only configurable for custom normalization.")
        colors = values.get("colors")
        if colors is None or colors == [] or colors == ():
            colors = palette(len(labels))
        if (not isinstance(colors, (list, tuple)) or len(colors) != len(labels) or any(not isinstance(c, (list, tuple)) or len(c) != 3
                or any(type(n) is not int or not 0 <= n <= 255 for n in c) for c in colors)
                or len(set(tuple(c) for c in colors)) != len(colors)):
            raise ValueError("Provide one distinct RGB colour per model class.")
        values["colors"] = tuple(tuple(c) for c in colors)
        if not isinstance(values.get("note", ""), str) or len(values.get("note", "")) > 2000:
            raise ValueError("Model profile note must be text of at most 2000 characters.")
        profile = cls(**values, source=source)
        if profile.input_size[0] * profile.input_size[1] > 4_194_304:
            raise ValueError("Network inputs above four million pixels are not supported.")
        if profile.task_type == "segmentation" and len(labels) * profile.input_size[0] * profile.input_size[1] * 4 > 256 * 1024 * 1024:
            raise ValueError("The declared segmentation output exceeds the validation memory budget.")
        if profile.tile_size[0] * profile.tile_size[1] > 25_000_000:
            raise ValueError("Source tiles above 25 million pixels are not supported.")
        if profile.task_type == "segmentation" and profile.edge_policy not in ("skip", "reflect"):
            raise ValueError("Tiled segmentation supports explicit skip or reflect edges.")
        if any(step > tile for step, tile in zip(profile.stride, profile.tile_size)):
            raise ValueError("Stride must not exceed the corresponding tile dimension.")
        if profile.adapter == "upernet_reference" and (
            profile.task_type != "segmentation" or len(labels) != 9
            or profile.input_size != (224, 224) or profile.normalization != "imagenet"
            or profile.resize_backend != "pillow_bilinear" or profile.image_decoder != "pillow_rgb"
            or profile.tile_size != (1000, 1000) or profile.stride != (512, 512)
            or profile.field_um is not None or profile.output_kind != "logits"
            or profile.edge_policy != "reflect"
        ):
            raise ValueError("The UPerNet reference adapter retains the supplied 1000/512/224 pixel pipeline; its physical field is not established.")
        return profile

    def to_dict(self):
        data = {name: getattr(self, name) for name in self.__dataclass_fields__}
        return json.loads(json.dumps({"schema": SCHEMA, **data}))

    def preprocessor(self):
        from core.preprocessor import Preprocessor
        return Preprocessor(self.normalization, self.input_size, self.resize_backend,
                            mean=self.mean, std=self.std, input_scale=self.input_scale)


def read_profile(path, expected_hash):
    path = Path(path)
    if path.stat().st_size > MAX_PROFILE_BYTES:
        raise ValueError("Model input profile exceeds 128 KiB.")
    profile = ModelInputProfile.from_dict(json.loads(path.read_text(encoding="utf-8-sig")), expected_hash=expected_hash)
    validate_known_contract(profile)
    return profile


def validate_known_contract(profile):
    if profile.model_sha256 == CRC_SHA256:
        known = known_profile(CRC_SHA256)
        if any(getattr(known, key) != getattr(profile, key)
               for key in ("task_type", "classes", "input_size", "normalization", "image_decoder", "resize_backend", "field_um", "input_scope", "output_kind")):
            raise ValueError("Profile conflicts with the verified CRC checkpoint's input requirements.")


def known_profile(checksum, *, upernet=False):
    if checksum == CRC_SHA256:
        from core.classification_tiles import CLASSIFICATION_COLORS, CLASSIFICATION_LABELS
        return ModelInputProfile.from_dict({
            "schema": SCHEMA, "model_sha256": checksum, "task_type": "classification",
            "classes": list(CLASSIFICATION_LABELS), "normalization": "raw255",
            "image_decoder": "opencv_color", "resize_backend": "opencv_linear",
            "input_scope": "patch", "field_um": [112.0, 112.0],
            "colors": [list(c) for c in CLASSIFICATION_COLORS],
            "note": "CRC training validation: 224 px at nominal 0.5 um/px. Stain normalization is not performed by this profile.",
        }, source="verified_crc_checkpoint")
    if upernet and checksum == UPERNET_SHA256:
        from core.large_image_segmentation import SEGMENTATION_LABELS, SEGMENTATION_COLORS
        return ModelInputProfile.from_dict({
            "schema": SCHEMA, "model_sha256": checksum, "task_type": "segmentation",
            "classes": list(SEGMENTATION_LABELS), "adapter": "upernet_reference",
            "input_scope": "patch", "tile_size": [1000, 1000], "stride": [512, 512],
            "edge_policy": "reflect", "pixel_edge_policy": "reflect",
            "colors": [list(c) for c in SEGMENTATION_COLORS],
            "note": "Supplied inference notebook. No confirmed physical field or MPP target; no physical resampling is applied.",
        }, source="upernet_reference_code")
    return None
