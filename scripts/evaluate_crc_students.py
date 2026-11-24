"""Evaluate validation-selected compact students and DenseNet on identical CRC patches."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch

from benchmark_crc_classifier import (
    add_evaluation_args, benchmark, evaluation_inputs, write_comparison,
)
from core.model_loader import ModelLoader
from core.model_profile import file_sha256


def selected_student(directory, method):
    """Require a completed run and its minimum-validation-loss checkpoint."""
    config = json.loads((directory / "config.json").read_text(encoding="utf-8"))
    with (directory / "metrics.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if (config["method"] != method or config["epochs"] < 1
            or [int(row["epoch"]) for row in rows] != list(range(1, config["epochs"] + 1))):
        raise ValueError(f"Expected a completed {method} student run: {directory}")
    losses = [float(row["val_loss"]) for row in rows]
    if not np.isfinite(losses).all():
        raise ValueError(f"Validation losses must be finite: {directory}")
    selected = rows[int(np.argmin(losses))]
    path = directory / "best_model.pth"
    saved = torch.load(path, map_location="cpu", weights_only=True)
    if (saved["epoch"] != int(selected["epoch"])
            or any(saved[key] != value for key, value in config["model_settings"].items())):
        raise ValueError(f"Checkpoint does not match the validation-selected student: {directory}")
    loaded = ModelLoader().load_with_info(path)
    details = {
        "run_directory": str(directory.resolve()), "method": method,
        "selected_epoch": saved["epoch"],
        "selection_rule": "first minimum validation loss, before external testing",
        "validation": {key: float(value) for key, value in selected.items() if key != "epoch"},
        "parameters": sum(parameter.numel() for parameter in loaded.model.parameters()),
        "checkpoint_bytes": path.stat().st_size,
        "config_sha256": file_sha256(directory / "config.json"),
        "metrics_sha256": file_sha256(directory / "metrics.csv"),
        "training_config": config,
    }
    return path, config, details


def matched_configs(supervised, distilled):
    """Only the training method and teacher targets may differ in this comparison."""
    allowed = {"method", "teacher_targets_sha256"}
    differences = {key for key in supervised.keys() | distilled.keys()
                   if supervised.get(key) != distilled.get(key)} - allowed
    if differences or supervised.get("teacher_targets_sha256") is not None or not distilled.get("teacher_targets_sha256"):
        raise ValueError(f"Student training configurations are not matched: {sorted(differences)}")


def paired_changes(records, supervised, distilled):
    target = np.asarray([label for _, label in records])
    before = supervised.argmax(1) == target
    after = distilled.argmax(1) == target
    return {
        "samples": len(records), "both_correct": int((before & after).sum()),
        "both_wrong": int((~before & ~after).sum()),
        "corrected_by_distillation": int((~before & after).sum()),
        "new_errors_from_distillation": int((before & ~after).sum()),
        "accuracy_change_percentage_points": float((after.mean() - before.mean()) * 100),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_evaluation_args(parser)
    parser.add_argument("--supervised-run", type=Path, required=True)
    parser.add_argument("--distilled-run", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    records, device = evaluation_inputs(args)
    first, first_config, first_details = selected_student(args.supervised_run, "supervised")
    second, second_config, second_details = selected_student(args.distilled_run, "distilled")
    matched_configs(first_config, second_config)
    predictions, timings, models = {}, {}, {}
    for name, checkpoint in (("baseline", args.baseline), ("supervised_student", first),
                             ("distilled_student", second)):
        print(f"Evaluating {name}: {checkpoint}", flush=True)
        scores, timing, identity = benchmark(checkpoint, args.test_root, records,
            args.batch_size, args.workers, device, use_tta=False)
        predictions[name] = scores["baseline"]
        timings[name] = timing
        models[name] = identity
    changes = paired_changes(records, predictions["supervised_student"], predictions["distilled_student"])
    provenance = {
        "evaluation": "one forward pass per patch; no TTA or teacher encoder at inference",
        "evaluation_script_sha256": file_sha256(Path(__file__)),
        "test_root": str(args.test_root.resolve()), "models": models,
        "student_runs": {"supervised": first_details, "distilled": second_details},
        "distillation_vs_supervised": changes,
        "scope": "Existing external CRC benchmark. GPU timings do not measure Windows CPU performance.",
    }
    write_comparison(args.output_dir, records, predictions, timings, provenance)
    print("Distillation versus matched supervised student: " + json.dumps(changes), flush=True)
    for details in (first_details, second_details):
        print(f'{details["method"]}: epoch={details["selected_epoch"]}, '
              f'parameters={details["parameters"]:,}, checkpoint={details["checkpoint_bytes"]:,} bytes', flush=True)
    print(f"RESULTS: {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
