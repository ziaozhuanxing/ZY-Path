"""Run model inference in a worker thread or directly for testing."""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import torch
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from core.model_loader import LoadedModel, ModelLoader, ModelValidationError
from core.output_parser import OutputParser
from core.preprocessor import Preprocessor


logger = logging.getLogger(__name__)


class InferenceEngine(QThread):
    """Run inference on a background thread and emit its result or error."""

    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        model_path: str | Path,
        image_path: str | Path,
        task_type: Literal["classification", "segmentation"],
        class_labels: list[str] | None = None,
        preprocess_profile: str | None = None,
        parent: object | None = None,
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

    def run_pipeline(self) -> dict[str, object]:
        """Load, validate, and run inference without starting the thread."""
        started_at = time.perf_counter()
        loaded_model = ModelLoader().load_with_info(self.model_path)
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
        except (OSError, ValueError) as error:
            raise ValueError(
                "The image could not be opened. Choose a valid image file."
            ) from error

        input_tensor = Preprocessor(profile=profile).transform(original_image)
        with torch.no_grad():
            output_tensor = loaded_model.model(input_tensor)

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
            parsed_result = OutputParser.parse_classification(output_tensor, labels)
            result.update(parsed_result)
        else:
            parsed_result = OutputParser.parse_segmentation(
                output_tensor,
                original_image.size,
                class_labels=labels,
            )
            result.update(parsed_result)
            result["blended"] = OutputParser.blend_overlay(
                original_image,
                parsed_result["overlay"],
            )

        result["elapsed_seconds"] = time.perf_counter() - started_at
        return result

    def run(self) -> None:
        """Run the pipeline and emit one success or error signal."""
        try:
            self.result_ready.emit(self.run_pipeline())
        except (ModelValidationError, ValueError) as error:
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