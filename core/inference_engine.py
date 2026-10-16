"""Run model inference in a worker thread or directly for testing."""

import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import torch
import numpy as np
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from core.model_loader import LoadedModel, ModelLoader, ModelValidationError
from core.output_parser import OutputParser
from core.preprocessor import Preprocessor
from core.classification_tiles import ClassificationTileSpec, predict_classification_tiles
from core.large_image_segmentation import (
    SEGMENTATION_COLORS,
    SEGMENTATION_LABELS,
    make_overlay,
    predict_large_image,
)


logger = logging.getLogger(__name__)


class InferenceEngine(QThread):
    """Run inference on a background thread and emit its result or error."""

    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(int, int)
    status_changed = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(
        self,
        model_path: str | Path,
        image_path: str | Path,
        task_type: Literal["classification", "segmentation"],
        class_labels: list[str] | None = None,
        preprocess_profile: str | None = None,
        tile: int = 1000,
        stride: int = 512,
        input_size: int = 224,
        loaded_model: LoadedModel | None = None,
        parent: object | None = None,
        classification_tile_metadata: dict | None = None,
        classification_mode: str = "single_image",
        classification_resize_backend: str = "pillow_bilinear",
    ) -> None:
        """Create an inference worker for one model and image."""
        if task_type not in ("classification", "segmentation"):
            raise ValueError("Task type must be 'classification' or 'segmentation'.")
        super().__init__(parent)
        self.model_path = Path(model_path)
        self.image_path = Path(image_path)
        self.task_type = task_type
        self.class_labels = list(class_labels) if class_labels is not None else None
        self.preprocess_profile = preprocess_profile
        self.tile = tile
        self.stride = stride
        self.input_size = input_size
        self._cancel_event = threading.Event()
        self.loaded_model = loaded_model
        if classification_mode not in ("single_image", "tiled_analysis"):
            raise ValueError("Unknown classification mode.")
        self.classification_mode = classification_mode
        self.classification_resize_backend = classification_resize_backend
        self.classification_tile_metadata = classification_tile_metadata

    def cancel(self) -> None:
        """Request cooperative cancellation after the current tile."""
        self._cancel_event.set()

    def run_pipeline(self) -> dict[str, object]:
        """Load, validate, and run inference without starting the thread."""
        started_at = time.perf_counter()
        logger.info(
            "Inference pipeline started: model=%s image=%s task=%s",
            self.model_path,
            self.image_path,
            self.task_type,
        )
        loaded_model = self.loaded_model or ModelLoader().load_with_info(self.model_path)
        logger.info("Inference model ready: source=%s", loaded_model.source_format)
        validation = ModelLoader.validate(loaded_model.model)
        if validation.task_type != self.task_type:
            expected_task = validation.task_type.capitalize()
            raise ModelValidationError(
                f"This model produces {validation.task_type} output; "
                f"please select {expected_task}."
            )

        profile = (
            self.preprocess_profile
            if self.preprocess_profile is not None
            else loaded_model.preprocess_profile or "imagenet"
        )
        labels = self._select_class_labels(loaded_model, validation.num_classes)

        try:
            with Image.open(self.image_path) as source_image:
                source_image.seek(0)
                original_image = source_image.convert("RGB").copy()
            logger.info("Input image opened: size=%s", original_image.size)
        except (OSError, ValueError) as error:
            raise ValueError(
                "The image could not be opened. Choose a valid image file."
            ) from error

        tile_spec = None
        tile_metadata = self.classification_tile_metadata or loaded_model.classification_tiles
        if self.task_type == "classification" and self.classification_mode == "tiled_analysis":
            if tile_metadata is None:
                raise ModelValidationError("Tiled analysis requires explicit original-image tile dimensions.")
            if loaded_model.classes != labels or loaded_model.preprocess_profile != profile:
                raise ModelValidationError("Classification tiles require matching model class and preprocessing metadata.")
            tile_spec = ClassificationTileSpec.from_metadata(
                tile_metadata, labels, profile
            )
            self.status_changed.emit("Running classification tiles...")
            result = predict_classification_tiles(
                original_image, loaded_model.model, tile_spec,
                progress_callback=self.progress_changed.emit,
                cancel_callback=self._cancel_event.is_set,
            )
            result.update({
                "task_type": "classification", "classification_mode": "tiled_analysis", "model_path": str(self.model_path),
                "model_name": self.model_path.name, "image_path": str(self.image_path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "preprocess_profile": profile, "source_format": loaded_model.source_format,
                "class_labels": labels, "elapsed_seconds": time.perf_counter() - started_at,
            })
            result["classification_analysis"].update({
                "model_path": str(self.model_path.resolve()), "model_name": self.model_path.name,
                "source_format": loaded_model.source_format, "timestamp": result["timestamp"],
            })
            return result
        input_tensor = None
        if not (
            self.task_type == "segmentation"
            and loaded_model.source_format == "upernet_state_dict"
        ):
            preprocessor = (Preprocessor(profile=profile, size=tile_spec.input_size)
                            if tile_spec else Preprocessor(profile=profile))
            if self.task_type == "classification":
                preprocessor.resize_backend = self.classification_resize_backend
            input_tensor = preprocessor.transform(original_image)
        if self.task_type == "classification":
            print(f"Input shape: {tuple(input_tensor.shape)}", flush=True)
            print(f"Input dtype: {input_tensor.dtype}", flush=True)
            print(
                f"Input range: {float(input_tensor.min().item())} - "
                f"{float(input_tensor.max().item())}",
                flush=True,
            )
            print(f"Inference model: {self.model_path}", flush=True)
            with torch.inference_mode():
                output_tensor = ModelLoader.forward(loaded_model.model, input_tensor)
        result: dict[str, object] = {
            "task_type": self.task_type,
            "model_path": str(self.model_path),
            "model_name": self.model_path.name,
            "image_path": str(self.image_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "preprocess_profile": profile,
            "source_format": loaded_model.source_format,
            "class_labels": labels,
        }

        if self.task_type == "classification":
            result["classification_mode"] = "single_image"
            result["classification_parameters"] = {
                "mode": "single_image", "classification_mode": "single_image",
                "resize_backend": self.classification_resize_backend,
                "preprocess": profile, "input_size": [224, 224],
            }
            parsed_result = OutputParser.parse_classification(output_tensor, labels)
            result.update(parsed_result)
            print("Classification probabilities:", flush=True)
            for class_label, probability in zip(labels, parsed_result["probabilities"]):
                print(f"{class_label}: {float(probability):.10f}", flush=True)
            print(f"Predicted class: {parsed_result['label']}", flush=True)
            print(f"Confidence: {float(parsed_result['confidence']):.10f}", flush=True)
            print(
                f"Probability sum: {sum(parsed_result['probabilities']):.10f}",
                flush=True,
            )
        else:
            if loaded_model.source_format == "upernet_state_dict":
                self.status_changed.emit("Running large-image segmentation...")
                logger.info(
                    "Large-image inference started: tile=%s stride=%s input=%s",
                    self.tile,
                    self.stride,
                    self.input_size,
                )
                segmentation = predict_large_image(
                    original_image,
                    loaded_model.model,
                    torch.device("cpu"),
                    tile=self.tile,
                    stride=self.stride,
                    input_size=self.input_size,
                    progress_callback=lambda done, total: self.progress_changed.emit(done, total),
                    cancel_callback=self._cancel_event.is_set,
                )
                labels = list(SEGMENTATION_LABELS)
                legend_items = [
                    (label, SEGMENTATION_COLORS[index])
                    for index, label in enumerate(labels)
                ]
                result.update(segmentation)
                result["class_labels"] = labels
                result["legend_items"] = legend_items
                result["overlay"] = make_overlay(
                    original_image,
                    segmentation["color_mask"],
                    alpha=0.2,
                )
                result["blended"] = result["overlay"]
                result["overlay_alpha"] = 0.2
                result["device"] = "cpu"
            else:
                with torch.inference_mode():
                    output_tensor = ModelLoader.forward(loaded_model.model, input_tensor)
                parsed_result = OutputParser.parse_segmentation(
                    output_tensor,
                    original_image.size,
                    class_labels=labels,
                    class_colors=SEGMENTATION_COLORS if len(labels) == 9 else None,
                )
                result.update(parsed_result)
                mask = parsed_result["mask"]
                result["mask"] = mask.astype(np.uint8)
                result["color_mask"] = Image.fromarray(
                    np.asarray(SEGMENTATION_COLORS, dtype=np.uint8)[result["mask"]],
                    mode="RGB",
                )
                result["counts"] = np.bincount(
                    result["mask"].ravel(), minlength=len(SEGMENTATION_COLORS)
                )
                result["blended"] = OutputParser.blend_overlay(
                    original_image,
                    parsed_result["overlay"],
                )

        result["elapsed_seconds"] = time.perf_counter() - started_at
        logger.info(
            "Inference result prepared: task=%s elapsed=%.3fs",
            self.task_type,
            result["elapsed_seconds"],
        )
        return result

    def run(self) -> None:
        """Run the pipeline and emit one success or error signal."""
        try:
            self.result_ready.emit(self.run_pipeline())
        except InterruptedError:
            logger.info("Inference cancelled: model=%s", self.model_path)
            self.cancelled.emit()
        except (ModelValidationError, ValueError) as error:
            logger.exception("Inference failed with a handled validation error")
            self.error_occurred.emit(str(error))
        except Exception:
            logger.exception("Unexpected error while running inference")
            self.error_occurred.emit(
                "Unexpected error while running inference. Details were written to the log."
            )

    def _select_class_labels(
        self,
        loaded_model: LoadedModel,
        num_classes: int,
    ) -> list[str]:
        if self.class_labels is not None:
            labels = self.class_labels
        elif loaded_model.classes is not None:
            labels = loaded_model.classes
        else:
            labels = [f"Class {index}" for index in range(num_classes)]

        if len(labels) != num_classes:
            raise ModelValidationError(
                f"This model has {num_classes} classes, but {len(labels)} class labels were provided. "
                "Use one label for each model class."
            )
        return list(labels)


class ModelValidationThread(QThread):
    """Load and validate a large model without blocking the GUI thread."""

    validation_ready = pyqtSignal(object, object)
    validation_error = pyqtSignal(str)

    def __init__(self, model_path: str | Path, parent: object | None = None) -> None:
        super().__init__(parent)
        self.model_path = Path(model_path)

    def run(self) -> None:
        try:
            logger.info("Model validation thread started: %s", self.model_path)
            loaded_model = ModelLoader().load_with_info(self.model_path)
            validation = ModelLoader.validate(loaded_model.model)
            logger.info("Model validation thread finished: %s", self.model_path)
            self.validation_ready.emit(loaded_model, validation)
        except (ModelValidationError, ValueError) as error:
            logger.exception("Model validation failed: %s", self.model_path)
            self.validation_error.emit(str(error))
        except Exception:
            logger.exception("Unexpected error while validating a model")
            self.validation_error.emit(
                "Unexpected error while validating the model. Details were written to the log."
            )
