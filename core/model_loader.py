"""Load models and validate their inference outputs."""

from dataclasses import dataclass
from collections.abc import Mapping
import logging
import json
import sys
from pathlib import Path
from typing import Literal

import torch
from torch import nn
from torchvision import models
from utils.paths import resource_path


logger = logging.getLogger(__name__)


def _upernet_config_source():
    """Frozen releases carry the same verified config instead of a user cache."""
    if getattr(sys, "frozen", False):
        directory = resource_path("models/upernet-config")
        if not (directory / "config.json").is_file():
            raise ModelValidationError("The packaged UPerNet configuration is missing. Reinstall the complete application folder.")
        return str(directory)
    return "openmmlab/upernet-swin-base"


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
    source_format: Literal["torchscript", "module", "checkpoint", "upernet_state_dict"]
    classes: list[str] | None
    arch: str | None
    preprocess_profile: Literal["raw255", "imagenet"] | None
    classification_tiles: dict | None = None
    input_profile: object | None = None
    model_sha256: str | None = None
    profile_file_sha256: str | None = None


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
        logger.info("Model load started: %s", model_path)
        self._validate_file(model_path)
        source_identity = model_path.stat()

        tile_metadata = None
        embedded_profile = None
        try:
            model = torch.jit.load(str(model_path), map_location="cpu")
            source_format: Literal["torchscript", "module", "checkpoint"] = "torchscript"
            classes = None
            arch = None
            preprocess_profile = None
        except Exception:
            try:
                loaded_object = self._load_torch_object(model_path)
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
            elif isinstance(loaded_object, Mapping):
                tile_metadata = loaded_object.get("classification_tiles")
                embedded_profile = loaded_object.get("zypath_input_profile")
                if self._looks_like_upernet_state_dict(loaded_object):
                    model = self._build_upernet(loaded_object)
                    source_format = "upernet_state_dict"
                    classes = None
                    arch = "upernet-swin-base"
                    preprocess_profile = "imagenet"
                    model.eval()
                    logger.info("UPerNet model load finished: %s", model_path)
                    return self._attach_input_profile(LoadedModel(
                        model=model,
                        source_format=source_format,
                        classes=classes,
                        arch=arch,
                        preprocess_profile=preprocess_profile,
                    ), model_path, embedded_profile, source_identity)
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

        logger.info("Model load finished: %s source=%s", model_path, source_format)
        sidecar = model_path.with_suffix(model_path.suffix + ".classification-tiles.json")
        if tile_metadata is None and sidecar.is_file():
            try:
                tile_metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                raise ModelValidationError("Classification tile metadata could not be read.") from error
        if tile_metadata is not None:
            from core.classification_tiles import ClassificationTileSpec
            try:
                if not isinstance(tile_metadata, dict) or classes is None:
                    raise ValueError("Classification tiles require checkpoint class metadata.")
                ClassificationTileSpec.from_metadata(tile_metadata, classes, preprocess_profile)
            except ValueError as error:
                raise ModelValidationError(str(error)) from error
        return self._attach_input_profile(LoadedModel(
            model=model,
            source_format=source_format,
            classes=classes,
            arch=arch,
            preprocess_profile=preprocess_profile,
            classification_tiles=tile_metadata,
        ), model_path, embedded_profile, source_identity)

    @staticmethod
    def _attach_input_profile(loaded, path, embedded=None, source_identity=None):
        from core.model_profile import ModelInputProfile, file_sha256, known_profile, read_profile
        try:
            loaded.model_sha256 = file_sha256(path)
            sidecar = path.with_name(path.name + ".zypath-model.json")
            sidecar_before = sidecar.stat() if sidecar.is_file() else None
            profile = read_profile(sidecar, loaded.model_sha256) if sidecar.is_file() else None
            loaded.profile_file_sha256 = file_sha256(sidecar) if sidecar.is_file() else None
            sidecar_after = sidecar.stat() if sidecar.is_file() else None
            if ((sidecar_before is None) != (sidecar_after is None)
                    or (sidecar_before is not None and (sidecar_before.st_size, sidecar_before.st_mtime_ns) != (sidecar_after.st_size, sidecar_after.st_mtime_ns))):
                raise ValueError("Model input profile changed while loading.")
            if embedded is not None:
                if not isinstance(embedded, dict):
                    raise ValueError("Embedded model input profile must be an object.")
                # An embedded profile cannot contain its own enclosing file's checksum.
                data = {**embedded, "model_sha256": loaded.model_sha256}
                inside = ModelInputProfile.from_dict(data, source="checkpoint")
                if profile and {**profile.to_dict(), "source": ""} != {**inside.to_dict(), "source": ""}:
                    raise ValueError("External and embedded model input profiles conflict.")
                profile = profile or inside
            known = known_profile(loaded.model_sha256, upernet=loaded.source_format == "upernet_state_dict")
            if known and profile and known.source == "verified_crc_checkpoint" and any(
                getattr(known, key) != getattr(profile, key)
                for key in ("task_type", "classes", "input_size", "normalization", "image_decoder", "resize_backend", "field_um")
            ):
                raise ValueError("Profile conflicts with the verified CRC checkpoint's input requirements.")
            loaded.input_profile = profile or known
            if loaded.input_profile:
                if loaded.classes is not None and tuple(loaded.classes) != loaded.input_profile.classes:
                    raise ValueError("Model profile class order conflicts with checkpoint metadata.")
                loaded.classes = list(loaded.input_profile.classes)
            after = path.stat()
            if source_identity is not None and (source_identity.st_size, source_identity.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError("Model file changed while loading; select it again.")
            return loaded
        except (OSError, TypeError, ValueError) as error:
            raise ModelValidationError(f"Model input profile: {error}") from error

    def load(self, path: str | Path) -> nn.Module:
        """Load a model and return only the model object."""
        return self.load_with_info(path).model

    @staticmethod
    def validate_loaded(loaded: LoadedModel) -> ValidationResult:
        """Validate the output and the labels that will be used for inference."""
        profile = getattr(loaded, "input_profile", None)
        if (profile is None and getattr(loaded, "source_format", None) == "upernet_state_dict"
                and getattr(loaded, "model_sha256", None) is not None):
            raise ModelValidationError("This UPerNet state dictionary requires its own model input profile. Class names and preprocessing cannot be inferred from an unrecognized weight file; use Model input to import its specification.")
        result = (ModelLoader.validate(loaded.model, input_profile=profile)
                  if profile is not None else ModelLoader.validate(loaded.model))
        if profile is not None and profile.task_type != result.task_type:
            raise ModelValidationError("The model output task conflicts with its input profile.")
        if loaded.classes is not None and len(loaded.classes) != result.num_classes:
            raise ModelValidationError(
                f"The model declares {len(loaded.classes)} class labels but outputs "
                f"{result.num_classes} classes. Correct the checkpoint class metadata "
                "before using this model."
            )
        return result

    @staticmethod
    def validate(model: nn.Module, *, input_profile=None) -> ValidationResult:
        """Run a small probe and identify the model's output task and shape."""
        logger.info("Model validation started: %s", type(model).__name__)
        if not isinstance(model, nn.Module):
            raise ModelValidationError("The model must be a PyTorch neural network module.")

        try:
            with torch.inference_mode():
                if input_profile is None:
                    probe = torch.rand((1, 3, 224, 224), dtype=torch.float32)
                else:
                    from PIL import Image
                    probe = input_profile.preprocessor().transform(Image.new("RGB", input_profile.input_size, (128, 128, 128)))
                output = ModelLoader.forward(model, probe)
        except RuntimeError as error:
            raise ModelValidationError(
                "The model could not process the configured RGB test image (224 by 224 without a profile). "
                "It must accept input shaped (1, 3, H, W)."
            ) from error
        except Exception as error:
            raise ModelValidationError(
                "The model failed on the configured RGB test image (224 by 224 without a profile). "
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
            if output.shape[1] < 2:
                raise ModelValidationError(
                    "Classification output must have shape (1, C) with at least two class logits. "
                    "Single-logit binary classifiers are not supported; use a model with two output logits."
                )
            task_type: Literal["classification", "segmentation"] = "classification"
            num_classes = output.shape[1]
        elif output.ndim == 4:
            if min(output.shape[1:]) < 1:
                raise ModelValidationError(
                    "Segmentation output must contain classes and pixels in shape (1, C, H, W)."
                )
            if output.shape[1] == 1:
                raise ModelValidationError("Single-logit binary segmentation requires an explicit sigmoid/threshold adapter; a one-channel argmax is not supported.")
            task_type = "segmentation"
            num_classes = output.shape[1]
        else:
            raise ModelValidationError(
                f"This model outputs {output.ndim} dimensions; ZY-Path expects "
                "(1, C) or (1, C, H, W)."
            )

        result = ValidationResult(
            task_type=task_type,
            num_classes=num_classes,
            output_shape=tuple(output.shape),
        )
        logger.info(
            "Model validation finished: task=%s classes=%s output=%s",
            result.task_type,
            result.num_classes,
            result.output_shape,
        )
        return result

    @staticmethod
    def forward(model: nn.Module, inputs: torch.Tensor) -> torch.Tensor:
        """Run a model with either positional or Hugging Face pixel-value input."""
        try:
            output = model(inputs)
        except TypeError:
            output = model(pixel_values=inputs)
        logits = output if isinstance(output, torch.Tensor) else getattr(output, "logits", None)
        if not isinstance(logits, torch.Tensor):
            raise ModelValidationError(
                "The model must return a tensor or an object with a logits tensor."
            )
        return logits

    @staticmethod
    def _load_torch_object(model_path: Path) -> object:
        try:
            return torch.load(str(model_path), map_location="cpu", weights_only=True)
        except Exception:
            try:
                return torch.load(str(model_path), map_location="cpu", weights_only=False)
            except Exception as error:
                raise ModelValidationError(
                    "The model file could not be loaded. Use a valid TorchScript model, "
                    "saved PyTorch module, or supported checkpoint."
                ) from error

    @staticmethod
    def _looks_like_upernet_state_dict(checkpoint: Mapping[object, object]) -> bool:
        if not checkpoint or not all(
            isinstance(key, str) and isinstance(value, torch.Tensor)
            for key, value in checkpoint.items()
        ):
            return False
        keys = set(checkpoint)
        required = {
            "backbone.embeddings.patch_embeddings.projection.weight",
            "backbone.encoder.layers.0.blocks.0.attention.self.query.weight",
            "decode_head.classifier.weight",
            "decode_head.classifier.bias",
            "auxiliary_head.classifier.weight",
            "auxiliary_head.classifier.bias",
        }
        if not required.issubset(keys):
            return False
        decode_weight = checkpoint["decode_head.classifier.weight"]
        auxiliary_weight = checkpoint["auxiliary_head.classifier.weight"]
        return (
            tuple(decode_weight.shape) == (9, 512, 1, 1)
            and tuple(checkpoint["decode_head.classifier.bias"].shape) == (9,)
            and tuple(auxiliary_weight.shape) == (9, 256, 1, 1)
            and tuple(checkpoint["auxiliary_head.classifier.bias"].shape) == (9,)
        )

    @staticmethod
    def _build_upernet(checkpoint: Mapping[object, object]) -> nn.Module:
        logger.info("UPerNet network construction started")
        try:
            from transformers import UperNetConfig, UperNetForSemanticSegmentation
        except ImportError as error:
            raise ModelValidationError(
                "UPerNet segmentation requires transformers==4.38.2. Install the project dependencies."
            ) from error

        try:
            config = UperNetConfig.from_pretrained(
                _upernet_config_source(),
                local_files_only=True,
            )
        except (OSError, ValueError) as error:
            raise ModelValidationError(
                "The verified UPerNet configuration is not available in the local Hugging Face cache. "
                "Run the verification setup once while connected, then use offline mode."
            ) from error
        labels = (
            "Exclude", "Cancerous epithelium", "Stroma", "TILs",
            "Normal epithelium", "Junk/Debris", "Blood", "Other",
            "Whitespace/Empty",
        )
        config.num_labels = len(labels)
        config.id2label = dict(enumerate(labels))
        config.label2id = {label: index for index, label in enumerate(labels)}
        model = UperNetForSemanticSegmentation(config)
        try:
            model.load_state_dict(dict(checkpoint), strict=True)
        except (RuntimeError, TypeError, ValueError) as error:
            raise ModelValidationError(
                "The UPerNet weights do not exactly match the verified Swin Base nine-class architecture."
            ) from error
        logger.info("UPerNet strict state_dict load finished")
        return model

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
            self._validate_crc_densenet_metadata(checkpoint)
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

    @staticmethod
    def _validate_crc_densenet_metadata(checkpoint: dict[str, object]) -> None:
        if "in_channels" not in checkpoint:
            return
        if checkpoint["in_channels"] != 3:
            raise ModelValidationError(
                "This DenseNet checkpoint requires in_channels=3."
            )
        if checkpoint.get("num_classes") != 9:
            raise ModelValidationError(
                "This CRC DenseNet checkpoint requires num_classes=9."
            )
        if checkpoint.get("classes") != [
            "ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM"
        ]:
            raise ModelValidationError(
                "This CRC DenseNet checkpoint has an unsupported class order."
            )
        if checkpoint.get("preprocess") != "raw255":
            raise ModelValidationError(
                "This CRC DenseNet checkpoint requires raw255 preprocessing."
            )
        if checkpoint.get("input_size") not in ([224, 224], (224, 224)):
            raise ModelValidationError(
                "This CRC DenseNet checkpoint requires input_size=[224, 224]."
            )

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
