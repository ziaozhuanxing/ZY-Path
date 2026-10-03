"""Load models and validate their inference outputs."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import torch
from torch import nn
from torchvision import models


class ModelValidationError(Exception):
    """Raised when a model file or model output is not supported."""


@dataclass
class ValidationResult:
    """Describe the task and output shape detected for a model."""

    task_type: Literal["classification", "segmentation"]
    num_classes: int
    output_shape: tuple[int, ...]


@dataclass
class LoadedModel:
    """Hold a loaded model and optional checkpoint metadata."""

    model: nn.Module
    source_format: Literal["torchscript", "module", "checkpoint"]
    classes: list[str] | None
    arch: str | None
    preprocess_profile: Literal["raw255", "imagenet"] | None


class ModelLoader:
    """Load supported PyTorch model files and inspect their outputs."""

    MAX_FILE_BYTES = 500 * 1024 * 1024
    _ALLOWED_EXTENSIONS = {".pt", ".pth"}
    _DENSENET_KEYS = (
        "growth_rate",
        "block_config",
        "num_init_features",
        "bn_size",
        "drop_rate",
        "num_classes",
    )
    _ARCHITECTURES = {
        "resnet18": models.resnet18,
        "resnet34": models.resnet34,
        "resnet50": models.resnet50,
        "resnet101": models.resnet101,
        "densenet121": models.densenet121,
        "densenet161": models.densenet161,
        "densenet169": models.densenet169,
        "densenet201": models.densenet201,
    }

    def load_with_info(self, path: str | Path) -> LoadedModel:
        """Load a supported model file and return its available metadata."""
        model_path = Path(path)
        self._validate_file(model_path)

        try:
            model = torch.jit.load(str(model_path), map_location="cpu")
            source_format: Literal["torchscript", "module", "checkpoint"] = "torchscript"
            classes = None
            arch = None
            preprocess_profile = None
        except Exception:
            try:
                # Explicitly disable weights-only loading for supported full modules/checkpoints.
                loaded_object = torch.load(
                    str(model_path),
                    map_location="cpu",
                    weights_only=False,
                )
            except Exception as error:
                raise ModelValidationError(
                    "The model file could not be loaded. Use a valid TorchScript model, "
                    "saved PyTorch module, or supported checkpoint."
                ) from error

            if isinstance(loaded_object, nn.Module):
                model = loaded_object
                source_format = "module"
                classes = None
                arch = None
                preprocess_profile = None
            elif isinstance(loaded_object, dict):
                model, classes, arch, preprocess_profile = self._load_checkpoint(loaded_object)
                source_format = "checkpoint"
            else:
                raise ModelValidationError(
                    "The model file must contain a TorchScript model, a PyTorch module, "
                    "or a supported checkpoint dictionary."
                )

        try:
            model.eval()
        except Exception as error:
            raise ModelValidationError(
                "The loaded model could not be prepared for inference. "
                "Use a valid PyTorch model."
            ) from error

        return LoadedModel(
            model=model,
            source_format=source_format,
            classes=classes,
            arch=arch,
            preprocess_profile=preprocess_profile,
        )

    def load(self, path: str | Path) -> nn.Module:
        """Load a model and return only the model object."""
        return self.load_with_info(path).model

    @staticmethod
    def validate(model: nn.Module) -> ValidationResult:
        """Run a small probe and identify the model's output task and shape."""
        if not isinstance(model, nn.Module):
            raise ModelValidationError("The model must be a PyTorch neural network module.")

        try:
            with torch.no_grad():
                output = model(torch.rand((1, 3, 224, 224), dtype=torch.float32))
        except RuntimeError as error:
            raise ModelValidationError(
                "The model could not process a 224 by 224 RGB test image. "
                "It must accept input shaped (1, 3, H, W)."
            ) from error
        except Exception as error:
            raise ModelValidationError(
                "The model failed on a 224 by 224 RGB test image. "
                "It must accept input shaped (1, 3, H, W)."
            ) from error

        if not isinstance(output, torch.Tensor):
            raise ModelValidationError(
                "The model must return one tensor shaped (1, C) or (1, C, H, W)."
            )
        if not bool(torch.isfinite(output).all().item()):
            raise ModelValidationError(
                "The model output contains NaN or infinite values; finite logits are required."
            )
        if output.ndim == 0 or output.shape[0] != 1:
            raise ModelValidationError(
                "The model output must have batch size 1 and shape (1, C) "
                "or (1, C, H, W)."
            )

        if output.ndim == 2:
            if output.shape[1] < 1:
                raise ModelValidationError(
                    "Classification output must contain at least one class and have shape (1, C)."
                )
            task_type: Literal["classification", "segmentation"] = "classification"
            num_classes = output.shape[1]
        elif output.ndim == 4:
            if min(output.shape[1:]) < 1:
                raise ModelValidationError(
                    "Segmentation output must contain classes and pixels in shape (1, C, H, W)."
                )
            task_type = "segmentation"
            num_classes = output.shape[1]
        else:
            raise ModelValidationError(
                f"This model outputs {output.ndim} dimensions; ZY-Path expects "
                "(1, C) or (1, C, H, W)."
            )

        return ValidationResult(
            task_type=task_type,
            num_classes=num_classes,
            output_shape=tuple(output.shape),
        )

    def _validate_file(self, model_path: Path) -> None:
        if not model_path.is_file():
            raise ModelValidationError(
                "The model file could not be found. Choose an existing .pt or .pth file."
            )
        if model_path.suffix.lower() not in self._ALLOWED_EXTENSIONS:
            raise ModelValidationError(
                "Unsupported model file extension. Choose a .pt or .pth file."
            )
        try:
            file_size = model_path.stat().st_size
        except OSError as error:
            raise ModelValidationError(
                "The model file size could not be checked. Choose a readable .pt or .pth file."
            ) from error
        if file_size > self.MAX_FILE_BYTES:
            max_megabytes = self.MAX_FILE_BYTES // (1024 * 1024)
            raise ModelValidationError(
                f"The model file is larger than the {max_megabytes} MB limit. "
                "Choose a smaller .pt or .pth file."
            )

    def _load_checkpoint(
        self,
        checkpoint: dict[str, object],
    ) -> tuple[nn.Module, list[str] | None, str | None, str | None]:
        classes = self._read_classes(checkpoint)
        preprocess_profile = self._read_preprocess_profile(checkpoint)

        if "arch" in checkpoint:
            model, arch = self._build_named_architecture(checkpoint)
        else:
            model = self._build_supervisor_densenet(checkpoint)
            arch = "densenet"

        state_dict = checkpoint.get("model_dict", checkpoint.get("state_dict"))
        if state_dict is None:
            raise ModelValidationError(
                "The checkpoint is missing required weights. Include 'model_dict' or 'state_dict'."
            )
        try:
            model.load_state_dict(state_dict, strict=True)
        except Exception as error:
            raise ModelValidationError(
                "The checkpoint weights do not match the declared model architecture. "
                "Use weights from the same model."
            ) from error

        return model, classes, arch, preprocess_profile

    def _build_named_architecture(
        self,
        checkpoint: dict[str, object],
    ) -> tuple[nn.Module, str]:
        arch = checkpoint.get("arch")
        if not isinstance(arch, str) or arch not in self._ARCHITECTURES:
            allowed = ", ".join(self._ARCHITECTURES)
            raise ModelValidationError(
                f"Unsupported checkpoint architecture. Choose one of: {allowed}."
            )

        missing_keys = [key for key in ("num_classes",) if key not in checkpoint]
        if missing_keys:
            raise ModelValidationError(
                "The checkpoint is missing required keys: " + ", ".join(missing_keys) + "."
            )
        num_classes = checkpoint["num_classes"]
        if not isinstance(num_classes, int) or isinstance(num_classes, bool) or num_classes < 1:
            raise ModelValidationError(
                "Checkpoint 'num_classes' must be a positive integer."
            )
        try:
            model = self._ARCHITECTURES[arch](weights=None, num_classes=num_classes)
        except Exception as error:
            raise ModelValidationError(
                "The checkpoint architecture could not be created with its class count. "
                "Check the architecture and num_classes values."
            ) from error
        return model, arch

    @staticmethod
    def _build_supervisor_densenet(checkpoint: dict[str, object]) -> nn.Module:
        required_keys = (*ModelLoader._DENSENET_KEYS,)
        missing_keys = [key for key in required_keys if key not in checkpoint]
        if missing_keys:
            raise ModelValidationError(
                "The DenseNet checkpoint is missing required keys: "
                + ", ".join(missing_keys)
                + "."
            )

        num_classes = checkpoint["num_classes"]
        if not isinstance(num_classes, int) or isinstance(num_classes, bool) or num_classes < 1:
            raise ModelValidationError(
                "Checkpoint 'num_classes' must be a positive integer."
            )
        try:
            return models.DenseNet(
                growth_rate=checkpoint["growth_rate"],
                block_config=tuple(checkpoint["block_config"]),
                num_init_features=checkpoint["num_init_features"],
                bn_size=checkpoint["bn_size"],
                drop_rate=checkpoint["drop_rate"],
                num_classes=num_classes,
            )
        except Exception as error:
            raise ModelValidationError(
                "The DenseNet checkpoint settings are invalid. "
                "Check its growth_rate, block_config, feature, and class values."
            ) from error

    @staticmethod
    def _read_classes(checkpoint: dict[str, object]) -> list[str] | None:
        classes = checkpoint.get("classes")
        if classes is None:
            return None
        if not isinstance(classes, (list, tuple)) or not all(
            isinstance(label, str) for label in classes
        ):
            raise ModelValidationError(
                "Checkpoint 'classes' must be a list of class names or be omitted."
            )
        return list(classes)

    @staticmethod
    def _read_preprocess_profile(checkpoint: dict[str, object]) -> str | None:
        if "preprocess" not in checkpoint:
            return None
        profile = checkpoint["preprocess"]
        if profile not in ("raw255", "imagenet"):
            raise ModelValidationError(
                "Checkpoint 'preprocess' must be 'raw255' or 'imagenet'."
            )
        return profile