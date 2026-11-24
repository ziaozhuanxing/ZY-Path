"""Verify paired evaluation and validation-only checkpoint selection."""

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from torchvision.models import DenseNet


@pytest.fixture
def evaluator(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("crc_student_evaluation_test", scripts / "evaluate_crc_students.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_distillation_reports_regressions_as_well_as_corrections(evaluator):
    records = [(f"example-{i}", i) for i in range(5)]
    first = np.eye(9)[[0, 0, 2, 4, 4]]
    second = np.eye(9)[[0, 1, 1, 4, 4]]
    assert evaluator.paired_changes(records, first, second) == {
        "samples": 5, "both_correct": 2, "both_wrong": 1,
        "corrected_by_distillation": 1, "new_errors_from_distillation": 1,
        "accuracy_change_percentage_points": 0.,
    }


def test_matching_rejects_confounding_training_changes(evaluator):
    config = {"method": "supervised", "teacher_targets_sha256": None, "epochs": 30, "seed": 42}
    distilled = {**config, "method": "distilled", "teacher_targets_sha256": "teacher-cache"}
    evaluator.matched_configs(config, distilled)
    with pytest.raises(ValueError, match="not matched"):
        evaluator.matched_configs(config, {**distilled, "epochs": 100})
    with pytest.raises(ValueError, match="not matched"):
        evaluator.matched_configs(config, {**distilled, "teacher_targets_sha256": None})


def test_selected_student_rejects_incomplete_or_wrong_epoch(evaluator, tmp_path):
    import distill_crc_student as trainer

    config = {"method": "distilled", "epochs": 3, "model_settings": trainer.MODEL_SETTINGS}
    (tmp_path / "config.json").write_text(json.dumps(config))
    fields = ("epoch", "val_loss", "val_accuracy", "val_macro_f1")
    rows = [(1, .5, .8, .8), (2, .1, .9, .9), (3, .2, .95, .95)]
    def save_rows(values):
        with (tmp_path / "metrics.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            writer.writerows(values)
    save_rows(rows[:2])
    with pytest.raises(ValueError, match="completed"):
        evaluator.selected_student(tmp_path, "distilled")
    save_rows(rows)
    model = DenseNet(**trainer.MODEL_SETTINGS)
    torch.save(trainer.checkpoint(model, 2), tmp_path / "best_model.pth")
    path, saved_config, details = evaluator.selected_student(tmp_path, "distilled")
    assert path.name == "best_model.pth" and saved_config == config
    assert details["selected_epoch"] == 2
    assert details["parameters"] == 416457
    torch.save(trainer.checkpoint(model, 3), path)
    with pytest.raises(ValueError, match="validation-selected"):
        evaluator.selected_student(tmp_path, "distilled")
