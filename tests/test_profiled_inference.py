import json

import numpy as np
from PIL import Image
import pytest
import torch
from torch import nn

from core.classification_tiles import render_classification_map
from core.inference_engine import InferenceEngine
from core.large_image_segmentation import predict_large_image
from core.model_loader import LoadedModel, ModelLoader, ModelValidationError
from core.model_profile import ModelInputProfile, SCHEMA, UPERNET_SHA256, known_profile
from core.spatial_sampling import source_tile_size
from core.image_calibration import ImageCalibration


class RecordingClassifier(nn.Module):
    def __init__(self, probabilities=False):
        super().__init__()
        self.inputs = []
        self.probabilities = probabilities

    def forward(self, value):
        self.inputs.append(value.detach().clone())
        return torch.tensor([[.6, .3, .1]]) if self.probabilities else value.mean((2, 3))


class RecordingSegmenter(nn.Module):
    def __init__(self, count=3):
        super().__init__()
        self.count, self.inputs = count, []

    def forward(self, value):
        self.inputs.append(value.detach().clone())
        output = torch.zeros((value.shape[0], self.count, value.shape[2], value.shape[3]))
        output[:, 1, :, :value.shape[3] // 2] = 4
        output[:, 2 if self.count > 2 else 0, :, value.shape[3] // 2:] = 4
        return output


def make_profile(**changes):
    return ModelInputProfile.from_dict({
        "schema": SCHEMA, "model_sha256": "1" * 64, "task_type": "classification",
        "classes": ["red", "green", "blue"], "input_size": [8, 8], "normalization": "raw255",
        "input_scope": "patch", "field_um": [4, 4], "tile_size": [8, 8], "stride": [4, 4], **changes})


def engine_for(tmp_path, profile, image, model=None, **changes):
    path = tmp_path / "image.png"
    image.save(path)
    model = model or RecordingClassifier()
    loaded = LoadedModel(model, "checkpoint", list(profile.classes), "test", None, input_profile=profile)
    engine = InferenceEngine(tmp_path / "in-memory-test.pth", path, profile.task_type,
        loaded_model=loaded, classification_mode="tiled_analysis", **changes)
    return engine, model


def test_crc_example_computes444_without_assuming_other_models_share_it():
    profile = make_profile(field_um=[112, 112], input_size=[224, 224])
    calibration = ImageCalibration((.252, .252), "explicit fixture", (4440, 4440))
    assert source_tile_size(profile, calibration) == (444, 444)
    assert source_tile_size(make_profile(field_um=[500, 250]), calibration) == (1984, 992)


def test_physical_plan_is_validated_instead_of_stale_pixel_preferences(tmp_path):
    from core.classification_tiles import exploratory_metadata
    engine, _ = engine_for(tmp_path, make_profile(), Image.new("RGB", (400, 400)),
        classification_tile_metadata=exploratory_metadata(1, 1),
        input_options={"match_scale": True, "manual_mpp": [.01, .01]})
    result = engine.run_pipeline()
    assert result["classification_analysis"]["tile_size"] == [400, 400]
    assert len(result["classification_analysis"]["tiles"]) == 1


def test_physical_workload_limit_is_checked_before_decoding_pixels(tmp_path, monkeypatch):
    engine, _ = engine_for(tmp_path, make_profile(), Image.new("RGB", (101, 101)),
        input_options={"match_scale": True, "manual_mpp": [4, 4]})
    def unexpected_decode(*args):
        pytest.fail("Over-budget calibrated geometry must not decode the image")
    monkeypatch.setattr("core.profiled_inference.load_rgb_image", unexpected_decode)
    with pytest.raises(ValueError, match="10,000"):
        engine.run_pipeline()


def test_extreme_calibration_cannot_allocate_giant_reflect_padding():
    with pytest.raises(ValueError, match="25 million"):
        source_tile_size(make_profile(edge_policy="reflect"), ImageCalibration((.0001, .0001), "fixture", (1, 1)))


def test_unrotated_rectangular_overbudget_image_stops_before_model_load(tmp_path, monkeypatch):
    from core.classification_tiles import exploratory_metadata
    path = tmp_path / "wide.png"
    Image.new("RGB", (11000, 1)).save(path)
    def unexpected_load(*args):
        pytest.fail("An unrotated over-budget request must not load weights")
    monkeypatch.setattr(ModelLoader, "load_with_info", unexpected_load)
    with pytest.raises(ValueError, match="10,000"):
        InferenceEngine("unused", path, "classification", classification_mode="tiled_analysis",
            classification_tile_metadata=exploratory_metadata(1, 100)).run_pipeline()


def test_calibrated_source_field_reaches_network_with_anisotropic_geometry(tmp_path):
    engine, model = engine_for(tmp_path, make_profile(), Image.new("RGB", (32, 16), (255, 20, 10)),
        input_options={"match_scale": True, "manual_mpp": [.25, .5]})
    result = engine.run_pipeline()
    analysis = result["classification_analysis"]
    assert analysis["tile_size"] == [16, 8]
    assert len(analysis["tiles"]) == 4
    assert analysis["spatial_context"]["actual_field_um"] == [4., 4.]
    assert analysis["spatial_context"]["effective_input_mpp"] == [.5, .5]
    assert analysis["unanalysed_pixels"] == 0
    assert analysis["input_profile"]["classes"] == ["red", "green", "blue"]
    assert analysis["pixel_counts"] == [512, 0, 0]
    assert all(tuple(value.shape) == (1, 3, 8, 8) for value in model.inputs)
    assert model.inputs[-1][0, :, 0, 0].tolist() == [255, 20, 10]


def test_incomplete_physical_fields_are_excluded_not_stretched(tmp_path):
    original = Image.new("RGB", (18, 10), (255, 20, 10))
    engine, model = engine_for(tmp_path, make_profile(), original,
        input_options={"match_scale": True, "manual_mpp": [.5, .5]})
    result = engine.run_pipeline()
    analysis = result["classification_analysis"]
    assert len(analysis["tiles"]) == 2
    assert analysis["analysed_pixels"] == 128
    assert analysis["unanalysed_pixels"] == 52
    assert sum(analysis["area_ratios"]) == pytest.approx(128 / 180)
    overlay = render_classification_map(original, result["color_map"], analysis)
    assert overlay.getpixel((17, 9)) == original.getpixel((17, 9))
    assert overlay.getpixel((0, 0)) != original.getpixel((0, 0))


def test_single_image_matching_requires_one_actual_physical_field(tmp_path):
    engine, model = engine_for(tmp_path, make_profile(), Image.new("RGB", (16, 16)),
        input_options={"match_scale": True, "manual_mpp": [.5, .5]})
    engine.classification_mode = "single_image"
    with pytest.raises(ValueError, match="Single image"):
        engine.run_pipeline()
    Image.new("RGB", (8, 8)).save(engine.image_path)
    assert engine.run_pipeline()["classification_parameters"]["spatial_context"]["mode"] == "physical"


@pytest.mark.parametrize("profile,options,message", [
    (make_profile(), {"match_scale": True}, "MPP is unknown"),
    (make_profile(field_um=None), {"match_scale": True, "manual_mpp": [.5, .5]}, "no established physical field"),
    (make_profile(input_scope="image"), {"match_scale": True, "manual_mpp": [.5, .5]}, "patch-based"),
])
def test_missing_information_is_not_replaced_by_model_or_dataset_guesses(tmp_path, profile, options, message):
    engine, _ = engine_for(tmp_path, profile, Image.new("RGB", (8, 8)), input_options=options)
    with pytest.raises(ValueError, match=message):
        engine.run_pipeline()


def test_probability_outputs_are_not_softmaxed_twice(tmp_path):
    profile = make_profile(output_kind="probabilities")
    engine, _ = engine_for(tmp_path, profile, Image.new("RGB", (8, 8)), model=RecordingClassifier(True))
    result = engine.run_pipeline()
    assert result["probabilities"] == pytest.approx([.6, .3, .1])
    assert result["confidence"] == pytest.approx(.6)


def test_standard_segmentation_uses_its_own_class_count_and_calibrated_field(tmp_path):
    profile = make_profile(task_type="segmentation", input_size=[6, 4])
    engine, model = engine_for(tmp_path, profile, Image.new("RGB", (23, 17), (120, 80, 30)),
        model=RecordingSegmenter(), input_options={"match_scale": True, "manual_mpp": [.25, .5]})
    result = engine.run_pipeline()
    assert result["tile"] == [16, 8]
    assert result["stride"] == [8, 4]
    assert result["mask"].shape == (17, 23)
    assert result["counts"].sum() == 17 * 23
    assert set(np.unique(result["mask"])) == {1, 2}
    assert result["spatial_context"]["actual_field_um"] == [4., 4.]
    assert all(tuple(tensor.shape) == (1, 3, 4, 6) for tensor in model.inputs)


def test_upernet_adapter_keeps_reference_probabilities_and_mask(tmp_path):
    profile = known_profile(UPERNET_SHA256, upernet=True)
    original = Image.new("RGB", (1011, 31), (100, 60, 200))
    engine, model = engine_for(tmp_path, profile, original, model=RecordingSegmenter(9),
        input_options={"match_scale": False, "manual_mpp": [.252, .252]})
    actual = engine.run_pipeline()
    reference_model = RecordingSegmenter(9)
    expected = predict_large_image(original, reference_model, torch.device("cpu"))
    assert np.array_equal(actual["mask"], expected["mask"])
    assert torch.equal(model.inputs[-1], reference_model.inputs[-1])
    assert actual["spatial_context"]["reference_field_um"] is None
    assert actual["spatial_context"]["mode"] == "pixel"
    engine.input_options["match_scale"] = True
    with pytest.raises(ValueError, match="no established physical field"):
        engine.run_pipeline()


def test_rerun_reuses_snapshot_and_detects_profile_or_image_changes(tmp_path):
    profile = make_profile()
    engine, _ = engine_for(tmp_path, profile, Image.new("RGB", (16, 16)),
        input_options={"match_scale": True, "manual_mpp": [.5, .5]})
    first = engine.run_pipeline()
    analysis = first["classification_analysis"]
    engine.input_options = {"recorded_input_profile": analysis["input_profile"],
                            "recorded_spatial_context": analysis["spatial_context"]}
    again = engine.run_pipeline()
    assert again["classification_analysis"]["spatial_context"] == analysis["spatial_context"]
    engine.loaded_model.input_profile = make_profile(field_um=[5, 5])
    with pytest.raises(ModelValidationError, match="profile differs"):
        engine.run_pipeline()
    engine.loaded_model.input_profile = profile
    Image.new("RGB", (16, 16), (255, 0, 0)).save(engine.image_path)
    with pytest.raises(ValueError, match="input image differs"):
        engine.run_pipeline()
