"""Compare a frozen UNI2-h encoder and a CRC linear probe against DenseNet."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

from benchmark_crc_classifier import (
    CLASSIFICATION_LABELS, CRCPatches, add_evaluation_args, benchmark, evaluation_inputs, metrics, write_comparison,
)
from core.model_profile import file_sha256


def development_records(manifest, root_override=None):
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if tuple(data["classes"]) != CLASSIFICATION_LABELS:
        raise ValueError(f"Unexpected CRC class order in {manifest}.")
    root = (root_override or Path(data["dataset_root"])).resolve()
    records = []
    for row in data["images"]:
        path, label = Path(row["file_name"]), row["label"]
        if (path.is_absolute() or len(path.parts) != 2 or ".." in path.parts or type(label) is not int
                or not 0 <= label < len(CLASSIFICATION_LABELS) or path.parts[0] != CLASSIFICATION_LABELS[label]):
            raise ValueError(f"Invalid relative image path or label in {manifest}: {path}")
        records.append((path.as_posix(), label))
    if (len({name for name, _ in records}) != len(records)
            or {label for _, label in records} != set(range(len(CLASSIFICATION_LABELS)))):
        raise ValueError(f"Use distinct patches and all nine classes in {manifest}.")
    return root, records


def load_encoder(weights, device):
    import timm

    encoder = timm.create_model(
        "vit_giant_patch14_224", pretrained=False, img_size=224, patch_size=14,
        depth=24, num_heads=24, init_values=1e-5, embed_dim=1536, mlp_ratio=2.66667 * 2,
        num_classes=0, no_embed_class=True, mlp_layer=timm.layers.SwiGLUPacked,
        act_layer=nn.SiLU, reg_tokens=8, dynamic_img_size=True,
    )
    if weights.suffix == ".safetensors":
        from safetensors.torch import load_file

        state = load_file(str(weights))
    else:
        state = torch.load(weights, map_location="cpu", weights_only=True)
    encoder.load_state_dict(state, strict=True)
    return encoder.to(device).eval().requires_grad_(False), timm.__version__


@torch.inference_mode()
def embeddings(encoder, dataset, batch_size, workers, device, phase):
    batches = DataLoader(dataset, batch_size=batch_size, num_workers=workers, pin_memory=device.type == "cuda")
    features = []
    for index, (batch, _) in enumerate(batches, 1):
        values = encoder(batch.to(device, non_blocking=True)).float()
        if values.ndim != 2 or not torch.isfinite(values).all():
            raise ValueError("The encoder must return one finite feature vector per patch.")
        features.append(values.cpu())
        if index % 100 == 0 or index == len(batches):
            print(f"UNI2-h {phase} embeddings {index}/{len(batches)}", flush=True)
    return torch.cat(features)


def normalized_features(features):
    return F.normalize(features, dim=1) * features.shape[1] ** .5


def fit_head(features, target, device):
    torch.manual_seed(42)
    x = normalized_features(features.to(device))
    y = torch.as_tensor(target, device=device)
    head = nn.Linear(x.shape[1], len(CLASSIFICATION_LABELS)).to(device)
    nn.init.zeros_(head.weight)
    nn.init.zeros_(head.bias)
    # A fixed, regularized multinomial linear probe. All fitting uses training patches.
    optimizer = torch.optim.LBFGS(head.parameters(), max_iter=100, line_search_fn="strong_wolfe")

    def closure():
        optimizer.zero_grad()
        loss = F.cross_entropy(head(x), y) + .0005 * head.weight.square().sum()
        loss.backward()
        return loss

    optimizer.step(closure)
    return head.eval()


@torch.inference_mode()
def score_head(head, features, device):
    return head(normalized_features(features.to(device))).softmax(1).cpu().numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_evaluation_args(parser)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--uni2-h-weights", type=Path, required=True)
    parser.add_argument("--train-manifest", type=Path, required=True)
    parser.add_argument("--val-manifest", type=Path, required=True)
    parser.add_argument("--train-root", type=Path)
    args = parser.parse_args()
    test, device = evaluation_inputs(args)
    train_root, train = development_records(args.train_manifest, args.train_root)
    val_root, validation = development_records(args.val_manifest, args.train_root)
    if train_root != val_root or args.test_root.resolve() == train_root:
        raise ValueError("Use one development dataset and a separate external test dataset.")
    if {name for name, _ in train} & {name for name, _ in validation}:
        raise ValueError("Training and validation manifests contain overlapping paths.")
    if {name for name, _ in train + validation} & {name for name, _ in test}:
        raise ValueError("Development and test records contain overlapping relative filenames.")

    from torchvision import transforms

    # The 224 × 224 input patches already satisfy the official fixed-size resize and center crop.
    transform = transforms.Compose([transforms.ToTensor(),
        transforms.Normalize((.485, .456, .406), (.229, .224, .225))])
    encoder, timm_version = load_encoder(args.uni2_h_weights, device)

    def extract(root, records, phase):
        return embeddings(encoder, CRCPatches(root, records, transform, "pillow_rgb"),
                          args.batch_size, args.workers, device, phase)

    # Validate the actual weights and a full-size batch on the requested device
    # before starting the feature extraction pass over the development dataset.
    smoke = extract(train_root, train[:args.batch_size], "preflight")
    if smoke.shape[1] != 1536:
        raise ValueError("Expected 1,536 UNI2-h features per crop.")
    print("UNI2-h weight and development-batch preflight passed", flush=True)
    del smoke
    predictions, times, provenance = benchmark(
        args.baseline, args.test_root, test, args.batch_size, args.workers, device, use_tta=False)

    x = extract(train_root, train, "train")
    head = fit_head(x, [label for _, label in train], device)
    del x
    val_scores = score_head(head, extract(val_root, validation, "validation"), device)
    val_metrics = metrics(np.asarray([label for _, label in validation]), val_scores)
    print(f'UNI2-h validation macro-F1={val_metrics["macro_f1"]:.4f}', flush=True)
    started = perf_counter()
    test_scores = score_head(head, extract(args.test_root, test, "test"), device)
    test_seconds = perf_counter() - started
    del encoder
    predictions["uni2_h_linear_probe"] = test_scores
    provenance["foundation"] = {
        "encoder": "MahmoodLab/UNI2-h", "weights_sha256": file_sha256(args.uni2_h_weights),
        "probe_script_sha256": file_sha256(Path(__file__)),
        "train_manifest_sha256": file_sha256(args.train_manifest), "train_samples": len(train),
        "validation_manifest_sha256": file_sha256(args.val_manifest), "validation_samples": len(validation),
        "validation": val_metrics, "timm": timm_version,
        "decoder": "pillow_rgb", "input_size": [224, 224], "normalization": "imagenet",
    }
    times["uni2_h_test_total"] = test_seconds
    write_comparison(args.output_dir, test, predictions, times, provenance)
    torch.save({"state_dict": {key: value.cpu() for key, value in head.state_dict().items()},
                "class_order": list(CLASSIFICATION_LABELS), "encoder": provenance["foundation"],
                "feature_normalization": "l2_sqrt_dimension"}, args.output_dir / "linear_head.pth")


if __name__ == "__main__":
    main()
