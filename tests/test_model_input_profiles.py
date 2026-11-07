"""Verify input contracts using temporary models, not clinical accuracy claims."""

import json

import numpy as np
from PIL import Image
import pytest
import torch
from torch import nn

from core.model_loader import ModelLoader, ModelValidationError
from core.model_profile import CRC_SHA256, UPERNET_SHA256, ModelInputProfile, SCHEMA, file_sha256, known_profile, palette


class RectangularClassifier(nn.Module):
    def forward(self, value):
        if value.shape[2:] != (48, 64):
            raise RuntimeError("This test model requires a 64 x 48 boundary tensor")
        return value.mean((2, 3))


def profile_data(checksum="1" * 64, **overrides):
    return {"schema": SCHEMA, "model_sha256": checksum, "task_type": "classification",
            "classes": ["first", "second", "third"], "input_size": [64, 48],
            "normalization": "raw255", "input_scope": "patch", "field_um": [32, 24], **overrides}


def test_profile_input_boundary_supports_non224_and_ordered_classes(tmp_path):
    path = tmp_path / "rectangular.pth"
    torch.save(RectangularClassifier(), path)
    with pytest.raises(ModelValidationError, match="configured RGB"):
        ModelLoader.validate_loaded(ModelLoader().load_with_info(path))
    data = profile_data(file_sha256(path))
    path.with_name(path.name + ".zypath-model.json").write_text(json.dumps(data))
    loaded = ModelLoader().load_with_info(path)
    validation = ModelLoader.validate_loaded(loaded)
    assert validation.num_classes == 3
    assert loaded.classes == data["classes"]
    assert loaded.input_profile.input_size == (64, 48)
    assert loaded.input_profile.field_um == (32., 24.)


def test_profile_for_different_weights_cannot_be_applied(tmp_path):
    path = tmp_path / "rectangular.pth"
    torch.save(RectangularClassifier(), path)
    path.with_name(path.name + ".zypath-model.json").write_text(json.dumps(profile_data()))
    with pytest.raises(ModelValidationError, match="SHA-256"):
        ModelLoader().load_with_info(path)


def test_editing_profile_after_validation_requires_revalidation(tmp_path):
    from core.inference_engine import InferenceEngine
    path = tmp_path / "rectangular.pth"
    torch.save(RectangularClassifier(), path)
    sidecar = path.with_name(path.name + ".zypath-model.json")
    sidecar.write_text(json.dumps(profile_data(file_sha256(path))))
    loaded = ModelLoader().load_with_info(path)
    image = tmp_path / "input.png"
    Image.new("RGB", (64, 48)).save(image)
    sidecar.write_text(json.dumps(profile_data(file_sha256(path), field_um=[64, 48])))
    with pytest.raises(ModelValidationError, match="changed after validation"):
        InferenceEngine(path, image, "classification", loaded_model=loaded).run_pipeline()


@pytest.mark.parametrize("overrides", [
    {"field_um": [0, 10]}, {"field_um": [float("nan"), 10]},
    {"classes": ["same", "same"]}, {"input_size": [True, 224]},
    {"input_size": [8192, 8192]}, {"normalization": "guess"},
    {"normalization": "custom"}, {"normalization": "embedded", "mean": [0, 0, 0]},
    {"input_scale": float("inf")}, {"resize_inside_model": True},
    {"tile_size": [100, 100], "stride": [101, 100]},
    {"colors": [[1, 2, 3]] * 3}, {"output_kind": "sigmoid"},
    {"tile_size": [100000, 100000]}, {"colors": 12},
])
def test_invalid_or_unsupported_contract_is_rejected(overrides):
    with pytest.raises(ValueError):
        ModelInputProfile.from_dict(profile_data(**overrides))


def test_embedded_normalization_is_not_applied_twice():
    data = profile_data(normalization="embedded")
    profile = ModelInputProfile.from_dict(data)
    actual = profile.preprocessor().transform(Image.new("RGB", (64, 48), (10, 100, 250)))
    assert actual[0, :, 0, 0].tolist() == [10., 100., 250.]
    custom = ModelInputProfile.from_dict(profile_data(normalization="custom", input_scale=.01,
        mean=[0, .5, 1], std=[1, 2, 4]))
    value = custom.preprocessor().transform(Image.new("RGB", (64, 48), (10, 100, 250)))
    assert value[0, :, 0, 0].tolist() == pytest.approx([.1, .25, .375])


def test_only_verified_crc_weights_get_the_crc_physical_field():
    assert known_profile("0" * 64) is None
    profile = known_profile(CRC_SHA256)
    assert profile.field_um == (112., 112.)
    assert profile.normalization == "raw255"
    assert profile.image_decoder == "opencv_color"
    assert profile.resize_backend == "opencv_linear"
    assert len(set(palette(2000))) == 2000


def test_upernet_reference_contains_no_assumed_mpp():
    assert known_profile("0" * 64, upernet=True) is None
    profile = known_profile(UPERNET_SHA256, upernet=True)
    assert profile.field_um is None
    assert profile.tile_size == (1000, 1000)
    assert profile.stride == (512, 512)
    assert profile.input_size == (224, 224)
    assert profile.edge_policy == "reflect"
    assert "0.5" not in json.dumps(profile.to_dict())
    with pytest.raises(ValueError, match="physical field is not established"):
        ModelInputProfile.from_dict({**profile.to_dict(), "field_um": [500, 500]})


def test_local_upernet_weights_do_not_inherit_the_builtin_tissue_contract():
    from core.model_loader import LoadedModel
    loaded = LoadedModel(nn.Conv2d(3, 9, 1), "upernet_state_dict", None, "upernet-swin-base", "imagenet",
                         model_sha256="0" * 64)
    with pytest.raises(ModelValidationError, match="requires its own model input profile"):
        ModelLoader.validate_loaded(loaded)


def test_single_logit_segmentation_is_not_misinterpreted_as_one_class_argmax():
    class SingleLogit(nn.Module):
        def forward(self, value):
            return value[:, :1]
    with pytest.raises(ModelValidationError, match="sigmoid/threshold"):
        ModelLoader.validate(SingleLogit())
