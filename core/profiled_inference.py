"""Execute a declared model contract using per-image calibrated geometry."""

from datetime import datetime, timezone
import time

import numpy as np
from PIL import Image
import torch

from core.classification_input import load_rgb_image
from core.classification_tiles import ClassificationTileSpec, predict_classification_tiles, validate_classification_workload
from core.image_calibration import read_image_calibration, recorded_calibration
from core.large_image_segmentation import predict_large_image, make_overlay, tile_positions
from core.model_loader import ModelLoader, ModelValidationError
from core.model_profile import file_sha256
from core.output_parser import OutputParser
from core.spatial_sampling import source_tile_size


MAX_FUSION_BYTES = 512 * 1024 * 1024


def _segmentation_tiles(image, loaded, profile, tile, stride, engine):
    """Fuse model probabilities on a bounded grid, independently of tissue labels."""
    width, height = image.size
    tw, th = tile
    iw, ih = profile.input_size
    if profile.edge_policy == "skip" and (width < tw or height < th):
        raise ValueError("No complete segmentation field fits in this image.")
    xs = tile_positions(max(width, tw), tw, stride[0])
    ys = tile_positions(max(height, th), th, stride[1])
    total = len(xs) * len(ys)
    if total > 10000:
        raise ValueError("Segmentation exceeds 10,000 processing regions; select a smaller image region.")
    sx, sy = iw / tw, ih / th
    low_w, low_h = round(xs[-1] * sx) + iw, round(ys[-1] * sy) + ih
    count = len(profile.classes)
    if low_w * low_h * (count + 1) * 4 > MAX_FUSION_BYTES:
        raise ValueError("Segmentation probability fusion exceeds 512 MiB; select a smaller image region.")
    sums = np.zeros((count, low_h, low_w), np.float32)
    weights = np.zeros((low_h, low_w), np.float32)
    window = np.outer(np.hanning(ih + 2)[1:-1], np.hanning(iw + 2)[1:-1]).astype(np.float32) + 1e-3
    preprocessor = profile.preprocessor()
    done = 0
    with torch.inference_mode():
        for y in ys:
            for x in xs:
                engine._check_cancelled()
                patch = image.crop((x, y, min(width, x + tw), min(height, y + th)))
                if patch.size != (tw, th):
                    patch = Image.fromarray(np.pad(np.asarray(patch.convert("RGB")),
                        ((0, th - patch.height), (0, tw - patch.width), (0, 0)), mode="reflect"))
                output = ModelLoader.forward(loaded.model, preprocessor.transform(patch))
                if output.ndim != 4 or output.shape[0] != 1 or output.shape[1] != count:
                    raise ModelValidationError("Segmentation output does not match its declared class count.")
                probs = OutputParser.probabilities(output, profile.output_kind)
                if tuple(probs.shape[2:]) != (ih, iw):
                    probs = torch.nn.functional.interpolate(probs, size=(ih, iw), mode="bilinear", align_corners=False)
                probabilities = probs[0].cpu().numpy()
                ly, lx = round(y * sy), round(x * sx)
                sums[:, ly:ly + ih, lx:lx + iw] += probabilities * window
                weights[ly:ly + ih, lx:lx + iw] += window
                done += 1
                engine.progress_changed.emit(done, total)
    if bool((weights <= 0).any()):
        raise ValueError("The configured segmentation stride leaves uncovered output pixels.")
    low = (sums / weights[None]).argmax(0).astype(np.uint8 if count <= 256 else np.uint16)
    restored_size = (max(width, round(low_w / sx)), max(height, round(low_h / sy)))
    mask = np.asarray(Image.fromarray(low).resize(restored_size, Image.Resampling.NEAREST))[:height, :width].copy()
    return {"mask": mask, "counts": np.bincount(mask.ravel(), minlength=count),
            "classes_present": [int(i) for i in np.unique(mask)], "tile": list(tile),
            "stride": list(stride), "input_size": list(profile.input_size), "total_tiles": total}


def run_profiled(engine, loaded, started_at):
    profile = loaded.input_profile
    request = engine.input_options or {}
    image_identity = engine.image_path.stat()
    recorded = request.get("recorded_input_profile")
    if recorded is not None:
        expected = {**recorded, "source": ""}
        actual = {**profile.to_dict(), "source": ""}
        if expected != actual:
            raise ModelValidationError("The model input profile differs from the saved analysis; start a new run.")
    validation = ModelLoader.validate_loaded(loaded)
    if validation.task_type != engine.task_type:
        raise ModelValidationError("The selected task does not match the model input profile.")
    engine._check_cancelled()
    snapshot = request.get("recorded_spatial_context")
    if snapshot is not None:
        if not isinstance(snapshot, dict) or snapshot.get("mode") not in ("pixel", "physical"):
            raise ValueError("Invalid saved scale-matching context.")
        calibration = recorded_calibration(engine.image_path, snapshot.get("calibration"), profile.image_decoder)
        matched = snapshot["mode"] == "physical"
    else:
        calibration = read_image_calibration(engine.image_path, profile.image_decoder, verify=True,
                                             manual_mpp=request.get("manual_mpp"))
        matched = request.get("match_scale", False)
        if type(matched) is not bool:
            raise ValueError("Scale matching must be explicitly enabled or disabled.")
    context = {"mode": "physical" if matched else "pixel", "calibration": calibration.to_dict(),
               "reference_field_um": list(profile.field_um) if profile.field_um else None}
    physical_tile = source_tile_size(profile, calibration) if matched else None
    if matched:
        context.update({"source_tile_px": list(physical_tile),
                        "actual_field_um": [n * mpp for n, mpp in zip(physical_tile, calibration.mpp)],
                        "effective_input_mpp": [n * mpp / size for n, mpp, size in zip(physical_tile, calibration.mpp, profile.input_size)],
                        "source_coarser_than_model": [mpp > field / size for mpp, field, size in zip(calibration.mpp, profile.field_um, profile.input_size)]})
    if engine.task_type == "classification" and engine.classification_mode == "tiled_analysis":
        planned_tile = physical_tile or tuple((engine.classification_tile_metadata or {}).get("tile_size", profile.tile_size))
        validate_classification_workload(calibration.image_size, planned_tile)
    image = load_rgb_image(engine.image_path, profile.image_decoder)
    if image.size != calibration.image_size:
        raise ValueError("Decoded image dimensions do not match its calibration.")
    common = {"task_type": engine.task_type, "model_path": str(engine.model_path),
              "model_name": engine.model_path.name, "image_path": str(engine.image_path),
              "timestamp": datetime.now(timezone.utc).isoformat(), "class_labels": list(profile.classes),
              "preprocess_profile": profile.normalization, "source_format": loaded.source_format,
              "model_sha256": loaded.model_sha256 or profile.model_sha256,
              "input_profile": profile.to_dict(), "spatial_context": context}
    if engine.task_type == "classification":
        mode = engine.classification_mode
        if mode == "tiled_analysis":
            tile = physical_tile or tuple((engine.classification_tile_metadata or {}).get("tile_size", profile.tile_size))
            edge = profile.edge_policy if matched else profile.pixel_edge_policy
            if matched and edge == "crop_then_resize":
                raise ValueError("Physical matching requires skip or reflect edges; stretching a partial crop changes its field.")
            metadata = {"tile_size": list(tile), "input_size": list(profile.input_size),
                        "classes": list(profile.classes), "colors": [list(c) for c in profile.colors],
                        "preprocess": profile.normalization, "resize_backend": profile.resize_backend,
                        "scale_status": "physical_field_matched" if matched else "unconfirmed_exploratory",
                        "edge_policy": edge, "output_kind": profile.output_kind, "input_profile": profile.to_dict()}
            spec = ClassificationTileSpec.from_metadata(metadata, list(profile.classes), profile.normalization)
            engine.status_changed.emit("Running classification tiles...")
            result = predict_classification_tiles(image, loaded.model, spec, engine.progress_changed.emit,
                                                   engine._cancel_event.is_set)
            analysis = result["classification_analysis"]
            analysis.update({"image_decoder": profile.image_decoder, "spatial_context": context,
                             "model_sha256": common["model_sha256"], "model_path": str(engine.model_path.resolve()),
                             "model_name": engine.model_path.name, "source_format": loaded.source_format})
        elif mode == "single_image":
            if matched and image.size != physical_tile:
                raise ValueError("Single image does not cover the model's expected physical field. Use Tiled analysis or crop a calibrated field; the image was not silently stretched.")
            with torch.inference_mode():
                output = ModelLoader.forward(loaded.model, profile.preprocessor().transform(image))
            result = OutputParser.parse_classification(output, profile.classes, output_kind=profile.output_kind)
            result["classification_parameters"] = {
                "mode": mode, "classification_mode": mode, "input_size": list(profile.input_size),
                "preprocess": profile.normalization, "image_decoder": profile.image_decoder,
                "resize_backend": profile.resize_backend, "input_profile": profile.to_dict(),
                "spatial_context": context, "model_sha256": common["model_sha256"], "output_kind": profile.output_kind}
        else:
            raise ValueError("Unknown classification mode.")
        result["classification_mode"] = mode
    else:
        engine.status_changed.emit("Running segmentation...")
        if profile.adapter == "upernet_reference":
            # No assumed MPP and no change to the supplied notebook's numerical path.
            result = predict_large_image(image, loaded.model, torch.device("cpu"),
                progress_callback=engine.progress_changed.emit, cancel_callback=engine._cancel_event.is_set)
        elif profile.input_scope == "patch":
            tile = physical_tile or profile.tile_size
            stride = tuple(max(1, min(length, round(step * length / base)))
                           for step, length, base in zip(profile.stride, tile, profile.tile_size))
            result = _segmentation_tiles(image, loaded, profile, tile, stride, engine)
        else:
            with torch.inference_mode():
                output = ModelLoader.forward(loaded.model, profile.preprocessor().transform(image))
            if output.ndim != 4 or output.shape[0] != 1 or output.shape[1] != len(profile.classes):
                raise ModelValidationError("Segmentation output does not match its declared class count and spatial shape.")
            probs = OutputParser.probabilities(output, profile.output_kind)
            low = probs.argmax(1)[0].cpu().numpy().astype(np.uint8 if len(profile.classes) <= 256 else np.uint16)
            mask = np.asarray(Image.fromarray(low).resize(image.size, Image.Resampling.NEAREST)).copy()
            result = {"mask": mask, "counts": np.bincount(mask.ravel(), minlength=len(profile.classes)),
                      "classes_present": [int(i) for i in np.unique(mask)], "input_size": list(profile.input_size)}
        colors = np.asarray(profile.colors, np.uint8)[result["mask"]]
        result["color_mask"] = Image.fromarray(colors)
        result["overlay"] = make_overlay(image, result["color_mask"], .2)
        result["blended"] = result["overlay"]
        result["overlay_alpha"] = .2
        result["device"] = "cpu"
        result["class_items"] = [{"index": i, "label": label, "color": list(profile.colors[i])}
                                 for i, label in enumerate(profile.classes)]
        result["legend_items"] = [(label, profile.colors[i]) for i, label in enumerate(profile.classes)]
    result.update(common)
    current_identity = engine.image_path.stat()
    if (image_identity.st_size, image_identity.st_mtime_ns) != (current_identity.st_size, current_identity.st_mtime_ns):
        raise ValueError("The input image changed during inference; no result was accepted.")
    result["elapsed_seconds"] = time.perf_counter() - started_at
    engine._check_cancelled()
    return result
