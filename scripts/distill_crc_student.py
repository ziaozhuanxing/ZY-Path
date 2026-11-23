"""Train matched compact CRC classifiers with labels or cached teacher scores."""

import argparse
import csv
import json
from pathlib import Path
import random

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torchvision.models import DenseNet

from benchmark_crc_classifier import CLASSIFICATION_LABELS, CRCPatches, metrics
from probe_crc_foundation import development_records
from core.model_profile import file_sha256, SCHEMA
from core.preprocessor import Preprocessor


MODEL_SETTINGS = dict(growth_rate=32, block_config=[2, 2, 2, 2],
                      num_init_features=64, bn_size=4, drop_rate=0., num_classes=9)


def atomic_save(value, path):
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, temporary)
    temporary.replace(path)


def teacher_scores(path, manifest, root, records):
    with np.load(path, allow_pickle=False) as archive:
        if (tuple(archive["classes"].tolist()) != CLASSIFICATION_LABELS
                or archive["train_manifest_sha256"].item() != file_sha256(manifest)
                or archive["paths"].tolist() != [name for name, _ in records]
                or archive["labels"].tolist() != [label for _, label in records]):
            raise ValueError("Teacher targets do not match these training records.")
        if archive["image_sha256"].tolist() != [file_sha256(root / name) for name, _ in records]:
            raise ValueError("Training image bytes differ from the teacher target cache.")
        scores = archive["logits"].copy()
    if scores.shape != (len(records), 9) or not np.isfinite(scores).all():
        raise ValueError("Expected finite nine-class teacher logits for every training image.")
    return torch.from_numpy(scores).float()


class StudentPatches(CRCPatches):
    def __getitem__(self, index):
        image, label = super().__getitem__(index)
        return image, label, index


def checkpoint(model, epoch):
    profile = {
        "schema": SCHEMA, "task_type": "classification",
        "classes": list(CLASSIFICATION_LABELS), "normalization": "imagenet",
        "image_decoder": "opencv_color", "resize_backend": "opencv_linear",
        "input_scope": "patch", "input_size": [224, 224], "tile_size": [224, 224],
        "stride": [224, 224], "field_um": [112., 112.],
        "edge_policy": "skip", "pixel_edge_policy": "crop_then_resize",
        "note": "Compact CRC student. Original 224-pixel CRC training patches at nominal 0.5 MPP.",
    }
    return {**MODEL_SETTINGS, "model_dict": model.state_dict(), "epoch": epoch,
            "classes": list(CLASSIFICATION_LABELS), "preprocess": "imagenet", "input_size": [224, 224],
            "zypath_input_profile": profile}


def loss_function(logits, labels, teacher, temperature, alpha):
    supervised = F.cross_entropy(logits, labels)
    if teacher is None:
        return supervised
    knowledge = F.kl_div(F.log_softmax(logits / temperature, dim=1),
                         F.softmax(teacher / temperature, dim=1), reduction="batchmean")
    return (1 - alpha) * supervised + alpha * temperature**2 * knowledge


def train(args):
    if (args.epochs < 1 or args.batch_size < 1 or args.workers < 0
            or not 0 < args.alpha < 1 or not 0 < args.temperature <= 20):
        raise ValueError("Check epochs, batch size, workers, alpha and temperature.")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Submit to a GPU node or explicitly choose --device cpu.")
    if args.method == "distilled" and not args.teacher_targets:
        raise ValueError("Distilled training requires --teacher-targets from the completed teacher run.")
    train_root, training = development_records(args.train_manifest, args.train_root)
    val_root, validation = development_records(args.val_manifest, args.train_root)
    if train_root != val_root or {p for p, _ in training} & {p for p, _ in validation}:
        raise ValueError("Use disjoint training and validation manifests from the same dataset.")
    if len(training) < 2:
        raise ValueError("At least two training patches are required.")
    targets = teacher_scores(args.teacher_targets, args.train_manifest, train_root, training) if args.method == "distilled" else None
    contract = {
        "method": args.method, "model_settings": MODEL_SETTINGS, "seed": 42,
        "train_manifest_sha256": file_sha256(args.train_manifest),
        "val_manifest_sha256": file_sha256(args.val_manifest),
        "dataset_root": str(train_root), "train_count": len(training), "val_count": len(validation),
        "teacher_targets_sha256": file_sha256(args.teacher_targets) if targets is not None else None,
        "trainer_sha256": file_sha256(Path(__file__)), "preprocess": "imagenet",
        "epochs": args.epochs, "batch_size": args.batch_size,
        "augmentation": "exact rotations and reflections; applied per batch",
        "optimizer": "AdamW, lr=0.0003, weight_decay=0.0001; cosine schedule",
        "alpha": args.alpha, "temperature": args.temperature, "device": str(device),
    }
    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    model = DenseNet(**MODEL_SETTINGS).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs)
    first_epoch, best, rows = 1, float("inf"), []
    if args.resume:
        saved = torch.load(args.output_dir / "last_checkpoint.pth", map_location="cpu", weights_only=True)
        if saved["contract"] != contract:
            raise ValueError("Resume arguments, data manifests or teacher targets changed.")
        model.load_state_dict(saved["model_dict"])
        optimizer.load_state_dict(saved["optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        torch.set_rng_state(saved["torch_rng"])
        if device.type == "cuda":
            torch.cuda.set_rng_state_all(saved["cuda_rng"])
        first_epoch, best, rows = saved["epoch"] + 1, saved["best_validation_loss"], saved["metrics"]
    else:
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / "config.json").write_text(json.dumps(contract, indent=2) + "\n")
    transform = Preprocessor("imagenet", (224, 224), "opencv_linear").transform
    training_data = StudentPatches(train_root, training, transform, "opencv_color")
    validation_loader = DataLoader(CRCPatches(val_root, validation, transform, "opencv_color"),
                                   batch_size=args.batch_size, num_workers=args.workers)
    for epoch in range(first_epoch, args.epochs + 1):
        generator = torch.Generator().manual_seed(42 + epoch)
        loader = DataLoader(training_data, batch_size=args.batch_size, shuffle=True, generator=generator,
                            num_workers=args.workers)
        model.train()
        loss_sum, total = 0., 0
        for index, (images, labels, indices) in enumerate(loader, 1):
            images, labels = images.to(device), labels.to(device)
            images = torch.rot90(images, int(torch.randint(4, (1,))), (-2, -1))
            if bool(torch.rand(()) < .5):
                images = images.flip(-1)
            optimizer.zero_grad(set_to_none=True)
            teacher = targets[indices].to(device) if targets is not None else None
            loss = loss_function(model(images), labels, teacher, args.temperature, args.alpha)
            if not torch.isfinite(loss):
                raise FloatingPointError("The student loss is not finite.")
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.detach()) * len(labels)
            total += len(labels)
            if index % 200 == 0:
                print(f"Epoch {epoch} batch {index}/{len(loader)}", flush=True)
        model.eval()
        probabilities, val_loss = [], 0.
        with torch.inference_mode():
            for images, labels in validation_loader:
                logits = model(images.to(device))
                val_loss += float(F.cross_entropy(logits, labels.to(device), reduction="sum"))
                probabilities.append(logits.softmax(1).cpu().numpy())
        validation_metrics = metrics(np.asarray([label for _, label in validation]), np.concatenate(probabilities))
        val_loss /= len(validation)
        row = {"epoch": epoch, "train_loss": loss_sum / total, "val_loss": val_loss,
               "val_accuracy": validation_metrics["accuracy"], "val_macro_f1": validation_metrics["macro_f1"],
               "val_mus_as_str": validation_metrics["mus_as_str"], "val_str_as_mus": validation_metrics["str_as_mus"]}
        rows.append(row)
        scheduler.step()
        if val_loss < best:
            best = val_loss
            atomic_save(checkpoint(model, epoch), args.output_dir / "best_model.pth")
        state = {**checkpoint(model, epoch), "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
                 "best_validation_loss": best, "metrics": rows, "contract": contract,
                 "torch_rng": torch.get_rng_state(),
                 "cuda_rng": torch.cuda.get_rng_state_all() if device.type == "cuda" else []}
        atomic_save(state, args.output_dir / "last_checkpoint.pth")
        with (args.output_dir / "metrics.csv.tmp").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerows(rows)
        (args.output_dir / "metrics.csv.tmp").replace(args.output_dir / "metrics.csv")
        print(json.dumps(row), flush=True)
    print(f"Student run complete: {args.output_dir}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("supervised", "distilled"), required=True)
    parser.add_argument("--train-manifest", type=Path, required=True)
    parser.add_argument("--val-manifest", type=Path, required=True)
    parser.add_argument("--train-root", type=Path)
    parser.add_argument("--teacher-targets", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--temperature", type=float, default=3.)
    parser.add_argument("--alpha", type=float, default=.5)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    # The Sunway launcher creates a unique output for each job. Also lock the
    # target when explicitly resuming a run from another shell.
    import fcntl

    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    lock = args.output_dir.with_name(f".{args.output_dir.name}.training.lock")
    with lock.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another process is using this student experiment.") from error
        train(args)


if __name__ == "__main__":
    main()
