import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import UperNetConfig, UperNetForSemanticSegmentation

from verify_segmentation import MODEL_PATH, LABELS


COLORS = np.array([
    [0, 0, 0],          # Exclude
    [255, 0, 0],        # Cancerous epithelium
    [0, 255, 0],        # Stroma
    [0, 0, 255],        # TILs
    [255, 255, 0],      # Normal epithelium
    [128, 0, 128],      # Junk/Debris
    [0, 255, 255],      # Blood
    [255, 165, 0],      # Other
    [255, 255, 255],    # Whitespace/Empty
], dtype=np.uint8)


def positions(length, tile, stride):
    if length <= tile:
        return [0]

    result = list(range(0, length - tile + 1, stride))
    if result[-1] != length - tile:
        result.append(length - tile)
    return result


def load_model(device):
    config = UperNetConfig.from_pretrained(
        "openmmlab/upernet-swin-base"
    )
    config.num_labels = len(LABELS)
    config.id2label = dict(enumerate(LABELS))
    config.label2id = {
        label: index for index, label in enumerate(LABELS)
    }

    model = UperNetForSemanticSegmentation(config)
    weights = torch.load(
        MODEL_PATH,
        map_location="cpu",
        weights_only=True,
    )
    model.load_state_dict(weights, strict=True)
    del weights
    return model.to(device).eval()


def predict_large_image(image, model, device, tile=1000, stride=512):
    input_size = 224
    array = np.asarray(image)
    height, width = array.shape[:2]

    pad_h = max(0, tile - height)
    pad_w = max(0, tile - width)
    if pad_h or pad_w:
        array = np.pad(
            array,
            ((0, pad_h), (0, pad_w), (0, 0)),
            mode="reflect",
        )

    ys = positions(array.shape[0], tile, stride)
    xs = positions(array.shape[1], tile, stride)
    scale = input_size / tile

    low_h = round(ys[-1] * scale) + input_size
    low_w = round(xs[-1] * scale) + input_size

    probabilities = np.zeros(
        (len(LABELS), low_h, low_w), dtype=np.float32
    )
    weights = np.zeros((low_h, low_w), dtype=np.float32)

    hann = np.hanning(input_size + 2)[1:-1].astype(np.float32)
    window = np.outer(hann, hann) + 1e-3

    mean = torch.tensor(
        [0.485, 0.456, 0.406], device=device
    ).view(1, 3, 1, 1)
    std = torch.tensor(
        [0.229, 0.224, 0.225], device=device
    ).view(1, 3, 1, 1)

    total = len(ys) * len(xs)
    done = 0
    print(f"图片尺寸：{width} × {height}")
    print(f"共需分析 {total} 个区域。", flush=True)

    with torch.inference_mode():
        for y in ys:
            for x in xs:
                patch = Image.fromarray(
                    array[y:y + tile, x:x + tile]
                ).resize(
                    (input_size, input_size),
                    Image.Resampling.BILINEAR,
                )

                tensor = torch.from_numpy(
                    np.array(patch, dtype=np.float32)
                ).permute(2, 0, 1).unsqueeze(0).to(device)

                tensor = (tensor / 255.0 - mean) / std
                logits = model(pixel_values=tensor).logits

                if tuple(logits.shape) != (
                    1, len(LABELS), input_size, input_size
                ):
                    raise ValueError(
                        f"输出形状异常：{tuple(logits.shape)}"
                    )
                if not torch.isfinite(logits).all().item():
                    raise ValueError("模型输出含 NaN 或无穷大。")

                probability = logits.softmax(1)[0].cpu().numpy()
                low_y = round(y * scale)
                low_x = round(x * scale)

                probabilities[
                    :, low_y:low_y + input_size,
                    low_x:low_x + input_size
                ] += probability * window

                weights[
                    low_y:low_y + input_size,
                    low_x:low_x + input_size
                ] += window

                done += 1
                print(f"已完成：{done}/{total}", flush=True)

    probabilities /= np.maximum(weights, 1e-6)[None, :, :]
    low_mask = probabilities.argmax(axis=0).astype(np.uint8)

    # 与导师 notebook 一样，先恢复拼接画布尺度，再裁到原图范围。
    restored_mask = Image.fromarray(low_mask).resize(
        (round(low_w / scale), round(low_h / scale)),
        Image.Resampling.NEAREST,
    )
    return np.array(restored_mask)[:height, :width]


def save_results(image, mask, output_dir, stem):
    output_dir.mkdir(parents=True, exist_ok=True)

    color_mask = COLORS[mask]
    original = np.asarray(image, dtype=np.float32)
    overlay = np.clip(
        0.8 * original + 0.2 * color_mask,
        0, 255,
    ).astype(np.uint8)

    # 0～8 的原始类别编号，后续统计使用此文件。
    Image.fromarray(mask).save(
        output_dir / f"{stem}_labels.png"
    )
    Image.fromarray(color_mask).save(
        output_dir / f"{stem}_mask.png"
    )
    Image.fromarray(overlay).save(
        output_dir / f"{stem}_overlay.png"
    )

    counts = np.bincount(mask.ravel(), minlength=len(LABELS))
    print("\n各类预测面积比例（分母为整张图片，包含空白和排除区域）：")
    for index, label in enumerate(LABELS):
        print(f"{label}: {counts[index] / mask.size:.2%}")

    print(f"\n结果保存到：{output_dir.resolve()}")
    print("这些是模型预测比例，不代表准确率或确诊结果。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("segmentation_test_output")
    )
    args = parser.parse_args()

    if not args.image.is_file():
        raise FileNotFoundError(f"找不到图片：{args.image}")
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"找不到权重：{MODEL_PATH}")

    with Image.open(args.image) as source:
        image = source.convert("RGB").copy()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"预测设备：{device}", flush=True)
    print("加载模型……", flush=True)
    model = load_model(device)

    mask = predict_large_image(image, model, device)
    save_results(image, mask, args.output, args.image.stem)


if __name__ == "__main__":
    main()