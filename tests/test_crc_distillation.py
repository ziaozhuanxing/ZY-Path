"""Verify student loss, cache identity and independent checkpoint inference."""

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest
import torch
from torch.nn import functional as F

from core.classification_tiles import CLASSIFICATION_LABELS
from core.model_loader import ModelLoader
from core.model_profile import file_sha256


@pytest.fixture
def trainer(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("crc_student_test", scripts / "distill_crc_student.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_distillation_loss_keeps_labels_and_temperature_scaling(trainer):
    student = torch.tensor([[1., -1.], [-2., 2.]], requires_grad=True)
    labels = torch.tensor([0, 1])
    teacher = torch.tensor([[2., 0.], [0., 1.]])
    expected = .5 * F.cross_entropy(student, labels) + 4.5 * F.kl_div(
        F.log_softmax(student / 3, dim=1), F.softmax(teacher / 3, dim=1), reduction="batchmean")
    loss = trainer.loss_function(student, labels, teacher, 3, .5)
    assert torch.allclose(loss, expected)
    loss.backward()
    assert torch.isfinite(student.grad).all()
    assert torch.equal(trainer.loss_function(student, labels, None, 3, .5),
                       F.cross_entropy(student, labels))


def test_students_export_self_contained_models_and_reject_changed_training_images(trainer, tmp_path):
    records = {}
    for split in ("train", "val"):
        images = []
        for label, name in enumerate(CLASSIFICATION_LABELS):
            path = tmp_path / "images" / name / f"{split}.tif"
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (224, 224), (label * 25, 50, 100)).save(path)
            images.append({"file_name": f"{name}/{split}.tif", "label": label})
        manifest = tmp_path / f"{split}.json"
        manifest.write_text(json.dumps({"classes": CLASSIFICATION_LABELS,
                                       "dataset_root": str(tmp_path / "images"), "images": images}))
        records[split] = manifest
    root, training = trainer.development_records(records["train"])
    teacher = tmp_path / "targets.npz"
    np.savez_compressed(teacher, classes=np.asarray(CLASSIFICATION_LABELS),
                        paths=np.asarray([p for p, _ in training]), labels=np.arange(9),
                        logits=np.eye(9, dtype=np.float32) * 3,
                        train_manifest_sha256=np.asarray(file_sha256(records["train"])),
                        image_sha256=np.asarray([file_sha256(root / p) for p, _ in training]))
    for method in ("supervised", "distilled"):
        args = argparse.Namespace(method=method, train_manifest=records["train"], val_manifest=records["val"],
            train_root=None, teacher_targets=teacher, output_dir=tmp_path / method, epochs=1,
            batch_size=3, workers=0, device="cpu", temperature=3., alpha=.5, resume=False)
        trainer.train(args)
        loaded = ModelLoader().load_with_info(args.output_dir / "best_model.pth")
        assert sum(p.numel() for p in loaded.model.parameters()) == 416457
        assert loaded.input_profile.classes == CLASSIFICATION_LABELS
        assert loaded.input_profile.normalization == "imagenet"
        tensor = loaded.input_profile.preprocessor().transform(Image.new("RGB", (224, 224)))
        with torch.inference_mode():
            assert tuple(loaded.model(tensor).shape) == (1, 9)
        initial = file_sha256(args.output_dir / "best_model.pth")
        args.resume = True
        trainer.train(args)
        assert file_sha256(args.output_dir / "best_model.pth") == initial
        args.alpha = .6
        with pytest.raises(ValueError, match="Resume arguments"):
            trainer.train(args)
    Image.new("RGB", (224, 224), "white").save(root / training[0][0])
    with pytest.raises(ValueError, match="image bytes differ"):
        trainer.teacher_scores(teacher, records["train"], root, training)
