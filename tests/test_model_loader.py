from pathlib import Path

import pytest
import torch
from torch import nn
from torchvision import models

from core.model_loader import ModelLoader, ModelValidationError


class SmallClassifier(nn.Module):
    def __init__(self, num_classes: int = 3) -> None:
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Linear(3, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.pool(inputs).flatten(1))


class ThreeDimensionalOutput(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return inputs[:, 0, :1, :1]


class FailingModel(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raise RuntimeError("private internal detail")


@pytest.fixture(autouse=True)
def use_one_torch_thread() -> None:
    previous_thread_count = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous_thread_count)


def save_module(path: Path, model: nn.Module) -> None:
    torch.save(model, path)


def make_supervisor_checkpoint() -> dict[str, object]:
    model = models.DenseNet(
        growth_rate=4,
        block_config=(1, 1),
        num_init_features=8,
        bn_size=2,
        drop_rate=0.0,
        num_classes=3,
    )
    return {
        "model_dict": model.state_dict(),
        "growth_rate": 4,
        "block_config": (1, 1),
        "num_init_features": 8,
        "bn_size": 2,
        "drop_rate": 0.0,
        "num_classes": 3,
    }


def test_loads_torchscript_model_and_validates_classification(tmp_path: Path) -> None:
    model_path = tmp_path / "scripted.pt"
    model = SmallClassifier(num_classes=3).eval()
    scripted_model = torch.jit.trace(model, torch.rand((1, 3, 16, 16)))
    scripted_model.save(str(model_path))

    loaded = ModelLoader().load_with_info(model_path)
    result = ModelLoader.validate(loaded.model)

    assert loaded.source_format == "torchscript"
    assert loaded.classes is None
    assert loaded.arch is None
    assert loaded.preprocess_profile is None
    assert not loaded.model.training
    assert result.task_type == "classification"
    assert result.num_classes == 3
    assert result.output_shape == (1, 3)


def test_loads_full_module_and_accepts_uppercase_extension(tmp_path: Path) -> None:
    model_path = tmp_path / "module.PTH"
    save_module(model_path, SmallClassifier())

    loaded = ModelLoader().load_with_info(model_path)

    assert loaded.source_format == "module"
    assert not loaded.model.training
    assert ModelLoader.validate(loaded.model).num_classes == 3
    assert isinstance(ModelLoader().load(model_path), nn.Module)


def test_loads_supervisor_densenet_checkpoint(tmp_path: Path) -> None:
    model_path = tmp_path / "supervisor.pth"
    torch.save(make_supervisor_checkpoint(), model_path)

    loaded = ModelLoader().load_with_info(model_path)
    result = ModelLoader.validate(loaded.model)

    assert loaded.source_format == "checkpoint"
    assert loaded.arch == "densenet"
    assert loaded.classes is None
    assert loaded.preprocess_profile is None
    assert not loaded.model.training
    assert result.task_type == "classification"
    assert result.num_classes == 3


def test_loads_named_resnet_checkpoint_with_metadata(tmp_path: Path) -> None:
    model_path = tmp_path / "resnet18.pth"
    source_model = models.resnet18(weights=None, num_classes=9)
    torch.save(
        {
            "arch": "resnet18",
            "num_classes": 9,
            "model_dict": source_model.state_dict(),
            "classes": [f"Class {index}" for index in range(9)],
            "preprocess": "raw255",
        },
        model_path,
    )

    loaded = ModelLoader().load_with_info(model_path)
    result = ModelLoader.validate(loaded.model)

    assert loaded.source_format == "checkpoint"
    assert loaded.arch == "resnet18"
    assert loaded.classes == [f"Class {index}" for index in range(9)]
    assert loaded.preprocess_profile == "raw255"
    assert not loaded.model.training
    assert result.task_type == "classification"
    assert result.num_classes == 9
    assert result.output_shape == (1, 9)


def test_validates_segmentation_model(tmp_path: Path) -> None:
    model_path = tmp_path / "segmenter.pt"
    save_module(model_path, nn.Conv2d(3, 5, kernel_size=1))

    result = ModelLoader.validate(ModelLoader().load(model_path))

    assert result.task_type == "segmentation"
    assert result.num_classes == 5
    assert result.output_shape == (1, 5, 224, 224)


def test_rejects_missing_model_file(tmp_path: Path) -> None:
    with pytest.raises(ModelValidationError, match="could not be found"):
        ModelLoader().load(tmp_path / "missing.pt")


def test_rejects_unsupported_extension(tmp_path: Path) -> None:
    model_path = tmp_path / "model.bin"
    model_path.write_bytes(b"not a model")

    with pytest.raises(ModelValidationError, match=r"\.pt or \.pth"):
        ModelLoader().load(model_path)


def test_rejects_file_over_configured_size_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "too-large.pt"
    model_path.write_bytes(b"123456")
    monkeypatch.setattr(ModelLoader, "MAX_FILE_BYTES", 5)

    with pytest.raises(ModelValidationError, match="larger than the 0 MB limit"):
        ModelLoader().load(model_path)


def test_rejects_corrupt_model_file_with_friendly_message(tmp_path: Path) -> None:
    model_path = tmp_path / "corrupt.pt"
    model_path.write_bytes(b"this is not a model")

    with pytest.raises(ModelValidationError, match="could not be loaded") as error:
        ModelLoader().load(model_path)

    assert "private" not in str(error.value)


def test_rejects_checkpoint_missing_required_keys(tmp_path: Path) -> None:
    model_path = tmp_path / "incomplete.pth"
    torch.save({"growth_rate": 4, "num_classes": 3}, model_path)

    with pytest.raises(ModelValidationError, match="block_config") as error:
        ModelLoader().load(model_path)

    assert "num_init_features" in str(error.value)
    assert "bn_size" in str(error.value)
    assert "drop_rate" in str(error.value)


def test_rejects_architecture_outside_allowlist(tmp_path: Path) -> None:
    model_path = tmp_path / "unsupported-architecture.pth"
    torch.save(
        {"arch": "made_up", "num_classes": 3, "state_dict": {}},
        model_path,
    )

    with pytest.raises(ModelValidationError, match="Unsupported checkpoint architecture"):
        ModelLoader().load(model_path)


def test_rejects_invalid_preprocess_profile(tmp_path: Path) -> None:
    checkpoint = make_supervisor_checkpoint()
    checkpoint["preprocess"] = "unknown"
    model_path = tmp_path / "bad-preprocess.pth"
    torch.save(checkpoint, model_path)

    with pytest.raises(ModelValidationError, match="raw255.*imagenet"):
        ModelLoader().load(model_path)


def test_validate_rejects_three_dimensional_output() -> None:
    with pytest.raises(ModelValidationError, match="outputs 3 dimensions"):
        ModelLoader.validate(ThreeDimensionalOutput())


def test_validate_rejects_runtime_error_without_exposing_details() -> None:
    with pytest.raises(ModelValidationError, match="could not process") as error:
        ModelLoader.validate(FailingModel())

    assert "private internal detail" not in str(error.value)


def test_validate_rejects_non_finite_output() -> None:
    model = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(), nn.Linear(3, 2))
    with torch.no_grad():
        model[-1].weight.fill_(float("inf"))

    with pytest.raises(ModelValidationError, match="NaN or infinite"):
        ModelLoader.validate(model)