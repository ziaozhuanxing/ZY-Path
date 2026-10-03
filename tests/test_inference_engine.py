import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest
import torch
from PIL import Image
from torch import nn

import core.inference_engine as inference_engine_module
from core.inference_engine import InferenceEngine
from core.model_loader import LoadedModel, ModelValidationError
from core.preprocessor import Preprocessor as RealPreprocessor


class TinyClassifier(nn.Module):
    def __init__(self, num_classes: int = 3) -> None:
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Linear(3, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.pool(inputs).flatten(1))


class TinySegmenter(nn.Module):
    def __init__(self, num_classes: int = 4) -> None:
        super().__init__()
        self.layer = nn.Conv2d(3, num_classes, kernel_size=1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.layer(inputs)


class UnexpectedOnSecondCall(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0
        self.classifier = TinyClassifier()

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        self.calls += 1
        if self.calls == 2:
            raise KeyError("secret internal detail")
        return self.classifier(inputs)


@pytest.fixture(autouse=True)
def use_one_torch_thread():
    previous_thread_count = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous_thread_count)


def save_model(path: Path, model: nn.Module) -> None:
    torch.save(model, path)


def save_image(path: Path, size: tuple[int, int] = (12, 8)) -> None:
    Image.new("RGB", size, (90, 120, 150)).save(path)


def install_loaded_model(
    monkeypatch: pytest.MonkeyPatch,
    model: nn.Module,
    classes: list[str] | None = None,
    profile: str | None = None,
) -> None:
    loaded_model = LoadedModel(
        model=model,
        source_format="module",
        classes=classes,
        arch=None,
        preprocess_profile=profile,
    )
    monkeypatch.setattr(
        inference_engine_module.ModelLoader,
        "load_with_info",
        lambda _loader, _path: loaded_model,
    )


@pytest.mark.parametrize("num_classes", [3, 9])
def test_run_pipeline_classifies_and_returns_metadata(
    tmp_path: Path,
    num_classes: int,
) -> None:
    model_path = tmp_path / "classifier.pth"
    image_path = tmp_path / "patch.png"
    save_model(model_path, TinyClassifier(num_classes))
    save_image(image_path)
    labels = [f"Tissue {index}" for index in range(num_classes)]

    result = InferenceEngine(
        model_path,
        image_path,
        "classification",
        class_labels=labels,
        preprocess_profile="raw255",
    ).run_pipeline()

    assert result["task_type"] == "classification"
    assert result["model_path"] == str(model_path)
    assert result["model_name"] == "classifier.pth"
    assert result["image_path"] == str(image_path)
    assert datetime.fromisoformat(result["timestamp"]).utcoffset().total_seconds() == 0
    assert result["preprocess_profile"] == "raw255"
    assert result["source_format"] == "module"
    assert result["class_labels"] == labels
    assert result["label"] in labels
    assert 0 <= result["class_index"] < num_classes
    assert len(result["probabilities"]) == num_classes
    assert sum(result["probabilities"]) == pytest.approx(1.0)
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["elapsed_seconds"] >= 0


def test_run_pipeline_segments_and_blends_original_image(tmp_path: Path) -> None:
    model_path = tmp_path / "segmenter.pt"
    image_path = tmp_path / "patch.png"
    save_model(model_path, TinySegmenter())
    save_image(image_path, (17, 11))

    result = InferenceEngine(model_path, image_path, "segmentation").run_pipeline()

    assert result["mask"].shape == (11, 17)
    assert result["overlay"].mode == "RGBA"
    assert result["overlay"].size == (17, 11)
    assert result["blended"].mode == "RGB"
    assert result["blended"].size == (17, 11)
    assert result["classes_present"]
    assert result["legend_items"]


@pytest.mark.parametrize(
    ("requested_profile", "model_profile", "expected_profile"),
    [
        ("raw255", "imagenet", "raw255"),
        (None, "raw255", "raw255"),
        (None, None, "imagenet"),
    ],
)
def test_preprocessing_profile_uses_requested_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    requested_profile: str | None,
    model_profile: str | None,
    expected_profile: str,
) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "patch.png"
    save_image(image_path)
    observed_profiles: list[str] = []
    install_loaded_model(monkeypatch, TinyClassifier(), profile=model_profile)

    class RecordingPreprocessor:
        def __init__(self, profile: str) -> None:
            observed_profiles.append(profile)
            self.preprocessor = RealPreprocessor(profile=profile)

        def transform(self, image: Image.Image) -> torch.Tensor:
            return self.preprocessor.transform(image)

    monkeypatch.setattr(inference_engine_module, "Preprocessor", RecordingPreprocessor)
    result = InferenceEngine(
        model_path,
        image_path,
        "classification",
        preprocess_profile=requested_profile,
    ).run_pipeline()

    assert observed_profiles == [expected_profile]
    assert result["preprocess_profile"] == expected_profile


@pytest.mark.parametrize(
    ("requested_labels", "model_labels", "expected_labels"),
    [
        (["Explicit A", "Explicit B", "Explicit C"], ["Saved A", "Saved B", "Saved C"], ["Explicit A", "Explicit B", "Explicit C"]),
        (None, ["Saved A", "Saved B", "Saved C"], ["Saved A", "Saved B", "Saved C"]),
        (None, None, ["Class 0", "Class 1", "Class 2"]),
    ],
)
def test_class_labels_use_requested_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    requested_labels: list[str] | None,
    model_labels: list[str] | None,
    expected_labels: list[str],
) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "patch.png"
    save_image(image_path)
    install_loaded_model(monkeypatch, TinyClassifier(), classes=model_labels)

    result = InferenceEngine(
        model_path,
        image_path,
        "classification",
        class_labels=requested_labels,
    ).run_pipeline()

    assert result["class_labels"] == expected_labels


def test_run_pipeline_rejects_wrong_number_of_class_labels(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "patch.png"
    save_image(image_path)
    install_loaded_model(monkeypatch, TinyClassifier())

    with pytest.raises(ModelValidationError, match="3 classes.*2 class labels"):
        InferenceEngine(
            model_path,
            image_path,
            "classification",
            class_labels=["A", "B"],
        ).run_pipeline()


@pytest.mark.parametrize(
    ("model", "task_type", "expected_task"),
    [
        (TinyClassifier(), "segmentation", "Classification"),
        (TinySegmenter(), "classification", "Segmentation"),
    ],
)
def test_run_pipeline_rejects_task_mismatch(
    tmp_path: Path,
    model: nn.Module,
    task_type: str,
    expected_task: str,
) -> None:
    model_path = tmp_path / "model.pt"
    image_path = tmp_path / "patch.png"
    save_model(model_path, model)
    save_image(image_path)

    with pytest.raises(ModelValidationError, match=f"please select {expected_task}"):
        InferenceEngine(model_path, image_path, task_type).run_pipeline()


def test_run_pipeline_rejects_unreadable_image(tmp_path: Path) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "invalid.png"
    save_model(model_path, TinyClassifier())
    image_path.write_bytes(b"not an image")

    with pytest.raises(ValueError, match="image could not be opened"):
        InferenceEngine(model_path, image_path, "classification").run_pipeline()


def test_run_pipeline_uses_first_frame_of_multipage_tiff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "pages.tiff"
    first_page = Image.new("RGB", (9, 7), (220, 10, 20))
    second_page = Image.new("RGB", (9, 7), (5, 210, 30))
    first_page.save(image_path, save_all=True, append_images=[second_page])
    observed_pixels: list[tuple[int, int, int]] = []
    install_loaded_model(monkeypatch, TinyClassifier())

    class RecordingPreprocessor:
        def __init__(self, profile: str) -> None:
            self.preprocessor = RealPreprocessor(profile=profile)

        def transform(self, image: Image.Image) -> torch.Tensor:
            observed_pixels.append(image.getpixel((0, 0)))
            return self.preprocessor.transform(image)

    monkeypatch.setattr(inference_engine_module, "Preprocessor", RecordingPreprocessor)
    result = InferenceEngine(model_path, image_path, "classification").run_pipeline()

    assert observed_pixels == [(220, 10, 20)]
    assert result["image_path"] == str(image_path)


def test_constructor_rejects_unknown_task_type(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Task type must"):
        InferenceEngine(tmp_path / "model.pt", tmp_path / "image.png", "unknown")  # type: ignore[arg-type]


def test_thread_emits_success_result(qtbot, tmp_path: Path) -> None:
    model_path = tmp_path / "classifier.pt"
    image_path = tmp_path / "patch.png"
    save_model(model_path, TinyClassifier())
    save_image(image_path)
    engine = InferenceEngine(model_path, image_path, "classification")

    with qtbot.waitSignal(engine.result_ready, timeout=5000) as signal:
        engine.start()

    assert signal.args[0]["task_type"] == "classification"
    assert signal.args[0]["model_name"] == "classifier.pt"
    engine.wait()


def test_thread_emits_friendly_error(qtbot, tmp_path: Path) -> None:
    engine = InferenceEngine(
        tmp_path / "missing.pt",
        tmp_path / "patch.png",
        "classification",
    )

    with qtbot.waitSignal(engine.error_occurred, timeout=5000) as signal:
        engine.start()

    assert "could not be found" in signal.args[0]
    engine.wait()


def test_thread_hides_unexpected_error_and_logs_details(
    qtbot,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    model_path = tmp_path / "unexpected.pt"
    image_path = tmp_path / "patch.png"
    save_model(model_path, UnexpectedOnSecondCall())
    save_image(image_path)
    engine = InferenceEngine(model_path, image_path, "classification")

    with caplog.at_level(logging.ERROR, logger=inference_engine_module.__name__):
        with qtbot.waitSignal(engine.error_occurred, timeout=5000) as signal:
            engine.start()

    assert signal.args == [
        "Unexpected error while running inference. Details were written to the log."
    ]
    assert "secret internal detail" in caplog.text
    assert "secret internal detail" not in signal.args[0]
    engine.wait()