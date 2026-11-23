"""Compare unchanged CRC inference and rotation/reflection test-time averaging."""

import argparse
import csv
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from core.classification_input import load_rgb_image
from core.classification_tiles import CLASSIFICATION_LABELS, CLASSIFICATION_REVIEW_SCORE
from core.model_loader import ModelLoader
from core.model_profile import file_sha256
from core.output_parser import OutputParser


class CRCPatches(Dataset):
    def __init__(self, root, records, transform, decoder):
        self.root, self.records, self.transform, self.decoder = root, records, transform, decoder

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        relative_path, label = self.records[index]
        image = load_rgb_image(self.root / relative_path, self.decoder)
        if image.size != (224, 224):
            raise ValueError(f"Expected an original 224 × 224 CRC patch: {relative_path}")
        return self.transform(image).squeeze(0), label


def test_records(root, expected):
    records = [(file.relative_to(root).as_posix(), label)
               for label, name in enumerate(CLASSIFICATION_LABELS)
               for file in sorted((root / name).glob("*"))
               if file.is_file() and file.suffix.lower() in (".tif", ".tiff")]
    if len(records) != expected:
        raise ValueError(f"Expected {expected} test patches in the CRC class folders, found {len(records)}.")
    if expected == 7180 and len({label for _, label in records}) != len(CLASSIFICATION_LABELS):
        raise ValueError("The full 7,180-patch benchmark must contain all nine CRC classes.")
    return records


def metrics(target, scores):
    classes = CLASSIFICATION_LABELS
    rows = len(target)
    if scores.shape != (rows, len(classes)) or not np.isfinite(scores).all():
        raise ValueError("Each image must have one finite score per CRC class.")
    pred = scores.argmax(axis=1)
    matrix = np.bincount(len(classes) * target + pred, minlength=len(classes)**2).reshape(len(classes), len(classes))
    support = matrix.sum(axis=1)
    denominator = support + matrix.sum(axis=0)
    f1 = np.divide(2 * matrix.diagonal(), denominator, out=np.zeros(len(classes)), where=denominator != 0)
    review = scores.max(axis=1) < CLASSIFICATION_REVIEW_SCORE
    correct = pred == target
    mus, str_ = classes.index("MUS"), classes.index("STR")
    return {
        "correct": int(correct.sum()), "accuracy": float(correct.mean()),
        "macro_f1": float(f1[support > 0].mean()),
        "per_class": {label: {"f1": float(f1[i]), "support": int(support[i])}
                      for i, label in enumerate(classes)},
        "mus_as_str": int(matrix[mus, str_]), "str_as_mus": int(matrix[str_, mus]),
        "confusion_matrix": matrix.tolist(),
        "review": {"threshold": CLASSIFICATION_REVIEW_SCORE, "queued": int(review.sum()),
                   "retained_accuracy": float(correct[~review].mean()) if (~review).any() else None,
                   "errors_in_queue": int((review & ~correct).sum())},
    }


def write_comparison(output, records, predictions, timings, provenance):
    target = np.asarray([label for _, label in records])
    baseline_correct = predictions["baseline"].argmax(axis=1) == target
    comparisons = {}
    for name, scores in predictions.items():
        result = metrics(target, scores)
        correct = scores.argmax(axis=1) == target
        result.update(corrected=int((correct & ~baseline_correct).sum()),
                      new_errors=int((~correct & baseline_correct).sum()))
        comparisons[name] = result
    index_hash = hashlib.sha256(json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    report = {"samples": len(records), "class_order": list(CLASSIFICATION_LABELS),
              "test_path_label_index_sha256": index_hash,
              **provenance, "timing_seconds": timings, "methods": comparisons}
    output.mkdir(parents=True, exist_ok=False)
    with (output / "predictions.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["relative_path", "true_class", "method", "predicted_class",
                         *[f"probability_{name}" for name in CLASSIFICATION_LABELS]])
        for name, scores in predictions.items():
            for (path, label), row in zip(records, scores):
                writer.writerow([path, CLASSIFICATION_LABELS[label], name,
                                 CLASSIFICATION_LABELS[row.argmax()], *row.tolist()])
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, result in comparisons.items():
        print(f'{name}: accuracy={result["accuracy"]:.4%}, macro-F1={result["macro_f1"]:.4f}, '
              f'MUS→STR={result["mus_as_str"]}, STR→MUS={result["str_as_mus"]}', flush=True)
    return report


def d4_views(batch):
    """Exact tensor symmetries, applied after the model's usual preprocessing."""
    for index in range(1, 4):
        yield torch.rot90(batch, index, (-2, -1))
    flipped = batch.flip(-1)
    for index in range(4):
        yield torch.rot90(flipped, index, (-2, -1))


@torch.inference_mode()
def benchmark(model_path, root, records, batch_size, workers, device, *, use_tta=True):
    loaded = ModelLoader().load_with_info(model_path)
    profile = loaded.input_profile
    if (not profile or profile.task_type != "classification" or profile.classes != CLASSIFICATION_LABELS
            or profile.input_size != (224, 224)):
        raise ValueError("Use a nine-class CRC checkpoint with its matching ZY-Path model profile and 224 × 224 input.")
    loader = DataLoader(CRCPatches(root, records, profile.preprocessor().transform, profile.image_decoder),
                        batch_size=batch_size, num_workers=workers)
    model = loaded.model.to(device).eval()
    baseline, full, selective = [], [], []
    times = {"baseline_forward": 0., "d4_additional_forward": 0.}

    def scores(tensor):
        output = ModelLoader.forward(model, tensor)
        return OutputParser.probabilities(output, profile.output_kind).float()

    flagged = 0
    for index, (batch, _) in enumerate(loader, 1):
        batch = batch.to(device)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = perf_counter()
        one = scores(batch).cpu()
        times["baseline_forward"] += perf_counter() - start
        baseline.append(one)
        if use_tta:
            start = perf_counter()
            combined = one.to(device)
            for view in d4_views(batch):
                combined = combined + scores(view)
            combined = combined.cpu() / 8
            times["d4_additional_forward"] += perf_counter() - start
            full.append(combined)
            eligible = one.amax(1) < CLASSIFICATION_REVIEW_SCORE
            flagged += int(eligible.sum())
            selective.append(torch.where(eligible[:, None], combined, one))
        if index % 100 == 0:
            print(f"CRC evaluation batch {index}/{len(loader)}", flush=True)
    predictions = {"baseline": torch.cat(baseline).numpy()}
    if use_tta:
        predictions.update(d4=torch.cat(full).numpy(), selective_d4=torch.cat(selective).numpy())
    dependencies = {"python": platform.python_version(), "torch": str(torch.__version__),
                    "torchvision": version("torchvision"), "pillow": version("Pillow"),
                    "numpy": np.__version__}
    if profile.image_decoder == "opencv_color" or profile.resize_backend == "opencv_linear":
        import cv2

        dependencies["opencv"] = cv2.__version__
    provenance = {"model_sha256": loaded.model_sha256, "model_profile": profile.to_dict(),
                  "benchmark_sha256": file_sha256(Path(__file__)), "dependencies": dependencies, "device": str(device),
                  "forward_views_per_method": {"baseline": len(records), **(
                      {"d4": 8 * len(records), "selective_d4": len(records) + 7 * flagged} if use_tta else {})}}
    return predictions, times, provenance


def add_evaluation_args(parser):
    parser.add_argument("--test-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-test-count", type=int, default=7180)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")


def evaluation_inputs(args):
    if args.output_dir.exists():
        raise ValueError("Choose a new output directory for this evaluation.")
    if args.expected_test_count <= 0 or args.batch_size <= 0 or args.workers < 0:
        raise ValueError("Expected test count and batch size must be positive. Workers cannot be negative.")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable. Use a Sunway GPU job, or pass --device cpu.")
    return test_records(args.test_root, args.expected_test_count), torch.device(args.device)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_evaluation_args(parser)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    records, device = evaluation_inputs(args)
    predictions, times, provenance = benchmark(args.model, args.test_root, records, args.batch_size, args.workers, device)
    write_comparison(args.output_dir, records, predictions, times, provenance)


if __name__ == "__main__":
    main()
